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
    SQL_CONVERTER,
    SQL_CONVERTER_1,
    QUERY_ROUTER,
)
from .retriever import Retriever
from .config import config
from .cache import Cache
from .logs import simple_logger
from .utils import json_cleaning, json_text_cleaning, json_cleaning_1, json_string_to_dict
from .business_objects import FINANCIAL_BO, LOGISTICS_BO
from langchain.chat_models import ChatOpenAI


SEED = 44
torch.manual_seed(SEED)
np.random.seed(SEED)
torch.cuda.manual_seed_all(SEED)
random.seed(SEED)


template_for_not_answer = "پاسخ به این سوال در محدوده دانش من نیست"
template_for_not_context = "این سوال خارج از حوزه کاری همکاران سیستم است. لطفا سوال خود را در رابطه با محصولات و خدمات همکاران سیستم مطرح کنید."

async def get_chat_response(prompt: str, answer_type: str) -> str:
    print("Character Length of the prompt: ", len(prompt)) # TODO print should be replaced with a proper log
    print("words length of the prompt: ", len(prompt.split())) # TODO print should be replaced with a proper log
    if answer_type == "qa":
        model_name = config["ollama"]["qa_model_name"]
        base_url = f"http://185.13.230.222:{str(config['ollama']['qa_model_port'])}/v1"
        num_ctx = config['ollama']['qa_model_num_ctx']
        llm = ChatOpenAI(
            openai_api_base=base_url,
            openai_api_key="EMPTY",
            model_name="/models/aya-expanse-32b-gptq-4bit"
        ) 
    else:
        model_name = config["ollama"]["sql_model_name"]
        # base_url = f"http://ollama:{config['ollama']['sql_model_port']}"
        base_url = "http://localhost:8980"
        num_ctx = config['ollama']['sql_model_num_ctx']
        llm = ChatOllama(
            model=model_name,
            temperature=0,
            keep_alive=config["ollama"]["keep_alive"],
            seed=SEED,
            # base_url="http://ollama:11434",
            base_url=base_url, 
            num_ctx=num_ctx
        )

    messages = [SystemMessage(content=prompt)]
    response = await llm.ainvoke(messages)  
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
    response = await get_chat_response(prompt, answer_type="sql")
    response = json_cleaning(response)
    # import pdb
    # pdb.set_trace()
    # response_ = json_cleaning_1(response)
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
    response = await get_chat_response(prompt, answer_type="qa")
    return response
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

    retriever = Retriever()
    context = await retriever.retrieve_context(query) + "\n\n" + context
    # TODO: need appropriate context management > context = context[: config["context"]["max_length"]]
    return context.strip()

async def module_proposer():
    return ["انبار", "مالی"]


async def sql_responder_(query: str, detected_module: str = ""):
    if detected_module.strip() == "مالی":
        bo_prompt = SQL_CONVERTER.format(schema=FINANCIAL_BO, query=query)
    else:
        bo_prompt = SQL_CONVERTER.format(schema=LOGISTICS_BO, query=query)
    raw_json_response = await get_chat_response(bo_prompt, answer_type="sql")
    response = json_cleaning(raw_json_response)
    
    # response_dict = json_cleaning(raw_json_response)
    # response = response_dict["sql"]
    # json_response = json_text_cleaning(raw_json_response)
    # response = json_response["query"]
    if not response:
        response = "در حال حاضر نمیتوانم به این سوال پاسخ دهم"
    return response
    
    
async def router_SQL_QA(query: str, context: str):
    prompt = QUERY_ROUTER.format(query=query, context=context)
    raw_response = await get_chat_response(prompt, answer_type="sql")
    response = json_cleaning(raw_response)
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
        return paraphrased_utterance, "", ""

    route_response = await router_SQL_QA(paraphrased_utterance, context)
    if route_response == "DATABASE":
        return paraphrased_utterance, "", ""
        
    response = await query_responder(paraphrased_utterance, context, history)
    # json_response = fix_asterisks(json_response)
    # return paraphrased_utterance, json_response["answer"], context
    if "محدوده دانش من " in response:
        response = template_for_not_answer
    if "خارج از حوزه کاری" in response:
        response = template_for_not_context
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
