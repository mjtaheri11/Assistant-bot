import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import os

import numpy as np
from langchain_core.documents import Document

# Import the classes to be tested
from src.retriever import ModelManager, Retriever, TritonEmbeddings, OpenRouterEmbeddings, TritonBGEReranker

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
            "retrieved_rank2_documents": 5
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
    async def test_retrieve_context_with_reranker(self, mock_qdrant_vdb):
        """Test context retrieval with reranking."""
        # Setup mocks
        mock_retriever_instance = AsyncMock()
        mock_documents = [Document(page_content=f"doc {i}") for i in range(5)]
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

class TestOpenRouterEmbeddings(unittest.TestCase):

    def setUp(self):
        self.openrouter_embeddings = OpenRouterEmbeddings(
            model_name="test_model",
            api_key="test_key"
        )

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

class TestTritonBGEReranker(unittest.TestCase):

    @patch('src.retriever.AutoTokenizer.from_pretrained')
    def setUp(self, mock_from_pretrained):
        self.mock_tokenizer = MagicMock()
        mock_from_pretrained.return_value = self.mock_tokenizer
        self.triton_reranker = TritonBGEReranker()

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

if __name__ == '__main__':
    unittest.main()
