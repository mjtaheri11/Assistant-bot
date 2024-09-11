import json
import argparse
import logging
import time
from datetime import datetime
from typing import List, Tuple, Optional

import requests
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import psycopg2
import traceback

from config import config
from logs import simple_logger, non_generative_agent_logger
from logic import prepare_final_context, query_responder, utterance_paraphraser

app = FastAPI(title="Digital Assistant")

# انتخاب تامین کننده برای رسید خرید داخلی اجباری است

# Models for request and response
# TODO api_url should be a hyper parameter
# 

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
    session_id: str


def query(q, is_insert=False, insert_values=None):   
    # import pdb
    # pdb.set_trace()
    conn = psycopg2.connect(database="chatbot",
        host="172.19.0.1", #"postgres",
        user="postgres",
        password="MySecretPassword123!@#",
        port="5432")

    try:
        with conn:
            with conn.cursor() as cursor:
                if insert_values is not None:
                    cursor.execute(q, insert_values)

                else:
                    cursor.execute(q)


                if is_insert:
                    output = cursor.fetchone()

                else:
                    output = cursor.fetchall()

                
    except psycopg2.ProgrammingError as ex:
        raise ex
    
    finally:
        conn.commit()
        conn.close()

    return output


def session_create(api_url: str = "http://185.13.230.222:8691"): 
    """
    Sends a POST request to create a session and returns the session ID if successful.

    :param api_url: The URL for the session creation API endpoint.
    :return: The session ID if successful, None otherwise.
    """
    try:
        response = requests.post(f"{api_url}/session/create")
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response and extract the session_id
            data = response.json()
            session_id = data.get('session_id')
            print(f"Session ID: {session_id}")
            return session_id
        else:
            # Handle any other status codes
            return None

    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the request
        return None

def chat_request(session_id: str, query: str, api_url: str = "http://185.13.230.222:8691"):
    # Define the request data
    chat_data = {
        "query": query,
        "session_id": session_id,  # Assume this is generated or fetched from somewhere
    }

    # Send the POST request with the chat data
    headers = {"Session-ID": session_id}
    response = requests.post(f"{api_url}/chat", json=chat_data, headers=headers)

    # Handle the different response status codes
    json_response = response.json()
    if response.status_code == 200:
        return {"status": "success", "query": json_response["query"], "response": json_response["response"], "message_id": json_response["message_id"]}
    elif response.status_code == 404:
        return {"status": "error", "query": "", "response": "", "message_id": ""}
    elif response.status_code == 422:
        return {"status": "error", "query": "", "response": "", "message_id": ""}
    elif response.status_code == 500:
        return {"status": "error", "query": "", "response": "", "message_id": ""}
    else:
        return {"status": "error", "query": "", "response": "", "message_id": ""}


def send_feedback(message_id: str, feedback_type: str, session_id: str, api_url: str = "http://185.13.230.222:8691"):
    # Define the request data
    feedback_data = {
        "message_id": message_id,
        "feedback_type": feedback_type,
        "session_id": session_id
    }

    # Send the POST request with the feedback data
    response = requests.post(f"{api_url}/feedback", json=feedback_data, headers={"Session-ID": session_id})


@app.post('/session/create', response_model=SessionResponse, responses={
    200: {},
    500: {"description": "Unhandled error that should be reported"}
})
async def create_session():
    try:
        q = f"INSERT INTO public.session(history_length) VALUES ({config['retriever']['history_length']}) RETURNING session_id;"
        sid = query(q, True)

        return {
            'session_id': sid[0]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail="Unhandled error, Please report")


