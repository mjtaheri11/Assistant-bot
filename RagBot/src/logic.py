import random
import re
import os
import statistics
import yaml
import json
from dotenv import load_dotenv

import numpy as np
from langchain.schema import SystemMessage
import torch
import sqlglot
import tiktoken
from sqlglot import exp
from dataclasses import dataclass, field

from collections import Counter
from typing import List, Tuple, Union, Set, Any, Optional
from .prompts import (
    RAG_CONCISE_SYSTEM_PROMPT,
    RAG_CONCISE_SYSTEM_PROMPT_WITH_VIDEO,
    RAG_EXPLANATORY_SYSTEM_PROMPT,
    RAG_NORMAL_SYSTEM_PROMPT,
    UTTERANCE_PARAPHRASER_PROMPT,
    CHITCHAT_PROMPT,
    SQL_CONVERTER_MODIFIED_WITH_PARAMETERS_TEMPLATE_V2,
    ANSWER_VALIDATOR_PROMPT,
    SEMANTIC_ROUTER,
    BUSINESS_OBJECT_PARAMETER_EXTRACTOR_PROMPT
)

from .retriever import Retriever
from .config import config
from .cache import Cache
from .utils import json_cleaning, json_cleaning_1, calculate_date_context, format_documents_as_sql_examples, convert_sql_parameters, integrate_params, add_param_keys, has_video_link_

# ========================
# from .business_objects import LOGISTICS_SALES_MODIFIED, FINANCIAL_BO_MODIFIED, CRM_BO, LOGISTICS_MODIFIED #, TREASURY_BO
# from .business_objects import PARTIAL_LOGISTICS, PARTIAL_LOGISTICS_DDL, PARTIAL_LOGISTICS_SCHEMA_STYLE
from .bo_loader import ALL_BOS_RAW
from .bo_selector import get_schema_for_module
# ========================

from .semantic_router import SemanticRouterPipeline
from .default_examples import DEFAULT_EXAMPLES
from langchain.chat_models import ChatOpenAI
from langfuse import observe
import hashlib
from .llm_clients import llm_manager

# Load environment variables from .env file
load_dotenv()

SEED = 44
torch.manual_seed(SEED)
np.random.seed(SEED)
torch.cuda.manual_seed_all(SEED)
random.seed(SEED)
GPT_OSS_NAME = "/gpt-120"
OSS_LLM_MODEL_NAME = os.getenv("OSS_LLM_MODEL_NAME", GPT_OSS_NAME)
GPT_LLM_MODEL_NAME = os.getenv("GPT_LLM_MODEL_NAME", "gpt-4.1-2025-04-14")
QWEN3_CODER_LLM_MODEL_NAME = os.getenv("QWEN3_CODER_MODEL_NAME", "/Qwen/Qwen3-Coder-30B-A3B-Instruct")
OSS_API_KEY = os.getenv("OSS_API_KEY", "EMPTY")
GPT_API_KEY = os.getenv("GPT_API_KEY", "EMPTY")
QWEN3_CODER_API_KEY = os.getenv("QWEN3_CODER_API_KEY", "EMPTY")
USE_JOBLIB = config["router_model"]["use_joblib"]

LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_BASE_URL = os.getenv("LANGFUSE_BASE_URL")

OSS_API_BASE = os.getenv("OSS_API_BASE", "http://gpt-oss-120b-predictor.admin.svc.cluster.local/v1")
GPT_API_BASE = os.getenv("GPT_API_BASE", "https://api.openai.com/v1/")
QWEN3_CODER_API_BASE = os.getenv("QWEN3_CODER_API_BASE", "http://qwen3-coder-30b-predictor.admin.svc.cluster.local/v1")

QA_MODULE_PROPOSER_THRESHOLD = float(os.getenv("QA_MODULE_PROPOSER_THRESHOLD", 0.75))
SQL_MODULE_PROPOSER_THRESHOLD = float(os.getenv("SQL_MODULE_PROPOSER_THRESHOLD", 0.75))

MAX_PROMPT_SIZE = 16000
PROMPT_TEMPLATE_SIZE = 729
MAX_CONTEXT_AVAILABLE_SIZE = MAX_PROMPT_SIZE - PROMPT_TEMPLATE_SIZE

template_for_chitchat_answers = """من اینجا هستم تا تنها به سوالات مربوط به محصولات نسل چهارم شرکت همکاران سیستم پاسخ دهم. لطفاً سوالات خود را در مورد راه‌حل‌های نسل چهارم ما مطرح کنید."""
template_for_not_answer = "پاسخ به این سوال در محدوده پاسخگویی من نیست."
template_for_not_context = """این سوال خارج از حوزه کاری {company_name} است. لطفا سوال خود را در رابطه با محصولات و خدمات {company_name} مطرح کنید. برای اطلاعات بیشتر به 'https://systemgroup.net' مراجعه کنید"""
template_for_doubtful_answer = "سوال شما را به خوبی متوجه نشدم. لطفا سوال خود را به صورت دقیق تر بپرسید تا بتوانم بهتر کمک کنم."
MODULE_CLARIFICATION_RESPONSE_TEMPLATE = "لطفا مشخص نمایید سوال شما از کدام یک از ماژول های سیستم است."
RESPONSE_TEMPLATE_FOR_NO_ANSWER = "متاسفانه، پاسخی به سوال شما یافت نشد."

