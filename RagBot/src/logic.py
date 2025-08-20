import random
from typing import List
from collections import Counter
import os
import statistics
from dotenv import load_dotenv

import torch
import numpy as np
from langchain.schema import SystemMessage

from collections import Counter
from typing import List, Tuple, Union, Set
from .prompts import (
    RAG_CONCISE_SYSTEM_PROMPT,
    RAG_EXPLANATORY_SYSTEM_PROMPT,
    RAG_NORMAL_SYSTEM_PROMPT,
    UTTERANCE_PARAPHRASER_PROMPT,
    SQL_CONVERTER,
    SQL_CONVERTER_MODIFIED,
    SQL_MODIFIER,
    QUERY_ROUTER,
    ANSWER_VALIDATOR_PROMPT
)
from .retriever import Retriever
from .config import config
from .cache import Cache
from .logs import simple_logger, logger_no_session_id
from .utils import json_cleaning, json_text_cleaning
from .business_objects import LOGISTICS_SALES_MODIFIED, FINANCIAL_BO_MODIFIED
from .semantic_router import SemanticRouterPipeline
from langchain.chat_models import ChatOpenAI
from langfuse.decorators import langfuse_context, observe
import logging
import hashlib


SEED = 44
torch.manual_seed(SEED)
np.random.seed(SEED)
torch.cuda.manual_seed_all(SEED)
random.seed(SEED)

template_for_not_answer = "پاسخ به این سوال در محدوده پاسخگویی من نیست برای اطلاعات بیشتر به 'https://systemgroup.net' مراجعه کنید."
template_for_not_context = """این سوال خارج از حوزه کاری {company_name} است. لطفا سوال خود را در رابطه با محصولات و خدمات {company_name} مطرح کنید. برای اطلاعات بیشتر به 'https://systemgroup.net' مراجعه کنید"""
template_for_doubtful_answer = "سوال شما را به خوبی متوجه نشدم. لطفا سوال خود را به صورت دقیق تر بپرسید تا بتوانم بهتر کمک کنم."


def hash_string(input_string):
    """Hashes a string using the SHA-256 algorithm."""

    # Encode the string into bytes, which is required by the hash function
    encoded_string = input_string.encode('utf-8')

    # Create a SHA-256 hash object
    hash_object = hashlib.sha256(encoded_string)

    # Get the hexadecimal representation of the hash
    hex_digest = hash_object.hexdigest()

    return hex_digest

@observe()
async def get_chat_response(prompt: str, answer_type: str = "qa") -> str:
    print("Character Length of the prompt: ", len(prompt))
    print("words length of the prompt: ", len(prompt.split()))

    # Load environment variables from .env file
    load_dotenv()

    # Check for environment variables for different configurations
    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME") 
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_API_BASE = os.getenv("LLM_API_BASE")
    # Use OpenRouter if available, otherwise fall back to original configuration
    if LLM_API_KEY and LLM_MODEL_NAME and LLM_API_BASE:
        llm = ChatOpenAI(
            openai_api_base=LLM_API_BASE,
            openai_api_key=LLM_API_KEY,
            model_name=LLM_MODEL_NAME,
            temperature=0,
        )
    else:
        raise ValueError("No valid LLM configuration found in environment variables")


    messages = [SystemMessage(content=prompt)]
    response = await llm.ainvoke(messages)
    return response.content

@observe()
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

@observe()
def history_serializer(history: List[tuple[str, str]]) -> str:
    serialized_history = ""
    for question, answer in history:
        serialized_history += f"USER: {question}\nASSISTANT: {answer}\n\n"
    return serialized_history

@observe()
async def utterance_paraphraser(history: List[tuple[str, str]], user_utterance: str, assistant_name: str = None) -> str:
    serialized_history = history_serializer(history)
    
    if assistant_name:
        # Use the original format with assistant_name (from develop branch)
        prompt = UTTERANCE_PARAPHRASER_PROMPT.format(
            history=serialized_history,
            assistant_name=assistant_name,
            question=user_utterance,
        )
    else:
        # Use the simplified format (from feature/add-sql-agent branch)
        prompt = UTTERANCE_PARAPHRASER_PROMPT.format(
            history=serialized_history,
            question=user_utterance,
        )
    
    response = await get_chat_response(prompt, answer_type="sql")
    response = json_cleaning(response)
    return response

