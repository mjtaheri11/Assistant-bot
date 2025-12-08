import unittest
from unittest.mock import patch, MagicMock, ANY
import uuid
from redis.exceptions import RedisError

from src.cache import Cache, REDIS_HOST, REDIS_PORT


@patch('src.cache.qdrant_client', new_callable=MagicMock)
@patch('src.cache.ModelManager', new_callable=MagicMock)
@patch('src.cache.redis.Redis', new_callable=MagicMock)
@patch('src.cache.config', {'cache': {'index_name': 'test_collection', 'num_rank2_documents': 3}})
class TestCache(unittest.TestCase):

    def setUp(self):
        """Set up mocks and reset the Cache singleton before each test."""
        # Reset singleton instance to ensure test isolation
        Cache._instance = None

        # Get the mocks from the patches - they're available as test method parameters
        # but we need to access them differently in setUp

        # We'll set up the cache in each test method instead, or use setUpClass
        # For now, we can just reset the instance
        pass

    def _setup_cache(self, mock_redis_class, mock_model_manager_class, mock_qdrant_client):
        """Helper method to set up cache with mocks."""
        # Mock the models
        self.mock_embedding_model = MagicMock()
        self.mock_embedding_model.embed_query.return_value = [0.1] * 10
        self.mock_reranker_model = MagicMock()
        mock_model_manager_class.return_value.embedding_model = self.mock_embedding_model
        mock_model_manager_class.return_value.reranker_model = self.mock_reranker_model

        # Mock Redis client
        self.mock_redis_instance = MagicMock()
        mock_redis_class.return_value = self.mock_redis_instance

        # Mock Qdrant client
        self.mock_qdrant_instance = mock_qdrant_client

        # Instantiate the cache, which will use the mocked clients
        self.cache = Cache()
        self.cache.initialize(recreate=False)

    def tearDown(self):
        """Clean up by resetting the singleton instance after each test."""
        Cache._instance = None

    def test_singleton_pattern(self, mock_redis_class, mock_model_manager_class, mock_qdrant_client):
        """Test that Cache is a singleton and returns the same instance."""
        self._setup_cache(mock_redis_class, mock_model_manager_class, mock_qdrant_client)
        instance1 = Cache()
        instance2 = Cache()
        self.assertIs(instance1, instance2)
        self.assertIs(instance1, self.cache)

    def test_initialize(self, mock_redis_class, mock_model_manager_class, mock_qdrant_client):
        """Test the initialization of Redis, Qdrant, and models."""
        self._setup_cache(mock_redis_class, mock_model_manager_class, mock_qdrant_client)

        # Check if Redis was initialized
        mock_redis_class.assert_called_once_with(
            host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
        )
        self.assertIsNotNone(self.cache.redis_db)

        # Check if ModelManager was called
        mock_model_manager_class.assert_called_once()
        self.assertIsNotNone(self.cache.embedding_model)
        self.assertIsNotNone(self.cache.reranker_model)

        # Check if Qdrant client is set
        self.assertEqual(self.cache._client, self.mock_qdrant_instance)
        self.assertEqual(self.cache._collection_name, 'test_collection')
        self.assertEqual(self.cache._embedding_dim, 10)

    def test_ensure_collection_exists_recreate(self, mock_redis_class, mock_model_manager_class, mock_qdrant_client):
        """Test that collection is deleted and recreated when recreate=True."""
        Cache._instance = None  # Reset to re-initialize
        self._setup_cache(mock_redis_class, mock_model_manager_class, mock_qdrant_client)

        # We need to re-initialize to test the 'recreate' flag
        Cache._instance = None
        cache = Cache()
        cache.initialize(recreate=True)

        mock_qdrant_client.delete_collection.assert_called_once_with(collection_name='test_collection')
        mock_qdrant_client.create_collection.assert_called_once()
        self.assertEqual(mock_qdrant_client.create_payload_index.call_count, 4)

    def test_get_exact_cache(self, mock_redis_class, mock_model_manager_class, mock_qdrant_client):
        """Test retrieving a value from the Redis cache."""
        self._setup_cache(mock_redis_class, mock_model_manager_class, mock_qdrant_client)
        self.mock_redis_instance.get.return_value = "cached_response"
        result = self.cache.get_exact_cache("test_query")
        self.mock_redis_instance.get.assert_called_once_with("test_query")
        self.assertEqual(result, "cached_response")

    def test_set_exact_cache(self, mock_redis_class, mock_model_manager_class, mock_qdrant_client):
        """Test setting a value in the Redis cache."""
        self._setup_cache(mock_redis_class, mock_model_manager_class, mock_qdrant_client)
        self.cache.set_exact_cache("test_key", "test_value")
        self.mock_redis_instance.set.assert_called_once_with("test_key", "test_value")

    def test_query_to_point_id(self, mock_redis_class, mock_model_manager_class, mock_qdrant_client):
        """Test deterministic UUID generation for a query."""
        self._setup_cache(mock_redis_class, mock_model_manager_class, mock_qdrant_client)
        query = "hello world"
        expected_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, query))
        result_id = self.cache._query_to_point_id(query)
        self.assertEqual(result_id, expected_id)

    def test_insert_row(self, mock_redis_class, mock_model_manager_class, mock_qdrant_client):
        """Test inserting a new row into Qdrant."""
        self._setup_cache(mock_redis_class, mock_model_manager_class, mock_qdrant_client)
        self.cache._insert_row("q", "r", "u", 1, 0, 0)
        self.mock_embedding_model.embed_query.assert_called_with("q")
        self.mock_qdrant_instance.upsert.assert_called_once()
        # Check that the payload is correct in the call to upsert
        args, kwargs = self.mock_qdrant_instance.upsert.call_args
        self.assertEqual(kwargs['collection_name'], 'test_collection')
        point = kwargs['points'][0]
        self.assertEqual(point.payload['query'], 'q')
        self.assertEqual(point.payload['response'], 'r')

    def test_update_row_existing(self, mock_redis_class, mock_model_manager_class, mock_qdrant_client):
        """Test updating an existing row in Qdrant."""
        self._setup_cache(mock_redis_class, mock_model_manager_class, mock_qdrant_client)
        existing_payload = {"query": "q", "response": "r", "thumb_up": 1}
        with patch.object(self.cache, '_get_row', return_value=existing_payload) as mock_get_row:
            self.cache._update_row("q", {"thumb_up": 2, "response": "new_r"})

            self.mock_qdrant_instance.upsert.assert_called_once()
            args, kwargs = self.mock_qdrant_instance.upsert.call_args
            point = kwargs['points'][0]
            # Verify payload is correctly merged
            self.assertEqual(point.payload['response'], 'new_r')
            self.assertEqual(point.payload['thumb_up'], 2)

    def test_update_row_new(self, mock_redis_class, mock_model_manager_class, mock_qdrant_client):
        """Test that _update_row calls _insert_row for a new query."""
        self._setup_cache(mock_redis_class, mock_model_manager_class, mock_qdrant_client)
        with patch.object(self.cache, '_get_row', return_value=None) as mock_get_row:
            with patch.object(self.cache, '_insert_row', autospec=True) as mock_insert_row:
                self.cache._update_row("new_q", {"response": "new_r"})
                mock_get_row.assert_called_once_with("new_q")
                mock_insert_row.assert_called_once_with(
                    query="new_q",
                    response="new_r",
                    url="",
                    thumb_up=0,
                    thumb_down=0,
                    flag=0
                )

    def test_get_row(self, mock_redis_class, mock_model_manager_class, mock_qdrant_client):
        """Test retrieving a single row from Qdrant by query."""
        self._setup_cache(mock_redis_class, mock_model_manager_class, mock_qdrant_client)
        mock_point = MagicMock()
        mock_point.payload = {"query": "q", "response": "r"}
        self.mock_qdrant_instance.retrieve.return_value = [mock_point]

        result = self.cache._get_row("q")

        point_id = self.cache._query_to_point_id("q")
        self.mock_qdrant_instance.retrieve.assert_called_once_with(
            collection_name='test_collection', ids=[point_id], with_payload=True
        )
        self.assertEqual(result, {"query": "q", "response": "r"})

    def test_rerank_score(self, mock_redis_class, mock_model_manager_class, mock_qdrant_client):
        """Test the reranking logic."""
        self._setup_cache(mock_redis_class, mock_model_manager_class, mock_qdrant_client)
        matches = [
            {"query": "doc1", "response": "resp1"},
            {"query": "doc2", "response": "resp2"},
        ]
        # Reranker returns higher score for doc2
        self.mock_reranker_model.compute_score.return_value = [0.5, 0.9]

        reranked_matches = self.cache._rerank_score("query", matches)

        self.mock_reranker_model.compute_score.assert_called_once()
        # Check that doc2 is now first
        self.assertEqual(len(reranked_matches), 2)
        self.assertEqual(reranked_matches[0]['query'], 'doc2')
        self.assertEqual(reranked_matches[1]['query'], 'doc1')

    def test_get_embedding_match(self, mock_redis_class, mock_model_manager_class, mock_qdrant_client):
        """Test finding similar documents via embedding search."""
        self._setup_cache(mock_redis_class, mock_model_manager_class, mock_qdrant_client)
        mock_result = MagicMock()
        mock_result.score = 0.95  # High similarity
        mock_result.payload = {"query": "similar_q", "response": "r"}
        self.mock_qdrant_instance.search.return_value = [mock_result]

        with patch.object(self.cache, '_rerank_score', side_effect=lambda q, m, k: m) as mock_rerank:
            matches = self.cache.get_embedding_match("query", threshold=0.1, knn=5)

            self.mock_qdrant_instance.search.assert_called_once_with(
                collection_name='test_collection',
                query_vector=[0.1] * 10,
                limit=5,
                with_payload=True,
                score_threshold=0.9  # 1 - 0.1
            )
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0]['query'], 'similar_q')
            # Rerank should not be called for a single match
            mock_rerank.assert_not_called()

    def test_get_embedding_match_with_rerank(self, mock_redis_class, mock_model_manager_class, mock_qdrant_client):
        """Test that reranking is called for multiple matches."""
        self._setup_cache(mock_redis_class, mock_model_manager_class, mock_qdrant_client)
        mock_result1 = MagicMock(score=0.95, payload={"query": "q1"})
        mock_result2 = MagicMock(score=0.92, payload={"query": "q2"})
        self.mock_qdrant_instance.search.return_value = [mock_result1, mock_result2]

        with patch.object(self.cache, '_rerank_score', return_value=[{"query": "reranked"}],
                          autospec=True) as mock_rerank:
            matches = self.cache.get_embedding_match("query", threshold=0.1, knn=5)

            self.assertTrue(len(matches) > 0)
            mock_rerank.assert_called_once()
            self.assertEqual(matches[0]['query'], 'reranked')

    def test_increment_thumb_up_new_document(self, mock_redis_class, mock_model_manager_class, mock_qdrant_client):
        """Test incrementing thumb_up for a document that doesn't exist."""
        self._setup_cache(mock_redis_class, mock_model_manager_class, mock_qdrant_client)
        with patch.object(self.cache, '_get_row', return_value=None) as mock_get_row:
            with patch.object(self.cache, '_insert_row', autospec=True) as mock_insert_row:
                self.cache.increment_thumb_up("q", "r", "u")

                mock_get_row.assert_called_once_with("q")
                mock_insert_row.assert_called_once_with(
                    query="q", response="r", url="u", thumb_up=1, thumb_down=0, flag=0
                )

    def test_increment_thumb_down_existing_document(self, mock_redis_class, mock_model_manager_class,
                                                    mock_qdrant_client):
        """Test incrementing thumb_down for an existing document."""
        self._setup_cache(mock_redis_class, mock_model_manager_class, mock_qdrant_client)
        existing_record = {"query": "q", "thumb_down": 1}
        with patch.object(self.cache, '_get_row', return_value=existing_record) as mock_get_row:
            with patch.object(self.cache, '_update_row', autospec=True) as mock_update_row:
                self.cache.increment_thumb_down("q", "r", "u")

                mock_get_row.assert_called_once_with("q")
                mock_update_row.assert_called_once_with("q", {"thumb_down": 2})

    def test_filter_documents(self, mock_redis_class, mock_model_manager_class, mock_qdrant_client):
        """Test filtering documents using the scroll API."""
        self._setup_cache(mock_redis_class, mock_model_manager_class, mock_qdrant_client)
        mock_point1 = MagicMock(payload={'query': 'q1'})
        mock_point2 = MagicMock(payload={'query': 'q2'})

        # Simulate pagination: first call returns one result and a next offset, second call returns another
        self.mock_qdrant_instance.scroll.side_effect = [
            ([mock_point1], "next_offset_id"),
            ([mock_point2], None)
        ]

        filters = {"author": "test_user", "flag": {"$gte": 1}}
        results = self.cache.filter_documents(filters)

        self.assertEqual(self.mock_qdrant_instance.scroll.call_count, 2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['query'], 'q1')
        self.assertEqual(results[1]['query'], 'q2')

        # Check that the filter was constructed correctly
        first_call_args, first_call_kwargs = self.mock_qdrant_instance.scroll.call_args_list[0]
        scroll_filter = first_call_kwargs['scroll_filter']
        self.assertIsNotNone(scroll_filter)
        self.assertEqual(len(scroll_filter.must), 2)

    def test_get_documents_with_metadata_field_numeric(self, mock_redis_class, mock_model_manager_class,
                                                       mock_qdrant_client):
        """Test getting documents that have a specific numeric metadata field."""
        self._setup_cache(mock_redis_class, mock_model_manager_class, mock_qdrant_client)
        with patch.object(self.cache, 'filter_documents', autospec=True) as mock_filter:
            self.cache.get_documents_with_metadata_field("thumb_up")
            mock_filter.assert_called_once_with({"thumb_up": {"$gte": 0}})

    def test_get_documents_with_metadata_field_non_numeric(self, mock_redis_class, mock_model_manager_class,
                                                           mock_qdrant_client):
        """Test getting documents that have a specific non-numeric metadata field."""
        self._setup_cache(mock_redis_class, mock_model_manager_class, mock_qdrant_client)
        self.mock_qdrant_instance.scroll.return_value = ([], None)  # Return empty result
        self.cache.get_documents_with_metadata_field("url")

        self.mock_qdrant_instance.scroll.assert_called_once()
        args, kwargs = self.mock_qdrant_instance.scroll.call_args
        scroll_filter = kwargs['scroll_filter']
        # Check for must_not=[IsEmptyCondition(...)] which is now IsNotNullCondition
        self.assertIsNotNone(scroll_filter.must)
        self.assertEqual(scroll_filter.must[0].is_not_null.key, "url")

    def test_delete_document(self, mock_redis_class, mock_model_manager_class, mock_qdrant_client):
        """Test deleting a document from Qdrant."""
        self._setup_cache(mock_redis_class, mock_model_manager_class, mock_qdrant_client)
        query = "query_to_delete"
        point_id = self.cache._query_to_point_id(query)

        with patch.object(self.cache, '_get_row', return_value={"query": query}) as mock_get_row:
            self.cache.delete_document(query)

            self.mock_qdrant_instance.delete.assert_called_once()
            args, kwargs = self.mock_qdrant_instance.delete.call_args
            self.assertEqual(kwargs['collection_name'], 'test_collection')
            self.assertEqual(kwargs['points_selector'].points, [point_id])

    def test_delete_document_not_found(self, mock_redis_class, mock_model_manager_class, mock_qdrant_client):
        """Test that delete is not called if the document doesn't exist."""
        self._setup_cache(mock_redis_class, mock_model_manager_class, mock_qdrant_client)
        with patch.object(self.cache, '_get_row', return_value=None) as mock_get_row:
            self.cache.delete_document("non_existent_query")
            self.mock_qdrant_instance.delete.assert_not_called()


if __name__ == '__main__':
    unittest.main()