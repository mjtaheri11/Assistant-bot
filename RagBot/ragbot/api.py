import os
import csv
import json
import argparse
import logging
import time
from datetime import datetime
from typing import List, Tuple, Optional

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import psycopg2
import traceback

from config import config
from logs import simple_logger, non_generative_agent_logger
from logic import (
    prepare_final_context,
    query_responder,
    utterance_paraphraser,
    feedback_,
    chat_responder_,
)

RESPONSE_TEMPLATE_FOR_NO_ANSWER = "در حال حاضر نمی‌توانم به سوال شما پاسخ دهم"
app = FastAPI(title="Digital Assistant")

# Models for request and response


# sudo docker exec -it postgres psql -U postgres -d chatbot -c "CREATE TABLE public.session (session_id UUID DEFAULT gen_random_uuid() PRIMARY KEY, history_length INT)"

# CREATE EXTENSION IF NOT EXISTS "pgcrypto";

# CREATE TABLE public.session (
#     session_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
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


class SessionResponse(BaseModel):
    session_id: str


class FeedbackRequest(BaseModel):
    message_id: str
    feedback_type: str
    session_id: Optional[str] = None


class Postgres:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.database = config["postgres"]["database"]
        self.connection_address = config["postgres"]["address"]

    def _execute_query(
        self,
        query: str,
        is_insert: bool = False,
        insert_values: Optional[Tuple] = None,
        fetch_results: bool = True,
    ):
        try:
            postgres_connection = psycopg2.connect(
                    database=self.database,
                    host="postgres", #"172.22.0.4",  #
                    user="postgres",
                    password="MySecretPassword123!@#", # add to environment variables``
                    port="5432",
                )
            with postgres_connection:
                with postgres_connection.cursor() as cursor:
                    if insert_values is not None:
                        cursor.execute(query, insert_values)
                    else:
                        cursor.execute(query)

                    if fetch_results:
                        if is_insert:
                            output = cursor.fetchone()
                        else:
                            output = cursor.fetchall()
                    else:
                        output = None

        except psycopg2.ProgrammingError as ex:
            raise ex

        finally:
            postgres_connection.commit()
            postgres_connection.close()

        return output

    def exist_session(self, session_id):
        sql_exist_session_query = (
            "SELECT session_id FROM session WHERE session_id = %s;"
        )
        result = self._execute_query(
            sql_exist_session_query, fetch_results=True, insert_values=(session_id,)
        )
        if len(result):
            return True
        return False

    def get_message_fields(self, session_id, message_id):
        sql_get_message_fileds = (
            "SELECT user_query, paraphrased_query, bot_response FROM message WHERE message_id = %s AND session_id = %s;"
        )
        message_fields = self._execute_query(
            sql_get_message_fileds,
            fetch_results=True,
            insert_values=(message_id, session_id),
        )
        if not len(message_fields):
            return []
        return message_fields[0]

    def create_session(self):
        sql_create_session_query = (
            "INSERT INTO public.session DEFAULT VALUES RETURNING session_id;"
        )
        sid = self._execute_query(
            sql_create_session_query, is_insert=True, fetch_results=True
        )
        output = SessionResponse(session_id=sid[0])
        return output

    def get_history(self, session_id, history_length):
        sql_history_query = """
            SELECT user_query, paraphrased_query, bot_response FROM message
            WHERE session_id = %s
            ORDER BY create_time DESC
            LIMIT %s;
        """
        selected_history = self._execute_query(
            sql_history_query,
            fetch_results=True,
            insert_values=(session_id, history_length)
        )
        history = [
            (
                [h[0], h[2]]
                if len(h[0]) < config["postgres"]["max_user_input_character_length"]
                else [h[1], h[2]]
            )
            for h in reversed(selected_history)
        ]
        return history

    def insert_chat_row(
        self, session_id, user_query, paraphrased_query, bot_response, elapsed_time
    ):
        values = (
            session_id,
            user_query,
            paraphrased_query,
            bot_response,
            elapsed_time,
        )
        sql_insert_query = "INSERT INTO message (session_id, user_query, paraphrased_query, bot_response, elapsed_time) VALUES (%s, %s, %s, %s, %s) RETURNING message_id;"
        message_id = self._execute_query(
            sql_insert_query, is_insert=True, insert_values=values, fetch_results=True
        )
        return message_id[0]

    def set_feedback(self, message_id, feedback_type):
        update_query = "UPDATE message SET feedback = %s WHERE message_id = %s RETURNING message_id;"
        _ = self._execute_query(
            update_query,
            fetch_results=True,
            insert_values=(feedback_type, message_id),
        )


def get_session_id(request: Request, content_request: ChatRequest):
    # Try to get the session ID from headers, fall back to request object
    session_id = request.headers.get("Session-ID") or content_request.session_id
    if not session_id:
        raise HTTPException(status_code=422, detail="No Session-ID")
    return session_id


def validate_query(query):
    if not query.strip():
        raise HTTPException(status_code=422, detail="Query is empty")



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
        session_id = postgres.create_session()
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

    try:
        start_time = time.time()
        postgres = Postgres()
        session_id = get_session_id(request, chat_request)
        validate_query(chat_request.query)
        simple_logger(f"Received chat request", session_id)
        history = postgres.get_history(session_id, config["postgres"]["history_length"])
        if len(chat_request.query.split()) > 60:
            paraphrased_utterance, response, context = "No valid query", RESPONSE_TEMPLATE_FOR_NO_ANSWER, ""
        else:
            paraphrased_utterance, response, context = chat_responder_(
                history, chat_request.query
            )
        elapsed_time = time.time() - start_time
        message_id = postgres.insert_chat_row(
            session_id, chat_request.query, paraphrased_utterance, response, elapsed_time
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
    try:
        if feedback_request.feedback_type not in ["thumb_up", "thumb_down", "flag"]:
            raise HTTPException(status_code=422, detail="Invalid feedback")

        start_time = time.time()
        session_id = get_session_id(request, feedback_request)
        message_id = feedback_request.message_id
        postgres = Postgres()
        message_fields = postgres.get_message_fields(session_id, message_id)
        
        if not len(message_fields):
            raise HTTPException(status_code=404, detail="Message not found")
        else:
            user_query, paraphrased_query, bot_response = message_fields
            
        simple_logger(f"Received feedback request", session_id)

        output = {"message": "Feedback received"}

        feedback_(paraphrased_query, bot_response, "", feedback_request.feedback_type)
        postgres.set_feedback(message_id, feedback_request.feedback_type)
        elapsed_time = time.time() - start_time
        
        non_generative_agent_logger(
            session_id=session_id,
            agent="feedback",
            message="feedback generated",
            input_dict={"user_utterance": user_query, "paraphrased_query": paraphrased_query},
            output_dict={"response": feedback_request.feedback_type},
            elapsed_time=elapsed_time,
        )
        
        return output

    except HTTPException as e:
        raise e

    except Exception as e:
        traceback.print_exc()
        non_generative_agent_logger(
            session_id,
            "feedback",
            f"Error in feedback: {str(e)}",
            feedback_request.dict(),
            {},
            time.time() - start_time,
        )

        raise HTTPException(status_code=500, detail="Unhandled error, Please report")