@dataclass
class ChatResult:
    utterance: str
    response: str = ""
    context: str = ""
    do_clarify: bool = False
    modules: List[str] = field(default_factory=list)

    def to_tuple(self):
        """Maintains backward compatibility if your caller expects a tuple."""
        return self.utterance, self.response, self.context, self.do_clarify, self.modules

def _get_statement_exclusions(statement: exp.Expression) -> tuple[set, set]:
    """
    Identifies temporary names (CTEs and subquery aliases) within a statement
    that should not be treated as real tables.
    """
    ctes = {cte.alias for cte in statement.find_all(exp.CTE)}
    aliases = {sub.alias for sub in statement.find_all(exp.Subquery) if sub.alias}
    return ctes, aliases

def finalize_parameters(a_dict, b_dict):
    # concatenation = {"parameters": a_dict["parameters"] | b_dict["parameters"]}
    concatenation = (a_dict | b_dict) | {"parameters": a_dict.get("parameters", {}) | b_dict.get("parameters", {})}
    return concatenation


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
            local_ctes, local_aliases = _get_statement_exclusions(statement)
            cte_names.update(local_ctes)
            subquery_aliases.update(local_aliases)
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
    Includes Persian calendar week boundaries (Saturday-Friday).
    Includes rolling day/week/month calculations for relative date expressions.
    """
    from datetime import datetime, timedelta
    from dateutil.relativedelta import relativedelta
    
    ref_dt = datetime.now()
    ref_date = ref_dt.date()
    reference_datetime_str = ref_dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # ========== BASIC DATES ==========
    today_date = ref_date.strftime('%Y-%m-%d')
    yesterday_date = (ref_date - timedelta(days=1)).strftime('%Y-%m-%d')
    last_month_date = (ref_date - relativedelta(months=1)).strftime('%Y-%m-%d')
    last_year_date = (ref_date - relativedelta(years=1)).strftime('%Y-%m-%d')
    
    # ========== ROLLING DAY CALCULATIONS ==========
    three_days_ago = (ref_date - timedelta(days=3)).strftime('%Y-%m-%d')
    one_week_ago = (ref_date - timedelta(days=7)).strftime('%Y-%m-%d')
    ten_days_ago = (ref_date - timedelta(days=10)).strftime('%Y-%m-%d')
    two_weeks_ago = (ref_date - timedelta(days=14)).strftime('%Y-%m-%d')
    three_weeks_ago = (ref_date - timedelta(days=21)).strftime('%Y-%m-%d')
    four_weeks_ago = (ref_date - timedelta(days=28)).strftime('%Y-%m-%d')
    
    # ========== ROLLING MONTH CALCULATIONS ==========
    two_months_ago = (ref_date - relativedelta(months=2)).strftime('%Y-%m-%d')
    three_months_ago = (ref_date - relativedelta(months=3)).strftime('%Y-%m-%d')
    six_months_ago = (ref_date - relativedelta(months=6)).strftime('%Y-%m-%d')
    
    # ========== PERSIAN WEEK CALCULATIONS ==========
    # Python weekday(): Monday=0, ..., Saturday=5, Sunday=6
    python_weekday = ref_date.weekday()
    days_since_saturday = (python_weekday - 5) % 7
    
    # Current week boundaries
    current_week_saturday = ref_date - timedelta(days=days_since_saturday)
    current_week_friday = current_week_saturday + timedelta(days=6)
    
    # Last week boundaries
    last_week_saturday = current_week_saturday - timedelta(days=7)
    last_week_friday = current_week_saturday - timedelta(days=1)
    
    # Persian day names
    persian_day_names = {
        5: 'شنبه', 6: 'یکشنبه', 0: 'دوشنبه', 1: 'سه‌شنبه',
        2: 'چهارشنبه', 3: 'پنجشنبه', 4: 'جمعه'
    }
    current_persian_day_name = persian_day_names[python_weekday]
    persian_day_index = days_since_saturday
    
    # Individual days - THIS WEEK
    this_week_saturday = current_week_saturday.strftime('%Y-%m-%d')
    this_week_sunday = (current_week_saturday + timedelta(days=1)).strftime('%Y-%m-%d')
    this_week_monday = (current_week_saturday + timedelta(days=2)).strftime('%Y-%m-%d')
    this_week_tuesday = (current_week_saturday + timedelta(days=3)).strftime('%Y-%m-%d')
    this_week_wednesday = (current_week_saturday + timedelta(days=4)).strftime('%Y-%m-%d')
    this_week_thursday = (current_week_saturday + timedelta(days=5)).strftime('%Y-%m-%d')
    this_week_friday = (current_week_saturday + timedelta(days=6)).strftime('%Y-%m-%d')
    
    # Individual days - LAST WEEK
    last_week_saturday_str = last_week_saturday.strftime('%Y-%m-%d')
    last_week_sunday = (last_week_saturday + timedelta(days=1)).strftime('%Y-%m-%d')
    last_week_monday = (last_week_saturday + timedelta(days=2)).strftime('%Y-%m-%d')
    last_week_tuesday = (last_week_saturday + timedelta(days=3)).strftime('%Y-%m-%d')
    last_week_wednesday = (last_week_saturday + timedelta(days=4)).strftime('%Y-%m-%d')
    last_week_thursday = (last_week_saturday + timedelta(days=5)).strftime('%Y-%m-%d')
    last_week_friday_str = last_week_friday.strftime('%Y-%m-%d')
    
    # ========== PERSIAN YEAR CALCULATIONS ==========
    year, month, day = ref_date.year, ref_date.month, ref_date.day
    persian_year = year - 621 if (month > 3 or (month == 3 and day >= 21)) else year - 622
    
    def get_persian_year_start(p_year):
        g_year = p_year + 621
        return f"{g_year}-03-20" if p_year in [1403] else f"{g_year}-03-21"
    
    def get_persian_year_end(p_year):
        g_year = p_year + 621 + 1
        return f"{g_year}-03-19" if p_year in [1402] else f"{g_year}-03-20"
    
    persian_year_start = get_persian_year_start(persian_year)
    persian_year_end = get_persian_year_end(persian_year)
    prev_persian_year = persian_year - 1
    prev_persian_year_start = get_persian_year_start(prev_persian_year)
    prev_persian_year_end = get_persian_year_end(prev_persian_year)
    
    return {
        'current_datetime': reference_datetime_str,
        'today_date': today_date,
        'yesterday_date': yesterday_date,
        'last_month_date': last_month_date,
        'last_year_date': last_year_date,
        
        # Rolling day calculations
        'three_days_ago': three_days_ago,
        'one_week_ago': one_week_ago,
        'ten_days_ago': ten_days_ago,
        'two_weeks_ago': two_weeks_ago,
        'three_weeks_ago': three_weeks_ago,
        'four_weeks_ago': four_weeks_ago,
        
        # Rolling month calculations
        'two_months_ago': two_months_ago,
        'three_months_ago': three_months_ago,
        'six_months_ago': six_months_ago,
        
        # Persian day info
        'current_persian_day_name': current_persian_day_name,
        'persian_day_index': str(persian_day_index),
        
        # This week (individual days)
        'this_week_saturday': this_week_saturday,
        'this_week_sunday': this_week_sunday,
        'this_week_monday': this_week_monday,
        'this_week_tuesday': this_week_tuesday,
        'this_week_wednesday': this_week_wednesday,
        'this_week_thursday': this_week_thursday,
        'this_week_friday': this_week_friday,
        
        # Last week (individual days)
        'last_week_saturday': last_week_saturday_str,
        'last_week_sunday': last_week_sunday,
        'last_week_monday': last_week_monday,
        'last_week_tuesday': last_week_tuesday,
        'last_week_wednesday': last_week_wednesday,
        'last_week_thursday': last_week_thursday,
        'last_week_friday': last_week_friday_str,
        
        # Persian year
        'persian_year': str(persian_year),
        'persian_year_start': persian_year_start,
        'persian_year_end': persian_year_end,
        'prev_persian_year': str(prev_persian_year),
        'prev_persian_year_start': prev_persian_year_start,
        'prev_persian_year_end': prev_persian_year_end,
        'current_hour': str(ref_dt.hour),
        'current_minute': str(ref_dt.minute),
    }

def format_sql_prompt(
    query: str, 
    schema: str, 
    target_prompt: str = SQL_CONVERTER_MODIFIED_WITH_PARAMETERS_TEMPLATE_V2,
    examples: Optional[str] = None
) -> str:
    """
    Format the SQL converter prompt with all date context values using current datetime.
    """
    # Calculate date context from current datetime
    date_context = calculate_date_context()
    
    # Use default examples if none provided
    raw_examples = examples if examples else DEFAULT_EXAMPLES
    
    # Format examples using regex to only replace known placeholders
    formatted_examples = replace_placeholders(raw_examples, date_context)

    # Add query, schema, and pre-formatted examples to context
    date_context['query'] = query
    date_context['schema'] = schema
    date_context['examples'] = formatted_examples
    
    # Format the final prompt
    final_prompt = target_prompt.format(**date_context)

    return final_prompt


def replace_placeholders(text: str, context: dict) -> str:
    """
    Replace only known placeholders in text, leaving JSON braces untouched.
    Matches {placeholder_name} only for keys that exist in context.
    """
    def replacer(match):
        key = match.group(1)
        if key in context:
            return str(context[key])
        # Return original if not a known placeholder
        return match.group(0)
    
    # Pattern matches {word_characters} but not empty braces or JSON-like patterns
    pattern = r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}'
    return re.sub(pattern, replacer, text)

def format_param_responder_prompt(query: str, sql_query: str, schema: str, target_prompt: str = SQL_CONVERTER_MODIFIED_WITH_PARAMETERS_TEMPLATE_V2) -> str:
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
    date_context['sql_query'] = sql_query
    
    # Format the prompt
    return target_prompt.format(**date_context)


def subselect_yaml(
    data: dict,
    selections: dict[str, list[str] | None],
    output_format: str = "dict"
) -> dict | str:
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


@observe()
async def get_chat_response_legacy(
        prompt: str, 
        model_name: str = OSS_LLM_MODEL_NAME,
        api_key=OSS_API_KEY, 
        api_base=OSS_API_BASE
    ) -> str:

    print("LLM_MODEL_NAME:", model_name)
    # Use OpenRouter if available, otherwise fall back to original configuration
    if api_base and model_name and api_key:
        if model_name != GPT_OSS_NAME:
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
            temperature=1,
            model_kwargs={},
            extra_body=extra
        )
    else:
        raise ValueError("No valid LLM configuration found in environment variables")


    messages = [SystemMessage(content=prompt)]
    
    response = await llm.ainvoke(messages)
    result = response.content
    
    return result

def extract_response_text(response, config) -> str:
    """Extract text from either Responses API or Chat Completions API response."""
    if config.supports_reasoning:
        # Responses API: response.output[0].content[0].text
        for item in response.output:
            if hasattr(item, 'content'):
                for content in item.content:
                    if hasattr(content, 'text'):
                        return content.text
        return ""
    else:
        # Chat Completions API: response.choices[0].message.content
        return response.choices[0].message.content or ""


# @observe()
# async def get_chat_response(
#         prompt: str, 
#         model_name,
#     ) -> str:

#     print("Character Length of the prompt: ", len(prompt))
#     print("words length of the prompt: ", len(prompt.split()))

    

#     # Prepare messages in the standard OpenAI dictionary format
#     # The original code used SystemMessage, so we use "role": "system"
#     messages = [
#         {"role": "system", "content": prompt}
#     ]

#     try:
#         response = await llm_manager.complete(model_name, messages)

#         # Extract text
#         _, config = llm_manager.get_model(model_name)
#         if config.supports_reasoning:
#             text = response.output[0].content[0].text
#         else:
#             text = response.choices[0].message.content
#         return text
#     except Exception as e:
#         # Basic error handling
#         print(f"Error generating response: {e}")
#         raise e

@observe()
async def get_cache_response(
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


async def process_sql_response(
    paraphrased_utterance: str,
    selected_module: str,
    context: str = "",
    model_name: str = "",
) -> tuple[bool, str, dict | None, str | None]:
    """
    Process SQL response and return (is_sql, response, parameters, response_template).
    """
    if not model_name:
        model_name = config["api_default"]["sql_responder_model_name"]
    if not context:
        context = DEFAULT_EXAMPLES
    response_dict_str = await sql_responder_(
        paraphrased_utterance,
        selected_module,
        context=context,
    )
    
    response_dict = json.loads(response_dict_str)
    
    if response_dict["SQL"] is None:
        return False, RESPONSE_TEMPLATE_FOR_NO_ANSWER, None, None
    
    response_dict["SQL"] = convert_sql_parameters(response_dict["SQL"])
    response = response_dict["SQL"]
    
    if response_dict["parameters"]:
        response_dict["parameters"] = add_param_keys(response_dict["parameters"])
    
    sql_with_params = integrate_params(response, response_dict["parameters"])    
    # bo_parameters_with_template = await parameters_responder(
    #     paraphrased_utterance,
    #     sql_with_params,
    #     selected_module,
    # )
    # bo_parameters_with_template_dict = json.loads(bo_parameters_with_template)
    # parameters_dict = finalize_parameters(response_dict, bo_parameters_with_template_dict)
    return (
        True,
        response,
        response_dict["parameters"],
        response_dict["response_template"]
    )


@observe()
async def utterance_paraphraser(
        history: List[tuple[str, str]], 
        user_utterance: str, 
        assistant_name: str = None, 
        model_name: str = "", 
        reasoning_effort: str = "high"
    ) -> str:
    serialized_history = history_serializer(history)
    if not model_name:
        model_name = config["api_default"]["utterance_paraphraser_model_name"]
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

    response_1 = await get_chat_response(prompt, model_name=model_name, reasoning_effort=reasoning_effort)
    response = json_cleaning_1(response_1)
    return response


async def get_chat_response(prompt: str, model_name: str, reasoning_effort="high") -> str:
    # 1. Initialize
    if not llm_manager._initialized:
        await llm_manager.initialize()

    # 2. Config & Role Selection
    _, config = llm_manager.get_model(model_name)
    
    # Use "user" for responses API models to be safe
    role = "system" 
    messages = [{"role": role, "content": prompt}]
    print("promtp word length:", len(prompt.split()))
    print("prompt character length:", len(prompt))

    print("Character Length of the prompt: ", len(prompt))
    print("words length of the prompt: ", len(prompt.split()))
    print("model_name:", model_name)
    try:
        # 3. Generate
        response = await llm_manager.complete(model_name, messages, reasoning_effort=reasoning_effort)
        
        # 4. Extract (Now using the robust regex fallback)
        text = llm_manager.extract_text(response, model_name)
        
        # Debug print to verify
        # print(f"Extracted Text: {text[:100]}...") 
        
        return text

    except Exception as e:
        print(f"Error generating response: {e}")
        raise e


async def embed_query(query):
    from src.retriever import ModelManager
    model_manager = ModelManager()
    embedding_query = await model_manager.embedding_model.aembed_query(query)
    return embedding_query


@observe()
async def chitchat_responder(
    query: str,
    context: str, 
    history: List[tuple[str, str]],
    model_name: bool = "", 
    reasoning_effort: str = "medium"
    ):
    if not model_name:
        model_name = config["api_default"]["chitchat_responder_model_name"]
    serialized_history = history_serializer(history)
    prompt = CHITCHAT_PROMPT.format(user_question=query, 
                             context=context, 
                             history=serialized_history
                             )
    response = await get_chat_response(prompt, model_name, reasoning_effort=reasoning_effort)
    return response

    
@observe()
async def answer_validator(question: str, context: str, answer: str, model_name: str = "", reasoning_effort="high") -> str:
    if not model_name: 
        model_name = config["api_default"]["answer_validator_model_name"]
    prompt = ANSWER_VALIDATOR_PROMPT.format(
        context=context,
        question=question,
        answer=answer,
    )
    response = await get_chat_response(prompt, model_name, reasoning_effort=reasoning_effort)
    return response


@observe()
async def is_somewhat_uniform(freq_dict: dict, threshold: float = QA_MODULE_PROPOSER_THRESHOLD) -> tuple[bool, float]:
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
        final_result = (cv <= threshold, mean_freq) # Thsi should be changed to less than, not equal or less than
    return final_result


@observe()
async def retrieve_context_with_metadata(query: str, input_modules: List = None, database_index: str = None, num_retrieve_context: int = config["retriever"]["retrieved_rank2_documents"]) -> Tuple[List,List]:
    retriever = Retriever()
    if input_modules:
        context_with_metadata, query_embedding = await retriever.retrieve_context(
            query, 
            database_index,
            module_filter=input_modules, 
            k=num_retrieve_context
            )
    elif database_index:
        # Support database_index parameter from develop branch
        context_with_metadata, query_embedding = await retriever.retrieve_context(query, database_index, k=num_retrieve_context)
    else:
        context_with_metadata, query_embedding = await retriever.retrieve_context(query, k=num_retrieve_context)
    return context_with_metadata, query_embedding


@observe()
async def prepare_final_context(
    query: str,
    query_embedding,
    database_index: str = None,
    input_module: str = "",
    num_retrieve_context=config["retriever"]["retrieved_rank2_documents"], 
    use_sql_modules: bool = False, 
    clarification_threshold: float = .7
):
    """
    Unified function supporting both develop branch (simple context)
    and feature/add-sql-agent (complex module handling)
    """
    context_with_metadata, query_embedding = await retrieve_context_with_metadata(
        query,
        database_index=database_index,
        input_modules=[input_module] if input_module else None, 
        num_retrieve_context=num_retrieve_context
    )
    if not context_with_metadata:
        return False, [], []

    if input_module:
        result = _handle_single_module_case(
            context_with_metadata, 
            input_module, 
            index_name=database_index
        )
        return result

    if use_sql_modules:
        proposable_modules = set(config["modules"]["sql_proposable_modules"])
    else:
        proposable_modules = set(config["modules"]["qa_proposable_modules"])
    detected_modules = [result["module"] for result in context_with_metadata]
    module_frequencies = Counter(detected_modules)
    print(module_frequencies)
    if len(module_frequencies) < 2:
        detected_modules_lst = list(module_frequencies.keys())
        result = _handle_single_module_case(
            context_with_metadata, 
            detected_modules_lst[0],
            index_name=database_index
        )
        return result

    print(module_frequencies)

    needs_clarification, _ = await is_somewhat_uniform(module_frequencies, threshold=clarification_threshold)

    if not needs_clarification:
        max_value = max(module_frequencies.values())
        probable_detected_module = [
            k for k, v in module_frequencies.items() if v == max_value
        ]
        result = _handle_clear_preference_case(
            context_with_metadata, 
            probable_detected_module[0],
            index_name=database_index
        )
    else:
        probable_detected_modules = list(module_frequencies.keys())
        result = _handle_clarification_case(
            context_with_metadata,
            probable_detected_modules,
            proposable_modules,
            index_name=database_index
        )

    return result


def _format_single_document(doc: dict, index: int = 1) -> str:
    """
    Format a single document based on whether it contains SQL or not.
    
    Args:
        doc: Document dict from _documents_to_standard_format
        index: Example number for formatting
        
    Returns:
        Formatted string for the document
    """
    sql_query = doc.get("sql", "")
    
    # If no SQL, return the text directly
    if not sql_query:
        # Append video links if present
        video_links = doc.get("video_links", [])
        if video_links:
            video_links_str = ", ".join(video_links)
            doc["text"] += f"=> [ویدیوی مرتبط: {video_links_str}]"
        return doc["text"]
    
    # Format as SQL example
    question = doc["text"]
    
    try:
        parameters = json.loads(doc.get("parameters", "{}"))
    except json.JSONDecodeError:
        parameters = {}
    
    params_formatted = ", ".join(
        f'"{k}": "{v}"' for k, v in parameters.items()
    )
    
    metadata = doc.get("metadata", {})
    complexity = metadata.get("complexity", "")
    domain = metadata.get("domain", "")
    response_template = doc.get("response_template", "")

    example_header = f"Example {index}"
    if complexity or domain:
        example_header += f" - {domain.capitalize() if domain else ''}"
        if complexity:
            example_header += f" ({complexity})"
    
    return f"""{example_header}:
