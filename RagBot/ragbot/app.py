import json 
import re
import pathlib

import requests
import streamlit as st
from retriever import Retriever
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx

from logs import simple_logger, non_generative_agent_logger
from prompts import RAG_SYSTEM_PROMPT
from utils import init_session_state
from config import config



RESPONSE_TEMPLATE_FOR_NO_ANSWER = """
    به سامانه سوال و جواب همکاران سیستم خوش آمدید. 
    سوال فعلی شما به همکاران سیستم مرتبط نیست. 
    لطفا سوالاتی را که به همکاران سیستم مرتبط هستند، بپرسید. 
    با تشکر
    """

CSS_STYLE_FILE = "{path}/style.css".format(path=pathlib.Path(__file__).parent.resolve())
BASE_URL = "http://185.13.230.222:8691" # "http://172.17.224.24:8686" 
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
    headers = {"Session-ID": session_id}
    response = requests.post(f"{api_url}/chat", json=chat_data, headers=headers)

    # Handle the different response status codes
    json_response = response.json()
    if response.status_code == 200:
        return {"status": "success", "query": query, "response": json_response["response"], "message_id": json_response["message_id"]}
    elif response.status_code == 404:
        return {"status": "error", "query": "", "response": "", "message_id": ""}
    elif response.status_code == 422:
        return {"status": "error", "query": "", "response": "", "message_id": ""}
    elif response.status_code == 500:
        return {"status": "error", "query": "", "response": "", "message_id": ""}
    else:
        return {"status": "error", "query": "", "response": "", "message_id": ""}


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


def feedback_button_clicked():
    return (
        st.session_state.get("like", False)
        or st.session_state.get("dislike", False)
        or st.session_state.get("flag", False)
    )


