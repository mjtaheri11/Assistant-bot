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
