import asyncpg
import asyncio
from typing import Optional, Tuple

from .config import config

# Models for request and response


# sudo docker exec -it postgres psql -U postgres -d chatbot -c "CREATE TABLE public.session (session_id UUID DEFAULT gen_random_uuid() PRIMARY KEY, history_length INT)"

# CREATE EXTENSION IF NOT EXISTS "pgcrypto";

# CREATE TABLE public.session (
#     session_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
#     create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );


# CREATE TABLE public.message (
#     message_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
#     session_id UUID REFERENCES public.session(session_id),
#     user_query TEXT,
#     paraphrased_query TEXT,
#     bot_response TEXT,
#     feedback TEXT,
#     elapsed_time TEXT,
#     create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# sudo docker exec -it postgres psql -U postgres -d chatbot -c "ALTER TABLE public.message ADD COLUMN is_sql BOOLEAN DEFAULT FALSE;"

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

    async def get_history(self, session_id, page_index, page_size, with_paraphrase=False):
        sql_history_query = """
            SELECT user_query, paraphrased_query, bot_response, message_id FROM message
            WHERE session_id = $1
            ORDER BY create_time DESC
            OFFSET $2
            LIMIT $3;
        """
        
        # Calculate the number of records to skip and the limit for the query
        offset = (page_index - 1) * page_size  # Skip records based on the page number and batch size
        limit = page_size  # Limit to the batch size for each page
        selected_history = await self._execute_query(
            sql_history_query,
            fetch_results=True,
            insert_values=(session_id, offset, limit)
        )
        
        # Process the history results in the desired format
        if with_paraphrase:
            history = [
                    {"query": h[0], "response": h[2], "paraphrased_query": h[1], "message_id": h[3]}
                for h in reversed(selected_history)
            ]
        else:
            history = [
                    {"query": h[0], "response": h[2], "message_id": h[3]}
                    for h in reversed(selected_history)
            ]       
                
        return history
    
    async def get_latent_sessions(self, num_sessions=30):
        sql_latent_sessions =  """
            SELECT session_id FROM session
            ORDER BY create_time DESC
            OFFSET $1
            LIMIT $2;
        """
        selected_sessions = await self._execute_query(
            sql_latent_sessions,
            fetch_results=True,
            insert_values=(1, num_sessions)
        )
        
        return [str(session[0]) for session in selected_sessions]
        
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
        