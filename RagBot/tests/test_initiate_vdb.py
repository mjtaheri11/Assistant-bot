import unittest
from unittest.mock import MagicMock, patch, call
import os
from langchain_core.documents import Document
from qdrant_client import QdrantClient, models

# Import the module itself to use patch.object
import src.initiate_vdb

# Import the functions to be tested
from src.initiate_vdb import (
    _initialize_qdrant_client,
    create_vector_database,
    create_vector_database_from_config,
    delete_vector_database,
    list_vector_databases,
    get_collection_info,
    add_documents_to_existing_collection,
)

class TestInitiateVDB(unittest.TestCase):

    @patch('src.initiate_vdb.QdrantClient')
    def test_initialize_qdrant_client_http(self, mock_qdrant_client):
        """Test Qdrant client initialization with HTTP."""
        os.environ['QDRANT_API_BASE'] = 'localhost'
        os.environ['QDRANT_API_PORT'] = '6333'
        os.environ['QDRANT_API_KEY'] = 'test_key'

        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        client = _initialize_qdrant_client()

        self.assertIsNotNone(client)
        mock_qdrant_client.assert_called_with(
            host='localhost',
            port='6333',
            api_key='test_key',
            timeout=60,
            prefer_grpc=False,
            https=False
        )

    @patch('src.initiate_vdb.QdrantClient')
    def test_initialize_qdrant_client_https_fallback(self, mock_qdrant_client):
        """Test Qdrant client initialization with HTTPS fallback."""
        os.environ['QDRANT_API_BASE'] = 'localhost'
        os.environ['QDRANT_API_PORT'] = '6333'
        os.environ['QDRANT_API_KEY'] = 'test_key'

        # Simulate HTTP connection failure
        mock_qdrant_client.side_effect = [Exception("HTTP failed"), MagicMock()]

        client = _initialize_qdrant_client()

        self.assertIsNotNone(client)
        self.assertEqual(mock_qdrant_client.call_count, 2)
        # Check the second call for HTTPS
        https_call = mock_qdrant_client.call_args_list[1]
        self.assertEqual(https_call, call(url='http://localhost:6333', api_key='test_key', timeout=60, verify=False))

    def test_create_vector_database(self):
        """Test the main vector database creation function."""
        mock_qdrant_client = MagicMock(spec=QdrantClient)
        mock_embedding_model = MagicMock()
        mock_embedding_model.embed_query.return_value = [0.1] * 768

        documents = [Document(page_content="Test content")]
        database_id = "test_db"

        with patch('src.initiate_vdb.Qdrant') as mock_qdrant_vdb:
            create_vector_database(
                database_id=database_id,
                all_documents=documents,
                qdrant_client=mock_qdrant_client,
                embedding_model=mock_embedding_model,
                recreate=True
            )

            mock_qdrant_client.collection_exists.assert_called_with(database_id)
            mock_qdrant_client.delete_collection.assert_called_with(collection_name=database_id)
            mock_qdrant_client.create_collection.assert_called_once()
            mock_qdrant_vdb.return_value.add_documents.assert_called_with(documents)

    @patch.object(src.initiate_vdb, 'qdrant_client', None) # Applied first to override the global
    @patch('src.retriever.ModelManager')
    @patch('src.initiate_vdb._initialize_qdrant_client')
    def test_create_vector_database_from_config(self, mock_init_client, mock_model_manager):
        """Test the config-based wrapper for DB creation."""
        mock_qdrant_client_instance = MagicMock(spec=QdrantClient)
        mock_init_client.return_value = mock_qdrant_client_instance # _initialize_qdrant_client will return this mock

        mock_embedding_model = MagicMock()
        mock_model_manager.return_value.embedding_model = mock_embedding_model
        mock_embedding_model.embed_query.return_value = [0.1] * 768

        documents = [Document(page_content="Test content")]
        database_id = "test_db_from_config"

        with patch('src.initiate_vdb.create_vector_database') as mock_create_db:
            create_vector_database_from_config(
                database_id=database_id,
                all_documents=documents
            )

            mock_create_db.assert_called_once()
            _, kwargs = mock_create_db.call_args
            self.assertEqual(kwargs['database_id'], database_id)
            # Now, kwargs['qdrant_client'] should be the mock_qdrant_client_instance
            self.assertEqual(kwargs['qdrant_client'], mock_qdrant_client_instance)
            self.assertEqual(kwargs['embedding_model'], mock_embedding_model)
            self.assertEqual(kwargs['all_documents'], documents)

    def test_delete_vector_database(self):
        """Test deleting a vector database."""
        mock_qdrant_client = MagicMock(spec=QdrantClient)
        database_id = "db_to_delete"

        result = delete_vector_database(database_id, mock_qdrant_client)

        self.assertTrue(result)
        mock_qdrant_client.delete_collection.assert_called_with(collection_name=database_id)

    def test_list_vector_databases(self):
        """Test listing vector databases."""
        mock_qdrant_client = MagicMock(spec=QdrantClient)
        mock_collection = MagicMock()
        mock_collection.name = "test_collection"
        mock_qdrant_client.get_collections.return_value.collections = [mock_collection]

        collections = list_vector_databases(mock_qdrant_client)

        self.assertEqual(collections, ["test_collection"])

    def test_get_collection_info(self):
        """Test getting collection information."""
        mock_qdrant_client = MagicMock(spec=QdrantClient)
        database_id = "test_info_db"
        mock_info = MagicMock()
        mock_info.points_count = 100
        mock_info.status = "green"
        mock_info.config.params.vectors.size = 768
        mock_qdrant_client.get_collection.return_value = mock_info

        info = get_collection_info(database_id, mock_qdrant_client)

        self.assertIsNotNone(info)
        self.assertEqual(info['points_count'], 100)
        self.assertEqual(info['vector_size'], 768)

    def test_add_documents_to_existing_collection(self):
        """Test adding documents to an existing collection."""
        mock_qdrant_client = MagicMock(spec=QdrantClient)
        mock_embedding_model = MagicMock()
        database_id = "existing_db"
        documents = [Document(page_content="More content")]

        mock_qdrant_client.collection_exists.return_value = True

        with patch('src.initiate_vdb.Qdrant') as mock_qdrant_vdb:
            result = add_documents_to_existing_collection(
                database_id=database_id,
                documents=documents,
                qdrant_client=mock_qdrant_client,
                embedding_model=mock_embedding_model
            )

            self.assertTrue(result)
            mock_qdrant_vdb.return_value.add_documents.assert_called_with(documents)

if __name__ == '__main__':
    unittest.main()
