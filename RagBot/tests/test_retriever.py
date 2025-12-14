import unittest
from unittest.mock import patch, MagicMock, AsyncMock, call
import os

import numpy as np
from langchain_core.documents import Document

# Import the classes to be tested
from src.retriever import (
    ModelManager, Retriever, TritonEmbeddings, OpenRouterEmbeddings,
    TritonBGEReranker, RerankerServiceClient, QwenReranker, APIType
)


class TestRetriever(unittest.TestCase):

    @patch.dict(os.environ, {
        "QDRANT_API_BASE": "localhost",
        "QDRANT_API_PORT": "6333",
        "QDRANT_API_KEY": "test_key",
        "OPENROUTER_API_KEY": "or_key",
        "OPENROUTER_MODEL_NAME": "or_model",
    })
    @patch('src.retriever.config', {
        "embedding_model": {
            "type": "local",
            "model_path": "fake/path",
            "device": "cpu"
        },
        "reranker": {
            "type": "local",
            "primary_model": "flag",
            "flag_model": {
                "model_path": "fake/reranker_path",
                "device": "cpu"
            }
        },
        "retriever": {
            "use_reranker": True,
            "alpha_threshold": 0.5,
            "retrieved_documents": 10,
            "retrieved_rank2_documents": 5,
            "retriever_threshold": 0.0
        }
    })
    @patch('langchain_community.embeddings.HuggingFaceEmbeddings')
    @patch('src.retriever.FlagReranker')
    @patch('src.retriever.QdrantClient')
    def setUp(self, mock_qdrant_client, mock_flag_reranker, mock_hf_embeddings):
        """Set up a clean instance of the Retriever for each test."""
        # Reset singletons
        ModelManager._instance = None
        Retriever._instance = None

        self.mock_hf_embeddings = mock_hf_embeddings
        self.mock_flag_reranker = mock_flag_reranker
        self.mock_qdrant_client = mock_qdrant_client

        self.retriever = Retriever()

    def test_retriever_initialization(self):
        """Test the initialization of the Retriever class."""
        self.assertIsNotNone(self.retriever.embedding_model_)
        self.assertIsNotNone(self.retriever.reranker_model_)
        self.assertTrue(self.retriever.use_reranker)
        self.mock_qdrant_client.assert_called_once()

    @patch('src.retriever.Qdrant')
    async def test_find_vdb(self, mock_qdrant_vdb):
        """Test finding and connecting to a Qdrant collection."""
        mock_collection = MagicMock()
        mock_collection.name = "test_collection"
        self.retriever.qdrant_client.get_collections.return_value.collections = [mock_collection]

        await self.retriever.find_vdb("test_collection")

        self.assertIsNotNone(self.retriever.vectordb_)
        self.assertIsNotNone(self.retriever.retriever_)
        mock_qdrant_vdb.assert_called_with(
            client=self.retriever.qdrant_client,
            collection_name="test_collection",
            embeddings=self.retriever.embedding_model_,
        )

    @patch('src.retriever.Qdrant')
    async def test_find_vdb_collection_not_found(self, mock_qdrant_vdb):
        """Test error when collection doesn't exist."""
        self.retriever.qdrant_client.get_collections.return_value.collections = []

        with self.assertRaises(ValueError) as context:
            await self.retriever.find_vdb("nonexistent_collection")

        self.assertIn("not found", str(context.exception))

    @patch('src.retriever.Qdrant')
    async def test_retrieve_context_with_reranker(self, mock_qdrant_vdb):
        """Test context retrieval with reranking."""
        # Setup mocks
        mock_retriever_instance = AsyncMock()
        mock_documents = [Document(page_content=f"doc {i}", metadata={"module": "test", "source": "test.pdf"}) for i in
                          range(5)]
        mock_retriever_instance.ainvoke.return_value = mock_documents
        self.retriever.retriever_ = mock_retriever_instance
        self.retriever.reranker_model_.compute_score.return_value = [0.9, 0.8, 0.7, 0.6, 0.5]
        self.retriever.embedding_model_.aembed_query = AsyncMock(return_value=[0.1] * 10)

        result, _ = await self.retriever.retrieve_context("test query")

        self.assertEqual(len(result), 5)
        self.assertIn("score", result[0])
        self.retriever.reranker_model_.compute_score.assert_called_once()

    @patch('src.retriever.Qdrant')
    async def test_retrieve_context_without_reranker(self, mock_qdrant_vdb):
        """Test context retrieval without reranking."""
        mock_retriever_instance = AsyncMock()
        mock_documents = [Document(page_content=f"doc {i}", metadata={}) for i in range(5)]
        mock_retriever_instance.ainvoke.return_value = mock_documents
        self.retriever.retriever_ = mock_retriever_instance
        self.retriever.embedding_model_.aembed_query = AsyncMock(return_value=[0.1] * 10)

        result, _ = await self.retriever.retrieve_context("test query", use_reranker=False)

        self.assertEqual(len(result), 5)
        self.assertNotIn("score", result[0])
        self.retriever.reranker_model_.compute_score.assert_not_called()

    @patch('src.retriever.Qdrant')
    async def test_retrieve_context_by_module(self, mock_qdrant_vdb):
        """Test context retrieval filtered by module."""
        mock_retriever = AsyncMock()
        mock_documents = [Document(page_content="doc", metadata={"module": "test_module"})]
        mock_retriever.ainvoke.return_value = mock_documents

        with patch.object(self.retriever, '_get_retriever', return_value=mock_retriever):
            self.retriever.embedding_model_.aembed_query = AsyncMock(return_value=[0.1] * 10)
            result, _ = await self.retriever.retrieve_context_by_module("query", "test_module")

            self.assertEqual(len(result), 1)

    @patch('src.retriever.Qdrant')
    async def test_retrieve_context_by_modules(self, mock_qdrant_vdb):
        """Test context retrieval filtered by multiple modules."""
        mock_retriever = AsyncMock()
        mock_documents = [
            Document(page_content="doc1", metadata={"module": "module1"}),
            Document(page_content="doc2", metadata={"module": "module2"})
        ]
        mock_retriever.ainvoke.return_value = mock_documents

        with patch.object(self.retriever, '_get_retriever', return_value=mock_retriever):
            self.retriever.embedding_model_.aembed_query = AsyncMock(return_value=[0.1] * 10)
            result, _ = await self.retriever.retrieve_context_by_modules("query", ["module1", "module2"])

            self.assertEqual(len(result), 2)

    def test_get_available_modules(self):
        """Test getting available modules from a collection."""
        mock_records = [
            MagicMock(payload={'metadata': {'module': 'module1'}}),
            MagicMock(payload={'metadata': {'module': 'module2'}}),
            MagicMock(payload={'metadata': {'module': 'module1'}})
        ]
        self.retriever.qdrant_client.scroll.side_effect = [(mock_records, "next_offset"), ([], None)]

        modules = self.retriever.get_available_modules("test_collection")

        self.assertEqual(sorted(modules), ["module1", "module2"])

    def test_get_available_modules_no_collection(self):
        """Test getting modules when no collection is specified."""
        modules = self.retriever.get_available_modules()
        self.assertEqual(modules, [])

    def test_documents_to_standard_format(self):
        """Test document formatting."""
        docs = [
            Document(page_content="text1", metadata={"module": "mod1", "source": "src1"}),
            Document(page_content="text2", metadata={"module": "mod2", "source": "src2"})
        ]

        result = Retriever._documents_to_standard_format(docs)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["text"], "text1")
        self.assertEqual(result[0]["module"], "mod1")
        self.assertEqual(result[1]["text"], "text2")

    def test_documents_to_standard_format_reverse(self):
        """Test document formatting with reverse."""
        docs = [
            Document(page_content="text1", metadata={}),
            Document(page_content="text2", metadata={})
        ]

        result = Retriever._documents_to_standard_format(docs, reverse=True)

        self.assertEqual(result[0]["text"], "text2")
        self.assertEqual(result[1]["text"], "text1")


