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