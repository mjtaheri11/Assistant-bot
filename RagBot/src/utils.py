import json

import streamlit as st
JSON_START_STR = "```json"

def get_substituted_value(param_value):
    # Handle different data types
    if isinstance(param_value, str):
        # Escape single quotes in strings and wrap in quotes
        escaped_value = param_value.replace("'", "''")
        substituted_value = f"'{escaped_value}'"
    elif isinstance(param_value, (int, float)):
        # Numbers don't need quotes
        substituted_value = str(param_value)
    elif isinstance(param_value, list):
        # For lists, we'll take the first element (you may want to modify this behavior)
        if param_value and isinstance(param_value[0], str):
            escaped_value = param_value[0].replace("'", "''")
            substituted_value = f"'{escaped_value}'"
        elif param_value:
            substituted_value = str(param_value[0])
        else:
            substituted_value = "NULL"
    elif param_value is None:
        substituted_value = "NULL"
    else:
        # For other types, convert to string and wrap in quotes
        substituted_value = f"'{str(param_value)}'"
    return substituted_value
import yaml
from pythonjsonlogger import jsonlogger
from langchain_core.documents import Document

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Tuple, Optional, Dict, Any

# Try to import jdatetime for accurate Persian calendar conversion
try:
    import jdatetime
    JDATETIME_AVAILABLE = True
except ImportError:
    JDATETIME_AVAILABLE = False


"""
Enhanced date context calculator with accurate Persian (Jalali) calendar support.

This module provides date context for prompts including:
- Gregorian date references (today, yesterday, last month, last year)
- Persian (Jalali) week boundaries (Saturday-Friday)
- Accurate Persian year calculations using jdatetime library
- Individual day references for current and previous weeks

Dependencies:
- python-dateutil
- jdatetime (pip install jdatetime)
"""

# ============================================================================
# CONSTANTS
# ============================================================================

# Persian month names (1-indexed)
PERSIAN_MONTH_NAMES = {
    1: 'فروردین', 2: 'اردیبهشت', 3: 'خرداد',
    4: 'تیر', 5: 'مرداد', 6: 'شهریور',
    7: 'مهر', 8: 'آبان', 9: 'آذر',
    10: 'دی', 11: 'بهمن', 12: 'اسفند'
}

# Persian day names (keyed by Python weekday: Monday=0, ..., Sunday=6)
PERSIAN_DAY_NAMES = {
    5: 'شنبه',      # Saturday
    6: 'یکشنبه',    # Sunday
    0: 'دوشنبه',    # Monday
    1: 'سه‌شنبه',   # Tuesday
    2: 'چهارشنبه',  # Wednesday
    3: 'پنجشنبه',   # Thursday
    4: 'جمعه'       # Friday
}


# ============================================================================
# PERSIAN CALENDAR FUNCTIONS
# ============================================================================

def gregorian_to_persian(g_year: int, g_month: int, g_day: int) -> Tuple[int, int, int]:
    """
    Convert Gregorian date to Persian (Jalali) date.
    
    Args:
        g_year: Gregorian year
        g_month: Gregorian month (1-12)
        g_day: Gregorian day
        
    Returns:
        Tuple of (persian_year, persian_month, persian_day)
    """
    if JDATETIME_AVAILABLE:
        jd = jdatetime.date.fromgregorian(year=g_year, month=g_month, day=g_day)
        return jd.year, jd.month, jd.day
    else:
        # Fallback: simplified calculation (less accurate for edge cases)
        return _gregorian_to_persian_fallback(g_year, g_month, g_day)


def persian_to_gregorian(p_year: int, p_month: int, p_day: int) -> Tuple[int, int, int]:
    """
    Convert Persian (Jalali) date to Gregorian date.
    
    Args:
        p_year: Persian year
        p_month: Persian month (1-12)
        p_day: Persian day
        
    Returns:
        Tuple of (gregorian_year, gregorian_month, gregorian_day)
    """
    if JDATETIME_AVAILABLE:
        jd = jdatetime.date(p_year, p_month, p_day)
        gd = jd.togregorian()
        return gd.year, gd.month, gd.day
    else:
        return _persian_to_gregorian_fallback(p_year, p_month, p_day)


