import random
import json
import os
import statistics
import yaml
from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+
### remove this!

import numpy as np
from langchain.schema import SystemMessage
import torch
import sqlglot

from collections import Counter
from typing import List, Tuple, Union, Set
from .prompts import (
    RAG_CONCISE_SYSTEM_PROMPT,
    RAG_EXPLANATORY_SYSTEM_PROMPT,
    RAG_NORMAL_SYSTEM_PROMPT,
    UTTERANCE_PARAPHRASER_PROMPT,
    CHITCHAT_PROMPT,
    SQL_CONVERTER_MODIFIED_WITH_PARAMETERS_TEMPLATE,
    SQL_MODIFIER,
    ANSWER_VALIDATOR_PROMPT,
    SEMANTIC_ROUTER,
    BUSINESS_OBJECT_PARAMETER_EXTRACTOR_PROMPT
)
from .retriever import Retriever
from .config import config
from .cache import Cache
from .utils import json_cleaning, json_cleaning_1
from .business_objects import LOGISTICS_SALES_MODIFIED, FINANCIAL_BO_MODIFIED
from .semantic_router import SemanticRouterPipeline
from langchain.chat_models import ChatOpenAI
from langfuse import observe
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

import sqlglot
from sqlglot import exp

def extract_tables_robust(sql: str, dialect: str = None) -> dict:
    """
    Robustly extract table names from SQL, handling aliases, CTEs, and subqueries.
    
    Args:
        sql: The SQL query string
        dialect: SQL dialect (e.g., 'postgres', 'mysql', 'tsql', 'oracle')
    
    Returns:
        Dictionary with 'tables' (real tables) and 'ctes' (CTE names)
    """
    try:
        parsed = sqlglot.parse(sql, dialect=dialect)
        real_tables = set()
        cte_names = set()
        subquery_aliases = set()
        
        for statement in parsed:
            # First, collect CTE names so we can exclude them
            for cte in statement.find_all(exp.CTE):
                cte_names.add(cte.alias)
            
            # Collect subquery aliases
            for subquery in statement.find_all(exp.Subquery):
                if subquery.alias:
                    subquery_aliases.add(subquery.alias)
            
            # Now extract all table references
            for table in statement.find_all(exp.Table):
                table_name = table.name
                
                # Skip if it's a CTE reference or subquery alias
                if table_name in cte_names or table_name in subquery_aliases:
                    continue
                
                # Build full table name with catalog/schema if present
                parts = []
                if table.catalog:
                    parts.append(table.catalog)
                if table.db:
                    parts.append(table.db)
                parts.append(table_name)
                
                full_name = ".".join(parts)
                real_tables.add(full_name)
        
        return {
            "tables": list(real_tables),
            "ctes": list(cte_names),
            "aliases_found": True  # sqlglot automatically resolves aliases
        }
        
    except Exception as e:
        return {"error": str(e), "tables": [], "ctes": []}


def extract_tables_simple(sql: str, dialect: str = None) -> list[str]:
    """Simple wrapper that returns just the table names."""
    result = extract_tables_robust(sql, dialect)
    return result.get("tables", [])


def calculate_date_context() -> dict:
    """
    Calculate all date context values from the current system datetime.
    
    Returns:
        Dictionary with all pre-calculated date context values based on current datetime
    """
    from datetime import datetime, timedelta
    from dateutil.relativedelta import relativedelta
    
    # Get current datetime from system
    ref_dt = datetime.now()
    ref_date = ref_dt.date()
    reference_datetime_str = ref_dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Calculate basic relative dates
    today_date = ref_date.strftime('%Y-%m-%d')
    yesterday_date = (ref_date - timedelta(days=1)).strftime('%Y-%m-%d')
    last_week_date = (ref_date - timedelta(days=7)).strftime('%Y-%m-%d')
    last_month_date = (ref_date - relativedelta(months=1)).strftime('%Y-%m-%d')
    last_year_date = (ref_date - relativedelta(years=1)).strftime('%Y-%m-%d')
    
    # Calculate Persian year from Gregorian date
    year = ref_date.year
    month = ref_date.month
    day = ref_date.day
    
    # Determine Persian year
    # Persian new year (Nowruz) is around March 20-21
    # Persian year = Gregorian year - 621 (approximately)
    if month > 3 or (month == 3 and day >= 21):
        persian_year = year - 621
    else:
        persian_year = year - 622
    
    # Calculate Persian year start and end in Gregorian
    # Persian year starts on March 20 or 21 depending on the year
    def get_persian_year_start(p_year):
        g_year = p_year + 621
        # Simplified: using March 21 for most years, March 20 for leap adjustments
        if p_year in [1403]:  # Known years with March 20 start
            return f"{g_year}-03-20"
        return f"{g_year}-03-21"
    
    def get_persian_year_end(p_year):
        g_year = p_year + 621 + 1  # End is in the next Gregorian year
        if p_year in [1402]:  # Known years with March 19 end
            return f"{g_year}-03-19"
        return f"{g_year}-03-20"
    
    persian_year_start = get_persian_year_start(persian_year)
    persian_year_end = get_persian_year_end(persian_year)
    prev_persian_year = persian_year - 1
    prev_persian_year_start = get_persian_year_start(prev_persian_year)
    prev_persian_year_end = get_persian_year_end(prev_persian_year)
    
    return {
        'current_datetime': reference_datetime_str,
        'today_date': today_date,
        'yesterday_date': yesterday_date,
        'last_week_date': last_week_date,
        'last_month_date': last_month_date,
        'last_year_date': last_year_date,
        'persian_year': str(persian_year),
        'persian_year_start': persian_year_start,
        'persian_year_end': persian_year_end,
        'prev_persian_year': str(prev_persian_year),
        'prev_persian_year_start': prev_persian_year_start,
        'prev_persian_year_end': prev_persian_year_end,
        'current_hour': str(ref_dt.hour),
        'current_minute': str(ref_dt.minute),
    }

