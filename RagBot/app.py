import json 
import random
import re
import pathlib

import requests
import streamlit as st

from src.logs import simple_logger, non_generative_agent_logger
from src.utils import init_session_state
from src.config import config
from src.logic import feedback_
from src.retriever import Retriever


NUMBER_OF_SUGGESTED_SESSIONS = 30
RESPONSE_TEMPLATE_FOR_NO_ANSWER = """
    به سامانه سوال و جواب همکاران سیستم خوش آمدید. 
    سوال فعلی شما به همکاران سیستم مرتبط نیست. 
    لطفا سوالاتی را که به همکاران سیستم مرتبط هستند، بپرسید. 
    با تشکر
    """

CSS_STYLE_FILE = "./src/style.css"
BASE_URL = "http://185.13.230.222:8686" # "http://172.27.0.6:8686" #
# with open(CSS_STYLE_FILE) as f:
#     st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def session_create(api_url: str = BASE_URL): 
    """
    Sends a POST request to create a session and returns the session ID if successful.

    :param api_url: The URL for the session creation API endpoint.
    :return: The session ID if successful, None otherwise.
    """
    try:
        response = requests.post(f"{api_url}/session/create")
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response and extract the session_id
            data = response.json()
            session_id = data.get('session_id')
            print(f"Session ID: {session_id}")
            return session_id
        else:
            # Handle any other status codes
            return None

    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the request
        return None

def chat_request(session_id: str, query: str, api_url: str = BASE_URL):
    # Define the request data
    chat_data = {
        "query": query,
        "session_id": session_id,  # Assume this is generated or fetched from somewhere
    }

    # Send the POST request with the chat data
    # import pdb
    # pdb.set_trace()
    headers = {"Session-ID": session_id}
    response = requests.post(f"{api_url}/chat", json=chat_data, headers=headers) # , timeout=11

    # Handle the different response status codes
    json_response = response.json()
    if response.status_code == 200:
        return {"status": "success", "query": json_response["query"], "response": json_response["response"], "message_id": json_response["message_id"]}
    else:
        return {"status": "error", "query": "", "response": "", "message_id": ""}


def request_history(session_id, api_url: str = BASE_URL):
    payload = {
        "page_index": 1,
        "page_size": 30,
        "session_id": session_id,
        "contain_paraphrase": True
        }
    response = requests.get(f"{api_url}/chat", params=payload)
    json_response = response.json()
    if response.status_code == 200: 
        return {"status": "sucess", "history": json_response['history']}
    else:
        return {"status": "error", "history": ""}
    

def request_previous_sessions(api_url: str = BASE_URL):
    response = requests.get(f"{api_url}/sessions")
    json_response = response.json()
    if response.status_code == 200: 
        return {"status": "sucess", "response": json_response['response']}
    else:
        return {"status": "error", "response": ""}
    

def send_feedback(message_id: str, feedback_type: str, session_id: str, api_url: str = BASE_URL):
    # Define the request data
    feedback_data = {
        "message_id": message_id,
        "feedback_type": feedback_type,
        "session_id": session_id
    }

    # Send the POST request with the feedback data
    response = requests.post(f"{api_url}/feedback", json=feedback_data, headers={"Session-ID": session_id})


def clear_logs():
    st.session_state["log"] = []


def clear_text():
    st.session_state["user_input"] = st.session_state["temporal_user_input"]
    st.session_state["temporal_user_input"] = ""


def encounter_with_chatbox():
    if not st.session_state["query"]:
        st.session_state["first_encounter_with_chatbox"] = True


def feedback_button_clicked():
    return (
        st.session_state.get("like", False)
        or st.session_state.get("dislike", False)
        or st.session_state.get("flag", False)
    )


