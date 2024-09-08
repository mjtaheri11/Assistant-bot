import json
import logging
import logging.handlers
import uuid

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
def json_cleaning(input_string):
    cleaned_string = input_string.replace("json", "").replace("```", "")
    return cleaned_string

def init_session_state():
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = uuid.uuid4().hex
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