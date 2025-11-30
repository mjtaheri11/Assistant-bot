import random
from typing import List
import json
from collections import Counter
import os
import statistics
from dotenv import load_dotenv
### remove this!
import pdb
pdb.set_trace = lambda: 1

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
    SQL_CONVERTER_MODIFIED_WITH_PARAMETERS,
    CHITCHAT_PROMPT,
    SQL_CONVERTER_MODIFIED_WITH_PARAMETERS_TEMPLATE,
    SQL_MODIFIER,
    ANSWER_VALIDATOR_PROMPT,
    SEMANTIC_ROUTER
    # SQL_CONVERTER,
)
from .retriever import Retriever
from .config import config
from .cache import Cache
from .logs import simple_logger, logger_no_session_id
from .utils import json_cleaning, json_text_cleaning, json_cleaning_1
from .business_objects import LOGISTICS_SALES_MODIFIED, FINANCIAL_BO_MODIFIED
from .semantic_router import SemanticRouterPipeline
from langchain.chat_models import ChatOpenAI
from langfuse import observe, get_client
import logging
import hashlib

# Load environment variables from .env file
load_dotenv()

SEED = 44
torch.manual_seed(SEED)
np.random.seed(SEED)
torch.cuda.manual_seed_all(SEED)
random.seed(SEED)
OSS_LLM_MODEL_NAME = os.getenv("OSS_LLM_MODEL_NAME", "/gpt-120")
GPT_LLM_MODEL_NAME = os.getenv("GPT_LLM_MODEL_NAME", "gpt-4.1-2025-04-14")
QWEN3_CODER_LLM_MODEL_NAME = os.getenv("QWEN3_CODER_MODEL_NAME", "/Qwen/Qwen3-Coder-30B-A3B-Instruct")
OSS_API_KEY = os.getenv("OSS_API_KEY", "EMPTY")
GPT_API_KEY = os.getenv("GPT_API_KEY", "EMPTY")
QWEN3_CODER_API_KEY = os.getenv("QWEN3_CODER_API_KEY", "EMPTY")

LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_BASE_URL = os.getenv("LANGFUSE_BASE_URL")

OSS_API_BASE = os.getenv("OSS_API_BASE", "http://gpt-oss-120b-predictor.admin.svc.cluster.local/v1")
GPT_API_BASE = os.getenv("GPT_API_BASE", "https://api.openai.com/v1/")
QWEN3_CODER_API_BASE = os.getenv("QWEN3_CODER_API_BASE", "http://qwen3-coder-30b-predictor.admin.svc.cluster.local/v1")

MODULE_PROPOSER_THRESHOLD = float(os.getenv("MODULE_PROPOSER_THRESHOLD", 0.75))

template_for_chitchat_answers = """من اینجا هستم تا تنها به سوالات مربوط به محصولات نسل چهارم شرکت همکاران سیستم پاسخ دهم. لطفاً سوالات خود را در مورد راه‌حل‌های نسل چهارم ما مطرح کنید."""
template_for_not_answer = "پاسخ به این سوال در محدوده پاسخگویی من نیست."
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

def model_selector(use_oss: bool = False, use_qwen3_coder: bool = False):
    if use_oss:
        model_name = OSS_LLM_MODEL_NAME
        api_base = OSS_API_BASE
        api_key = OSS_API_KEY
    elif use_qwen3_coder:
        model_name = QWEN3_CODER_LLM_MODEL_NAME
        api_base = QWEN3_CODER_API_BASE
        api_key = QWEN3_CODER_API_KEY
    else:
        model_name = GPT_LLM_MODEL_NAME
        api_base = GPT_API_BASE
        api_key = GPT_API_KEY

    pdb.set_trace()
    result = model_name, api_base, api_key
    return result

