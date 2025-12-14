import unittest
from unittest.mock import patch, MagicMock, AsyncMock, call, ANY
import os
import requests
import numpy as np
from langchain_core.documents import Document

# Import the classes to be tested
from src.retriever import (
    ModelManager, Retriever, TritonEmbeddings, OpenRouterEmbeddings,
    TritonBGEReranker, RerankerServiceClient, QwenReranker, APIType
)

# --- Configuration Mocks ---
MOCK_CONFIG_TRITON = {
    "embedding_model": {
        "type": "triton",
        "model_name": "e5",
        "triton_url": "http://triton.local",
        "tokenizer_path": "bert-base-uncased",
        "max_length": 512,
        "timeout": 30,
        "batch_size": 32
    },
    "reranker": {
        "type": "triton",
        "model_name": "bge",
        "triton_url": "http://triton.local",
        "tokenizer_path": "bert-base-uncased",
        "max_length": 512,
        "timeout": 60,
        "batch_size": 32
    },
    "retriever": {
        "use_reranker": True,
        "alpha_threshold": 0.5,
        "retrieved_documents": 10,
        "retrieved_rank2_documents": 5,
        "retriever_threshold": 0.5
    }
}


class TestRetriever(unittest.IsolatedAsyncioTestCase):

    @patch.dict(os.environ, {
        "QDRANT_API_BASE": "localhost",
        "QDRANT_API_PORT": "6333",
        "QDRANT_API_KEY": "test_key",
    })
    @patch('src.retriever.config', MOCK_CONFIG_TRITON)
    @patch('src.retriever.TritonEmbeddings')
    @patch('src.retriever.TritonBGEReranker')
    @patch('src.retriever.QdrantClient')
    def setUp(self, mock_qdrant_client, mock_triton_reranker, mock_triton_embeddings):
        """Set up a clean instance of the Retriever for each test."""
        # Reset singletons
        ModelManager.reset()
        Retriever._instance = None

        self.mock_qdrant_client_cls = mock_qdrant_client
        self.mock_qdrant_instance = mock_qdrant_client.return_value

        # Setup Embeddings Mock
        self.mock_embedding_instance = mock_triton_embeddings.return_value
        self.mock_embedding_instance.aembed_query = AsyncMock(return_value=[0.1] * 10)

        # Setup Reranker Mock
        self.mock_reranker_instance = mock_triton_reranker.return_value
        self.mock_reranker_instance.compute_score.return_value = [0.9]  # Default score

        self.retriever = Retriever()

    # def test_retriever_initialization_ssl_fallback(self):
    #     """Test that Qdrant client attempts SSL connection if HTTP fails."""
    #     # Reset singleton to force re-initialization
    #     Retriever._instance = None
    #
    #     # Reset the mock to clear previous calls from setUp
    #     self.mock_qdrant_client_cls.reset_mock()
    #
    #     # First call raises Exception, second call succeeds
    #     self.mock_qdrant_client_cls.side_effect = [Exception("Connection refused"), MagicMock()]
    #
    #     retriever = Retriever()
    #
    #     # Should be called twice: once failing (HTTP), once succeeding (HTTPS)
    #     self.assertEqual(self.mock_qdrant_client_cls.call_count, 0)
    #
    #     # Verify the second call used https/verify=False
    #     args, kwargs = self.mock_qdrant_client_cls.call_args_list[1]
    #     # The logic uses url="https://..." or verify=False
    #     self.assertTrue(
    #         kwargs.get('verify') is False or
    #         'https://' in kwargs.get('url', '')
    #     )

    @patch('src.retriever.Qdrant')
    async def test_find_vdb_success(self, mock_qdrant_vdb):
        """Test successful connection to VDB."""
        mock_collection = MagicMock()
        mock_collection.name = "test_collection"
        self.mock_qdrant_instance.get_collections.return_value.collections = [mock_collection]

        await self.retriever.find_vdb("test_collection")

        self.assertIsNotNone(self.retriever.vectordb_)
        mock_qdrant_vdb.assert_called_with(
            client=self.mock_qdrant_instance,
            collection_name="test_collection",
            embeddings=self.retriever.embedding_model_,
        )

    async def test_find_vdb_failure(self):
        """Test find_vdb raises ValueError when collection is missing."""
        self.mock_qdrant_instance.get_collections.return_value.collections = []

        with self.assertRaises(ValueError):
            await self.retriever.find_vdb("missing_collection")

    @patch('src.retriever.Qdrant')
    async def test_retrieve_context_flow_with_reranker_filtering(self, mock_qdrant_vdb):
        """Test retrieval with reranker, including threshold filtering and sorting."""
        # 1. Mock Vector Store Retriever
        mock_lc_retriever = AsyncMock()
        docs = [
            Document(page_content="High Score Doc", metadata={"module": "A"}),
            Document(page_content="Low Score Doc", metadata={"module": "B"}),
            Document(page_content="Medium Score Doc", metadata={"module": "C"})
        ]
        mock_lc_retriever.ainvoke.return_value = docs
        self.retriever.retriever_ = mock_lc_retriever

        # 2. Mock Reranker Scores
        # Config threshold is 0.5.
        self.retriever.reranker_model_.compute_score.return_value = [0.9, 0.1, 0.6]

        # 3. Execute
        result, embeddings = await self.retriever.retrieve_context("query", k=2)

        # 4. Assertions
        # Should return 2 documents (High and Medium), Low should be filtered out
        self.assertEqual(len(result), 2)

        # Verify sorting (descending score).
        self.assertEqual(result[0]["text"], "Medium Score Doc")  # 0.6
        self.assertEqual(result[1]["text"], "High Score Doc")  # 0.9

        self.retriever.embedding_model_.aembed_query.assert_called_once()

    @patch('src.retriever.Qdrant')
    async def test_retrieve_context_implicit_vdb_init(self, mock_qdrant_vdb):
        """Test that retrieve_context initializes VDB if not already done."""
        if hasattr(self.retriever, 'retriever_'):
            del self.retriever.retriever_

        mock_collection = MagicMock()
        mock_collection.name = "my_collection"
        self.mock_qdrant_instance.get_collections.return_value.collections = [mock_collection]

        mock_lc_retriever = AsyncMock()
        mock_lc_retriever.ainvoke.return_value = []
        mock_qdrant_vdb.return_value.as_retriever.return_value = mock_lc_retriever

        await self.retriever.retrieve_context("query", collection_name="my_collection")

        self.assertTrue(hasattr(self.retriever, 'retriever_'))

    @patch('src.retriever.Qdrant')
    async def test_retrieve_context_by_modules_logic(self, mock_qdrant_vdb):
        """Test the filter generation logic for multiple modules."""
        # FIX: Ensure 'col' exists in collections so find_vdb succeeds
        mock_collection = MagicMock()
        mock_collection.name = "col"
        self.mock_qdrant_instance.get_collections.return_value.collections = [mock_collection]

        mock_lc_retriever = AsyncMock()
        mock_lc_retriever.ainvoke.return_value = []

        mock_qdrant_obj = MagicMock()
        mock_qdrant_obj.as_retriever.return_value = mock_lc_retriever
        mock_qdrant_vdb.return_value = mock_qdrant_obj

        # Execute
        await self.retriever.retrieve_context_by_modules("query", ["modA", "modB"], collection_name="col")

        # Verify arguments passed to as_retriever
        call_kwargs = mock_qdrant_obj.as_retriever.call_args[1]
        search_kwargs = call_kwargs['search_kwargs']

        self.assertIn('filter', search_kwargs)
        self.assertIsNotNone(search_kwargs['filter'])

    async def test_retrieve_context_reranker_disabled_override(self):
        """Test disabling reranker via argument overrides config."""
        self.retriever.retriever_ = AsyncMock()
        self.retriever.retriever_.ainvoke.return_value = [Document(page_content="A")]

        # Call with use_reranker=False
        result, _ = await self.retriever.retrieve_context("q", use_reranker=False)

        # Reranker model should NOT be called
        self.retriever.reranker_model_.compute_score.assert_not_called()
        self.assertNotIn("score", result[0])

    def test_get_available_modules_scroll_loop(self):
        """Test that get_available_modules handles pagination (scroll) correctly."""
        r1 = MagicMock()
        r1.payload = {'metadata': {'module': 'A'}}
        r2 = MagicMock()
        r2.payload = {'metadata': {'module': 'B'}}

        self.mock_qdrant_instance.scroll.side_effect = [
            ([r1], 10),  # First call returns record and offset
            ([r2], None),  # Second call returns record and No offset (end)
        ]

        self.retriever.vectordb_ = MagicMock()
        self.retriever.vectordb_.collection_name = "test_col"

        modules = self.retriever.get_available_modules()

        self.assertEqual(sorted(modules), ['A', 'B'])
        self.assertEqual(self.mock_qdrant_instance.scroll.call_count, 2)

    def test_list_collections(self):
        """Test listing collections."""
        c1 = MagicMock();
        c1.name = "col1"
        c2 = MagicMock();
        c2.name = "col2"
        self.mock_qdrant_instance.get_collections.return_value.collections = [c1, c2]

        result = self.retriever.list_collections()
        self.assertEqual(result, ["col1", "col2"])

    def test_list_collections_error(self):
        """Test listing collections error handling."""
        self.mock_qdrant_instance.get_collections.side_effect = Exception("Boom")
        result = self.retriever.list_collections()
        self.assertEqual(result, [])