class TestTritonEmbeddings(unittest.TestCase):

    @patch('src.retriever.AutoTokenizer.from_pretrained')
    def setUp(self, mock_from_pretrained):
        self.mock_tokenizer = MagicMock()
        mock_from_pretrained.return_value = self.mock_tokenizer
        self.triton_embeddings = TritonEmbeddings(
            model_name="e5",
            triton_url="http://triton-server.admin.svc.cluster.local",
            tokenizer_path="../saved_models/models--intfloat--multilingual-e5-large/snapshots/0dc5580a448e4284468b8909bae50fa925907bc5"
        )

    def test_clean_text(self):
        """Test text cleaning."""
        # Normal text
        self.assertEqual(self.triton_embeddings._clean_text("  hello  world  "), "hello world")
        # Empty text
        self.assertEqual(self.triton_embeddings._clean_text(""), "")
        # None
        self.assertEqual(self.triton_embeddings._clean_text(None), "")
        # Multiple newlines
        self.assertEqual(self.triton_embeddings._clean_text("hello\n\n\nworld"), "hello world")

    def test_tokenize_texts(self):
        """Test text tokenization."""
        self.mock_tokenizer.return_value = {
            "input_ids": np.array([[1, 2, 3]]),
            "attention_mask": np.array([[1, 1, 1]])
        }

        result = self.triton_embeddings._tokenize_texts(["test text"])

        self.assertIn("input_ids", result)
        self.assertIn("attention_mask", result)
        self.mock_tokenizer.assert_called_once()

    def test_validate_tokenized_inputs_valid(self):
        """Test validation of valid inputs."""
        self.mock_tokenizer.vocab_size = 250002
        tokenized = {
            "input_ids": np.array([[1, 2, 3]]),
            "attention_mask": np.array([[1, 1, 1]])
        }

        result = self.triton_embeddings._validate_tokenized_inputs(tokenized)

        self.assertTrue(result)

    def test_validate_tokenized_inputs_shape_mismatch(self):
        """Test validation with shape mismatch."""
        tokenized = {
            "input_ids": np.array([[1, 2, 3]]),
            "attention_mask": np.array([[1, 1]])
        }

        result = self.triton_embeddings._validate_tokenized_inputs(tokenized)

        self.assertFalse(result)

    def test_validate_tokenized_inputs_empty_batch(self):
        """Test validation with empty batch."""
        tokenized = {
            "input_ids": np.array([[]]),
            "attention_mask": np.array([[]])
        }

        result = self.triton_embeddings._validate_tokenized_inputs(tokenized)

        self.assertFalse(result)

    def test_prepare_triton_request(self):
        """Test Triton request preparation."""
        tokenized = {
            "input_ids": np.array([[1, 2, 3]]),
            "attention_mask": np.array([[1, 1, 1]])
        }

        result = self.triton_embeddings._prepare_triton_request(tokenized)

        self.assertIn("inputs", result)
        self.assertEqual(len(result["inputs"]), 2)
        self.assertEqual(result["inputs"][0]["name"], "input_ids")
        self.assertEqual(result["inputs"][1]["name"], "attention_mask")

    def test_parse_triton_response(self):
        """Test parsing Triton response."""
        response = {
            "outputs": [{
                "shape": [2, 5],
                "data": list(range(10))
            }]
        }

        result = self.triton_embeddings._parse_triton_response(response, 2)

        self.assertEqual(result.shape, (2, 5))

    def test_parse_triton_response_invalid(self):
        """Test parsing invalid response."""
        response = {"invalid": "response"}

        with self.assertRaises(ValueError):
            self.triton_embeddings._parse_triton_response(response, 1)

    def test_batch_texts(self):
        """Test text batching."""
        texts = [f"text{i}" for i in range(100)]
        self.triton_embeddings.batch_size = 32

        batches = self.triton_embeddings._batch_texts(texts)

        self.assertEqual(len(batches), 4)  # 32, 32, 32, 4
        self.assertEqual(len(batches[0]), 32)
        self.assertEqual(len(batches[-1]), 4)

    @patch('src.retriever.requests.post')
    def test_call_triton(self, mock_post):
        """Test the _call_triton method."""
        self.mock_tokenizer.return_value = {
            "input_ids": np.array([[1, 2, 3]]),
            "attention_mask": np.array([[1, 1, 1]])
        }
        self.mock_tokenizer.vocab_size = 250002
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "outputs": [{
                "shape": [1, 10],
                "data": list(range(10))
            }]
        }
        mock_post.return_value = mock_response

        embeddings = self.triton_embeddings._call_triton(["test text"])

        self.assertEqual(len(embeddings), 1)
        self.assertEqual(len(embeddings[0]), 10)

    @patch('src.retriever.requests.post')
    def test_call_triton_error(self, mock_post):
        """Test _call_triton with HTTP error."""
        self.mock_tokenizer.return_value = {
            "input_ids": np.array([[1, 2, 3]]),
            "attention_mask": np.array([[1, 1, 1]])
        }
        self.mock_tokenizer.vocab_size = 250002
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        with self.assertRaises(Exception):
            self.triton_embeddings._call_triton(["test text"])

    # @patch('src.retriever.requests.post')
    # def test_embed_documents(self, mock_post):
    #     """Test embedding multiple documents."""
    #     self.mock_tokenizer.return_value = {
    #         "input_ids": np.array([[1, 2, 3]]),
    #         "attention_mask": np.array([[1, 1, 1]])
    #     }
    #     self.mock_tokenizer.vocab_size = 250002
    #     mock_response = MagicMock()
    #     mock_response.status_code = 200
    #     mock_response.json.return_value = {
    #         "outputs": [{
    #             "shape": [1, 10],
    #             "data": list(range(10))
    #         }]
    #     }
    #     mock_post.return_value = mock_response
    #
    #     embeddings = self.triton_embeddings.embed_documents(["text1", "text2", "text3"])
    #
    #     self.assertEqual(len(embeddings), 3)

    @patch('src.retriever.requests.post')
    def test_embed_query(self, mock_post):
        """Test embedding a query."""
        self.mock_tokenizer.return_value = {
            "input_ids": np.array([[1, 2, 3]]),
            "attention_mask": np.array([[1, 1, 1]])
        }
        self.mock_tokenizer.vocab_size = 250002
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "outputs": [{
                "shape": [1, 10],
                "data": list(range(10))
            }]
        }
        mock_post.return_value = mock_response

        embedding = self.triton_embeddings.embed_query("test query")

        self.assertEqual(len(embedding), 10)

    def test_embed_query_invalid(self):
        """Test embedding invalid query."""
        with patch.object(self.triton_embeddings, '_call_triton', return_value=[[0.1] * 10]):
            embedding = self.triton_embeddings.embed_query(None)
            self.assertEqual(len(embedding), 10)


