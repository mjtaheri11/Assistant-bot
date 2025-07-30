import json
import logging
import logging.handlers
import re
import uuid
from json.decoder import JSONDecodeError

import streamlit as st
import yaml
from pythonjsonlogger import jsonlogger


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
    input_string.replace("\n", "").strip()
    json_input = json.loads(input_string)
    return json_input["user_standalone_input"]

def json_cleaning(input_string):    
    cleaned_string = re.sub(r'<think>.*?</think>', '', input_string, flags=re.DOTALL)
    # cleaned_string = re.sub(r'\n+', '\n', cleaned_string)
    final_cleaned_response = cleaned_string.replace("sql", "").replace("```", "").strip() #.replace("\n\n", "\n").strip()
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
    if cleaned_str.startswith("```json"):
        cleaned_str = cleaned_str.replace("```json", "").replace("```", "").strip()
    
    try:
        # Parse JSON string into dictionary
        result = json.loads(cleaned_str)
        return result
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")
    
    
def init_session_state():
    if "message_id" not in st.session_state:
        st.session_state["message_id"] = []
    if "user_input" not in st.session_state:
        st.session_state["user_input"] = ""
    if "user_input_storage" not in st.session_state:
        st.session_state["user_input_storage"] = []
    if "user_utterance" not in st.session_state:
        st.session_state["user_utterance"] = []
    if "response" not in st.session_state:
        st.session_state["response"] = []
    if "log" not in st.session_state:
        st.session_state["log"] = []
    if "urls" not in st.session_state:
        st.session_state["urls"] = []
    if "query" not in st.session_state:
        st.session_state["query"] = []
    if "suggested_sessions" not in st.session_state:
        st.session_state["suggested_sessions"] = []
    if "have_clicked_on_feedback" not in st.session_state:
        st.session_state["have_clicked_on_feedback"] = False
    if "first_encounter_with_searchbox" not in st.session_state:
        st.session_state["first_encounter_with_searchbox"] = True
    if "first_encounter_with_extra_sessions" not in st.session_state:
        st.session_state["first_encounter_with_extra_sessions"] = True
    if "do_generate_sessions" not in st.session_state:
        st.session_state["do_generate_sessions"] = False
    if "response_is_valid" not in st.session_state:
        st.session_state["response_is_valid"] = ""
    if "do_suggest_modules" not in st.session_state:
        st.session_state["do_suggest_modules"] = False
    if "on_click" not in st.session_state:
        st.session_state["on_click"] = False
    if "suggested_modules" not in st.session_state:
        st.session_state["suggested_modules"] = []
    if "on_click_user_input" not in st.session_state:
        st.session_state["on_click_user_input"] = False
    if "sql_response_type" not in st.session_state: # TODO only for MAY demo. => should be removed 
        st.session_state["sql_response_type"] = []
    if "temporary_response" not in st.session_state:
        st.session_state["temporary_response"] = ""
    if "suggested_choices" not in st.session_state:
        st.session_state["suggested_choices"] = []
    if "sql_mode" not in st.session_state:
        st.session_state["sql_mode"] = True