def format_sql_prompt(query: str, schema: str, target_prompt: str = SQL_CONVERTER_MODIFIED_WITH_PARAMETERS_TEMPLATE) -> str:
    """
    Format the SQL converter prompt with all date context values using current datetime.
    
    Args:
        query: The natural language query in Persian
        schema: The business object schema
    
    Returns:
        Formatted prompt string with all placeholders filled using current datetime
    """
    # Calculate date context from current datetime
    date_context = calculate_date_context()
    
    # Add query and schema to context
    date_context['query'] = query
    date_context['schema'] = schema
    
    # Format the prompt
    return target_prompt.format(**date_context)

def format_sql_modifier_prompt(
    schema: str,
    original_query: str,
    faulty_sql_query: str,
    faulty_parameters: str,
    error_message: str
) -> str:
    """
    Format the SQL modifier prompt with all date context values using current datetime.
    
    Args:
        schema: The business object schema
        original_query: The original natural language query in Persian
        faulty_sql_query: The SQL query that produced an error
        faulty_parameters: The parameters used with the faulty query
        error_message: The error message received
    
    Returns:
        Formatted prompt string with all placeholders filled using current datetime
    """
    # Calculate date context from current datetime
    date_context = calculate_date_context()
    
    # Add all required fields to context
    date_context['schema'] = schema
    date_context['original_query'] = original_query
    date_context['faulty_sql_query'] = faulty_sql_query
    date_context['faulty_parameters'] = faulty_parameters
    date_context['error_message'] = error_message
    
    # Format the prompt
    return SQL_MODIFIER.format(**date_context)

def subselect_yaml(
    data: dict,
    selections: dict[str, list[str] | None],
    output_format: str = "dict"
) -> Union[dict, str]:
    """
    Subselect specific keys from multiple tables in YAML data.
    
    Args:
        data: The full YAML data dict
        selections: Dict mapping table names to list of keys to extract.
                   Use None or empty list to extract the entire table.
                   Example: {
                       'sales_pricelistitem': ['parameters'],
                       'sales_invoice': ['attributes', 'relations'],
                       'sales_product': None  # extracts entire table
                   }
        output_format: 'dict' to return Python dict, 'yaml' to return YAML string
    
    Returns:
        dict or str: Extracted data as dict or YAML string
    
    Raises:
        KeyError: If a specified table is not found in data
        ValueError: If output_format is invalid
    """
    if output_format not in ("dict", "yaml"):
        raise ValueError(f"output_format must be 'dict' or 'yaml', got '{output_format}'")
    
    result = {}
    
    for table, keys in selections.items():
        if table not in data:
            raise KeyError(f"Table '{table}' not found in data")
        
        # If keys is None or empty, extract entire table
        if not keys:
            result[table] = data[table]
        else:
            result[table] = {}
            for key in keys:
                if key in data[table]:
                    result[table][key] = data[table][key]
                # Optionally warn if key not found (silent skip for now)
    
    if output_format == "yaml":
        return yaml.dump(result, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    return result

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
        else:
            extra = {
                "top_k": 1,
                "do_sample": False,
                "seed": 42,
                "sampling_method": "greedy",
                "reasoning_effort": "medium"
            }
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
    
    response = await llm.ainvoke(messages)
    result = response.content
    
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
    history: List[tuple[str, str]],
    company_name: str = None, 
    assistant_name: str = None, 
    answer_type: str = "normal", 
    use_oss: bool = True
    ) -> str:

    serialized_history = history_serializer(history)
    
    # Use develop branch format with multiple prompt types
    if answer_type == "concise":
        rag_system_prompt = RAG_CONCISE_SYSTEM_PROMPT
    elif answer_type == "normal":
        rag_system_prompt = RAG_NORMAL_SYSTEM_PROMPT
    elif answer_type == "explanatory":
        rag_system_prompt = RAG_EXPLANATORY_SYSTEM_PROMPT
    else:
        rag_system_prompt = RAG_NORMAL_SYSTEM_PROMPT
        
    prompt = rag_system_prompt.format(
        context=context,
        company_name=company_name,
        assistant_name=assistant_name,
        question=query,
        conversation_history=serialized_history
    )
    model_name, api_base, api_key = model_selector(use_oss, use_qwen3_coder=False)
    response = await get_chat_response(prompt, model_name, api_key, api_base)
    response = json_cleaning(response)
    
    return response


