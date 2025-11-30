import os
import uuid
import logging
from typing import List, Dict

import numpy as np
import yaml
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient, models
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import Optional
import json
import pandas as pd
from langchain_core.documents import Document

from .config import config
# from .make_sentence_chunks import chunk_document
from dotenv import load_dotenv

load_dotenv()

def get_logger():
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(__name__)

logger = get_logger()

# Initialize Qdrant client
QDRANT_URL = os.getenv("QDRANT_API_BASE")
QDRANT_PORT = os.getenv("QDRANT_API_PORT")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Try to connect without SSL first (common for internal cluster communication)
try:
    qdrant_client = QdrantClient(
        host=QDRANT_URL,
        port=QDRANT_PORT,
        api_key=QDRANT_API_KEY,
        timeout=60,
        prefer_grpc=False,  # Use HTTP instead of gRPC
        https=False,  # Disable HTTPS for internal cluster communication
    )
    print("✅ Connected to Qdrant via HTTP (no SSL)")
except Exception as e:
    print(f"⚠️ HTTP connection failed, trying with SSL: {e}")
    # Fallback to HTTPS if HTTP fails
    qdrant_client = QdrantClient(
        url=f"https://{QDRANT_URL}",
        api_key=QDRANT_API_KEY,
        timeout=60,
        verify=False,  # Skip SSL certificate verification if needed
    )


def create_vector_database(
    database_id: str,
    all_documents: List[Document],
    qdrant_client: QdrantClient,
    embedding_model,
    recreate: bool = True,
    batch_size: int = 100
) -> str:
    """
    Creates a new Qdrant collection for the vector database.
    """
    from langchain_qdrant import Qdrant
    
    collection_name = database_id
    
    logger.info(f"Creating Qdrant collection: {collection_name}")
    logger.info(f"Total documents to add: {len(all_documents)}")
    
    if len(all_documents) == 0:
        raise ValueError("No documents to add to the collection")
    
    # Validate documents before processing
    logger.info("Validating documents...")
    valid_documents = []
    for i, doc in enumerate(all_documents):
        if not hasattr(doc, 'page_content') or not doc.page_content:
            logger.warning(f"Document {i} has no page_content, skipping")
            continue
        if not isinstance(doc.page_content, str):
            logger.warning(f"Document {i} page_content is not a string: {type(doc.page_content)}, skipping")
            continue
        valid_documents.append(doc)
    
    logger.info(f"Valid documents: {len(valid_documents)} out of {len(all_documents)}")
    
    if len(valid_documents) == 0:
        raise ValueError("No valid documents to add to the collection")
    
    # Get embedding dimension from the model
    try:
        logger.info("Determining embedding dimension...")
        sample_embedding = embedding_model.embed_query("test")
        vector_size = len(sample_embedding)
        logger.info(f"✅ Embedding dimension: {vector_size}")
    except Exception as e:
        logger.error(f"❌ Failed to get embedding dimension: {e}")
        raise ValueError(f"Could not determine embedding dimension from model: {e}")
    
    # Check if collection exists
    try:
        collections = qdrant_client.get_collections().collections
        collection_exists = any(c.name == collection_name for c in collections)
        
        if collection_exists:
            if recreate:
                logger.warning(f"Collection '{collection_name}' already exists. Deleting...")
                qdrant_client.delete_collection(collection_name=collection_name)
                logger.info(f"✅ Deleted existing collection '{collection_name}'")
            else:
                logger.info(f"Collection '{collection_name}' already exists. Appending documents...")
                vdb = Qdrant(
                    client=qdrant_client,
                    collection_name=collection_name,
                    embeddings=embedding_model,
                )
                
                # Add documents in batches with error handling
                if len(valid_documents) > batch_size:
                    logger.info(f"Adding {len(valid_documents)} documents in batches of {batch_size}")
                    for i in range(0, len(valid_documents), batch_size):
                        batch = valid_documents[i:i + batch_size]
                        try:
                            logger.info(f"Adding batch {i//batch_size + 1}/{(len(valid_documents)-1)//batch_size + 1}")
                            vdb.add_documents(batch)
                            logger.info(f"✅ Batch {i//batch_size + 1} completed")
                        except Exception as batch_error:
                            logger.error(f"❌ Error adding batch {i//batch_size + 1}: {batch_error}")
                            # Log problematic documents
                            for j, doc in enumerate(batch):
                                logger.error(f"  Doc {j}: {doc.page_content[:100]}...")
                            raise
                else:
                    try:
                        logger.info(f"Adding {len(valid_documents)} documents")
                        vdb.add_documents(valid_documents)
                        logger.info(f"✅ Added {len(valid_documents)} documents")
                    except Exception as add_error:
                        logger.error(f"❌ Error adding documents: {add_error}")
                        # Try to identify problematic document
                        for i, doc in enumerate(valid_documents):
                            logger.error(f"  Doc {i}: content_length={len(doc.page_content)}, "
                                       f"metadata={doc.metadata}")
                        raise
                
                logger.info(f"✅ Added {len(valid_documents)} documents to existing collection")
                return collection_name
                
    except Exception as e:
        logger.error(f"Error checking existing collection: {e}")
        raise
    
    # Create new collection
    try:
        logger.info(f"Creating new collection with vector size {vector_size}...")
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE
            ),
            optimizers_config=models.OptimizersConfigDiff(
                indexing_threshold=10000
            ),
            on_disk_payload=True
        )
        logger.info(f"✅ Created collection '{collection_name}'")
    except Exception as e:
        logger.error(f"❌ Failed to create collection: {e}")
        raise
    
    # Initialize Qdrant vector store and add documents
    try:
        vdb = Qdrant(
            client=qdrant_client,
            collection_name=collection_name,
            embeddings=embedding_model,
        )
        
        # Add documents in batches
        if len(valid_documents) > batch_size:
            logger.info(f"Adding {len(valid_documents)} documents in batches of {batch_size}")
            for i in range(0, len(valid_documents), batch_size):
                batch = valid_documents[i:i + batch_size]
                try:
                    logger.info(f"Adding batch {i//batch_size + 1}/{(len(valid_documents)-1)//batch_size + 1}")
                    vdb.add_documents(batch)
                    logger.info(f"✅ Batch {i//batch_size + 1} completed")
                except Exception as batch_error:
                    logger.error(f"❌ Error adding batch {i//batch_size + 1}: {batch_error}")
                    raise
        else:
            vdb.add_documents(valid_documents)
        
        logger.info(f"✅ Successfully added {len(valid_documents)} documents to collection '{collection_name}'")
        
        # Verify collection
        collection_info = qdrant_client.get_collection(collection_name=collection_name)
        logger.info(f"Collection verification: {collection_info.points_count} points indexed")
        
    except Exception as e:
        logger.error(f"❌ Failed to add documents: {e}")
        raise
    
    return collection_name

    