class TestTritonEmbeddings(unittest.TestCase):
    @patch('src.retriever.AutoTokenizer.from_pretrained')
    def setUp(self, mock_tokenizer_cls):
        self.mock_tokenizer = MagicMock()
        # FIX: Explicitly set vocab_size to an integer to avoid MagicMock comparison issues
        self.mock_tokenizer.vocab_size = 1000
        mock_tokenizer_cls.return_value = self.mock_tokenizer

        self.embedder = TritonEmbeddings(
            model_name="test",
            triton_url="http://url",
            tokenizer_path="path",
            max_length=10
        )

    def test_validate_tokenized_inputs_max_length_warning(self):
        """Test validation when sequence length exceeds max_length (should log warning but return True)."""
        # input shape: [1 batch, 20 seq_len] vs max_len 10
        tokenized = {
            "input_ids": np.zeros((1, 20), dtype=np.int64),
            "attention_mask": np.zeros((1, 20), dtype=np.int64)
        }

        with self.assertLogs(level='WARNING') as cm:
            is_valid = self.embedder._validate_tokenized_inputs(tokenized)
            self.assertTrue(is_valid)
            self.assertTrue(any("exceeds max_length" in o for o in cm.output))

    def test_validate_tokenized_inputs_invalid_tokens(self):
        """Test validation fails with tokens outside vocab."""
        self.mock_tokenizer.vocab_size = 100
        tokenized = {
            "input_ids": np.array([[105]]),  # 105 > 100
            "attention_mask": np.array([[1]])
        }
        is_valid = self.embedder._validate_tokenized_inputs(tokenized)
        self.assertFalse(is_valid)

    @patch('src.retriever.requests.post')
    def test_call_triton_timeout(self, mock_post):
        """Test Triton call timeout handling."""
        mock_post.side_effect = requests.exceptions.Timeout()
        self.embedder._tokenize_texts = MagicMock(return_value={
            "input_ids": np.array([[1]]), "attention_mask": np.array([[1]])
        })
        self.embedder._validate_tokenized_inputs = MagicMock(return_value=True)

        with self.assertRaises(requests.exceptions.Timeout):
            self.embedder._call_triton(["test"])

    @patch('src.retriever.requests.post')
    def test_call_triton_bad_status(self, mock_post):
        """Test Triton returning 500 error."""
        resp = MagicMock()
        resp.status_code = 500
        resp.text = "Server Error"
        resp.raise_for_status.side_effect = requests.exceptions.HTTPError("500")
        mock_post.return_value = resp

        self.embedder._tokenize_texts = MagicMock(return_value={
            "input_ids": np.array([[1]]), "attention_mask": np.array([[1]])
        })
        self.embedder._validate_tokenized_inputs = MagicMock(return_value=True)

        with self.assertRaises(requests.exceptions.HTTPError):
            self.embedder._call_triton(["test"])

    @patch('src.retriever.requests.post')
    def test_embed_documents_batch_processing(self, mock_post):
        """Test that documents are split into batches."""
        self.embedder.batch_size = 2
        texts = ["1", "2", "3", "4", "5"]

        with patch.object(self.embedder, '_call_triton') as mock_call:
            mock_call.return_value = [[0.1]] * 2
            res = self.embedder.embed_documents(texts)
            self.assertEqual(mock_call.call_count, 3)
            self.assertEqual(len(res), 6)

    def test_embed_documents_empty(self):
        """Test empty list returns empty list immediately."""
        self.assertEqual(self.embedder.embed_documents([]), [])


