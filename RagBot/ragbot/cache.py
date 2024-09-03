from typing import Any, List, Mapping

import numpy as np
from redis import Redis
from redis.commands.search.query import Query
from redis.commands.search.document import Document  # type: ignore

from config import config, secret
from faqtory.HF_topk import HFTopK


class Cache:
    def __init__(
        self,
        index_name: str = config["cache"]["index_name"],
    ) -> None:
        self._connection = Redis(
            host=secret["cache"]["host"],
            port=secret["cache"]["port"],
            socket_timeout=config["cache"]["socket_timeout"],
        )
        self._hf_top_k_ranker = HFTopK(
            model_path=config["faqtory"]["model_path"],
            name=config["faqtory"]["model_name"],
        )
        self._index_name = index_name
        self._schema = {
            "query_field": {
                "name": config["cache"]["schema"]["query_field_name"],
                "type": str,
            },
            "vector_field": {
                "name": config["cache"]["schema"]["vector_field_name"],
                "type": np.ndarray,
            },
            "answer_field": {
                "name": config["cache"]["schema"]["answer_field_name"],
                "type": str,
            },
            "url_field": {
                "name": config["cache"]["schema"]["url_field_name"],
                "type": str,
            },
            "thumb_up_field": {
                "name": config["cache"]["schema"]["thumb_up_field_name"],
                "type": int,
            },
            "thumb_down_field": {
                "name": config["cache"]["schema"]["thumb_down_field_name"],
                "type": int,
            },
        }

    def _get_list_of_allowed_fields(self) -> List[str]:
        return [
            self._schema["query_field"]["name"],
            self._schema["answer_field"]["name"],
            self._schema["url_field"]["name"],
            self._schema["thumb_up_field"]["name"],
            self._schema["thumb_down_field"]["name"],
        ]

    def _decode_redis_output(self, field: str, value: bytes | None) -> Any:
        if value is None:
            return None
        else:
            field_name = f"{field}_field"
            _type = self._schema[field_name]["type"]
            return _type(value)

    def _parse_redis_record(self, record: dict[str, bytes | None]) -> dict[str, Any]:
        return {
            key: self._decode_redis_output(key, value) for key, value in record.items()
        }

    def _parse_redis_document_object(self, redis_document: Document) -> dict[str, Any]:
        document_dict = dict(redis_document.__dict__)

        del document_dict["id"]
        del document_dict["payload"]

        return {
            key: self._decode_redis_output(key, value)
            for key, value in document_dict.items()
        }

    def _get_embedding(self, query: str) -> bytes:
        return (
            np.array(self._hf_top_k_ranker.get_embedding([query])[0])
            .astype(np.float64)
            .tobytes()
        )

    def _insert_row(
        self,
        query: str,
        response: str,
        url: str,
        thumb_up: int,
        thumb_down: int,
    ) -> None:
        self._connection.hset(
            name=query,
            mapping={
                self._schema["query_field"]["name"]: query,
                self._schema["vector_field"]["name"]: self._get_embedding(query),
                self._schema["answer_field"]["name"]: response,
                self._schema["url_field"]["name"]: url,
                self._schema["thumb_up_field"]["name"]: thumb_up,
                self._schema["thumb_down_field"]["name"]: thumb_down,
            },
        )

    def _update_row(
        self,
        query: str,
        mapping: Mapping[str | bytes, bytes | float | int | str],
    ) -> None:
        self._connection.hset(
            name=query,
            mapping=mapping,
        )

    def _get_row(self, query: str) -> dict[str, Any]:
        return_value: dict[str, Any] = dict()
        record = self._connection.hmget(
            name=query,
            keys=self._get_list_of_allowed_fields(),
        )
        if record:
            record_dict = {
                key: value
                for key, value in zip(self._get_list_of_allowed_fields(), record)
            }
            self._parse_redis_record(record_dict)
        return return_value

    def get_embedding_match(
        self,
        query: str,
        threshold: float,
        knn: int,
    ) -> List[dict]:
        # reference: https://redis.readthedocs.io/en/latest/examples/search_vector_similarity_examples.html#Searching
        vector_similarity_search_dialect = 2
        query_vector = self._get_embedding(query)
        query = (
            Query("@vector:[VECTOR_RANGE $radius $vector]=>{$YIELD_DISTANCE_AS: dist}")
            .sort_by("dist")
            .return_fields(*self._get_list_of_allowed_fields())
            .dialect(vector_similarity_search_dialect)
        )

        hits = self._connection.ft(self._index_name).search(
            query,
            query_params={
                "vector": query_vector,  # type: ignore [dict-item]
                "radius": threshold,
            },
        )
        records = hits.docs[:knn]
        return [self._parse_redis_document_object(record) for record in records]

    def _thumb_up_down_incrementor(
        self,
        query: str,
        response: str,
        url: str,
        field_name: str,
    ) -> None:
        update_value = 1
        record = self._get_row(query)
        if record:
            new_value = record[field_name] + update_value
            self._update_row(query, {field_name: new_value})
        else:
            self._insert_row(
                query=query,
                response=response,
                url=url,
                thumb_up=0,
                thumb_down=0,
            )
            self._update_row(query, {field_name: update_value})

    def increment_thumb_up(self, query: str, response: str, url: str) -> None:
        self._thumb_up_down_incrementor(
            query,
            response,
            url,
            self._schema["thumb_up_field"]["name"],
        )

    def increment_thumb_down(self, query: str, response: str, url: str) -> None:
        self._thumb_up_down_incrementor(
            query,
            response,
            url,
            self._schema["thumb_down_field"]["name"],
        )