@observe()
async def get_chat_response(
        prompt: str, 
        model_name: str = OSS_LLM_MODEL_NAME,
        api_key=OSS_API_KEY, 
        api_base=OSS_API_BASE
    ) -> str:

    print("Character Length of the prompt: ", len(prompt))
    print("words length of the prompt: ", len(prompt.split()))

    print("LLM_API_BASE:", api_base)
    print("LLM_API_KEY:", api_key)
    print("LLM_MODEL_NAME:", model_name)
    # Use OpenRouter if available, otherwise fall back to original configuration
    if api_base and model_name and api_key:
        if model_name != "/gpt-120":
            extra = {}
            # model_kwargs = {}
        else:
            extra = {
                "top_k": 1,
                "do_sample": False,
                "seed": 42,
                "sampling_method": "greedy",
                "reasoning_effort": "medium"
            }
            # model_kwargs={
            #     "top_p": 1,
            #     "max_completion_tokens": 8000
            # },
        llm = ChatOpenAI(
            openai_api_base=api_base,
            model_name=model_name,
            openai_api_key=api_key,
            temperature=0,
            model_kwargs={},
            extra_body=extra
        )
    else:
        raise ValueError("No valid LLM configuration found in environment variables")


    messages = [SystemMessage(content=prompt)]
    pdb.set_trace()
    response = await llm.ainvoke(messages)
    result = response.content
    pdb.set_trace()
    return result

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
        result = records[0]["response"], records[0]["url"]
        
    else:
        result = "", ""
    return result

@observe()
def history_serializer(history: List[tuple[str, str]]) -> str:
    serialized_history = ""
    for question, answer in history:
        serialized_history += f"USER: {question}\nASSISTANT: {answer}\n\n"
    return serialized_history

@observe()
async def utterance_paraphraser(history: List[tuple[str, str]], user_utterance: str, assistant_name: str = None, use_oss:bool = True) -> str:
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
    model_name, api_base, api_key = model_selector(use_oss, use_qwen3_coder=False)
    response_1 = await get_chat_response(prompt, model_name, api_key, api_base)
    response = json_cleaning_1(response_1)
    return response

