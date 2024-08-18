from statistics import mean
from utils import get_config
import logging

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from FlagEmbedding import FlagReranker

logger = logging.getLogger(__name__)
config = get_config()

class Retriever(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.config_ = get_config()

            cls._instance.embedding_model_ = HuggingFaceEmbeddings(
                model_name=cls._instance.config_["embedding_model"]["model_name"],
                model_kwargs={"device": cls._instance.config_["embedding_model"]["device"]}
            )

            cls._instance.reranker_model_ = FlagReranker(
                cls._instance.config_["reranker"]["model_name"],
                device=cls._instance.config_["reranker"]["device"]
            )

            cls._instance.vectordb_ = Chroma(
                persist_directory=cls._instance.config_["database"]["persist_directory"],
                embedding_function=cls._instance.embedding_model_
            )

            cls._instance.retriever_ = cls._instance.vectordb_.as_retriever(search_kwargs={"k":config['retriever']['retrieved_documents']})

            cls._instance.alpha_threshold_ = cls._instance.config_["retriever"]["alpha_threshold"]

        return cls._instance

    def retrieve_context(self, query, k=config['retriever']['retrieved_documents']):
        logger.info("retriever is called", extra={"query": query, "k": k})

        if self.config_["retriever"]["expansion"]:
            query = self.expand_query(query)
        documents = self.retriever_.invoke(query)
        documents = [doc.page_content for doc in documents][:k]
        conf = None
        if self.config_["retriever"]["rerank"]:
            scores = self.reranker_model_.compute_score([[query, doc] for doc in documents], normalize=True)
            documents = [doc for doc, score in zip(documents, scores) if score > self.alpha_threshold_][0:config['reranker']['cutoff']]
            conf = mean(scores)

        logger.info("retriever returns", extra={"query": query,"documents": '\n'.join(documents), "conf": conf})
        return '\n'.join(documents), conf

    def expand_query(self, query):
        # TODO: Add implementation for expanding the query using the first docuemnt outputed from KB
        pass