def is_persian_leap_year(year: int) -> bool:
    """
    Check if a Persian year is a leap year.
    
    Args:
        year: Persian year
        
    Returns:
        True if leap year, False otherwise
    """
    if JDATETIME_AVAILABLE:
        return jdatetime.date(year, 1, 1).isleap()
    else:
        return _is_persian_leap_year_fallback(year)


def get_persian_year_bounds(persian_year: int) -> Tuple[str, str]:
    """
    Get the Gregorian start and end dates for a Persian year.
    
    Args:
        persian_year: The Persian year
        
    Returns:
        Tuple of (start_date, end_date) in 'YYYY-MM-DD' format
    """
    # Start: Farvardin 1
    start_g = persian_to_gregorian(persian_year, 1, 1)
    start_date = f"{start_g[0]:04d}-{start_g[1]:02d}-{start_g[2]:02d}"
    
    # End: Esfand 29 or 30 (depending on leap year)
    last_day = 30 if is_persian_leap_year(persian_year) else 29
    end_g = persian_to_gregorian(persian_year, 12, last_day)
    end_date = f"{end_g[0]:04d}-{end_g[1]:02d}-{end_g[2]:02d}"
    
    return start_date, end_date


def get_days_in_persian_month(year: int, month: int) -> int:
    """
    Get the number of days in a Persian month.
    
    Args:
        year: Persian year
        month: Persian month (1-12)
        
    Returns:
        Number of days in the month
    """
    if month <= 6:
        return 31
    elif month <= 11:
        return 30
    else:  # month 12 (Esfand)
        return 30 if is_persian_leap_year(year) else 29


# ============================================================================
# FALLBACK IMPLEMENTATIONS (when jdatetime is not available)
# ============================================================================

def _is_persian_leap_year_fallback(year: int) -> bool:
    """
    Fallback leap year check using the 33-year sub-cycle pattern.
    
    The Persian calendar follows a complex 2820-year cycle, but for practical
    purposes (years 1178-1633, or 1799-2254 CE), the 33-year cycle is accurate.
    
    In each 33-year cycle, years at positions 1, 5, 9, 13, 17, 22, 26, 30 are leap.
    """
    # Leap years in a 33-year cycle (0-indexed positions)
    leap_positions = {0, 4, 8, 12, 16, 21, 25, 29}
    
    # Adjust to cycle position (using reference year 1375 which is position 0)
    cycle_position = (year - 1375) % 33
    if cycle_position < 0:
        cycle_position += 33
    
    return cycle_position in leap_positions


def _gregorian_to_persian_fallback(g_year: int, g_month: int, g_day: int) -> Tuple[int, int, int]:
    """
    Fallback Gregorian to Persian conversion.
    
    This uses a day-counting approach from a known reference point.
    """
    # Reference: March 21, 2024 = Farvardin 1, 1403
    ref_g = datetime(2024, 3, 20)
    ref_p = (1403, 1, 1)
    
    target = datetime(g_year, g_month, g_day)
    delta_days = (target - ref_g).days
    
    p_year, p_month, p_day = ref_p
    
    if delta_days >= 0:
        # Move forward
        while delta_days > 0:
            days_in_month = get_days_in_persian_month(p_year, p_month)
            days_left_in_month = days_in_month - p_day
            
            if delta_days <= days_left_in_month:
                p_day += delta_days
                delta_days = 0
            else:
                delta_days -= (days_left_in_month + 1)
                p_month += 1
                p_day = 1
                if p_month > 12:
                    p_month = 1
                    p_year += 1
    else:
        # Move backward
        while delta_days < 0:
            if p_day + delta_days >= 1:
                p_day += delta_days
                delta_days = 0
            else:
                delta_days += p_day
                p_month -= 1
                if p_month < 1:
                    p_month = 12
                    p_year -= 1
                p_day = get_days_in_persian_month(p_year, p_month)
    
    return p_year, p_month, p_day