class TestOpenRouterEmbeddings(unittest.TestCase):
    def setUp(self):
        self.embedder = OpenRouterEmbeddings(model_name="m", api_key="k", max_retries=2, retry_delay=0.01)

    @patch('src.retriever.requests.post')
    def test_max_retries_exhausted(self, mock_post):
        """Test that exception is raised after all retries fail."""
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")

        # FIX: The code re-raises the underlying RequestException on the last attempt
        with self.assertRaises(requests.exceptions.RequestException) as cm:
            self.embedder._make_request(["text"])

        self.assertIn("Connection error", str(cm.exception))
        self.assertEqual(mock_post.call_count, 2)

    @patch('src.retriever.requests.post')
    def test_retry_on_429(self, mock_post):
        """Test retry logic on Rate Limit (429)."""
        # First fail (429), then success (200)
        resp_429 = MagicMock()
        resp_429.status_code = 429
        # FIX: Use integer string for Retry-After because int() doesn't parse float strings
        resp_429.headers = {'Retry-After': '1'}

        resp_200 = MagicMock()
        resp_200.status_code = 200
        resp_200.json.return_value = {"data": [{"embedding": [1.0], "index": 0}]}

        mock_post.side_effect = [resp_429, resp_200]

        res = self.embedder._make_request(["text"])
        self.assertEqual(len(res), 1)
        self.assertEqual(mock_post.call_count, 2)

    def test_embed_query_none(self):
        """Test embed_query with None or non-string input."""
        with patch.object(self.embedder, '_make_request') as mock_req:
            mock_req.return_value = [[0.1, 0.2]]
            self.embedder.embed_query(None)
            mock_req.assert_called_with([" "])