Query: {question}
{{"SQL": "{sql_query}", "parameters": {{{params_formatted}}}, "response_template": {response_template}}}"""


def _format_documents_as_string(context_with_metadata: List[dict]) -> str:
    """Format multiple documents as a single concatenated string."""
    return "\n\n".join(
        _format_single_document(doc, i) 
        for i, doc in enumerate(context_with_metadata, 1)
    )


def _format_documents_as_list(context_with_metadata: List[dict]) -> List[str]:
    """Format multiple documents as a list of formatted strings."""
    return [
        _format_single_document(doc, i) 
        for i, doc in enumerate(context_with_metadata, 1)
    ]

@observe()
def _handle_single_module_case(
    context_with_metadata: List[dict],
    detected_modules: str,
    index_name: str
) -> Tuple[bool, List[str], str]:
    """Handle case where only one module type is detected."""
    documents = _format_documents_as_string(context_with_metadata)
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    num_tokens = len(encoding.encode(documents))
    print("num_tokens_of_context is %s" % num_tokens)
    if num_tokens > MAX_CONTEXT_AVAILABLE_SIZE:
        documents = _format_documents_as_string(context_with_metadata[-2:])
        print("Num new tokens is: %s" % num_tokens)
    return False, [detected_modules], documents

@observe()
def _handle_clear_preference_case(
    context_with_metadata: List[dict], 
    detected_module: str, 
    index_name: str
) -> Tuple[bool, List[str], List[str]]:
    """Handle case where module preference is clear (no clarification needed)."""
    documents = _format_documents_as_string(context_with_metadata)
    return False, [detected_module], documents

@observe()
def _handle_clarification_case(
    context_with_metadata: List[dict],
    detected_modules: List[str],
    proposable_modules: Set[str],
    index_name: str
) -> Tuple[bool, List[str], Union[str, List[str]]]:
    """Handle case where clarification is needed for module selection."""
    unique_modules = set(detected_modules)
    valid_modules = unique_modules & proposable_modules
    
    if len(valid_modules) < 2:
        documents = _format_single_document(context_with_metadata[0], index=1)
        valid_modules_lst = list(valid_modules)
        result = False, valid_modules_lst, documents
    else:
        documents = _format_documents_as_string(context_with_metadata)
        valid_modules_lst = list(valid_modules)
        result = True, valid_modules_lst, documents
    return result


def format_retrieved_as_prompt_examples(
    retrieved_docs: List,
    max_examples: int = 10
) -> str:
    """
    Format retrieved documents as examples for the SQL converter prompt.
    
    Args:
        retrieved_docs: List of Documents from vector similarity search
        max_examples: Maximum number of examples to include
        
    Returns:
        Formatted string of examples ready for prompt injection
    """
    # Convert raw Documents to standard format first
    formatted_docs = []
    for idx, doc in enumerate(retrieved_docs[:max_examples]):
        formatted_doc = {
            "text": doc.page_content,
            "index": idx,
            "module": doc.metadata.get("module", "unknown"),
            "source": doc.metadata.get("source", "unknown"),
            "sql": doc.metadata.get("sql", ""),
            "parameters": doc.metadata.get("parameters", "{}"),
            "response_template": doc.metadata.get("response_template", ""),
            "metadata": doc.metadata
        }
        formatted_docs.append(formatted_doc)
    
    return _format_documents_as_string(formatted_docs)

    
# def get_schema_for_module(detected_module: str) -> str:
#     """
#     Returns the appropriate schema based on the detected module.
    