def _persian_to_gregorian_fallback(p_year: int, p_month: int, p_day: int) -> Tuple[int, int, int]:
    """
    Fallback Persian to Gregorian conversion.
    """
    # Reference: Farvardin 1, 1403 = March 20, 2024
    ref_p = (1403, 1, 1)
    ref_g = datetime(2024, 3, 20)
    
    # Calculate days from reference Persian date
    days_delta = 0
    
    if (p_year, p_month, p_day) >= ref_p:
        # Count forward
        y, m, d = ref_p
        while (y, m, d) != (p_year, p_month, p_day):
            days_in_month = get_days_in_persian_month(y, m)
            if y == p_year and m == p_month:
                days_delta += p_day - d
                break
            else:
                days_delta += days_in_month - d + 1
                d = 1
                m += 1
                if m > 12:
                    m = 1
                    y += 1
    else:
        # Count backward
        y, m, d = ref_p
        while (y, m, d) != (p_year, p_month, p_day):
            if y == p_year and m == p_month:
                days_delta -= d - p_day
                break
            else:
                days_delta -= d
                m -= 1
                if m < 1:
                    m = 12
                    y -= 1
                d = get_days_in_persian_month(y, m)
    
    result = ref_g + timedelta(days=days_delta)
    return result.year, result.month, result.day


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def calculate_date_context() -> dict:
    """
    Calculate all date context values from the current system datetime.
    Includes Persian calendar week boundaries (Saturday-Friday).
    
    Returns:
        Dictionary containing:
        - current_datetime: Full datetime string
        - today_date, yesterday_date, last_month_date, last_year_date
        - current_persian_day_name, persian_day_index
        - this_week_* and last_week_* for each day (Saturday-Friday)
        - persian_year, persian_year_start, persian_year_end
        - prev_persian_year, prev_persian_year_start, prev_persian_year_end
        - current_hour, current_minute
    """
    ref_dt = datetime.now()
    ref_date = ref_dt.date()
    reference_datetime_str = ref_dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # ========== BASIC GREGORIAN DATES ==========
    today_date = ref_date.strftime('%Y-%m-%d')
    yesterday_date = (ref_date - timedelta(days=1)).strftime('%Y-%m-%d')
    last_month_date = (ref_date - relativedelta(months=1)).strftime('%Y-%m-%d')
    last_year_date = (ref_date - relativedelta(years=1)).strftime('%Y-%m-%d')
    
    # ========== PERSIAN WEEK CALCULATIONS ==========
    # Python weekday(): Monday=0, Tuesday=1, ..., Saturday=5, Sunday=6
    # Persian week: Saturday (شنبه) is the first day
    python_weekday = ref_date.weekday()
    days_since_saturday = (python_weekday - 5) % 7  # 0 for Saturday, 1 for Sunday, etc.
    
    # Current week boundaries (Saturday to Friday)
    current_week_saturday = ref_date - timedelta(days=days_since_saturday)
    
    # Last week boundaries
    last_week_saturday = current_week_saturday - timedelta(days=7)
    last_week_friday = current_week_saturday - timedelta(days=1)
    
    # Persian day info
    current_persian_day_name = PERSIAN_DAY_NAMES[python_weekday]
    persian_day_index = days_since_saturday  # 0=Saturday, ..., 6=Friday
    
    # ========== INDIVIDUAL DAYS - THIS WEEK ==========
    this_week_saturday = current_week_saturday.strftime('%Y-%m-%d')
    this_week_sunday = (current_week_saturday + timedelta(days=1)).strftime('%Y-%m-%d')
    this_week_monday = (current_week_saturday + timedelta(days=2)).strftime('%Y-%m-%d')
    this_week_tuesday = (current_week_saturday + timedelta(days=3)).strftime('%Y-%m-%d')
    this_week_wednesday = (current_week_saturday + timedelta(days=4)).strftime('%Y-%m-%d')
    this_week_thursday = (current_week_saturday + timedelta(days=5)).strftime('%Y-%m-%d')
    this_week_friday = (current_week_saturday + timedelta(days=6)).strftime('%Y-%m-%d')
    
    # ========== INDIVIDUAL DAYS - LAST WEEK ==========
    last_week_saturday_str = last_week_saturday.strftime('%Y-%m-%d')
    last_week_sunday = (last_week_saturday + timedelta(days=1)).strftime('%Y-%m-%d')
    last_week_monday = (last_week_saturday + timedelta(days=2)).strftime('%Y-%m-%d')
    last_week_tuesday = (last_week_saturday + timedelta(days=3)).strftime('%Y-%m-%d')
    last_week_wednesday = (last_week_saturday + timedelta(days=4)).strftime('%Y-%m-%d')
    last_week_thursday = (last_week_saturday + timedelta(days=5)).strftime('%Y-%m-%d')
    last_week_friday_str = last_week_friday.strftime('%Y-%m-%d')
    
    # ========== PERSIAN CALENDAR CALCULATIONS ==========
    persian_year, persian_month, persian_day = gregorian_to_persian(
        ref_date.year, ref_date.month, ref_date.day
    )
    
    # Get accurate Persian year boundaries
    persian_year_start, persian_year_end = get_persian_year_bounds(persian_year)
    prev_persian_year_start, prev_persian_year_end = get_persian_year_bounds(persian_year - 1)
    
    return {
        # Basic datetime info
        'current_datetime': reference_datetime_str,
        'today_date': today_date,
        'yesterday_date': yesterday_date,
        'last_month_date': last_month_date,
        'last_year_date': last_year_date,
        
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
        
        # Persian year (same output format as original)
        'persian_year': str(persian_year),
        'persian_year_start': persian_year_start,
        'persian_year_end': persian_year_end,
        'prev_persian_year': str(persian_year - 1),
        'prev_persian_year_start': prev_persian_year_start,
        'prev_persian_year_end': prev_persian_year_end,
        
        # Time components
        'current_hour': str(ref_dt.hour),
        'current_minute': str(ref_dt.minute),
    }