class TestOpenRouterEmbeddings(unittest.TestCase):

    def setUp(self):
        self.openrouter_embeddings = OpenRouterEmbeddings(
            model_name="test_model",
            api_key="test_key"
        )

    def test_clean_text(self):
        """Test text cleaning."""
        self.assertEqual(self.openrouter_embeddings._clean_text("  hello  world  "), "hello world")
        self.assertEqual(self.openrouter_embeddings._clean_text(""), "")
        self.assertEqual(self.openrouter_embeddings._clean_text(None), "")

    def test_clean_text_truncation(self):
        """Test text truncation for long texts."""
        long_text = "a" * 10000
        result = self.openrouter_embeddings._clean_text(long_text)
        self.assertLessEqual(len(result), 8000)

    @patch('src.retriever.requests.post')
    def test_make_request(self, mock_post):
        """Test the _make_request method."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{
                "embedding": list(range(10)),
                "index": 0
            }]
        }
        mock_post.return_value = mock_response

        embeddings = self.openrouter_embeddings._make_request(["test text"])

        self.assertEqual(len(embeddings), 1)
        self.assertEqual(len(embeddings[0]), 10)

    @patch('src.retriever.requests.post')
    def test_make_request_rate_limit(self, mock_post):
        """Test handling rate limit."""
        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {'Retry-After': '1'}

        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {
            "data": [{"embedding": list(range(10)), "index": 0}]
        }

        mock_post.side_effect = [mock_response_429, mock_response_200]

        embeddings = self.openrouter_embeddings._make_request(["test"])

        self.assertEqual(len(embeddings), 1)

    @patch('src.retriever.requests.post')
    def test_make_request_auth_error(self, mock_post):
        """Test handling authentication error."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        with self.assertRaises(ValueError) as context:
            self.openrouter_embeddings._make_request(["test"])

        self.assertIn("Invalid API key", str(context.exception))

    def test_parse_response(self):
        """Test response parsing."""
        response = {
            "data": [
                {"embedding": [0.1, 0.2], "index": 0},
                {"embedding": [0.3, 0.4], "index": 1}
            ]
        }

        result = self.openrouter_embeddings._parse_response(response, 2)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], [0.1, 0.2])

    def test_parse_response_invalid(self):
        """Test parsing invalid response."""
        response = {"invalid": "response"}

        with self.assertRaises(ValueError):
            self.openrouter_embeddings._parse_response(response, 1)

    def test_batch_texts(self):
        """Test text batching."""
        texts = [f"text{i}" for i in range(250)]

        batches = self.openrouter_embeddings._batch_texts(texts)

        self.assertEqual(len(batches), 3)  # 100, 100, 50

    @patch('src.retriever.requests.post')
    def test_embed_documents(self, mock_post):
        """Test embedding documents."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"embedding": list(range(10)), "index": 0}]
        }
        mock_post.return_value = mock_response

        embeddings = self.openrouter_embeddings.embed_documents(["text1"])

        self.assertEqual(len(embeddings), 1)

    @patch('src.retriever.requests.post')
    def test_embed_query(self, mock_post):
        """Test embedding query."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"embedding": list(range(10)), "index": 0}]
        }
        mock_post.return_value = mock_response

        embedding = self.openrouter_embeddings.embed_query("test")

        self.assertEqual(len(embedding), 10)


