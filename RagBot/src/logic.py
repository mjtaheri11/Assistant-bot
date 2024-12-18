import asyncio
import json
import random
from typing import List
import os

import torch
import numpy as np
from langchain.schema import SystemMessage
from langchain_community.chat_models import ChatOllama

from .prompts import (
    RAG_SYSTEM_PROMPT,
    UTTERANCE_PARAPHRASER_PROMPT,
    SQL_CONVERTER
)
from .retriever import Retriever
from .config import config
from .cache import Cache
from .logs import simple_logger
from .utils import json_cleaning, json_text_cleaning

SEED = 44
torch.manual_seed(SEED)
np.random.seed(SEED)
torch.cuda.manual_seed_all(SEED)
random.seed(SEED)


template_for_not_answer = "پاسخ به این سوال در محدوده دانش من نیست"


async def get_chat_response(prompt: str, model_name: str) -> str:
    # OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://dockerize_assistant-ollama-1:11434')
    # LLM_MODEL = os.getenv('LLM_MODEL', 'gemma2:9b-instruct-fp16')
    print("Character Length of the prompt: ", len(prompt))
    print("words length of the prompt: ", len(prompt.split()))
    llm = ChatOllama(
        model=model_name,
        temperature=config["ollama"]["temperature"],
        keep_alive=config["ollama"]["keep_alive"],
        seed=SEED,
        # base_url="127.0.0.1:8089"
        # base_url="http://ollama:11434",
        # base_url="http://172.20.0.3:11434"
        # base_url=OLLAMA_HOST
    )
    messages = [SystemMessage(content=prompt)]
    response = await llm.ainvoke(messages)  # type: ignore[arg-type]
    return response.content


async def get_cache_response(
    query: str,
    threshold: float = config["cache"]["alpha_threshold"],
) -> tuple[str, str]:
    knn = 1
    cache = Cache()
    records = await cache.get_embedding_match(
        query=query,
        threshold=threshold,
        knn=knn,
    )
    if records and records[0]["thumb_up"] > 0:
        return records[0]["response"], records[0]["url"]
    else:
        return "", ""


def history_serializer(history: List[tuple[str, str]]) -> str:
    serialized_history = ""
    # TODO this history part should be considered effectively. I just wrote something messy.
    for question, answer in history:
        serialized_history += f"USER: {question}\nASSISTANT: {answer}\n\n"
    return serialized_history


async def utterance_paraphraser(history: List[tuple[str, str]], user_utterance: str) -> str:
    # TODO such a messy modification. resolve it as soon as you can
    # serialized_history = "\n".join(["USER: " + user_hist[0] + "\n" + "ASSISTANT" + user_hist[1] for user_hist in history])
    # import pdb
    # pdb.set_trace()
    serialized_history = history_serializer(history)
    prompt = UTTERANCE_PARAPHRASER_PROMPT.format(
        history=serialized_history,
        question=user_utterance,
    )
    response = await get_chat_response(prompt, config["ollama"]["model_name"])
    # import pdb
    # pdb.set_trace()
    # paraphrased_query = json_cleaning(response)
    # paraphrased_query_dict = json_text_cleaning(paraphrased_query, key="rephrased_question")
    # return paraphrased_query_dict
    return response


async def query_responder(query: str, context: str, history: str) -> str:
    # TODO: Add appropriate logger.
    serialized_history = history_serializer(history)
    prompt = RAG_SYSTEM_PROMPT.format(
        context=context,
        # history=serialized_history,
        question=query,
    )
    response = await get_chat_response(prompt, config["ollama"]["model_name"])
    return response.replace("متن", "دانش")
    # cleaned_response = json_cleaning(response)
    # cleaned_response_dict = json_text_cleaning(cleaned_response, "answer")
    # return cleaned_response_dict


async def prepare_final_context(query: str) -> str:
    cache = Cache()
    records = await cache.get_embedding_match(
        query,
        config["cache"]["beta_threshold"],
        config["cache"]["knn"],
    )

    context = "\n\n".join(
        "Q: " + result["query"] + "\n" + "A: " + result["response"]
        for result in reversed(records)
        if result["query"].strip() != ""
    )

    # import pdb
    # pdb.set_trace()
    retriever = Retriever()
    context = await retriever.retrieve_context(query) + "\n\n" + context
    # TODO: need appropriate context management > context = context[: config["context"]["max_length"]]
    return context


async def sql_responder(query: str, table_schemas: List[str]) -> str:
    schema = "\n\n".join(table_schemas)
    prompt = SQL_CONVERTER.format(schema=schema, query=query)
    response = await get_chat_response(prompt, config["ollama"]["sql_model_name"])
    return response


async def chat_responder_(
    history: List[tuple[str, str]],
    user_utterance: str,
) -> tuple[str, str, str, str]:

    response, url = await get_cache_response(
        user_utterance,
    )
    if response:
        return user_utterance, response, ""
    paraphrased_utterance_dict = await utterance_paraphraser(history, user_utterance)
    # paraphrased_utterance = paraphrased_utterance_dict["rephrased_question"]
    paraphrased_utterance = paraphrased_utterance_dict
    response, url = await get_cache_response(
        paraphrased_utterance,
    )
    if response:
        return paraphrased_utterance, response, ""

    context = await prepare_final_context(paraphrased_utterance)
    if not context:
        return paraphrased_utterance, template_for_not_answer, "" 
        
    response = await query_responder(paraphrased_utterance, context, history)
    # json_response = fix_asterisks(json_response)
    # return paraphrased_utterance, json_response["answer"], context
    if "محدوده دانش من نیست" in response:
        response = template_for_not_answer
    return paraphrased_utterance, response, context


async def feedback_(
    query: str,
    response: str,
    url: str,
    feedback_type: str,
) -> None:
    cache = Cache()
    if feedback_type == "thumb_up":
        await cache.increment_thumb_up(query, response, url)
    elif feedback_type == "thumb_down":
        await cache.increment_thumb_down(query, response, url)
    elif feedback_type == "flag":
        await cache.increment_flag(query, response, url)