@staticmethod
def format_documents_as_sql_examples(
    documents: list[dict],
    max_examples: Optional[int] = None,
    include_analysis: bool = True,
    number_from: int = 1
) -> str:
    """
    Convert standard format documents to the SQL prompt examples format.
    
    Args:
        documents: List of documents in standard format from _documents_to_standard_format
        max_examples: Maximum number of examples to include (None for all)
        include_analysis: Whether to include analysis text if available
        number_from: Starting number for example numbering
    
    Returns:
        Formatted string of examples for the SQL converter prompt
    
    Example output:
        Example 1 - Sales Query:
        Query: مجموع فروش هفته گذشته
        Analysis: "هفته گذشته" = calendar week
        {{"SQL": "SELECT SUM(...)", "parameters": {{"1": "value"}}}}
    """
    if not documents:
        return ""
    
    # Limit documents if max_examples specified
    docs_to_process = documents[:max_examples] if max_examples else documents
    
    examples_parts = []
    
    for i, doc in enumerate(docs_to_process):
        example_num = number_from + i
        query = doc.get("text", "").strip()
        sql = doc.get("sql", "")
        parameters = doc.get("parameters", "{}")
        metadata = doc.get("metadata", {})
        
        # Skip if no query text
        if not query:
            continue
        
        # Get optional fields from metadata
        title = metadata.get("title") or metadata.get("category", "Retrieved Example")
        analysis = metadata.get("analysis", "") if include_analysis else ""
        
        # Process parameters
        params_str = _escape_and_format_parameters(parameters)
        
        # Escape braces in SQL for .format() compatibility
        if sql:
            sql_escaped = sql.replace("{", "{{").replace("}", "}}")
            json_output = f'{{"SQL": "{sql_escaped}", "parameters": {params_str}}}'
        else:
            json_output = '{{"SQL": null, "parameters": {{}}}}'
        
        # Build the example
        example_lines = [f"Example {example_num} - {title}:", f"Query: {query}"]
        
        if analysis:
            example_lines.append(f"Analysis: {analysis}")
        
        example_lines.append(json_output)
        
        examples_parts.append("\n".join(example_lines))
    
    return "\n\n".join(examples_parts)