class TestTritonBGEReranker(unittest.TestCase):

    @patch('src.retriever.AutoTokenizer.from_pretrained')
    def setUp(self, mock_from_pretrained):
        self.mock_tokenizer = MagicMock()
        mock_from_pretrained.return_value = self.mock_tokenizer
        self.triton_reranker = TritonBGEReranker()

    def test_prepare_pairs(self):
        """Test query-document pair preparation."""
        query = "test query"
        documents = ["doc1", "doc2", "doc3"]

        pairs = self.triton_reranker._prepare_pairs(query, documents)

        self.assertEqual(len(pairs), 3)
        self.assertEqual(pairs[0], ["test query", "doc1"])

    def test_tokenize_pairs(self):
        """Test tokenizing pairs."""
        self.mock_tokenizer.return_value = {
            "input_ids": np.array([[1, 2, 3]]),
            "attention_mask": np.array([[1, 1, 1]])
        }

        result = self.triton_reranker._tokenize_pairs([["query", "doc"]])

        self.assertIn("input_ids", result)
        self.assertIn("attention_mask", result)

    def test_prepare_triton_request(self):
        """Test preparing Triton request."""
        tokenized = {
            "input_ids": np.array([[1, 2, 3]]),
            "attention_mask": np.array([[1, 1, 1]])
        }

        result = self.triton_reranker._prepare_triton_request(tokenized)

        self.assertIn("inputs", result)
        self.assertEqual(len(result["inputs"]), 2)

    def test_parse_triton_response_flat(self):
        """Test parsing flat response."""
        response = {
            "outputs": [{
                "data": [0.9, 0.8, 0.7]
            }]
        }

        result = self.triton_reranker._parse_triton_response(response, 3)

        self.assertEqual(len(result), 3)

    def test_parse_triton_response_2d(self):
        """Test parsing 2D response."""
        response = {
            "outputs": [{
                "data": [0.9, 0.8, 0.7]
            }]
        }

        result = self.triton_reranker._parse_triton_response(response, 3)

        self.assertEqual(len(result), 3)

    @patch('src.retriever.requests.post')
    def test_call_triton(self, mock_post):
        """Test the _call_triton method for the reranker."""
        self.mock_tokenizer.return_value = {
            "input_ids": np.array([[1, 2, 3]]),
            "attention_mask": np.array([[1, 1, 1]])
        }
        self.mock_tokenizer.vocab_size = 250002
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "outputs": [{
                "data": [0.9]
            }]
        }
        mock_post.return_value = mock_response

        scores = self.triton_reranker._call_triton([["query", "doc"]])

        self.assertEqual(len(scores), 1)
        self.assertIsInstance(scores[0], float)

    def test_batch_pairs(self):
        """Test batching pairs."""
        pairs = [[f"q{i}", f"d{i}"] for i in range(100)]
        self.triton_reranker.batch_size = 32

        batches = self.triton_reranker._batch_pairs(pairs)

        self.assertEqual(len(batches), 4)

    @patch('src.retriever.requests.post')
    def test_compute_score(self, mock_post):
        """Test computing scores."""
        self.mock_tokenizer.return_value = {
            "input_ids": np.array([[1, 2, 3]]),
            "attention_mask": np.array([[1, 1, 1]])
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "outputs": [{"data": [0.9]}]
        }
        mock_post.return_value = mock_response

        scores = self.triton_reranker.compute_score([["query", "doc"]], normalize=True)

        self.assertEqual(len(scores), 1)

    @patch('src.retriever.requests.post')
    def test_compute_score_no_normalize(self, mock_post):
        """Test computing scores without normalization."""
        self.mock_tokenizer.return_value = {
            "input_ids": np.array([[1, 2, 3]]),
            "attention_mask": np.array([[1, 1, 1]])
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "outputs": [{"data": [0.9]}]
        }
        mock_post.return_value = mock_response

        scores = self.triton_reranker.compute_score([["query", "doc"]], normalize=False)

        self.assertEqual(len(scores), 1)


