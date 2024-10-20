import os
from typing import Any, List, Mapping, Optional, Dict

import numpy as np
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings  # Ensure compatibility
from FlagEmbedding import FlagReranker

from config import config
from retriever import ModelManager


class Cache:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance


    def _initialize(self):
        model_manager = ModelManager()
        self.embedding_model = model_manager.embedding_model
        self.reranker_model = model_manager.reranker_model

        # Initialize Chroma with persistence
        persist_directory = config["cache"].get("persist_directory", "../../cache_db")
        self._collection_name = config["cache"]["index_name"]

        # Initialize the Chroma vector store
        self._vector_store = Chroma(
            collection_name=self._collection_name,
            embedding_function=self.embedding_model,
            persist_directory=persist_directory,
        )


    def _get_embedding(self, query: str) -> List[float]:
        return self.embedding_model.embed_query(query)

    def _insert_row(
        self,
        query: str,
        response: str,
        url: str,
        thumb_up: int,
        thumb_down: int,
        flag: int,
    ) -> None:
        embedding = self._get_embedding(query)
        metadata = {
            "query": query,
            "response": response,
            "url": url,
            "thumb_up": thumb_up,
            "thumb_down": thumb_down,
            "flag": flag,
        }
        self._vector_store.add_texts(
            texts=[query],  # The text is the query itself
            metadatas=[metadata],
            embeddings=[embedding],
            ids=[query],  # Using query as the unique ID
        )
        # self._vector_store.persist()

    def _update_row(
        self,
        query: str,
        mapping: Mapping[str, Any],
    ) -> None:
        existing_record = self._get_row(query)
        if existing_record:
            metadata = existing_record.copy()
            metadata.update(mapping)
            # Remove the 'query' field if present, since it's the ID
            metadata.pop("query", None)
            # Update the record by re-adding it with the updated metadata
            self._vector_store.add_texts(
                texts=[query],
                metadatas=[metadata],
                embeddings=[self._get_embedding(query)],
                ids=[query],
            )
            # self._vector_store.persist()
        else:
            # If the record doesn't exist, insert it with default values
            self._insert_row(
                query=query,
                response=mapping.get("response", ""),
                url=mapping.get("url", ""),
                thumb_up=mapping.get("thumb_up", 0),
                thumb_down=mapping.get("thumb_down", 0),
                flag=mapping.get("flag", 0),
            )

    def _get_row(self, query: str) -> Optional[dict[str, Any]]:
        results = self._vector_store.get(
            ids=[query],
            include=["metadatas"],
        )
        if results and results["metadatas"]:
            return results["metadatas"][0]
        return None

    def _rerank_score(
        self,
        query: str,
        matches: List[Dict],
        k_rank: int = config["cache"]["num_rank2_documents"],
    ):
        
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
        returned_matches = [matches[0] for matches in docs_scores_sorted]
        return returned_matches

    def get_embedding_match(
        self,
        query: str,
        threshold: float,
        knn: int,
    ) -> List[dict]:
        embedding = self._get_embedding(query)
        results = self._vector_store.similarity_search_with_score(query, k=knn)
        matches = []
        if len(results) == 1:
            doc, score = results[0]
            if score < threshold:
                matches = [doc.metadata]
        else:
            for doc, score in results:
                # Assuming cosine similarity, score ranges between 0 and 2
                # Convert to cosine distance if necessary
                # Adjust the threshold comparison based on actual distance metric
                if score <= threshold:
                    matches.append(doc.metadata)
            if len(matches) > 0:
                matches = self._rerank_score(query, matches)
        return matches

    def _thumb_up_down_incrementor(
        self,
        query: str,
        response: str,
        url: str,
        field_name: str,
    ) -> None:
        record = self._get_row(query)
        if record:
            new_value = record.get(field_name, 0) + 1
            self._update_row(query, {field_name: new_value})
        else:
            # Insert a new record with default counts and increment the specific field
            self._insert_row(
                query=query,
                response=response,
                url=url,
                thumb_up=1 if field_name == "thumb_up" else 0,
                thumb_down=1 if field_name == "thumb_down" else 0,
                flag=1 if field_name == "flag" else 0,
            )

    def increment_thumb_up(self, query: str, response: str, url: str) -> None:
        self._thumb_up_down_incrementor(
            query,
            response,
            url,
            "thumb_up",
        )

    def increment_thumb_down(self, query: str, response: str, url: str) -> None:
        self._thumb_up_down_incrementor(
            query,
            response,
            url,
            "thumb_down",
        )

    def increment_flag(self, query: str, response: str, url: str) -> None:
        self._thumb_up_down_incrementor(
            query,
            response,
            url,
            "flag",
        )

    def filter_documents(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Retrieve documents that match the specified metadata filters.

        Args:
            filters (Dict[str, Any]): A dictionary where keys are metadata fields
                                    and values are the desired values.

        Returns:
            List[Dict[str, Any]]: A list of metadata dictionaries for matching documents.
        """
        results = self._vector_store.get(
            where=filters,
            include=["metadatas"],
        )
        matched_docs = []
        if results and results["metadatas"]:
            for metadata in results["metadatas"]:
                matched_docs.append(metadata)
        return matched_docs

    def get_documents_with_metadata_field(
        self, field_name: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all documents that contain a specific metadata field.

        Args:
            field_name (str): The metadata field to filter by.

        Returns:
            List[Dict[str, Any]]: A list of metadata dictionaries for matching documents.
        """
        # ChromaDB via LangChain doesn't support direct existence checks.
        # As a workaround, retrieve documents where the field is not null or set to a default value.
        # For numeric fields, you might use a range filter.
        # For string fields, you might check for non-empty strings.

        # Here, we'll assume 'flag' is an integer and retrieve all documents where 'flag' >= 0
        if field_name in ["thumb_up", "thumb_down", "flag"]:
            filters = {field_name: {"$gte": 0}}
        else:
            # For other fields, adjust accordingly
            filters = {field_name: {"$ne": None}}

        return self.filter_documents(filters)

    def delete_document(self, query: str) -> None:
        """
        Delete a specific document from the ChromaDB dataset based on its query (ID).

        Args:
            query (str): The unique identifier (query) of the document to delete.
        """
        if self._get_row(query) is not None:
            self._vector_store.delete(ids=[query])
        # self._vector_store.persist()



# if __name__ == "__main__":
    
#     lst = [("سلام.", """سلام! 👋
#     چطور میتونم کمکتون کنم؟ 😊
#     """), ("سلام. خوبی؟", """سلام! 
#     چطور میتونم کمکتون کنم؟ 😊
#     """),("سلام. خوبی", """سلام! 👋
#     چطور میتونم کمکتون کنم؟ 😊
#     """),("درود", """سلام! 👋
#     چطور میتونم کمکتون کنم؟ 😊
#     """),("سلام علیکم", """سلام! 👋
#     چطور میتونم کمکتون کنم؟ 😊
#     """),("سلام و ارادت", """سلام! 👋
#     چطور میتونم کمکتون کنم؟ 😊
#     """),("عرض ادب و احترام", """سلام! 👋
#     چطور میتونم کمکتون کنم؟ 😊
#     """),("سلامعلیکم", """سلام! 👋
#     چطور میتونم کمکتون کنم؟ 😊
#     """),
#         ("خیلی ممنون", "خواهش میکنم. اگر سوال دیگری بود در خدمتم. "), 
#         ("لطف کردی", "خواهش میکنم. اگر سوال دیگری بود در خدمتم. "), 
#         ("زحمت دادم. ", "خواهش میکنم. اگر سوال دیگری بود در خدمتم. "), 
#         ("دمت گرم", "خواهش میکنم. اگر سوال دیگری بود در خدمتم. "), 
#         ("متشکرم", "خواهش میکنم. اگر سوال دیگری بود در خدمتم. "), 
#         ("خیلی متشکرم", "خواهش میکنم. اگر سوال دیگری بود در خدمتم. "), 
#         ("متچکرم", "خواهش میکنم. اگر سوال دیگری بود در خدمتم. "), 
#         ("ممنون از پاسخت", "خواهش میکنم. اگر سوال دیگری بود در خدمتم. "), 
#         ("متشکر از پاسخ شما", "خواهش میکنم. اگر سوال دیگری بود در خدمتم. "), 
#         ("ممنونم که جواب دادی", "خواهش میکنم. اگر سوال دیگری بود در خدمتم. "), 
#         ("جواب خوبی بود. مرسی", "خواهش میکنم. اگر سوال دیگری بود در خدمتم. "), 
#         ("مرسی", "خواهش میکنم. اگر سوال دیگری بود در خدمتم. "), 
#         ("مرسی. ممنون", "خواهش میکنم. اگر سوال دیگری بود در خدمتم. "), 
#         ("مرسی. متشکر", "خواهش میکنم. اگر سوال دیگری بود در خدمتم. "),
#         ("مرسی تشکر.", "خواهش میکنم. اگر سوال دیگری بود در خدمتم. "),
#         ("تشکر. ", "خواهش میکنم. اگر سوال دیگری بود در خدمتم. ")
#         ]
        
#     cache = Cache()
#     for query, response in lst:
#         cache.increment_thumb_up(query, response, "")
    
    
# import os
# from typing import Any, List, Mapping

# import numpy as np
# import chromadb
# from chromadb.config import Settings
# from FlagEmbedding import FlagReranker
# from langchain_community.embeddings import HuggingFaceEmbeddings

# from config import config


# class Cache:
#     _instance = None

#     def __new__(cls, *args, **kwargs):
#         if not cls._instance:
#             cls._instance = super().__new__(cls, *args, **kwargs)

#             cls._instance.embedding_model = HuggingFaceEmbeddings(
#                 model_name=config["embedding_model"]["model_name"],
#                 model_kwargs={"device": config["embedding_model"]["device"]},
#             )

#             cls._instance.reranker_model = FlagReranker(
#                 config["reranker"]["model_name"],
#                 device=config["reranker"]["device"],
#             )

#             # Initialize ChromaDB client with persistence
#             persist_directory = config["cache"].get("persist_directory", "./cache_db")
#             cls._instance._client = chromadb.Client(
#                 Settings(
#                     persist_directory=persist_directory,
#                     chroma_db_impl="duckdb+parquet",
#                 )
#             )
#             cls._instance._collection_name = config["cache"]["index_name"]
#             # Get or create collection
#             cls._instance._collection = cls._instance._client.get_or_create_collection(
#                 name=cls._instance._collection_name
#             )

#         return cls._instance

#     def _get_embedding(self, query: str) -> List[float]:
#         return self.embedding_model.embed_query(query)

#     def _insert_row(
#         self,
#         query: str,
#         response: str,
#         url: str,
#         thumb_up: int,
#         thumb_down: int,
#         flag: int,
#     ) -> None:
#         embedding = self._get_embedding(query)
#         metadata = {
#             "query": query,
#             "response": response,
#             "url": url,
#             "thumb_up": thumb_up,
#             "thumb_down": thumb_down,
#             "flag": flag,
#         }
#         self._collection.upsert(
#             ids=[query],
#             embeddings=[embedding],
#             metadatas=[metadata],
#         )

#     def _update_row(
#         self,
#         query: str,
#         mapping: Mapping[str, Any],
#     ) -> None:
#         # Get existing metadata
#         results = self._collection.get(ids=[query], include=["metadatas"])
#         if results and results["metadatas"]:
#             metadata = results["metadatas"][0]
#         else:
#             metadata = {}
#         # Update metadata
#         metadata.update(mapping)
#         # Update the record
#         self._collection.update(
#             ids=[query],
#             metadatas=[metadata],
#         )

#     def _get_row(self, query: str) -> dict[str, Any]:
#         results = self._collection.get(ids=[query], include=["metadatas"])
#         if results and results["metadatas"]:
#             return results["metadatas"][0]
#         else:
#             return {}

#     def get_embedding_match(
#         self,
#         query: str,
#         threshold: float,
#         knn: int,
#     ) -> List[dict]:
#         embedding = self._get_embedding(query)
#         results = self._collection.query(
#             query_embeddings=[embedding],
#             n_results=knn,
#             include=["metadatas", "distances"],
#         )
#         # Filter results by threshold
#         matches = []
#         if results and results["metadatas"]:
#             for metadata, distance in zip(
#                 results["metadatas"][0], results["distances"][0]
#             ):
#                 if distance <= threshold:
#                     matches.append(metadata)
#         return matches

#     def _thumb_up_down_incrementor(
#         self,
#         query: str,
#         response: str,
#         url: str,
#         field_name: str,
#     ) -> None:
#         # Get existing metadata
#         results = self._collection.get(ids=[query], include=["metadatas"])
#         if results and results["metadatas"]:
#             metadata = results["metadatas"][0]
#         else:
#             # Record does not exist, insert a new one
#             self._insert_row(
#                 query=query,
#                 response=response,
#                 url=url,
#                 thumb_up=0,
#                 thumb_down=0,
#                 flag=0,
#             )
#             metadata = {
#                 "query": query,
#                 "response": response,
#                 "url": url,
#                 "thumb_up": 0,
#                 "thumb_down": 0,
#                 "flag": 0,
#             }
#         # Increment the field
#         metadata[field_name] = metadata.get(field_name, 0) + 1
#         # Update the record
#         self._collection.update(
#             ids=[query],
#             metadatas=[metadata],
#         )

#     def increment_thumb_up(self, query: str, response: str, url: str) -> None:
#         self._thumb_up_down_incrementor(
#             query,
#             response,
#             url,
#             "thumb_up",
#         )

#     def increment_thumb_down(self, query: str, response: str, url: str) -> None:
#         self._thumb_up_down_incrementor(
#             query,
#             response,
#             url,
#             "thumb_down",
#         )

#     def increment_flag(self, query: str, response: str, url: str) -> None:
#         self._thumb_up_down_incrementor(
#             query,
#             response,
#             url,
#             "flag",
#         )


# import os
# from typing import Any, List, Mapping

# import numpy as np
# from redis import Redis
# from redis.commands.search.query import Query
# from redis.commands.search.document import Document  # type: ignore
# from FlagEmbedding import FlagReranker
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from redis.commands.search.field import VectorField, TextField
# from redis.commands.search.indexDefinition import IndexDefinition, IndexType
# from redis.commands.search.field import (
# NumericField,
# TextField,
# VectorField,
# )
# from redis.commands.search.indexDefinition import IndexDefinition, IndexType

# from config import config


# class Cache:
#     _instance = None
#     def __new__(cls, *args, **kwargs):
#         if not cls._instance:
#             cls._instance = super().__new__(cls, *args, **kwargs)

#             cls._instance.embedding_model = HuggingFaceEmbeddings(
#                 model_name=config["embedding_model"]["model_name"],
#                 model_kwargs={
#                     "device": config["embedding_model"]["device"]
#                 },
#             )

#             cls._instance.reranker_model = FlagReranker(
#                 config["reranker"]["model_name"],
#                 device=config["reranker"]["device"],
#             )

#             cls._instance._connection = Redis(
#                 # host=config["cache"]["host"],  # TODO: this should be transfer to secret
#                 # host="127.0.0.1",
#                 host="172.17.0.2",
#                 port=config["cache"]["port"],  # # TODO: this should be transfer to secret
#                 socket_timeout=config["cache"]["socket_timeout"],
#                 # password="myRedisPassword123!@#",
#             )

#             cls._instance._index_name = config["cache"]["index_name"]

#             cls._instance._schema = {
#                 "query_field": {
#                     "name": config["cache"]["schema"]["query_field_name"],
#                     "type": str,
#                 },
#                 "vector_field": {
#                     "name": config["cache"]["schema"]["vector_field_name"],
#                     "type": np.ndarray,
#                 },
#                 "answer_field": {
#                     "name": config["cache"]["schema"]["answer_field_name"],
#                     "type": str,
#                 },
#                 "url_field": {
#                     "name": config["cache"]["schema"]["url_field_name"],
#                     "type": str,
#                 },
#                 "thumb_up_field": {
#                     "name": config["cache"]["schema"]["thumb_up_field_name"],
#                     "type": int,
#                 },
#                 "thumb_down_field": {
#                     "name": config["cache"]["schema"]["thumb_down_field_name"],
#                     "type": int,
#                 },
#                 "flag_field": {
#                     "name": config["cache"]["schema"]["flag_field_name"],
#                     "type": int,
#                 },
#             }

#             if not cls._instance.index_exists():
#                 cls._instance.create_index()

#         return cls._instance


#     def index_exists(self) -> bool:
#         try:
#             self._connection.ft(self._index_name).info()
#             return True
#         except Exception:
#             print("index created")
#             # If there's an exception, it means the index doesn't exist
#             return False

#     def create_index(self):
#         schema = [
#             TextField(name=self._schema["query_field"]["name"]),
#             TextField(name=self._schema["answer_field"]["name"]),
#             TextField(name=self._schema["url_field"]["name"]),
#             NumericField(name=self._schema["thumb_up_field"]["name"]),
#             NumericField(name=self._schema["thumb_down_field"]["name"]),
#             NumericField(name=self._schema["flag_field"]["name"]),
#             VectorField(
#                 self._schema["vector_field"]["name"],
#                 "HNSW",  # or "FLAT" depending on your needs
#                 {
#                     "TYPE": "FLOAT64",
#                     "DIM": len(self.embedding_model.embed_query("test")),
#                     "DISTANCE_METRIC": "COSINE",
#                 },
#             ),
#         ]

#         definition = IndexDefinition(prefix=["query:"], index_type=IndexType.HASH)
#         self._connection.ft(self._index_name).create_index(
#             schema, definition=definition
#         )

#     def _get_list_of_allowed_fields(self) -> List[str]:
#         return [
#             self._schema["query_field"]["name"],
#             self._schema["answer_field"]["name"],
#             self._schema["url_field"]["name"],
#             self._schema["thumb_up_field"]["name"],
#             self._schema["thumb_down_field"]["name"],
#             self._schema["flag_field"]["name"],
#         ]

#     def _decode_redis_output(self, field: str, value: bytes | None) -> Any:
#         if value is None:
#             return None
#         else:
#             field_name = f"{field}_field"
#             _type = self._schema[field_name]["type"]
#             return _type(value)

#     def _parse_redis_record(self, record: dict[str, bytes | None]) -> dict[str, Any]:
#         parsed_output = {
#             key: self._decode_redis_output(key, value) for key, value in record.items()
#         }
#         return parsed_output

#     def _parse_redis_document_object(self, redis_document: Document) -> dict[str, Any]:
#         document_dict = dict(redis_document.__dict__)

#         del document_dict["id"]
#         del document_dict["payload"]

#         return {
#             key: self._decode_redis_output(key, value)
#             for key, value in document_dict.items()
#         }

#     def _get_embedding(self, query: str) -> bytes:
#         return (
#             np.array(self.embedding_model.embed_query(query))
#             .astype(np.float64)
#             .tobytes()
#         )

#     def _insert_row(
#         self,
#         query: str,
#         response: str,
#         url: str,
#         thumb_up: int,
#         thumb_down: int,
#         flag: int,
#     ) -> None:
#         key_name = f"query:{query}"
#         self._connection.hset(
#             name=key_name,
#             mapping={
#                 self._schema["query_field"]["name"]: query,
#                 self._schema["vector_field"]["name"]: self._get_embedding(query),
#                 self._schema["answer_field"]["name"]: response,
#                 self._schema["url_field"]["name"]: url,
#                 self._schema["thumb_up_field"]["name"]: thumb_up,
#                 self._schema["thumb_down_field"]["name"]: thumb_down,
#                 self._schema["flag_field"]["name"]: flag,
#             },
#          )

#     def _update_row(
#         self,
#         query: str,
#         mapping: Mapping[str | bytes, bytes | float | int | str],
#     ) -> None:
#         key_name = f"query:{query}"
#         self._connection.hset(
#             name=key_name,
#             mapping=mapping,
#         )

#     @staticmethod
#     def to_none_if_all_none(record):
#         return None if all(item is None for item in record) else record


#     def _get_row(self, query: str) -> dict[str, Any]:
#         return_value: dict[str, Any] = dict()
#         key_name = f"query:{query}"
#         # record = self._connection.hgetall(key_name)
#         record = self._connection.hmget(
#             name=key_name,
#             keys=self._get_list_of_allowed_fields(),
#         )
#         if self.to_none_if_all_none(record):
#             record_dict = {
#                 key: value
#                 for key, value in zip(self._get_list_of_allowed_fields(), record)
#             }
#             return_value = self._parse_redis_record(record_dict)
#         return return_value

#     def get_embedding_match(
#         self,
#         query: str,
#         threshold: float,
#         knn: int,
#     ) -> List[dict]:
#         # reference: https://redis.readthedocs.io/en/latest/examples/search_vector_similarity_examples.html#Searching
#         vector_similarity_search_dialect = 2
#         query_vector = self._get_embedding(query)
#         query = (
#             Query("@vector:[VECTOR_RANGE $radius $vector]=>{$YIELD_DISTANCE_AS: dist}")
#             .sort_by("dist")
#             .return_fields(*self._get_list_of_allowed_fields())
#             .dialect(vector_similarity_search_dialect)
#         )
#         # Query(f"*=>[KNN {knn} @vector $vector AS dist]")

#         hits = self._connection.ft(self._index_name).search(
#             query,
#             query_params={
#                 "vector": query_vector,  # type: ignore [dict-item]
#                 "radius": threshold,
#             },
#         )
#         records = hits.docs[:knn]
#         # TODO: add reranking part
#         return [self._parse_redis_document_object(record) for record in records]

#     def _thumb_up_down_incrementor(
#         self,
#         query: str,
#         response: str,
#         url: str,
#         field_name: str,
#     ) -> None:
#         update_value = 1
#         record = self._get_row(query)
#         if record:
#             new_value = record[field_name] + update_value
#             self._update_row(query, {field_name: new_value})
#         else:
#             self._insert_row(
#                 query=query,
#                 response=response,
#                 url=url,
#                 thumb_up=0,
#                 thumb_down=0,
#                 flag=0,
#             )
#             self._update_row(query, {field_name: update_value})

#     def increment_thumb_up(self, query: str, response: str, url: str) -> None:
#         self._thumb_up_down_incrementor(
#             query,
#             response,
#             url,
#             self._schema["thumb_up_field"]["name"],
#         )

#     def increment_thumb_down(self, query: str, response: str, url: str) -> None:
#         self._thumb_up_down_incrementor(
#             query,
#             response,
#             url,
#             self._schema["thumb_down_field"]["name"],
#         )

#     def increment_flag(self, query: str, response: str, url: str) -> None:
#         self._thumb_up_down_incrementor(
#             query,
#             response,
#             url,
#             self._schema["flag_field"]["name"],
#         )
