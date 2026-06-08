import os
import logging
import json
from typing import List, Dict, Optional, Any

from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient, models
from langchain_core.documents import Document
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_logger():
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(__name__)


logger = get_logger()


# ==========================================
# CLIENT INITIALIZATION (Restored Global)
# ==========================================

def delete_documents_by_sources(
        database_id: str,
        sources: List[str],
        qdrant_client: Optional[QdrantClient] = None,
) -> int:
    """
    Delete every point whose `metadata.source` is one of `sources`.

    Returns the number of points that matched the filter *before* deletion
    (best-effort; -1 if the count call failed). Other files are untouched.
    """
    if not sources:
        return 0

    if qdrant_client is None:
        qdrant_client = globals().get('qdrant_client') or _initialize_qdrant_client()
    if qdrant_client is None:
        raise ValueError("No Qdrant client available")

    source_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="metadata.source",
                match=models.MatchAny(any=list(sources)),
            )
        ]
    )

    # Best-effort: how many points are we about to remove?
    try:
        matched = qdrant_client.count(
            collection_name=database_id,
            count_filter=source_filter,
            exact=True,
        ).count
    except Exception as e:
        logger.warning(f"Could not count points for sources {sources}: {e}")
        matched = -1

    qdrant_client.delete(
        collection_name=database_id,
        points_selector=models.FilterSelector(filter=source_filter),
        wait=True,
    )
    logger.info(f"🗑️  Deleted vectors for sources={sources} (matched={matched})")
    return matched


def upsert_documents_by_source(
        database_id: str,
        documents: List[Document],
        qdrant_client: Optional[QdrantClient] = None,
        embedding_model=None,
        batch_size: int = 100,
        create_if_missing: bool = True,
) -> Dict[str, Any]:
    """
    Replace only the vectors that belong to the filenames present in
    `documents`, leaving every other file in the collection intact.

      1. Collect the distinct `metadata.source` values from `documents`.
      2. Delete all existing points whose source is in that set.
      3. Insert the new documents.

    Returns: {"deleted": int, "added": int, "sources": [...]}.
    """
    if not documents:
        return {"deleted": 0, "added": 0, "sources": []}

    if qdrant_client is None:
        qdrant_client = globals().get('qdrant_client') or _initialize_qdrant_client()
    if qdrant_client is None:
        raise ValueError("No Qdrant client available")

    if embedding_model is None:
        from src.retriever import ModelManager
        embedding_model = ModelManager().embedding_model

    valid_documents = _validate_documents(documents)

    # Distinct source filenames carried by the incoming batch
    sources = sorted({
        doc.metadata.get("source")
        for doc in valid_documents
        if doc.metadata.get("source")
    })
    if not sources:
        raise ValueError(
            "Cannot upsert by source: documents have no 'source' in metadata."
        )

    # Make sure the collection exists (create empty if necessary)
    if not qdrant_client.collection_exists(database_id):
        if not create_if_missing:
            raise ValueError(f"Collection '{database_id}' does not exist")
        vector_size = _get_embedding_dimension(embedding_model)
        _recreate_collection_if_needed(
            qdrant_client, database_id, vector_size, recreate=False
        )
        deleted = 0
    else:
        deleted = delete_documents_by_sources(database_id, sources, qdrant_client)

    # Insert the fresh chunks
    vdb = Qdrant(
        client=qdrant_client,
        collection_name=database_id,
        embeddings=embedding_model,
    )
    _add_batches(vdb, valid_documents, batch_size)

    logger.info(
        f"✅ Upsert complete for '{database_id}': "
        f"removed={deleted}, added={len(valid_documents)}, sources={sources}"
    )
    return {"deleted": deleted, "added": len(valid_documents), "sources": sources}

