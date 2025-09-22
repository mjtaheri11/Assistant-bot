import asyncio
import logging
from dataclasses import dataclass
from operator import attrgetter
from typing import List

import torch
from FlagEmbedding import FlagReranker
from langchain.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from transformers import AutoModelForCausalLM, AutoTokenizer

from .config import config 

# Assume 'config' and 'get_logger' are defined elsewhere as in the original code.
# For demonstration purposes, here are placeholder implementations:

def get_logger():
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(__name__)

logger = get_logger()

# --- New Qwen Reranker Class ---
class QwenReranker:
    """
    A dedicated class to handle the logic for the Qwen3-Reranker model.
    It provides a `compute_score` method compatible with FlagReranker.
    """
    def __init__(self, model_name: str, device: str = 'cuda', max_length: int = 8192):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side='left')
        # Recommended to use flash_attention_2 for better performance
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            attn_implementation="flash_attention_2"
        ).to(device).eval()
        self.device = device
        self.max_length = max_length

        self.token_false_id = self.tokenizer.convert_tokens_to_ids("no")
        self.token_true_id = self.tokenizer.convert_tokens_to_ids("yes")

        prefix = "<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be \"yes\" or \"no\".<|im_end|>\n<|im_start|>user\n"
        suffix = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
        self.prefix_tokens = self.tokenizer.encode(prefix, add_special_tokens=False)
        self.suffix_tokens = self.tokenizer.encode(suffix, add_special_tokens=False)
        self.instruction = 'Given a web search query, retrieve relevant passages that answer the query'

    def _format_instruction(self, query: str, doc: str) -> str:
        return f"<Instruct>: {self.instruction}\n<Query>: {query}\n<Document>: {doc}"

    def _process_inputs(self, pairs: List[str]):
        max_len = self.max_length - len(self.prefix_tokens) - len(self.suffix_tokens)
        inputs = self.tokenizer(
            pairs, padding=False, truncation='longest_first',
            return_attention_mask=False, max_length=max_len
        )
        for i in range(len(inputs['input_ids'])):
            inputs['input_ids'][i] = self.prefix_tokens + inputs['input_ids'][i] + self.suffix_tokens
        
        inputs = self.tokenizer.pad(inputs, padding=True, return_tensors="pt", max_length=self.max_length)
        for key in inputs:
            inputs[key] = inputs[key].to(self.device)
        return inputs

    @torch.no_grad()
    def _compute_logits(self, inputs) -> List[float]:
        batch_scores = self.model(**inputs).logits[:, -1, :]
        true_vector = batch_scores[:, self.token_true_id]
        false_vector = batch_scores[:, self.token_false_id]
        
        stacked_scores = torch.stack([false_vector, true_vector], dim=1)
        log_softmax_scores = torch.nn.functional.log_softmax(stacked_scores, dim=1)
        
        scores = log_softmax_scores[:, 1].exp().tolist()
        return scores

    def compute_score(self, query_doc_pairs: List[List[str]], normalize: bool = True) -> List[float]:
        """
        Computes relevance scores. The 'normalize' parameter is ignored but kept for API compatibility.
        """
        if not query_doc_pairs:
            return []
        
        query = query_doc_pairs[0][0]
        documents = [pair[1] for pair in query_doc_pairs]
        
        formatted_pairs = [self._format_instruction(query, doc) for doc in documents]
        inputs = self._process_inputs(formatted_pairs)
        return self._compute_logits(inputs)

