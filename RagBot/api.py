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
from fastapi import FastAPI, HTTPException, Request, Query
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
    sql_responder_,
    utterance_paraphraser,
    module_proposer,
    router_SQL_QA,
)
from src.logs import non_generative_agent_logger, simple_logger

RESPONSE_TEMPLATE_FOR_NO_ANSWER = "در حال حاضر نمی‌توانم به سوال شما پاسخ دهم"
MODULE_CLARIFICATION_RESPONSE_TEMPLATE = "لطفا ماژول مدنظر سوال خود را انتخاب کنید"
app = FastAPI(title="Digital Assistant")

# Define Prometheus metrics
REQUEST_COUNT = Counter("api_http_requests_total", "Total API Requests", ["endpoint"])
REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds", "Latency of API Requests", ["endpoint"]
)


class SessionResponse(BaseModel):
    session_id: str


class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    tenant_name: Optional[str] = None
    user_code: Optional[str] = None
    on_click: Optional[bool] = False


class ChatResponse(BaseModel):
    message_id: str
    response: str
    query: str
    is_sql: bool = False
    do_suggest: bool = False
    choices: List[str] = []
    

class CreateSessionRequest(BaseModel):
    tenant_name: str = ""
    user_code: str = ""
    

class HistoryResponse(BaseModel):
    history: List[dict]  # Assuming history is a list of lists of strings
    

class HistoryRequest(BaseModel):
    page_index: int = 1
    page_size: int = 5
    session_id: str
    contain_paraphrase: str = False


class GetSessionsResponse(BaseModel):
    response: List[dict]  


class MakeRequest(BaseModel):
    message_id: str
    session_id: str
    answer: Optional[str]


class MakeResponse(BaseModel):
    response: Optional[str]


class FeedbackRequest(BaseModel):
    message_id: str
    feedback_type: str
    session_id: Optional[str] = None  # Add default value
    tenant_name: Optional[str] = None
    user_code: Optional[str] = None


class FeedbackResponse(BaseModel):
    message: str


def get_session_id(request: Request, content_request: ChatRequest):
    # Try to get the session ID from headers, fall back to request object
    session_id = request.headers.get("Session-ID") or content_request.session_id
    if not session_id:
        raise HTTPException(status_code=422, detail="No Session-ID")
    return session_id

def get_tenant_name(content_request: BaseModel):
    if hasattr(content_request, "tenant_name"):
        if content_request.tenant_name: 
            return content_request.tenant_name
    return ""
    

def get_user_code(content_request: BaseModel):
    if hasattr(content_request, "user_code"):
        if content_request.user_code: 
            return content_request.user_code
    return ""

    
def validate_query(query):
    if not query.strip():
        raise HTTPException(status_code=422, detail="Query is empty")


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")


@app.get(
    "/sessions",
    response_model=GetSessionsResponse,
    responses={
        200: {},
        500: {"description": "Unhandled error that should be reported"},
    }
)
async def get_latest_sessions():
    try:
        postgres = Postgres()
        sessions = await postgres.get_latest_sessions()
        return GetSessionsResponse(response=sessions)
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise e


@app.get(
    "/chat",
    response_model=HistoryResponse,
    responses={
        200: {},
        500: {"description": "Unhandled error that should be reported"},
    },
)
async def get_history(
    request: Request,
    page_index: int = Query(1, alias="page_index"),  # Default to 1
    page_size: int = Query(5, alias="page_size"),    # Default to 5
    session_id: str = Query(..., alias="session_id"), # Required parameter
    contain_paraphrase: bool = Query(False, alias="contain_paraphrase"), # Default to False
):
    try:
        postgres = Postgres()
        simple_logger(f"Received history request", session_id)
        history = await postgres.get_history(
            session_id, page_index, page_size, contain_paraphrase
        )
        
        return HistoryResponse(history=history)

    except HTTPException as e:
        raise e

    except Exception as e:
        traceback.print_exc()
        # TODO: add a proper logger to this function
        raise HTTPException(status_code=500, detail="Unhandled error, Please report")

