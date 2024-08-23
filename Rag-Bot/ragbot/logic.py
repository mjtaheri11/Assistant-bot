from typing import List

from langchain.schema import SystemMessage
from langchain_community.chat_models import ChatOllama

from prompts import RAG_SYSTEM_PROMPT
from retriever import Retriever
from config import config
from logs import simple_logger


def get_chat_response(prompt: str) -> str:
    llm = ChatOllama(
        model=config["ollama"]["model_name"],
        temperature=config["ollama"]["temperature"],
        keep_alive=config["ollama"]["keep_alive"],
    )
    messages = [SystemMessage(content=prompt)]
    response = llm.invoke(messages)  # type: ignore[arg-type]
    return response.content


def history_serializer(history: List[tuple[str, str]]) -> str:
    serialized_history = ""
    for question, answer in history:
        serialized_history += f"USER: {question}\nASSISTANT: {answer}\n\n"
    return serialized_history


def query_responder(query: str, context: str, history: str) -> str:
    # TODO: Add appropriate logger.
    history = history_serializer(history)
    prompt = RAG_SYSTEM_PROMPT.format(
        context=context,
        history=history,
        question=query,
    )

    response = get_chat_response(prompt)
    return response


def prepare_final_context(query: str) -> str:
    retriever = Retriever()
    context = retriever.retrieve_context(query)[0]
    # TODO: need appropriate context management > context = context[: config["context"]["max_length"]] 
    if context.strip() == "":
        raise Exception("no context fetched")
    return context


def chat_responder(
    history: List[tuple[str, str]],
    user_utterance: str,
) -> tuple[str, str, str, str]:

    ok_response_status = config["chat_responder"]["ok_status"]
    doubtful_response_status = config["chat_responder"]["doubtful_status"]
    no_answer_response_status = config["chat_responder"]["no_answer_status"]

    try:
        context = prepare_final_context(user_utterance)
        response = query_responder(user_utterance, context, history)
        # TODO: response should be validated
        response_is_valid = True
        # response_is_valid = answer_validator(
        #     paraphrased_utterance,
        #     context,
        #     response,
        # )
        if response_is_valid:
            return user_utterance, response, ok_response_status
        else:
            return user_utterance, response, ok_response_status
    except Exception:
        return user_utterance, "", no_answer_response_status

def feedback(
    query: str,
    response: str,
    feedback_type: str,
) -> None:
    # TODO: there should be an appropriate caching strategy
    # cache = Cache()
    if feedback_type == "thumb_up":
        pass
        # cache.increment_thumb_up(query, response, url)
    elif feedback_type == "thumb_down":
        pass
        # cache.increment_thumb_down(query, response, url)