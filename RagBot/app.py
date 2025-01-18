import json
import pathlib
import random
import re
from io import StringIO

import requests
import streamlit as st
from src.config import config
from src.logic import feedback_
from src.logs import non_generative_agent_logger, simple_logger
from src.utils import init_session_state

NUMBER_OF_SUGGESTED_SESSIONS = 30

CSS_STYLE_FILE = "./src/style.css"

BASE_URL = "http://185.13.230.222:8686" # "http://172.27.0.6:8686" #


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
            # Parse the JSON response and extract the 
            data = response.json()
            session_id = data.get("session_id")
            print(f"Session ID: {session_id}")
            return session_id
        else:
            # Handle any other status codes
            return None

    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the request
        return None


def chat_request(session_id: str, query: str, database_id: str = None, answer_type: str = "concise", does_evaluate: str = False, use_cache: bool = True, api_url: str = BASE_URL):

    # Define the request data
    if database_id:
        chat_data = {
            "query": query,
            "session_id": session_id,  # Assume this is generated or fetched from somewhere
            "database_index": database_id,
            "answer_type": answer_type,
            "does_evaluate": does_evaluate,
            "use_cache": use_cache
        }
    else:
        chat_data = {
            "query": query,
            "session_id": session_id,  # Assume this is generated or fetched from somewhere
        }
        
    headers = {"Session-ID": session_id}
    response = requests.post(
        f"{api_url}/chat", json=chat_data, headers=headers
    )  # , timeout=11

    # Handle the different response status codes
    json_response = response.json()
    if response.status_code == 200:
        return {
            "status": "success",
            "query": json_response["query"],
            "response": json_response["response"],
            "message_id": json_response["message_id"],
        }
    else:
        return {"status": "error", "query": "", "response": "", "message_id": ""}


def request_history(session_id, api_url: str = BASE_URL):
    payload = {
        "page_index": 1,
        "page_size": 30,
        "session_id": session_id,
        "contain_paraphrase": True,
    }
    response = requests.get(f"{api_url}/chat", params=payload)
    json_response = response.json()
    if response.status_code == 200:
        return {"status": "sucess", "history": json_response["history"]}
    else:
        return {"status": "error", "history": ""}


def request_previous_sessions(api_url: str = BASE_URL):
    response = requests.get(f"{api_url}/sessions")
    json_response = response.json()
    if response.status_code == 200:
        paraphrased_query = []
        sessions = []
        for response in json_response["response"]:
            sessions.append(response["session_id"])
            paraphrased_query.append(response["paraphrased_query"])
        return {
            "status": "sucess",
            "paraphrased_queries": paraphrased_query,
            "sessions": sessions,
        }
    else:
        raise Exception
        # return {"status": "error", "response": ""}


def send_feedback(
    message_id: str, feedback_type: str, session_id: str, api_url: str = BASE_URL
):
    # Define the request data
    feedback_data = {
        "message_id": message_id,
        "feedback_type": feedback_type,
        "session_id": session_id,
    }

    # Send the POST request with the feedback data
    response = requests.post(
        f"{api_url}/feedback", json=feedback_data, headers={"Session-ID": session_id}
    )
    json_response = response.json()
    if response.status_code == 200:
        return json_response
    else:
        return {"message": "error"}


def create_database_api_request(
    company_name, assistant_name, uploaded_files
):
    params = {
        "company_name": company_name,
        "assistant_name": assistant_name

    }
    files = [('files', (file.name, file)) for file in uploaded_files]

    try:
        response = requests.post(
            f"{BASE_URL}/chat/create/database", params=params, files=files
        )
        response.raise_for_status()
        return ("success", "Database created successfully!", response.json())
    except requests.exceptions.HTTPError as http_err:
        return ("error", f"HTTP error occurred: {http_err}", None)
    except Exception as err:
        return ("error", f"An error occurred: {err}", None)

def form_submit_button():
    st.session_state["form_submitted"] = True

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

def find_answer_type(type_: str):
    if type_.strip() == "خلاصه":
        return "concise"
    if type_.strip() == "توضیحی":
        return "explanatory"
    if type_.strip() == "عادی":
        return "normal"    
        

def boolean_mapper(type_):
    if type_.strip() == "بله":
        return True
    elif type_.strip() == "خیر":
        return False


