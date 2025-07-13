import asyncio
import logging
from statistics import mean

from FlagEmbedding import FlagReranker
from mxbai_rerank import MxbaiRerankV2
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
        # self.reranker_model = FlagReranker(
        #     config["reranker"]["model_name"],
        #     device=config["reranker"]["device"],
        #     use_fp16=True
        # )
        self.reranker_model = MxbaiRerankV2(model_name_or_path="mixedbread-ai/mxbai-rerank-large-v2",
                                    device=config["reranker"]["device"], 
                                    top_k=config["retriever"]["retrieved_documents"])


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

    async def _rerank_documents(self, query: str, documents: list[str], k: int, reverse: bool = True) -> list[str]:
        """
        Reranks documents using the MxbaiRerankV2 model with custom filtering logic.
        """
        # 1. Get ranked results from the mxbai model.
        # The `rank` method returns a sorted list of dictionaries with scores.
        # We retrieve all results initially to apply custom thresholds later.
        results = self.reranker_model_.rank(
            query=query,
            documents=documents,
            return_documents=True,
            normalize=True,
        )
        # 2. Filter the already sorted results based on your score threshold.
        # The mxbai model output is a list of dicts: [{'text': doc, 'score': score}, ...]
        docs_scores_sorted = [
            res for res in results
            if res.score > self.config_["retriever"]["retriever_threshold"]
        ]

        # 3. Apply your custom logic for selecting the top 'k' documents.
        if docs_scores_sorted:
            final_docs = []
            # Check if we have more than 'k' documents and if the k-th score is above 0.06
            if len(docs_scores_sorted) > k and docs_scores_sorted[k-1].score > 0.06:
                # As in your original code, take the top k+3 documents
                final_docs = docs_scores_sorted[:k+3]
            else:
                # Otherwise, just take the top k documents
                final_docs = docs_scores_sorted[:k]

            # 4. Extract the document text for the final output.
            # NOTE: Your original function reversed the list at the end, returning documents
            # from lowest score to highest. This behavior is replicated here.
            # If you want the most relevant documents first, remove `reversed()`.
            if reverse:
                sorted_documents = [d.document for d in reversed(final_docs)]
            else:
                sorted_documents = [d.document for d in final_docs]                
        else:
            # If no documents meet the threshold, return an empty list.
            sorted_documents = []
        return sorted_documents

    async def retrieve_context(self, query, k=config["retriever"]["retrieved_rank2_documents"]):
        # TODO: appropriate logger
        documents = await self.retriever_.ainvoke(query)
        documents = [{"page_content": doc.page_content, "module": doc.metadata["source"]} for doc in documents]
        sorted_documents = await self._rerank_documents(query, documents, k)
        final_documents = '\n\n'.join(sorted_documents)
        return final_documents


# import asyncio
# import logging
# from statistics import mean

# from FlagEmbedding import FlagReranker
# from mxbai_rerank import MxbaiRerankV2
# from langchain.vectorstores import Chroma
# from langchain_community.embeddings import HuggingFaceEmbeddings

# # from utils import get_config
# from .config import config
# from .logs import get_logger

# logger = get_logger()


# class ModelManager:
#     _instance = None

#     def __new__(cls, *args, **kwargs):
#         if not cls._instance:
#             cls._instance = super(ModelManager, cls).__new__(cls)
#             cls._instance._initialize()
#         return cls._instance

#     def _initialize(self):
#         self.embedding_model = HuggingFaceEmbeddings(
#             model_name=config["embedding_model"]["model_name"],
#             model_kwargs={"device": config["embedding_model"]["device"]} 
#                           #"trust_remote_code": config["embedding_model"]["trust_remote_code"]}
#         )
#         # self.reranker_model = FlagReranker(
#         #     config["reranker"]["model_name"],
#         #     device=config["reranker"]["device"],
#         #     use_fp16=True
#         # )
#         self.reranker_model = MxbaiRerankV2(model_name_or_path="mixedbread-ai/mxbai-rerank-large-v2",
#                                             device=config["reranker"]["device"], 
#                                             top_k=config["retriever"]["retrieved_documents"])

# class Retriever(object):
#     _instance = None

#     def __new__(cls, *args, **kwargs):
#         if not cls._instance:
#             cls._instance = super().__new__(cls, *args, **kwargs)
#             cls._instance._initialize()
#         return cls._instance
    
