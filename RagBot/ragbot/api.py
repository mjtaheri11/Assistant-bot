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
# import aiofiles
# import aiocsv

from config import config
from logs import simple_logger, non_generative_agent_logger
from logic import prepare_final_context, query_responder, utterance_paraphraser, feedback_, chat_responder_

app = FastAPI(title="Digital Assistant")

# Models for request and response
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


def query_executor(q: str, is_insert: bool = False, insert_values: Optional[Tuple] = None, fetch_results: bool = True):
    """
    Executes a SQL query against the PostgreSQL database.

    Args:
        q (str): The SQL query to execute.
        is_insert (bool): Indicates if the query is an INSERT statement that returns a value.
        insert_values (Optional[Tuple]): Values to insert into the query.
        fetch_results (bool): Whether to fetch and return results from the query.

    Returns:
        Optional[List[Tuple]]: Fetched results if any, else None.
    """   
    conn = psycopg2.connect(
        database="chatbot",
        host="postgres", # "192.168.112.2", # 
        user="postgres",
        password="MySecretPassword123!@#",
        port="5432"
    )

    try:
        with conn:
            with conn.cursor() as cursor:
                if insert_values is not None:
                    cursor.execute(q, insert_values)
                else:
                    cursor.execute(q)

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
        conn.commit()
        conn.close()

    return output


def maintain_history(session_id: str, history_length: int):
    """
    Ensures that the number of messages for a session does not exceed history_length.
    If it does, deletes the oldest messages to maintain the limit.
    """
    # Count the total number of messages for the session
    count_query = "SELECT COUNT(*) FROM message WHERE session_id = %s;"
    count_result = query_executor(count_query, fetch_results=True, insert_values=(session_id,))
    total_messages = count_result[0][0] if count_result else 0

    if total_messages > history_length:
        # Calculate how many messages need to be deleted
        messages_to_delete = total_messages - history_length

        # Use a Common Table Expression (CTE) to delete the oldest messages
        delete_query = """
            WITH oldest_messages AS (
                SELECT message_id FROM message
                WHERE session_id = %s
                ORDER BY create_time ASC
                LIMIT %s
            )
            DELETE FROM message
            WHERE message_id IN (SELECT message_id FROM oldest_messages);
        """
        # Execute the DELETE query without fetching results
        query_executor(delete_query, fetch_results=False, insert_values=(session_id, messages_to_delete))