def main():
    st.set_page_config(
        page_title="hamzan",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    init_session_state()
    clicked_on_sidebar_sessions = False
    clicked_on_new_session = False
    clicked_on_create_database = False
    form_submitted = False
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

    if st.session_state.get("new_session"):
        st.session_state["first_encounter_with_searchbox"] = True
        st.session_state["session_id"] = session_create()

    if st.session_state.get("create_database"):
        st.session_state["enable_submit_form"] = True
        clicked_on_new_session = True

    if "session_id" not in st.session_state:
        session_id = session_create()
        st.session_state["session_id"] = session_id
    
    if st.session_state["form_submitted"]:
        form_submitted = True

    number_of_columns = [2, 3, 1, 5, 4]
    _, sessions_column, logging_column, main_column, _ = st.columns(
        number_of_columns,
        gap="small",
    )

    with open(CSS_STYLE_FILE) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    with st.sidebar:
        # st.checkbox("Show Logs", key="enable_show_logs")
        st.markdown("در این قسمت هم میتوانید دستیار سفارشی خود را سفارش دهید")
        st.button("سفارش دستیار سفارشی", key="create_database")
        st.divider()

    if st.session_state.get("clear_logs_button", False):
        clear_logs()

    with main_column: 
        if st.session_state["form_submitted"]:
            if st.session_state["uploaded_files"] is None or len(st.session_state["uploaded_files"]) == 0:
                st.error("Please upload at least one file.")
            else:
                # Show a spinner while processing
                with st.spinner("در حال ساخت پایگاه داده هستم ..."):
                    # Make the POST request
                    status, message, data = create_database_api_request(
                        st.session_state["temporal_company_name"],
                        st.session_state["temporal_assistant_name"],
                        st.session_state["uploaded_files"],
                    )
                    if status == "success":
                        st.session_state["does_evaluate"] = boolean_mapper(st.session_state.get("temporal_does_evaluate"))
                        st.session_state["answer_type"] = find_answer_type(st.session_state.get("temporal_answer_type"))
                        st.session_state["use_cache"] = boolean_mapper(st.session_state["temporal_use_cache"])
                        st.session_state["database_id"] = data["database_id"] 
                        st.info(f"سلام، من سامانه {st.session_state['temporal_assistant_name'].strip()} {st.session_state['temporal_company_name'].strip()} هستم. لطفا سوالتون رو در کادر زیر بپرسید.")
                        st.session_state["enable_submit_form"] = False
                        st.session_state["form_submitted"] = False
                    else:
                        st.error(message)
        
        if st.session_state["enable_submit_form"]:
            with st.form(key="create_database_form"):
                st.info(
                    " با استفاده از این سامانه میتواند فایل های خود را آپلود کرده و دستیار شخصی سازی شده خود را تحویل بگیرید.",
                )
                uploaded_files = st.file_uploader(
                    "لطفا داکیومنت های مربوط به شرکت یا سازمان خود را با فرمت های مشخص شده وارد کنید.",
                    type=["docx", "doc"],
                    accept_multiple_files=True,
                    key="uploaded_files",
                    help=None,
                    on_change=None,
                    disabled=False,
                    label_visibility="hidden",
                )
                
                st.markdown("نام دستیار خود را وارد کنید")
                st.text_input(
                    "نام دستیار خود را وارد کنید",
                    placeholder="نام دستیار خود را وارد کنید",
                    key="temporal_assistant_name",
                    label_visibility="collapsed",
                )
                st.markdown("نام شرکت خود را وارد کنید")
                st.text_input(
                    "نام شرکت خود را وارد کنید",
                    placeholder="نام شرکت خود را وارد کنید",
                    key="temporal_company_name",
                    label_visibility="collapsed",
                )
                # st.markdown("مقدار تقسیم بندی داکیومنت")
                # st.number_input(
                #     "مقدار تقسیم بندی داکیومنت",
                #     placeholder="کمترین میزان تقسیم بندی سند",
                #     key="temporal_chunk_size",
                #     step=10,
                #     value=1000,
                #     min_value=500,
                #     max_value=2500,
                #     label_visibility="collapsed",
                # )
                # st.markdown("بیشترین مقدار تقسیم بندی سند")
                # st.number_input(
                #     "بیشترین مقدار تقسیم بندی داکیومنت",
                #     placeholder="بیشترین میزان تقسیم بندی داکیومنت خود را وارد کنید",
                #     key="temporal_max_chunk_size",
                #     step=10,
                #     value=2000,
                #     min_value=500,
                #     max_value=2000,
                #     label_visibility="collapsed",
                # )
                st.markdown("نحوه پاسخ گویی به سوالات کاربر را وارد کنید")
                st.selectbox(
                    "نحوه پاسخ گویی به سوالات کاربر را وارد کنید",
                    ["توضیحی", "عادی", "خلاصه"],
                    key="temporal_answer_type",
                    label_visibility="collapsed"
                )
                st.markdown("ارزیابی برخط بر روی پاسخ خروجی")
                st.selectbox(
                    "ارزیابی برخط بر روی پاسخ خروجی",
                    ["خیر", "بله"],
                    key="temporal_does_evaluate",
                    label_visibility="collapsed"
                )
                st.markdown("استفاده از کش سیستم (دستیار دیجیتال نسل 4)")
                st.selectbox(
                    "استفاده از کش سیستم (دستیار دیجیتال نسل 4)",
                    ["خیر", "بله"],
                    key="temporal_use_cache",
                    label_visibility="collapsed"
                )
                st.form_submit_button("ارسال", on_click=form_submit_button, type="primary")
  
        else:
            if st.session_state["first_encounter_with_searchbox"]:
                st.info(
                    "سلام، من سامانه دستیار دیجیتال نسل چهارم همکاران سیستم هستم. لطفا سوالتون رو در کادر زیر بپرسید",

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
                    database_id = st.session_state["database_id"]
                    st.session_state.user_utterance.append(user_input)
                    simple_logger(
                        f"user said: {user_input}",
                        session_id=st.session_state.get("session_id"),
                    )
                    chat_response = chat_request(
                        st.session_state.get("session_id"),
                        user_input,
                        database_id,
                        st.session_state["answer_type"],
                        st.session_state["does_evaluate"],
                        st.session_state["use_cache"]
                    )
                    message_id, response, query = (
                        chat_response["message_id"],
                        chat_response["response"],
                        chat_response["query"],
                    )
                    if chat_response["status"] == config["chat_responder"]["ok_status"]:
                        response_is_valid = True

                    progress_bar.progress(value=100, text="Done")
                    st.session_state.query.append(query)
                    st.session_state.response.append(response)
                    st.session_state.user_input_storage.append(user_input)
                    st.session_state["user_input"] = ""
                    st.session_state["have_clicked_on_feedback"] = False
                    st.session_state["response_is_valid"] = response_is_valid
                    st.session_state["message_id"].append(message_id)

                elif clicked_on_sidebar_sessions:
                    session_id = st.session_state.get("session_id")
                    st.session_state.user_utterance = [
                        message["query"]
                        for message in history["history"]
                        if history["history"]
                    ]
                    st.session_state.query = [
                        message["paraphrased_query"]
                        for message in history["history"]
                        if history["history"]
                    ]
                    progress_bar.progress(value=100, text="Done.")
                    st.session_state.response = [
                        message["response"]
                        for message in history["history"]
                        if history["history"]
                    ]
                    st.session_state.user_input_storage = [
                        message["query"]
                        for message in history["history"]
                        if history["history"]
                    ]
                    st.session_state.message_id = [
                        message["message_id"]
                        for message in history["history"]
                        if history["history"]
                    ]
                    st.session_state["have_clicked_on_feedback"] = False
                    st.session_state["response_is_valid"] = True
                    progress_bar.progress(value=0)

                elif clicked_on_new_session:
                    st.session_state.user_utterance = []
                    st.session_state.query = []
                    st.session_state.response = []
                    st.session_state.user_input_storage = []
                    st.session_state.message_id = []
                    st.session_state.have_clicked_on_feedback = False
                    st.session_state.response_is_valid = False
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
                                help=help_msg,
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
                                        result = send_feedback(
                                            message_id,
                                            "thumb_up",
                                            st.session_state.get("session_id"),
                                        )
                                    elif dislike:
                                        result = send_feedback(
                                            message_id,
                                            "thumb_down",
                                            st.session_state.get("session_id"),
                                        )
                                    elif flag:
                                        # todo flag is not included in the redis yet!
                                        result = send_feedback(
                                            message_id,
                                            "flag",
                                            st.session_state.get("session_id"),
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
                                    if result["message"] == "Feedback received":
                                        *_, text_col = (
                                            feedback_column_placeholder.columns(
                                                [1, 1, 1, 5],
                                                gap="medium",
                                            )
                                        )
                                        with text_col:
                                            st.markdown("نظر شما ثبت شد.")
                                    else:
                                        *_, text_col = (
                                            feedback_column_placeholder.columns(
                                                [1, 1, 1, 5],
                                                gap="medium",
                                            )
                                        )
                                        with text_col:
                                            st.markdown("نظر شما قبلا ثبت شده است.")
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
            st.button("گفتگوی جدید", key="new_session", type="primary")
            previous_sessions = request_previous_sessions()
            sessions = previous_sessions["sessions"]
            paraphrased_queries = previous_sessions["paraphrased_queries"]
            for i, (paraphrased_query, session) in enumerate(
                zip(paraphrased_queries, sessions)
            ):
                st.button(paraphrased_query, key=f"session_button_{i}")
                st.session_state[f"session_{i}"] = session
                st.session_state[f"suggested_sessions_title_{i}"] = paraphrased_query
            st.session_state["suggested_sessions"] = sessions
            st.session_state["suggested_sessions_titles"] = paraphrased_queries
            st.session_state["first_encounter_with_extra_sessions"] = False

        else:
            st.button("جلسه جدید", key="new_session", type="primary")
            if clicked_on_new_session:
                previous_sessions = request_previous_sessions()
                sessions = previous_sessions["sessions"]
                paraphrased_queries = previous_sessions["paraphrased_queries"]
                st.session_state[f"session_title_{i}"] = paraphrased_queries
            else:
                sessions = st.session_state["suggested_sessions"]
                paraphrased_queries = st.session_state["suggested_sessions_titles"]
            for i, (paraphrased_query, session) in enumerate(
                zip(paraphrased_queries, sessions)
            ):
                st.button(paraphrased_query, key=f"session_button_{i}")
                st.session_state[f"session_{i}"] = session
                st.session_state[f"suggested_sessions_title_{i}"] = paraphrased_query

    with logging_column:
        for database in st.session_state["databases"]:
            title = database["title"]
            description = database["description"]
            with st.expander(title):
                st.write(description)


if __name__ == "__main__":
    main()