class TestRerankerServiceClient(unittest.TestCase):

    def test_detect_api_type_custom_v2(self):
        """Test API type detection for custom v2."""
        client = RerankerServiceClient(api_url="http://api.com/v2/rerank")
        self.assertEqual(client.api_type, APIType.CUSTOM_V2)

    def test_detect_api_type_openrouter(self):
        """Test API type detection for OpenRouter."""
        client = RerankerServiceClient(api_url="https://openrouter.ai/api/v1/rerank")
        self.assertEqual(client.api_type, APIType.OPENROUTER)

    def test_detect_api_type_legacy(self):
        """Test API type detection for legacy."""
        client = RerankerServiceClient(api_url="http://api.com/rerank")
        self.assertEqual(client.api_type, APIType.LEGACY)

    def test_get_headers_openrouter(self):
        """Test header generation for OpenRouter."""
        client = RerankerServiceClient(
            api_url="https://openrouter.ai/api",
            api_key="test_key",
            api_type=APIType.OPENROUTER
        )
        headers = client._get_headers()
        self.assertEqual(headers["Authorization"], "test_key")

    def test_format_request_custom_v2(self):
        """Test request formatting for custom v2."""
        client = RerankerServiceClient(
            api_url="http://api.com/v2/rerank",
            model_name="test_model"
        )
        payload = client._format_request_custom_v2("query", ["doc1", "doc2"], top_n=1)

        self.assertEqual(payload["query"], "query")
        self.assertEqual(len(payload["documents"]), 2)
        self.assertEqual(payload["top_n"], 1)

    def test_format_request_openrouter(self):
        """Test request formatting for OpenRouter."""
        client = RerankerServiceClient(
            api_url="https://openrouter.ai/api",
            model_name="test_model",
            api_type=APIType.OPENROUTER
        )
        payload = client._format_request_openrouter("query", ["doc1"], top_n=1)

        self.assertIn("query", payload)
        self.assertIn("documents", payload)

    def test_format_request_legacy(self):
        """Test request formatting for legacy."""
        client = RerankerServiceClient(
            api_url="http://api.com/rerank",
            api_type=APIType.LEGACY
        )
        payload = client._format_request_legacy([["q", "d"]], normalize=True)

        self.assertIn("pairs", payload)
        self.assertEqual(payload["normalize"], True)

    @patch('src.retriever.requests.post')
    def test_rerank_custom_v2(self, mock_post):
        """Test reranking with custom v2 API."""
        client = RerankerServiceClient(
            api_url="http://api.com/v2/rerank",
            api_type=APIType.CUSTOM_V2
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{"relevance_score": 0.9}, {"relevance_score": 0.8}]
        }
        mock_post.return_value = mock_response

        scores = client.rerank("query", ["doc1", "doc2"])

        self.assertEqual(len(scores), 2)

    @patch('src.retriever.requests.post')
    def test_rerank_with_documents(self, mock_post):
        """Test reranking returning documents."""
        client = RerankerServiceClient(
            api_url="http://api.com/v2/rerank",
            api_type=APIType.CUSTOM_V2
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "scores": [0.9, 0.8]
        }
        mock_post.return_value = mock_response

        result = client.rerank("query", ["doc1", "doc2"], return_documents=True)

        self.assertEqual(len(result), 2)
        self.assertIn("document", result[0])
        self.assertIn("score", result[0])

    @patch('src.retriever.requests.post')
    def test_compute_score_legacy(self, mock_post):
        """Test compute_score with legacy API."""
        client = RerankerServiceClient(
            api_url="http://api.com/rerank",
            api_type=APIType.LEGACY
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"scores": [0.9]}
        mock_post.return_value = mock_response

        scores = client.compute_score([["query", "doc"]])

        self.assertEqual(len(scores), 1)

    def test_compute_score_conversion(self):
        """Test compute_score converting to new API format."""
        client = RerankerServiceClient(
            api_url="http://api.com/v2/rerank",
            api_type=APIType.CUSTOM_V2
        )

        with patch.object(client, 'rerank', return_value=[0.9, 0.8]) as mock_rerank:
            scores = client.compute_score([["query", "doc1"], ["query", "doc2"]])
            mock_rerank.assert_called_once()

    @patch('src.retriever.requests.post')
    def test_rerank_batch(self, mock_post):
        """Test batch reranking."""
        client = RerankerServiceClient(
            api_url="http://api.com/v2/rerank",
            api_type=APIType.CUSTOM_V2
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"scores": [0.9]}
        mock_post.return_value = mock_response

        results = client.rerank_batch(["q1", "q2"], [["d1"], ["d2"]])

        self.assertEqual(len(results), 2)


