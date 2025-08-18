import asyncio
import logging
from statistics import mean
from typing import List, Dict
from dataclasses import dataclass

from FlagEmbedding import FlagReranker
# from mxbai_rerank import MxbaiRerankV2
from langchain.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# from utils import get_config
from .config import config
from .logs import get_logger

logger = get_logger()

@dataclass
class FlagDocument(object):
    document: str
    index: int
    score: float
    
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
                        #   "trust_remote_code": config["embedding_model"]["trust_remote_code"]}
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

        self.alpha_threshold_ = self.config_["retriever"]["alpha_threshold"]

    async def find_vdb(self, database_index):
        """
        Initialize vector database with specified index path.
        
        Args:
            database_index (str): Path to the vector database persist directory
        """
        self.vectordb_ = Chroma(
            persist_directory=database_index,
            embedding_function=self.embedding_model_,
        )

        self.retriever_ = self.vectordb_.as_retriever(
            search_kwargs={"k": config["retriever"]["retrieved_documents"]}
        )

    def _get_retriever(self, module_filter=None, database_index=None):
        """
        Get a retriever with optional module filtering and database selection.
       
        Args:
            module_filter (str, list, or None):
                - None or empty list: No filtering (retrieve from all modules)
                - str: Single module name to filter by
                - list: List of module names to filter by
            database_index (str, optional): Path to vector database
       
        Returns:
            Retriever object with appropriate filtering
        """
        # Use current vectordb if no database_index specified
        vectordb = self.vectordb_
        if database_index:
            vectordb = Chroma(
                persist_directory=database_index,
                embedding_function=self.embedding_model_,
            )
        
        search_kwargs = {"k": self.config_["retriever"]["retrieved_documents"]}
       
        # Apply filtering only if module_filter is provided and not empty
        if module_filter:
            if isinstance(module_filter, str):
                # Single module filter
                search_kwargs["filter"] = {"module": module_filter}
            elif isinstance(module_filter, list) and len(module_filter) > 0:
                # Multiple modules filter using $in operator
                search_kwargs["filter"] = {"module": {"$in": module_filter}}
       
        return vectordb.as_retriever(search_kwargs=search_kwargs)

    async def _rerank_documents_flag(self, query, documents, k, reverse=True):
        """
        Reranks documents using FlagReranker (from develop branch).
        """

        scores = self.reranker_model_.compute_score([[query, doc] for doc in documents], normalize=True)        
        docs_with_scores_index = [FlagDocument(document=documents[i], score=scores[i], index=i) 
                                  for i in range(len(documents)) if scores[i] > config["retriever"]["retriever_threshold"]
                                  ]
        from operator import attrgetter
        # 'attrgetter' creates a function that retrieves the 'score' attribute from an object.
        docs_scores_sorted = sorted(docs_with_scores_index, key=attrgetter('score'), reverse=True)

        if len(docs_with_scores_index) > 0:
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

    # async def _rerank_documents_mxbai(self, query: str, documents: list[str], k: int, reverse: bool = True) -> list[str]:
    #     """
    #     Reranks documents using the MxbaiRerankV2 model with custom filtering logic.
    #     """
    #     # 1. Get ranked results from the mxbai model.
    #     # The `rank` method returns a sorted list of dictionaries with scores.
    #     # We retrieve all results initially to apply custom thresholds later.
    #     results = self.mxbai_reranker_model_.rank(
    #         query=query,
    #         documents=documents,
    #         return_documents=True,
    #         normalize=True,
    #     )
    #     # 2. Filter the already sorted results based on your score threshold.
    #     # The mxbai model output is a list of dicts: [{'text': doc, 'score': score}, ...]
    #     docs_scores_sorted = [
    #         res for res in results
    #         if res.score > self.config_["retriever"]["retriever_threshold"]
    #     ]

    #     # 3. Apply your custom logic for selecting the top 'k' documents.
    #     if docs_scores_sorted:
    #         final_docs = []
    #         # Check if we have more than 'k' documents and if the k-th score is above 0.06
    #         if len(docs_scores_sorted) > k and docs_scores_sorted[k-1].score > 0.06:
    #             # As in your original code, take the top k+3 documents
    #             final_docs = docs_scores_sorted[:k+3]
    #         else:
    #             # Otherwise, just take the top k documents
    #             final_docs = docs_scores_sorted[:k]

    #         # 4. Extract the document text for the final output.
    #         # NOTE: Your original function reversed the list at the end, returning documents
    #         # from lowest score to highest. This behavior is replicated here.
    #         # If you want the most relevant documents first, remove `reversed()`.
    #         if reverse:
    #             sorted_documents = [{"text": d.document, "index": d.index} for d in reversed(final_docs)]
    #         else:
    #             sorted_documents = [{"text": d.document, "index": d.index} for d in final_docs]                
    #     else:
    #         # If no documents meet the threshold, return an empty list.
    #         sorted_documents = [{}]
    #     return sorted_documents
   
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
   
    async def retrieve_context(self, query, database_index=None, k=None, module_filter=None, reverse=True, split=False):
        """
        Retrieve context with optional module filtering and database selection.
       
        Args:
            query (str): The search query
            database_index (str, optional): Path to vector database persist directory
            k (int): Number of documents to return after reranking
            module_filter (str, list, or None):
                - None or empty list: No filtering (retrieve from all modules)
                - str: Single module name to filter by
                - list: List of module names to filter by
            reverse (bool): Whether to reverse the final document order
            split (bool): Whether to join documents with separator or newlines
            use_mxbai (bool): Whether to use MxbaiRerankV2 instead of FlagReranker
       
        Returns:
            str or list: Retrieved and reranked documents
        """
        if k is None:
            k = self.config_["retriever"]["retrieved_rank2_documents"]
       
        # Initialize database if index provided
        
        if database_index:
            await self.find_vdb(database_index)
        
        # Get retriever with or without filtering
        if module_filter:
            retriever = self._get_retriever(module_filter, database_index)
            documents = await retriever.ainvoke(query)
        else:
            # Use standard retriever for backward compatibility
            if not self.retriever_ and database_index:
                await self.find_vdb(database_index)
            documents = await self.retriever_.ainvoke(query)

        # Store original documents for metadata extraction (needed for module filtering)
        original_documents = documents
       
        # Extract page content for reranking
        document_texts = [doc.page_content for doc in documents]
       
        # Choose reranking method

        sorted_documents_with_indices = await self._rerank_documents_flag(query, document_texts, k, reverse)            
        if sorted_documents_with_indices and sorted_documents_with_indices != [{}]:
            final_documents_with_metadata = self.add_module(sorted_documents_with_indices, original_documents)
            return final_documents_with_metadata
        else:
            return sorted_documents_with_indices
            
    async def retrieve_context_by_module(self, query, module_name, database_index=None, k=None, use_mxbai=False):
        """
        Convenience method to retrieve context from a specific module.
       
        Args:
            query (str): The search query
            module_name (str): Name of the module to filter by
            database_index (str, optional): Path to vector database
            k (int): Number of documents to return after reranking
            use_mxbai (bool): Whether to use MxbaiRerankV2
       
        Returns:
            list or str: Retrieved and reranked documents from the specified module
        """
        return await self.retrieve_context(query, database_index=database_index, k=k, module_filter=module_name, use_mxbai=use_mxbai)

    async def retrieve_context_by_modules(self, query, module_names, database_index=None, k=None, use_mxbai=False):
        """
        Convenience method to retrieve context from multiple modules.
       
        Args:
            query (str): The search query
            module_names (list): List of module names to filter by
            database_index (str, optional): Path to vector database
            k (int): Number of documents to return after reranking
            use_mxbai (bool): Whether to use MxbaiRerankV2
       
        Returns:
            list or str: Retrieved and reranked documents from the specified modules
        """
        return await self.retrieve_context(query, database_index=database_index, k=k, module_filter=module_names, use_mxbai=use_mxbai)

    def get_available_modules(self, database_index=None):
        """
        Get list of available modules in the vector database.
        
        Args:
            database_index (str, optional): Path to vector database
       
        Returns:
            list: List of unique module names
        """
        try:
            # Use specified database or current one
            vectordb = self.vectordb_
            if database_index:
                vectordb = Chroma(
                    persist_directory=database_index,
                    embedding_function=self.embedding_model_,
                )
            
            if not vectordb:
                return []
                
            # Get all documents and extract unique modules
            all_docs = vectordb.get()
            modules = set()
            if all_docs and 'metadatas' in all_docs:
                for metadata in all_docs['metadatas']:
                    if metadata and 'module' in metadata:
                        modules.add(metadata['module'])
            return sorted(list(modules))
        except Exception as e:
            print(f"Error getting available modules: {e}")
            return []