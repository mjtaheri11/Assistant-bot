import argparse
import asyncio
import csv
import json
import logging
import re
import os
import shutil
import time
import traceback
from datetime import datetime
from io import BytesIO
from typing import List, Any, Optional, Tuple, Dict

import asyncpg
from fastapi import FastAPI, HTTPException, Request, Query, File, Form, UploadFile, Depends
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest
from pydantic import BaseModel, Field
from starlette.responses import Response
from langfuse import observe, get_client
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from openai import AsyncOpenAI
from src.shear_parser import convert_word_to_markdown, SoleChunker
import tempfile
from pathlib import Path
# Langfuse configuration
load_dotenv()

LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")

from src.vector_db_utils import (
    create_vector_database,
    create_vector_database_from_config,
    delete_vector_database,
    list_vector_databases,
    get_collection_info,
    add_documents_to_existing_collection
)
from src.orm import Postgres
from src.config import config
from src.initiate_vdb import qdrant_client
from src.retriever import Retriever, ModelManager
from src.logic import (
    chat_responder_,
    feedback_,
    prepare_final_context,
    query_responder,
    sql_responder_,
    utterance_paraphraser,
    module_proposer,
    parameters_responder
)
from src.logs import non_generative_agent_logger, simple_logger
from src.utils import substitute_sql_parameters

from langchain.schema import Document
from qdrant_client import QdrantClient, models

llm_clients = {}

async def get_client_llm():
    return llm_clients
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    
    # Initialize the Standard OpenAI Client
    llm_clients["gpt"] = AsyncOpenAI(
        base_url=os.getenv("GPT_API_BASE"), 
        api_key=os.getenv("GPT_API_KEY")
    )
    
    # Initialize the Local Client (e.g., Ollama, vLLM, LocalAI)
    # Note: 'base_url' points to your local server
    # Note: 'api_key' is required by the SDK but often ignored by local servers
    llm_clients["oss"] = AsyncOpenAI(
        base_url=os.getenv("OSS_API_BASE"), 
        api_key=os.getenv("OSS_API_KEY") 
    )
    
    print("Clients initialized.")
    yield
    
    # --- Shutdown ---
    # Close both connections cleanly
    await llm_clients["oss"].close()
    await llm_clients["gpt"].close()
    print("Clients closed.")

RESPONSE_TEMPLATE_FOR_NO_ANSWER = "متاسفانه، پاسخی به سوال شما یافت نشد."
MODULE_CLARIFICATION_RESPONSE_TEMPLATE = "لطفا مشخص نمایید سوال شما از کدام یک از ماژول های سیستم است."
app = FastAPI(title="Digital Assistant", lifespan=lifespan, root_path=os.getenv("FASTAPI_ROOT_PATH")) # should be added to env variables
 
# Define Prometheus metrics
REQUEST_COUNT = Counter("api_http_requests_total", "Total API Requests", ["endpoint"])
REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds", "Latency of API Requests", ["endpoint"]
)

SUPPORTED_FILE_EXTENSIONS = os.getenv("SUPPORTED_FILE_EXTENSIONS").split(",")
# ================== Data Models ==================

class SessionResponse(BaseModel):
    session_id: str

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    does_evaluate: Optional[bool] = False
    response_type: Optional[str] = "concise"
    use_cache: Optional[bool] = False
    # SQL Agent specific fields
    on_click: Optional[bool] = False
    do_retry: Optional[bool] = False
    error_payload: Optional[str] = ""
    is_sync: Optional[bool] = True
    sql_mode: Optional[bool] = True  # Toggle between legacy and SQL agent mode
    use_oss: Optional[bool] = False

class ChatResponse(BaseModel):
    message_id: str
    response: str
    query: str
    is_sql: bool = False
    do_suggest: bool = False
    choices: List[str] = []
    parameters: Optional[dict] = {}
    response_template: str = ""

class CreateSessionRequest(BaseModel):
    tenant_name: Optional[str] = ""
    user_code: Optional[str] = ""
    database_id: Optional[str] = ""

class SQLRequest(BaseModel):
    # Support both legacy (table_schemas) and new (session-based) approaches
    table_schemas: Optional[List[str]] = None
    query: str
    session_id: Optional[str] = ""
    on_click: Optional[bool] = False

class SQLResponse(BaseModel):
    response: str
    do_suggest: bool = False
    choices: List[str] = []
    message_id: Optional[str] = ""

class HistoryResponse(BaseModel):
    history: List[dict]

class HistoryRequest(BaseModel):
    page_index: int = 1
    page_size: int = 5
    session_id: str
    contain_paraphrase: str = False

class GetSessionsResponse(BaseModel):
    response: List[dict]

class GetDatabasesResponse(BaseModel):
    response: List[dict]

class FaqRequest(BaseModel):
    query: str
    session_id: Optional[str] = ""
    database_index: str

class FaqResponse(BaseModel):
    response: str

class ModuleRequest(BaseModel):
    query: str

class ModuleResponse(BaseModel):
    response: str = ""

class MakeRequest(BaseModel):
    message_id: str
    session_id: str
    answer: Optional[str]

class MakeResponse(BaseModel):
    response: Optional[str]

class FeedbackRequest(BaseModel):
    message_id: str
    feedback_type: str
    session_id: Optional[str] = None
    tenant_name: Optional[str] = None
    user_code: Optional[str] = None

class FeedbackResponse(BaseModel):
    message: str

class CreateDatabaseResponse(BaseModel):
    database_id: str
    collection_name: str
    message: str
    total_documents: int
    files_processed: List[str]

class ListCollectionsResponse(BaseModel):
    collections: List[str]
    count: int

class DatabaseInfoResponse(BaseModel):
    name: str = Field(..., description="Collection name")
    points_count: int = Field(..., description="Number of points in the collection")
    vectors_count: Optional[int] = Field(None, description="Number of vectors (can be None)")
    indexed_vectors_count: int = Field(..., description="Number of indexed vectors")
    status: str = Field(..., description="Collection status")
    optimizer_status: str = Field(..., description="Optimizer status")
    vector_size: int = Field(..., description="Vector dimension size")
    distance: str = Field(..., description="Distance metric used")
    
    class Config:
        use_enum_values = True


class DeleteDatabaseResponse(BaseModel):
    message: str
    database_id: str

class AddDocumentsResponse(BaseModel):
    message: str
    database_id: str
    documents_added: int
    total_documents: Optional[int] = None  # Total documents in collection after addition

# ================== Utility Functions ==================


def find_module_name(original_filename):
    main_filename = Path(original_filename).stem
    module = config["modules"]["names"][main_filename]
    return module
    