def convert_sql_parameters(sql_query):
    """
    Convert SQL parameter placeholders from $ format to @ format.
    All numbers in parameters get an underscore prefix (e.g., $1 -> @_1, @2 -> @_2).
    
    Args:
        sql_query (str): SQL query with $ parameters (e.g., $param, $1, $param_name)
        
    Returns:
        str: SQL query with @ parameters where numbers have underscore prefix
    """
    # First convert all $ to @
    # Pattern to match $ followed by parameter name (alphanumeric + underscore) or just numbers
    pattern = r'\$([a-zA-Z_][a-zA-Z0-9_]*|\d+)'
    sql_query = re.sub(pattern, r'@\1', sql_query)
    
    # Then add underscore before any numbers that follow @
    # This catches @1, @2, @3, etc. and converts them to @_1, @_2, @_3
    sql_query = re.sub(r'@(\d+)', r'@param\1', sql_query)
    
    return sql_query


@staticmethod
def _escape_and_format_parameters(parameters) -> str:
    """
    Convert parameters to escaped JSON string for prompt template.
    
    Args:
        parameters: Parameters as dict or JSON string
    
    Returns:
        Escaped JSON string safe for .format()
    """
    if isinstance(parameters, dict):
        params_dict = parameters
    elif isinstance(parameters, str):
        try:
            params_dict = json.loads(parameters) if parameters.strip() else {}
        except json.JSONDecodeError:
            params_dict = {}
    else:
        params_dict = {}
    
    # Convert to JSON and escape braces
    params_str = json.dumps(params_dict, ensure_ascii=False)
    return params_str.replace("{", "{{").replace("}", "}}")


def substitute_sql_parameters(json_input):
    """
    Substitutes parameters in a SQL query to create a non-parametric SQL query.
    
    Args:
        json_input (str or dict): JSON string or dictionary containing 'SQL' and 'parameters' keys
    
    Returns:
        str: SQL query with parameters substituted
    """
    
    # Parse JSON if it's a string
    if isinstance(json_input, str):
        data = json.loads(json_input)
    else:
        data = json_input
    
    sql_query = data['SQL']
    parameters = data['parameters']
    
    # Create a copy of the SQL query to modify
    result_sql = sql_query
    
    # Find all parameter placeholders in the SQL (format: :parameter_name)
    param_pattern = r':(\w+)'
    placeholders = re.findall(param_pattern, sql_query)
    
    # Replace each parameter placeholder with its value
    for param_name in placeholders:
        if param_name in parameters:
            param_value = parameters[param_name]
            placeholder = f':{param_name}'
            substituted_value = get_substituted_value(param_value)
            # Replace the placeholder with the actual value
            result_sql = result_sql.replace(placeholder, substituted_value)
    
    return result_sql


def json_text_cleaning(text, answer_key="query"):
    # Extract reasoning value
    reasoning_pattern = r'"reasoning"\s*:\s*"((?:[^"\\]|\\.)*)"'
    match_reasoning = re.search(reasoning_pattern, text, re.DOTALL)
    
    # If reasoning is not in quotes, try to match with a different pattern
    if not match_reasoning:
        reasoning_pattern = rf'"reasoning"\s*:\s*"?(.*?)"?\s*(?=,\s*"{answer_key}")'
        match_reasoning = re.search(reasoning_pattern, text, re.DOTALL)
    
    if match_reasoning:
        reasoning_value = match_reasoning.group(1)
        # Unescape any escaped quotes and preserve newlines
        reasoning_value = reasoning_value.replace('\\"', '"').replace('\\n', '\n')
        # Properly format numbered lists
        reasoning_value = re.sub(r'\n(\d+)[\.:]?\s*', r'\n\1. ', reasoning_value)
        # Replace asterisks used for bullet points with actual bullet points
        reasoning_value = re.sub(r'^\s*\*\s*', '• ', reasoning_value, flags=re.MULTILINE)
    else:
        reasoning_value = ""
    
    # Extract sql_query value
    answer_pattern = rf'"{answer_key}"\s*:\s*"((?:[^"\\]|\\.)*)"'
    match_answer = re.search(answer_pattern, text, re.DOTALL)
    
    # If sql_query is not in quotes, try to match with a different pattern
    if not match_answer:
        answer_pattern = rf'"{answer_key}"\s*:\s*"?(.*?)"?\s*(?=\s*[,}}]*)'
        match_answer = re.search(answer_pattern, text, re.DOTALL)
    
    if match_answer:
        answer_value = match_answer.group(1)
        # Unescape any escaped quotes and preserve newlines
        answer_value = answer_value.replace('\\"', '"').replace('\\n', '\n')
    else:
        answer_value = ""
    
    # Create the output dictionary with both keys
    json_output = {
        "reasoning": str(reasoning_value),
        answer_key: str(answer_value)
    }
    
    return json_output

