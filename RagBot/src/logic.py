import asyncio
import json
import random
from typing import List
from collections import Counter
import os
import statistics
from dotenv import load_dotenv

import torch
import numpy as np
from langchain.schema import SystemMessage
from langchain_community.chat_models import ChatOllama

from collections import Counter
from typing import List, Tuple, Union, Set
from .prompts import (
    RAG_SYSTEM_PROMPT,
    UTTERANCE_PARAPHRASER_PROMPT,
    SQL_CONVERTER,
    SQL_CONVERTER_1,
    SQL_CONVERTER_MODIFIED,
    SQL_MODIFIER,
    QUERY_ROUTER,
)
from .retriever import Retriever
from .config import config
from .cache import Cache
from .logs import simple_logger
from .utils import json_cleaning, json_text_cleaning, json_cleaning_1, json_string_to_dict
from .business_objects import FINANCIAL_BO, LOGISTICS_BO, LOGISTICS_SALES_MODIFIED, FINANCIAL_BO_MODIFIED
from langchain.chat_models import ChatOpenAI

SEED = 44
torch.manual_seed(SEED)
np.random.seed(SEED)
torch.cuda.manual_seed_all(SEED)
random.seed(SEED)


template_for_not_answer = "پاسخ به این سوال در محدوده دانش من نیست"
template_for_not_context = "این سوال خارج از حوزه کاری همکاران سیستم است. لطفا سوال خود را در رابطه با محصولات و خدمات همکاران سیستم مطرح کنید."


# chat = ChatOpenAI(  # type: ignore[call-arg]
#     openai_api_base=secret["openai"]["api_base"],
#     openai_api_key=secret["openai"]["api_key"],
#     openai_proxy=secret["openai"]["proxy"],
#     model_name=config["openai"]["model_name"],
#     max_tokens=config["openai"]["max_tokens"],
#     temperature=config["openai"]["temperature"],
# )



#   GNU nano 6.2                                                                                       test_gpt.py                                                                                                 import os
# from openai import OpenAI

# # It's recommended to set your API key as an environment variable
# # to avoid hardcoding it in your script.
# # You can get your API key from https://platform.openai.com/
# client = OpenAI(api_key="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") # Replace with y>
# try:
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",  # You can also use other models like "gpt-4"
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": "Hello, world!"},
#         ]
#     )

#     print(response.choices[0].message.content)

# except Exception as e:
#     print(f"An error occurred: {e}")