# ===== CONFIG-BASED VERSION (Uses ModelManager) =====
def create_vector_database_from_config(
    database_id: str,
    all_documents: List[Document],
    recreate: bool = True,
    batch_size: int = 100,
    qdrant_client: Optional[QdrantClient] = None,
    embedding_model = None
) -> str:
    """
    Creates a new Qdrant collection using the configuration from config.py.
    This version automatically initializes the embedding model and Qdrant client
    from the ModelManager singleton.
    
    Args:
        database_id: Unique identifier for the database (used as collection_name)
        all_documents: List of Document objects to add to the collection
        recreate: If True, delete existing collection; if False, append to existing
        batch_size: Number of documents to process at once
        qdrant_client: Optional custom QdrantClient (uses default if not provided)
        embedding_model: Optional custom embedding model (uses config default if not provided)
    
    Returns:
        collection_name: The name of the created collection (same as database_id)
    """
    # Get embedding model from ModelManager if not provided
    if embedding_model is None:
        from src.retriever import ModelManager    
        logger.info("Using embedding model from ModelManager (based on config)")
        model_manager = ModelManager()
        embedding_model = model_manager.embedding_model
    
    # Initialize Qdrant client if not provided
    if qdrant_client is None:
        logger.info("Initializing Qdrant client from environment variables")
        qdrant_host = os.getenv("QDRANT_API_BASE")
        qdrant_port = os.getenv("QDRANT_API_PORT")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        try:
            qdrant_client = QdrantClient(
                host=qdrant_host,
                port=qdrant_port,
                api_key=qdrant_api_key,
                timeout=60,
                prefer_grpc=False,
                https=False,
            )
            logger.info("✅ Connected to Qdrant via HTTP (no SSL)")
        except Exception as e:
            logger.warning(f"⚠️ HTTP connection failed, trying with SSL: {e}")
            qdrant_client = QdrantClient(
                url=f"https://{qdrant_host}:{qdrant_port}",
                api_key=qdrant_api_key,
                timeout=60,
                verify=False,
            )
    
    # Call the standalone function with the configured models
    return create_vector_database(
        database_id=database_id,
        all_documents=all_documents,
        qdrant_client=qdrant_client,
        embedding_model=embedding_model,
        recreate=recreate,
        batch_size=batch_size
    )


# ===== HELPER FUNCTIONS =====
def delete_vector_database(
    database_id: str,
    qdrant_client: Optional[QdrantClient] = None
) -> bool:
    """
    Delete a Qdrant collection.
    
    Args:
        database_id: Collection name to delete
        qdrant_client: Optional QdrantClient instance
    
    Returns:
        True if deleted successfully, False otherwise
    """
    if qdrant_client is None:
        qdrant_host = os.getenv("QDRANT_API_BASE")
        qdrant_port = os.getenv("QDRANT_API_PORT")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        try:
            qdrant_client = QdrantClient(
                host=qdrant_host,
                port=qdrant_port,
                api_key=qdrant_api_key,
                timeout=60,
                prefer_grpc=False,
                https=False,
            )
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            return False
    
    try:
        qdrant_client.delete_collection(collection_name=database_id)
        logger.info(f"✅ Deleted collection '{database_id}'")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to delete collection '{database_id}': {e}")
        return False


