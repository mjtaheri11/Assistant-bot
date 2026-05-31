import os
import re
import json
import requests
import streamlit as st
import time

from aiohttp.web_exceptions import HTTPException

from src.config import config
from src.logs import non_generative_agent_logger, simple_logger
from src.utils import init_session_state
from dotenv import load_dotenv


load_dotenv()

NUMBER_OF_SUGGESTED_SESSIONS = 30
NUMBER_OF_SUGGESTED_DATABASE = 10
INPUT_COMPANY_NAME = "نام شرکت خود را وارد کنید"
INPUT_ASSISTANT_NAME = "نام دستیار خود را وارد کنید"
BASE_URL = os.getenv("BASE_URL_BACKEND")

CSS_STYLE_FILE = "./src/style.css"
validation_template_response = "If the query is executable on the platform engine:"

def validate_execution(query):
    import json
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as p:
            # Launch the browser in visible mode (headless=False) to see the interaction
            try:
                browser = p.chromium.launch(headless=True)
            except Exception as e:
                return f"Error launching browser: {e}"
            
            try:
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
                )
                page = context.new_page()
            except Exception as e:
                browser.close()
                return f"Error creating browser page: {e}"

            # --- LOGIN FLOW ---
            try:
                # 1. Open the URL
                login_url = "http://aiconnect-dev.uat.mars.abramad.com/~shell/main/auth/ai-dev"
                print(f"Navigating to Login: {login_url}...")
                page.goto(login_url)
            except Exception as e:
                browser.close()
                return f"Error opening login page: {e}"

            # 2. Fill User 'admin'
            print("Filling username...")
            try:
                page.wait_for_selector("input.ng-touched", timeout=1000)
                page.fill("input.ng-touched", "pegah")
            except Exception as e:
                print(f"Could not find 'input.ng-touched' immediately: {e}")
                print("Attempting to fill the first available input as fallback...")
                browser.close()
                return "Error filling in username"

            # 3. Fill Password 'admin'
            print("Filling password...")
            try:
                page.fill(".relative-field > input:nth-child(1)", "Aa123456")
            except Exception as e:
                browser.close()
                return f"خطا هنگام پر کردن رمز عبور: {e}"

            # 4. Press the submit button
            print("Clicking submit button...")
            try:
                page.click(".form__submit-btn")
            except Exception as e:
                browser.close()
                return f"Error when clicking the login button: {e}"

            # 5. Wait 2 seconds for login to process
            print("Waiting 1.5 seconds...")
            page.wait_for_timeout(1500)

            # --- POST REQUEST FLOW ---

            # 6. Navigate to the specific URL (ensures we are on the right page)
            try:
                target_url = "http://aiconnect-dev.uat.mars.abramad.com/~shell/main/auth/ai-dev"
                print(f"Navigating to Target: {target_url}...")
                page.goto(target_url)
            except Exception as e:
                browser.close()
                return f"Error opening target page: {e}"

            # 7. Extract cookies and perform the POST request
            print("Extracting cookies...")
            try:
                cookies = context.cookies()
                # Format cookies into a single header string: "key1=value1; key2=value2"
                cookie_header = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
                print(f"Cookies retrieved: {cookie_header[:50]}...")  # Print first 50 chars for verification
            except Exception as e:
                browser.close()
                return f"Error extracting cookies: {e}"

            post_url = "http://aiconnect-dev.uat.mars.abramad.com/aiconnect/api/dev/parse"

            payload = {
                "query": query
            }

            # Include the extracted cookies explicitly in the headers
            post_headers = {
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json",
                # "Idempotency-Key": "97ad29db-b327-d352-6222-d5b9b2224638",
                "Origin": "http://aiconnect-dev.uat.mars.abramad.com",
                "Referer": "http://aiconnect-dev.uat.mars.abramad.com/main/auth/ai-dev",
                "Cookie": cookie_header
            }

            print(f"Sending POST request to {post_url}...")
            try:
                # We use page.request here, but since we are explicitly passing the Cookie header,
                # it ensures the specific tokens we extracted are sent.
                response = page.request.post(post_url, data=payload, headers=post_headers)

                print(f"Status Code: {response.status}")
                print("\nResponse Body:")
                
                if response.status == 200:
                    try:
                        response_data = response.json()
                        print(json.dumps(response_data, indent=2))
                        browser.close()
                        return f"The operation was successful. Status code: {response.status}"
                    except Exception:
                        response_text = response.text()
                        print(response_text)
                        browser.close()
                        return f"The operation was successful. Status code: {response.status}"
                else:
                    browser.close()
                    return f"API request error. Status code: {response.status}"

            except Exception as e:
                print(f"API Request failed: {e}")
                browser.close()
                return f"Error sending request to API: {e}"

    except Exception as e:
        return f"خطای غیرمنتظره: {e}"


