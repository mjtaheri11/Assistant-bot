import unittest
import sys
import os
import uuid
from unittest.mock import MagicMock, patch, ANY

# Ensure the root directory is in sys.path to import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cache import Cache
from qdrant_client.http import models as qmodels
from redis.exceptions import RedisError


class TestCache(unittest.TestCase):

    def setUp(self):
        """
        Runs before every test method.
        Resets the Singleton instance to ensure test isolation.
        """
        Cache.reset()

        # Setup common mock objects for dependencies
        self.mock_qdrant_client = MagicMock()
        self.mock_model_manager = MagicMock()
        self.mock_embedding_model = MagicMock()
        self.mock_reranker_model = MagicMock()

        # Configure ModelManager mocks
        self.mock_model_manager.embedding_model = self.mock_embedding_model
        self.mock_model_manager.reranker_model = self.mock_reranker_model

        # Default behavior: Embeddings return a dummy vector
        self.mock_embedding_model.embed_query.return_value = [0.1, 0.2, 0.3]

        # Patch configuration
        self.config_patcher = patch('src.cache.config')
        self.mock_config = self.config_patcher.start()
        self.mock_config.__getitem__.side_effect = lambda x: {"index_name": "test_collection"} if x == "cache" else {}

    def tearDown(self):
        """Runs after every test method."""
        self.config_patcher.stop()
        Cache.reset()

    @patch('src.cache.redis.Redis')
    @patch('src.cache.ModelManager')
    def test_singleton_pattern(self, MockModelManager, MockRedis):
        """Ensure Cache acts as a singleton."""
        MockModelManager.return_value = self.mock_model_manager

        cache1 = Cache()
        cache2 = Cache()

        self.assertIs(cache1, cache2, "Cache should be a singleton instance")
        self.assertTrue(cache1._initialized)

    @patch('src.cache.redis.Redis')
    @patch('src.cache.ModelManager')
    def test_initialize_logic(self, MockModelManager, MockRedis):
        """Test initialization logic including collection creation."""
        MockModelManager.return_value = self.mock_model_manager

        # Initialize Cache with our mock Qdrant client
        cache = Cache(qdrant_client_instance=self.mock_qdrant_client, recreate=True)

        # Verify Redis connection attempted
        MockRedis.assert_called_once()

        # Verify Collection was deleted and created (since recreate=True)
        self.mock_qdrant_client.delete_collection.assert_called_with(collection_name="test_collection")
        self.mock_qdrant_client.create_collection.assert_called()

        # Verify Payload Indices created (query, thumb_up, thumb_down, flag)
        self.assertEqual(self.mock_qdrant_client.create_payload_index.call_count, 4)

    @patch('src.cache.redis.Redis')
    @patch('src.cache.ModelManager')
    def test_initialize_no_redis(self, MockModelManager, MockRedis):
        """Test initialization when Redis is disabled."""
        MockModelManager.return_value = self.mock_model_manager

        cache = Cache(exact_cache=False, qdrant_client_instance=self.mock_qdrant_client)

        self.assertIsNone(cache.redis_db)
        MockRedis.assert_not_called()

    @patch('src.cache.redis.Redis')
    @patch('src.cache.ModelManager')
    def test_get_set_exact_cache(self, MockModelManager, MockRedis):
        """Test Redis get and set operations."""
        MockModelManager.return_value = self.mock_model_manager
        mock_redis_instance = MockRedis.return_value

        cache = Cache(qdrant_client_instance=self.mock_qdrant_client)

        # Test Set
        cache.set_exact_cache("key", "value")
        mock_redis_instance.set.assert_called_with("key", "value")

        # Test Get Hit
        mock_redis_instance.get.return_value = "cached_value"
        result = cache.get_exact_cache("query")
        self.assertEqual(result, "cached_value")

        # Test Get Miss/Error
        mock_redis_instance.get.side_effect = RedisError("Connection failed")
        result = cache.get_exact_cache("query")
        self.assertIsNone(result)

    @patch('src.cache.ModelManager')
    def test_insert_row(self, MockModelManager):
        """Test inserting a row into Qdrant."""
        MockModelManager.return_value = self.mock_model_manager
        cache = Cache(exact_cache=False, qdrant_client_instance=self.mock_qdrant_client)

        query = "test query"
        cache._insert_row(query, "response", "url", 0, 0, 0)

        # Check embedding was generated
        self.mock_embedding_model.embed_query.assert_called_with(query)

        # Check upsert was called
        self.mock_qdrant_client.upsert.assert_called_once()
        call_args = self.mock_qdrant_client.upsert.call_args
        self.assertEqual(call_args.kwargs['collection_name'], "test_collection")

        # Verify Payload
        points = call_args.kwargs['points']
        self.assertEqual(points[0].payload['query'], query)
        self.assertEqual(points[0].payload['response'], "response")

    @patch('src.cache.ModelManager')
    def test_get_embedding_match_single(self, MockModelManager):
        """Test vector search with a single result."""
        MockModelManager.return_value = self.mock_model_manager
        cache = Cache(exact_cache=False, qdrant_client_instance=self.mock_qdrant_client)

        # Mock Search Result
        mock_point = MagicMock()
        mock_point.score = 0.95  # Distance = 1 - 0.95 = 0.05
        mock_point.payload = {"query": "test", "data": "val"}
        self.mock_qdrant_client.search.return_value = [mock_point]

        # Threshold is 0.1. Distance 0.05 <= 0.1, so it should match.
        matches = cache.get_embedding_match("query", threshold=0.1, knn=1)

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], mock_point.payload)

    @patch('src.cache.ModelManager')
    def test_get_embedding_match_rerank(self, MockModelManager):
        """Test vector search with multiple results triggering rerank."""
        MockModelManager.return_value = self.mock_model_manager
        cache = Cache(exact_cache=False, qdrant_client_instance=self.mock_qdrant_client)

        # Mock Search Results (2 hits)
        p1 = MagicMock(score=0.99, payload={"query": "doc1"})
        p2 = MagicMock(score=0.98, payload={"query": "doc2"})
        self.mock_qdrant_client.search.return_value = [p1, p2]

        # Mock Reranker
        # Assume reranker flips the order: doc2 is better than doc1
        self.mock_reranker_model.compute_score.return_value = [0.1, 0.9]  # doc1 score, doc2 score

        matches = cache.get_embedding_match("query", threshold=0.1, knn=2)

        # Reranker should be called
        self.mock_reranker_model.compute_score.assert_called()

        # Verify return order is based on reranker scores (doc2 first)
        self.assertEqual(matches[0]['query'], "doc2")
        self.assertEqual(matches[1]['query'], "doc1")

    @patch('src.cache.ModelManager')
    def test_increment_thumb_up_new_record(self, MockModelManager):
        """Test incrementing thumb up for a new record (creates new row)."""
        MockModelManager.return_value = self.mock_model_manager
        cache = Cache(exact_cache=False, qdrant_client_instance=self.mock_qdrant_client)

        # Mock retrieve returning empty (record doesn't exist)
        self.mock_qdrant_client.retrieve.return_value = []

        cache.increment_thumb_up("new query", "resp", "url")

        # Should call upsert with thumb_up = 1
        self.mock_qdrant_client.upsert.assert_called()
        points = self.mock_qdrant_client.upsert.call_args.kwargs['points']
        self.assertEqual(points[0].payload['thumb_up'], 1)

    @patch('src.cache.ModelManager')
    def test_increment_thumb_up_existing_record(self, MockModelManager):
        """Test incrementing thumb up for existing record (updates row)."""
        MockModelManager.return_value = self.mock_model_manager
        cache = Cache(exact_cache=False, qdrant_client_instance=self.mock_qdrant_client)

        # Mock retrieve returning existing record
        existing_payload = {"query": "q", "thumb_up": 5, "response": "r"}
        mock_point = MagicMock()
        mock_point.payload = existing_payload
        self.mock_qdrant_client.retrieve.return_value = [mock_point]

        cache.increment_thumb_up("q", "r", "u")

        # Should call upsert with thumb_up = 6 (5 + 1)
        points = self.mock_qdrant_client.upsert.call_args.kwargs['points']
        self.assertEqual(points[0].payload['thumb_up'], 6)

    @patch('src.cache.ModelManager')
    def test_filter_documents(self, MockModelManager):
        """Test filtering documents with scroll."""
        MockModelManager.return_value = self.mock_model_manager
        cache = Cache(exact_cache=False, qdrant_client_instance=self.mock_qdrant_client)

        # Mock Scroll results
        p1 = MagicMock(payload={"id": 1})
        # Return tuple (points, next_offset)
        self.mock_qdrant_client.scroll.return_value = ([p1], None)

        filters = {"flag": {"$gte": 1}}
        results = cache.filter_documents(filters)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], 1)

        # Verify Filter construction
        call_args = self.mock_qdrant_client.scroll.call_args
        scroll_filter = call_args.kwargs['scroll_filter']
        self.assertIsInstance(scroll_filter, qmodels.Filter)
        # Check if Range condition was created for $gte
        self.assertTrue(any(isinstance(c.range, qmodels.Range) for c in scroll_filter.must if hasattr(c, 'range')))

    @patch('src.cache.ModelManager')
    def test_delete_document(self, MockModelManager):
        """Test deleting a document."""
        MockModelManager.return_value = self.mock_model_manager
        cache = Cache(exact_cache=False, qdrant_client_instance=self.mock_qdrant_client)

        # Mock existance check
        self.mock_qdrant_client.retrieve.return_value = [MagicMock()]

        cache.delete_document("query_to_delete")

        self.mock_qdrant_client.delete.assert_called_once()
        call_args = self.mock_qdrant_client.delete.call_args
        self.assertEqual(call_args.kwargs['collection_name'], "test_collection")


if __name__ == '__main__':
    unittest.main()