import asyncio
import os
import uuid
from typing import Any, List, Mapping, Optional, Dict

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    Range,
)
import redis
from dotenv import load_dotenv

from .config import config
from .retriever import ModelManager
from .initiate_vdb import qdrant_client

REDIS_HOST = os.environ.get("REDIS_HOST", "185.13.230.222")
REDIS_PORT = os.environ.get("REDIS_PORT", "6380")


class Cache:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.initialize(**kwargs)
        return cls._instance

    def initialize(
        self,
        exact_cache: bool = True,
        recreate: bool = False
    ) -> None:
        """
        Initialize the cache with a Qdrant client.

        Args:
            qdrant_client: Pre-configured QdrantClient instance from external code
            exact_cache: Whether to use Redis for exact caching
        """
        if exact_cache:
            self.redis_db = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=0,
                decode_responses=True,
            )
        model_manager = ModelManager()
        self.embedding_model = model_manager.embedding_model
        # self.reranker_model = model_manager.reranker_model

        self._client = qdrant_client
        self._collection_name = config["cache"]["index_name"]

        # Get embedding dimension from a sample embedding
        sample_embedding = self.embedding_model.embed_query("sample")
        self._embedding_dim = len(sample_embedding)

        # Ensure collection exists
        self._ensure_collection_exists(recreate=recreate)

    def _ensure_collection_exists(self, recreate) -> None:
        """Create the collection if it doesn't exist."""
        # collections = self._client.get_collections().collections
        # collection_names = [c.name for c in collections]

        # if self._collection_name not in collection_names:
        if recreate:
            qdrant_client.delete_collection(collection_name=self._collection_name)    
            self._client.create_collection(
                collection_name=self._collection_name,
                vectors_config=VectorParams(
                    size=self._embedding_dim,
                    distance=Distance.COSINE,
                ),
            )
            # Create payload index for query field to enable filtering
            self._client.create_payload_index(
                collection_name=self._collection_name,
                field_name="query",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
            # Create payload indices for numeric fields
            for field in ["thumb_up", "thumb_down", "flag"]:
                self._client.create_payload_index(
                    collection_name=self._collection_name,
                    field_name=field,
                    field_schema=models.PayloadSchemaType.INTEGER,
                )
            

    def get_exact_cache(self, query: str) -> Optional[str]:
        """Get exact match from Redis cache."""
        route_response_cached = self.redis_db.get(query)
        return route_response_cached

    def set_exact_cache(self, key: str, value: str) -> None:
        """Set exact match in Redis cache."""
        self.redis_db.set(key, value)

    def _get_embedding(self, query: str) -> List[float]:
        """Get embedding vector for a query."""
        return self.embedding_model.embed_query(query)

    def _query_to_point_id(self, query: str) -> str:
        """
        Generate a deterministic UUID from query string.
        This ensures the same query always maps to the same point ID.
        """
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, query))

    async def _insert_row(
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

        payload = {
            "query": query,
            "response": response,
            "url": url,
            "thumb_up": thumb_up,
            "thumb_down": thumb_down,
            "flag": flag,
        }

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

    async def _update_row(
        self,
        query: str,
        mapping: Mapping[str, Any],
    ) -> None:
        """Update an existing row or insert if not exists."""
        existing_record = await self._get_row(query)
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
            # Insert new record with default values
            await self._insert_row(
                query=query,
                response=mapping.get("response", ""),
                url=mapping.get("url", ""),
                thumb_up=mapping.get("thumb_up", 0),
                thumb_down=mapping.get("thumb_down", 0),
                flag=mapping.get("flag", 0),
            )

    async def _get_row(self, query: str) -> Optional[Dict[str, Any]]:
        """Retrieve a row by query (used as ID)."""
        point_id = self._query_to_point_id(query)

        try:
            points = self._client.retrieve(
                collection_name=self._collection_name,
                ids=[point_id],
                with_payload=True,
            )
            if points:
                return points[0].payload
        except Exception:
            pass
        return None

    async def _rerank_score(
        self,
        query: str,
        matches: List[Dict],
        k_rank: int = None,
    ) -> List[Dict]:
        """Rerank matches using the reranker model."""
        if k_rank is None:
            k_rank = config["cache"]["num_rank2_documents"]

        documents = [record["query"] for record in matches]
        scores = self.reranker_model.compute_score(
            [[query, doc] for doc in documents], normalize=True
        )

        if len(documents) > 1:
            docs_scores = [(matches[i], scores[i]) for i in range(len(documents))]
        else:
            docs_scores = [(matches[i], scores) for i in range(len(documents))]

        docs_scores_sorted = sorted(docs_scores, key=lambda x: x[1], reverse=True)[
            :k_rank
        ]
        returned_matches = [match for match, _ in docs_scores_sorted]
        return returned_matches

    async def get_embedding_match(
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

        # Qdrant returns cosine similarity score (1 = identical, 0 = orthogonal, -1 = opposite)
        # Convert threshold from distance to similarity: similarity = 1 - distance
        similarity_threshold = 1 - threshold

        results = self._client.search(
            collection_name=self._collection_name,
            query_vector=embedding,
            limit=knn,
            with_payload=True,
            score_threshold=similarity_threshold,
        )

        matches = []
        if len(results) == 1:
            # Convert similarity back to distance for threshold comparison
            distance = 1 - results[0].score
            if distance <= threshold:
                matches = [results[0].payload]
        else:
            for result in results:
                distance = 1 - result.score
                if distance <= threshold:
                    matches.append(result.payload)
            if len(matches) > 0:
                matches = await self._rerank_score(query, matches)

        return matches

    async def _thumb_up_down_incrementor(
        self,
        query: str,
        response: str,
        url: str,
        field_name: str,
    ) -> None:
        """Increment a counter field (thumb_up, thumb_down, or flag)."""
        record = await self._get_row(query)
        if record:
            new_value = record.get(field_name, 0) + 1
            await self._update_row(query, {field_name: new_value})
        else:
            # Insert new record with the specific field incremented
            await self._insert_row(
                query=query,
                response=response,
                url=url,
                thumb_up=1 if field_name == "thumb_up" else 0,
                thumb_down=1 if field_name == "thumb_down" else 0,
                flag=1 if field_name == "flag" else 0,
            )

    async def increment_thumb_up(self, query: str, response: str, url: str) -> None:
        """Increment the thumb_up counter for a query."""
        await self._thumb_up_down_incrementor(query, response, url, "thumb_up")

    async def increment_thumb_down(self, query: str, response: str, url: str) -> None:
        """Increment the thumb_down counter for a query."""
        await self._thumb_up_down_incrementor(query, response, url, "thumb_down")

    async def increment_flag(self, query: str, response: str, url: str) -> None:
        """Increment the flag counter for a query."""
        await self._thumb_up_down_incrementor(query, response, url, "flag")

    async def filter_documents(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Retrieve documents that match the specified metadata filters.

        Args:
            filters: A dictionary where keys are metadata fields
                    and values are the desired values or filter conditions.

        Returns:
            List of metadata dictionaries for matching documents.
        """
        must_conditions = []

        for key, value in filters.items():
            if isinstance(value, dict):
                # Handle range queries like {"$gte": 0}
                range_params = {}
                if "$gte" in value:
                    range_params["gte"] = value["$gte"]
                if "$gt" in value:
                    range_params["gt"] = value["$gt"]
                if "$lte" in value:
                    range_params["lte"] = value["$lte"]
                if "$lt" in value:
                    range_params["lt"] = value["$lt"]

                if range_params:
                    must_conditions.append(
                        FieldCondition(
                            key=key,
                            range=Range(**range_params),
                        )
                    )
                elif "$ne" in value:
                    # For $ne, we need to use must_not (handled separately)
                    pass
            else:
                # Exact match
                must_conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value),
                    )
                )

        scroll_filter = Filter(must=must_conditions) if must_conditions else None

        # Scroll through all matching documents
        all_results = []
        offset = None

        while True:
            results, next_offset = self._client.scroll(
                collection_name=self._collection_name,
                scroll_filter=scroll_filter,
                with_payload=True,
                limit=100,
                offset=offset,
            )

            all_results.extend([point.payload for point in results])

            if next_offset is None:
                break
            offset = next_offset

        return all_results

    async def get_documents_with_metadata_field(
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
            # For numeric fields, retrieve where field >= 0
            filters = {field_name: {"$gte": 0}}
        else:
            # For other fields, we need a different approach
            # Qdrant doesn't have direct "field exists" filter
            # Using IsNotNull condition
            scroll_filter = Filter(
                must=[
                    models.IsNotNullCondition(
                        is_not_null=models.PayloadField(key=field_name)
                    )
                ]
            )

            all_results = []
            offset = None

            while True:
                results, next_offset = self._client.scroll(
                    collection_name=self._collection_name,
                    scroll_filter=scroll_filter,
                    with_payload=True,
                    limit=100,
                    offset=offset,
                )

                all_results.extend([point.payload for point in results])

                if next_offset is None:
                    break
                offset = next_offset

            return all_results

        return await self.filter_documents(filters)

    async def delete_document(self, query: str) -> None:
        """
        Delete a specific document from the Qdrant collection based on its query.

        Args:
            query: The unique identifier (query) of the document to delete.
        """
        if await self._get_row(query) is not None:
            point_id = self._query_to_point_id(query)
            self._client.delete(
                collection_name=self._collection_name,
                points_selector=models.PointIdsList(points=[point_id]),
            )


# Example usage and testing
async def temp():
    response =  "سلام. من دستیار دیجیتال نسل 4 هستم. می‌توانم در مورد ماژول‌های دفتر کل، انبار، گزارش ساز و خزانه داری به شما کمک کنم. پرسش خود را بپرسید تا در صورت امکان، پاسخ آن را ارائه دهم."
    lst_1 = ["سلام. خوبی؟",
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
            "سلامعلیکم"
            "سلام صبح بخیر",
            "سلام صبحت بخیر",
            "صبح بخیر",
            "سلام ظهر بخیر",
            "ظهر بخیر",
            "سلام روز بخیر",
            "سلام. صبح بخیر"
            ]
    
    response_2 = "خواهش میکنم. اگر سوال دیگری بود در خدمتم "
    lst_2 = ["خیلی ممنون",
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
        qdrant_client = QdrantClient(
            host=qdrant_host,
            port=qdrant_port,
            api_key=qdrant_api_key,
            timeout=60,
            prefer_grpc=False,
            https=False,
        )
    except Exception as e:
        qdrant_client = QdrantClient(
            url=f"https://{qdrant_host}:{qdrant_port}",
            api_key=qdrant_api_key,
            timeout=60,
            verify=False,
        )

    # Or for Qdrant Cloud:
    # qdrant_client = QdrantClient(url="https://your-cluster.qdrant.io", api_key="your-api-key")

    cache = Cache(recreate=True)
    cache.initialize(qdrant_client)
    for query in lst_1:
        await cache.increment_thumb_up(query, response, "")

    for query in lst_2:
        await cache.increment_thumb_up(query, response_2, "")

    print("Done!")


if __name__ == "__main__":
    asyncio.run(temp())
    