class TestQwenReranker(unittest.TestCase):

    @patch('src.retriever.AutoTokenizer.from_pretrained')
    @patch('src.retriever.AutoModelForCausalLM.from_pretrained')
    def setUp(self, mock_model, mock_tokenizer):
        self.mock_tokenizer_instance = MagicMock()
        self.mock_model_instance = MagicMock()

        mock_tokenizer.return_value = self.mock_tokenizer_instance
        mock_model.return_value = self.mock_model_instance

        self.mock_tokenizer_instance.convert_tokens_to_ids.side_effect = lambda x: {"no": 0, "yes": 1}[x]
        self.mock_tokenizer_instance.encode.return_value = [1, 2, 3]
        self.mock_model_instance.to.return_value = self.mock_model_instance
        self.mock_model_instance.eval.return_value = self.mock_model_instance

        self.qwen_reranker = QwenReranker(model_path="test_model")

    def test_format_instruction(self):
        """Test instruction formatting."""
        result = self.qwen_reranker._format_instruction("query", "doc")

        self.assertIn("query", result)
        self.assertIn("doc", result)
        self.assertIn("Instruct", result)

    def test_process_inputs(self):
        """Test input processing."""
        self.mock_tokenizer_instance.return_value = {
            "input_ids": [[1, 2, 3]]
        }
        self.mock_tokenizer_instance.pad.return_value = {
            "input_ids": MagicMock(to=lambda x: MagicMock())
        }

        result = self.qwen_reranker._process_inputs(["test"])

        self.assertIsNotNone(result)

    @patch('torch.no_grad')
    def test_compute_score(self, mock_no_grad):
        """Test score computation."""
        mock_no_grad.return_value.__enter__ = MagicMock()
        mock_no_grad.return_value.__exit__ = MagicMock()

        self.mock_tokenizer_instance.return_value = {
            "input_ids": [[1, 2, 3]]
        }
        self.mock_tokenizer_instance.pad.return_value = {
            "input_ids": MagicMock(to=lambda x: MagicMock())
        }

        # Mock model output
        import torch
        mock_logits = torch.tensor([[0.1, 0.9]])
        self.mock_model_instance.return_value = MagicMock(logits=mock_logits)

        with patch.object(self.qwen_reranker, '_process_inputs', return_value={}):
            with patch.object(self.qwen_reranker, '_compute_logits', return_value=[0.9]):
                scores = self.qwen_reranker.compute_score([["query", "doc"]])
                self.assertEqual(len(scores), 1)


