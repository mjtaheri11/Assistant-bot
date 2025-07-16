import asyncio
import logging
from statistics import mean
from typing import List, Dict

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

        self.alpha_threshold_ = self.config_["retriever"][
            "alpha_threshold"
        ]

    def _get_retriever(self, module_filter=None):
        """
        Get a retriever with optional module filtering.
        
        Args:
            module_filter (str, list, or None): 
                - None or empty list: No filtering (retrieve from all modules)
                - str: Single module name to filter by
                - list: List of module names to filter by
        
        Returns:
            Retriever object with appropriate filtering
        """
        search_kwargs = {"k": self.config_["retriever"]["retrieved_documents"]}
        
        # Apply filtering only if module_filter is provided and not empty
        if module_filter:
            if isinstance(module_filter, str):
                # Single module filter
                search_kwargs["filter"] = {"module": module_filter}
            elif isinstance(module_filter, list) and len(module_filter) > 0:
                # Multiple modules filter using $in operator
                search_kwargs["filter"] = {"module": {"$in": module_filter}}
        
        return self.vectordb_.as_retriever(search_kwargs=search_kwargs)

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
                sorted_documents = [{"text": d.document, "index": d.index} for d in reversed(final_docs)]
            else:
                sorted_documents = [{"text": d.document, "index": d.index} for d in final_docs]                
        else:
            # If no documents meet the threshold, return an empty list.
            sorted_documents = [{}]
        return sorted_documents
    
    @staticmethod
    def add_module(lst: List, original_documents: List):
        """
        Add module metadata to the retrieved documents.
        
        Args:
            lst: List of documents with indices
            original_documents: Original documents from retriever with metadata
        """
        output_lst = []
        for item in lst:
            if "index" in item and item["index"] < len(original_documents):
                item["module"] = original_documents[item["index"]].metadata.get("module", "unknown")
                item["source"] = original_documents[item["index"]].metadata.get("source", "unknown")
            output_lst.append(item)
        return output_lst
    
    async def retrieve_context(self, query, k=None, module_filter=None):
        """
        Retrieve context with optional module filtering.
        
        Args:
            query (str): The search query
            k (int): Number of documents to return after reranking
            module_filter (str, list, or None): 
                - None or empty list: No filtering (retrieve from all modules)
                - str: Single module name to filter by
                - list: List of module names to filter by
        
        Returns:
            list: Retrieved and reranked documents with metadata
        """
        if k is None:
            k = self.config_["retriever"]["retrieved_rank2_documents"]
        
        # Get retriever with or without filtering
        retriever = self._get_retriever(module_filter)
        documents = await retriever.ainvoke(query)
        
        # Store original documents for metadata extraction
        original_documents = documents
        
        # Extract page content for reranking
        document_texts = [doc.page_content for doc in documents]
        
        # Rerank documents
        sorted_documents_with_indices = await self._rerank_documents(query, document_texts, k)
        
        if sorted_documents_with_indices and sorted_documents_with_indices != [{}]:
            final_documents_with_metadata = self.add_module(sorted_documents_with_indices, original_documents)
            return final_documents_with_metadata
        else:
            return sorted_documents_with_indices

    async def retrieve_context_by_module(self, query, module_name, k=None):
        """
        Convenience method to retrieve context from a specific module.
        
        Args:
            query (str): The search query
            module_name (str): Name of the module to filter by
            k (int): Number of documents to return after reranking
        
        Returns:
            list: Retrieved and reranked documents from the specified module
        """
        return await self.retrieve_context(query, k=k, module_filter=module_name)

    async def retrieve_context_by_modules(self, query, module_names, k=None):
        """
        Convenience method to retrieve context from multiple modules.
        
        Args:
            query (str): The search query
            module_names (list): List of module names to filter by
            k (int): Number of documents to return after reranking
        
        Returns:
            list: Retrieved and reranked documents from the specified modules
        """
        return await self.retrieve_context(query, k=k, module_filter=module_names)

    def get_available_modules(self):
        """
        Get list of available modules in the vector database.
        
        Returns:
            list: List of unique module names
        """
        try:
            # Get all documents and extract unique modules
            all_docs = self.vectordb_.get()
            modules = set()
            if all_docs and 'metadatas' in all_docs:
                for metadata in all_docs['metadatas']:
                    if metadata and 'module' in metadata:
                        modules.add(metadata['module'])
            return sorted(list(modules))
        except Exception as e:
            print(f"Error getting available modules: {e}")
            return []


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

#         self.vectordb_ = Chroma(
#             persist_directory=self.config_["database"][
#                 "persist_directory"
#             ],
#             embedding_function=self.embedding_model_,
#         )

#         self.retriever_ = self.vectordb_.as_retriever(
#             search_kwargs={"k": config["retriever"]["retrieved_documents"]}
#         )

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
#                 sorted_documents = [{"text": d.document, "index": d.index} for d in reversed(final_docs)]
#             else:
#                 sorted_documents = [{"text": d.document, "index": d.index} for d in final_docs]                
#         else:
#             # If no documents meet the threshold, return an empty list.
#             sorted_documents = [{}]
#         return sorted_documents
    
#     @staticmethod
#     def add_module(lst: List):
#         output_lst = []
#         for item in lst:
#             item["module"] = lst[item["index"]]
#             output_lst.append(item)
#         return output_lst
    

#     async def retrieve_context(self, query, k=config["retriever"]["retrieved_rank2_documents"]):
#         # TODO: appropriate logger
#         documents = await self.retriever_.ainvoke(query)
#         # documents = [{"page_content": doc.page_content, "module": doc.metadata["source"]} for doc in documents]
#         documents = [doc.page_content for doc in documents]
#         sorted_documents_with_indices = await self._rerank_documents(query, documents, k)
#         if sorted_documents_with_indices:
#             final_documents_with_metadata = self.add_module(sorted_documents_with_indices)
#             return final_documents_with_metadata
#         else:
#             return sorted_documents_with_indices

















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