def main():
    # simple_logger("A session started")

    st.set_page_config(
        page_title="hamBot",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    init_session_state()
    if "session_id" not in st.session_state:
        session_id = session_create()
        st.session_state["session_id"] = session_id
    number_of_columns = [1, 4, 3]
    _, logging_column, main_column = st.columns(
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
                "سلام، من سامانه سوال و جواب همکاران سیستم هستم. لطفا سوالتون رو در کادر زیر بپرسید.",
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
                history = [
                    (user_utterance, system_response)
                    for user_utterance, system_response in zip(
                        st.session_state["user_utterance"],
                        st.session_state["response"],
                    )
                ]
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
                # elif response_status == config["chat_responder"]["doubtful_status"]:
                #     response = RESPONSE_TEMPLATE_FOR_DOUBTFUL_ANSWER
                #     response_is_valid = False
                elif chat_response["status"] == config["chat_responder"]["no_answer_status"]:
                    response = RESPONSE_TEMPLATE_FOR_NO_ANSWER
                    response_is_valid = False
                progress_bar.progress(value=100, text="Done.")
                st.session_state.query.append(query)
                st.session_state.response.append(response)
                st.session_state.user_input_storage.append(user_input)
                st.session_state["user_input"] = ""
                st.session_state["have_clicked_on_feedback"] = False
                st.session_state["response_is_valid"] = response_is_valid
                st.session_state["message_id"].append(message_id)

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
                            .replace("*", "&ast;")
                            .replace("#", "&#35;")
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
                                response = st.session_state.get("response")[i]
                                # TODO: has bug when you click on a suggested question and then on thumbup/down buttons
                                like = st.session_state.get("like", False)
                                dislike = st.session_state.get("dislike", False)
                                flag = st.session_state.get("flag", False)
                                if like:
                                    send_feedback(
                                        st.session_state["message_id"][-1],
                                        "thumb_up",
                                        st.session_state.get("session_id"),
                                    )
                                elif dislike:
                                    send_feedback(
                                        st.session_state["message_id"][-1],
                                        "thumb_down",
                                        st.session_state.get("session_id"),
                                    )
                                elif flag:
                                    # todo flag is not included in the redis yet!
                                    pass
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

    with logging_column:
        if st.session_state["enable_show_logs"]:
            for log in st.session_state["log"]:
                title = log["title"]
                description = log["description"]
                with st.expander(title):
                    st.write(description)


# from logic import chat_responder, feedback
# from streamlit_feedback import streamlit_feedback

# from styles import (HTML_RTL_INPUT_BODY, HTML_RTL_INPUT_TITLE,
#                     HTML_STYLE_FOR_RTL_INPUT_ELEMENT)

# st.set_page_config(page_title="SG-DA RAG BOT", page_icon="🤖")

# st.title("Welcome to System Group RAG BOT!!")
# ctx = get_script_run_ctx()

# logger = utils.init_logger()
# # logger.info("The app is started!", extra={"session": ctx.session_id})

# config = utils.get_config()
# llm_model = config["ollama"]["model_name"]
# /home/user01/mj-workspace/Assistant-bot/TempVectorDB
# # logger.info("Loading Ollama model", extra={"model": llm_model, "session": ctx.session_id})

# llm = ChatOllama(
#     model=llm_model,
#     temperature=config["ollama"]["temperature"],
#     keep_alive=config["ollama"]["keep_alive"],
# )
# retriever = Retriever()


# def reset_conversation() -> None:
#     st.session_state.messages = []
#     st.session_state.contexts = []


# def feedback_submit(values, session_id=None, question=None, answer=None):
#     logger.info(
#         "feedback submitted",
#         extra={
#             "session": session_id,
#             "feedback_score": values["score"],
#             "feedback_text": values["text"],
#             "question": question,
#             "answer": answer,
#         },
#     )


# def main():

#     full_response = ""

#     if "messages" not in st.session_state:
#         st.session_state.messages = []

#     if "contexts" not in st.session_state:
#         st.session_state.contexts = []

#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(
#                 HTML_RTL_INPUT_BODY.format(message["content"]), unsafe_allow_html=True
#             )

#     user_query = st.chat_input(placeholder="سوالتون رو اینجا بپرسید")

#     if user_query:
#         with st.chat_message("user"):
#             st.markdown(HTML_RTL_INPUT_BODY.format(user_query), unsafe_allow_html=True)

#         with st.chat_message("assistant"):
#             message_placeholder = st.empty()
#             context = retriever.retrieve_context(user_query)[0]
#             history = [
#                 m["role"] + ": " + m["content"] for m in st.session_state.messages
#             ]
#             history = "\n".join(history)

#             if (
#                 len(st.session_state.contexts)
#                 > config["retriever"]["max_context_length"]
#             ):
#                 reset_conversation()

#             st.session_state.contexts.append(context)
#             contexts = "\n\n".join(st.session_state.contexts)

#             st.session_state.messages.append({"role": "user", "content": user_query})

#             full_response = ""

#             for response in llm.stream(
#                 RAG_SYSTEM_PROMPT.format(
#                     context=contexts, history=history, question=user_query
#                 )
#             ):
#                 full_response += response.content
#                 message_placeholder.markdown(
#                     HTML_RTL_INPUT_BODY.format(full_response + "▌"),
#                     unsafe_allow_html=True,
#                 )
#             message_placeholder.markdown(
#                 HTML_RTL_INPUT_BODY.format(full_response), unsafe_allow_html=True
#             )

#         st.session_state.messages.append(
#             {"role": "assistant", "content": full_response}
#         )
#         logger.info(
#             "call llm",
#             extra={
#                 "session": ctx.session_id,
#                 "question": user_query,
#                 "answer": full_response,
#                 "context": context,
#                 "history": history,
#             },
#         )

#     if "sidebar_visible" not in st.session_state:
#         st.session_state.sidebar_visible = False

#     col1, col2, col3 = st.columns([1, 1, 4])
#     with col1:
#         st.button("Clear History", on_click=reset_conversation, type="primary")

#     with col2:
#         if st.button("See the Context", type="primary"):
#             st.session_state.sidebar_visible = not st.session_state.sidebar_visible

#     with col3:
#         streamlit_feedback(
#             feedback_type="faces",
#             optional_text_label="میشه دلیلشو بگی؟",
#             kwargs={
#                 "question": user_query,
#                 "answer": full_response,
#                 "session_id": ctx.session_id,
#             },
#             align="flex-start",
#             on_submit=feedback_submit,
#         )

#     if st.session_state.sidebar_visible:
#         with st.sidebar:
#             st.markdown(
#                 HTML_RTL_INPUT_TITLE.format("مطالب مرتبط با سوال شما"),
#                 unsafe_allow_html=True,
#             )
#             for c in st.session_state.contexts:
#                 st.markdown(HTML_RTL_INPUT_BODY.format(c), unsafe_allow_html=True)
#                 st.write("--------------------")


if __name__ == "__main__":
    # st.markdown(HTML_STYLE_FOR_RTL_INPUT_ELEMENT, unsafe_allow_html=True)

    main()