def integrate_params(sql_query, params):
    # Parse the JSON parameters
    
    # Replace each parameter in the query
    result = sql_query
    for key, value in params.items():
        placeholder = f"@{key}"
        if placeholder in result:
            # Add quotes around string values
            result = result.replace(placeholder, f"'{value}'")
    
    return result


def add_param_keys(dictionary):
    """
    Add an underscore prefix to all keys in a dictionary.
    
    Args:
        dictionary (dict): Input dictionary
        
    Returns:
        dict: New dictionary with underscore-prefixed keys
    """
    return {f"param{key}": value for key, value in dictionary.items()}


def reconstruct_example_dict(doc: Document) -> Dict[str, Any]:
    """
    Reconstruct the original example structure from a retrieved document.
    
    Useful when you need the structured data rather than formatted text.
    
    Args:
        doc: Retrieved Document from vector search
        
    Returns:
        Dictionary with question, sql, parameters, and metadata
    """
    try:
        parameters = json.loads(doc.metadata.get("parameters", "{}"))
    except json.JSONDecodeError:
        parameters = {}
    
    return {
        "question": doc.page_content,
        "sql": {
            "SQL": doc.metadata.get("sql", ""),
            "parameters": parameters
        },
        "complexity": doc.metadata.get("complexity", ""),
        "domain": doc.metadata.get("domain", ""),
        "table": doc.metadata.get("table", "")
    }

# def json_text_cleaning(text, key="answer"):
#     if key == "answer":
#         # match_answer = re.search(rf'"{key}"\s*:\s*"((?:[^"\\]|\\.)*)"\s*(?:,|}})', text, re.DOTALL)

#         # Adjusted regex to allow for a single closing brace '}'
#         match_answer = re.search(rf'"reasoning"\s*:\s*(.*?)(?=,\s*"(?:{key}|[^"]+)"\s*:|}}$)', text, re.DOTALL)        
        
#     elif key == "sql_query":
#         match_answer = re.search(rf'"reasoning"\s*:\s*(.*?)(?=,\s*"(?:{key}|[^"]+)"\s*:|}}$)', text, re.DOTALL)

#     if match_answer:
#         answer_value = match_answer.group(1)
#         answer_value = answer_value.strip('"')
#         # Unescape any escaped quotes and preserve newlines
#         answer_value = answer_value.replace('\\"', '"').replace('\\n', '\n')
#         # Properly format numbered lists while preserving newlines
#         answer_value = re.sub(r'(\n|^)(\d+)[\.:]?\s*', r'\1\2. ', answer_value)
#         # Replace asterisks used for bullet points with actual bullet points, preserving newlines
#         answer_value = re.sub(r'(\n|^)\s*\*\s*', r'\1• ', answer_value)
#         # Ensure there's a newline before each bullet point (except the first one)
#         answer_value = re.sub(r'([^\n])(\n• )', r'\1\n\n• ', answer_value)
#         # Remove any extra newlines
#         answer_value = re.sub(r'\n{3,}', '\n\n', answer_value)
#     else:
#         answer_value = ""
    
#     match_reasoning = re.search(r'"reasoning"\s*:\s*"((?:[^"\\]|\\.)*)"', text, re.DOTALL)
#     if match_reasoning:
#         reasoning_value = match_reasoning.group(1)
#         reasoning_value = reasoning_value.strip('"')
#         # Unescape any escaped quotes within the value
#         reasoning_value = reasoning_value.replace('\\"', '"').replace('\\n', '\n')
#         # Properly format numbered lists
#         reasoning_value = re.sub(r'\n(\d+)[\.:]?\s*', r'\n\1. ', reasoning_value)
#         # Replace asterisks used for bullet points with actual bullet points
#         reasoning_value = re.sub(r'^\s*\*\s*', '• ', reasoning_value, flags=re.MULTILINE)
#     else:
#         reasoning_value = ""
    
