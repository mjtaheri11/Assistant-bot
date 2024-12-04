import asyncpg
import asyncio
from typing import Optional, Tuple

from .config import config


class Postgres:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.database = config["postgres"]["database"]
        self.connection_address = config["postgres"]["address"]

    async def _execute_query(
        self,
        query: str,
        is_insert: bool = False,
        insert_values: Optional[Tuple] = None,
        fetch_results: bool = True,
    ):
        try:
            connection = await asyncpg.connect(
                database=self.database,
                host=self.connection_address,
                user="postgres",
                password="MySecretPassword123!@#",  # add to environment variables
                port="5432",
            )
            async with connection.transaction():                
                # if insert_values is not None:
                #     await connection.execute(query, *insert_values)
                # else:
                #     await connection.execute(query)

                if fetch_results:
                    if is_insert:
                        result = await connection.fetchrow(query, *insert_values if insert_values else [])
                        return result
                    else:
                        result = await connection.fetch(query, *insert_values if insert_values else [])
                        return result
                else:
                    return ""

        except Exception as ex:
            raise ex

    async def exist_session(self, session_id):
        sql_exist_session_query = (
            "SELECT session_id FROM session WHERE session_id = $1;"
        )
        result = await self._execute_query(
            sql_exist_session_query, fetch_results=True, insert_values=(session_id,)
        )
        return bool(result)

    async def get_message_fields(self, session_id, message_id):
        sql_get_message_fileds = (
            "SELECT user_query, paraphrased_query, bot_response FROM message WHERE message_id = $1 AND session_id = $2;"
        )
        message_fields = await self._execute_query(
            sql_get_message_fileds,
            fetch_results=True,
            insert_values=(message_id, session_id),
        )
        return message_fields[0] if message_fields else []

    async def create_session(self):
        sql_create_session_query = (
            "INSERT INTO public.session DEFAULT VALUES RETURNING session_id;"
        )
        sid = await self._execute_query(
            sql_create_session_query, is_insert=True, fetch_results=True
        )
        output = {"session_id": str(sid[0])}
        return output

    async def get_history(self, session_id, start_index, end_index):
        sql_history_query = """
            SELECT user_query, paraphrased_query, bot_response FROM message
            WHERE session_id = $1
            ORDER BY create_time DESC
            OFFSET $2
            LIMIT $3;
        """
        # Calculate the number of records to skip and the limit for the query
        offset = start_index - 1  # start_index is 1-based, so subtract 1 for 0-based offset
        limit = end_index - start_index + 1  # The total number of records to fetch
        
        selected_history = await self._execute_query(
            sql_history_query,
            fetch_results=True,
            insert_values=(session_id, offset, limit)
        )
        
        # Process the history results in the desired format
        history = [
            (
                [h[0], h[2]]
                if len(h[0]) < config["postgres"]["max_user_input_character_length"]
                else [h[1], h[2]]
            )
            for h in reversed(selected_history)
        ]
        
        return history

    async def insert_chat_row(
        self, session_id, user_query, paraphrased_query, bot_response, elapsed_time
    ):
        values = (
            session_id,
            user_query,
            paraphrased_query,
            bot_response,
            elapsed_time,
        )
        sql_insert_query = "INSERT INTO message (session_id, user_query, paraphrased_query, bot_response, elapsed_time) VALUES ($1, $2, $3, $4, $5) RETURNING message_id;"
        message_id = await self._execute_query(
            sql_insert_query, is_insert=True, insert_values=values, fetch_results=True
        )
        return str(message_id[0])

    async def set_feedback(self, message_id, feedback_type):
        update_query = "UPDATE message SET feedback = $1 WHERE message_id = $2 RETURNING message_id;"
        await self._execute_query(
            update_query,
            fetch_results=True,
            insert_values=(feedback_type, message_id),
        )
        