class TestModelManager(unittest.TestCase):

    def tearDown(self):
        """Reset singleton after each test."""
        ModelManager._instance = None

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key", "OPENROUTER_MODEL_NAME": "test_model"})
    @patch('src.retriever.config', {
        "embedding_model": {"type": "triton", "model_name": "e5", "triton_url": "http://triton-server.admin.svc.cluster.local",
                            "tokenizer_path": "../saved_models/models--intfloat--multilingual-e5-large/snapshots/0dc5580a448e4284468b8909bae50fa925907bc5", "max_length": 8192, "timeout": 30, "batch_size": 32},
        "reranker": {"type": "triton", "model_name": "bge", "triton_url": "http://triton-server.admin.svc.cluster.local"
                     ,"max_length": 8192, "timeout": 60, "batch_size": 32}
    })
    @patch('src.retriever.AutoTokenizer.from_pretrained')
    def test_initialization_triton(self, mock_tokenizer):
        """Test ModelManager initialization with Triton."""
        mock_tokenizer.return_value = MagicMock()
        ModelManager.reset()
        manager = ModelManager()

        self.assertIsInstance(manager.embedding_model, TritonEmbeddings)
        self.assertIsInstance(manager.reranker_model, TritonBGEReranker)

    @patch('src.retriever.config', {
        "embedding_model": {"type": "local", "model_path": "test/path", "device": "cpu"},
        "reranker": {"type": "local", "primary_model": "flag",
                     "flag_model": {"model_path": "test/path", "device": "cpu"}}
    })

    @patch('src.retriever.config', {
        "embedding_model": {"type": "invalid_type"},
        "reranker": {"type": "triton", "model_name": "bge"}
    })
    def test_invalid_embedding_type(self):
        """Test error with invalid embedding type."""
        with self.assertRaises(OSError):
            ModelManager()

    @patch('src.retriever.config', {
        "embedding_model": {"type": "local", "model_path": "test", "device": "cpu"},
        "reranker": {"type": "invalid_type"}
    })
    @patch('langchain_community.embeddings.HuggingFaceEmbeddings')
    def test_invalid_reranker_type(self, mock_hf):
        """Test error with invalid reranker type."""
        with self.assertRaises(ValueError):
            ModelManager()


if __name__ == '__main__':
    unittest.main()