#     Args:
#         detected_module: The detected module name (e.g., 'دفتر کل', 'انبار', 'فروش')
    
#     Returns:
#         The corresponding schema string for the module.
#     """
#     module = detected_module.strip()
    
#     if module.strip() in ("دفتر کل", "دفترکل"):
#         return FINANCIAL_BO_MODIFIED
#     elif module.strip() in ("انبار"):
#         return LOGISTICS_MODIFIED
#     elif module.strip() in ("فروش"):
#         return LOGISTICS_SALES_MODIFIED
#     elif module in ("مدیریت ارتباط با مشتری"):
#         return CRM_BO
#     # elif module in ("خزانه داری"):
#     #     return TREASURY_BO
#     else:
#         # Fallback: combine both schemas
#         return LOGISTICS_SALES_MODIFIED + "\n" + FINANCIAL_BO_MODIFIED


@observe()
async def sql_responder_(
    query: str,
    detected_module: str = "",
    context: str = "",
    model_name: str = "",
    reasoning_effort="medium"
):
    if not model_name:
        model_name = config["api_default"]["sql_responder_model_name"]

    schema_fmt = config.get("schema", {}).get("format", "create_table")
    schema = get_schema_for_module(ALL_BOS_RAW, detected_module, fmt=schema_fmt)

    bo_prompt = format_sql_prompt(query, schema=schema, examples=context)
    raw_json_response = await get_chat_response(
        bo_prompt, model_name, reasoning_effort=reasoning_effort
    )
    response = json_cleaning(raw_json_response)
    return response


