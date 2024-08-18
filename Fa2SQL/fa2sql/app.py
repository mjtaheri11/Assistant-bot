import utils
import streamlit as st
from prompts import SQL_GENERATOR_PROMPT_HIST, SCHEMA_GL, SCHEMA_INV, SQL_GENERATOR_PROMPT_NO_HIST
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx
from streamlit_feedback import streamlit_feedback
from styles import  HTML_RTL_INPUT_BODY

from langchain_community.chat_models import ChatOllama


schemas = {'دفتر کل': SCHEMA_GL, 'انبار': SCHEMA_INV}

utils.validate_config()
st.set_page_config(page_title= "SG-DA Fa2SQL BOT", page_icon= "🤖")
st.title("Welcome to System Group Fa2SQL BOT!")
ctx = get_script_run_ctx()

schema_name = st.selectbox(
    '**از کدوم ماژول میخواید گزارش بگیرید؟**', [s for s in schemas], 
    index=1
     )

logger = utils.init_logger()
logger.info("The app is started!", extra={"session": ctx.session_id})

config = utils.get_config()
llm_model = config['ollama']['model_name']

logger.info("Loading Ollama model", extra={"model": llm_model, "session": ctx.session_id})

llm = ChatOllama(model= llm_model, temperature=config['ollama']['temperature'], keep_alive=config['ollama']['keep_alive'])

def reset_conversation() -> None:
    st.session_state.messages = []

def feedback_submit(values, session_id=None, question=None, answer=None):
    logger.info('feedback submitted', extra={"session": session_id, 'feedback_score': values['score'], 
                                             'feedback_text': values['text'], 'question': question,  'answer': answer})

def main():
   
    full_response = ""

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(HTML_RTL_INPUT_BODY.format(message["content"]),unsafe_allow_html=True)

    user_query = st.chat_input(placeholder="چه گزارشی لازم دارید؟")

    if user_query:
        with st.chat_message("user"):
            st.markdown(HTML_RTL_INPUT_BODY.format(user_query),unsafe_allow_html=True)
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            history = [m['role'] + ": " + m['content'] for m in st.session_state.messages]
            history = '\n'.join(history)

            st.session_state.messages.append({"role": "user", "content": user_query})

            full_response = ""
            
            for response in llm.stream(SQL_GENERATOR_PROMPT_NO_HIST.format(schema=schemas[schema_name], question=user_query)):
                full_response += response.content
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        logger.info("call llm", extra={"session": ctx.session_id, 'question': user_query, 'answer': full_response, 'history': history})

    if 'sidebar_visible' not in st.session_state:
        st.session_state.sidebar_visible = False

    col1, col2, col3 = st.columns([1,1,4])
    with col1:
        st.button('Clear History', on_click=reset_conversation, type="primary")

    with col2:
        if st.button('See the Schema',type="primary"):
            st.session_state.sidebar_visible = not st.session_state.sidebar_visible

    with col3:
        streamlit_feedback(
            feedback_type="faces",
            optional_text_label="میشه دلیلشو بگی؟",
            kwargs={'question': user_query, 'answer': full_response, 'session_id': ctx.session_id},
            align='flex-start',
            on_submit=feedback_submit
            )
    if st.session_state.sidebar_visible:
        with st.sidebar:
            st.title("Database Schema")
            st.write(schemas[schema_name])


if __name__ == "__main__":
    main()