@app.post("/chat", response_model=ChatResponse, responses={
    200: {},
    500: {"description": "Unhandled error that should be reported"},
    404: {"description": "Session not found", "content": {"application/json": {"example": {"detail": "Session not found"}}}},
    422: {"description": "unprocessable entity e.g. no session id, or no query", "content": {"application/json": {"example": {"detail": "Query is empty"}}}}
})
async def chat_responder(request: ChatRequest, req: Request):
    try:
        start_time = time.time()
        
        session_id = req.headers.get("Session-ID", None)
        if session_id is None:
            session_id = request.session_id

            if session_id is None:
                raise HTTPException(status_code=422, detail="No Session-ID")
                return

        if len(request.query.strip()) == 0:
            raise HTTPException(status_code=422, detail="Query is empty")
            return

        try:
            q = f"SELECT session_id FROM session WHERE session_id='{session_id}';"
            result = query(q)
            if len(result) == 0:
                raise HTTPException(status_code=404, detail="Session not found")
                return

        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=404, detail="Session not found")
            return

        simple_logger(f"Received chat request", session_id)
        ok_response_status = config["chat_responder"]["ok_status"]
        error = config["chat_responder"]["error_status"]

        q = f"SELECT user_query, bot_response FROM message WHERE session_id='{session_id}' ORDER BY create_time DESC LIMIT {config['retriever']['history_length']};"
        selected_history = query(q)
        history = [[h[0], h[1]] for h in selected_history[::-1]]
        
        query_history = [h[0] for h in history]
        paraphrased_utterance_dict = utterance_paraphraser(query_history, request.query)
        paraphrased_utterance = paraphrased_utterance_dict["rephrased_query"]
        context = prepare_final_context(paraphrased_utterance)
        
        json_response = query_responder(request.query, context, history)
        response = json_response["answer"]

        q = "INSERT INTO message (session_id, user_query, bot_response) VALUES (%s, %s, %s) RETURNING message_id;"
        values = (session_id, request.query, response)
        msg_id = query(q, True, values)
        # import pdb
        # pdb.set_trace()
        
        elapsed_time = time.time() - start_time
        output = ChatResponse(
            response=response,
            message_id=msg_id[0],
            query=paraphrased_utterance
        )

        non_generative_agent_logger(
            session_id,
            "chat_responder",
            "Chat response generated",
            {"user_utterance": request.query, "history": history},
            output.dict(),
            elapsed_time,
        )
            
        return output

    except HTTPException as e:
        raise e

    except Exception as e:
        traceback.print_exc()
        elapsed_time = time.time() - start_time
        non_generative_agent_logger(
            session_id,
            "chat_responder",
            f"Error in chat response: {str(e)}",
            {"user_utterance": request.query, "history": history},
            {},
            elapsed_time,
        )


        raise HTTPException(status_code=500, detail="Unhandled error, Please report")
        

@app.post("/feedback", responses={
    200: {"content": {"application/json": {"example": {"message": "Feedback received"}}}},
    422: {"description": "Unprocessable entity e.g. no session id, or invalid feedabck", "content": {"application/json": {"example": {"detail": "No Session-ID"}}}},
    404: {"description": "No message found with sent message id and session id", "content": {"application/json": {"example": {"detail": "Message not found"}}}},
    500: {"description": "Unhandled error that should be reported"}
})
async def feedback(request: FeedbackRequest, req: Request):
    try:
        start_time = time.time()
        
        session_id = req.headers.get("Session-ID", None)
        if session_id is None:
            session_id = request.session_id
            
            if session_id is None:
                raise HTTPException(status_code=422, detail="No Session-ID")

        msg_id = request.message_id
        
        try:
            q = f"SELECT FROM message WHERE message_id='{msg_id}' and session_id='{session_id}';"
            result = query(q)

            if len(result) == 0:
                raise HTTPException(status_code=404, detail="Message not found")

        except Exception as e:
            raise HTTPException(status_code=404, detail="Message not found")


        simple_logger(f"Received feedback request", session_id)

        output = {"message": "Feedback received"}
        
        if request.feedback_type not in ["thumb_up", "thumb_down", "flag"]:
            raise HTTPException(status_code=422, detail="Invalid feedback")

        elapsed_time = time.time() - start_time

        non_generative_agent_logger(
            session_id,
            "feedback",
            f"Feedback processed: {request.feedback_type}",
            request.dict(),
            output,
            elapsed_time,
        )

        q = f"UPDATE message SET feedback='{request.feedback_type}' WHERE message_id='{msg_id}' RETURNING message_id;"
        result = query(q)

        return output
    
    except HTTPException as e:
        raise e

    except Exception as e:
        traceback.print_exc() 

        non_generative_agent_logger(
            session_id,
            "feedback",
            f"Error in feedback: {str(e)}",
            request.dict(),
            {},
            time.time() - start_time,
        )
        
        
        raise HTTPException(status_code=500, detail="Unhandled error, Please report")


