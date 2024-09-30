import logging
from statistics import mean

from FlagEmbedding import FlagReranker
from langchain.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# from utils import get_config
from config import config
from logs import get_logger

logger = get_logger()


class Retriever(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.config_ = config

        self.embedding_model_ = HuggingFaceEmbeddings(
            model_name=self.config_["embedding_model"]["model_name"],
            model_kwargs={
                "device": self.config_["embedding_model"]["device"]
            },
        )

        self.reranker_model_ = FlagReranker(
            self.config_["reranker"]["model_name"],
            device=self.config_["reranker"]["device"],
        )

        self.vectordb_ = Chroma(
            persist_directory=self.config_["database"][
                "persist_directory"
            ],
            embedding_function=self.embedding_model_,
        )

        self.retriever_ = self.vectordb_.as_retriever(
            search_kwargs={"k": config["retriever"]["retrieved_documents"]}
        )

        self.alpha_threshold_ = self.config_["retriever"][
            "alpha_threshold"
        ]


    def _rerank_documents(self, query, documents, k):
        scores = self.reranker_model_.compute_score([[query, doc] for doc in documents], normalize=True)
        docs_with_scores = [(documents[i], scores[i]) for i in range(len(documents)) if scores[i] > config["retriever"]["retriever_threshold"]]
        # import pdb
        # pdb.set_trace()
        if len(docs_with_scores) > 0:
            docs_scores_sorted = sorted(docs_with_scores, key=lambda x: x[1], reverse=True)[:k]
            # conf = mean([d[1] for d in docs_scores_sorted])        
            # TODO: appropriate logger
            sorted_documents = '\n\n'.join([d[0] for d in reversed(docs_scores_sorted)])
        else:
            sorted_documents = "No context fetched"
        return sorted_documents

    def retrieve_context(self, query, k=config["retriever"]["retrieved_rank2_documents"]):
        # TODO: appropriate logger

        if self.config_["retriever"]["expansion"]:
            query = self.expand_query(query)
        documents = self.retriever_.invoke(query)
        documents = [doc.page_content for doc in documents]
        conf = None
        sorted_documents = self._rerank_documents(query, documents, k)
        return sorted_documents

    def expand_query(self, query):
        # TODO: Add implementation for expanding the query using the first docuemnt outputed from KB
        pass
