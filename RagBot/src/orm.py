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


# sudo docker exec -it postgres psql -U postgres -d chatbot -c "CREATE TABLE public.databases (
    #                                                               database_id UUID DEFAULT gen_random_uuid() PRIMARY KEY, 
    #                                                               company_name TEXT DEFAULT 'همکاران سیستم',
    #                                                               assistant_name TEXT DEFAULT 'دستیار دیجیتال',
    #                                                               create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    #                                                           );"
        
# sudo docker exec -it postgres psql -U postgres -d chatbot -c "CREATE TABLE public.sessions (
    #                                                               session_id UUID DEFAULT gen_random_uuid() PRIMARY KEY, 
    #                                                               database_id UUID REFERENCES public.databases(database_id), 
    #                                                               response_type VARCHAR(20) DEFAULT 'concise',
    #                                                               create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    #                                                           );"
    
# sudo docker exec -it postgres psql -U postgres -d chatbot -c "CREATE TABLE public.message (
    #                                                               message_id UUID DEFAULT gen_random_uuid() PRIMARY KEY, 
    #                                                               session_id UUID REFERENCES public.sessions(session_id), 
    #                                                               user_query TEXT, 
    #                                                               paraphrased_query TEXT, 
    #                                                               bot_response TEXT, 
    #                                                               feedback TEXT, 
    #                                                               elapsed_time FLOAT, 
    #                                                               create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    #                                                           );"

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
    
    async def create_database(self, company_name=None, assistant_name=None):
        sql_create_database_query = "INSERT INTO public.databases"
        columns = []
        values_placeholder = []
        query_params = []

        if company_name is not None:
            columns.append("company_name")
            values_placeholder.append("$1")
            query_params.append(company_name)

        if assistant_name and company_name:
            columns.append("assistant_name")
            values_placeholder.append("$2")
            query_params.append(assistant_name)
        
        if (assistant_name is not None) and (company_name is None):
            columns.append("assistant_name")
            values_placeholder.append("$1")
            query_params.append(assistant_name)    

        if columns:
            sql_create_database_query += f" ({', '.join(columns)}) VALUES ({', '.join(values_placeholder)}) RETURNING database_id;"
            query_params_tuple = tuple(query_params)
        else:
            sql_create_database_query += " DEFAULT VALUES RETURNING database_id;"
            query_params_tuple = None

        db_id = await self._execute_query(
            sql_create_database_query, insert_values=query_params_tuple, is_insert=True, fetch_results=True
        )
        output = {"database_id": str(db_id[0])}
        return output
    
    async def find_database_id(self, session_id):
        sql_query_find_dbid = "SELECT database_id FROM public.session WHERE session_id = $1"
        import pdb
        pdb.set_trace()
        database_id = await self._execute_query(
            sql_query_find_dbid,
            insert_values=(session_id,),
            is_insert=True,
            fetch_results=True
        )
        output = {"database_id": str(database_id[0])}
        return output

    async def create_session(self, database_id=None):
        sql_create_database_query = "INSERT INTO public.session"
        columns = []
        values_placeholder = []
        query_params = []

        if database_id is not None:
            columns.append("database_id")
            values_placeholder.append("$1")
            query_params.append(database_id)

        if columns:
            sql_create_database_query += f" ({', '.join(columns)}) VALUES ({', '.join(values_placeholder)}) RETURNING session_id;"
            query_params_tuple = tuple(query_params)
        else:
            sql_create_database_query += " DEFAULT VALUES RETURNING session_id;"
            query_params_tuple = None

        session_id = await self._execute_query(
            sql_create_database_query, insert_values=query_params_tuple, is_insert=True, fetch_results=True
        )
        output = {"session_id": str(session_id[0])}
        return output
        
    async def extract_response_type(self, session_id):
        sql_extract_response_type = (
            "select response_type from public.session where session_id=$1"
        )
        _response_type = await self._execute_query(
                            sql_extract_response_type,
                            fetch_results=True,
                            insert_values=(session_id)
                        )
        output = {"response_type": _response_type}
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
    
    async def get_latest_sessions(
        self,
        num_sessions=30, 
        offset=0, 
        recent_limit=1000
    ):
        sql_latest_unique_sessions_with_paraphrase = """
            WITH recent_messages AS (
                SELECT session_id, create_time
                FROM message
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
                    FROM message m
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
                "session_id": row[0],
                "paraphrased_query": row[1]
            }
            for row in results
        ]
    
    async def insert_chat_row(
        self, session_id, user_query, paraphrased_query, bot_response, response_type, elapsed_time
    ):
        values = (
            session_id,
            user_query,
            paraphrased_query,
            bot_response,
            response_type,
            elapsed_time,
        )
        sql_insert_query = "INSERT INTO message (session_id, user_query, paraphrased_query, bot_response, response_type, elapsed_time) VALUES ($1, $2, $3, $4, $5, $6) RETURNING message_id;"
        message_id = await self._execute_query(
            sql_insert_query, is_insert=True, insert_values=values, fetch_results=True
        )
        return str(message_id[0])

    async def set_feedback(self, message_id, feedback_type):
        update_query = """
            UPDATE message 
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
        import pdb
        pdb.set_trace()
        return 
        