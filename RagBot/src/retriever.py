import asyncio
import logging
from statistics import mean

from FlagEmbedding import FlagReranker
from langchain.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# from utils import get_config
from .config import config
from .logs import get_logger

logger = get_logger()


class ModelManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=config["embedding_model"]["model_name"],
            model_kwargs={"device": config["embedding_model"]["device"]}
        )
        self.reranker_model = FlagReranker(
            config["reranker"]["model_name"],
            device=config["reranker"]["device"],
            use_fp16=True
        )



class Retriever(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.config_ = config
        model_manager = ModelManager()

        self.embedding_model_ = model_manager.embedding_model
        self.reranker_model_ = model_manager.reranker_model

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


    async def _rerank_documents(self, query, documents, k):
        scores = self.reranker_model_.compute_score([[query, doc] for doc in documents], normalize=True)
        docs_with_scores = [(documents[i], scores[i]) for i in range(len(documents)) if scores[i] > config["retriever"]["retriever_threshold"]]
        if len(docs_with_scores) > 0:
            docs_scores_sorted = sorted(docs_with_scores, key=lambda x: x[1], reverse=True)
            if len(docs_scores_sorted) > k and docs_scores_sorted[k-1][1] > 0.06:
                # TODO: here I want to add all the documents with similarity more that 35 percent
                docs_scores_sorted = [elem for i, elem in enumerate(docs_scores_sorted) if i < k+3]
            else:
                docs_scores_sorted = docs_scores_sorted[:k]
            # conf = mean([d[1] for d in docs_scores_sorted])        
            # TODO: appropriate logger
            sorted_documents = '\n\n'.join([d[0] for i, d in enumerate(docs_scores_sorted)])
        else:
            sorted_documents = ""
        return sorted_documents

    async def retrieve_context(self, query, k=config["retriever"]["retrieved_rank2_documents"]):
        # TODO: appropriate logger
        documents = await self.retriever_.ainvoke(query)
        documents = [doc.page_content for doc in documents]
        conf = None
        sorted_documents = await self._rerank_documents(query, documents, k)
        return sorted_documents