@observe()
async def query_responder(
    query: str, 
    context: str, 
    history: str, 
    company_name: str = None, 
    assistant_name: str = None, 
    answer_type: str = "normal", 
    use_oss: bool = True
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
    model_name, api_base, api_key = model_selector(use_oss, use_qwen3_coder=False)
    response = await get_chat_response(prompt, model_name, api_key, api_base)
    response = json_cleaning(response)
    pdb.set_trace()
    return response


@observe()
async def chitchat_responder(
    query: str,
    context: str, 
    history: str,
    use_oss: bool
    ):
    serialized_history = history_serializer(history)
    prompt = CHITCHAT_PROMPT.format(user_question=query, 
                             context=context, 
                             history=serialized_history
                             )
    model_name, api_base, api_key = model_selector(use_oss, use_qwen3_coder=False)
    response = await get_chat_response(prompt, model_name, api_key, api_base)
    pdb.set_trace()
    return response

    
@observe()
async def answer_validator(question: str, context: str, answer: str) -> bool:
    prompt = ANSWER_VALIDATOR_PROMPT.format(
        context=context,
        question=question,
        answer=answer,
    )
    model_name, api_base, api_key = model_selector(use_oss, use_qwen3_coder=False)
    response = await get_chat_response(prompt, model_name, api_key, api_base)
    pdb.set_trace()
    return response

@observe()
async def is_somewhat_uniform(freq_dict: dict, threshold: float = MODULE_PROPOSER_THRESHOLD) -> bool:
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
    check_cv = (cv <= threshold, mean_freq)
    return check_cv

@observe()
async def retrieve_context_with_metadata(query: str, input_modules: List = None, database_index: str = None) -> List[dict]:
    retriever = Retriever()
    
    if input_modules:
        context_with_metadata = await retriever.retrieve_context(query, database_index, module_filter=input_modules)
    elif database_index:
        # Support database_index parameter from develop branch
        context_with_metadata, query_embedding = await retriever.retrieve_context(query, database_index)
    else:
        context_with_metadata, query_embedding = await retriever.retrieve_context(query)
    return context_with_metadata, query_embedding

@observe()
async def prepare_final_context(query: str, database_index: str = None, input_module: str = "") -> Union[str, Tuple[bool, List[str], Union[str, List[str]]]]:
    """
    Unified function supporting both develop branch (simple context) and feature/add-sql-agent (complex module handling)
    """
    
    context_with_metadata, query_embedding = await retrieve_context_with_metadata(query, database_index=database_index, input_modules=[input_module] if input_module else None)
    print("#########\n")
    print(context_with_metadata)
    print("\n#########")
    if not context_with_metadata:
        return False, [], [], query_embedding
    if input_module:
        result = _handle_single_module_case(context_with_metadata, input_module) 
        return *result, query_embedding 
    proposable_modules = set(config["modules"]["proposable_modules"])
    detected_modules = [result["module"] for result in context_with_metadata]
    module_frequencies = Counter(detected_modules)
    if len(module_frequencies) < 2:
        detected_modules_lst = list(module_frequencies.keys())
        result = _handle_single_module_case(context_with_metadata, detected_modules_lst[0])
        return *result, query_embedding
    
    print(module_frequencies) # temp logs
    needs_clarification, mean_freq = await is_somewhat_uniform(module_frequencies)
    if not needs_clarification:
        max_value = max(module_frequencies.values())
        probable_detected_module = [k for k, v in module_frequencies.items() if v == max_value]
        result = _handle_clear_preference_case(context_with_metadata, probable_detected_module[0])
    else:
        # probable_detected_modules = [k for k, v in module_frequencies.items() if v >= mean_freq]
        probable_detected_modules = list(module_frequencies.keys())
        result = _handle_clarification_case(
            context_with_metadata,
            probable_detected_modules,
            proposable_modules
        )
    return *result, query_embedding

@observe()
def _handle_single_module_case(
    context_with_metadata: List,
    detected_modules: str
) -> Tuple[bool, List[str], str]:
    """Handle case where only one module type is detected."""
    documents = "\n\n".join(context["text"] for context in context_with_metadata)
    result = False, [detected_modules], documents
    return result

@observe()
def _handle_clear_preference_case(
    context_with_metadata: List, detected_module: str
) -> Tuple[bool, List[str], List[str]]:
    """Handle case where module preference is clear (no clarification needed)."""
    documents = [doc["text"] for doc in context_with_metadata]
    result = False, [detected_module], documents
    return result

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
        result = False, valid_modules_lst, documents 
    else:
        documents = [doc["text"] for doc in context_with_metadata]
        valid_modules_lst = list(valid_modules)
        result = True, valid_modules_lst, documents
    return result

@observe()
async def module_proposer():
    return ["انبار و فروش", "دفتر کل"]

@observe()
async def sql_responder_(
    query: str,
    detected_module: str = "", 
    faulty_sql_query: str = "", 
    error_message: str = "", 
    do_retry: bool = False,
    parameters: dict = {},
    use_oss: bool = False
    ):
    """
    Unified SQL responder supporting both simple schema list and module-based schema selection
    """
    
    # Use feature/add-sql-agent logic with detected_module
    if detected_module.strip() == "دفتر کل" or detected_module.strip() == "دفترکل":
        if not do_retry:
            bo_prompt = SQL_CONVERTER_MODIFIED_WITH_PARAMETERS_TEMPLATE.format(schema=FINANCIAL_BO_MODIFIED, query=query)
        else:
            faulty_sql_query = json.dumps({"SQL": faulty_sql_query, "parameters": parameters})
            bo_prompt = SQL_MODIFIER.format(schema=FINANCIAL_BO_MODIFIED, original_query=query, 
                                          faulty_sql_query=faulty_sql_query, error_message=error_message)
    elif detected_module.strip() == "انبار" or detected_module.strip() == "فروش":
        if not do_retry:
            faulty_sql_query = json.dumps({"SQL": faulty_sql_query, "parameters": parameters})
            bo_prompt = SQL_CONVERTER_MODIFIED_WITH_PARAMETERS_TEMPLATE.format(schema=LOGISTICS_SALES_MODIFIED, query=query)
        else:
            bo_prompt = SQL_MODIFIER.format(schema=LOGISTICS_SALES_MODIFIED, original_query=query, 
                                          faulty_sql_query=faulty_sql_query, error_message=error_message)
    else:
        if not do_retry:
            all_schema = LOGISTICS_SALES_MODIFIED + "\n" + FINANCIAL_BO_MODIFIED
            faulty_sql_query = json.dumps({"SQL": faulty_sql_query, "parameters": parameters})
            bo_prompt = SQL_CONVERTER_MODIFIED_WITH_PARAMETERS_TEMPLATE.format(schema=all_schema, query=query)
        else:
            bo_prompt = SQL_MODIFIER.format(schema=LOGISTICS_SALES_MODIFIED, original_query=query, 
                                          faulty_sql_query=faulty_sql_query, error_message=error_message)
    model_name, api_base, api_key = model_selector(use_oss, use_qwen3_coder=False)
    raw_json_response = await get_chat_response(
        bo_prompt, 
        model_name=model_name, 
        api_key=api_key,
        api_base=api_base
        )
    response = json_cleaning(raw_json_response)
    pdb.set_trace()
    return response


def _get_chitchat_cache_key(utterance: str) -> str:
    """Generates a consistent cache key for chitchat routes."""
    hashed_utterance = hash_string(utterance)
    result = f"chitchat_{hashed_utterance}"
    return result


async def _determine_final_route(
    utterance: str,
    use_joblib: bool = True
) -> str:

    ROUTER_CONFIG = config["router_model"]
    ALPHA_THRESHOLD = ROUTER_CONFIG["alpha_threshold"]
    BETA_THRESHOLD = ROUTER_CONFIG["beta_threshold"]
    """Determines the final route based on probability thresholds."""
    if use_joblib:
        semantic_router_client = SemanticRouterPipeline(
            inference_only=True,
            embedding_address=config["embedding_model"]["model_name"],
            classifier_address=ROUTER_CONFIG["address"],
            model_name=ROUTER_CONFIG["model_name"]
        )
        predictions, probabilities, max_prob = semantic_router_client.predict_sentences([utterance])
        top_prediction = predictions[0]
        probabilities = list(probabilities)  # Convert to list to make it subscriptable

        if max_prob > ALPHA_THRESHOLD and ("همکاران" not in utterance) and (top_prediction != "illegal"):
            return top_prediction

        # If confidence is low, see if multiple routes are plausible
        if "همکاران" not in utterance:
            plausible_routes = [
                route for route, prob in probabilities if prob > BETA_THRESHOLD
            ]
        else:
            plausible_routes = [route for route, prob in probabilities]

        if len(plausible_routes) < 2:
            # Fallback if no route meets the beta threshold
            # Get the top two routes by probability
            sorted_probabilities = sorted(probabilities, key=lambda x: x[1], reverse=True)
            plausible_routes = [sorted_probabilities[0][0], sorted_probabilities[1][0]]
    else:
        plausible_routes = ['chitchat', 'illegal', 'irrelevant', 'sql', 'qa']

    # Use an LLM to disambiguate between plausible routes
    model_name, api_base, api_key = model_selector(use_oss, use_qwen3_coder=False)
    result = await get_chat_response(
        SEMANTIC_ROUTER.format(user_query=utterance, class_list=plausible_routes), model_name, api_key, api_base
    )
    return result

@observe()
async def get_route_for_utterance(utterance: str, use_joblib: bool = False) -> str:    
    CHITCHAT_ROUTE = "chitchat"
    ROUTER_CONFIG = config["router_model"]
    
    # It's better to instantiate clients once and reuse them
    # rather than creating them in a function that's called frequently.
    cache_client = Cache()

    """
    Determines the semantic route for a given utterance, using caching to improve performance.
    """
    # 1. Check for a direct cached route first (guard clause)
    cached_route = cache_client.get_exact_cache(utterance)
    if cached_route:
        return cached_route

    # 2. Check for the specific chitchat cache (from original logic)
    chitchat_key = _get_chitchat_cache_key(utterance)
    if cache_client.get_exact_cache(chitchat_key):
        return CHITCHAT_ROUTE
    semantic_router_client = SemanticRouterPipeline(
        inference_only=True,
        embedding_address=None,
        embedding_model=ROUTER_CONFIG["embedding_model"],
        classifier_address=ROUTER_CONFIG["address"],
        model_name=ROUTER_CONFIG["model_name"]
    )

    # 3. Determine the final route using the logic in the helper function
    final_route = await _determine_final_route(utterance, use_joblib)

    # 4. Cache the result for future requests
    # Note: The original code had a commented-out line to cache all routes.
    # This version explicitly caches the final determined route.
    # cache_client.set_exact_cache(utterance, final_route)
    # logging.info(f"Cached route for '{utterance}': '{final_route}'")

    # The original code had a special caching rule for chitchat.
    # It cached an undefined 'response' variable. Here we cache the route name for consistency.
    # if final_route == CHITCHAT_ROUTE:
    #     cache_client.set_exact_cache(chitchat_key, final_route)
    return final_route.strip()


@observe()
async def router_SQL_QA(query: str, context: str):
    # prompt = QUERY_ROUTER.format(query=query, context=context)
    model_name, api_base, api_key = model_selector(use_oss, use_qwen3_coder=False)
    raw_response = await get_chat_response(prompt, model_name, api_key, api_base)
    response = json_cleaning(raw_response)
    pdb.set_trace()
    return response

@observe()
async def chat_responder_(
    history: List[tuple[str, str]],
    user_utterance: str,
    database_index: str = config["database"]["collection_name"],
    company_name: str = config["database"]["company_name"],
    assistant_name: str = config["database"]["assistant_name"],
    response_type: str = config["database"]["response_type"],
    does_evaluate: bool = config["database"]["does_evaluate"],
    use_cache: bool = config["database"]["use_cache"],
    detected_module: str = "",
    use_oss: bool = True
) -> Union[tuple[str, str, str, str], tuple[str, str, str, bool, List[str]]]:
    """
    Unified chat responder supporting both develop branch (simple RAG) and feature/add-sql-agent (SQL + module handling)
    """
    # If sql_mode is True, use the new SQL agent logic
    if not detected_module and use_cache:
        response, url = await get_cache_response(user_utterance)
        if response:
            result_temp = user_utterance, response, "", False, []
            return result_temp

    paraphrased_utterance = await utterance_paraphraser(history, user_utterance, use_oss)
    if use_cache:
        response, url = await get_cache_response(paraphrased_utterance) 
        if response:
            result_temp = paraphrased_utterance, response, "", False, []
            return result_temp
    if detected_module:
        do_clarify, modules, context, query_embedding = await prepare_final_context(paraphrased_utterance, database_index=database_index, input_module=detected_module)
    else:
        do_clarify, modules, context, query_embedding = await prepare_final_context(paraphrased_utterance, database_index=database_index)

    if do_clarify:
        result_temp = paraphrased_utterance, "", "", do_clarify, modules
        return result_temp

    route_response = await get_route_for_utterance(paraphrased_utterance, query_embedding, use_oss)
    if route_response == "sql":
        if not modules:
            modules = ["all"]
        result_temp = paraphrased_utterance, "", "", False, [modules[0]]
        pdb.set_trace()
        return result_temp
    
    if route_response == "chitchat":
        response = await chitchat_responder(paraphrased_utterance, history=history, context=context, use_oss=use_oss)
        result_temp = paraphrased_utterance, response, context, False, []
        pdb.set_trace()
        return result_temp
    
    if route_response == "illegal" or route_response =="irrelevant":
        result_temp = paraphrased_utterance, template_for_not_answer, "", False, []
        pdb.set_trace()
        return result_temp

    if not context:
        result_temp = paraphrased_utterance, "", "", False, []
        return result_temp

    response = await query_responder(
        paraphrased_utterance,
        context,
        history,
        company_name=company_name,
        assistant_name=assistant_name,
        answer_type=response_type,
        use_oss=use_oss
        )

    if "محدوده دانش من " in response:
        response = template_for_not_answer
    if "خارج از حوزه کاری" in response:
        response = template_for_not_context.format(company_name=company_name)
    result_temp = paraphrased_utterance, response, context, do_clarify, modules
    pdb.set_trace()
    return result_temp

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