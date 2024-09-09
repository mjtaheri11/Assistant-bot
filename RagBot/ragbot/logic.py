import json
import random
from typing import List
import os

import torch
import numpy as np
from langchain.schema import SystemMessage
from langchain_community.chat_models import ChatOllama

from prompts import RAG_SYSTEM_PROMPT, UTTERANCE_PARAPHRASER_PROMPT
from retriever import Retriever
from config import config
from logs import simple_logger
from utils import json_cleaning

SEED = 0
torch.manual_seed(SEED)
np.random.seed(SEED)
torch.cuda.manual_seed_all(SEED)
random.seed(SEED)



def get_chat_response(prompt: str) -> str:
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://dockerize_assistant-ollama-1:11434')
    LLM_MODEL = os.getenv('LLM_MODEL', 'gemma2:9b-instruct-fp16')

    llm = ChatOllama(
        model=config["ollama"]["model_name"],
        temperature=config["ollama"]["temperature"],
        keep_alive=config["ollama"]["keep_alive"],
        seed=SEED,
        base_url=OLLAMA_HOST
    )
    messages = [SystemMessage(content=prompt)]
    response = llm.invoke(messages)  # type: ignore[arg-type]
    return response.content


def history_serializer(history: List[tuple[str, str]]) -> str:
    serialized_history = ""
    # TODO this history part should be considered effectively. I just wrote something messy.
    for question, answer in history[-2:]:
        serialized_history += f"USER: {question}\nASSISTANT: {answer}\n\n"
    return serialized_history


def utterance_paraphraser(history: List[tuple[str, str]], user_utterance: str) -> str:
    # TODO such a messy modification. resolve it as soon as you can 
    serialized_history = "\n".join(["USER: " + user_hist[0] for user_hist in history])
    prompt = UTTERANCE_PARAPHRASER_PROMPT.format(
        history=serialized_history,
        question=user_utterance,
    )
    response = get_chat_response(prompt)
    paraphrased_query = json.loads(json_cleaning(response))["answer"]
    return paraphrased_query


def query_responder(query: str, context: str, history: str) -> str:
    # TODO: Add appropriate logger.
    serialized_history = history_serializer(history)
    prompt = RAG_SYSTEM_PROMPT.format(
        context=context,
        history=serialized_history,
        question=query,
    )

    response = get_chat_response(prompt)
    return response


def prepare_final_context(query: str) -> str:
    retriever = Retriever()
    context = retriever.retrieve_context(query)[0]
    # TODO: need appropriate context management > context = context[: config["context"]["max_length"]]
    if context.strip() == "":
        raise Exception("no context fetched")
    return context


def chat_responder(
    history: List[tuple[str, str]],
    user_utterance: str,
) -> tuple[str, str, str, str]:

    ok_response_status = config["chat_responder"]["ok_status"]
    doubtful_response_status = config["chat_responder"]["doubtful_status"]
    no_answer_response_status = config["chat_responder"]["no_answer_status"]

    paraphrased_utterance = utterance_paraphraser(history, user_utterance)

    try:
        context = prepare_final_context(paraphrased_utterance)
        response = query_responder(paraphrased_utterance, context, history)
        # TODO: response should be validated
        # response_is_valid = True
        # response_is_valid = answer_validator(
        #     paraphrased_utterance,
        #     context,
        #     response,
        # )
        # if response_is_valid:
        return paraphrased_utterance, response, ok_response_status
        # else:
        #     return user_utterance, response, ok_response_status
    except Exception:
        return paraphrased_utterance, "", no_answer_response_status


def feedback(
    query: str,
    response: str,
    feedback_type: str,
) -> None:
    # TODO: there should be an appropriate caching strategy
    # cache = Cache()
    if feedback_type == "thumb_up":
        pass
        # cache.increment_thumb_up(query, response, url)
    elif feedback_type == "thumb_down":
        pass
        # cache.increment_thumb_down(query, response, url)