def session_create(database_id: str = None, api_url: str = BASE_URL):
    """
    Sends a POST request to create a session and returns the session ID if successful.

    :param api_url: The URL for the session creation API endpoint.
    :return: The session ID if successful, None otherwise.
    """
    try:
        create_session_data = {"tenant_name": "admin", "user_code": "admin"}
        if database_id:
            create_session_data = {"database_id": database_id,
                                   "tenant_name": "admin",
                                   "user_code": "admin"
                                   }
        response = requests.post(
            f"{api_url}/v1/session/create", json=create_session_data)
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response and extract the
            data = response.json()
            session_id = data.get("session_id")
            return session_id
        else:
            # Handle any other status codes
            return None

    except requests.exceptions.RequestException:
        # Handle any errors that occur during the request
        return None


def request_simple_qa(session_id, query, api_url: str = BASE_URL):
    payload = {
        "query": query,
        "session_id": session_id,  # Assume this is generated or fetched from somewhere
    }

    response = requests.get(f"{api_url}/v1/faq", params=payload)
    json_response = response.json()
    if response.status_code == 200:
        return {
            "status": "success",
            "response": json_response["response"]
        }
    else:
        return {"status": "error", "response": ""}


def chat_request(
    session_id: str,
    query: str,
    on_click: bool,
    database_id: str = None,
    answer_type: str = "concise",
    does_evaluate: bool = False,
    use_cache: bool = True,
    api_url: str = BASE_URL,
    sql_mode: bool = False,
):

    # Define the request data
    chat_data = {
        "query": query,
        "session_id": session_id,  # Assume this is generated or fetched from somewhere
        "on_click": on_click,
        "does_evaluate": does_evaluate,
        "response_type": answer_type,
        "use_cache": use_cache,
        "sql_mode": sql_mode,
    }
    if database_id:
        chat_data["database_id"] = database_id

    headers = {"Session-ID": session_id}
    response = requests.post(
        f"{api_url}/v1/chat", json=chat_data, headers=headers
    )  # , timeout=11

    # Handle the different response status codes
    json_response = response.json()
    if response.status_code == 200:
        is_sql = json_response.get("is_sql", False)
        is_ticket = json_response.get("is_ticket", False)
        parameters = json_response.get("parameters", {}) or {}

        if is_sql:
            json_response["response"] = {
                "response": json_response["response"],
                "parameters": parameters,
                "response_template": json_response.get("response_template", ""),
            }
        elif is_ticket:
            # Bundle the ticket fields with the response so the renderer has
            # everything it needs in one place.
            json_response["response"] = {
                "response": json_response["response"],
                "parameters": parameters,
            }

        return {
            "status": "success",
            "query": json_response["query"],
            "response": json_response["response"],
            "message_id": json_response["message_id"],
            "choices": json_response.get("choices", []),
            "is_sql": is_sql,
            "is_ticket": is_ticket,
            "do_suggest": json_response.get("do_suggest", False),
        }
    else:
        return {"status": "error", "query": "", "response": "", "message_id": "",
                "choices": [], "is_sql": False, "is_ticket": False, "do_suggest": False}


def sql_request(query: str, session_id: str, on_click: bool, database_id: str = None, api_url: str = BASE_URL):
    # Define the request data
    sql_data = {
        "session_id": session_id,
        "query": query,
        "on_click": on_click
    }
    if database_id:
        sql_data["database_id"] = database_id

    response = requests.post(f"{api_url}/chat/sql",
                             json=sql_data)  # , timeout=11

    # Handle the different response status codes
    json_response = response.json()
    if response.status_code == 200:
        return {"status": "success", "query": query, "response": json_response["response"],
                "message_id": json_response["message_id"], "choices": json_response.get("choices", [])}
    else:
        return {"status": "error", "query": "", "response": "", "message_id": "", "choices": []}


def request_history(session_id, api_url: str = BASE_URL):
    payload = {
        "page_index": 1,
        "page_size": 30,
        "session_id": session_id,
        "contain_paraphrase": True,
    }
    response = requests.get(f"{api_url}/v1/chat", params=payload)
    json_response = response.json()
    if response.status_code == 200:
        return {"status": "sucess", "history": json_response["history"]}
    else:
        return {"status": "error", "history": ""}