async def get_chat_response(prompt: str, answer_type: str) -> str:
    print("Character Length of the prompt: ", len(prompt)) # TODO print should be replaced with a proper log
    print("words length of the prompt: ", len(prompt.split())) # TODO print should be replaced with a proper log
    # if answer_type == "qa":
    #     model_name = config["ollama"]["qa_model_name"]
    #     base_url = f"http://185.13.230.222:{str(config['ollama']['qa_model_port'])}/v1"
    #     num_ctx = config['ollama']['qa_model_num_ctx']
    #     llm = ChatOpenAI(
    #         openai_api_base=base_url,
    #         openai_api_key="EMPTY",
    #         model_name="/models/aya-expanse-32b-gptq-4bit"
    #     ) 
    # else:
    #     model_name = config["ollama"]["sql_model_name"]
    #     # base_url = f"http://ollama:{config['ollama']['sql_model_port']}"
    #     base_url = "http://localhost:8980"
    #     num_ctx = config['ollama']['sql_model_num_ctx']
    #     llm = ChatOllama(
    #         model=model_name,
    #         temperature=0,
    #         keep_alive=config["ollama"]["keep_alive"],
    #         seed=SEED,
    #         # base_url="http://ollama:11434",
    #         base_url=base_url, 
    #         num_ctx=num_ctx
    #     )
    
    # llm = ChatOpenAI(  # type: ignore[call-arg]
    #     openai_api_base="https://api.openai.com/v1",
    #     openai_api_key="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",
    #     # openai_proxy=secret["openai"]["proxy"],
    #     max_tokens=8192,
    #     model_name="gpt-4.1",
    #     temperature=0,
    # )

    # Load environment variables from .env file
    load_dotenv()

    # Access environment variables
    api_key = os.getenv('OPENROUTER_API_KEY')

    llm = ChatOpenAI(
        # openai_api_key=api_key,
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        # model_name="moonshotai/kimi-k2:free",
        model_name="deepseek/deepseek-r1-0528-qwen3-8b:free",
        streaming=False,
        temperature=0,
        # Optionally add headers via openai_client_headers or monkeypatch if needed
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
    return response


async def query_responder(query: str, context: str, history: str) -> str:
    # TODO: Add appropriate logger.
    
    serialized_history = history_serializer(history)
    prompt = RAG_SYSTEM_PROMPT.format(
        context=context,
        history=serialized_history,
        question=query,
    )
    response = await get_chat_response(prompt, answer_type="qa")
    return response
    # cleaned_response = json_cleaning(response)
    # cleaned_response_dict = json_text_cleaning(cleaned_response, "answer")
    # return cleaned_response_dict    


async def is_somewhat_uniform(freq_dict: dict, threshold: float = 0.65) -> bool:
    """
    Checks if the frequency distribution in a dictionary is somewhat uniform
    based on the Coefficient of Variation (CV).

    Args:
        freq_dict: A dictionary with items as keys and frequencies as values.
        threshold: The maximum allowed CV to be considered uniform.
                   Defaults to 0.3.

    Returns:
        True if the distribution is somewhat uniform, False otherwise.
    """
    # Ensure that the freq_dict has more than one item
    assert len(freq_dict) > 1, "Frequency dictionary must contain more than one item."
    
    frequencies = list(freq_dict.values())

    # Calculate mean and standard deviation
    mean_freq = statistics.mean(frequencies)
    
    # Avoid division by zero if all frequencies are 0
    if mean_freq == 0:
        return True, mean_freq # All items are 0, so it's perfectly uniform

    stdev_freq = statistics.stdev(frequencies)

    # Calculate the Coefficient of Variation (CV)
    cv = stdev_freq / mean_freq
    
    return cv < threshold, mean_freq


async def retrieve_context_with_metadata(query: str, input_modules: List) -> List[dict]:
    retriever = Retriever() 
    if input_modules:
        context_with_metadata = await retriever.retrieve_context(query, module_filter=input_modules)
    else:
        context_with_metadata = await retriever.retrieve_context(query)
    return context_with_metadata


async def prepare_final_context(query: str, input_module: str = "") -> Tuple[bool, List[str], Union[str, List[str]]]:
    """
    Analyzes query context and determines if clarification is needed for module selection.
    
    Args:
        query: The input query string
        
    Returns:
        Tuple containing:
        - bool: Whether clarification is needed
        - List[str]: List of detected/proposed modules
        - Union[str, List[str]]: Document content (single string or list of strings)
    """
    context_with_metadata = await retrieve_context_with_metadata(query, input_module)

    if not context_with_metadata:
        return False, [], []
    
    if input_module:
        # If a specific module is provided, we assume no clarification is needed
        return _handle_single_module_case(context_with_metadata, input_module)
    
    proposable_modules = set(config["modules"]["proposable_modules"])
    detected_modules = [result["module"] for result in context_with_metadata]
    module_frequencies = Counter(detected_modules)
    
    # Handle single module case
    if len(module_frequencies) < 2:
        detected_modules_lst = list(module_frequencies.keys())
        return _handle_single_module_case(context_with_metadata, detected_modules_lst[0])
    
    # Check if distribution is uniform (needs clarification)
    needs_clarification, mean_freq = await is_somewhat_uniform(module_frequencies)
    if not needs_clarification:
        max_value = max(module_frequencies.values())
        probable_detected_module = [k for k, v in module_frequencies.items() if v == max_value]
        return _handle_clear_preference_case(context_with_metadata, probable_detected_module[0])
    else:
        probable_detected_modules = [k for k, v in module_frequencies.items() if v > mean_freq] 
        return _handle_clarification_case(
            context_with_metadata, 
            probable_detected_modules, 
            proposable_modules
        )


def _handle_single_module_case(
    context_with_metadata: List, 
    detected_modules: List[str]
) -> Tuple[bool, List[str], str]:
    """Handle case where only one module type is detected."""
    documents = "\n\n".join(context["text"] for context in context_with_metadata)
    module = detected_modules if detected_modules else ""
    return False, [module], documents


def _handle_clear_preference_case(
    context_with_metadata: List, detected_module: str
) -> Tuple[bool, List[str], List[str]]:
    """Handle case where module preference is clear (no clarification needed)."""
    documents = [doc["text"] for doc in context_with_metadata]
    return False, detected_module, documents


def _handle_clarification_case(
    context_with_metadata: List,
    detected_modules: List[str],
    proposable_modules: Set[str]
) -> Tuple[bool, List[str], Union[str, List[str]]]:
    """Handle case where clarification is needed for module selection."""
    unique_modules = set(detected_modules)
    valid_modules = unique_modules & proposable_modules
    
    if len(valid_modules) < 2:
        # Not enough valid modules for clarification
        documents = context_with_metadata[0]["text"]
        valid_modules_lst = list(valid_modules)
        return False, valid_modules_lst, documents
    else:
        # Multiple valid modules - clarification needed
        documents = [doc["text"] for doc in context_with_metadata]
        valid_modules_lst = list(valid_modules)
        return True, valid_modules_lst, documents
        

async def module_proposer():
    return ["انبار و فروش", "دفتر کل"]


async def sql_responder_(query: str,
                         detected_module: str = "",
                         faulty_sql_query: str = "",
                         error_message: str = "",
                         do_retry: bool = False
                         ):
    if detected_module.strip() == "دفتر کل":
        if not do_retry:
            bo_prompt = SQL_CONVERTER_MODIFIED.format(schema=FINANCIAL_BO_MODIFIED, query=query)
        else:
            bo_prompt = SQL_MODIFIER.format(schema=FINANCIAL_BO_MODIFIED, original_query=query, faulty_sql_query=faulty_sql_query, error_message=error_message)
    else:
        if not do_retry:
            bo_prompt = SQL_CONVERTER_MODIFIED.format(schema=LOGISTICS_SALES_MODIFIED, query=query)
        else:
            bo_prompt = SQL_MODIFIER.format(schema=LOGISTICS_SALES_MODIFIED, original_query=query, faulty_sql_query=faulty_sql_query, error_message=error_message)
        
    raw_json_response = await get_chat_response(bo_prompt, answer_type="sql")
    response = json_cleaning(raw_json_response)
    response = response
    if not response:
        response = "در حال حاضر نمیتوانم به این سوال پاسخ دهم"
    return response
    
    
async def router_SQL_QA(query: str, context: str):
    prompt = QUERY_ROUTER.format(query=query, context=context)
    raw_response = await get_chat_response(prompt, answer_type="sql")
    response = json_cleaning(raw_response)
    return response

# async def qa_module_clarification(query: str, context: str):

async def chat_responder_(
    history: List[tuple[str, str]],
    user_utterance: str,
    detected_module: bool = False,
) -> tuple[str, str, str, bool, List[str]]:

    if not detected_module:
        response, url = await get_cache_response(
            user_utterance,
        )
        if response:
            return user_utterance, response, "", False, []

    paraphrased_utterance = await utterance_paraphraser(history, user_utterance)
    response, url = await get_cache_response(
        paraphrased_utterance,
    )
    if response:
        return paraphrased_utterance, response, "", False, []
    if detected_module:
        do_clarify, modules, context = await prepare_final_context(paraphrased_utterance, user_utterance) # user_utterance as detected_module
    else:
        do_clarify, modules, context = await prepare_final_context(paraphrased_utterance) # user_utterance as detected_module

    # When you detect a module, it is impossible not to return context
    if not context:
        return paraphrased_utterance, "", "", False, []

    if do_clarify:
        return paraphrased_utterance, "", "", do_clarify, modules
    
    route_response = await router_SQL_QA(paraphrased_utterance, context)
    if route_response == "DATABASE":
        return paraphrased_utterance, "", "", do_clarify, modules
    
    response = await query_responder(paraphrased_utterance, context, history)
    # json_response = fix_asterisks(json_response)
    # return paraphrased_utterance, json_response["answer"], context
    
    if "محدوده دانش من " in response:
        response = template_for_not_answer
    if "خارج از حوزه کاری" in response:
        response = template_for_not_context
    return paraphrased_utterance, response, context, do_clarify, modules


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