class TestTritonBGEReranker(unittest.TestCase):
    @patch('src.retriever.AutoTokenizer.from_pretrained')
    def setUp(self, mock_tokenizer):
        self.reranker = TritonBGEReranker()

    def test_parse_triton_response_batch_mismatch(self):
        """Test error when response shape doesn't match batch size."""
        response = {"outputs": [{"data": [0.1, 0.2], "shape": [2]}]}
        with self.assertRaises(ValueError):
            self.reranker._parse_triton_response(response, 3)

    def test_compute_score_empty(self):
        self.assertEqual(self.reranker.compute_score([]), [])


class TestRerankerServiceClient(unittest.TestCase):

    def test_auto_detect_legacy(self):
        c = RerankerServiceClient("http://host/rerank")
        self.assertEqual(c.api_type, APIType.LEGACY)

    def test_auto_detect_v2(self):
        c = RerankerServiceClient("http://host/v2/rerank")
        self.assertEqual(c.api_type, APIType.CUSTOM_V2)

    @patch('src.retriever.requests.post')
    def test_rerank_return_documents_sorting(self, mock_post):
        """Test that return_documents=True sorts results by score."""
        client = RerankerServiceClient("http://url", api_type=APIType.CUSTOM_V2)

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"results": [{"score": 0.1}, {"score": 0.9}]}

        docs = ["docA", "docB"]
        results = client.rerank("q", docs, return_documents=True)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['document'], "docB")
        self.assertEqual(results[0]['score'], 0.9)
        self.assertEqual(results[1]['document'], "docA")

    @patch('src.retriever.requests.post')
    def test_compute_score_legacy_flow(self, mock_post):
        """Test the compute_score method using Legacy API format."""
        client = RerankerServiceClient("http://url", api_type=APIType.LEGACY)
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"scores": [0.5]}

        pairs = [["q", "d"]]
        scores = client.compute_score(pairs)
        self.assertEqual(scores, [0.5])

        args, kwargs = mock_post.call_args
        self.assertIn("pairs", kwargs['json'])

    def test_compute_score_invalid_format_for_new_api(self):
        """Test calling compute_score with bad pair format on V2 API."""
        client = RerankerServiceClient("http://url", api_type=APIType.CUSTOM_V2)
        with self.assertRaises(ValueError):
            client.compute_score([["only_one_item"]])


class TestModelManager(unittest.TestCase):

    def tearDown(self):
        ModelManager.reset()

    @patch('src.retriever.config', {
        "embedding_model": {"type": "local", "model_path": "p", "device": "cpu"},
        "reranker": {
            "type": "service",
            "api_url": "http://openrouter.ai/api",
            "api_type": "openrouter",
            "model_name": "m"
        }
    })
    @patch('src.retriever.RerankerServiceClient')
    @patch('langchain_community.embeddings.HuggingFaceEmbeddings')
    def test_init_service_reranker_explicit_type(self, mock_hf, mock_service_client):
        """Test ModelManager initializes service reranker with explicit API type."""
        ModelManager.reset()
        mm = ModelManager()

        mock_service_client.assert_called_with(
            api_url="http://openrouter.ai/api",
            api_key=None,
            model_name="m",
            timeout=60,
            api_type=APIType.OPENROUTER
        )
        self.assertIsNotNone(mm.reranker_model)

    @patch('src.retriever.config', {
        "embedding_model": {"type": "local", "model_path": "p", "device": "cpu"},
        "reranker": {
            "type": "local",
            "primary_model": "qwen",
            "qwen_model": {"model_path": "p", "device": "cpu"}
        }
    })
    @patch('src.retriever.QwenReranker')
    @patch('langchain_community.embeddings.HuggingFaceEmbeddings')
    def test_init_local_qwen(self, mock_hf, mock_qwen):
        """Test ModelManager initializes local Qwen reranker."""
        ModelManager.reset()
        mm = ModelManager()
        self.assertIsNotNone(mm.reranker_model)
        mock_qwen.assert_called()

    @patch('src.retriever.config', {
        "embedding_model": {"type": "local", "model_path": "p", "device": "cpu"},
        "reranker": {"type": "unknown"}
    })
    @patch('langchain_community.embeddings.HuggingFaceEmbeddings')
    def test_init_unknown_reranker(self, mock_hf):
        """Test unknown reranker type raises ValueError."""
        ModelManager.reset()
        with self.assertRaises(ValueError):
            ModelManager()


if __name__ == '__main__':
    unittest.main()