def _initialize_qdrant_client() -> QdrantClient:
    """
    Internal helper to create the QdrantClient.
    Handles the logic of trying HTTP first, then falling back to HTTPS.
    """
    qdrant_host = os.getenv("QDRANT_API_BASE")
    qdrant_port = os.getenv("QDRANT_API_PORT")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not qdrant_host:
        # If no URL is set, we might want to return None or raise an error depending on strictness
        # For now, we return None and let the functions handle it if they need it.
        logger.warning("QDRANT_API_BASE not set. Client will be None.")
        return None

    # Try HTTP first (common for internal cluster communication)
    try:
        client = QdrantClient(
            host=qdrant_host,
            port=qdrant_port,
            api_key=qdrant_api_key,
            timeout=60,
            prefer_grpc=False,
            https=False,
        )
        logger.info("✅ Connected to Qdrant via HTTP (no SSL)")
        return client
    except Exception as e:
        logger.warning(f"⚠️ HTTP connection failed, trying with SSL: {e}")
        return QdrantClient(
            url=f"http://{qdrant_host}:{qdrant_port}",
            api_key=qdrant_api_key,
            timeout=60,
            verify=False,
        )

    # Fallback to HTTPS
    try:
        full_url = f"https://{url}"
        if port:
            full_url = f"{full_url}:{port}"

        return QdrantClient(
            url=full_url,
            api_key=api_key,
            timeout=60,
            verify=False,
        )
    except Exception as e:
        # If this fails, the global variable will fail to initialize, mirroring original behavior
        print(f"❌ Critical: Failed to connect to Qdrant via SSL: {e}")
        raise


# Initialize Global Client immediately (Restored)
try:
    qdrant_client = _initialize_qdrant_client()
except Exception as e:
    logger.error(f"Failed to initialize global qdrant_client: {e}")
    qdrant_client = None


# ==========================================
# INTERNAL HELPER FUNCTIONS
# ==========================================

def _json_item_to_document(item: Dict[str, Any]) -> Document:
    question = item.get("question", "")
    
    sql_obj = item.get("sql", {})
    sql_query = sql_obj.get("SQL", "")
    sql_parameters = sql_obj.get("parameters", {})
    
    metadata = {
        "sql": sql_query,
        "parameters": json.dumps(sql_parameters, ensure_ascii=False),
        "complexity": item.get("complexity", ""),
        "module": item.get("module", ""),  # ✅ This is already captured
        "table": item.get("table", ""),
    }
    
    return Document(page_content=question, metadata=metadata)


def _validate_documents(documents: List[Document]) -> List[Document]:
    """Filters out invalid documents to reduce complexity in main function."""
    valid_docs = []
    for i, doc in enumerate(documents):
        if not hasattr(doc, 'page_content') or not doc.page_content:
            logger.warning(f"Document {i} skipped: No page_content.")
            continue
        if not isinstance(doc.page_content, str):
            logger.warning(f"Document {i} skipped: page_content is not string.")
            continue
        valid_docs.append(doc)

    if not valid_docs:
        raise ValueError("No valid documents found to add to the collection.")

    logger.info(f"Valid documents: {len(valid_docs)} out of {len(documents)}")
    return valid_docs


def _get_embedding_dimension(embedding_model) -> int:
    """Safely determines vector size."""
    try:
        sample_embedding = embedding_model.embed_query("test")
        vector_size = len(sample_embedding)
        logger.info(f"✅ Embedding dimension: {vector_size}")
        return vector_size
    except Exception as e:
        raise ValueError(f"Could not determine embedding dimension: {e}")


def _recreate_collection_if_needed(
        client: QdrantClient,
        collection_name: str,
        vector_size: int,
        recreate: bool
) -> None:
    """Handles collection existence checks and creation."""
    exists = client.collection_exists(collection_name)

    if exists and recreate:
        logger.warning(f"Collection '{collection_name}' exists. Deleting...")
        client.delete_collection(collection_name=collection_name)
        exists = False
        logger.info(f"✅ Deleted existing collection '{collection_name}'")

    if not exists:
        logger.info(f"Creating new collection '{collection_name}'...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE
            ),
            optimizers_config=models.OptimizersConfigDiff(indexing_threshold=10000),
            on_disk_payload=True
        )
        logger.info(f"✅ Created collection '{collection_name}'")


