import os
import uuid
from typing import Any, List, Mapping, Optional, Dict

from qdrant_client import QdrantClient, models
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    Range,
    IsEmptyCondition
)
import redis
from redis.exceptions import RedisError


from .config import config
from .retriever import ModelManager
from .initiate_vdb import qdrant_client

REDIS_HOST = os.environ.get("REDIS_HOST", "185.13.230.222")
REDIS_PORT = os.environ.get("REDIS_PORT", "6380")


class Cache:
    """
    A singleton class that implements a hybrid caching mechanism.

    This class uses Redis for fast, exact-match caching and a Qdrant vector database
    for semantic (vector-based) caching. It is designed to store and retrieve
    query-response pairs, handle user feedback (thumbs up/down, flags), and
    perform semantic searches to find similar past queries.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Implements the singleton pattern to ensure only one instance of the cache exists."""
        if not cls._instance:
            cls._instance = super().__new__(cls)  # <--- FIXED
            cls._instance.initialize(**kwargs)
        return cls._instance

    @classmethod
    def reset(cls):
        """Reset the singleton instance"""
        cls._instance = None

    def initialize(self, exact_cache: bool = True, recreate: bool = False, qdrant_client_instance=None) -> None:
        """
        Initialize the cache with a Qdrant client.

        Args:
            exact_cache: If True, enables Redis for exact-match caching.
            recreate: If True, deletes and recreates the Qdrant collection.
            qdrant_client_instance: An instance of QdrantClient.
        """
        # Avoid re-initialization
        if hasattr(self, '_initialized') and self._initialized:
            return

        self.redis_db = None

        if exact_cache:
            # Initialize Redis client for exact caching if enabled.
            try:
                self.redis_db = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    db=0,
                    decode_responses=True,
                )
            except RedisError:
                self.redis_db = None
        model_manager = ModelManager()
        # Load the embedding model for converting text to vectors.
        self.embedding_model = model_manager.embedding_model
        self.reranker_model = model_manager.reranker_model

        self._client = qdrant_client_instance or qdrant_client
        self._collection_name = config["cache"]["index_name"]

        # Get embedding dimension from a sample embedding
        sample_embedding = self.embedding_model.embed_query("sample")
        self._embedding_dim = len(sample_embedding)

        # Ensure collection exists
        self._ensure_collection_exists(recreate=recreate)

        self._initialized = True

    def _ensure_collection_exists(self, recreate) -> None:
        """
        Ensures the Qdrant collection exists. If `recreate` is True, it deletes
        the old collection and creates a new one with the required payload indices.
        """
        if recreate:
            # Delete the collection if it already exists and recreation is requested.
            self._client.delete_collection(collection_name=self._collection_name)
            self._client.create_collection(
                collection_name=self._collection_name,
                vectors_config=VectorParams(
                    size=self._embedding_dim,
                    distance=Distance.COSINE,
                ),
            )
            # Create a payload index on the 'query' field for efficient keyword-based filtering.
            self._client.create_payload_index(
                collection_name=self._collection_name,
                field_name="query",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
            # Create payload indices on numeric fields for efficient range filtering and sorting.
            for field in ["thumb_up", "thumb_down", "flag"]:
                self._client.create_payload_index(
                    collection_name=self._collection_name,
                    field_name=field,
                    field_schema=models.PayloadSchemaType.INTEGER,
                )

    def get_exact_cache(self, query: str) -> Optional[str]:
        """Get exact match from Redis cache."""
        if self.redis_db:
            try:
                return self.redis_db.get(query)
            except RedisError:
                return None
        return None

    def set_exact_cache(self, key: str, value: str) -> None:
        """Set exact match in Redis cache."""
        if self.redis_db:
            try:
                self.redis_db.set(key, value)
            except RedisError:
                pass

    def _get_embedding(self, query: str) -> List[float]:
        """Get embedding vector for a query."""
        return self.embedding_model.embed_query(query)

    @staticmethod
    def _query_to_point_id(query: str) -> str:
        """
        Generate a deterministic UUID from query string.
        This ensures the same query always maps to the same point ID.
        """  # noqa: E501
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, query))

    def _insert_row(
        self,
        query: str,
        response: str,
        url: str,
        thumb_up: int,
        thumb_down: int,
        flag: int,
    ) -> None:
        """Insert a new row into the Qdrant collection."""
        embedding = self._get_embedding(query)
        point_id = self._query_to_point_id(query)

        # Define the data payload for the Qdrant point.
        payload = {
            "query": query,
            "response": response,
            "url": url,
            "thumb_up": thumb_up,
            "thumb_down": thumb_down,
            "flag": flag,
        }

        # Upsert the point into the collection. 'upsert' will create or update the point.
        self._client.upsert(
            collection_name=self._collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload,
                )
            ],
        )

    def _update_row(
        self,
        query: str,
        mapping: Mapping[str, Any],
    ) -> None:
        """Update an existing row or insert if not exists."""
        # Check if a record for the query already exists.
        existing_record = self._get_row(query)
        if existing_record:
            # Merge existing payload with new values
            payload = existing_record.copy()
            payload.update(mapping)

            embedding = self._get_embedding(query)
            point_id = self._query_to_point_id(query)

            self._client.upsert(
                collection_name=self._collection_name,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=payload,
                    )
                ],
            )
        else:
            # If the record doesn't exist, insert a new one with provided or default values.
            self._insert_row(
                query=query,
                response=mapping.get("response", ""),
                url=mapping.get("url", ""),
                thumb_up=mapping.get("thumb_up", 0),
                thumb_down=mapping.get("thumb_down", 0),
                flag=mapping.get("flag", 0),
            )

    def _get_row(self, query: str) -> Optional[Dict[str, Any]]:
        """Retrieve a row by query (used as ID)."""
        point_id = self._query_to_point_id(query)

        try:
            # Retrieve a single point by its ID.
            points = self._client.retrieve(
                collection_name=self._collection_name,
                ids=[point_id],
                with_payload=True,
            )
            if points:
                return points[0].payload
        # Catch potential exceptions if the point doesn't exist or the client fails.
        except Exception:
            pass
        return None

    def _rerank_score(
        self,
        query: str,
        matches: List[Dict],
        k_rank: Optional[int] = None,
    ) -> List[Dict]:
        """Rerank matches using the reranker model."""
        if k_rank is None:
            k_rank = config["cache"]["num_rank2_documents"]

        # Extract the original queries from the matched documents to be reranked.
        documents = [record["query"] for record in matches]
        # Compute reranking scores for the query against the candidate documents.
        scores = self.reranker_model.compute_score(
            [[query, doc] for doc in documents], normalize=True
        )

        # Pair each match with its corresponding reranker score.
        if len(documents) > 1:
            docs_scores = list(zip(matches, scores))
        else:
            docs_scores = [(matches[i], scores) for i in range(len(documents))]

        # Sort the matches based on the new scores in descending order and take the top k_rank.
        docs_scores_sorted = sorted(docs_scores, key=lambda x: x[1], reverse=True)[
            :k_rank
        ]
        # Return only the document payloads, not the scores.
        returned_matches = [match for match, _ in docs_scores_sorted]
        return returned_matches

    def get_embedding_match(
        self,
        query: str,
        threshold: float,
        knn: int,
    ) -> List[Dict]:
        """
        Find similar documents using embedding similarity.

        Args:
            query: The query string to match
            threshold: Maximum distance threshold (lower = more similar)
            knn: Number of nearest neighbors to retrieve

        Returns:
            List of matching document metadata
        """
        embedding = self._get_embedding(query)

        # Qdrant uses cosine similarity (higher is better). A score of 1 means identical.
        # The input 'threshold' is a distance metric (lower is better).
        # We convert the distance threshold to a similarity threshold for the Qdrant query.
        similarity_threshold = 1 - threshold

        # Perform the vector search in the Qdrant collection.
        results = self._client.search(
            collection_name=self._collection_name,
            query_vector=embedding,
            limit=knn,
            with_payload=True,
            score_threshold=similarity_threshold,
        )

        matches = []
        if len(results) == 1:
            # For a single result, check if it meets the distance threshold.
            distance = 1 - results[0].score
            if distance <= threshold:
                matches = [results[0].payload]
        else:
            # For multiple results, filter them by the distance threshold.
            for result in results:
                distance = 1 - result.score
                if distance <= threshold:
                    matches.append(result.payload)
            # If there are multiple valid matches, rerank them for better relevance.
            if len(matches) > 0:
                matches = self._rerank_score(query, matches, k_rank=knn)

        return matches

    def _thumb_up_down_incrementor(
        self,
        query: str,
        response: str,
        url: str,
        field_name: str,
    ) -> None:
        """Atomically increments a counter field (thumb_up, thumb_down, or flag)."""
        # Check if the document already exists in the cache.
        record = self._get_row(query)
        if record:
            new_value = record.get(field_name, 0) + 1
            self._update_row(query, {field_name: new_value})
        else:
            # If the document doesn't exist, create it with the counter field set to 1.
            self._insert_row(
                query=query,
                response=response,
                url=url,
                thumb_up=1 if field_name == "thumb_up" else 0,
                thumb_down=1 if field_name == "thumb_down" else 0,
                flag=1 if field_name == "flag" else 0,
            )

    def increment_thumb_up(self, query: str, response: str, url: str) -> None:
        """Increment the thumb_up counter for a query."""
        self._thumb_up_down_incrementor(query, response, url, "thumb_up")

    def increment_thumb_down(self, query: str, response: str, url: str) -> None:
        """Increment the thumb_down counter for a query."""
        self._thumb_up_down_incrementor(query, response, url, "thumb_down")

    def increment_flag(self, query: str, response: str, url: str) -> None:
        """Increment the flag counter for a query."""
        self._thumb_up_down_incrementor(query, response, url, "flag")

    @staticmethod
    def _build_must_conditions(filters: Dict[str, Any]) -> List[Any]:
        must_conditions = []
        for key, value in filters.items():
            if isinstance(value, dict):
                # FIX: Strip the '$' from keys like '$gte' so they become 'gte'
                range_params = {
                    k.replace("$", ""): v
                    for k, v in value.items()
                    if k in ["$gte", "$gt", "$lte", "$lt"]
                }
                if range_params:
                    must_conditions.append(
                        FieldCondition(
                            key=key,
                            range=Range(**range_params),
                        )
                    )
            else:
                must_conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value),
                    )
                )
        return must_conditions

    def filter_documents(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Retrieve documents that match the specified metadata filters.

        Args:
            filters: A dictionary where keys are metadata fields
                    and values are the desired values or filter conditions.

        Returns:
            List of metadata dictionaries for matching documents.
        """
        must_conditions = self._build_must_conditions(filters)
        scroll_filter = Filter(must=must_conditions) if must_conditions else None

        all_results = []
        offset = None
        results, next_offset = [], None

        while True:
            try:
                results, next_offset = self._client.scroll(
                    collection_name=self._collection_name,
                    scroll_filter=scroll_filter,
                    with_payload=True,
                    limit=100,
                    offset=offset,
                )
            except Exception:
                break

            all_results.extend([point.payload for point in results])

            if next_offset is None:
                break
            offset = next_offset

        return all_results

    def get_documents_with_metadata_field(
        self, field_name: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all documents that contain a specific metadata field.

        Args:
            field_name: The metadata field to filter by.

        Returns:
            List of metadata dictionaries for matching documents.
        """
        if field_name in ["thumb_up", "thumb_down", "flag"]:
            filters = {field_name: {"$gte": 0}}
            return self.filter_documents(filters)

        scroll_filter = Filter(
            must_not=[
                IsEmptyCondition(
                    is_empty=models.PayloadField(key=field_name)
                )
            ]
        )

        all_results = []

        while True:
            try:
                results, next_offset = self._client.scroll(
                    collection_name=self._collection_name,
                    scroll_filter=scroll_filter,
                    with_payload=True,
                    limit=100,
                    offset=offset,
                )
            except Exception:
                break

            all_results.extend([point.payload for point in results])

            if next_offset is None:
                break
            offset = next_offset

        return all_results

    def delete_document(self, query: str) -> None:
        """
        Delete a specific document from the Qdrant collection based on its query.

        Args:
            query: The unique identifier (query) of the document to delete.
        """
        if self._get_row(query) is not None:
            point_id = self._query_to_point_id(query)
            self._client.delete(
                collection_name=self._collection_name,
                points_selector=models.PointIdsList(points=[point_id]),
            )


# Example usage and testing
def temp():
    """A temporary async function for demonstrating and testing the Cache class."""
    response = "سلام. من دستیار دیجیتال نسل 4 هستم. می‌توانم در مورد ماژول‌های دفتر کل، انبار، گزارش ساز و خزانه داری به شما کمک کنم. پرسش خود را بپرسید تا در صورت امکان، پاسخ آن را ارائه دهم."
    lst_1 = [
        "سلام. خوبی؟",
        "سلام. حالت چطوره",
        "سلام خوبی",
        "سلام خوبی؟",
        "سلام حالت خوبه",
        "سلام.",
        "سلام",
        "سلام خوبی",
        "سلام. خوبی",
        "درود",
        "سلام علیکم",
        "سلام و ارادت",
        "عرض ادب و احترام",
        "سلامعلیکم",
        "سلام صبح بخیر",
        "صبح بخیر",
        "سلام ظهر بخیر",
        "ظهر بخیر",
        "سلام. صبح بخیر",
    ]

    response_2 = "خواهش میکنم. اگر سوال دیگری بود در خدمتم "
    lst_2 = [
        "خیلی ممنون",
        "لطف کردی",
        "زحمت دادم. ",
        "دمت گرم",
        "متشکرم",
        "خیلی متشکرم",
        "متچکرم",
        "ممنون از پاسخت",
        "متشکر از پاسخ شما",
        "ممنونم که جواب دادی",
        "جواب خوبی بود. مرسی",
        "مرسی",
        "مرسی. ممنون",
        "مرسی. متشکر",
        "مرسی تشکر.",
        "تشکر. ",
        "ممنونم",
    ]

    print("Initializing cache...")

    qdrant_host = os.getenv("QDRANT_API_BASE")
    qdrant_port = os.getenv("QDRANT_API_PORT")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    try:
        qdrant_client_temp = QdrantClient(
            host=qdrant_host,
            port=qdrant_port,
            api_key=qdrant_api_key,
            timeout=60,
            prefer_grpc=False,
            https=False,
        )
    except Exception:
        qdrant_client_temp = QdrantClient(
            url=f"https://{qdrant_host}:{qdrant_port}",
            api_key=qdrant_api_key,
            timeout=60,
            verify=False,
        )

    cache = Cache()
    cache.initialize(recreate=True, qdrant_client_instance=qdrant_client_temp)
    for query in lst_1:
        cache.increment_thumb_up(query, response, "")

    for query in lst_2:
        cache.increment_thumb_up(query, response_2, "")

    print("Done!")