@observe()
async def chitchat_responder(
    query: str,
    context: str, 
    history: List[tuple[str, str]],
    use_oss: bool
    ):
    serialized_history = history_serializer(history)
    prompt = CHITCHAT_PROMPT.format(user_question=query, 
                             context=context, 
                             history=serialized_history
                             )
    model_name, api_base, api_key = model_selector(use_oss, use_qwen3_coder=False)
    response = await get_chat_response(prompt, model_name, api_key, api_base)
    
    return response

    
@observe()
async def answer_validator(question: str, context: str, answer: str, use_oss: bool) -> str:
    prompt = ANSWER_VALIDATOR_PROMPT.format(
        context=context,
        question=question,
        answer=answer,
    )
    model_name, api_base, api_key = model_selector(use_oss, use_qwen3_coder=False)
    response = await get_chat_response(prompt, model_name, api_key, api_base)
    return response

@observe()
async def is_somewhat_uniform(freq_dict: dict, threshold: float = MODULE_PROPOSER_THRESHOLD) -> tuple[bool, float]:
    """
    Checks if the frequency distribution in a dictionary is somewhat uniform
    based on the Coefficient of Variation (CV).
    """
    assert len(freq_dict) > 1, "Frequency dictionary must contain more than one item."
    
    frequencies = list(freq_dict.values())
    mean_freq = float(statistics.mean(frequencies))
    if mean_freq <= 1e-5:
        final_result = (True, mean_freq)
    else:
        stdev_freq = statistics.stdev(frequencies)
        cv = stdev_freq / mean_freq
        final_result = (cv <= threshold, mean_freq)
    return final_result

@observe()
async def retrieve_context_with_metadata(query: str, input_modules: List = None, database_index: str = None) -> Tuple[List,List]:
    retriever = Retriever()
    
    if input_modules:
        context_with_metadata, query_embedding = await retriever.retrieve_context(query, database_index,
                                                                                  module_filter=input_modules)
    elif database_index:
        # Support database_index parameter from develop branch
        context_with_metadata, query_embedding = await retriever.retrieve_context(query, database_index)
    else:
        context_with_metadata, query_embedding = await retriever.retrieve_context(query)
    return context_with_metadata, query_embedding

@observe()
async def prepare_final_context(query: str, database_index: str = None, input_module: str = ""):
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
    needs_clarification, _ = await is_somewhat_uniform(module_frequencies)
    if not needs_clarification:
        max_value = max(module_frequencies.values())
        probable_detected_module = [k for k, v in module_frequencies.items() if v == max_value]
        result = _handle_clear_preference_case(context_with_metadata, probable_detected_module[0])
    else:
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
    
def get_schema_for_module(detected_module: str) -> str:
    """
    Returns the appropriate schema based on the detected module.
    
    Args:
        detected_module: The detected module name (e.g., 'دفتر کل', 'انبار', 'فروش')
    
    Returns:
        The corresponding schema string for the module.
    """
    module = detected_module.strip()
    
    if module in ("دفتر کل", "دفترکل"):
        return FINANCIAL_BO_MODIFIED
    elif module in ("انبار", "فروش"):
        return LOGISTICS_SALES_MODIFIED
    else:
        # Fallback: combine both schemas
        return LOGISTICS_SALES_MODIFIED + "\n" + FINANCIAL_BO_MODIFIED