#     def _initialize(self): 
#         self.config_ = config
#         model_manager = ModelManager()
#         self.embedding_model_ = model_manager.embedding_model
#         self.reranker_model_ = model_manager.reranker_model
#         self.alpha_threshold_ = self.config_["retriever"][
#             "alpha_threshold"
#         ]

#     async def _rerank_documents(self, query: str, documents: list[str], k: int, reverse: bool = True) -> list[str]:
#         """
#         Reranks documents using the MxbaiRerankV2 model with custom filtering logic.
#         """
#         # 1. Get ranked results from the mxbai model.
#         # The `rank` method returns a sorted list of dictionaries with scores.
#         # We retrieve all results initially to apply custom thresholds later.
#         results = self.reranker_model_.rank(
#             query=query,
#             documents=documents,
#             return_documents=True,
#             normalize=True,
#         )
#         # 2. Filter the already sorted results based on your score threshold.
#         # The mxbai model output is a list of dicts: [{'text': doc, 'score': score}, ...]
#         docs_scores_sorted = [
#             res for res in results
#             if res.score > self.config_["retriever"]["retriever_threshold"]
#         ]

#         # 3. Apply your custom logic for selecting the top 'k' documents.
#         if docs_scores_sorted:
#             final_docs = []
#             # Check if we have more than 'k' documents and if the k-th score is above 0.06
#             if len(docs_scores_sorted) > k and docs_scores_sorted[k-1].score > 0.06:
#                 # As in your original code, take the top k+3 documents
#                 final_docs = docs_scores_sorted[:k+3]
#             else:
#                 # Otherwise, just take the top k documents
#                 final_docs = docs_scores_sorted[:k]

#             # 4. Extract the document text for the final output.
#             # NOTE: Your original function reversed the list at the end, returning documents
#             # from lowest score to highest. This behavior is replicated here.
#             # If you want the most relevant documents first, remove `reversed()`.
#             if reverse:
#                 sorted_documents = [d.document for d in reversed(final_docs)]
#             else:
#                 sorted_documents = [d.document for d in final_docs]                
#         else:
#             # If no documents meet the threshold, return an empty list.
#             sorted_documents = []
#         return sorted_documents


#     # async def _rerank_documents(self, query, documents, k):
#     #     scores = self.reranker_model_.compute_score([[query, doc] for doc in documents], normalize=True)
#     #     docs_with_scores = [(documents[i], scores[i]) for i in range(len(documents)) if scores[i] > config["retriever"]["retriever_threshold"]]
#     #     if len(docs_with_scores) > 0:
#     #         docs_scores_sorted = sorted(docs_with_scores, key=lambda x: x[1], reverse=True)
#     #         if len(docs_scores_sorted) > k and docs_scores_sorted[k-1][1] > 0.06:
#     #             # TODO: here I want to add all the documents with similarity more that 35 percent
#     #             docs_scores_sorted = [elem for i, elem in enumerate(docs_scores_sorted) if i < k+3]
#     #         else:
#     #             docs_scores_sorted = docs_scores_sorted[:k]
#     #         # conf = mean([d[1] for d in docs_scores_sorted])        
#     #         # TODO: appropriate logger
#     #         sorted_documents = [d[0] for d in reversed(docs_scores_sorted)]
#     #     else:
#     #         sorted_documents = []
#     #     return sorted_documents

#     async def find_vdb(self, database_index): 
#         vectordb_ = Chroma(
#             persist_directory=database_index,
#             embedding_function=self.embedding_model_,
#         )

#         self.retriever_ = vectordb_.as_retriever(
#             search_kwargs={"k": config["retriever"]["retrieved_documents"]}
#         )
        
#     async def retrieve_context(self, query, database_index, k=config["retriever"]["retrieved_rank2_documents"], reverse=True, split=False):
#         # TODO: appropriate logger
#         await self.find_vdb(database_index)
#         documents = await self.retriever_.ainvoke(query)
#         documents = [doc.page_content for doc in documents]
#         sorted_documents = await self._rerank_documents(query, documents, k, reverse=reverse)
#         if split:
#             split_marker = "\n\n ============================================================= \n\n"
#             final_documents = split_marker.join(sorted_documents)
#         else:
#             final_documents = '\n\n'.join(sorted_documents)
#         return final_documents
