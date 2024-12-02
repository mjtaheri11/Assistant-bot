import argparse
import asyncio
import csv
import json
import logging
import os
import time
import traceback
from datetime import datetime
from typing import List, Optional, Tuple

import asyncpg
from fastapi import FastAPI, HTTPException, Query, Request
from prometheus_client import Counter, Histogram, generate_latest
from pydantic import BaseModel
from starlette.responses import Response

from src.orm import Postgres
from src.config import config
from src.logic import (
    chat_responder_,
    feedback_,
    prepare_final_context,
    query_responder,
    sql_responder,
    utterance_paraphraser,
)
from src.logs import non_generative_agent_logger, simple_logger

RESPONSE_TEMPLATE_FOR_NO_ANSWER = "در حال حاضر نمی‌توانم به سوال شما پاسخ دهم"
app = FastAPI(title="Digital Assistant")

# Define Prometheus metrics
REQUEST_COUNT = Counter("api_http_requests_total", "Total API Requests", ["endpoint"])
REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds", "Latency of API Requests", ["endpoint"]
)


# Models for request and response


# sudo docker exec -it postgres psql -U postgres -d chatbot -c "CREATE TABLE public.session (session_id UUID DEFAULT gen_random_uuid() PRIMARY KEY, history_length INT)"

# CREATE EXTENSION IF NOT EXISTS "pgcrypto";

# CREATE TABLE public.session (
#     session_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
#     create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );


# CREATE TABLE public.message (
#     message_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
#     session_id UUID REFERENCES public.session(session_id),
#     user_query TEXT,
#     paraphrased_query TEXT,
#     bot_response TEXT,
#     feedback TEXT,
#     elapsed_time TEXT,
#     create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );


class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    message_id: str
    response: str
    query: str


class SQLRequest(BaseModel):
    table_schemas: List[str]  # Accept a list of schemas
    query: str


class SQLResponse(BaseModel):
    response: str


class SessionResponse(BaseModel):
    session_id: str


class FeedbackRequest(BaseModel):
    message_id: str
    feedback_type: str
    session_id: Optional[str] = None


class FeedbackResponse(BaseModel):
    message: str


def get_session_id(request: Request, content_request: ChatRequest):
    # Try to get the session ID from headers, fall back to request object
    session_id = request.headers.get("Session-ID") or content_request.session_id
    if not session_id:
        raise HTTPException(status_code=422, detail="No Session-ID")
    return session_id


def validate_query(query):
    if not query.strip():
        raise HTTPException(status_code=422, detail="Query is empty")


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")


@app.post(
    "/session/create",
    response_model=SessionResponse,
    responses={
        200: {},
        500: {"description": "Unhandled error that should be reported"},
    },
)
async def create_session():
    try:
        postgres = Postgres()
        session_id = await postgres.create_session()
        return session_id
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unhandled error, Please report")