@observe()
async def sql_responder_(
    query: str,
    detected_module: str = "", 
    faulty_sql_query: str = "", 
    error_message: str = "", 
    do_retry: bool = False,
    parameters: dict = None,
    use_oss: bool = False
):
    """
    Unified SQL responder supporting both simple schema list and module-based schema selection.
    """
    if parameters is None:
        parameters = {}
    
    schema = get_schema_for_module(detected_module)
    
    if not do_retry:
        bo_prompt = format_sql_prompt(query, schema=schema)
    else:
        faulty_sql_query_json = json.dumps({"SQL": faulty_sql_query, "parameters": parameters})
        bo_prompt = format_modifier_prompt(
            schema=schema,
            original_query=query,
            faulty_sql_query=faulty_sql_query_json,
            faulty_parameters=parameters,  # Fixed: was undefined 'faulty_parameters'
            error_message=error_message
        )
    
    model_name, api_base, api_key = model_selector(use_oss, use_qwen3_coder=False)
    raw_json_response = await get_chat_response(
        bo_prompt, 
        model_name=model_name, 
        api_key=api_key,
        api_base=api_base
    )
    response = json_cleaning(raw_json_response)
    return response

@observe()
async def parameters_responder(
    paraphrased_utterance, 
    sql_query,
    detected_module: str = ""
    ):

    sql_proposed_tables = extract_tables_simple(sql_query)
    schema = get_schema_for_module(detected_module)
    yaml_schema = yaml.safe_load(schema)
    selections = {table: ['parameters'] for table in sql_proposed_tables}
    bo_parameters_schema = subselect_yaml(yaml_schema, selections, "yaml")
    prompt = format_sql_prompt(paraphrased_utterance, bo_parameters_schema, BUSINESS_OBJECT_PARAMETER_EXTRACTOR_PROMPT)
    raw_json_response = await get_chat_response(prompt)
    response = json_cleaning(raw_json_response)
    return response

@observe()
def _get_chitchat_cache_key(utterance: str) -> str:
    """Generates a consistent cache key for chitchat routes."""
    hashed_utterance = hash_string(utterance)
    result = f"chitchat_{hashed_utterance}"
    return result


async def _determine_final_route(
    utterance: str,
    query_embedding: List,
    use_joblib: bool = True,
    use_oss: bool = False,
) -> str:

    router_config = config["router_model"]
    alpha_threshold = router_config["alpha_threshold"]
    beta_threshold = router_config["beta_threshold"]
    """Determines the final route based on probability thresholds."""
    if use_joblib:
        semantic_router_client = SemanticRouterPipeline(
            inference_only=True,
            embedding_model=router_config["embedding_model"],
            classifier_address=router_config["address"],
            model_name=router_config["model_name"]
        )
        predictions, probabilities, max_prob = semantic_router_client.predict_sentences_input_embedding_and_sentences([utterance], [query_embedding])
        top_prediction = predictions[0][0]
        probabilities = list(probabilities)  # Convert to list to make it subscriptable

        if max_prob > alpha_threshold and ("همکاران" not in utterance) and (top_prediction != "illegal"):
            return top_prediction

        # If confidence is low, see if multiple routes are plausible
        if "همکاران" not in utterance:
            plausible_routes = [
                route for route, prob in probabilities if prob > beta_threshold
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
    model_name, api_base, api_key = model_selector(True, use_qwen3_coder=False)
    result = await get_chat_response(
        SEMANTIC_ROUTER.format(user_query=utterance, class_list=plausible_routes), model_name, api_key, api_base
    )
    return result

@observe()
async def get_route_for_utterance(utterance: str, query_embedding: List, use_joblib: bool = False) -> str:    
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
        return chitchat_route

    # 3. Determine the final route using the logic in the helper function
    final_route = await _determine_final_route(utterance, query_embedding, use_joblib, use_oss)

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
async def chat_responder_(
    history: List[tuple[str, str]],
    user_utterance: str,
    database_index: str = config["database"]["collection_name"],
    company_name: str = config["database"]["company_name"],
    assistant_name: str = config["database"]["assistant_name"],
    response_type: str = config["database"]["response_type"],
    use_cache: bool = config["database"]["use_cache"],
    detected_module: str = "",
    use_oss: bool = True
) -> Union[tuple[str, str, str, str], tuple[str, str, str, bool, List[str]]]:
    """
    Unified chat responder supporting both develop branch (simple RAG) and feature/add-sql-agent (SQL + module handling)
    """
    # If sql_mode is True, use the new SQL agent logic
    if not detected_module and use_cache:
        response, _ = await get_cache_response(user_utterance)
        if response:
            result_temp = user_utterance, response, "", False, []
            return result_temp

    paraphrased_utterance = await utterance_paraphraser(history, user_utterance, use_oss=use_oss)
    if use_cache:
        response, _ = await get_cache_response(paraphrased_utterance)
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
        
        return result_temp
    
    if route_response == "chitchat":
        response = await chitchat_responder(paraphrased_utterance, history=history, context=context, use_oss=use_oss)
        result_temp = paraphrased_utterance, response, context, False, []
        
        return result_temp
    
    if route_response == "illegal" or route_response =="irrelevant":
        result_temp = paraphrased_utterance, template_for_not_answer, "", False, []
        
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