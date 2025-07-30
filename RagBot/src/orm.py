import asyncpg
import asyncio
import os
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
            # The transaction will automatically commit on success or rollback on error.
            async with connection.transaction():
                # Handle cases where we need to fetch data (e.g., SELECT)
                if fetch_results:
                    values = insert_values if insert_values else []
                    # `is_insert` seems to mean "fetch one row"
                    if is_insert:
                        return await connection.fetchrow(query, *values)
                    else:
                        return await connection.fetch(query, *values)
                # Handle cases where we just execute a command (e.g., UPDATE, INSERT, DELETE)
                else:
                    await connection.execute(query, *insert_values if insert_values else [])
                    return True  # Return a success indicator

        except Exception as ex:
            # It's good practice to log the exception here
            print(f"Database query failed: {ex}")
            raise ex
        finally:
            # Always ensure the connection is closed
            if 'connection' in locals() and not connection.is_closed():
                await connection.close()
                

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
            "SELECT user_query, paraphrased_query, bot_response FROM messages WHERE message_id = $1 AND session_id = $2;"
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
            SELECT user_query, paraphrased_query, bot_response, message_id, is_sql, selected_module, elapsed_time, do_suggest FROM messages
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
                    {"query": h[0], "response": h[2], "paraphrased_query": h[1], "message_id": h[3], "is_sql": h[4], "selected_module": h[5], "elapsed_time": h[6], "do_suggest": h[7]}
                for h in reversed(selected_history)
            ]
        else:
            history = [
                    {"query": h[0], "response": h[2], "message_id": h[3], "is_sql": h[4], "selected_module": h[5], "elapsed_time": h[6], "do_suggest": h[7]}
                    for h in reversed(selected_history)
            ]       
                
        return history
    
    async def remove_previous_response(self, message_id):
        sql_remove_previous_response = """UPDATE messages SET bot_response = NULL WHERE message_id = $1;"""
        await self._execute_query(
            sql_remove_previous_response,
            is_insert=True,
            insert_values=(message_id,),
            fetch_results=False
        )
        return True
    
    async def get_latest_sessions(
        self,
        num_sessions=30, 
        offset=0, 
        recent_limit=1000
    ):
        sql_latest_unique_sessions_with_paraphrase = """
            WITH recent_messages AS (
                SELECT session_id, create_time
                FROM messages
                ORDER BY create_time DESC
                LIMIT $3
            ),
            distinct_sessions AS (
                SELECT DISTINCT ON (session_id)
                    session_id,
                    create_time
                FROM recent_messages
                ORDER BY session_id, create_time DESC
            )
            SELECT 
                ds.session_id,
                (
                    SELECT m.paraphrased_query
                    FROM messages m
                    WHERE m.session_id = ds.session_id
                    AND m.paraphrased_query IS NOT NULL
                    ORDER BY m.create_time ASC
                    LIMIT 1
                ) AS first_paraphrased_query
            FROM distinct_sessions ds
            ORDER BY ds.create_time DESC
            OFFSET $1
            LIMIT $2;
        """
        
        results = await self._execute_query(
            sql_latest_unique_sessions_with_paraphrase,
            fetch_results=True,
            insert_values=(offset, num_sessions, recent_limit)
        )
        # Each row = (session_id, first_paraphrased_query)
        return [
            {
                "session_id": str(row[0]),
                "paraphrased_query": row[1]
            }
            for row in results
        ]
    
    async def insert_chat_row(
        self, session_id, user_query, paraphrased_query, bot_response, elapsed_time, selected_module=None
    ):
        # Start with required columns and their values
        columns = ["session_id", "user_query"]
        values = [session_id, user_query]

        # Conditionally add parameters if they are not None
        if paraphrased_query is not None:
            columns.append("paraphrased_query")
            values.append(paraphrased_query)
        if bot_response is not None:
            columns.append("bot_response")
            values.append(bot_response)
        if elapsed_time is not None:
            columns.append("elapsed_time")
            values.append(elapsed_time)
        if selected_module is not None:
            columns.append("selected_module")
            values.append(selected_module)

        # Construct the SQL query dynamically
        sql_insert_query = f"INSERT INTO messages ({', '.join(columns)}) VALUES ({', '.join([f'${i}' for i in range(1, len(values) + 1)])}) RETURNING message_id;"

        # Execute the query
        message_id = await self._execute_query(
            sql_insert_query, is_insert=True, insert_values=tuple(values), fetch_results=True
        )
        # Assuming _execute_query returns a list of tuples, e.g., [(123,)], adjust return accordingly
        return str(message_id[0])
    
    
    async def update_last_chat_row(
        self,
        session_id,
        paraphrased_query,
        bot_response,
        is_sql,
        elapsed_time,
        do_suggest=False,
        selected_module=None
        ):
        
        values = (
            paraphrased_query,
            bot_response,
            elapsed_time,
            selected_module,  # Pass None directly; the driver converts it to NULL
            session_id,
            is_sql,
            do_suggest
        )
        sql_update_query = """
            UPDATE messages
            SET paraphrased_query = $1,
                bot_response = $2,
                elapsed_time = $3,
                selected_module = $4,
                is_sql = $6,
                do_suggest = $7
            WHERE message_id = (
                SELECT message_id
                FROM messages
                WHERE session_id = $5
                ORDER BY create_time DESC
                LIMIT 1
            )
            RETURNING message_id;
        """        # The _execute_query probably returns a list of records, e.g., [(123,)]
        message_id = await self._execute_query(
            sql_update_query, is_insert=True, insert_values=values, fetch_results=True
        )            
        return str(message_id[0])


    async def update_on_click_chat_row(
        self,
        message_id,
        bot_response,
        elapsed_time,
        do_suggest=False,
        is_sql=False
    ):
        values = (
            bot_response,
            elapsed_time,
            message_id,
            do_suggest,
            is_sql,
        )
        sql_insert_query = "UPDATE messages SET bot_response = $1, elapsed_time = $2, do_suggest = $4, is_sql = $5 WHERE message_id = $3;" 
        message_id = await self._execute_query(
            sql_insert_query, is_insert=True, insert_values=values, fetch_results=True
        )
        return True
    
    async def update_selected_module(
        self, message_id, selected_module
    ):
        values = (selected_module, message_id)
        sql_insert_query = "UPDATE messages SET selected_module = $1 WHERE message_id = $2;"
        message_id = await self._execute_query(
            sql_insert_query, is_insert=True, insert_values=values, fetch_results=True
        )
        return True


    async def set_feedback(self, message_id, feedback_type):
        update_query = """
            UPDATE messages
            SET feedback = $1 
            WHERE message_id = $2 AND feedback IS NULL 
            RETURNING message_id;
        """
        result = await self._execute_query(
            update_query,
            fetch_results=True,
            insert_values=(feedback_type, message_id),
        )        
        return bool(result)

    async def get_user_code_tenant_name(self, session_id):
        sql_get_user_code = "SELECT user_code, tenant_name FROM public.session where session_id = $1"
        result = await self._execute_query(
            update_query,
            fetch_results=True,
            insert_values=(feedback_type, message_id),
        )
        user_code, tenant_name = (result[0] if result[0] != None else "", result[1] if result[1] != None else "")
        {"user_code": str(user_code), "tenant_name": str(tenant_name)}
        return 
        
    async def insert_message_choices(self, message_id: str, *choices) -> None: 
        for choice in choices:
            insert_message_choice_query = "INSERT INTO messages_choices (message_id, choice_value) VALUES ($1, $2) RETURNING choice_id;"
            _ = await self._execute_query(
                insert_message_choice_query,
                fetch_results=True,
                insert_values=(message_id, choice),
            )                    
        return True
    
    async def get_message_choices(self, message_id: str) -> list[str]:
        """Retrieves all choice values for a given message_id as a list."""
        
        # 1. Define the SQL query to select choices for the given message_id
        get_choices_query = "SELECT choice_value FROM messages_choices WHERE message_id = $1;"
        
        # 2. Execute the query
        records = await self._execute_query(
            get_choices_query,
            fetch_results=True,
            insert_values=(message_id,),  # Use the same parameter passing mechanism
        )

        choices = [record[0] for record in records]
        
        return choices