def request_previous_sessions(api_url: str = BASE_URL):
    response = requests.get(f"{api_url}/v1/sessions")
    json_response = response.json()
    if response.status_code == 200:
        paraphrased_query = []
        sessions = []
        assistant_names = []
        company_names = []

        for response in json_response["response"]:
            assistant_names.append(response.get("assistant_name", ""))
            company_names.append(response.get("company_name", ""))
            sessions.append(response["session_id"])
            paraphrased_query.append("" if response.get(
                "paraphrased_query") == None else response.get("paraphrased_query"))
        return {
            "status": "sucess",
            "company_names": company_names,
            "assistant_names": assistant_names,
            "paraphrased_queries": paraphrased_query,
            "sessions": sessions,
        }
    else:
        raise HTTPException


def request_previous_databases(api_url: str = BASE_URL):
    response = requests.get(f"{api_url}/v1/databases")
    json_response = response.json()
    if response.status_code == 200:
        company_names = []
        assistant_names = []
        database_ids = []
        for response in json_response["response"]:
            database_ids.append(response["database_id"])
            company_names.append(response["company_name"])
            assistant_names.append(response["assistant_name"])
        return {
            "status": "sucess",
            "database_ids": database_ids,
            "company_names": company_names,
            "assistant_names": assistant_names
        }
    else:
        raise HTTPException


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
        f"{api_url}/v1/feedback", json=feedback_data, headers={"Session-ID": session_id}
    )
    json_response = response.json()
    if response.status_code == 200:
        return json_response
    else:
        return {"message": "error"}