def list_vector_databases(
    qdrant_client: Optional[QdrantClient] = None
) -> List[str]:
    """
    List all available Qdrant collections.
    
    Args:
        qdrant_client: Optional QdrantClient instance
    
    Returns:
        List of collection names
    """
    if qdrant_client is None:
        qdrant_host = os.getenv("QDRANT_API_BASE")
        qdrant_port = os.getenv("QDRANT_API_PORT")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        try:
            qdrant_client = QdrantClient(
                host=qdrant_host,
                port=qdrant_port,
                api_key=qdrant_api_key,
                timeout=60,
                prefer_grpc=False,
                https=False,
            )
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            return []
    
    try:
        collections = qdrant_client.get_collections().collections
        collection_names = [c.name for c in collections]
        logger.info(f"Found {len(collection_names)} collections")
        return collection_names
    except Exception as e:
        logger.error(f"Failed to list collections: {e}")
        return []


def get_collection_info(
    database_id: str,
    qdrant_client: Optional[QdrantClient] = None
) -> Optional[dict]:
    """
    Get information about a specific collection.
    
    Args:
        database_id: Collection name
        qdrant_client: Optional QdrantClient instance
    
    Returns:
        Dictionary with collection information or None if error
    """
    if qdrant_client is None:
        qdrant_host = os.getenv("QDRANT_API_BASE")
        qdrant_port = os.getenv("QDRANT_API_PORT")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        try:
            qdrant_client = QdrantClient(
                host=qdrant_host,
                port=qdrant_port,
                api_key=qdrant_api_key,
                timeout=60,
                prefer_grpc=False,
                https=False,
            )
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            return None
    
    try:
        collection_info = qdrant_client.get_collection(collection_name=database_id)
        
        info_dict = {
            "name": database_id,
            "points_count": collection_info.points_count,
            "vectors_count": collection_info.vectors_count,
            "indexed_vectors_count": collection_info.indexed_vectors_count,
            "status": collection_info.status,
            "optimizer_status": collection_info.optimizer_status,
            "vector_size": collection_info.config.params.vectors.size,
            "distance": collection_info.config.params.vectors.distance.name
        }
        
        logger.info(f"Collection '{database_id}': {info_dict['points_count']} points")
        return info_dict
        
    except Exception as e:
        logger.error(f"Failed to get collection info for '{database_id}': {e}")
        return None


def add_documents_to_existing_collection(
    database_id: str,
    documents: List[Document],
    qdrant_client: Optional[QdrantClient] = None,
    embedding_model = None,
    batch_size: int = 100
) -> bool:
    """
    Add documents to an existing Qdrant collection.
    
    Args:
        database_id: Existing collection name
        documents: List of Document objects to add
        qdrant_client: Optional QdrantClient instance
        embedding_model: Optional embedding model (uses config default if not provided)
        batch_size: Number of documents to process at once
    
    Returns:
        True if successful, False otherwise
    """
    if len(documents) == 0:
        logger.warning("No documents to add")
        return False
    
    # Get embedding model if not provided
    if embedding_model is None:
        from src.retriever import ModelManager
        logger.info("Using embedding model from ModelManager")
        model_manager = ModelManager()
        embedding_model = model_manager.embedding_model
    
    # Initialize Qdrant client if not provided
    if qdrant_client is None:
        qdrant_host = os.getenv("QDRANT_API_BASE")
        qdrant_port = os.getenv("QDRANT_API_PORT")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        try:
            qdrant_client = QdrantClient(
                host=qdrant_host,
                port=qdrant_port,
                api_key=qdrant_api_key,
                timeout=60,
                prefer_grpc=False,
                https=False,
            )
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            return False
    
    # Check if collection exists
    try:
        collections = qdrant_client.get_collections().collections
        collection_exists = any(c.name == database_id for c in collections)
        
        if not collection_exists:
            logger.error(f"Collection '{database_id}' does not exist")
            return False
    except Exception as e:
        logger.error(f"Error checking collection: {e}")
        return False
    
    # Add documents
    try:
        vdb = Qdrant(
            client=qdrant_client,
            collection_name=database_id,
            embeddings=embedding_model,
        )
        
        # Add in batches
        if len(documents) > batch_size:
            logger.info(f"Adding {len(documents)} documents in batches of {batch_size}")
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                vdb.add_documents(batch)
                logger.info(f"✅ Added batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
        else:
            vdb.add_documents(documents)
        
        logger.info(f"✅ Successfully added {len(documents)} documents to collection '{database_id}'")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to add documents: {e}")
        return False
