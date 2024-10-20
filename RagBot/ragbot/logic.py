import json
import random
from typing import List
import os

import torch
import numpy as np
from langchain.schema import SystemMessage
from langchain_community.chat_models import ChatOllama

from prompts import RAG_SYSTEM_PROMPT, UTTERANCE_PARAPHRASER_PROMPT, SUGGEST_QUESTIONS_FROM_CONTEXT_PROMPT
from retriever import Retriever
from config import config
from cache import Cache
from logs import simple_logger
from utils import json_cleaning, json_text_cleaning

SEED = 44
torch.manual_seed(SEED)
np.random.seed(SEED)
torch.cuda.manual_seed_all(SEED)
random.seed(SEED)  


def get_chat_response(prompt: str) -> str:
    # OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://dockerize_assistant-ollama-1:11434')
    # LLM_MODEL = os.getenv('LLM_MODEL', 'gemma2:9b-instruct-fp16')
    print("Character Length of the prompt: " , len(prompt))
    print("words length of the prompt: ", len(prompt.split()))
    llm = ChatOllama(
        model=config["ollama"]["model_name"],
        temperature=config["ollama"]["temperature"],
        keep_alive=config["ollama"]["keep_alive"],
        seed=SEED,
        # base_url="127.0.0.1:8089"
        base_url="http://ollama:11434",
        # base_url=OLLAMA_HOST
    )
    messages = [SystemMessage(content=prompt)]
    response = llm.invoke(messages)  # type: ignore[arg-type]
    return response.content


def get_cache_response(
    query: str,
    threshold: float = config["cache"]["alpha_threshold"],
) -> tuple[str, str]:
    knn = 1
    cache = Cache()

    records = cache.get_embedding_match(
        query=query,
        threshold=threshold,
        knn=knn,
    )
    if records and records[0]["thumb_up"] > 0:
        return records[0]["response"], records[0]["url"]
    else:
        return "", ""


def generate_followup_queries(question: str, context: str) -> List[str]:
    # TODO: Add appropriate logger.
    prompt = SUGGEST_QUESTIONS_FROM_CONTEXT_PROMPT.format(
        context=context,
        number_of_questions=config["followup_query_generator"][
            "number_of_suggested_queries"
        ],
        question=question,
    )

    response = get_chat_response(prompt)

    return [
        question.lstrip("123456789۱۲۳۴۵۶۷۸۹.- ") for question in response.split("\n")
    ]

def history_serializer(history: List[tuple[str, str]]) -> str:
    serialized_history = ""
    # TODO this history part should be considered effectively. I just wrote something messy.
    for question, answer in history:
        serialized_history += f"USER: {question}\nASSISTANT: {answer}\n\n"
    return serialized_history


def utterance_paraphraser(history: List[tuple[str, str]], user_utterance: str) -> str:
    # TODO such a messy modification. resolve it as soon as you can 
    # serialized_history = "\n".join(["USER: " + user_hist[0] + "\n" + "ASSISTANT" + user_hist[1] for user_hist in history])
    # import pdb
    # pdb.set_trace()
    serialized_history = history_serializer(history)
    prompt = UTTERANCE_PARAPHRASER_PROMPT.format(
        history=serialized_history,
        question=user_utterance,
    )
    response = get_chat_response(prompt)
    # import pdb
    # pdb.set_trace()
    # paraphrased_query = json_cleaning(response)
    # paraphrased_query_dict = json_text_cleaning(paraphrased_query, key="rephrased_question")
    # return paraphrased_query_dict
    return response

def query_responder(query: str, context: str, history: str) -> str:
    # TODO: Add appropriate logger.
    serialized_history = history_serializer(history)
    prompt = RAG_SYSTEM_PROMPT.format(
        context=context,
        # history=serialized_history,
        question=query,
    )
    response = get_chat_response(prompt)
    return response.replace("متن", "دانش")
    # cleaned_response = json_cleaning(response)
    # cleaned_response_dict = json_text_cleaning(cleaned_response, "answer")
    # return cleaned_response_dict

def prepare_final_context(query: str) -> str:
    cache = Cache()
    records = cache.get_embedding_match(
        query,
        config["cache"]["beta_threshold"],
        config["cache"]["knn"],
    )
    
    context = "\n\n".join(
        "Q: " + result["query"] + "\n" + "A: " + result["response"]
        for result in reversed(records)
        if result["query"].strip() != ""
    )
    
    context = "\n\n".join(
        "Q: " + result["query"] + "\n" + "A: " + result["response"]
        for result in reversed(records)
        if result["query"].strip() != ""
    )
    # import pdb
    # pdb.set_trace()
    retriever = Retriever()
    context = retriever.retrieve_context(query) + "\n\n" + context
    # TODO: need appropriate context management > context = context[: config["context"]["max_length"]]
    # if context.strip() == "":
    #     raise Exception("no context fetched")
    return context


def chat_responder_(
    history: List[tuple[str, str]],
    user_utterance: str,
) -> tuple[str, str, str, str]:

    # import pdb
    # pdb.set_trace()
    response, url = get_cache_response(
        user_utterance,
    )
    if response:
        return user_utterance, response, ""

    paraphrased_utterance_dict = utterance_paraphraser(history, user_utterance)
    # paraphrased_utterance = paraphrased_utterance_dict["rephrased_question"]
    paraphrased_utterance = paraphrased_utterance_dict
    response, url = get_cache_response(
        paraphrased_utterance,
    )
    if response:
        return paraphrased_utterance, response, ""

    context = prepare_final_context(paraphrased_utterance)
    json_response = query_responder(paraphrased_utterance, context, history)
    # json_response = fix_asterisks(json_response)
    # return paraphrased_utterance, json_response["answer"], context
    return paraphrased_utterance, json_response, context

def feedback_(
    query: str,
    response: str,
    url: str,
    feedback_type: str,
) -> None:
    cache = Cache()
    if feedback_type == "thumb_up":
        cache.increment_thumb_up(query, response, url)
    elif feedback_type == "thumb_down":
        cache.increment_thumb_down(query, response, url)
    elif feedback_type == "flag":
        cache.increment_flag(query, response, url)
        