def finalize_parameters(a_dict, b_dict):
    # concatenation = {"parameters": a_dict["parameters"] | b_dict["parameters"]}
    concatenation = (a_dict | b_dict) | {"parameters": a_dict.get("parameters", {}) | b_dict.get("parameters", {})}
    return concatenation

# ============================================================================
# PIPELINE INTEGRATION
# ============================================================================

async def process_uploaded_files(
    files: List[UploadFile],
    company_name: str,
    assistant_name: str
) -> Dict[str, List[Document]]:
    """
    Process uploaded files through the complete pipeline:
    1. Save uploaded files to temp directory
    2. Convert Word files to Markdown
    3. Chunk markdown files
    4. Create Document objects
    
    Args:
        files: List of uploaded files
        company_name: Company name for metadata
        assistant_name: Assistant name for metadata
    
    Returns:
        Dictionary mapping filenames to their chunked Documents
    """
    # Create temporary directory for processing
    temp_dir = tempfile.mkdtemp(prefix="doc_processing_")
    temp_upload_dir = Path(temp_dir) / "uploads"
    temp_markdown_dir = Path(temp_dir) / "markdown"
    temp_upload_dir.mkdir(parents=True, exist_ok=True)
    temp_markdown_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        processed_files = {}
        word_files_to_convert = []
        markdown_files_to_process = []
        # Step 1: Save uploaded files
        print(f"Processing {len(files)} uploaded files...")
        for file in files:
            file_path = temp_upload_dir / file.filename
            content = await file.read()
            
            with open(file_path, 'wb') as f:
                f.write(content)
            
            file_extension = Path(file.filename).suffix.lower()
            
            # Check if file type is supported
            if file_extension not in SUPPORTED_FILE_EXTENSIONS:
                raise HTTPException(
                    status_code=404,
                    detail=f"File type '{file_extension}' not supported. Supported types: {SUPPORTED_FILE_EXTENSIONS}"
                )
            
            # Categorize files for processing
            if file_extension in ['.docx', '.doc']:
                word_files_to_convert.append(file_path)
            elif file_extension == '.md':
                markdown_files_to_process.append((file_path, file.filename))
        
        # Step 2: Convert Word files to Markdown using ProcessDocs
        if word_files_to_convert:
            print(f"Converting {len(word_files_to_convert)} Word files to Markdown...")
            conversion_results = convert_word_to_markdown(
                word_files_to_convert,
                str(temp_markdown_dir)
            )
            # Check conversion results and add to markdown processing list
            for original_path, result in conversion_results.items():
                if result['status'] == 'success':
                    md_path = Path(result['output_path'])
                    original_filename = Path(original_path).stem
                    markdown_files_to_process.append((md_path, f"{original_filename}.md"))
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to convert {original_path}: {result['message']}"
                    )
        
        # Step 2.5: Preprocess markdown files that were uploaded directly
        # This ensures they also start with '#' and are properly formatted
        preprocessed_markdown_files = []
        for md_path, original_filename in markdown_files_to_process:
            # If file is from temp_upload_dir, it needs preprocessing
            if temp_upload_dir in md_path.parents:
                preprocessed_path = temp_markdown_dir / md_path.name
                print(f"Preprocessing markdown file: {md_path.name}")
                preprocess_markdown_file(md_path, preprocessed_path)
                preprocessed_markdown_files.append((preprocessed_path, original_filename))
            else:
                # Already preprocessed (from Word conversion)
                preprocessed_markdown_files.append((md_path, original_filename))
        
        # Step 3: Chunk all preprocessed markdown files
        print(f"Chunking {len(preprocessed_markdown_files)} markdown files...")
        for md_path, original_filename in preprocessed_markdown_files:
            try:
                # Use SoleChunker to process the markdown file
                chunker = SoleChunker(str(md_path))
                chunks = chunker(retain_only_headers=False, remove_imgs=True)
                
                # Create Document objects with metadata
                documents = []
                for idx, chunk_content in enumerate(chunks):
                    modules_dict = config["database"]["documents"]
                    modified_filename = str(Path(original_filename).stem.lower().strip())
                    if modified_filename in modules_dict:
                        module = modules_dict[modified_filename]
                    else: 
                        module = "unknown"
                    metadata = {
                        "source": original_filename,
                        "chunk_index": idx,
                        "company_name": company_name,
                        "assistant_name": assistant_name,
                        "module": module
                    }
                    doc = Document(page_content=chunk_content, metadata=metadata)
                    documents.append(doc)
                
                processed_files[original_filename] = documents
                print(f"  - {original_filename}: {len(documents)} chunks created")
                
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to chunk {original_filename}: {str(e)}"
                )
        
        return processed_files
        
    finally:
        # Cleanup: Remove temporary directory
        try:
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            print(f"Warning: Could not remove temp directory {temp_dir}: {e}")


def find_database_collection_with_postgres(postgres_obj: object, database_id: str = None):
    """
    Find database collection and fetch company/assistant names from PostgreSQL.
    This is the recommended approach for production use.
    
    Args:
        database_id: The unique identifier for the database
    
    Returns:
        tuple: (collection_name, company_name, assistant_name)
    """
    
    # If no database_id provided, use default from config
    if not database_id or database_id == "None" or database_id == None:
        collection_name = config.get("database", {}).get("collection_name", "default_collection")
        company_name = config.get("database", {}).get("company_name", "همکاران سیستم")
        assistant_name = config.get("database", {}).get("assistant_name", "دستیار دیجیتال")
        return collection_name, company_name, assistant_name
    
    # Use database_id as collection_name
    collection_name = database_id
    
    # Verify the collection exists in Qdrant
    try:
        collections = qdrant_client.get_collections().collections
        collection_exists = any(c.name == collection_name for c in collections)
        
        if not collection_exists:
            raise Exception(f"Collection '{collection_name}' not found in Qdrant")
        
        # Fetch company_name and assistant_name from PostgreSQL
        postgres = Postgres()
        database_info = postgres.get_database_by_id(database_id)  # You'll need this method
        
        company_name = database_info.get("company_name")
        assistant_name = database_info.get("assistant_name")
        
        print(f"✅ Found collection: {collection_name}")
        print(f"   Company: {company_name}, Assistant: {assistant_name}")
        
        return collection_name, company_name, assistant_name
        
    except Exception as e:
        raise Exception(f"ERROR finding database '{database_id}': {str(e)}")


def get_session_id(request: Request, content_request: BaseModel):
    """Extract session ID from headers or request body"""
    session_id = request.headers.get("Session-ID")
    if not session_id and hasattr(content_request, 'session_id'):
        session_id = content_request.session_id
    if not session_id:
        raise HTTPException(status_code=422, detail="No Session-ID")
    return session_id