@observe()
async def parameters_responder(
    paraphrased_utterance, 
    sql_query,
    detected_module: str,
    model_name: str = "",
    reasoning_effort="medium"
    ):

    if not model_name: 
        model_name = config["api_default"]["parameter_responder_model_name"]
    sql_proposed_tables = extract_tables_simple(sql_query)
    # schema = get_schema_for_module(detected_module)
    schema_fmt = config.get("schema", {}).get("format", "yaml_grouped")
    schema = get_schema_for_module(ALL_BOS_RAW, detected_module, fmt=schema_fmt)
    yaml_schema = yaml.safe_load(schema)
    selections = {table: ['parameters'] for table in sql_proposed_tables}
    bo_parameters_schema = subselect_yaml(yaml_schema, selections, "yaml")
    prompt = format_param_responder_prompt(paraphrased_utterance, sql_query, bo_parameters_schema, BUSINESS_OBJECT_PARAMETER_EXTRACTOR_PROMPT)
    raw_json_response = await get_chat_response(prompt, model_name, reasoning_effort=reasoning_effort)
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
    model_name: str = "",
    reasoning_effort="medium"
) -> str:

    if not model_name: 
        model_name = config["api_default"]["module_route_model_name"]
    router_config = config["router_model"]
    alpha_threshold = router_config["alpha_threshold"]
    beta_threshold = router_config["beta_threshold"]
    """Determines the final route based on probability thresholds."""
    if USE_JOBLIB:
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
    result = await get_chat_response(
        SEMANTIC_ROUTER.format(user_query=utterance, class_list=plausible_routes), model_name, reasoning_effort=reasoning_effort
    )
    return result