def create_database_api_request(
    company_name,
    assistant_name,
    uploaded_files,
    recreate: bool = True,
    batch_size: int = 100,
    default_collection: bool = False,
):
    params = {
        "company_name": company_name,
        "assistant_name": assistant_name,
        "recreate": recreate,
        "batch_size": batch_size,
        "default_collection": default_collection,
    }
    files = [('files', (file.name, file)) for file in uploaded_files]

    try:
        response = requests.post(
            f"{BASE_URL}/v1/chat/create/database", params=params, files=files
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


def udpate_temporal_names(key=None):
    st.session_state[key] = st.session_state[f"temporal_{key}"]
    st.session_state[f"temporal_{key}"] = ""


def clear_text():
    st.session_state["user_input"] = st.session_state["temporal_user_input"]
    st.session_state["temporal_user_input"] = ""


def clear_retriever_text():
    st.session_state["retriever_user_input"] = st.session_state["temporal_retriever_user_input"]
    st.session_state["temporal_retriever_user_input"] = ""


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

def render_ticket_card(ticket_payload: dict):
    """
    Render the ticket fields (title, description, system, form) as a read-only
    Persian form card inside the assistant message.
    `ticket_payload` is the dict stored in session_state.response[i] when
    the turn is a ticket turn — it has the shape:
      {"response": "<confirmation message>", "parameters": {title, description, system, form, ...}}
    """
    confirmation = ticket_payload.get("response", "")
    params = ticket_payload.get("parameters", {}) or {}

    title = params.get("title", "")
    description = params.get("description", "")
    system = params.get("system", "")
    form = params.get("form", "")

    if confirmation:
        st.markdown(
            f'<div class="markdown-rtl">{confirmation}</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="markdown-rtl" style="
            border: 1px solid #d0d7de;
            border-radius: 10px;
            padding: 16px 18px;
            margin-top: 8px;
            background-color: #fafbfc;">
          <div style="font-weight: 600; margin-bottom: 10px;">🎫 پیش‌نمایش تیکت</div>
          <div style="margin-bottom: 8px;">
            <span style="color:#555;">عنوان:</span>
            <span style="font-weight:500;">{title or '—'}</span>
          </div>
          <div style="margin-bottom: 8px;">
            <span style="color:#555;">سیستم:</span>
            <span style="font-weight:500;">{system or '—'}</span>
          </div>
          <div style="margin-bottom: 8px;">
            <span style="color:#555;">فرم:</span>
            <span style="font-weight:500;">{form or '—'}</span>
          </div>
          <div style="margin-bottom: 4px;">
            <span style="color:#555;">توضیحات:</span>
          </div>
          <div style="
              white-space: pre-wrap;
              background-color: #ffffff;
              border: 1px solid #e5e7eb;
              border-radius: 6px;
              padding: 10px 12px;
              line-height: 1.7;">
            {description or '—'}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def main():
    st.set_page_config(
        page_title="hamzan",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    init_session_state()
    clicked_on_sidebar_sessions = False
    clicked_on_new_session = False
    clicked_on_database_id = False
    for i in range(NUMBER_OF_SUGGESTED_SESSIONS):

        if st.session_state.get(f"session_button_{i}"):
            clicked_on_sidebar_sessions = True
            session_id_clicked = st.session_state.get(f"session_{i}")
            st.session_state["session_id"] = session_id_clicked
            st.session_state["company_name"] = st.session_state.get(
                f"suggested_company_name_{i}", "")
            st.session_state["assistant_name"] = st.session_state.get(
                f"suggested_assistant_name_{i}", "")
            history = request_history(session_id_clicked, BASE_URL)
            st.session_state["enable_submit_form"] = False
            st.session_state["form_submitted"] = False
            if history["history"]:
                st.session_state["first_encounter_with_searchbox"] = False
            else:
                st.session_state["first_encounter_with_searchbox"] = True

    for i in range(NUMBER_OF_SUGGESTED_DATABASE):
        if st.session_state.get(f"database_button_{i}"):
            clicked_on_database_id = True
            database_id_clicked = st.session_state.get(f"database_id_{i}")
            st.session_state["database_id"] = database_id_clicked
            st.session_state["company_name"] = st.session_state.get(
                f"company_name_{i}")
            st.session_state["assistant_name"] = st.session_state.get(
                f"assistant_name_{i}")
            st.session_state["session_id"] = session_create(
                database_id=database_id_clicked)
            st.session_state["first_encounter_with_searchbox"] = True
            st.session_state["enable_submit_form"] = False
            st.session_state["form_submitted"] = False

    for i in range(len(st.session_state.get("suggested_modules", []))):
        if st.session_state.get(f"suggestion_button_clicked_{i}"):
            st.session_state["user_input"] = st.session_state.get(
                f"suggestion_button_clicked_title_{i}")

    if st.session_state.get("new_session"):
        st.session_state["first_encounter_with_searchbox"] = True
        st.session_state["session_id"] = session_create()
        clicked_on_new_session = True

    if st.session_state.get("temporal_enable_submit_form"):
        st.session_state["enable_submit_form"] = True
        st.session_state["first_encounter_with_searchbox"] = True

    if "session_id" not in st.session_state:
        session_id = session_create()
        st.session_state["session_id"] = session_id

    number_of_columns = [1, 2, 1, 5, 2]
    logging_column, sessions_column, _, main_column, _ = st.columns(
        number_of_columns,
        gap="small",
    )

    with open(CSS_STYLE_FILE) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(
            "در این قسمت هم میتوانید دستیار خود را سفارش دهید یا از دستیار های قبلی خود استفاده کنید")
        st.button("ساخت دستیار", key="temporal_enable_submit_form",
                  type="primary")
        suggested_databases_titles = []
        previous_databases = request_previous_databases()
        database_ids = previous_databases["database_ids"]
        company_names = previous_databases["company_names"]
        assistant_names = previous_databases["assistant_names"]
        for i, (database_id, company_name, assistant_name) in enumerate(
            zip(database_ids, company_names, assistant_names)
        ):
            suggested_database_name = company_name + \
                " - " + assistant_name + "\n\n" + database_id
            st.button(suggested_database_name, key=f"database_button_{i}")
            st.session_state[f"database_id_{i}"] = database_id
            st.session_state[f"company_name_{i}"] = company_name
            st.session_state[f"assistant_name_{i}"] = assistant_name
            suggested_databases_titles.append(suggested_database_name)
        st.session_state["suggested_databases_titles"] = suggested_databases_titles
        st.session_state["suggested_databases"] = database_ids
        st.divider()

    if st.session_state.get("clear_logs_button", False):
        clear_logs()

    with main_column:
        main_chat_tab, simple_qa_tab = st.tabs(["چت اصلی", "ارزیابی بازیابی"])
        # --- Main Chat Tab ---
        with main_chat_tab:
            if st.session_state.get("form_submitted", False):
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
                            recreate=boolean_mapper(st.session_state.get("temporal_recreate", "بله")),
                            batch_size=int(st.session_state.get("temporal_batch_size", 100)),
                            default_collection=boolean_mapper(
                                st.session_state.get("temporal_default_collection", "خیر")
                            ),
                        )
                        if status == "success":
                            udpate_temporal_names("assistant_name")
                            udpate_temporal_names("company_name")
                            st.session_state["does_evaluate"] = boolean_mapper(
                                st.session_state.get("temporal_does_evaluate"))
                            st.session_state["use_cache"] = boolean_mapper(
                                st.session_state["temporal_use_cache"])
                            st.session_state["database_id"] = data["database_id"]
                            st.session_state["session_id"] = session_create(
                                database_id=data["database_id"])
                            st.session_state["enable_submit_form"] = False
                            st.session_state["form_submitted"] = False
                        else:
                            st.error(message)

            if st.session_state.get("enable_submit_form", False):
                with st.form(key="create_database_form"):
                    st.info(
                        " با استفاده از این سامانه میتواند فایل های خود را آپلود کرده و دستیار شخصی سازی شده خود را تحویل بگیرید.",
                    )
                    _ = st.file_uploader(
                        "لطفا داکیومنت های مربوط به شرکت یا سازمان خود را با فرمت های مشخص شده وارد کنید.",
                        type=["docx", "doc"],
                        accept_multiple_files=True,
                        key="uploaded_files",
                        help=None,
                        on_change=None,
                        disabled=False,
                        label_visibility="hidden",
                    )

                    st.markdown(INPUT_ASSISTANT_NAME)
                    st.text_input(
                        INPUT_ASSISTANT_NAME,
                        placeholder=INPUT_ASSISTANT_NAME,
                        key="temporal_assistant_name",
                        label_visibility="collapsed",
                    )
                    st.markdown(INPUT_COMPANY_NAME)
                    st.text_input(
                        INPUT_COMPANY_NAME,
                        placeholder=INPUT_COMPANY_NAME,
                        key="temporal_company_name",
                        label_visibility="collapsed",
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
                        ["بله", "خیر"],
                        key="temporal_use_cache",
                        label_visibility="collapsed"
                    )
                    st.markdown("استفاده از مجموعه پیش‌فرض")
                    st.selectbox(
                        "استفاده از مجموعه پیش‌فرض",
                        ["بله", "خیر"],
                        key="temporal_default_collection",
                        label_visibility="collapsed",
                    )
                    st.markdown("بازسازی مجموعه در صورت وجود")
                    st.selectbox(
                        "بازسازی مجموعه در صورت وجود",
                        ["بله", "خیر"],
                        key="temporal_recreate",
                        label_visibility="collapsed",
                    )

                    st.markdown("اندازه دسته پردازش")
                    st.number_input(
                        "اندازه دسته پردازش",
                        min_value=1,
                        max_value=1000,
                        value=100,
                        step=10,
                        key="temporal_batch_size",
                        label_visibility="collapsed",
                    )
                    st.form_submit_button(
                        "ارسال", on_click=form_submit_button, type="primary")
            else:
                if st.session_state["first_encounter_with_searchbox"]:
                    company_name = st.session_state.get(
                        'company_name', '').strip()
                    assistant_name = st.session_state.get(
                        'assistant_name', '').strip()
                    if company_name and assistant_name:
                        st.info(
                            f"سلام، من سامانه {assistant_name} {company_name} هستم. لطفا سوالتون رو در کادر زیر بپرسید.")
                    else:
                        st.info(
                            "سلام، من سامانه دستیار دیجیتال نسل چهارم همکاران سیستم هستم. لطفا سوالتون رو در کادر زیر بپرسید.")
                    st.session_state["first_encounter_with_searchbox"] = False
                
                st.markdown("""
                    <style>
                    div[data-testid="column"] {
                        padding-top: 0rem;
                        padding-bottom: 0rem;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                
                # IMPROVED: Compact layout for all controls
                col1, col2, col3, col4 = st.columns([6, 2, 2, 2], gap="small")

                with col1:
                    # IMPROVED: Radio buttons moved to same row, more compact
                    # st.markdown('<div class="markdown-rtl compact-radio-label">نوع پاسخ:</div>', unsafe_allow_html=True)
                    st.radio(
                        "نوع پاسخ",
                        options=["خلاصه", "عادی", "توضیحی"],
                        key="temporal_answer_type",
                        label_visibility="visible",
                        disabled=False,
                        horizontal=True,
                    )

                with col2:
                    st.markdown(
                        '<div class="markdown-rtl">عامل SQL</div>', unsafe_allow_html=True)
                    st.selectbox(
                        '<div class="markdown-rtl">عامل SQL</div>',
                        ["بله", "خیر"],
                        key="temporal_sql_mode",
                        label_visibility="collapsed"
                    )

                with col3:
                    st.markdown(
                        '<div class="markdown-rtl">OSS برای SQL</div>', unsafe_allow_html=True)
                    st.selectbox(
                        '<div class="markdown-rtl">مدل او اس اس برای SQL</div>',
                        ["خیر", "بله"],
                        key="temporal_model_selector",
                        label_visibility="collapsed"
                    )

                with col4:
                    st.markdown(
                        '<div class="markdown-rtl">اجرای کوئری</div>', unsafe_allow_html=True)
                    st.selectbox(
                        '<div class="markdown-rtl">اجرای کوئری</div>',
                        ["خیر", "بله"],
                        key="temporal_evaluate_sql",
                        label_visibility="collapsed"
                    ) 
                
                # Text input on its own row
                st.text_input(
                    st.session_state.get("session_id"),
                    placeholder="لطفا سوال خود را وارد کنید",
                    key="temporal_user_input",
                    on_change=clear_text,
                )
                st.session_state["sql_mode"] = boolean_mapper(
                    st.session_state["temporal_sql_mode"])
                st.session_state["model_selector"] = boolean_mapper(
                    st.session_state["temporal_model_selector"]
                )
                st.session_state["evaluate_sql"] = boolean_mapper(
                    st.session_state["temporal_evaluate_sql"]
                )
                progress_bar = st.progress(value=0)
                with st.container():
                    if st.session_state.get("user_input"):
                        user_input = st.session_state["user_input"]
                        database_id = st.session_state.get("database_id")
                        st.session_state.user_utterance.append(user_input)
                        st.session_state["answer_type"] = find_answer_type(
                            st.session_state.get("temporal_answer_type", "عادی"))
                        st.session_state["on_click"] = st.session_state.get(
                            "on_click", False)
                        st.session_state["does_evaluate"] = st.session_state.get(
                            "does_evaluate", False)
                        st.session_state["use_cache"] = st.session_state.get(
                            "use_cache", True)

                        simple_logger(
                            f"user said: {user_input}",
                            session_id=st.session_state.get("session_id"),
                        )
                        chat_response = chat_request(
                            session_id=st.session_state["session_id"],
                            query=user_input,
                            on_click=st.session_state["on_click"],
                            database_id=database_id,
                            answer_type=st.session_state["answer_type"],
                            does_evaluate=st.session_state["does_evaluate"],
                            use_cache=st.session_state["use_cache"],
                            sql_mode=st.session_state["sql_mode"],
                        )
                        do_suggest, is_sql, is_ticket, choices, message_id, response, query = (
                            chat_response["do_suggest"],
                            chat_response["is_sql"],
                            chat_response.get("is_ticket", False),
                            chat_response["choices"],
                            chat_response["message_id"],
                            chat_response["response"],
                            chat_response["query"],
                        )
                        if chat_response["status"] == config["chat_responder"]["ok_status"]:
                            response_is_valid = True
                        if do_suggest:
                            st.session_state["do_suggest_modules"] = True
                            st.session_state["on_click"] = True
                        else:
                            st.session_state["do_suggest_modules"] = False
                            st.session_state["on_click"] = False

                        progress_bar.progress(value=100, text="Done.")
                        st.session_state["choices"] = choices
                        st.session_state.do_suggest = do_suggest
                        st.session_state.query.append(query)
                        st.session_state.user_input_storage.append(user_input)
                        st.session_state["user_input"] = ""
                        st.session_state["have_clicked_on_feedback"] = False
                        st.session_state["response_is_valid"] = response_is_valid
                        st.session_state["suggested_modules"] = choices
                        st.session_state.sql_response_type.append(is_sql)
                        st.session_state.ticket_response_type.append(is_ticket)
                        st.session_state.response.append(response)
                        st.session_state.message_id.append(message_id)

                    elif clicked_on_sidebar_sessions:
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
                        def _rehydrate(message):
                            if message.get("is_sql"):
                                return {
                                    "response": message["response"],
                                    "parameters": message.get("parameters", {}),
                                    "response_template": message.get("response_template", ""),
                                }
                            if message.get("is_ticket"):
                                return {
                                    "response": message["response"],
                                    "parameters": message.get("parameters", {}),
                                }
                            return message["response"]

                        st.session_state.response = [
                            _rehydrate(message)
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
                        st.session_state.sql_response_type = [
                            message.get("is_sql", False)
                            for message in history["history"]
                            if history["history"]
                        ]
                        st.session_state.ticket_response_type = [
                            message.get("is_ticket", False)
                            for message in history["history"]
                            if history["history"]
                        ]
                        st.session_state["have_clicked_on_feedback"] = False
                        st.session_state["response_is_valid"] = True
                        progress_bar.progress(value=0)

                    elif clicked_on_new_session or clicked_on_database_id:
                        st.session_state.user_utterance = []
                        st.session_state.query = []
                        st.session_state.response = []
                        st.session_state.user_input_storage = []
                        st.session_state.message_id = []
                        st.session_state.have_clicked_on_feedback = False
                        st.session_state.response_is_valid = False
                        st.session_state.sql_response_type = []
                        st.session_state.ticket_response_type = []
                        progress_bar.progress(value=0)

                    if st.session_state.get("user_utterance"):
                        for i in reversed(range(len(st.session_state["user_utterance"]))):
                            with st.chat_message("user"):
                                st.markdown(
                                    f'<div class="markdown-rtl">{st.session_state["user_utterance"][i]}</div>',
                                    unsafe_allow_html=True,

                                )
                            with st.chat_message("assistant"):
                                help_msg = f"""برای پاسخ به سوال شما کوئری «{st.session_state['query'][i]}» \
                                جستجو شده است."""
                                content = st.session_state["response"][i]
                                is_sql = st.session_state.get(
                                    "sql_response_type", [False] * len(st.session_state["response"]))[i]
                                is_ticket = st.session_state.get(
                                    "ticket_response_type", [False] * len(st.session_state["response"]))[i]

                                if is_sql:
                                    validation_response = ""
                                    if st.session_state["evaluate_sql"] and st.session_state["user_input"]:
                                        direct_validation_response = validate_execution(content["response"])
                                        validation_response = f"The output of the execution response is:\n\n{direct_validation_response}"
                                    st.markdown(f'<div class="markdown-ltr sql-code-block">\n\n```sql\n{content}\n```\n\n{validation_response}</div>', unsafe_allow_html=True, help=help_msg)
                                elif is_ticket:
                                    # Inject RTL styling so the ticket card respects direction
                                    st.markdown("""
                                    <style>
                                    .stMarkdown { direction: rtl; text-align: right; }
                                    </style>
                                    """, unsafe_allow_html=True, help=help_msg)
                                    render_ticket_card(content)
                                else:
                                    # Inject RTL styling for all markdown content
                                    st.markdown("""
                                    <style>
                                    .stMarkdown {
                                        direction: rtl;
                                        text-align: right;
                                    }
                                    </style>
                                    """, unsafe_allow_html=True, help=help_msg)

                                    # Now use regular markdown (no unsafe_allow_html needed)
                                    st.markdown(content)
                                if st.session_state.get("do_suggest_modules") and i == len(st.session_state["response"]) - 1:
                                    # Create a number of columns equal to the number of suggested modules
                                    suggested_modules = st.session_state.get(
                                        "suggested_modules", [])
                                    if suggested_modules:
                                        cols = st.columns(
                                            len(suggested_modules))
                                        # Iterate through each module to create a button in its own column
                                        for index, module_name in enumerate(suggested_modules):
                                            with cols[index]:
                                                # Create a button with a unique key for each module
                                                st.button(
                                                    module_name, key=f"suggestion_button_clicked_{index}")
                                                # Store the module's title in the session state with a corresponding unique key
                                                st.session_state[
                                                    f"suggestion_button_clicked_title_{index}"] = module_name

                                if (
                                    i == len(st.session_state["response"]) - 1
                                    and not st.session_state.get("do_suggest_modules", False)
                                ):
                                    feedback_column_placeholder = st.empty()
                                    if feedback_button_clicked():
                                        st.session_state["have_clicked_on_feedback"] = True
                                        user_utterance = st.session_state.get(
                                            "user_input_storage",
                                        )[i]
                                        paraphrased_query = st.session_state.get("query")[
                                            i]
                                        message_id = st.session_state["message_id"][-1]
                                        response = st.session_state.get("response")[
                                            i]
                                        # TODO: has bug when you click on a suggested question and then on thumbup/down buttons
                                        like = st.session_state.get(
                                            "like", False)
                                        dislike = st.session_state.get(
                                            "dislike", False)
                                        flag = st.session_state.get(
                                            "flag", False)
                                        if like:
                                            result = send_feedback(
                                                message_id,
                                                "thumb_up",
                                                st.session_state.get(
                                                    "session_id"),
                                            )
                                        elif dislike:
                                            result = send_feedback(
                                                message_id,
                                                "thumb_down",
                                                st.session_state.get(
                                                    "session_id"),
                                            )
                                        elif flag:
                                            # todo flag is not included in the redis yet!
                                            result = send_feedback(
                                                message_id,
                                                "flag",
                                                st.session_state.get(
                                                    "session_id")
                                            )
                                        non_generative_agent_logger(
                                            session_id=st.session_state.get(
                                                "session_id"),
                                            agent="user feedback",
                                            message="user is clicked on feedback button",
                                            user_code="admin",
                                            tenant_name="admin",
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
                                        if result.get("message", "").lower() in ["feedback received", "feedback received"]:
                                            *_, text_col = feedback_column_placeholder.columns(
                                                [1, 1, 1, 5],
                                                gap="medium",
                                            )
                                            with text_col:
                                                st.markdown("نظر شما ثبت شد.")
                                        else:
                                            *_, text_col = feedback_column_placeholder.columns(
                                                [1, 1, 1, 5],
                                                gap="medium",
                                            )
                                            with text_col:
                                                st.markdown(
                                                    "نظر شما قبلا ثبت شده است.")
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

        # --- NEW TAB: Direct Q&A ---
        with simple_qa_tab:
            st.markdown("### پرسش و پاسخ مستقیم")
            st.info(
                "در این بخش می‌توانید یک سوال مشخص بپرسید و اسناد مربوط به آن را مشاهده کنید.")

            # This tab requires a database to be selected
            company_name = st.session_state.get(
                "company_name", "همکاران سیستم")
            assistant_name = st.session_state.get(
                "assistant_name", "دستیار دیجیتال")
            st.warning(
                f"در حال حاضر در حال استفاده از {assistant_name} برای شرکت {company_name} هستید.")

            # Input for the simple question
            st.text_input(
                st.session_state.get("session_id"),
                placeholder="لطفا سوال خود را وارد کنید",
                key="temporal_retriever_user_input",
                on_change=clear_retriever_text
            )

            if st.session_state.get("retriever_user_input"):
                with st.spinner("در حال جستجوی اسناد..."):
                    api_response = request_simple_qa(
                        query=st.session_state["retriever_user_input"],
                        session_id=st.session_state.get("session_id")
                    )
                    if api_response["status"] == "success":
                        st.session_state.retriever_user_answer = api_response["response"]
                    else:
                        st.session_state.retriever_user_answer = f"خطا در دریافت پاسخ: {api_response['response']}"
            else:
                if st.session_state.get("retriever_user_input") == "":
                    st.error("لطفا یک سوال وارد کنید.")

            # Display the last question and answer
            if st.session_state.get("retriever_user_answer"):
                st.markdown("---")
                st.success("**سوال شما:**")
                st.markdown(st.session_state.retriever_user_input)
                st.success("**پاسخ دریافت شده:**")
                st.markdown(
                    st.session_state.retriever_user_answer.replace("\n", "  \n"))

    with sessions_column:
        if st.session_state["first_encounter_with_extra_sessions"]:
            st.success(
                "این جا هم یه سری از جلسات قبلی شما هست که میتونید ازشون استفاده کنید.",
            )
            st.button("گفتگوی جدید", key="new_session", type="primary")
            previous_sessions = request_previous_sessions()
            sessions = previous_sessions["sessions"]
            paraphrased_queries = previous_sessions["paraphrased_queries"]
            company_names = previous_sessions.get("company_names", [])
            assistant_names = previous_sessions.get("assistant_names", [])
            for i, (paraphrased_query, session) in enumerate(zip(paraphrased_queries, sessions)):

                st.button(paraphrased_query, key=f"session_button_{i}")
                st.session_state[f"session_{i}"] = session
                st.session_state[f"suggested_sessions_title_{i}"] = paraphrased_query
                if i < len(company_names):
                    st.session_state[f"suggested_company_name_{i}"] = company_names[i]
                if i < len(assistant_names):
                    st.session_state[f"suggested_assistant_name_{i}"] = assistant_names[i]
            st.session_state["suggested_sessions"] = sessions
            st.session_state["suggested_sessions_titles"] = paraphrased_queries
            st.session_state["first_encounter_with_extra_sessions"] = False
        else:
            st.button("جلسه جدید", key="new_session", type="primary")
            if clicked_on_new_session:
                previous_sessions = request_previous_sessions()
                sessions = previous_sessions["sessions"]
                paraphrased_queries = previous_sessions["paraphrased_queries"]
            else:
                sessions = st.session_state.get("suggested_sessions", [])
                paraphrased_queries = st.session_state.get(
                    "suggested_sessions_titles", [])
            for i, (paraphrased_query, session) in enumerate(
                zip(paraphrased_queries, sessions)
            ):
                st.button(paraphrased_query, key=f"session_button_{i}")
                st.session_state[f"session_{i}"] = session
                st.session_state[f"suggested_sessions_title_{i}"] = paraphrased_query

    with logging_column:
        databases = st.session_state.get("databases", [])
        for database in databases:
            title = database["title"]
            description = database["description"]
            with st.expander(title):
                st.write(description)


if __name__ == "__main__":
    main()


# playwright install
# playwright install-deps