@app.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        200: {},
        500: {"description": "Unhandled error that should be reported"},
        404: {
            "description": "Session not found",
            "content": {
                "application/json": {"example": {"detail": "Session not found"}}
            },
        },
        422: {
            "description": "Unprocessable entity e.g. no session id, or no query",
            "content": {"application/json": {"example": {"detail": "Query is empty"}}},
        },
    },
)
async def chat_responder(chat_request: ChatRequest, request: Request):
    REQUEST_COUNT.labels(endpoint="/chat").inc()  # Increment request count for /chat
    start_time = time.time()

    try:
        postgres = Postgres()
        session_id = get_session_id(request, chat_request)
        validate_query(chat_request.query)
        simple_logger(f"Received chat request", session_id)
        history = await postgres.get_history(
            session_id, 1, config["postgres"]["history_length"]
        )
        if len(chat_request.query.split()) > 60:
            paraphrased_utterance, response, context = (
                "No valid query",
                RESPONSE_TEMPLATE_FOR_NO_ANSWER,
                "",
            )
        else:
            paraphrased_utterance, response, context = await chat_responder_(
                history, chat_request.query
            )
        elapsed_time = time.time() - start_time
        REQUEST_LATENCY.labels(endpoint="/chat").observe(elapsed_time)  # Record latency
        message_id = await postgres.insert_chat_row(
            session_id,
            chat_request.query,
            paraphrased_utterance,
            response,
            elapsed_time,
        )
        non_generative_agent_logger(
            session_id=session_id,
            agent="chat_responder",
            message="Chat response generated",
            input_dict={
                "user_utterance": chat_request.query,
                "paraphrased_query": paraphrased_utterance,
                "context": context,
            },
            output_dict={"response": response},
            elapsed_time=elapsed_time,
        )
        return ChatResponse(
            response=response, message_id=message_id, query=paraphrased_utterance
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        traceback.print_exc()
        elapsed_time = time.time() - start_time
        REQUEST_LATENCY.labels(endpoint="/chat").observe(elapsed_time)
        non_generative_agent_logger(
            session_id=session_id,
            agent="chat_responder",
            message="Chat response not generated",
            input_dict={
                "user_utterance": chat_request.query,
                "paraphrased_query": "",
            },
            output_dict={"response": ""},
            elapsed_time=elapsed_time,
        )

        raise HTTPException(status_code=500, detail="Unhandled error, Please report")


# Define the endpoint
@app.post(
    "/convert/sql",
    responses={
        200: {
            "description": "Successful conversion of natural language query to SQL query.",
            "content": {
                "application/json": {
                    "example": {
                        "sql_query": "SELECT name, salary FROM employees WHERE department = 'Engineering' AND salary > 70000;"
                    }
                }
            },
        },
        422: {
            "description": "Unprocessable entity, e.g., missing or invalid input.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Missing required field 'table_schemas' in the request body."
                    }
                }
            },
        },
        404: {
            "description": "Relevant schema not found in the input.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No matching schema found for the provided natural query."
                    }
                }
            },
        },
        500: {
            "description": "Internal server error. Unhandled error occurred.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An unexpected error occurred. Please try again later."
                    }
                }
            },
        },
    },
)
async def convert_to_sql(request: SQLRequest):
    start_time = time.time()
    try:
        # Extract schemas and query from the request
        table_schemas = request.table_schemas
        query = request.query

        # Use OpenAI API to generate SQL query
        response = sql_responder(query, table_schemas)
        elapsed_time = time.time() - start_time
        non_generative_agent_logger(
            session_id="",
            agent="SQL converter",
            message="SQL generated",
            input_dict={
                "user_utterance": request.query,
            },
            output_dict={"response": response},
            elapsed_time=elapsed_time,
        )
        return SQLResponse(response=response)

    except HTTPException as e:
        raise e

    except Exception as e:
        traceback.print_exc()
        elapsed_time = time.time() - start_time
        REQUEST_LATENCY.labels(endpoint="/convert").observe(elapsed_time)
        non_generative_agent_logger(
            session_id="",
            agent="SQL converter",
            message="convert SQL response not generated",
            input_dict={
                "user_utterance": request.query,
            },
            output_dict={"response": ""},
            elapsed_time=elapsed_time,
        )

        raise HTTPException(status_code=500, detail="Unhandled error, Please report")


@app.post(
    "/feedback",
    responses={
        200: {
            "content": {
                "application/json": {"example": {"message": "Feedback received"}}
            }
        },
        422: {
            "description": "Unprocessable entity e.g. no session id, or invalid feedback",
            "content": {"application/json": {"example": {"detail": "No Session-ID"}}},
        },
        404: {
            "description": "No message found with sent message id and session id",
            "content": {
                "application/json": {"example": {"detail": "Message not found"}}
            },
        },
        500: {"description": "Unhandled error that should be reported"},
    },
)
async def feedback(feedback_request: FeedbackRequest, request: Request):
    REQUEST_COUNT.labels(endpoint="/chat").inc()  # Increment request count for /chat
    start_time = time.time()

    try:
        if feedback_request.feedback_type not in ["thumb_up", "thumb_down", "flag"]:
            raise HTTPException(status_code=422, detail="Invalid feedback")

        session_id = get_session_id(request, feedback_request)
        message_id = feedback_request.message_id
        postgres = Postgres()
        message_fields = await postgres.get_message_fields(session_id, message_id)

        if not len(message_fields):
            raise HTTPException(status_code=404, detail="Message not found")
        else:
            user_query, paraphrased_query, bot_response = message_fields

        simple_logger(f"Received feedback request", session_id)
        feedback_(paraphrased_query, bot_response, "", feedback_request.feedback_type)
        await postgres.set_feedback(message_id, feedback_request.feedback_type)
        elapsed_time = time.time() - start_time
        REQUEST_LATENCY.labels(endpoint="/feedback").observe(
            elapsed_time
        )  # Record latency

        non_generative_agent_logger(
            session_id=session_id,
            agent="feedback",
            message="feedback generated",
            input_dict={
                "user_utterance": user_query,
                "paraphrased_query": paraphrased_query,
            },
            output_dict={"response": feedback_request.feedback_type},
            elapsed_time=elapsed_time,
        )

        return FeedbackResponse(message="Feedback received")

    except HTTPException as e:
        raise e

    except Exception as e:
        traceback.print_exc()
        REQUEST_LATENCY.labels(endpoint="/feedback").observe(elapsed_time)
        non_generative_agent_logger(
            session_id,
            "feedback",
            f"Error in feedback: {str(e)}",
            feedback_request.dict(),
            {},
            time.time() - start_time,
        )
        raise HTTPException(status_code=500, detail="Unhandled error, Please report")