# --- Original Code (Refactored) ---

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
        )

        # --- Reranker Selection Logic ---
        reranker_choice = config["reranker"]["primary_model"]
        logger.info(f"Initializing primary reranker: {reranker_choice}")

        if reranker_choice == "flag":
            self.reranker_model = FlagReranker(
                config["reranker"]["flag_model"]["model_name"],
                device=config["reranker"]["flag_model"]["device"],
                use_fp16=True
            )
        elif reranker_choice == "qwen":
            self.reranker_model = QwenReranker(
                model_name=config["reranker"]["qwen_model"]["model_name"],
                device=config["reranker"]["qwen_model"]["device"],
                max_length=config["reranker"]["qwen_model"].get("max_length", 8192)
            )
        else:
            raise ValueError(f"Unsupported reranker model in config: '{reranker_choice}'")


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
        # This is now a generic reranker model (either FlagReranker or QwenReranker)
        self.reranker_model_ = model_manager.reranker_model

        self.alpha_threshold_ = self.config_["retriever"]["alpha_threshold"]

    async def find_vdb(self, database_index):
        """
        Initialize vector database with specified index path.
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
        """
        vectordb = None
        if database_index:
            vectordb = Chroma(
                persist_directory=database_index,
                embedding_function=self.embedding_model_,
            )
        elif hasattr(self, 'vectordb_'):
            vectordb = self.vectordb_
        
        if not vectordb:
            raise AttributeError(
                "'Retriever' object has not been initialized. "
                "You must call `find_vdb()` or provide a `database_index` argument."
            )
        
        search_kwargs = {"k": self.config_["retriever"]["retrieved_documents"]}
        
        if module_filter:
            if isinstance(module_filter, str):
                search_kwargs["filter"] = {"module": module_filter}
            elif isinstance(module_filter, list) and len(module_filter) > 0:
                search_kwargs["filter"] = {"module": {"$in": module_filter}}
        
        return vectordb.as_retriever(search_kwargs=search_kwargs)
    
    async def _rerank_documents(self, query, documents, k, reverse=True):
        """
        Reranks documents using the primary reranker model selected in the config.
        """
        scores = self.reranker_model_.compute_score([[query, doc] for doc in documents], normalize=True)
        
        docs_with_scores_index = [
            FlagDocument(document=documents[i], score=scores[i], index=i)
            for i in range(len(documents)) if scores[i] > config["retriever"]["retriever_threshold"]
        ]
        
        docs_scores_sorted = sorted(docs_with_scores_index, key=attrgetter('score'), reverse=True)
        
        if docs_with_scores_index:
            final_docs = []
            if len(docs_scores_sorted) > k and docs_scores_sorted[k-1].score > 0.06:
                final_docs = docs_scores_sorted[:k+3]
            else:
                final_docs = docs_scores_sorted[:k]
            
            if reverse:
                sorted_documents = [{"text": d.document, "index": d.index} for d in reversed(final_docs)]
            else:
                sorted_documents = [{"text": d.document, "index": d.index} for d in final_docs]
        else:
            sorted_documents = []
            
        return sorted_documents

    @staticmethod
    def add_module(lst: List, original_documents: List):
        """
        Add module metadata to the retrieved documents.
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
        """
        if k is None:
            k = self.config_["retriever"]["retrieved_rank2_documents"]
        
        if database_index:
            await self.find_vdb(database_index)
        
        if module_filter:
            retriever = self._get_retriever(module_filter, database_index)
            documents = await retriever.ainvoke(query)
        else:
            if not hasattr(self, 'retriever_') and database_index:
                await self.find_vdb(database_index)
            documents = await self.retriever_.ainvoke(query)

        original_documents = documents
        document_texts = [doc.page_content for doc in documents]
        
        # Generic call to the reranking method
        sorted_documents_with_indices = await self._rerank_documents(query, document_texts, k, reverse)

        if sorted_documents_with_indices:
            return self.add_module(sorted_documents_with_indices, original_documents)
        else:
            return []
            
    async def retrieve_context_by_module(self, query, module_name, database_index=None, k=None):
        return await self.retrieve_context(
            query, database_index=database_index, k=k, module_filter=module_name
        )

    async def retrieve_context_by_modules(self, query, module_names, database_index=None, k=None):
        return await self.retrieve_context(
            query, database_index=database_index, k=k, module_filter=module_names
        )

    def get_available_modules(self, database_index=None):
        """
        Get list of available modules in the vector database.
        """
        try:
            vectordb = self.vectordb_
            if database_index:
                vectordb = Chroma(
                    persist_directory=database_index,
                    embedding_function=self.embedding_model_,
                )
            
            if not vectordb:
                return []
                
            all_docs = vectordb.get()
            modules = set()
            if all_docs and 'metadatas' in all_docs:
                for metadata in all_docs['metadatas']:
                    if metadata and 'module' in metadata:
                        modules.add(metadata['module'])
            return sorted(list(modules))
        except Exception as e:
            logger.error(f"Error getting available modules: {e}")
            return []