def main():
    st.set_page_config(
        page_title="hamzan",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    init_session_state()

    clicked_on_sidebar_sessions = False
    for i in range(NUMBER_OF_SUGGESTED_SESSIONS):
        if st.session_state.get(f"session_button_{i}"):
            clicked_on_sidebar_sessions = True
            session_id_clicked = st.session_state.get(f"session_{i}")
            st.session_state["session_id"] = session_id_clicked
            history = request_history(session_id_clicked, BASE_URL)
            if history["history"]:
                st.session_state["first_encounter_with_searchbox"] = False
            else:
                st.session_state["first_encounter_with_searchbox"] = True

    if "session_id" not in st.session_state:
        session_id = session_create()
        st.session_state["session_id"] = session_id
    number_of_columns = [3, 4, 1, 5, 3]
    _, sessions_column, logging_column, main_column, _ = st.columns(
        number_of_columns,
        gap="small",
    )

    with open(CSS_STYLE_FILE) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    with st.sidebar:
        st.checkbox("Show Logs", key="enable_show_logs")
        st.button("Clear Logs", key="clear_logs_button")
        st.divider()

    if st.session_state.get("clear_logs_button", False):
        clear_logs()
        

    with main_column:
        if st.session_state["first_encounter_with_searchbox"]:
            st.info(
                "سلام، من سامانه دستیار دیجیتال نسل چهارم همکاران سیستم هستم. لطفا سوالتون رو در کادر زیر بپرسید.",
            )    
            st.session_state["first_encounter_with_searchbox"] = False
                        
        st.text_input(
            st.session_state.get("session_id"),
            placeholder="هر چه می‌خواهد دل تنگت بپرس!",
            key="temporal_user_input",
            on_change=clear_text,
        )
        progress_bar = st.progress(value=0)
        with st.container():
            if st.session_state.get("user_input"):
                user_input = st.session_state["user_input"]
                st.session_state.user_utterance.append(user_input)
                simple_logger(
                    f"user said: {user_input}",
                    session_id=st.session_state.get("session_id"),
                )
                chat_response = chat_request(
                    st.session_state.get("session_id"), user_input, 
                )
                message_id, response, query = (
                    chat_response["message_id"],
                    chat_response["response"],
                    chat_response["query"],
                )
                if chat_response["status"] == config["chat_responder"]["ok_status"]:
                    response_is_valid = True
                    
                progress_bar.progress(value=100, text="Done.")
                st.session_state.query.append(query)
                st.session_state.response.append(response)
                st.session_state.user_input_storage.append(user_input)
                st.session_state["user_input"] = ""
                st.session_state["have_clicked_on_feedback"] = False
                st.session_state["response_is_valid"] = response_is_valid
                st.session_state["message_id"].append(message_id)
                
            elif clicked_on_sidebar_sessions:
                session_id = st.session_state.get("session_id")
                st.session_state.user_utterance = [message["query"] for message in history['history'] if history["history"]]
                st.session_state.query = [message["paraphrased_query"] for message in history['history'] if history["history"]]
                progress_bar.progress(value=100, text="Done.")
                st.session_state.response = [message["response"] for message in history['history'] if history["history"]]
                st.session_state.user_input_storage = [message["query"] for message in history['history'] if history["history"]]
                st.session_state.message_id = [message["message_id"] for message in history['history'] if history["history"]]
                st.session_state["have_clicked_on_feedback"] = False
                st.session_state["response_is_valid"] = True
                progress_bar.progress(value=0)


            if st.session_state.get("response") and st.session_state.get(
                "user_utterance",
            ):
                for i in reversed(range(len(st.session_state["response"]))):
                    with st.chat_message("user"):
                        st.markdown(
                            st.session_state["user_utterance"][i],
                            unsafe_allow_html=True,
                        )
                    with st.chat_message("assistant"):
                        help_msg = f"""برای پاسخ به سوال شما کوئری «{st.session_state['query'][i]}» \
                        جستجو شده است."""
                        content = (
                            st.session_state["response"][i]
                            # .replace("*", "&ast;")
                            # .replace("#", "&#35;")
                        )
                        st.markdown(
                            re.sub(
                                r"(\*([0-9]|&ast;|&#35;)*[0-9]+.{0,10}&#35;"
                                r"|&#35;([0-9]|&ast;|&#35;)\*[0-9]+.{0,10}\*)",
                                r'<span class="ussd-code" dir="ltr">\1</span>',
                                content,
                            ),
                            unsafe_allow_html=True,
                            help=help_msg
                        )
                        response_is_valid = st.session_state.get(
                            "response_is_valid",
                            False,
                        )
                        if (
                            i == len(st.session_state["response"]) - 1
                            and response_is_valid
                        ):
                            feedback_column_placeholder = st.empty()
                            if feedback_button_clicked():
                                st.session_state["have_clicked_on_feedback"] = True
                                user_utterance = st.session_state.get(
                                    "user_input_storage",
                                )[i]
                                paraphrased_query = st.session_state.get("query")[i]
                                message_id = st.session_state["message_id"][-1]
                                response = st.session_state.get("response")[i]
                                # TODO: has bug when you click on a suggested question and then on thumbup/down buttons
                                like = st.session_state.get("like", False)
                                dislike = st.session_state.get("dislike", False)
                                flag = st.session_state.get("flag", False)
                                if like:
                                    send_feedback(
                                        message_id,
                                        "thumb_up",
                                        st.session_state.get("session_id"),
                                    )
                                elif dislike:
                                    send_feedback(
                                        message_id,
                                        "thumb_down",
                                        st.session_state.get("session_id"),
                                    )
                                elif flag:
                                    # todo flag is not included in the redis yet!
                                    send_feedback(
                                        message_id,
                                        "flag",
                                        st.session_state.get("session_id")
                                    )
                                    # feedback(paraphrased_query, response, url, "flag")
                                non_generative_agent_logger(
                                    session_id=st.session_state.get("session_id"),
                                    agent="user feedback",
                                    message="user is clicked on feedback button",
                                    input_dict={
                                        "user_utterance": user_utterance,
                                        "response": response,
                                    },
                                    output_dict={
                                        "like": like,
                                        "dislike": dislike,
                                        "flag": flag,
                                    },
                                    elapsed_time=-1,
                                )  # TODO: The elapsed time is not correct, but I didn't have any other option
                            if st.session_state["have_clicked_on_feedback"]:
                                *_, text_col = feedback_column_placeholder.columns(
                                    [1, 1, 1, 5],
                                    gap="medium",
                                )
                                with text_col:
                                    st.markdown("نظر شما ثبت شد.")
                            else:
                                (
                                    thumb_up_col,
                                    report_col,
                                    thumb_down_col,
                                    text_col,
                                ) = feedback_column_placeholder.columns(
                                    [2, 2, 2, 2],
                                    gap="medium",
                                )
                                with thumb_up_col:
                                    st.button(
                                        ":+1:",
                                        key="like",
                                        use_container_width=True,
                                        help="جواب به حل مشکل من کمک کرد",
                                    )
                                with report_col:
                                    st.button(
                                        ":triangular_flag_on_post:",
                                        key="flag",
                                        use_container_width=True,
                                        help="این جواب از قوانین تبعیت نمی‌کند",
                                    )
                                with thumb_down_col:
                                    st.button(
                                        ":-1:",
                                        key="dislike",
                                        use_container_width=True,
                                        help="جواب به حل مشکل من کمک نکرد",
                                    )
                                with text_col:
                                    st.markdown("نظرت؟")
                                    
        with sessions_column:
            if st.session_state["first_encounter_with_extra_sessions"]:
                st.success(
                    "این جا هم یه سری از جلسات قبلی شما هست که میتونید ازشون استفاده کنید.",
                )
                sessions = request_previous_sessions()['response']
                for i, session in enumerate(sessions):
                    st.button(session, key=f"session_button_{i}")
                    st.session_state[f"session_{i}"] = session
                st.session_state["suggested_sessions"] = sessions
                st.session_state["first_encounter_with_extra_sessions"] = False
            else: 
                sessions = st.session_state["suggested_sessions"]
                for i, session in (enumerate(sessions)):
                    st.button(session, key=f"session_button_{i}")
                    st.session_state[f"session_{i}"] = session


    with logging_column:
        if st.session_state["enable_show_logs"]:
            for log in st.session_state["log"]:
                title = log["title"]
                description = log["description"]
                with st.expander(title):
                    st.write(description)


if __name__ == "__main__":
    # st.markdown(HTML_STYLE_FOR_RTL_INPUT_ELEMENT, unsafe_allow_html=True)

    main()
