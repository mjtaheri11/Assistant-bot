import logging
from datetime import datetime

from jsonformatter import JsonFormatter  # type: ignore

from config import config 

LOGGER_NAME = "HamBot"

def get_logger():
    # create a custom logger
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:  # logger is already setup, don't setup again
        return logger
    logger.propagate = False
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(config["log"]["file"], encoding="utf8")
    formatter = JsonFormatter(
        ensure_ascii=False,
        mix_extra=True,
        mix_extra_position="head",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def non_generative_agent_logger(
    session_id, agent, message, input_dict, output_dict, elapsed_time
):
    logger = get_logger()
    logger.info(
        message,
        extra={
            "session_id": session_id,
            "logtime": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "agent": agent,
            "input": input_dict,
            "elapsed_time_in_seconds": elapsed_time,
            "return": output_dict,
        },
    )

def simple_logger(message, session_id, log_level=logging.INFO):
    logger = get_logger()
    logger.log(
        log_level,
        message,
        extra={
            "session_id": session_id,
            "logtime": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
        },
    )