@app.post(
    "/session/create",
    response_model=SessionResponse,
    responses={
        200: {},
        500: {"description": "Unhandled error that should be reported"},
    },
)
async def create_session(create_session_request: Optional[CreateSessionRequest] = None):
    start_time = time.time()
    try:
        postgres = Postgres()  # Assuming Postgres is your DB class
        session_id = await postgres.create_session()
        
        if create_session_request is None:
            tenant_name = ""
            user_code = ""
        else:
            tenant_name = create_session_request.tenant_name
            user_code = create_session_request.user_code
        elapsed_time = time.time() - start_time
        non_generative_agent_logger(
            session_id=session_id.get("session_id"),
            tenant_name=tenant_name,
            user_code=user_code,
            agent="session_creator",
            message="session created",
            input_dict={
                "tenant_name": tenant_name,
                "user_code": user_code,
            },
            output_dict={"response": session_id.get("session_id")},
            elapsed_time=elapsed_time,
        )
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
    is_sql = False
    context = ""
    agent = "chat_responder"
    message = "Chat response generated"
    choices = []
    user_code = get_user_code(chat_request)
    tenant_name = get_tenant_name(chat_request)
    do_suggest = False
     
    try:
        postgres = Postgres()
        session_id = get_session_id(request, chat_request)
        validate_query(chat_request.query)
        history = await postgres.get_history(
            session_id,
            1,
            config["postgres"]["history_length"],
            True
        )        
        if len(chat_request.query.split()) > 60:
            paraphrased_utterance, response, context = (
                "No valid query",
                RESPONSE_TEMPLATE_FOR_NO_ANSWER,
                "",
            )
        else:
            selected_history = [[h["query"], h["response"]] if len(h["query"]) < 60 else [h["paraphrased_query"], h["response"]] for h in history]
            if chat_request.on_click:
                is_sql = True
                agent = "sql_responder"
                paraphrased_utterance, message_id = history[-1]["paraphrased_query"], str(history[-1]["message_id"]) # TODO: in the near future, this should be changed to paraphrased_query 
                detected_module = chat_request.query
                response = await sql_responder_(
                    paraphrased_utterance,
                    detected_module
                )
                message = "table response generated"
                elapsed_time = time.time() - start_time
                _ = await postgres.update_on_click_chat_row(message_id, response, elapsed_time)            
            else:
                paraphrased_utterance, response, context = await chat_responder_(
                    selected_history, chat_request.query
                )
                if not response:
                    response = MODULE_CLARIFICATION_RESPONSE_TEMPLATE
                    elapsed_time = time.time() - start_time
                    message_id = await postgres.insert_chat_row(
                        session_id,
                        chat_request.query,
                        paraphrased_utterance,
                        "",
                        elapsed_time,
                    )
                    response = MODULE_CLARIFICATION_RESPONSE_TEMPLATE
                    do_suggest = True
                    agent = "module_clarification"
                    message = "modules proposed"
                    choices = await module_proposer()
                else:
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
            tenant_name=tenant_name,
            user_code=user_code,
            agent=agent,
            message=message,
            input_dict={
                "user_utterance": chat_request.query,
                "paraphrased_query": paraphrased_utterance,
                "context": context,
            },
            output_dict={
                "response": response,
                "is_sql": is_sql,
                "do_suggest": do_suggest,
                "choices": choices
            },
            elapsed_time=elapsed_time,
        )
        return ChatResponse(
            response=response, 
            message_id=message_id, 
            query=paraphrased_utterance, 
            is_sql=is_sql,
            choices=choices,
            do_suggest=do_suggest
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        traceback.print_exc()
        elapsed_time = time.time() - start_time
        REQUEST_LATENCY.labels(endpoint="/chat").observe(elapsed_time)
        non_generative_agent_logger(
            session_id=session_id,
            tenant_name=tenant_name,
            user_code=user_code,
            agent="chat_responder",
            message="exception happened",
            input_dict={
                "user_utterance": chat_request.query,
                "paraphrased_query": "",
            },
            output_dict={
                "response": "",
                "do_suggest": do_suggest,
                "choices": choices},
            elapsed_time=elapsed_time,
        )

        raise HTTPException(status_code=500, detail="Unhandled error, Please report")


class SQLRequest(BaseModel):
    session_id: str = ""
    query: str
    on_click: Optional[bool] = False

class SQLResponse(BaseModel):
    response: str
    do_suggest: bool = False
    choices: List[str] = []
    message_id: str
    
    
@app.post(
    "/chat/sql",
    response_model=SQLResponse,
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
async def sql_responder(sql_request: SQLRequest, request: Request):
    REQUEST_COUNT.labels(endpoint="/chat").inc()  # Increment request count for /chat
    start_time = time.time()

    try:
        postgres = Postgres()
        session_id = get_session_id(request, sql_request)
        if sql_request.on_click:
            history = await postgres.get_history(
                session_id,
                1,
                1,
                True
            )
            user_question, message_id = history[0]["query"], str(history[0]["message_id"]) # TODO: in the near future, this should be changed to paraphrased_query 
            detected_module = sql_request.query
            response = await sql_responder_(
                user_question,
                detected_module
            )
            elapsed_time = time.time() - start_time
            await postgres.update_on_click_chat_row(message_id, response, elapsed_time)            
            choices = []
        else:
            elapsed_time = time.time() - start_time
            message_id = await postgres.insert_chat_row(
                session_id,
                sql_request.query,
                sql_request.query,
                "",
                elapsed_time,
            )
            response = ""
            do_suggest = True
            choices = await module_proposer()

        return SQLResponse(
            response=response,
            do_suggest=False,
            choices=choices,
            message_id=message_id
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        traceback.print_exc()
        elapsed_time = time.time() - start_time
        raise HTTPException(status_code=500, detail="Unhandled error, Please report")


class ModuleRequest(BaseModel):
    query: str
    

class ModuleResponse(BaseModel):
    response: str = ""
    
    
@app.post(
    "/chat/module",
    response_model=ModuleResponse,
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
async def detect_module(module_request: ModuleRequest, request: Request):
    try:
        context = await prepare_final_context(module_request.query)
        response = await router_SQL_QA(module_request.query, context)
        return ModuleResponse(response=response)

    except HTTPException as e:
        raise e

    except Exception as e:
        traceback.print_exc()
        # REQUEST_LATENCY.labels(endpoint="/MakeResponse").observe(elapsed_time)
        # non_generative_agent_logger(
        #     session_id,
        #     "feedback",
        #     f"Error in feedback: {str(e)}",
        #     feedback_request.dict(),
        #     {},
        #     time.time() - start_time,
        # )
        raise HTTPException(status_code=500, detail="Unhandled error, Please report")

# TODO
@app.post(
    "/chat/queries/id/response",
    response_model=MakeResponse,
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
async def make_response(make_request: MakeRequest, request: Request):
    try:
        postgres = Postgres()
        message_fields = await postgres.get_message_fields(session_id, message_id)

        if not len(message_fields):
            raise HTTPException(status_code=404, detail="Message not found")
        else:
            user_query, paraphrased_query, sql_query = message_fields

        # response = make_response(query, answer)
        return MakeResponse(response=response)

    except HTTPException as e:
        raise e

    except Exception as e:
        traceback.print_exc()
        # REQUEST_LATENCY.labels(endpoint="/MakeResponse").observe(elapsed_time)
        # non_generative_agent_logger(
        #     session_id,
        #     "feedback",
        #     f"Error in feedback: {str(e)}",
        #     feedback_request.dict(),
        #     {},
        #     time.time() - start_time,
        # )
        raise HTTPException(status_code=500, detail="Unhandled error, Please report")


@app.post(
    "/feedback",
    responses={
        200: {"content": {"application/json": {"example": {"message": "Feedback received"}}}},
        422: {"description": "Invalid feedback", "content": {"application/json": {"example": {"detail": "No Session-ID"}}}},
        404: {"description": "Message not found", "content": {"application/json": {"example": {"detail": "Message not found"}}}},
        500: {"description": "Unhandled error"},
    },
)
async def feedback(feedback_request: FeedbackRequest, request: Request):
    endpoint = "/feedback"
    REQUEST_COUNT.labels(endpoint=endpoint).inc()
    start_time = time.time()
    try:
        # validate_feedback(feedback_request)
        tenant_name = get_tenant_name(feedback_request)
        user_code = get_user_code(feedback_request)

        session_id = get_session_id(request, feedback_request)
        if session_id is None:
            session_id = feedback_request.session_id


            if session_id is None:
                raise HTTPException(status_code=422, detail="No Session-ID")

        message_fields = await fetch_message_fields(
            session_id, feedback_request.message_id
        )

        log_feedback_request(session_id)
        result = await process_feedback(feedback_request, message_fields)

        log_feedback_response(session_id, tenant_name, user_code, feedback_request, message_fields, start_time)
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        handle_unexpected_error(e, session_id, feedback_request, start_time)


# def validate_feedback(feedback_request: FeedbackRequest):
#     if feedback_request.feedback_type not in ["thumb_up", "thumb_down", "flag"]:
#         raise HTTPException(status_code=422, detail="Invalid feedback")

def validate_feedback(feedback_request: FeedbackRequest):
    if feedback_request.feedback_type not in ["thumb_up", "thumb_down", "flag"]:
        raise HTTPException(status_code=422, detail="Invalid feedback")


async def fetch_message_fields(session_id, message_id):
    postgres = Postgres()
    message_fields = await postgres.get_message_fields(session_id, message_id)

    if not message_fields:
        raise HTTPException(status_code=404, detail="Message not found")

    return message_fields


async def process_feedback(feedback_request, message_fields):
    message_id = feedback_request.message_id
    postgres = Postgres()
    result = await postgres.set_feedback(message_id, feedback_request.feedback_type)

    if result:
        # user_query, paraphrased_query, bot_response = message_fields
        # await feedback_(paraphrased_query, bot_response, "", feedback_request.feedback_type)
        return FeedbackResponse(message="feedback received")
    return FeedbackResponse(message="duplicate feedback")


def log_feedback_request(session_id):
    simple_logger("Received feedback request", session_id)


def log_feedback_response(session_id, tenant_name, user_code, feedback_request, message_fields, start_time):
    elapsed_time = time.time() - start_time
    REQUEST_LATENCY.labels(endpoint="/feedback").observe(elapsed_time)

    user_query, paraphrased_query, _ = message_fields
    non_generative_agent_logger(
        session_id=session_id,
        tenant_name=tenant_name,
        user_code=user_code,
        agent="feedback",
        message="feedback generated",
        input_dict={
            "user_utterance": user_query,
            "paraphrased_query": paraphrased_query,
        },
        output_dict={"response": feedback_request.feedback_type},
        elapsed_time=elapsed_time,
    )


def handle_unexpected_error(exception, tenant_name, user_code, session_id, feedback_request, start_time):
    elapsed_time = time.time() - start_time
    REQUEST_LATENCY.labels(endpoint="/feedback").observe(elapsed_time)

    traceback.print_exc()
    non_generative_agent_logger(
        session_id,
        tenant_name,
        user_code,
        "feedback",
        f"Error in feedback: {str(exception)}",
        feedback_request.dict(),
        {},
        elapsed_time,
    )
    raise HTTPException(status_code=500, detail="Unhandled error, Please report")