async def get_user_code_tenant_name(content_request: BaseModel, postgres_obj: object):
    user_tenant = await postgres_obj.get_user_code_tenant_name(content_request.session_id)
    return user_tenant["user_code"], user_tenant["tenant_name"]

def validate_query(query):
    if not query.strip():
        raise HTTPException(status_code=422, detail="Query is empty")


def convert_sql_parameters(sql_query):
    """
    Convert SQL parameter placeholders from $ format to @ format.
    All numbers in parameters get an underscore prefix (e.g., $1 -> @_1, @2 -> @_2).
    
    Args:
        sql_query (str): SQL query with $ parameters (e.g., $param, $1, $param_name)
        
    Returns:
        str: SQL query with @ parameters where numbers have underscore prefix
    """
    # First convert all $ to @
    # Pattern to match $ followed by parameter name (alphanumeric + underscore) or just numbers
    pattern = r'\$([a-zA-Z_][a-zA-Z0-9_]*|\d+)'
    sql_query = re.sub(pattern, r'@\1', sql_query)
    
    # Then add underscore before any numbers that follow @
    # This catches @1, @2, @3, etc. and converts them to @_1, @_2, @_3
    sql_query = re.sub(r'@(\d+)', r'@param\1', sql_query)
    
    return sql_query



def add_underscore_to_keys(dictionary):
    """
    Add an underscore prefix to all keys in a dictionary.
    
    Args:
        dictionary (dict): Input dictionary
        
    Returns:
        dict: New dictionary with underscore-prefixed keys
    """
    return {f"param{key}": value for key, value in dictionary.items()}


async def preprocess_vector_db_input(files, target_chunk_size, max_chunk_size, company_name, assistant_name):
    """Preprocess files for vector database creation - from develop branch"""
    _settings = {}
    for file in files:
        content = await file.read()
        obj_ = content
        _settings[obj_] = {
            "file_name": file.filename,
            "doc_obj": obj_,
            "target_chunk_size": target_chunk_size,
            "max_chunk_size": max_chunk_size,
            "sentence_overlap": 1,
        }
    _settings["company_name"] = company_name
    _settings["assistant_name"] = assistant_name
    return _settings

async def async_responder(session_id):
    """Handle async polling for responses - from SQL agent branch"""
    ASYNC_POLLING_TIMEOUT = 180
    ASYNC_POLLING_INTERVAL = 1

    postgres = Postgres()
    history = await postgres.get_history(session_id, 1, 1, True)
    if not history:
        raise HTTPException(status_code=404, detail="No previous sync request found for this session.")
   
    for _ in range(int(ASYNC_POLLING_TIMEOUT / ASYNC_POLLING_INTERVAL)):
        final_records = await postgres.get_history(session_id, 1, 1, True)
        final_record = final_records[0] if final_records else {}
        if final_record.get("response") is not None:
            if final_record.get("do_suggest"):
                final_record["choices"] = await postgres.get_message_choices(final_record["message_id"])
                assert len(final_record["choices"]) > 0, "No choices found for the message while do_suggest is True"
            return final_record
        await asyncio.sleep(ASYNC_POLLING_INTERVAL)
   
    raise HTTPException(status_code=408, detail="Request timed out while waiting for the synchronous job to complete.")

# ================== API Endpoints ==================


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")

@app.get(
    "/v1/sessions",
    response_model=GetSessionsResponse,
    responses={
        200: {},
        500: {"description": "Unhandled error that should be reported"},
    }
)
async def get_latest_sessions():
    try:
        postgres = Postgres()
        sessions = await postgres.get_latest_sessions()
        return GetSessionsResponse(response=sessions)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e

@app.get(
    "/v1/databases", 
    response_model=GetDatabasesResponse,
    responses={
        200: {},
        500: {"description": "Unhandled error that should be reported"},
    },
)
async def get_latest_databases():
    try:
        postgres = Postgres()
        databases = await postgres.get_latest_databases()
        return GetDatabasesResponse(response=databases)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e

@app.get(
    "/v1/faq",
    response_model=FaqResponse,
    responses={
        200: {},
        500: {"description": "Unhandled error that should be reported"},
    },
)
async def get_faq(
    request: Request,
    query: str = Query(..., alias="query"),
    session_id: str = Query(..., alias="session_id"),
):
    try:
        postgres = Postgres()
        database_id_dict = await postgres.find_database_id(session_id)
        database_id = database_id_dict["database_id"]
        retriever = Retriever()
        context_lst = await retriever.retrieve_context(query, database_id, reverse=False, split=True)
        context = "\n\n ============= \n\n".join([context["text"] for context in context_lst])
        return FaqResponse(response=context.strip())
    except HTTPException as e:
        raise e
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unhandled error, Please report")

@app.get(
    "/v1/chat",
    response_model=HistoryResponse,
    responses={
        200: {},
        500: {"description": "Unhandled error that should be reported"},
    },
)
async def get_history(
    request: Request,
    page_index: int = Query(1, alias="page_index"),
    page_size: int = Query(5, alias="page_size"),
    session_id: str = Query(..., alias="session_id"),
    contain_paraphrase: bool = Query(False, alias="contain_paraphrase"),
):
    try:
        postgres = Postgres()
        simple_logger(f"Received history request", session_id)
        history = await postgres.get_history(
            session_id, page_index, page_size, contain_paraphrase
        )
        return HistoryResponse(history=history)
    except HTTPException as e:
        raise e
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unhandled error, Please report")

@app.post(
    "/v1/session/create",
    response_model=SessionResponse,
    responses={
        200: {},
        500: {"description": "Unhandled error that should be reported"},
    },
)
@observe()
async def create_session(create_session_request: Optional[CreateSessionRequest] = None):
    start_time = time.time()
    try:
        postgres = Postgres()
        if not create_session_request:
            tenant_name = ""
            user_code = ""
            database_id = None
        else:
            tenant_name = create_session_request.tenant_name
            user_code = create_session_request.user_code
            database_id = create_session_request.database_id
            
        session_id = await postgres.create_session(tenant_name=tenant_name, user_code=user_code, database_id=database_id)
        elapsed_time = time.time() - start_time
        non_generative_agent_logger(
            session_id=session_id.get("session_id"),
            tenant_name=tenant_name,
            user_code=user_code,
            agent="session_creator",
            message="session created",
            input_dict={
                "tenant_name": tenant_name,
                "user_code": user_code,
            },
            output_dict={"response": session_id.get("session_id")},
            elapsed_time=elapsed_time,
        )
        langfuse_context = get_client()
        langfuse_context.update_current_trace(
            input={"create_session_request": create_session_request},
            output={"session_id": session_id}
        )
        return session_id
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unhandled error, Please report")

