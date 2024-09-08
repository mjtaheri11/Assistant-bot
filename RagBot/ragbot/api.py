import json
import argparse
import logging
import time
from datetime import datetime
from typing import List, Tuple

import requests
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from config import config
from logs import simple_logger, non_generative_agent_logger
from logic import prepare_final_context, query_responder, utterance_paraphraser
from utils import json_cleaning

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Let us build an app')
parser.add_argument('-p', '--port', default=8686, type=int, help='The port of the uvicorn')
args = parser.parse_args()

BASE_URL = f"http://0.0.0.0:{args.port}"
app = FastAPI(title="سرویس سوال و جواب همکاران سیستم (همکار بات!)")
# انتخاب تامین کننده برای رسید خرید داخلی اجباری است

# Models for request and response
class ChatRequest(BaseModel):
    history: List[Tuple[str, str]]
    user_utterance: str


class ChatResponse(BaseModel):
    user_utterance: str
    response: str
    status: str


class FeedbackRequest(BaseModel):
    query: str
    response: str
    feedback_type: str


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


@app.post("/chat", response_model=ChatResponse)
async def chat_responder(request: ChatRequest, req: Request):
    if not isinstance(request.history, list):
        raise HTTPException(status_code=400, detail="History must be a list of lists")

    session_id = req.headers.get("Session-ID", "unknown")
    simple_logger(f"Received chat request", session_id)

    ok_response_status = config["chat_responder"]["ok_status"]
    error = config["chat_responder"]["error_status"]

    start_time = time.time()
    try:
        paraphrased_utterance = utterance_paraphraser(request.history, request.user_utterance)
        context = prepare_final_context(paraphrased_utterance)
        response = query_responder(request.user_utterance, context, request.history)
        response = json.loads(json_cleaning(response))

        elapsed_time = time.time() - start_time
        output = ChatResponse(
            user_utterance=paraphrased_utterance,
            response=response["answer"],
            status=ok_response_status,
        )

        non_generative_agent_logger(
            session_id,
            "chat_responder",
            "Chat response generated",
            {"user_utterance": request.user_utterance, "history": request.history, "context": context},
            output.dict(),
            elapsed_time,
        )

        return output
    except Exception as e:
        print(e)
        elapsed_time = time.time() - start_time
        output = ChatResponse(
            user_utterance=request.user_utterance,
            response="",
            status=config["chat_responder"]["no_answer_status"],
        )

        non_generative_agent_logger(
            session_id,
            "chat_responder",
            f"Error in chat response: {str(e)}",
            {"user_utterance": request.user_utterance, "history": request.history},
            output.dict(),
            elapsed_time,
        )

        return output


@app.post("/feedback")
async def feedback(request: FeedbackRequest, req: Request):
    session_id = req.headers.get("Session-ID", "unknown")
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