@observe()
async def query_responder(
    query: str, 
    context: str, 
    history: str, 
    company_name: str = None, 
    assistant_name: str = None, 
    answer_type: str = "normal"
    ) -> str:

    serialized_history = history_serializer(history)
    
    # Use develop branch format with multiple prompt types
    if answer_type == "concise":
        RAG_SYSTEM_PROMPT = RAG_CONCISE_SYSTEM_PROMPT
    elif answer_type == "normal":
        RAG_SYSTEM_PROMPT = RAG_NORMAL_SYSTEM_PROMPT
    elif answer_type == "explanatory":
        RAG_SYSTEM_PROMPT = RAG_EXPLANATORY_SYSTEM_PROMPT
    else:
        RAG_SYSTEM_PROMPT = RAG_NORMAL_SYSTEM_PROMPT
        
    prompt = RAG_SYSTEM_PROMPT.format(
        context=context,
        company_name=company_name,
        assistant_name=assistant_name,
        question=query,
        conversation_history=serialized_history
    )
    
    response = await get_chat_response(prompt, answer_type="qa")
    response = json_cleaning(response)
    return response

@observe()
async def answer_validator(question: str, context: str, answer: str) -> bool:
    prompt = ANSWER_VALIDATOR_PROMPT.format(
        context=context,
        question=question,
        answer=answer,
    )
    response = await get_chat_response(prompt, answer_type="qa")
    return response

@observe()
async def is_somewhat_uniform(freq_dict: dict, threshold: float = 0.7) -> bool:
    """
    Checks if the frequency distribution in a dictionary is somewhat uniform
    based on the Coefficient of Variation (CV).
    """
    assert len(freq_dict) > 1, "Frequency dictionary must contain more than one item."
    
    frequencies = list(freq_dict.values())
    mean_freq = statistics.mean(frequencies)
    
    if mean_freq == 0:
        return True, mean_freq
    
    stdev_freq = statistics.stdev(frequencies)
    cv = stdev_freq / mean_freq
    
    return cv <= threshold, mean_freq

@observe()
async def retrieve_context_with_metadata(query: str, input_modules: List = None, database_index: str = None) -> List[dict]:
    retriever = Retriever()
    
    if input_modules:
        context_with_metadata = await retriever.retrieve_context(query, module_filter=input_modules)
    elif database_index:
        # Support database_index parameter from develop branch
        context_with_metadata = await retriever.retrieve_context(query, database_index)
    else:
        context_with_metadata = await retriever.retrieve_context(query)
    return context_with_metadata

@observe()
async def prepare_final_context(query: str, database_index: str = None, input_module: str = "") -> Union[str, Tuple[bool, List[str], Union[str, List[str]]]]:
    """
    Unified function supporting both develop branch (simple context) and feature/add-sql-agent (complex module handling)
    """
    
    context_with_metadata = await retrieve_context_with_metadata(query, database_index=database_index, input_modules=[input_module] if input_module else None)
    if not context_with_metadata:
        return False, [], []
    
    if input_module:
        return _handle_single_module_case(context_with_metadata, input_module)
    proposable_modules = set(config["modules"]["proposable_modules"])
    detected_modules = [result["module"] for result in context_with_metadata]
    module_frequencies = Counter(detected_modules)
    
    if len(module_frequencies) < 2:
        detected_modules_lst = list(module_frequencies.keys())
        return _handle_single_module_case(context_with_metadata, detected_modules_lst[0])
    
    print(module_frequencies)
    needs_clarification, mean_freq = await is_somewhat_uniform(module_frequencies)
    if not needs_clarification:
        max_value = max(module_frequencies.values())
        probable_detected_module = [k for k, v in module_frequencies.items() if v == max_value]
        return _handle_clear_preference_case(context_with_metadata, probable_detected_module[0])
    else:
        probable_detected_modules = [k for k, v in module_frequencies.items() if v >= mean_freq]
        return _handle_clarification_case(
            context_with_metadata,
            probable_detected_modules,
            proposable_modules
        )

@observe()
def _handle_single_module_case(
    context_with_metadata: List,
    detected_modules: str
) -> Tuple[bool, List[str], str]:
    """Handle case where only one module type is detected."""
    documents = "\n\n".join(context["text"] for context in context_with_metadata)
    return False, [detected_modules], documents

@observe()
def _handle_clear_preference_case(
    context_with_metadata: List, detected_module: str
) -> Tuple[bool, List[str], List[str]]:
    """Handle case where module preference is clear (no clarification needed)."""
    documents = [doc["text"] for doc in context_with_metadata]
    return False, [detected_module], documents

@observe()
def _handle_clarification_case(
    context_with_metadata: List,
    detected_modules: List[str],
    proposable_modules: Set[str]
) -> Tuple[bool, List[str], Union[str, List[str]]]:
    """Handle case where clarification is needed for module selection."""
    unique_modules = set(detected_modules)
    valid_modules = unique_modules & proposable_modules
    
    if len(valid_modules) < 2:
        documents = context_with_metadata[0]["text"]
        valid_modules_lst = list(valid_modules)
        return False, valid_modules_lst, documents
    else:
        documents = [doc["text"] for doc in context_with_metadata]
        valid_modules_lst = list(valid_modules)
        return True, valid_modules_lst, documents

@observe()
async def module_proposer():
    return ["انبار و فروش", "دفتر کل"]