#     json_output = {key: str(answer_value), "reasoning": str(reasoning_value)}
#     return json_output

import re

def extract_answer(llm_output):
    """
    Extracts the content between <answer> and </answer> tags using regex.

    Args:
        llm_output: A string containing the LLM's output.

    Returns:
        The extracted answer string, or None if the tags are not found.
    """
    # The re.DOTALL flag makes '.' match newlines as well
    match = re.search(r'<answer>(.*?)</answer>', llm_output, re.DOTALL)
    
    if match:
        # group(1) returns the first captured group (the content inside the parentheses)
        return match.group(1).strip()
    else:
        return None


def json_cleaning_1(input_string):
    final_cleaned_response = input_string.replace(JSON_START_STR, "").replace("```", "").strip() #.replace("\n\n", "\n").strip()
    return final_cleaned_response

def json_cleaning(input_string):    
    cleaned_string = re.sub(r'<think>.*?</think>', '', input_string, flags=re.DOTALL)
    final_cleaned_response = cleaned_string.replace(JSON_START_STR, "").replace("```", "").strip() #.replace("\n\n", "\n").strip()
    final_cleaned = extract_answer(final_cleaned_response)
    if final_cleaned:
        final_cleaned_response = final_cleaned

    return final_cleaned_response

def remove_think_tags(text):
    start_tag = "<think>"
    end_tag = "</think>"
    
    # Find start and end indices
    start_idx = text.find(start_tag)
    end_idx = text.find(end_tag) + len(end_tag)
    
    # If both tags are found, remove the content between them including tags
    if start_idx != -1 and end_idx != -1:
        return text[:start_idx] + text[end_idx:]
    return text

def json_string_to_dict(json_str):
    """
    Convert a JSON-like string into a Python dictionary.
    
    Args:
        json_str (str): A string containing JSON-like content.
        
    Returns:
        dict: The parsed dictionary from the JSON string.
        
    Raises:
        ValueError: If the input is not a string, is empty, or is invalid JSON.
    """
    # Validate input
    if not isinstance(json_str, str):
        raise ValueError("Input must be a string")
    if not json_str.strip():
        raise ValueError("Input string cannot be empty")
    
    # Remove code block markers if present
    cleaned_str = json_str.strip()
    if cleaned_str.startswith(JSON_START_STR):
        cleaned_str = cleaned_str.replace(JSON_START_STR, "").replace("```", "").strip()
    
    try:
        # Parse JSON string into dictionary
        result = json.loads(cleaned_str)
        return result
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")

def has_video_link_(parameters: dict) -> bool:
    """Check if parameters contain any video link references (videolink-*)."""
    if not parameters:
        return False
    pattern = re.compile(r'videolink-\w+')
    return any(pattern.search(str(v)) for v in parameters.values())

def init_session_state():
    # Define all state variables and their default values
    defaults = {
        # Lists
        "message_id": [],
        "user_input_storage": [],
        "user_utterance": [],
        "response": [],
        "log": [],
        "urls": [],
        "query": [],
        "suggested_sessions": [],
        "suggested_modules": [],
        "sql_response_type": [],
        "ticket_response_type": [],   # <-- NEW
        "suggested_choices": [],

        # Strings
        "user_input": "",
        "response_is_valid": "",
        "temporary_response": "",
        "model_selector": "GPT",

        # Booleans (False by default)
        "have_clicked_on_feedback": False,
        "do_generate_sessions": False,
        "do_suggest_modules": False,
        "on_click": False,
        "on_click_user_input": False,
        "evaluate_sql": False,

        # Booleans (True by default)
        "first_encounter_with_searchbox": True,
        "first_encounter_with_extra_sessions": True,
        "sql_mode": True,
    }

    # Iterate through the defaults and initialize if not present
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value