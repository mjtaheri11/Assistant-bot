import os
import logging
from dataclasses import dataclass
from typing import Tuple
import requests
import numpy as np

import torch
from FlagEmbedding import FlagReranker
from langchain_core.embeddings import Embeddings
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient, models
from transformers import AutoModelForCausalLM, AutoTokenizer
# --- Other Service Classes (Custom, Cohere, etc.) ---

from typing import List, Optional, Union, Dict, Any
from enum import Enum

import time

from .config import config 

def get_logger():
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(__name__)

HEADER_KEY_APPLICATION_JSON = "application/json"
logger = get_logger()

class TritonEmbeddings(Embeddings):
    """
    Embedding client for Triton Inference Server.
    Handles tokenization locally and sends tokenized inputs to Triton.
    """
    def __init__(
        self,
        model_name: str,
        triton_url: str,
        tokenizer_path: str,
        max_length: int = 512,
        timeout: int = 30,
        batch_size: int = 32
    ):
        """
        Initialize Triton embedding client.
        
        Args:
            model_name: Model name in Triton (e.g., "e5", "bge")
            triton_url: Base URL of Triton server
            tokenizer_path: HuggingFace tokenizer to use for preprocessing
            max_length: Maximum sequence length
            timeout: Request timeout in seconds
            batch_size: Maximum batch size for inference
        """
        self.model_name = model_name
        self.triton_url = triton_url.rstrip('/')
        self.infer_url = f"{self.triton_url}/v2/models/{model_name}/infer"
        self.max_length = max_length
        self.timeout = timeout
        self.batch_size = batch_size
        
        # Load tokenizer locally
        logger.info(f"Loading tokenizer: {tokenizer_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        
        logger.info(f"✅ Initialized Triton embedding client for model '{model_name}' at {self.triton_url}")

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Clean and validate text before tokenization.
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Strip whitespace
        text = text.strip()
        
        # Replace multiple spaces/newlines with single space
        import re
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def _tokenize_texts(self, texts: List[str]) -> Dict[str, np.ndarray]:
        """
        Tokenize texts and prepare inputs for Triton.
        
        Returns:
            Dictionary with 'input_ids' and 'attention_mask' as numpy arrays
        """
        # Clean texts
        cleaned_texts = [self._clean_text(text) for text in texts]
        
        # Filter out empty texts
        non_empty_texts = [text if text else "[EMPTY]" for text in cleaned_texts]
        try:
            # Tokenize all texts
            encoded = self.tokenizer(
                non_empty_texts,
                padding=True,
                truncation=True,
                max_length=self.max_length,
                return_tensors="np",
                add_special_tokens=True
            )
            
            return {
                "input_ids": encoded["input_ids"].astype(np.int64),
                "attention_mask": encoded["attention_mask"].astype(np.int64)
            }
        except Exception as e:
            logger.error(f"Error tokenizing texts: {e}")
            logger.error(f"Sample texts (first 100 chars): {[t[:100] for t in non_empty_texts[:3]]}")
            raise
    
    def _validate_tokenized_inputs(self, tokenized_inputs: Dict[str, np.ndarray]) -> bool:
        """
        Validate tokenized inputs before sending to Triton.
        """
        try:
            input_ids = tokenized_inputs["input_ids"]
            attention_mask = tokenized_inputs["attention_mask"]
            # Check shapes match
            if input_ids.shape != attention_mask.shape:
                logger.error(f"Shape mismatch: input_ids {input_ids.shape} vs attention_mask {attention_mask.shape}")
                return False
            
            # Check batch size
            batch_size = input_ids.shape[0]
            if batch_size == 0:
                logger.error("Batch size is 0")
                return False
            
            # Check sequence length
            seq_length = input_ids.shape[1]
            if seq_length == 0:
                logger.error("Sequence length is 0")
                return False
            
            if seq_length > self.max_length:
                logger.warning(f"Sequence length {seq_length} exceeds max_length {self.max_length}")
                # This is actually okay because we truncate, but log it
            
            # Check for invalid token IDs
            vocab_size = self.tokenizer.vocab_size
            if np.any(input_ids >= vocab_size) or np.any(input_ids < 0):
                logger.error(f"Invalid token IDs found. Vocab size: {vocab_size}, "
                           f"Min ID: {input_ids.min()}, Max ID: {input_ids.max()}")
                return False
            
            logger.debug(f"Validation passed: batch_size={batch_size}, seq_length={seq_length}")
            return True
            
        except Exception as e:
            logger.error(f"Error validating inputs: {e}")
            return False

    @staticmethod
    def _prepare_triton_request(tokenized_inputs: Dict[str, np.ndarray]) -> Dict:
        """
        Prepare Triton inference request payload.
        """
        batch_size, seq_length = tokenized_inputs["input_ids"].shape
        
        # Convert to lists for JSON serialization
        input_ids_list = tokenized_inputs["input_ids"].flatten().tolist()
        attention_mask_list = tokenized_inputs["attention_mask"].flatten().tolist()
        
        payload = {
            "inputs": [
                {
                    "name": "input_ids",
                    "shape": [batch_size, seq_length],
                    "datatype": "INT64",
                    "data": input_ids_list
                },
                {
                    "name": "attention_mask",
                    "shape": [batch_size, seq_length],
                    "datatype": "INT64",
                    "data": attention_mask_list
                }
            ]
        }
        
        logger.debug(f"Prepared Triton request: batch_size={batch_size}, seq_length={seq_length}")
        return payload

    @staticmethod
    def _parse_triton_response(response_json: Dict, expected_batch_size: int) -> np.ndarray:
        """
        Parse Triton inference response and extract embeddings.
        """
        if "outputs" not in response_json:
            raise ValueError(f"Invalid Triton response: missing 'outputs' key. Response: {response_json}")
        
        if len(response_json["outputs"]) == 0:
            raise ValueError("Triton response has empty outputs array")
        
        output = response_json["outputs"][0]
        
        if "shape" not in output or "data" not in output:
            raise ValueError(f"Invalid output format: {output}")
        
        shape = output["shape"]
        data = output["data"]
        
        logger.debug(f"Triton response shape: {shape}, data length: {len(data)}")
        
        # Validate shape
        if len(shape) != 2:
            raise ValueError(f"Expected 2D output shape, got {len(shape)}D: {shape}")
        
        if shape[0] != expected_batch_size:
            raise ValueError(f"Batch size mismatch: expected {expected_batch_size}, got {shape[0]}")
        
        # Reshape flat data array to [batch_size, embedding_dim]
        try:
            embeddings = np.array(data, dtype=np.float32).reshape(shape)
            return embeddings
        except Exception as e:
            logger.error(f"Error reshaping embeddings: {e}")
            logger.error(f"Data length: {len(data)}, Expected shape: {shape}")
            raise
    
    def _call_triton(self, texts: List[str]) -> List[List[float]]:
        """
        Call Triton inference server with tokenized texts.
        """
        if not texts:
            logger.warning("Empty texts list provided to _call_triton")
            return []
        
        batch_size = len(texts)
        logger.debug(f"Calling Triton with {batch_size} texts")
        
        try:
            # Tokenize inputs
            tokenized = self._tokenize_texts(texts)
            
            # Validate tokenized inputs
            if not self._validate_tokenized_inputs(tokenized):
                raise ValueError("Tokenized inputs validation failed")
            
            # Prepare Triton request
            payload = self._prepare_triton_request(tokenized)
            
            # Log request details for debugging
            logger.debug(f"Sending request to: {self.infer_url}")
            logger.debug(f"Request payload size: {len(str(payload))} chars")
            
            # Make request
            response = requests.post(
                self.infer_url,
                json=payload,
                headers={"Content-Type": HEADER_KEY_APPLICATION_JSON},
                timeout=self.timeout
            )
            
            # Check for HTTP errors
            if response.status_code != 200:
                logger.error(f"Triton returned status code {response.status_code}")
                logger.error(f"Response text: {response.text}")
                response.raise_for_status()
            
            # Parse response
            result = response.json()
            embeddings = self._parse_triton_response(result, batch_size)
            
            logger.debug(f"Successfully got embeddings: {embeddings.shape}")
            return embeddings.tolist()
            
        except requests.exceptions.Timeout:
            logger.error(f"Triton request timed out after {self.timeout}s")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Triton server: {e}")
            logger.error(f"Request URL: {self.infer_url}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in _call_triton: {e}")
            logger.error(f"Batch size: {batch_size}")
            logger.error(f"Sample text (first 200 chars): {texts[0][:200] if texts else 'N/A'}")
            raise
    
    def _batch_texts(self, texts: List[str]) -> List[List[str]]:
        """
        Split texts into batches to avoid overwhelming the server.
        """
        if not texts:
            return []
        return [texts[i:i + self.batch_size] for i in range(0, len(texts), self.batch_size)]
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple documents, processing in batches if necessary.
        """
        if not texts:
            logger.warning("Empty texts list provided to embed_documents")
            return []
        
        logger.info(f"Embedding {len(texts)} documents in batches of {self.batch_size}")
        
        # Process in batches
        batches = self._batch_texts(texts)
        all_embeddings = []
        
        for batch_idx, batch in enumerate(batches):
            try:
                logger.debug(f"Processing batch {batch_idx + 1}/{len(batches)} ({len(batch)} texts)")
                batch_embeddings = self._call_triton(batch)
                all_embeddings.extend(batch_embeddings)
                logger.debug(f"✅ Batch {batch_idx + 1}/{len(batches)} completed")
            except Exception as e:
                logger.error(f"❌ Error processing batch {batch_idx + 1}/{len(batches)}: {e}")
                # Log problematic texts
                for i, text in enumerate(batch):
                    logger.error(f"  Text {i}: {text[:100]}... (length: {len(text)})")
                raise
        
        logger.info(f"✅ Successfully embedded {len(texts)} documents")
        return all_embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query text.
        """
        if not text or not isinstance(text, str):
            logger.warning(f"Invalid query text: {text}")
            text = ""
        
        logger.debug(f"Embedding query (length: {len(text)})")
        embeddings = self._call_triton([text])
        return embeddings[0]



class OpenRouterEmbeddings(Embeddings):
    """
    Embedding client for OpenRouter API.
    Handles direct text embedding without local tokenization.
    """
    
    def __init__(
        self,
        model_name: str,
        api_key: str,
        api_base: str = "https://openrouter.ai/api/v1",
        batch_size: int = 100,
        max_retries: int = 3,
        retry_delay: int = 1,
        timeout: int = 30,
        **kwargs
    ):
        """
        Initialize OpenRouter embedding client.
        
        Args:
            model_name: Model identifier (e.g., "openai/text-embedding-3-small")
            api_key: OpenRouter API key
            api_base: Base URL for OpenRouter API
            batch_size: Maximum texts per request
            max_retries: Maximum retry attempts for failed requests
            retry_delay: Delay between retries in seconds
            timeout: Request timeout in seconds
            **kwargs: Additional parameters to pass in requests
        """
        self.model_name = model_name
        self.api_key = api_key
        self.api_base = api_base.rstrip('/')
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.extra_params = kwargs
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": HEADER_KEY_APPLICATION_JSON,
            "HTTP-Referer": kwargs.get("app_name", "langchain-app"),  # Optional app identifier
        }
        
        logger.info(f"✅ Initialized OpenRouter embedding client for model '{model_name}'")

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Clean and validate text before sending to API.
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Strip whitespace
        text = text.strip()
        
        # Replace multiple spaces/newlines with single space
        import re
        text = re.sub(r'\s+', ' ', text)
        
        # Ensure text is not too long (OpenRouter has limits)
        max_chars = 8000  # Conservative limit
        if len(text) > max_chars:
            logger.warning(f"Text truncated from {len(text)} to {max_chars} characters")
            text = text[:max_chars]
        
        return text
    
    def _make_request(self, texts: List[str]) -> List[List[float]]:
        """
        Make embedding request to OpenRouter API with retry logic.
        """
        cleaned_texts = [self._clean_text(text) for text in texts]
        non_empty_texts = [text if text else " " for text in cleaned_texts]  # OpenRouter needs non-empty
        
        payload = {
            "model": self.model_name,
            "input": non_empty_texts,
            **self.extra_params
        }
        
        url = f"{self.api_base}/embeddings"
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Sending request to OpenRouter (attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return self._parse_response(result, len(non_empty_texts))
                
                elif response.status_code == 429:  # Rate limit
                    retry_after = int(response.headers.get('Retry-After', self.retry_delay))
                    logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                    
                elif response.status_code == 401:
                    raise ValueError("Invalid API key")
                    
                else:
                    logger.error(f"OpenRouter returned status {response.status_code}: {response.text}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    response.raise_for_status()
                    
            except requests.exceptions.Timeout:
                logger.error(f"Request timed out (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                raise
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                raise
        
        raise Exception(f"Failed after {self.max_retries} attempts")

    @staticmethod
    def _parse_response(response: Dict[str, Any], expected_count: int) -> List[List[float]]:
        """
        Parse OpenRouter API response.
        
        Expected format:
        {
            "data": [
                {"embedding": [0.1, 0.2, ...], "index": 0},
                {"embedding": [0.3, 0.4, ...], "index": 1},
                ...
            ],
            "model": "...",
            "usage": {...}
        }
        """
        if "data" not in response:
            raise ValueError(f"Invalid response format: missing 'data' key. Response: {response}")
        
        data = response["data"]
        
        if len(data) != expected_count:
            raise ValueError(f"Expected {expected_count} embeddings, got {len(data)}")
        
        # Sort by index to ensure correct order
        sorted_data = sorted(data, key=lambda x: x.get("index", 0))
        
        embeddings = []
        for item in sorted_data:
            if "embedding" not in item:
                raise ValueError(f"Invalid embedding item: {item}")
            embeddings.append(item["embedding"])
        
        # Log usage if available
        if "usage" in response:
            usage = response["usage"]
            logger.debug(f"Token usage - Prompt: {usage.get('prompt_tokens', 'N/A')}, "
                        f"Total: {usage.get('total_tokens', 'N/A')}")
        
        return embeddings
    
    def _batch_texts(self, texts: List[str]) -> List[List[str]]:
        """
        Split texts into batches.
        """
        if not texts:
            return []
        return [texts[i:i + self.batch_size] for i in range(0, len(texts), self.batch_size)]
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple documents.
        """
        if not texts:
            logger.warning("Empty texts list provided")
            return []
        
        logger.info(f"Embedding {len(texts)} documents in batch es of {self.batch_size}")
        
        batches = self._batch_texts(texts)
        all_embeddings = []
        
        for batch_idx, batch in enumerate(batches):
            try:
                logger.debug(f"Processing batch {batch_idx + 1}/{len(batches)} ({len(batch)} texts)")
                batch_embeddings = self._make_request(batch)
                all_embeddings.extend(batch_embeddings)
                logger.debug(f"✅ Batch {batch_idx + 1}/{len(batches)} completed")
                
            except Exception as e:
                logger.error(f"❌ Error processing batch {batch_idx + 1}: {e}")
                raise
        
        logger.info(f"✅ Successfully embedded {len(texts)} documents")
        return all_embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query text.
        """
        if not text or not isinstance(text, str):
            logger.warning(f"Invalid query text: {text}")
            text = " "
        
        logger.debug(f"Embedding query (length: {len(text)})")
        embeddings = self._make_request([text])
        return embeddings[0]

        
# --- Triton BGE/Flag Reranker Client ---
class TritonBGEReranker:
    """
    BGE/Flag Reranker client for Triton Inference Server.
    This is the default service-based reranker that uses the BGE reranker model via Triton.
    """
    def __init__(
        self,
        model_name: str = "bge",
        triton_url: str = "http://triton-server.admin.svc.cluster.local",
        tokenizer_path: str = "BAAI/bge-reranker-large",
        max_length: int = 512,
        timeout: int = 60,
        batch_size: int = 32
    ):
        """
        Initialize Triton BGE reranker client.
        
        Args:
            model_name: Model name in Triton (typically "bge" for BGE reranker)
            triton_url: Base URL of Triton server
            tokenizer_path: HuggingFace tokenizer for preprocessing
            max_length: Maximum sequence length
            timeout: Request timeout in seconds
            batch_size: Maximum batch size for inference
        """
        self.model_name = model_name
        self.triton_url = triton_url.rstrip('/')
        self.infer_url = f"{self.triton_url}/v2/models/{model_name}/infer"
        self.max_length = max_length
        self.timeout = timeout
        self.batch_size = batch_size
        
        # Load tokenizer
        logger.info(f"Loading BGE reranker tokenizer: {tokenizer_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        
        logger.info(f"✅ Initialized Triton BGE reranker client for model '{model_name}' at {self.triton_url}")

    @staticmethod
    def _prepare_pairs(query: str, documents: List[str]) -> List[str]:
        """
        Prepare query-document pairs for reranking.
        BGE reranker expects concatenated pairs: [query, document]
        """
        return [[query, doc] for doc in documents]
    
    def _tokenize_pairs(self, pairs: List[List[str]]) -> Dict[str, np.ndarray]:
        """
        Tokenize query-document pairs for BGE reranker.
        The tokenizer will handle the pair formatting automatically.
        """
        # Tokenize pairs - the tokenizer will add [CLS] query [SEP] doc [SEP] format
        encoded = self.tokenizer(
            pairs,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="np"
        )
        
        return {
            "input_ids": encoded["input_ids"].astype(np.int64),
            "attention_mask": encoded["attention_mask"].astype(np.int64)
        }

    @staticmethod
    def _prepare_triton_request(tokenized_inputs: Dict[str, np.ndarray]) -> Dict:
        """
        Prepare Triton inference request payload.
        """
        batch_size, seq_length = tokenized_inputs["input_ids"].shape
        
        return {
            "inputs": [
                {
                    "name": "input_ids",
                    "shape": [batch_size, seq_length],
                    "datatype": "INT64",
                    "data": tokenized_inputs["input_ids"].flatten().tolist()
                },
                {
                    "name": "attention_mask",
                    "shape": [batch_size, seq_length],
                    "datatype": "INT64",
                    "data": tokenized_inputs["attention_mask"].flatten().tolist()
                }
            ]
        }

    @staticmethod
    def _parse_triton_response(response_json: Dict, batch_size: int) -> np.ndarray:
        """
        Parse Triton inference response and extract relevance scores.
        """
        if "outputs" not in response_json:
            raise ValueError(f"Invalid Triton response: {response_json}")
        
        output = response_json["outputs"][0]
        data = output["data"]
        
        # The output should be scores for each query-document pair
        # Shape could be [batch_size] or [batch_size, 1]
        scores = np.array(data)
        
        # If shape is [batch_size, 1], flatten it
        if len(scores.shape) > 1 and scores.shape[1] == 1:
            scores = scores.flatten()
        elif len(scores) != batch_size:
            # Reshape based on expected batch size
            scores = scores.reshape(batch_size, -1)
            if scores.shape[1] == 1:
                scores = scores.flatten()
            else:
                # Take the first column or max if multiple outputs
                scores = scores[:, 0]
        
        return scores
    
    def _call_triton(self, pairs: List[List[str]]) -> List[float]:
        """
        Call Triton for batch reranking.
        """
        # Tokenize pairs
        tokenized = self._tokenize_pairs(pairs)
        
        # Prepare Triton request
        payload = self._prepare_triton_request(tokenized)
        
        batch_size = len(pairs)
        
        try:
            response = requests.post(
                self.infer_url,
                json=payload,
                headers={"Content-Type": HEADER_KEY_APPLICATION_JSON},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            scores = self._parse_triton_response(result, batch_size)
            
            return scores.tolist()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Triton BGE reranker: {e}")
            raise
    
    def _batch_pairs(self, pairs: List[List[str]]) -> List[List[List[str]]]:
        """
        Split pairs into batches.
        """
        return [pairs[i:i + self.batch_size] for i in range(0, len(pairs), self.batch_size)]
    
    def compute_score(
        self, 
        query_doc_pairs: List[List[str]], 
        normalize: bool = True
    ) -> List[float]:
        """
        Compute relevance scores for query-document pairs.
        Compatible with FlagReranker and QwenReranker interface.
        
        Args:
            query_doc_pairs: List of [query, document] pairs
            normalize: Whether to normalize scores (applies sigmoid)
            
        Returns:
            List of relevance scores
        """
        if not query_doc_pairs:
            return []
        
        # Process in batches if necessary
        batches = self._batch_pairs(query_doc_pairs)
        all_scores = []
        
        for batch in batches:
            batch_scores = self._call_triton(batch)
            all_scores.extend(batch_scores)
        
        # Normalize scores using sigmoid if requested
        if normalize:
            all_scores = [1 / (1 + np.exp(-score)) for score in all_scores]
        
        return all_scores


class APIType(Enum):
    """Enum to distinguish between different API types."""
    CUSTOM_V2 = "custom_v2"  # Your new custom API
    OPENROUTER = "openrouter"
    LEGACY = "legacy"  # Your current format with pairs

class RerankerServiceClient:
    """Universal reranker service client supporting multiple API formats."""
    
    def __init__(
        self,
        api_url: str,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: int = 60,
        api_type: Optional[Union[APIType, str]] = None
    ):
        self.api_url = api_url
        self.api_key = api_key or os.getenv("RERANKER_SERVICE_API_KEY")
        self.model_name = model_name
        self.timeout = timeout
        
        # Auto-detect API type based on URL if not specified
        if api_type is None:
            self.api_type = self._detect_api_type(api_url)
        elif isinstance(api_type, str):
            self.api_type = APIType(api_type)
        else:
            self.api_type = api_type

    @staticmethod
    def _detect_api_type(url: str) -> APIType:
        """Detect API type based on URL patterns."""
        if "/v2/rerank" in url:
            return APIType.CUSTOM_V2
        elif "openrouter.ai" in url:
            return APIType.OPENROUTER
        else:
            return APIType.LEGACY
            
    def _get_headers(self) -> Dict[str, str]:
        """Get appropriate headers based on API type."""
        headers = {"Content-Type": HEADER_KEY_APPLICATION_JSON}
        
        if self.api_type == APIType.OPENROUTER and self.api_key:
            # OpenRouter typically uses different header format
            headers["Authorization"] = self.api_key
            headers["HTTP-Referer"] = "https://your-app.com"  # Optional but recommended
        elif self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        return headers
    
    def _format_request_custom_v2(
        self, 
        query: str, 
        documents: List[str], 
        top_n: Optional[int] = None
    ) -> Dict[str, Any]:
        """Format request for custom V2 API."""
        payload = {
            "query": query,
            "documents": documents
        }
        
        if self.model_name:
            payload["model"] = self.model_name
            
        if top_n is not None:
            payload["top_n"] = top_n
            
        return payload
    
    def _format_request_openrouter(
        self, 
        query: str, 
        documents: List[str], 
        top_n: Optional[int] = None
    ) -> Dict[str, Any]:
        """Format request for OpenRouter API."""
        # OpenRouter reranking format (adjust based on their actual API)
        payload = {
            "model": self.model_name or "default-reranker",
            "query": query,
            "documents": documents
        }
        
        if top_n is not None:
            payload["top_k"] = top_n  # OpenRouter might use top_k instead
            
        return payload
    
    def _format_request_legacy(
        self, 
        query_doc_pairs: List[List[str]], 
        normalize: bool = True
    ) -> Dict[str, Any]:
        """Format request for legacy API (current format)."""
        payload = {
            "pairs": query_doc_pairs,
            "normalize": normalize
        }
        
        if self.model_name:
            payload["model"] = self.model_name
            
        return payload
    
    def _parse_response(self, response_data: Any) -> List[float]:
        """Parse response based on API type."""
        if self.api_type == APIType.CUSTOM_V2:
            # Custom V2 API might return scores with indices
            if isinstance(response_data, dict):
                if "results" in response_data:
                    # Extract scores from results
                    return [item.get("relevance_score", item.get("score", 0.0)) 
                            for item in response_data["results"]]
                elif "scores" in response_data:
                    return response_data["scores"]
                    
        elif self.api_type == APIType.OPENROUTER:
            # OpenRouter format (adjust based on actual response)
            if isinstance(response_data, dict):
                if "data" in response_data:
                    return [item.get("relevance_score", item.get("score", 0.0)) 
                            for item in response_data["data"]]
                elif "results" in response_data:
                    return response_data["results"]
                    
        # Legacy or general parsing
        if "scores" in response_data:
            return response_data["scores"]
        elif "data" in response_data:
            return [item["score"] for item in response_data["data"]]
        elif isinstance(response_data, list):
            return response_data
        else:
            raise ValueError(f"Unexpected response format: {response_data}")
    
    def rerank(
        self,
        query: str,
        documents: List[str],
        top_n: Optional[int] = None,
        return_documents: bool = False
    ) -> Union[List[float], List[Dict[str, Any]]]:
        """
        Rerank documents based on query (for custom V2 and OpenRouter APIs).
        
        Args:
            query: The search query
            documents: List of documents to rerank
            top_n: Return only top N results
            return_documents: If True, return documents with scores
            
        Returns:
            List of scores or list of dicts with documents and scores
        """
        if self.api_type == APIType.LEGACY:
            raise ValueError("Use compute_score method for legacy API")
            
        if self.api_type == APIType.CUSTOM_V2:
            payload = self._format_request_custom_v2(query, documents, top_n)
        elif self.api_type == APIType.OPENROUTER:
            payload = self._format_request_openrouter(query, documents, top_n)
        else:
            raise ValueError(f"Unsupported API type: {self.api_type}")
            
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            scores = self._parse_response(result)
            
            if return_documents:
                # Return documents with their scores
                doc_scores = []
                for i, (doc, score) in enumerate(zip(documents, scores)):
                    doc_scores.append({
                        "document": doc,
                        "score": score,
                        "index": i
                    })
                # Sort by score descending and limit to top_n if specified
                doc_scores.sort(key=lambda x: x["score"], reverse=True)
                if top_n:
                    doc_scores = doc_scores[:top_n]
                return doc_scores
            else:
                return scores
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling reranker service: {e}")
            raise
    
    def compute_score(
        self, 
        query_doc_pairs: List[List[str]], 
        normalize: bool = True
    ) -> List[float]:
        """
        Legacy method for computing scores with query-document pairs.
        Kept for backward compatibility.
        """
        if not query_doc_pairs:
            return []
            
        if self.api_type in [APIType.CUSTOM_V2, APIType.OPENROUTER]:
            # Convert pairs format to new format
            # Assuming pairs are [query, document]
            if len(query_doc_pairs) > 0 and len(query_doc_pairs[0]) == 2:
                query = query_doc_pairs[0][0]  # Use first query
                documents = [pair[1] for pair in query_doc_pairs]
                return self.rerank(query, documents)
            else:
                raise ValueError("Invalid query_doc_pairs format for new API")
                
        # Use legacy format
        payload = self._format_request_legacy(query_doc_pairs, normalize)
            
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return self._parse_response(result)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling reranker service: {e}")
            raise
            
    def rerank_batch(
        self,
        queries: List[str],
        documents_list: List[List[str]],
        top_n: Optional[int] = None
    ) -> List[List[float]]:
        """
        Batch reranking for multiple queries.
        
        Args:
            queries: List of queries
            documents_list: List of document lists (one per query)
            top_n: Return only top N results per query
            
        Returns:
            List of score lists
        """
        results = []
        for query, documents in zip(queries, documents_list):
            scores = self.rerank(query, documents, top_n)
            results.append(scores)
        return results


# --- Local Qwen Reranker (unchanged) ---
class QwenReranker:
    """Local Qwen reranker model."""
    def __init__(self, model_path: str, device: str = 'cuda', max_length: int = 8192):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, padding_side='left')
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
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

    def compute_score(self, query_doc_pairs: List[List[str]]) -> List[float]:
        if not query_doc_pairs:
            return []
        
        query = query_doc_pairs[0][0]
        documents = [pair[1] for pair in query_doc_pairs]
        
        formatted_pairs = [self._format_instruction(query, doc) for doc in documents]
        inputs = self._process_inputs(formatted_pairs)
        return self._compute_logits(inputs)


# --- ModelManager with Triton BGE as Default ---
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
        # --- Embedding Model Selection ---
        embedding_config = config["embedding_model"]
        embedding_type = embedding_config.get("type")  # Default to Triton
        if embedding_type == "triton":
            # Triton Inference Server
            self.embedding_model = TritonEmbeddings(         
                model_name=embedding_config.get("model_name"),
                triton_url=embedding_config.get("triton_url"),
                tokenizer_path=embedding_config.get("tokenizer_path"),
                max_length=embedding_config.get("max_length"),
                timeout=embedding_config.get("timeout"),
                batch_size=embedding_config.get("batch_size")
            )
            logger.info("✅ Initialized Triton embedding model")
            
        elif embedding_type == "local":
            # Local model
            from langchain_community.embeddings import HuggingFaceEmbeddings
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=embedding_config["model_path"],
                model_kwargs={"device": embedding_config["device"]}
            )
            logger.info("✅ Initialized local HuggingFace embedding model")

        elif embedding_type == "openrouter":
            self.embedding_model = OpenRouterEmbeddings(
                model_name=os.getenv("OPENROUTER_MODEL_NAME"),  # or any other model
                api_key=os.getenv("OPENROUTER_API_KEY"),
                batch_size=100
            )
        else:
            raise ValueError(f"Unsupported embedding type: '{embedding_type}'")

        # --- Reranker Model Selection ---
        reranker_config = config["reranker"]
        reranker_type = reranker_config.get("type", "triton")  # Default to Triton
        if reranker_type == "triton":
            # Triton BGE/Flag Reranker - DEFAULT SERVICE-BASED RERANKER
            self.reranker_model = TritonBGEReranker(
                model_name=reranker_config.get("model_name"),
                triton_url=reranker_config.get("triton_url", "http://triton-server.admin.svc.cluster.local"),
                tokenizer_path=reranker_config.get("tokenizer_path", "BAAI/bge-reranker-large"),
                max_length=reranker_config.get("max_length", 512),
                timeout=reranker_config.get("timeout", 60),
                batch_size=reranker_config.get("batch_size", 32)
            )
            logger.info("✅ Initialized Triton BGE reranker model (default service-based reranker)")
            
        elif reranker_type == "service":
            # External reranker service with multiple API format support
            api_url = reranker_config["api_url"]
            
            # Determine API type from config or auto-detect
            api_type_str = reranker_config.get("api_type")  # Can be "custom_v2", "openrouter", "legacy", or None
            
            if api_type_str:
                # Explicit API type from config
                try:
                    api_type = APIType(api_type_str)
                except ValueError:
                    logger.warning(f"Unknown api_type '{api_type_str}', will auto-detect from URL")
                    api_type = None
            else:
                # Auto-detect from URL
                api_type = None
            
            # Initialize the reranker service client
            self.reranker_model = RerankerServiceClient(
                api_url=api_url,
                api_key=reranker_config.get("api_key"),
                model_name=reranker_config.get("model_name"),
                timeout=reranker_config.get("timeout", 60),
                api_type=api_type  # Will auto-detect if None
            )
            
            # Log the detected/specified API type for debugging
            detected_type = self.reranker_model.api_type.value
            logger.info(f"✅ Initialized reranker service client (API type: {detected_type})")
            
            # Log additional info based on API type
            if self.reranker_model.api_type == APIType.CUSTOM_V2:
                logger.info(f"   Using Custom V2 API at: {api_url}")
                logger.info(f"   Model: {reranker_config.get('model_name', 'default')}")
            elif self.reranker_model.api_type == APIType.OPENROUTER:
                logger.info(f"   Using OpenRouter API at: {api_url}")
                logger.info(f"   Model: {reranker_config.get('model_name', 'default')}")
            elif self.reranker_model.api_type == APIType.LEGACY:
                logger.info(f"   Using Legacy API format at: {api_url}")

        elif reranker_type == "local":
            # Local reranker models
            primary_model = reranker_config.get("primary_model", "flag")
            
            if primary_model == "flag":
                self.reranker_model = FlagReranker(
                    reranker_config["flag_model"]["model_path"],
                    device=reranker_config["flag_model"]["device"],
                    use_fp16=True
                )
                logger.info("✅ Initialized local FlagReranker model")
                
            elif primary_model == "qwen":
                self.reranker_model = QwenReranker(
                    model_name=reranker_config["qwen_model"]["model_path"],
                    device=reranker_config["qwen_model"]["device"],
                    max_length=reranker_config["qwen_model"].get("max_length", 8192)
                )
                logger.info("✅ Initialized local QwenReranker model")
                
            else:
                raise ValueError(f"Unsupported local reranker model: '{primary_model}'")
                
        else:
            raise ValueError(f"Unsupported reranker type: '{reranker_type}'")

    @classmethod
    def reset(cls):
        """
        Resets the singleton instance.
        This forces the next instantiation to re-run _initialize().
        """
        if cls._instance:
            # Optional: Explicitly delete heavy model references to aid Garbage Collection
            if hasattr(cls._instance, 'embedding_model'):
                del cls._instance.embedding_model
            if hasattr(cls._instance, 'reranker_model'):
                del cls._instance.reranker_model

            # Reset the instance to None
            cls._instance = None
            logger.info("♻️ ModelManager singleton has been reset.")

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
        
        # Make reranker optional - check if it's enabled in config
        self.use_reranker = self.config_.get("retriever", {}).get("use_reranker", True)
        if self.use_reranker:
            self.reranker_model_ = model_manager.reranker_model
        else:
            self.reranker_model_ = None
            logger.info("⚠️ Reranker is disabled in configuration")

        self.alpha_threshold_ = self.config_["retriever"]["alpha_threshold"]
        
        # Initialize Qdrant client
        self.qdrant_host = os.getenv("QDRANT_API_BASE")
        self.qdrant_port = os.getenv("QDRANT_API_PORT")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        try:
            self.qdrant_client = QdrantClient(
                host=self.qdrant_host,
                port=self.qdrant_port,
                api_key=self.qdrant_api_key,
                timeout=60,
                prefer_grpc=False,
                https=False,
            )
            logger.info("✅ Connected to Qdrant via HTTP (no SSL)")
        except Exception as e:
            logger.warning(f"⚠️ HTTP connection failed, trying with SSL: {e}")
            self.qdrant_client = QdrantClient(
                url=f"https://{self.qdrant_host}:{self.qdrant_port}",
                api_key=self.qdrant_api_key,
                timeout=60,
                verify=False,
            )

    async def find_vdb(self, collection_name: str):
        try:
            collections = self.qdrant_client.get_collections().collections
            collection_exists = any(c.name == collection_name for c in collections)
            
            if not collection_exists:
                logger.warning(f"Collection '{collection_name}' does not exist in Qdrant.")
                raise ValueError(f"Collection '{collection_name}' not found")
            
            self.vectordb_ = Qdrant(
                client=self.qdrant_client,
                collection_name=collection_name,
                embeddings=self.embedding_model_,
            )
            self.retriever_ = self.vectordb_.as_retriever(
                search_kwargs={"k": config["retriever"]["retrieved_documents"]}
            )
            logger.info(f"✅ Successfully connected to Qdrant collection: {collection_name}")
            
        except Exception as e:
            logger.error(f"❌ Error initializing Qdrant collection '{collection_name}': {e}")
            raise

    def _get_retriever(self, module_filter=None, collection_name=None):
        vectordb = None
        if collection_name:
            vectordb = Qdrant(
                client=self.qdrant_client,
                collection_name=collection_name,
                embeddings=self.embedding_model_,
            )
        elif hasattr(self, 'vectordb_'):
            vectordb = self.vectordb_
        
        if not vectordb:
            raise AttributeError(
                "'Retriever' object has not been initialized. "
                "You must call `find_vdb()` or provide a `collection_name` argument."
            )
        
        search_kwargs = {"k": self.config_["retriever"]["retrieved_documents"]}
        
        if module_filter:
            if isinstance(module_filter, str):
                search_kwargs["filter"] = models.Filter(
                    must=[
                        models.FieldCondition(
                            key="metadata.module",
                            match=models.MatchValue(value=module_filter)
                        )
                    ]
                )
            elif isinstance(module_filter, list) and len(module_filter) > 0:
                search_kwargs["filter"] = models.Filter(
                    should=[
                        models.FieldCondition(
                            key="metadata.module",
                            match=models.MatchValue(value=module)
                        )
                        for module in module_filter
                    ]
                )
        
        return vectordb.as_retriever(search_kwargs=search_kwargs)

    @staticmethod
    def _documents_to_standard_format(documents, reverse=False):
        """
        Convert Document objects to a standardized dictionary format.
        This ensures consistent output whether reranking is used or not.
        """
        formatted_docs = []
        for idx, doc in enumerate(documents):
            formatted_doc = {
                "text": doc.page_content,
                "index": idx,
                "module": doc.metadata.get("module", "unknown"),
                "source": doc.metadata.get("source", "unknown"),
                "metadata": doc.metadata  # Keep full metadata for potential future use
            }
            formatted_docs.append(formatted_doc)
        
        if reverse:
            formatted_docs.reverse()
        
        return formatted_docs
    
    async def _rerank_documents(self, query, documents, k, reverse=True):
        """
        Rerank documents and return in standardized format.
        """
        document_texts = [doc.page_content for doc in documents]
        scores = self.reranker_model_.compute_score(
            [[query, text] for text in document_texts], 
            normalize=True
        )
        
        if not isinstance(scores, list):
            scores = [scores]
        
        # Filter by threshold and create scored documents
        docs_with_scores = []
        threshold = self.config_["retriever"].get("retriever_threshold", 0.0)
        
        for i, (doc, score) in enumerate(zip(documents, scores)):
            if score > threshold:
                docs_with_scores.append({
                    "document": doc,
                    "score": score,
                    "index": i
                })
        
        # Sort by score
        docs_with_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Determine how many documents to keep
        if docs_with_scores:
            if len(docs_with_scores) > k and docs_with_scores[k-1]["score"] > 0.06:
                final_docs = docs_with_scores[:k+3]
            else:
                final_docs = docs_with_scores[:k]
            
            # Convert to standard format
            result = []
            for doc_info in final_docs:
                original_doc = doc_info["document"]
                formatted_doc = {
                    "text": original_doc.page_content,
                    "index": doc_info["index"],
                    "module": original_doc.metadata.get("module", "unknown"),
                    "source": original_doc.metadata.get("source", "unknown"),
                    "score": doc_info["score"],  # Include score for reranked docs
                    "metadata": original_doc.metadata
                }
                result.append(formatted_doc)
            
            if reverse:
                result.reverse()
            
            return result
        else:
            return []
    
    async def retrieve_context(self, query, collection_name=None, k=None, 
                              module_filter=None, reverse=True, use_reranker=None) -> Tuple[List, List]:
        """
        Retrieve context with optional reranking.
        
        Args:
            query: Search query
            collection_name: Optional collection name
            k: Number of documents to return
            module_filter: Optional module filter(s)
            reverse: Whether to reverse the final order
            use_reranker: Override the default reranker setting (True/False/None)
        """
        # 1. OPTIMIZATION: Generate embedding ONCE here.
        # This takes ~500ms. We will pass this vector to the DB to avoid re-calculating it.
        query_embedding = await self.embedding_model_.aembed_query(query)

        if k is None:
            k = self.config_["retriever"]["retrieved_rank2_documents"]
        
        # Determine whether to use reranker for this call
        should_use_reranker = self.use_reranker if use_reranker is None else use_reranker
        
        if collection_name:
            await self.find_vdb(collection_name)
        
        # Retrieve documents
        if module_filter:
            retriever = self._get_retriever(module_filter, collection_name)
            documents = await retriever.ainvoke(query)
        else:
            if not hasattr(self, 'retriever_') and collection_name:
                await self.find_vdb(collection_name)
            documents = await self.retriever_.ainvoke(query)
        
        # Apply reranking or just format the documents
        if should_use_reranker and self.reranker_model_ is not None:
            # Use reranker
            logger.debug(f"Using reranker for query: {query[:50]}...")
            result = await self._rerank_documents(query, documents, k, reverse)
        else:
            # No reranking - just format and potentially limit documents
            logger.debug(f"Skipping reranker for query: {query[:50]}...")
            result = self._documents_to_standard_format(documents[:k], reverse)
        
        return result, query_embedding
    
    async def retrieve_context_by_module(self, query, module_name, 
                                        collection_name=None, k=None, use_reranker=None):
        """
        Retrieve context filtered by a single module.
        """
        return await self.retrieve_context(
            query, 
            collection_name=collection_name, 
            k=k, 
            module_filter=module_name,
            use_reranker=use_reranker
        )

    async def retrieve_context_by_modules(self, query, module_names, 
                                         collection_name=None, k=None, use_reranker=None):
        """
        Retrieve context filtered by multiple modules.
        """
        return await self.retrieve_context(
            query, 
            collection_name=collection_name, 
            k=k, 
            module_filter=module_names,
            use_reranker=use_reranker
        )

    def get_available_modules(self, collection_name: Optional[str] = None) -> List[str]:
        try:
            if collection_name:
                target_collection = collection_name
            elif hasattr(self, 'vectordb_') and self.vectordb_:
                target_collection = self.vectordb_.collection_name
            else:
                logger.warning("No collection specified and no default collection initialized")
                return []
            
            modules = set()
            offset = None
            limit = 100
            
            while True:
                records, offset = self.qdrant_client.scroll(
                    collection_name=target_collection,
                    limit=limit,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )
                
                if not records:
                    break
                
                for record in records:
                    if record.payload and 'metadata' in record.payload:
                        metadata = record.payload['metadata']
                        if isinstance(metadata, dict) and 'module' in metadata:
                            modules.add(metadata['module'])
                
                if offset is None:
                    break
            
            return sorted(modules)
            
        except Exception as e:
            logger.error(f"Error getting available modules: {e}")
            return []

    def list_collections(self) -> List[str]:
        try:
            collections = self.qdrant_client.get_collections().collections
            return [c.name for c in collections]
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