@observe()
async def get_route_for_utterance(utterance: str, query_embedding: List, model_name: str = "") -> str:
    if not model_name:
        model_name = config["api_default"]["module_route_model_name"]
    CHITCHAT_ROUTE = "chitchat"
    
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

    # 3. Determine the final route using the logic in the helper function
    final_route = await _determine_final_route(utterance, query_embedding, model_name)

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

async def _check_cache_layer(utterance: str, use_cache: bool) -> Optional[str]:
    """Handles the cache lookup logic."""
    if not use_cache:
        return None
    response, _ = await get_cache_response(utterance)
    return response

def _post_process_rag_response(response: str, company_name: str) -> str:
    """Handles specific string replacements and fallback logic."""
    if "محدوده دانش من " in response:
        return template_for_not_answer
    if "خارج از حوزه کاری" in response:
        return template_for_not_context.format(company_name=company_name)
    return response


@observe()
async def query_responder(
    query: str, 
    context: str, 
    history: List[tuple[str, str]],
    company_name: str = None, 
    assistant_name: str = None, 
    answer_type: str = "concise", 
    reasoning_effort="medium",
    model_name: str = "",
    use_video_links: bool = False
    ) -> Tuple[str, dict]:
    if not model_name:
        model_name = config["api_default"]["query_responder_model_name"]

    serialized_history = history_serializer(history)
    
    if answer_type == "concise":
        rag_system_prompt = RAG_CONCISE_SYSTEM_PROMPT_WITH_VIDEO if use_video_links else RAG_CONCISE_SYSTEM_PROMPT
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

    raw_json_response = await get_chat_response(
        prompt, 
        model_name, 
        reasoning_effort=reasoning_effort
    )
    cleaned_response = json_cleaning(raw_json_response)
    
    if use_video_links:
        try:
            response_dict = json.loads(cleaned_response)
            response_text = response_dict.get("response", cleaned_response)
            video_parameters = response_dict.get("parameters", {})
        except (json.JSONDecodeError, TypeError):
            response_text = cleaned_response
            video_parameters = {}
    else:
        response_text = cleaned_response
        video_parameters = {}
    
    return response_text, video_parameters

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
    sql_mode: bool = True,
    route_for_utterance: bool = False,
    use_video_links: bool = True  # <-- add this
) -> Union[tuple[str, str, str, str], tuple[str, str, str, bool, List[str]]]:
    """
    Unified chat responder supporting both develop branch (simple RAG) and feature/add-sql-agent (SQL + module handling)
    """
    # If sql_mode is True, use the new SQL agent logic
    is_sql = False
    num_retrieve_context = config["retriever"]["retrieved_rank2_documents"]
    parameters = {}
    sql_response_template = ""
    has_video_link = False
    if not detected_module and use_cache:
        response, _ = await get_cache_response(user_utterance)
        if response:
            result_temp = is_sql, user_utterance, response, "", False, [], parameters, sql_response_template, has_video_link
            return result_temp

    paraphrased_utterance = await utterance_paraphraser(history, user_utterance)
    print(paraphrased_utterance)
    if use_cache:
        response, _ = await get_cache_response(paraphrased_utterance)
        if response:
            result_temp = is_sql, paraphrased_utterance, response, "", False, [], parameters, sql_response_template, has_video_link
            return result_temp

    query_embedding = await embed_query(paraphrased_utterance)
    if sql_mode: 
        route_response = await get_route_for_utterance(paraphrased_utterance, query_embedding)
        # route_response = "qa"
    else:
        route_response = "qa"
    use_sql_modules = True if route_response == "sql" else False
    if route_response == "chitchat":
        response = RESPONSE_TEMPLATE_FOR_NO_ANSWER
        context = ""
        result_temp = is_sql, paraphrased_utterance, response, context, False, [], parameters, sql_response_template, has_video_link
        return result_temp
    
    if route_response == "illegal" or route_response =="irrelevant":
        result_temp = is_sql, paraphrased_utterance, template_for_not_answer, "", False, [], parameters, sql_response_template, has_video_link
        return result_temp

    if route_response == "sql":
        clarification_threshold = SQL_MODULE_PROPOSER_THRESHOLD
        # database_index = config["database"]["sql_collection_name"]
    else:
        clarification_threshold = QA_MODULE_PROPOSER_THRESHOLD
    
    if detected_module:
        do_clarify, modules, context = await prepare_final_context(paraphrased_utterance, database_index=database_index, input_module=detected_module, query_embedding=query_embedding, num_retrieve_context=num_retrieve_context, use_sql_modules=use_sql_modules, clarification_threshold=clarification_threshold)
    else:
        do_clarify, modules, context = await prepare_final_context(paraphrased_utterance, database_index=database_index, query_embedding=query_embedding, num_retrieve_context=num_retrieve_context, use_sql_modules=use_sql_modules, clarification_threshold=clarification_threshold)

    if do_clarify:
        result_temp = is_sql, paraphrased_utterance, MODULE_CLARIFICATION_RESPONSE_TEMPLATE, "", do_clarify, modules, parameters, sql_response_template, has_video_link
        return result_temp

    if sql_mode:
        if route_response == "sql":
            num_retrieve_context = config["retriever"]["sql_retrieved_rank2_documents"]
            detected_database_index = config["database"]["sql_collection_name"]
        else:
            detected_database_index = database_index
            
    if route_response == "sql" and sql_mode:
        selected_module = modules[0] 
        if selected_module in config["modules"]["available_sql_modules"]:
            do_clarify, modules_2 , context = await prepare_final_context(paraphrased_utterance, database_index=config["database"]["sql_collection_name"], query_embedding=query_embedding, input_module=selected_module, num_retrieve_context=num_retrieve_context)
            if len(modules_2) == 0:
                modules_2 = modules 
            assert do_clarify == False, "The problem related to the prepare final context module. Do clarify should be False"
            assert len(modules_2) == 1, "The problem related to the prepare final context module. length of modules should be one"
            is_sql, response, parameters, sql_response_template = await process_sql_response(
                paraphrased_utterance,
                selected_module,
                context,
            )
            if not is_sql: 
                parameters = {}
                sql_response_template = ""  
            result_temp = is_sql, paraphrased_utterance, response, context, False, [selected_module], parameters, sql_response_template, has_video_link
            return result_temp

    if not context:
        response = template_for_not_answer
        context = ""
        result_temp = is_sql, paraphrased_utterance, response, context, False, [], parameters, sql_response_template, has_video_link
        return result_temp

    response, video_parameters = await query_responder(
        paraphrased_utterance,
        context,
        history,
        company_name=company_name,
        assistant_name=assistant_name,
        answer_type=response_type,
        use_video_links=use_video_links,
    )
    if "محدوده دانش من " in response:
        response = template_for_not_answer
        video_parameters = {}
    if "خارج از حوزه کاری" in response:
        response = template_for_not_context.format(company_name=company_name)
        video_parameters = {}
    parameters = video_parameters
    has_video_link = has_video_link_(parameters)
    result_temp = is_sql, paraphrased_utterance, response, context, do_clarify, modules, parameters, sql_response_template, has_video_link
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
        cache.increment_thumb_up(query, response, url)
    elif feedback_type == "thumb_down":
        cache.increment_thumb_down(query, response, url)
    elif feedback_type == "flag":
        cache.increment_flag(query, response, url)