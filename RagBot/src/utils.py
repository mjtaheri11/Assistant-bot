import json
import logging
import logging.handlers
import uuid
import re
from json.decoder import JSONDecodeError

import streamlit as st
import yaml
from pythonjsonlogger import jsonlogger

# def init_logger():
#     logger = logging.getLogger(__name__)
#     log_file = config_["logging"]["file"]
#     log_format = "%(asctime)s - %(levelname)s - %(message)s"
#     file_handler = logging.handlers.RotatingFileHandler(
#         log_file, maxBytes=100 * 1024 * 1024, backupCount=2, encoding="utf-8"
#     )
#     formatter = jsonlogger.JsonFormatter(log_format, timestamp=True)
#     file_handler.setFormatter(formatter)
#     logger.addHandler(file_handler)
#     logger.setLevel(logging.DEBUG)

#     return logger

def json_text_cleaning(text, key="explanation"):
    if key == "explanation":
        # match_answer = re.search(rf'"{key}"\s*:\s*"((?:[^"\\]|\\.)*)"\s*(?:,|}})', text, re.DOTALL)

        # Adjusted regex to allow for a single closing brace '}'
        match_answer = re.search(rf'"{key}"\s*:\s*(.*?)(?=,\s*"(?:appropriateness|[^"]+)"\s*:|}}$)', text, re.DOTALL)
        
        
    if match_answer:
        answer_value = match_answer.group(1)
        answer_value = answer_value.strip('"')
        # Unescape any escaped quotes and preserve newlines
        answer_value = answer_value.replace('\\"', '"').replace('\\n', '\n')
        # Properly format numbered lists while preserving newlines
        answer_value = re.sub(r'(\n|^)(\d+)[\.:]?\s*', r'\1\2. ', answer_value)
        # Replace asterisks used for bullet points with actual bullet points, preserving newlines
        answer_value = re.sub(r'(\n|^)\s*\*\s*', r'\1• ', answer_value)
        # Ensure there's a newline before each bullet point (except the first one)
        answer_value = re.sub(r'([^\n])(\n• )', r'\1\n\n• ', answer_value)
        # Remove any extra newlines
        answer_value = re.sub(r'\n{3,}', '\n\n', answer_value)
    else:
        answer_value = ""
    
    match_reasoning = re.search(r'"appropriateness"\s*:\s*"((?:[^"\\]|\\.)*)"', text, re.DOTALL)
    if match_reasoning:
        reasoning_value = match_reasoning.group(1)
        reasoning_value = reasoning_value.strip('"')
        # Unescape any escaped quotes within the value
        reasoning_value = reasoning_value.replace('\\"', '"').replace('\\n', '\n')
        # Properly format numbered lists
        reasoning_value = re.sub(r'\n(\d+)[\.:]?\s*', r'\n\1. ', reasoning_value)
        # Replace asterisks used for bullet points with actual bullet points
        reasoning_value = re.sub(r'^\s*\*\s*', '• ', reasoning_value, flags=re.MULTILINE)
    else:
        reasoning_value = ""
    
    json_output = {key: str(answer_value), "appropriateness": str(reasoning_value)}
    return json_output


def json_cleaning(input_string):    
    cleaned_string = input_string.replace("json", "").replace("```", "").strip() #.replace("\n\n", "\n").strip()
    # cleaned_string = re.sub(r'\n+', '\n', cleaned_string)
    return cleaned_string


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
    if "create_database" not in st.session_state:
        st.session_state["database"] = []
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
    if "databases" not in st.session_state:
        st.session_state["databases"] = []
    if "database_id" not in st.session_state:
        st.session_state["database_id"] = None
    if "enable_submit_form" not in st.session_state:
        st.session_state["enable_submit_form"] = False
    if "form_submitted" not in st.session_state: 
        st.session_state["form_submitted"] = False
    if "answer_type" not in st.session_state:
        st.session_state["answer_type"] = ""
    if "does_evaluate" not in st.session_state:
        st.session_state["does_evaluate"] = ""
    if "use_cache" not in st.session_state:
        st.session_state["use_cache"] = False

