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

def json_text_cleaning(text, key="answer"):
    # import pdb
    # pdb.set_trace()
    if key == "answer":
        match_answer = re.search(rf'"{key}"\s*:\s*"((?:[^"\\]|\\.)*)"\s*(?:,|}})', text, re.DOTALL)
        
    elif key == "rephrased_query":
        match_answer = re.search(rf'"{key}"\s*:\s*(.*?)(?=,\s*"(?:reasoning|[^"]+)"\s*:|}}$)', text, re.DOTALL)
    # import pdb
    # pdb.set_trace()
    match_reasoning = re.search(r'"reasoning"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,', text, re.DOTALL)
    if match_answer:
        answer_value = match_answer.group(1)
        answer_value = answer_value.strip('"')
        # Unescape any escaped quotes within the value
        answer_value = answer_value.replace('\\"', '"')
    else:
        answer_value = ""
    
    if match_reasoning:
        reasoning_value = match_reasoning.group(1)
        reasoning_value = answer_value.strip('"')
        # Unescape any escaped quotes within the value
        reasoning_value = answer_value.replace('\\"', '"')
    else:
        reasoning_value = ""
    
    json_output = {key: str(answer_value), "reasoning": str(reasoning_value)}
    return json_output


def json_cleaning(input_string, key):    
    cleaned_string = input_string.replace("json", "").replace("```", "").replace("\n\n", "\n").strip()
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
    if "log" not in st.session_state:
        st.session_state["log"] = []
    if "urls" not in st.session_state:
        st.session_state["urls"] = []
    if "query" not in st.session_state:
        st.session_state["query"] = []
    if "suggested_questions" not in st.session_state:
        st.session_state["suggested_questions"] = []
    if "context_reference_url" not in st.session_state:
        st.session_state["context_reference_url"] = ""
    if "context" not in st.session_state:
        st.session_state["context"] = ""
    if "have_suggested_questions" not in st.session_state:
        st.session_state["have_suggested_questions"] = False
    if "have_clicked_on_feedback" not in st.session_state:
        st.session_state["have_clicked_on_feedback"] = False
    if "first_encounter_with_searchbox" not in st.session_state:
        st.session_state["first_encounter_with_searchbox"] = True
    if "first_encounter_with_extra_questions" not in st.session_state:
        st.session_state["first_encounter_with_extra_questions"] = True
    if "do_generate_questions" not in st.session_state:
        st.session_state["do_generate_questions"] = False
    # if "enable_show_logs" not in st.session_state:
    #     st.session_state["enable_show_logs"] = False
    if "response_is_valid" not in st.session_state:
        st.session_state["response_is_valid"] = ""
