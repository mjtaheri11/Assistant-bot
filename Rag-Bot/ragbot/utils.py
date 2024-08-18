import logging
import logging.handlers
from pythonjsonlogger import jsonlogger
import yaml

CONFIG_ADDR = "../configs/rag-configs.yaml"

with open(CONFIG_ADDR, 'r') as f:
    config_ = yaml.safe_load(f)

REQUIRED_KEYS = [
    'logging', 'streamlit', 'database', 'ollama', 'embedding_model',
    'reranker', 'retriever', 'langchain'
]

def validate_config():
    missing_keys = [key for key in REQUIRED_KEYS if key not in config_]
    if missing_keys:
        raise ValueError(f'The following keys are missing from the config file: {", ".join(missing_keys)}')


def get_config():
    return config_

def init_logger():
    logger = logging.getLogger(__name__)
    log_file = config_['logging']['file']
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=100*1024*1024, backupCount=2, encoding='utf-8')
    formatter = jsonlogger.JsonFormatter(log_format, timestamp=True)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)
    
    return logger