@app.post(
    "/v1/chat",
    response_model=ChatResponse,
    responses={
        200: {},
        500: {"description": "Unhandled error that should be reported"},
        404: {
            "description": "Session not found",
            "content": {
                "application/json": {"example": {"detail": "Session not found"}}
            },
        },
        422: {
            "description": "Unprocessable entity e.g. no session id, or no query",
            "content": {"application/json": {"example": {"detail": "Query is empty"}}},
        },
    },
)
@observe()
async def chat_responder(chat_request: ChatRequest, request: Request, clients: dict = Depends(get_client_llm)):
    REQUEST_COUNT.labels(endpoint="/v1/chat").inc()
    start_time = time.time()
    is_sql = False
    context = ""
    agent = "chat_responder"
    message = "Chat response generated"
    choices = []
    do_suggest = False
    parameters = {}
    # parametric_response = None
    response_template = ""
    tenant_name = ""
    user_code = ""

    try:
        session_id = get_session_id(request, chat_request)
        if not chat_request.is_sync:
            final_records = await async_responder(session_id)
            response = final_records.get("response", "")
            paraphrased_utterance = final_records.get("paraphrased_query", "")
            message_id = str(final_records.get("message_id", ""))
            is_sql = final_records.get("is_sql", False)
            do_suggest = final_records.get("do_suggest", False)
            choices = final_records.get("choices", [])
            elapsed_time = final_records.get("elapsed_time", 0)
            parameters = json.loads(final_records.get("parameters", "{}"))
            response_template = final_records.get("response_template", "")
        else:
            postgres = Postgres()
            user_code, tenant_name = await get_user_code_tenant_name(chat_request, postgres)
            session_validation = await postgres.exist_session(session_id)
            if not session_validation:
                raise HTTPException(
                    status_code=404,
                    detail=f"Session not found: {session_id}"
                )
            validate_query(chat_request.query) # excessive request handling, we can remove it as soon as possible
            session_validation = await postgres.exist_session(session_id)
            if not session_validation:
                raise HTTPException(
                    status_code=404,
                    detail=f"Session not found: {session_id}"
                )
            simple_logger(f"Received chat request", session_id)
            history = await postgres.get_history(
                session_id,
                1,
                config["postgres"]["history_length"],
                True
            )
            
            if len(chat_request.query.split()) > 60:
                paraphrased_utterance, response, context = (
                    "No valid query",
                    RESPONSE_TEMPLATE_FOR_NO_ANSWER,
                    "",
                )
                if not chat_request.sql_mode:
                    # Legacy mode: insert immediately
                    message_id = await postgres.insert_chat_row(
                        session_id=session_id,
                        user_query=chat_request.query,
                        paraphrased_query=paraphrased_utterance,
                        bot_response=response,
                        response_type=chat_request.response_type,
                        elapsed_time=time.time() - start_time,
                        response_template=response_template,
                        parameters=json.dumps(parameters)
                    )
                else:
                    # SQL mode: use different insertion pattern
                    message_id = await postgres.insert_chat_row( # concise response in the database should be modified
                        session_id=session_id,
                        user_query=chat_request.query,
                        paraphrased_query=paraphrased_utterance,
                        bot_response=response,
                        response_type=chat_request.response_type,
                        elapsed_time=time.time() - start_time,
                        response_template=response_template,
                        parameters=json.dumps(parameters)
                    )
                elapsed_time = time.time() - start_time
            else:
                database_id_dict = await postgres.find_database_id(session_id)
                # company_name, assistant_name = find_company_assistant_names(postgres, database_id_dict["database_id"])
                matched_index, company_name, assistant_name = find_database_collection_with_postgres(postgres, database_id_dict["database_id"])
                selected_history = [
                    [h["query"], h["response"]] if len(h["query"]) < 60 
                    else [h["paraphrased_query"], h["response"]]
                    for h in history
                ]
                
                # Use SQL Agent logic
                if chat_request.do_retry:
                    # Handle SQL retry logic
                    is_sql = True
                    agent = "sql_responder"
                    paraphrased_utterance = history[-1]["paraphrased_query"]
                    message_id = str(history[-1]["message_id"])
                    selected_module = history[-1]["selected_module"]
                    faulty_sql_query = history[-1]["response"]
                    faulty_sql_query_parameters = history[-1]["parameters"]
                    
                    _ = await postgres.remove_previous_response(history[-1]["message_id"])
                    response_dict_str = await sql_responder_(
                        clients,
                        paraphrased_utterance,
                        selected_module,
                        faulty_sql_query,
                        chat_request.error_payload,
                        chat_request.do_retry,
                        faulty_sql_query_parameters, 
                        use_oss=chat_request.use_oss
                    )
                    response_dict = json.loads(response_dict_str)
                    if "NULL" not in response_dict_str:
                        response_dict["SQL"] = convert_sql_parameters(response_dict["SQL"])
                        response = response_dict["SQL"]
                        if response_dict["parameters"]:
                            response_dict["parameters"] = add_underscore_to_keys(response_dict["parameters"])
                        bo_parameters_with_template = await parameters_responder(paraphrased_utterance, response, selected_module)
                        bo_parameters_with_template_dict = json.loads(bo_parameters_with_template)
                        parameters_dict = finalize_parameters(response_dict, bo_parameters_with_template_dict)
                        parameters = parameters_dict["parameters"]
                        response_template = bo_parameters_with_template["response_template"]
                     
                    message = "retried table response generated"
                    elapsed_time = time.time() - start_time
                    _ = await postgres.update_on_click_chat_row(message_id, response, elapsed_time)

                elif chat_request.on_click:
                    # Handle on_click logic
                    selected_module = chat_request.query
                    do_suggest = False
                    message_id = await postgres.insert_chat_row(
                        session_id=session_id,
                        user_query=chat_request.query,
                    )
                    
                    paraphrased_utterance, response, context, do_clarify, modules = await chat_responder_(
                        clients,
                        selected_history,
                        chat_request.query,
                        detected_module=chat_request.query,
                        database_index=matched_index,
                        company_name=company_name,
                        assistant_name=assistant_name, 
                        use_oss=chat_request.use_oss, 
                    )
                    assert do_clarify == False, "on_click should not return do_clarify=True"
                    assert len(modules) <= 1, "on_click should not return modules"

                    if not response:
                        if chat_request.sql_mode:
                            if chat_request.query in ["انبار", "فروش", "دفتر کل"]:
                                is_sql = True                           
                                agent = "sql_responder"
                                response_dict_str = await sql_responder_(
                                    clients, 
                                    paraphrased_utterance,
                                    chat_request.query,
                                    "",
                                    "",
                                    chat_request.do_retry,
                                    use_oss=chat_request.use_oss
                                )
                                response_dict = json.loads(response_dict_str)
                                if "null" not in response_dict_str and response_dict["SQL"] is not None:
                                    response_dict["SQL"] = convert_sql_parameters(response_dict["SQL"])
                                    response = response_dict["SQL"]
                                    if response_dict["parameters"]:
                                        response_dict["parameters"] = add_underscore_to_keys(response_dict["parameters"])
                                    bo_parameters_with_template = await parameters_responder(paraphrased_utterance, response, selected_module)
                                    bo_parameters_with_template_dict = json.loads(bo_parameters_with_template)
                                    parameters_dict = finalize_parameters(response_dict, bo_parameters_with_template_dict)
                                    parameters = parameters_dict["parameters"]
                                    response_template = bo_parameters_with_template["response_template"]
                                else:
                                    is_sql = False
                                    response = RESPONSE_TEMPLATE_FOR_NO_ANSWER
                            else:
                                is_sql = False
                                response = RESPONSE_TEMPLATE_FOR_NO_ANSWER
                        else:
                            is_sql = False
                            response = RESPONSE_TEMPLATE_FOR_NO_ANSWER
                                                
                    elapsed_time = time.time() - start_time
                    message_id = await postgres.update_last_chat_row(
                        session_id,
                        paraphrased_utterance,
                        response,
                        is_sql,
                        elapsed_time,
                        do_suggest,
                        "",
                        response_template,
                        json.dumps(parameters)
                    )

                else:
                    # Regular SQL agent processing
                    message_id = await postgres.insert_chat_row(
                        session_id=session_id,
                        user_query=chat_request.query,
                    )
                    
                    paraphrased_utterance, response, context, do_clarify, modules = await chat_responder_(
                        clients,
                        selected_history,
                        chat_request.query,
                        detected_module="",
                        database_index=matched_index,
                        company_name=company_name,
                        assistant_name=assistant_name, 
                        use_oss=chat_request.use_oss, 
                    )
                    if do_clarify:
                        do_suggest = True
                        response = MODULE_CLARIFICATION_RESPONSE_TEMPLATE
                        elapsed_time = time.time() - start_time
                        _ = await postgres.insert_message_choices(message_id, *modules)
                        message_id = await postgres.update_last_chat_row(
                            session_id,
                            paraphrased_utterance,
                            MODULE_CLARIFICATION_RESPONSE_TEMPLATE,
                            is_sql,
                            elapsed_time,
                            do_suggest,
                            response_template,
                            json.dumps(parameters)
                        )
                        agent = "module_clarification"
                        message = "modules proposed"
                        choices = modules
                    else:
                        if not response:
                            if chat_request.sql_mode and modules:
                                selected_module = modules[0]
                                agent = "sql_responder"
                                is_sql = True
                                response_dict_str = await sql_responder_(
                                    clients,
                                    paraphrased_utterance,
                                    selected_module,
                                    "",
                                    "",
                                    chat_request.do_retry,
                                    use_oss=chat_request.use_oss
                                )
                               
                                response_dict = json.loads(response_dict_str)
                                if "null" not in response_dict_str and response_dict["SQL"] is not None:
                                    response_dict["SQL"] = convert_sql_parameters(response_dict["SQL"])
                                    response = response_dict["SQL"]
                                    if response_dict["parameters"]:
                                        response_dict["parameters"] = add_underscore_to_keys(response_dict["parameters"])
                                    bo_parameters_with_template = await parameters_responder(paraphrased_utterance, response, selected_module)
                                    bo_parameters_with_template_dict = json.loads(bo_parameters_with_template)
                                    parameters_dict = finalize_parameters(response_dict, bo_parameters_with_template_dict)
                                    parameters = parameters_dict["parameters"]
                                    response_template = parameters_dict["response_template"]
                                else:
                                    is_sql = False
                                    response = RESPONSE_TEMPLATE_FOR_NO_ANSWER
                            
                            else:
                                is_sql = False
                                response = RESPONSE_TEMPLATE_FOR_NO_ANSWER
                            
                        elapsed_time = time.time() - start_time
                        modules_str = modules[0] if modules else "cache"

                        message_id = await postgres.update_last_chat_row(
                            session_id,
                            paraphrased_utterance,
                            response,
                            is_sql,
                            elapsed_time,
                            do_suggest,
                            modules_str,
                            response_template,
                            json.dumps(parameters)
                        )
                
        REQUEST_LATENCY.labels(endpoint="/v1/chat").observe(time.time() - start_time)
        non_generative_agent_logger(
            session_id=session_id,
            tenant_name=tenant_name,
            user_code=user_code,
            agent=agent,
            message=message,
            input_dict={
                "user_utterance": chat_request.query,
                "paraphrased_query": paraphrased_utterance,
                "context": context,
            },
            output_dict={
                "response": response,
                "is_sql": is_sql,
                "do_suggest": do_suggest,
                "choices": choices,
                "response_templated": response_template
            },
            elapsed_time=elapsed_time,
        )
        
        langfuse_context = get_client()
        langfuse_context.update_current_trace(
            input={"chat_request": chat_request, "request": request},
            output={
                "response": response,
                "message_id": message_id,
                "query": paraphrased_utterance,
                "is_sql": is_sql,
                "choices": choices,
                "do_suggest": do_suggest,
                "parameters": parameters
            }
        )
        
        return ChatResponse(
            response=response,
            message_id=message_id,
            query=paraphrased_utterance,
            is_sql=is_sql,
            choices=choices,
            do_suggest=do_suggest,
            parameters=parameters,
            response_template=response_template
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        traceback.print_exc()
        elapsed_time = time.time() - start_time
        REQUEST_LATENCY.labels(endpoint="/v1/chat").observe(elapsed_time)
        
        non_generative_agent_logger(
            session_id=session_id,
            tenant_name=tenant_name,
            user_code=user_code,
            agent="chat_responder",
            message="exception happened",
            input_dict={
                "user_utterance": chat_request.query,
                "paraphrased_query": "",
            },
            output_dict={
                "response": "",
                "do_suggest": do_suggest,
                "choices": choices,
                "parameters": dict(parameters),
                "response_template": response_template
            },
            elapsed_time=elapsed_time,
        )
        raise HTTPException(status_code=500, detail="Unhandled error, Please report")

@app.post(
    "/v1/chat/sql",
    response_model=SQLResponse,
    responses={
        200: {},
        500: {"description": "Unhandled error that should be reported"},
        404: {"description": "Session not found"},
        422: {"description": "Unprocessable entity"},
    },
)
@observe()
async def sql_responder_endpoint(clients, sql_request: SQLRequest, request: Request):
    REQUEST_COUNT.labels(endpoint="/v1/chat/sql").inc()
    start_time = time.time()

    try:
        postgres = Postgres()
        
        # Handle both legacy (table_schemas) and new (session-based) approaches
        if sql_request.table_schemas:
            # Legacy approach: direct SQL generation from schemas
            response = await sql_responder_(clients, sql_request.query, sql_request.table_schemas)
            return SQLResponse(response=response, do_suggest=False, choices=[], message_id="")
        
        # New approach: session-based with module detection
        session_id = get_session_id(request, sql_request)
        
        if sql_request.on_click:
            history = await postgres.get_history(session_id, 1, 1, True)
            user_question = history[0]["query"]
            message_id = str(history[0]["message_id"])
            detected_module = sql_request.query
            is_sql = True
            response = await sql_responder_(
                clients,
                user_question,
                detected_module,
                use_oss=chat_request.use_oss
            )
            
            elapsed_time = time.time() - start_time
            await postgres.update_on_click_chat_row(message_id, response, elapsed_time)
            choices = []
        else:
            elapsed_time = time.time() - start_time
            message_id = await postgres.insert_chat_row(
                session_id,
                sql_request.query,
                sql_request.query,
                "",
                elapsed_time,
            )
            response = ""
            choices = await module_proposer()

        return SQLResponse(
            response=response,
            do_suggest=len(choices) > 0,
            choices=choices,
            message_id=message_id
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unhandled error, Please report")


def get_logger():
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(__name__)

logger = get_logger()

# Initialize global Qdrant client
def get_qdrant_client():
    """Get Qdrant client from environment variables."""
    qdrant_host = os.getenv("QDRANT_API_BASE")
    qdrant_port = os.getenv("QDRANT_API_PORT")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

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

# Global Qdrant client instance
qdrant_client = get_qdrant_client()


# ===== Main Endpoint Handler =====
async def create_database_endpoint(
    files: List[UploadFile],
    company_name: str,
    assistant_name: str,
    postgres,  # Your Postgres class instance
    use_config: bool = True,
    recreate: bool = True,
    batch_size: int = 100,
    default_collection: bool = False
) -> Dict[str, Any]:
    """
    Main endpoint handler for creating a vector database.
    
    Complete pipeline:
    1. Process and chunk uploaded files
    2. Create database entry in PostgreSQL
    3. Create Qdrant collection with chunked documents
    
    Args:
        files: List of uploaded files
        company_name: Name of the company
        assistant_name: Name of the assistant
        postgres: PostgreSQL client instance
        use_config: If True, use config-based approach (recommended)
        recreate: If True, recreate collection if exists; if False, append
        batch_size: Number of documents to process in each batch
    
    Returns:
        dict: Response containing database_id and collection_name
    """
    try:
        # Step 1: Process uploaded files (save → convert → chunk)
        logger.info("=" * 60)
        logger.info("STEP 1: Processing uploaded files")
        logger.info("=" * 60)
        processed_files = await process_uploaded_files(
            files=files,
            company_name=company_name,
            assistant_name=assistant_name
        )
        
        # Flatten all documents into a single list
        all_documents = []
        for filename, documents in processed_files.items():
            all_documents.extend(documents)
        
        logger.info(f"\nTotal documents created: {len(all_documents)}")
        logger.info(f"Files processed: {list(processed_files.keys())}")
        
        if len(all_documents) == 0:
            raise HTTPException(
                status_code=422,
                detail="No documents were extracted from the uploaded files"
            )
        
        # Step 2: Create database entry in PostgreSQL
        logger.info("\n" + "=" * 60)
        logger.info("STEP 2: Creating database entry in PostgreSQL")
        logger.info("=" * 60)
        if default_collection:
            database_id = "default_collection"
        else:
            try:
                database_id_dict = await postgres.create_database(company_name, assistant_name)
                database_id = database_id_dict["database_id"]
                logger.info(f"✅ Database ID created: {database_id}")
            except Exception as e:
                logger.error(f"❌ Failed to create database entry in PostgreSQL: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to create database entry: {str(e)}"
                )
        
        # Step 3: Create Qdrant collection with documents
        logger.info("\n" + "=" * 60)
        logger.info("STEP 3: Creating Qdrant collection")
        logger.info("=" * 60)
        
        try:
            if use_config:
                # Use config-based approach (automatically uses Triton if configured)
                collection_name = create_vector_database_from_config(
                    database_id=database_id,
                    all_documents=all_documents,
                    recreate=recreate,
                    batch_size=batch_size
                )
            else:
                # Use standalone approach with explicit parameters
                model_manager = ModelManager()
                collection_name = create_vector_database(
                    database_id=database_id,
                    all_documents=all_documents,
                    qdrant_client=qdrant_client,
                    embedding_model=model_manager.embedding_model,
                    recreate=recreate,
                    batch_size=batch_size
                )
        except Exception as e:
            logger.error(f"❌ Failed to create Qdrant collection: {e}")
            # Rollback: Delete PostgreSQL entry if collection creation fails
            if not default_collection:
                try:
                    await postgres.delete_database(database_id)
                    logger.info(f"Rolled back PostgreSQL entry for database_id: {database_id}")
                except Exception as rollback_error:
                    logger.error(f"Failed to rollback PostgreSQL entry: {rollback_error}")
            else:
                logger.info(f"Couldn't create default collection: {database_id}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create vector database: {str(e)}"
            )
        
        # Verify collection_name matches database_id
        assert collection_name == database_id, "Collection name should match database_id"
        
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info(f"Database ID: {database_id}")
        logger.info(f"Collection Name: {collection_name}")
        logger.info(f"Total documents: {len(all_documents)}")
        logger.info("=" * 60)
        
        return {
            "database_id": database_id,
            "collection_name": collection_name,
            "message": f"Database created successfully. Collection: {collection_name}",
            "total_documents": len(all_documents),
            "files_processed": list(processed_files.keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error creating database: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create database: {str(e)}"
        )


# ===== FastAPI Endpoints =====

@app.post(
    "/v1/chat/create/database",
    response_model=CreateDatabaseResponse,
    responses={
        200: {"description": "Database created successfully"},
        422: {"description": "Unprocessable entity - invalid input or no documents extracted"},
        500: {"description": "Internal server error"},
    },
    summary="Create a new vector database",
    description="Upload files, process them into chunks, and create a vector database with embeddings"
)
async def create_database(
    files: List[UploadFile] = File(..., description="Files to upload and process"),
    company_name: str = Query(..., description="Company name"),
    assistant_name: str = Query(..., description="Assistant name"),
    recreate: bool = Query(True, description="Recreate collection if exists"),
    batch_size: int = Query(100, description="Batch size for processing documents", ge=1, le=1000),
    default_collection: bool = Query(False, description="Whether the default collection be recreated or not")
):
    """
    Create a new vector database from uploaded files.
    
    This endpoint:
    1. Uploads and processes files
    2. Creates a PostgreSQL database entry
    3. Creates a Qdrant collection with document embeddings
    
    The embedding model is automatically selected based on the configuration
    (e.g., Triton E5/BGE, local models, or other services).
    """
    postgres = Postgres()
    
    return await create_database_endpoint(
        files=files,
        company_name=company_name,
        assistant_name=assistant_name,
        postgres=postgres,
        use_config=True,  # Use config-based approach
        recreate=recreate,
        batch_size=batch_size, 
        default_collection=default_collection
    )

@app.post(
    "/v1/chat/database/{database_id}/add-documents",
    response_model=AddDocumentsResponse,
    responses={
        200: {"description": "Documents added successfully"},
        404: {"description": "Database not found"},
        422: {"description": "No documents extracted from files"},
        500: {"description": "Internal server error"},
    },
    summary="Add documents to existing database",
    description="Upload additional files and add them to an existing vector database"
)
async def add_documents_to_database(
    database_id: str,
    files: List[UploadFile] = File(..., description="Additional files to upload"),
    batch_size: int = Query(100, description="Batch size for processing", ge=1, le=1000)
):
    """
    Add more documents to an existing vector database.
    
    Args:
        database_id: The existing database to add documents to
        files: The new files to process and add
        batch_size: Number of documents to process in each batch
    
    Returns:
        Response with success message and document count
    """
    try:
        # Check if collection exists
        collections = list_vector_databases(qdrant_client)
        if database_id not in collections:
            raise HTTPException(
                status_code=404,
                detail=f"Database '{database_id}' not found"
            )
        
        # Process uploaded files without company/assistant context
        logger.info(f"Processing {len(files)} files for database: {database_id}")
        processed_files = await process_uploaded_files(
            files=files,
            company_name=None,  # Not needed for adding to existing DB
            assistant_name=None  # Not needed for adding to existing DB
        )
        
        # Flatten documents
        all_documents = []
        for filename, documents in processed_files.items():
            all_documents.extend(documents)
        
        if len(all_documents) == 0:
            raise HTTPException(
                status_code=422,
                detail="No documents were extracted from the uploaded files"
            )
        
        logger.info(f"Adding {len(all_documents)} documents to database '{database_id}'")
        
        # Add documents to existing collection
        success = add_documents_to_existing_collection(
            database_id=database_id,
            documents=all_documents,
            qdrant_client=qdrant_client,
            embedding_model=None,  # Will use config default
            batch_size=batch_size
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to add documents to database"
            )
        
        # Get updated collection info
        info = get_collection_info(database_id, qdrant_client)
        
        return {
            "message": f"Successfully added {len(all_documents)} documents to database '{database_id}'",
            "database_id": database_id,
            "documents_added": len(all_documents),
            "total_documents": info.get("points_count", "unknown") if info else "unknown"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add documents: {str(e)}"
        )

@app.get(
    "/v1/chat/list/collections",
    response_model=ListCollectionsResponse,
    responses={
        200: {"description": "Collections listed successfully"},
        500: {"description": "Internal server error"},
    },
    summary="List all vector databases",
    description="Get a list of all available Qdrant collections (databases)"
)
async def list_collections():
    """
    Lists all available Qdrant collections (databases).
    Each collection name corresponds to a database_id in PostgreSQL.
    """
    try:
        collection_names = list_vector_databases(qdrant_client)
        
        return {
            "collections": collection_names,
            "count": len(collection_names)
        }
    except Exception as e:
        logger.error(f"Error listing collections: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list collections: {str(e)}"
        )


@app.get(
    "/v1/chat/database/{database_id}/info",
    response_model=DatabaseInfoResponse,
    responses={
        200: {"description": "Database info retrieved successfully"},
        404: {"description": "Database not found"},
        500: {"description": "Internal server error"},
    },
    summary="Get database information",
    description="Get detailed information about a specific vector database"
)
async def get_database_info_endpoint(database_id: str):
    """
    Gets detailed information about a specific database by database_id.
    The database_id is used as the collection_name.
    """
    try:
        info = get_collection_info(database_id, qdrant_client)
        if info is None:
            raise HTTPException(
                status_code=404,
                detail=f"Database '{database_id}' not found"
            )
        
        return info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting database info: {str(e)}")
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=404,
                detail=f"Database '{database_id}' not found"
            )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get database info: {str(e)}"
        )


@app.get(
    "/v1/chat/database/{database_id}/modules",
    responses={
        200: {"description": "Modules listed successfully"},
        404: {"description": "Database not found"},
        500: {"description": "Internal server error"},
    },
    summary="List modules in database",
    description="Get all unique module names in a database"
)
async def list_database_modules(database_id: str):
    """
    Get all unique module names (metadata.module) in a database.
    Useful for filtered retrieval.
    """
    from src.retriever import Retriever
    
    try:
        # Check if collection exists
        collection_names = list_vector_databases(qdrant_client)
        if database_id not in collection_names:
            raise HTTPException(
                status_code=404,
                detail=f"Database '{database_id}' not found"
            )
        
        # Get modules
        retriever = Retriever()
        modules = retriever.get_available_modules(collection_name=database_id)
        
        return {
            "database_id": database_id,
            "modules": modules,
            "count": len(modules)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing modules: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list modules: {str(e)}"
        )


@app.get(
    "/v1/chat/health",
    responses={
        200: {"description": "Service is healthy"},
        503: {"description": "Service is unhealthy"},
    },
    summary="Health check endpoint",
    description="Check if the service and dependencies are healthy"
)
async def health_check():
    """
    Health check endpoint for the service.
    Checks connectivity to Qdrant and availability of embedding models.
    """
    health_status = {
        "status": "healthy",
        "services": {}
    }
    
    # Check Qdrant
    try:
        collections = list_vector_databases(qdrant_client)
        health_status["services"]["qdrant"] = {
            "status": "healthy",
            "collections_count": len(collections)
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["services"]["qdrant"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check Embedding Model
    try:
        model_manager = ModelManager()
        embedding_config = config.get("embedding_model", {})
        health_status["services"]["embedding_model"] = {
            "status": "healthy",
            "type": embedding_config.get("type", "unknown"),
            "model": embedding_config.get("model_name", "unknown")
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["services"]["embedding_model"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check Reranker Model
    try:
        reranker_config = config.get("reranker", {})
        health_status["services"]["reranker_model"] = {
            "status": "healthy",
            "type": reranker_config.get("type", "unknown"),
            "model": reranker_config.get("model_name", "unknown")
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["services"]["reranker_model"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)


@app.get(
    "/v1/chat/config",
    responses={
        200: {"description": "Configuration retrieved successfully"},
    },
    summary="Get current configuration",
    description="Get the current embedding and reranker configuration (sensitive info redacted)"
)
async def get_config():
    """
    Get current service configuration (API keys and sensitive info redacted).
    """
    embedding_config = config.get("embedding_model", {}).copy()
    reranker_config = config.get("reranker", {}).copy()
    
    # Redact sensitive information
    if "api_key" in embedding_config:
        embedding_config["api_key"] = "***REDACTED***"
    if "api_key" in reranker_config:
        reranker_config["api_key"] = "***REDACTED***"
    
    return {
        "embedding_model": embedding_config,
        "reranker": reranker_config,
        "retriever": config.get("retriever", {})
    }


@app.delete(
    "/v1/chat/delete/database/{database_id}",
    response_model=DeleteDatabaseResponse,
    responses={
        200: {"description": "Database deleted successfully"},
        404: {"description": "Database not found"},
        500: {"description": "Internal server error"},
    },
    summary="Delete a vector database",
    description="Delete a Qdrant collection by database_id"
)
async def delete_database(
    database_id: str,
    delete_postgres: bool = Query(False, description="Also delete PostgreSQL entry")
):
    """
    Deletes a Qdrant collection by database_id.
    The database_id is used as the collection_name.
    
    Optionally deletes the PostgreSQL entry as well.
    """
    try:
        # Check if collection exists
        collection_names = list_vector_databases(qdrant_client)
        if database_id not in collection_names:
            raise HTTPException(
                status_code=404,
                detail=f"Database '{database_id}' not found"
            )
        
        # Delete Qdrant collection
        success = delete_vector_database(database_id, qdrant_client)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete database '{database_id}'"
            )
        
        # Optionally delete PostgreSQL entry
        if delete_postgres:
            try:
                postgres = Postgres()
                await postgres.delete_database(database_id)
                logger.info(f"✅ Deleted PostgreSQL entry for database_id: {database_id}")
            except Exception as pg_error:
                logger.warning(f"⚠️ Failed to delete PostgreSQL entry: {pg_error}")
                # Don't fail the whole operation if PostgreSQL deletion fails
        
        return {
            "message": f"Database '{database_id}' deleted successfully",
            "database_id": database_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting database: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete database: {str(e)}"
        )
        
@app.post(
    "/v1/feedback",
    responses={
        200: {"content": {"application/json": {"example": {"message": "Feedback received"}}}},
        422: {"description": "Invalid feedback", "content": {"application/json": {"example": {"detail": "No Session-ID"}}}},
        404: {"description": "Message not found", "content": {"application/json": {"example": {"detail": "Message not found"}}}},
        500: {"description": "Unhandled error"},
    },
)
@observe()
async def feedback(feedback_request: FeedbackRequest, request: Request):
    endpoint = "/v1/feedback"
    REQUEST_COUNT.labels(endpoint=endpoint).inc()
    start_time = time.time()
    try:

        session_id = get_session_id(request, feedback_request)
        if session_id is None:
            session_id = feedback_request.session_id


            if session_id is None:
                raise HTTPException(status_code=422, detail="No Session-ID")

        message_fields = await fetch_message_fields(
            session_id, feedback_request.message_id
        )

        log_feedback_request(session_id)
        result = await process_feedback(feedback_request, message_fields)

        log_feedback_response(session_id, "", "", feedback_request, message_fields, start_time)
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        handle_unexpected_error(e, session_id, feedback_request, start_time)


# def validate_feedback(feedback_request: FeedbackRequest):
#     if feedback_request.feedback_type not in ["thumb_up", "thumb_down", "flag"]:
#         raise HTTPException(status_code=422, detail="Invalid feedback")

def validate_feedback(feedback_request: FeedbackRequest):
    if feedback_request.feedback_type not in ["thumb_up", "thumb_down", "flag"]:
        raise HTTPException(status_code=422, detail="Invalid feedback")


async def fetch_message_fields(session_id, message_id):
    postgres = Postgres()
    message_fields = await postgres.get_message_fields(session_id, message_id)

    if not message_fields:
        raise HTTPException(status_code=404, detail="Message not found")

    return message_fields


async def process_feedback(feedback_request, message_fields):
    message_id = feedback_request.message_id
    postgres = Postgres()
    result = await postgres.set_feedback(message_id, feedback_request.feedback_type)

    if result:
        # user_query, paraphrased_query, bot_response = message_fields
        # await feedback_(paraphrased_query, bot_response, "", feedback_request.feedback_type)
        return FeedbackResponse(message="feedback received")
    return FeedbackResponse(message="duplicate feedback")


def log_feedback_request(session_id):
    simple_logger("Received feedback request", session_id)


def log_feedback_response(session_id, tenant_name, user_code, feedback_request, message_fields, start_time):
    elapsed_time = time.time() - start_time
    REQUEST_LATENCY.labels(endpoint="/v1/feedback").observe(elapsed_time)

    user_query, paraphrased_query, _ = message_fields
    non_generative_agent_logger(
        session_id=session_id,
        tenant_name=tenant_name,
        user_code=user_code,
        agent="feedback",
        message="feedback generated",
        input_dict={
            "user_utterance": user_query,
            "paraphrased_query": paraphrased_query,
        },
        output_dict={"response": feedback_request.feedback_type},
        elapsed_time=elapsed_time,
    )


def handle_unexpected_error(exception, tenant_name, user_code, session_id, feedback_request, start_time):
    elapsed_time = time.time() - start_time
    REQUEST_LATENCY.labels(endpoint="/v1/feedback").observe(elapsed_time)

    traceback.print_exc()
    non_generative_agent_logger(
        session_id,
        tenant_name,
        user_code,
        "feedback",
        f"Error in feedback: {str(exception)}",
        feedback_request.dict(),
        {},
        elapsed_time,
    )
    raise HTTPException(status_code=500, detail="Unhandled error, Please report")