def _add_batches(vdb: Qdrant, documents: List[Document], batch_size: int) -> None:
    """Handles batching logic."""
    total = len(documents)
    if total <= batch_size:
        vdb.add_documents(documents)
        logger.info(f"✅ Added {total} documents.")
        return

    logger.info(f"Adding {total} documents in batches of {batch_size}")
    for i in range(0, total, batch_size):
        batch = documents[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        try:
            vdb.add_documents(batch)
            logger.info(f"✅ Batch {batch_num} completed")
        except Exception as e:
            logger.error(f"❌ Error adding batch {batch_num}: {e}")
            raise


# ==========================================
# MAIN PUBLIC FUNCTIONS
# ==========================================

def create_vector_database(
    database_id: str,
    all_documents: List[Document],
    qdrant_client: QdrantClient,
    embedding_model,
    recreate: bool = True,
    batch_size: int = 100
) -> str:
    """
    Main orchestrator. Low cognitive complexity due to helper functions.
    """
    logger.info(f"Starting Qdrant operation for: {database_id}")

    # 1. Validation
    if not all_documents:
        raise ValueError("No documents provided")
    valid_documents = _validate_documents(all_documents)

    # 2. Setup
    vector_size = _get_embedding_dimension(embedding_model)
    _recreate_collection_if_needed(qdrant_client, database_id, vector_size, recreate)

    # 3. Ingestion
    try:
        vdb = Qdrant(
            client=qdrant_client,
            collection_name=database_id,
            embeddings=embedding_model,
        )
        _add_batches(vdb, valid_documents, batch_size)

        # 4. Verify
        info = qdrant_client.get_collection(collection_name=database_id)
        logger.info(f"Verification: {info.points_count} points indexed")
        return database_id

    except Exception as e:
        logger.error(f"❌ Critical error in create_vector_database: {e}")
        raise


def create_vector_database_from_config(
        database_id: str,
        all_documents: List[Document],
        recreate: bool = True,
        batch_size: int = 100,
        qdrant_client: Optional[QdrantClient] = None,  # Can pass local, or uses global below
        embedding_model=None
) -> str:
    """Wrapper that uses default/global config if arguments are missing."""

    # Use global client if none provided
    if qdrant_client is None:
        # We access the global variable defined at the top
        # Use globals() or just direct access if in same module
        qdrant_client = globals().get('qdrant_client')

        if qdrant_client is None:
            # Attempt re-init or fail
            logger.info("Global client was None, attempting re-init...")
            qdrant_client = _initialize_qdrant_client()
    if embedding_model is None:
        from src.retriever import ModelManager
        logger.info("Loading default embedding model from Manager")
        embedding_model = ModelManager().embedding_model

    return create_vector_database(
        database_id=database_id,
        all_documents=all_documents,
        qdrant_client=qdrant_client,
        embedding_model=embedding_model,
        recreate=recreate,
        batch_size=batch_size
    )


def delete_vector_database(
        database_id: str,
        qdrant_client: Optional[QdrantClient] = None
) -> bool:
    """Deletes a collection."""
    if qdrant_client is None:
        qdrant_client = globals().get('qdrant_client') or _initialize_qdrant_client()
        if not qdrant_client: return False

    try:
        qdrant_client.delete_collection(collection_name=database_id)
        logger.info(f"✅ Deleted collection '{database_id}'")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to delete collection '{database_id}': {e}")
        return False


def list_vector_databases(qdrant_client: Optional[QdrantClient] = None) -> List[str]:
    """Lists collections."""
    if qdrant_client is None:
        qdrant_client = globals().get('qdrant_client') or _initialize_qdrant_client()
        if not qdrant_client: return []

    try:
        cols = qdrant_client.get_collections()
        names = [c.name for c in cols.collections]
        logger.info(f"Found {len(names)} collections")
        return names
    except Exception as e:
        logger.error(f"Failed to list collections: {e}")
        return []


def get_collection_info(
        database_id: str,
        qdrant_client: Optional[QdrantClient] = None
) -> Optional[dict]:
    """Gets collection metadata."""
    if qdrant_client is None:
        qdrant_client = globals().get('qdrant_client') or _initialize_qdrant_client()
        if not qdrant_client: return None

    try:
        info = qdrant_client.get_collection(collection_name=database_id)
        return {
            "name": database_id,
            "points_count": info.points_count,
            "status": str(info.status),
            "vector_size": info.config.params.vectors.size,
        }
    except Exception as e:
        logger.error(f"Failed to get info for '{database_id}': {e}")
        return None


def add_documents_to_existing_collection(
        database_id: str,
        documents: List[Document],
        qdrant_client: Optional[QdrantClient] = None,
        embedding_model=None,
        batch_size: int = 100
) -> bool:
    """Adds documents to an existing collection."""
    if not documents: return False

    if qdrant_client is None:
        qdrant_client = globals().get('qdrant_client') or _initialize_qdrant_client()
        if not qdrant_client: return False

    if embedding_model is None:
        from src.retriever import ModelManager
        embedding_model = ModelManager().embedding_model

    if not qdrant_client.collection_exists(database_id):
        logger.error(f"Collection '{database_id}' does not exist.")
        return False

    try:
        vdb = Qdrant(
            client=qdrant_client,
            collection_name=database_id,
            embeddings=embedding_model,
        )
        _add_batches(vdb, documents, batch_size)
        return True
    except Exception as e:
        logger.error(f"❌ Failed to add to existing collection: {e}")
        return False