@app.post('/session/create', response_model=SessionResponse, responses={
    200: {},
    500: {"description": "Unhandled error that should be reported"}
})
async def create_session():
    try:
        q = "INSERT INTO public.session(history_length) VALUES (%s) RETURNING session_id;"
        sid = query_executor(q, is_insert=True, insert_values=(config['retriever']['history_length'],), fetch_results=True)

        return {
            'session_id': sid[0]
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unhandled error, Please report")


@app.post("/chat", response_model=ChatResponse, responses={
    200: {},
    500: {"description": "Unhandled error that should be reported"},
    404: {"description": "Session not found", "content": {"application/json": {"example": {"detail": "Session not found"}}}},
    422: {"description": "Unprocessable entity e.g. no session id, or no query", "content": {"application/json": {"example": {"detail": "Query is empty"}}}}
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
            q = "SELECT session_id FROM session WHERE session_id = %s;"
            result = query_executor(q, fetch_results=True, insert_values=(session_id,))
            if len(result) == 0:
                raise HTTPException(status_code=404, detail="Session not found")
                return

        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=404, detail="Session not found")
            return

        simple_logger(f"Received chat request", session_id)
        q = """
            SELECT user_query, bot_response FROM message
            WHERE session_id = %s
            ORDER BY create_time ASC
            LIMIT %s;
        """
        selected_history = query_executor(q, fetch_results=True, insert_values=(session_id, config['retriever']['history_length']))
        history = [[h[0], h[1]] for h in selected_history[-5:]]
        
        # query_history = [h[0] for h in history]
        paraphrased_utterance, response, context = chat_responder_(history, request.query)
        
        # Insert the new message into the database
        insert_query = "INSERT INTO message (session_id, user_query, bot_response) VALUES (%s, %s, %s) RETURNING message_id;"
        values = (session_id, request.query, response)
        msg_id = query_executor(insert_query, is_insert=True, insert_values=values, fetch_results=True)
        
        # Maintain the history length by deleting oldest messages if necessary
        maintain_history(session_id, config['retriever']['history_length'])
        
        elapsed_time = time.time() - start_time
        output = ChatResponse(
            response=response,
            message_id=msg_id[0],
            query=paraphrased_utterance
        )

        non_generative_agent_logger(
            session_id=session_id,
            agent="chat_responder",
            message="Chat response generated",
            input_dict={"user_utterance": request.query,
                        "paraphrased_query": paraphrased_utterance,
                        "context": context
                        },
            output_dict={"response": output.response},
            elapsed_time=elapsed_time,
        )
                
        return output

    except HTTPException as e:
        raise e

    except Exception as e:
        traceback.print_exc()
        elapsed_time = time.time() - start_time
        non_generative_agent_logger(
            session_id=session_id,
            agent="chat_responder",
            message="Chat response not generated",
            input_dict={"user_utterance": request.query,
                        "paraphrased_query": "",
                        },
            output_dict={"response": ""},
            elapsed_time=elapsed_time,
    )

        raise HTTPException(status_code=500, detail="Unhandled error, Please report")


        
CSV_FILE_PATH = 'feedback.csv'
CSV_HEADERS = ['timestamp', 'session_id', 'message_id', 'feedback_type', 'user_query', 'bot_response']

# async def append_feedback_to_csv(feedback_data):
#     async with aiofiles.open('feedback.csv', mode='a', encoding='utf-8', newline='') as f:
#         writer = aiocsv.AsyncDictWriter(f, fieldnames=CSV_HEADERS)
        
#         # If the file is new, write the header
#         if await f.tell() == 0:
#             await writer.writeheader()
        
#         await writer.writerow(feedback_data)

@app.post("/feedback", responses={
    200: {"content": {"application/json": {"example": {"message": "Feedback received"}}}},
    422: {"description": "Unprocessable entity e.g. no session id, or invalid feedback", "content": {"application/json": {"example": {"detail": "No Session-ID"}}}},
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
            q = "SELECT * FROM message WHERE message_id = %s AND session_id = %s;"
            query_ = query_executor(q, fetch_results=True, insert_values=(msg_id, session_id))

            if len(query_) == 0:
                raise HTTPException(status_code=404, detail="Message not found")

        except Exception as e:
            raise HTTPException(status_code=404, detail="Message not found")

        simple_logger(f"Received feedback request", session_id)

        output = {"message": "Feedback received"}
        if request.feedback_type not in ["thumb_up", "thumb_down", "flag"]:
            raise HTTPException(status_code=422, detail="Invalid feedback")
        temp_query = "SELECT user_query, bot_response FROM message WHERE message_id = %s AND session_id = %s;"
        response = query_executor(temp_query, fetch_results=True, insert_values=(msg_id, session_id))
        response_ = response[0][1]
        query_ = response[0][0]
        feedback_(query_, response_, "", request.feedback_type)
        elapsed_time = time.time() - start_time
        
        non_generative_agent_logger(
            session_id=session_id,
            agent="feedback",
            message="feedback generated",
            input_dict={"user_utterance": query_},
            output_dict={"response": request.feedback_type},
            elapsed_time=elapsed_time,
        )

        update_query = "UPDATE message SET feedback = %s WHERE message_id = %s RETURNING message_id;"
        result = query_executor(update_query, fetch_results=True, insert_values=(request.feedback_type, msg_id))

        # Prepare feedback data
        feedback_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            'session_id': session_id,
            'message_id': msg_id,
            'feedback_type': request.feedback_type,
            'user_query': query_,
            'bot_response': response_
        }

        # Append feedback to CSV asynchronously
        # await append_feedback_to_csv(feedback_data)

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