@observe()
async def sql_responder_(
    query: str,
    detected_module: str = "", 
    faulty_sql_query: str = "", 
    error_message: str = "", 
    do_retry: bool = False
    ):
    """
    Unified SQL responder supporting both simple schema list and module-based schema selection
    """
    
    # Use feature/add-sql-agent logic with detected_module
    if detected_module.strip() == "دفتر کل" or detected_module.strip() == "دفترکل":
        if not do_retry:
            bo_prompt = SQL_CONVERTER_MODIFIED.format(schema=FINANCIAL_BO_MODIFIED, query=query)
        else:
            bo_prompt = SQL_MODIFIER.format(schema=FINANCIAL_BO_MODIFIED, original_query=query, 
                                          faulty_sql_query=faulty_sql_query, error_message=error_message)
    else:
        if not do_retry:
            bo_prompt = SQL_CONVERTER_MODIFIED.format(schema=LOGISTICS_SALES_MODIFIED, query=query)
        else:
            bo_prompt = SQL_MODIFIER.format(schema=LOGISTICS_SALES_MODIFIED, original_query=query, 
                                          faulty_sql_query=faulty_sql_query, error_message=error_message)
    
    raw_json_response = await get_chat_response(bo_prompt, answer_type="sql")
    response = json_cleaning(raw_json_response)
    
    if not response:
        response = "در حال حاضر نمیتوانم به این سوال پاسخ دهم"
    
    return response

@observe()
async def router_SQL_QA(query: str, context: str):
    prompt = QUERY_ROUTER.format(query=query, context=context)
    raw_response = await get_chat_response(prompt, answer_type="sql")
    response = json_cleaning(raw_response)
    return response

@observe()
async def chat_responder_(
    history: List[tuple[str, str]],
    user_utterance: str,
    database_index: str = config["database"]["persist_directory"],
    company_name: str = config["database"]["company_name"],
    assistant_name: str = config["database"]["assistant_name"],
    response_type: str = config["database"]["response_type"],
    does_evaluate: bool = config["database"]["does_evaluate"],
    use_cache: bool = config["database"]["use_cache"],
    detected_module: str = "",
) -> Union[tuple[str, str, str, str], tuple[str, str, str, bool, List[str]]]:
    """
    Unified chat responder supporting both develop branch (simple RAG) and feature/add-sql-agent (SQL + module handling)
    """
    
    # If sql_mode is True, use the new SQL agent logic
    if not detected_module and use_cache:
        response, url = await get_cache_response(user_utterance)
        if response:
            return user_utterance, response, "", False, []

    paraphrased_utterance = await utterance_paraphraser(history, user_utterance)

    semantic_router_object = SemanticRouterPipeline(
        inference_only=True,
        embedding_address=config["embedding_model"]["model_name"],
        classifier_address=config["router_model"]["address"],
        model_name=config["router_model"]["model_name"]
    )
    cache = Cache() # TODO this should be added to a separate function 
    route_response_cached = cache.get_exact_cache(paraphrased_utterance)
    if route_response_cached is None:
        route_response = semantic_router_object.predict_sentences([paraphrased_utterance])
        route_response = route_response[0]
        cache.set_exact_cache(paraphrased_utterance, route_response)
        logger_no_session_id(message="key: %s, is added to redis!" % paraphrased_utterance)
    else:
        route_response = route_response_cached

    if route_response == "sql":
        return paraphrased_utterance, "", "", False, []

    if use_cache:
        response, url = await get_cache_response(paraphrased_utterance) 
        if response:
            return paraphrased_utterance, response, "", False, []
    
    if detected_module:
        do_clarify, modules, context = await prepare_final_context(paraphrased_utterance, database_index=database_index, input_module=detected_module)
    else:
        do_clarify, modules, context = await prepare_final_context(paraphrased_utterance, database_index=database_index)

    if not context:
        return paraphrased_utterance, "", "", False, []

    if do_clarify:
        return paraphrased_utterance, "", "", do_clarify, modules
    
    # Use semantic router if available

    hashed_paraphrased_utterance = hash_string(paraphrased_utterance)
    chitchat_redis_key = "chitchat_{hashed_pu}".format(hashed_pu=hashed_paraphrased_utterance)
    route_response_hashed_cached = cache.get_exact_cache(chitchat_redis_key)
    if route_response_hashed_cached is not None:
        response = route_response_hashed_cached
        return paraphrased_utterance, response, "", do_clarify, modules
    else:
        response = await query_responder(
            paraphrased_utterance,
            context,
            history,
            company_name=company_name,
            assistant_name=assistant_name,
            answer_type=response_type
            )

        if "محدوده دانش من " in response:
            response = template_for_not_answer
        if "خارج از حوزه کاری" in response:
            response = template_for_not_context.format(company_name=company_name)

        if route_response == "chitchat":
            cache.set_exact_cache(chitchat_redis_key, response)

    
    return paraphrased_utterance, response, context, do_clarify, modules

@observe()
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