import json
import argparse
import logging
import time
from datetime import datetime
from typing import List, Tuple

import requests
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import psycopg2

from config import config
from logs import simple_logger, non_generative_agent_logger
from logic import query_responder, prepare_final_context

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Let us build an app')
parser.add_argument('-p', '--port', default=8686, type=int, help='The port of the uvicorn')
args = parser.parse_args()
 
BASE_URL = f"http://localhost:{args.port}"

app = FastAPI(title="سرویس سوال و جواب همکاران سیستم (همکار بات!)")
# انتخاب تامین کننده برای رسید خرید داخلی اجباری است

# Models for request and response

class ChatRequest(BaseModel):
    query: str
    session_id: str


class ChatResponse(BaseModel):
    message_id: str
    response: str


class FeedbackRequest(BaseModel):
    message_id: str
    feedback_type: str
    session_id: str


def chat_request(user_utterance, history, session_id=-1):
    url = f"{BASE_URL}/chat"

    payload = {"history": history, "user_utterance": user_utterance}
    headers = {
        "Content-Type": "application/json",
        "Session-ID": session_id
    }
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        # TODO: here we should write a propoer logger
        # response.text
        return None


def send_feedback(query, response, feedback_type, session_id=-1):
    url = f"{BASE_URL}/feedback"

    payload = {"query": query, "response": response, "feedback_type": feedback_type}
    headers = {
        "Content-Type": "application/json",
        "Session-ID": session_id
    }
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        # TODO: here we should write a propoer logger
        # response.text
        return None


def query(q, is_insert=False, insert_values=None):
    conn = psycopg2.connect(database="chatbot",
        host="postgres",
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
        print("...", ex)
        raise ex
    
    finally:
        conn.commit()
        conn.close()

    return output

@app.post('/session/create')
async def create_session():
    q = "INSERT INTO public.session(history_length) VALUES (5) RETURNING session_id;"
    sid = query(q, True)

    return {
        'session_id': sid[0]
    }


@app.post("/chat", response_model=ChatResponse)
async def chat_responder(request: ChatRequest, req: Request):
    if not isinstance(request.query, str):
        raise HTTPException(status_code=400, detail="Query must be a string")

    session_id = req.headers.get("Session-ID", None)
    if session_id is None:
        try:
            session_id = request.session_id

        except Exception as e:
            print(e)
            raise HTTPException(status_code=400, detail="No Session-ID")

    print('SID =', session_id)
    simple_logger(f"Received chat request", session_id)
    ok_response_status = config["chat_responder"]["ok_status"]
    error = config["chat_responder"]["error_status"]

    start_time = time.time()
    try:
        context = prepare_final_context(request.query)

        q = f"SELECT user_query, bot_response FROM message WHERE session_id='{session_id}' ORDER BY create_time DESC LIMIT 5;"
        selected_history = query(q)
        history = [[h[0], h[1]] for h in selected_history[::-1]]

        response = query_responder(request.query, context, history)
        response = json.loads(response)

        q = "INSERT INTO message (session_id, user_query, bot_response) VALUES (%s, %s, %s) RETURNING message_id;"
        values = (session_id, request.query, response)
        msg_id = query(q, True, values)
        
        elapsed_time = time.time() - start_time
        output = ChatResponse(
            response=response,
            message_id=msg_id[0]
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

    except Exception as e:
        print(e)
        elapsed_time = time.time() - start_time
        
        non_generative_agent_logger(
            session_id,         
            "chat_responder",
            f"Error in chat response: {str(e)}",
            {"user_utterance": request.query, "history": history},
            output.dict(),
            elapsed_time,                                                                                                                           
        )

        raise HTTPException(status_code=500, detail=".....")

                                            return outputapp.post("/feedback")
async def feedback(request: FeedbackRequest, req: Request):
    session_id = req.headers.get("Session-ID", None)
    if session_id is None:
        try:
            session_id = request.session_id
            
        except Exception as e:
            print(e)
            raise HTTPException(status_code=400, detail="No Session-ID")
    
    try:
        msg_id = request.message_id

    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="No message id")

    simple_logger(f"Received feedback request", session_id)

    start_time = time.time()
    output = {"message": "Feedback received"}
    try:
        if request.feedback_type not in ["thumb_up", "thumb_down", "flag"]:
            raise ValueError("Invalid feedback type")

        # TODO: Implement appropriate caching strategy
        # cache = Cache()
        # if request.feedback_type == "thumb_up":
        #     cache.increment_thumb_up(request.query, request.response, url)
        # elif request.feedback_type == "thumb_down":
        #     cache.increment_thumb_down(request.query, request.response, url)

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
        print(result)

        return output
    except Exception as e:
        elapsed_time = time.time() - start_time
        error_output = {"error": str(e)}

        non_generative_agent_logger(
            session_id,
            "feedback",
            f"Error in feedback: {str(e)}",
            request.dict(),
            error_output,
            elapsed_time,
        )

        raise HTTPException(status_code=422, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=args.port)
