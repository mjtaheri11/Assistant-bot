import asyncio
import json
import logging
import re
import os
import shutil
import time
import traceback
from typing import List, Any, Optional, Dict

from fastapi import FastAPI, HTTPException, Request, Query, File, UploadFile, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest
from pydantic import BaseModel, Field
from starlette.responses import Response
from langfuse import observe, get_client
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from openai import AsyncOpenAI
import tempfile
from pathlib import Path
import aiofiles

from src.shear_parser import convert_word_to_markdown, SoleChunker, preprocess_markdown_file
from src.llm_clients import llm_manager
from src.utils import has_video_link_
# Langfuse configuration
load_dotenv()

LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")
FEEDBACK_ENDPOINT = "/v1/feedback"
CHAT_ENDPOINT = "/v1/chat"
SQL_ENDPOINT = "/v1/chat/sql"
UNHANDLED_ERROR_MESSAGE = "Unhandled error, Please report"

from src.vector_db_utils import (
    create_vector_database,
    create_vector_database_from_config,
    delete_vector_database,
    list_vector_databases,
    get_collection_info,
    add_documents_to_existing_collection,
    upsert_documents_by_source
)
from src.orm import Postgres
from src.config import config
from qdrant_client import QdrantClient                          # client class
from qdrant_client.models import Filter, FieldCondition, MatchValue  # query building blocksqdrant_client
from src.retriever import Retriever, ModelManager
from src.logic import (
    chat_responder_,
    sql_responder_,
    ticket_responder_,
    utterance_paraphraser,
    parameters_responder,
    retrieve_context_with_metadata,
    embed_query,
    warmup_prompt_template_sizes,
)
from src.logs import non_generative_agent_logger, simple_logger
from src.utils import substitute_sql_parameters, integrate_params

from langchain.schema import Document

@asynccontextmanager
async def lifespan(app: FastAPI):
    await llm_manager.initialize()
    warmup_prompt_template_sizes()
    yield
    await llm_manager.close()


RESPONSE_TEMPLATE_FOR_NO_ANSWER = "متاسفانه، پاسخی به سوال شما یافت نشد."
from fastapi import Request

app = FastAPI(
    title="Digital Assistant",
    lifespan=lifespan,
    root_path=os.getenv("FASTAPI_ROOT_PATH", ""),  # "" not None
    docs_url=None,
    redoc_url=None,
)

app.mount(
    "/swagger-static",
    StaticFiles(directory=os.getenv("FASTAPI_LOCAL_FILES_PATH")),
    name="swagger-static",
)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    root = app.root_path
    return get_swagger_ui_html(
        openapi_url=root + app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url=root + "/swagger-static/swagger-ui-bundle.js",
        swagger_css_url=root + "/swagger-static/swagger-ui.css",
        swagger_favicon_url=root + "/swagger-static/favicon-32x32.png",
    )
    
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
    use_cache: Optional[bool] = True
    # SQL Agent specific fields
    on_click: Optional[bool] = False
    error_payload: Optional[str] = ""
    is_sync: Optional[bool] = True
    model_name: Optional[str] = ""
    sql_mode: Optional[bool] = False  # Toggle between legacy and SQL agent mode
    use_video_links: Optional[bool] = True
    ticket_mode: Optional[bool] = False

 
class ChatResponse(BaseModel):
    message_id: str
    response: str
    query: str
    is_sql: bool = False
    is_ticket: bool = False   # <-- NEW
    do_suggest: bool = False
    choices: List[str] = []
    parameters: Optional[dict] = {}
    response_template: str = ""
    elapsed_time: float = 0.0
    has_video_link: bool = False

class CreateSessionRequest(BaseModel):
    tenant_name: Optional[str] = ""
    user_code: Optional[str] = ""
    database_id: Optional[str] = ""
    objects: Optional[dict] = None

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
    contain_paraphrase: bool = False

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

class ModulesInfoResponse(BaseModel):
    database_id: str
    modules: List[str]
    count: int
    module_counts: Dict[str, int]
    total_chunks: int

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
    write_mode: Optional[str] = None          # <-- add
    vectors_deleted: Optional[int] = None      # <-- add

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

class NL2SQLDatabaseResponse(BaseModel):
    success: bool
    message: str
    collection_name: str
    documents_count: int
    total_documents: Optional[int] = None

class TicketRequest(BaseModel):
    session_id: Optional[str] = None

class TicketResponse(BaseModel):
    title: str = ""
    description: str = ""
    system: str = ""
    form: str = ""

class ModuleChunksRequest(BaseModel):
    module: str

class ChunkInfo(BaseModel):
    text: str
    metadata: Dict[str, Any]

class ModuleChunksResponse(BaseModel):
    database_id: str
    module: str
    count: int
    chunks: List[ChunkInfo]

# ================== Utility Functions ==================

def extract_video_links(text: str) -> List[str]:
    """Extract video link patterns (e.g., videolink-gl005) from text."""
    pattern = r'videolink-\w+'
    return re.findall(pattern, text)

def find_module_name(original_filename):
    main_filename = Path(original_filename).stem  
    module = config["modules"]["names"][main_filename]
    return module
    

def _parse_json_file(content: bytes, filename: str) -> List[Dict[str, Any]]:
    """Parse JSON content from uploaded file."""
    try:
        data = json.loads(content.decode("utf-8"))
        return data if isinstance(data, list) else [data]
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid JSON in file '{filename}': {str(e)}"
        )


def _json_item_to_document(item: Dict[str, Any]) -> Document:
    """
    Convert a JSON item to a LangChain Document for NL2SQL.
    
    - page_content: The question (for embedding/similarity search)
    - metadata: SQL, parameters, module, complexity, table
    - 'id' is excluded as it may vary across files
    """
    question = item.get("question", "")
    
    if not question:
        raise ValueError("Item missing 'question' field")
    
    sql_obj = item.get("sql", {})
    sql_query = sql_obj.get("SQL", "")
    sql_parameters = sql_obj.get("parameters", {})
    response_template = sql_obj.get("response_template", "")
    metadata = {
        "sql": sql_query,
        "parameters": json.dumps(sql_parameters, ensure_ascii=False),
        "complexity": item.get("complexity", ""),
        "module": item.get("module", ""),
        "table": item.get("table", ""),
        "response_template": response_template
    }
    
    return Document(page_content=question, metadata=metadata)


async def process_nl2sql_json_files(
    files: List[UploadFile]
) -> List[Document]:
    """
    Process multiple JSON files and convert to Documents.
    
    Args:
        files: List of uploaded JSON files
        
    Returns:
        List of LangChain Documents
    """
    all_documents = []
    
    for file in files:
        # Validate file type
        if not file.filename.endswith(".json"):
            raise HTTPException(
                status_code=422,
                detail=f"File '{file.filename}' is not a JSON file. Only .json files are accepted."
            )
        
        content = await file.read()
        items = _parse_json_file(content, file.filename)
        
        for idx, item in enumerate(items):
            try:
                doc = _json_item_to_document(item)
                all_documents.append(doc)
            except ValueError as e:
                logger.warning(f"Skipping item {idx} in '{file.filename}': {e}")
                continue
            except Exception as e:
                logger.warning(f"Error processing item {idx} in '{file.filename}': {e}")
                continue
    
    return all_documents


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
    
    modules_dict = config["database"]["documents"]
    modules_dict_lower = {k.lower(): v for k, v in modules_dict.items()}
    try:
        processed_files = {}
        word_files_to_convert = []
        markdown_files_to_process = []
        # Step 1: Save uploaded files
        print(f"Processing {len(files)} uploaded files...")
        for file in files:
            file_path = temp_upload_dir / file.filename
            content = await file.read()

            async with aiofiles.open(file_path, 'wb') as f:
                # You must await the write operation
                await f.write(content)
            
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
                    modified_filename = str(Path(original_filename).stem.lower().strip())
                    module = modules_dict_lower.get(modified_filename, "unknown")
                    # Extract video links from chunk content
                    video_links = extract_video_links(chunk_content)

                    metadata = {
                        "source": original_filename,
                        "chunk_index": idx,
                        "company_name": company_name,
                        "assistant_name": assistant_name,
                        "module": module,
                        "video_links": video_links
                    }
                    # Remove video link patterns from the chunk text
                    # cleaned_content = re.sub(r'videolink-\w+', '', chunk_content).strip() 
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


async def find_database_collection_with_postgres(database_id: str = None):
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
            raise ValueError(f"Collection '{collection_name}' not found in Qdrant")
        
        # Fetch company_name and assistant_name from PostgreSQL
        postgres = Postgres()
        database_info = await postgres.find_company_assistant_names(database_id)  # You'll need this method
        
        company_name = database_info.get("company_name")
        assistant_name = database_info.get("assistant_name")
        
        print(f"✅ Found collection: {collection_name}")
        print(f"   Company: {company_name}, Assistant: {assistant_name}")
        
        return collection_name, company_name, assistant_name
        
    except Exception as e:
        raise ValueError(f"ERROR finding database '{database_id}': {str(e)}")


def get_session_id(request: Request, content_request: BaseModel):
    """Extract session ID from headers or request body"""
    session_id = request.headers.get("Session-ID")
    if not session_id and hasattr(content_request, 'session_id'):
        session_id = content_request.session_id
    if not session_id:
        raise HTTPException(status_code=422, detail="No Session-ID")
    return session_id

async def get_user_code_tenant_name(session_id, postgres_obj: object):
    user_tenant = await postgres_obj.get_user_code_tenant_name(session_id)
    return user_tenant["user_code"], user_tenant["tenant_name"]
    
def validate_query(query):
    if not query.strip():
        raise HTTPException(status_code=422, detail="Query is empty")


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
    postgres = Postgres()
    sessions = await postgres.get_latest_sessions()
    return GetSessionsResponse(response=sessions)

@app.get(
    "/v1/databases", 
    response_model=GetDatabasesResponse,
    responses={
        200: {},
        500: {"description": "Unhandled error that should be reported"},
    },
)
async def get_latest_databases():
    postgres = Postgres()
    databases = await postgres.get_latest_databases()
    return GetDatabasesResponse(response=databases)

class FaqDocument(BaseModel):
    text: str
    module: str = ""

class FaqResponse(BaseModel):
    documents: List[FaqDocument] = []

@app.get("/v1/faq", response_model=FaqResponse)
async def get_faq(request: Request,
                  query: str = Query(..., alias="query"),
                  session_id: str = Query(..., alias="session_id"),
                  num_retrieve_context: int = Query(
                      config["retriever"]["retrieved_rank2_documents"],
                      alias="num_retrieve_context", ge=1, le=50)):
    try:
        postgres = Postgres()
        database_id = config["database"]["collection_name"]
        context_with_metadata, _ = await retrieve_context_with_metadata(
            query=query, database_index=database_id,
            num_retrieve_context=num_retrieve_context)
        documents = [
            FaqDocument(text=(c["text"] or "").strip(), module=c.get("module", ""))
            for c in reversed(context_with_metadata)
        ]
        return FaqResponse(documents=documents)
    except HTTPException as e:
        raise e
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=UNHANDLED_ERROR_MESSAGE)

# @app.get(
#     "/v1/faq",
#     response_model=FaqResponse,
#     responses={
#         200: {},
#         500: {"description": "Unhandled error that should be reported"},
#     },
# )
# async def get_faq(
#     request: Request,
#     query: str = Query(..., alias="query"),
#     session_id: str = Query(..., alias="session_id"),
# ):
#     # needs_clarification, _ = await is_somewhat_uniform(module_frequencies)
#     try:
#         postgres = Postgres()
#         database_id_dict = await postgres.find_database_id(session_id)
#         database_id = database_id_dict["database_id"]
#         # if not database_id:
#         #     database_id = config["database"]["collection_name"]
#         #     context_with_metadata, _ = await retrieve_context_with_metadata(query=query, database_index=database_id)
#         #     context = "\n\n ============= \n\n".join([context["text"] + "\n" + context["module"] for context in reversed(context_with_metadata)])

#         database_id = config["database"]["collection_name"]
#         context_with_metadata, _ = await retrieve_context_with_metadata(query=query, database_index=database_id)
#         context = "\n\n =================== \n\n".join([context["text"] for context in reversed(context_with_metadata)])

#         return FaqResponse(response=context.strip())
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=UNHANDLED_ERROR_MESSAGE)

@app.get(
    CHAT_ENDPOINT,
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
        # simple_logger("Received history request", session_id)
        history = await postgres.get_history(
            session_id, page_index, page_size, contain_paraphrase
        )
        return HistoryResponse(history=history)
    except HTTPException as e:
        raise e
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=UNHANDLED_ERROR_MESSAGE)

@app.post(
    "/v1/session/create",
    response_model=SessionResponse,
    responses={
        200: {},
        422: {"description": "Invalid database_id (not a UUID)"},
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
            business_object = None
        else:
            tenant_name = create_session_request.tenant_name
            user_code = create_session_request.user_code
            database_id = create_session_request.database_id
            business_object = create_session_request.objects

        # Collapse "use the default collection" inputs to NULL; reject bad UUIDs early.
        database_id = _normalize_session_database_id(database_id)

        session_id = await postgres.create_session(
            tenant_name=tenant_name,
            user_code=user_code,
            database_id=database_id,
            business_object=business_object,
        )
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
                "database_id": database_id,  # NULL means default collection
            },
            output_dict={"response": session_id.get("session_id")},
            elapsed_time=elapsed_time,
        )
        langfuse_context = get_client()
        langfuse_context.update_current_trace(
            input={"create_session_request": create_session_request},
            output={"session_id": session_id},
        )
        return session_id
    except HTTPException:
        raise
    except ConnectionError:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=UNHANDLED_ERROR_MESSAGE)

@app.post(
    CHAT_ENDPOINT,
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
async def chat_responder(chat_request: ChatRequest, request: Request):
    REQUEST_COUNT.labels(endpoint=CHAT_ENDPOINT).inc()
    start_time = time.time()
    is_sql = False
    context = ""
    agent = "chat_responder"
    message = "Chat response generated"
    choices = []
    do_suggest = False
    parameters = {}
    response_template = ""
    tenant_name = ""
    user_code = ""
    has_video_link = False  # <-- ADD THIS LINE
    is_ticket = False
    modules = []          # <-- ADD
    do_clarify = False    # <-- ADD
    is_first_message = False

    try:
        postgres = Postgres()
        session_id = get_session_id(request, chat_request)
        user_code, tenant_name = await get_user_code_tenant_name(session_id, postgres)
        if not chat_request.is_sync:
            message = "async chat response generated"
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
            has_video_link = final_records.get("has_video_link", False)
            is_ticket = all(k in (parameters or {}) for k in ("title", "description", "system", "form"))
        else:
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
            # simple_logger("Received chat request", session_id)
            history = await postgres.get_history(
                session_id,
                1,
                config["postgres"]["history_length"],
                True
            )
            if len(history) == 0: is_first_message = True
            
            if len(chat_request.query.split()) > 200:
                paraphrased_utterance, response, context = (
                    "No valid query",
                    RESPONSE_TEMPLATE_FOR_NO_ANSWER,
                    "",
                )
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
                matched_index, company_name, assistant_name = await find_database_collection_with_postgres(database_id_dict["database_id"])
                business_object_raw = await postgres.find_business_object(session_id)   # <-- NEW (None => default BO)
                selected_history = [
                    [h["query"], h["response"]] if len(h["query"]) < 60 
                    else [h["paraphrased_query"], h["response"]]
                    for h in history
                ]
                
                if chat_request.on_click:
                    selected_module = chat_request.query
                    do_suggest = False

                    # The user's real action this turn is "I selected module X".
                    # Store that as the query so history reflects the click, not the old question.
                    message_id = await postgres.insert_chat_row(
                        session_id=session_id,
                        user_query=selected_module,
                    )
                    previous_paraphrased = history[-1].get("paraphrased_query") \
                        or history[-1].get("query", "")

                    is_sql, paraphrased_utterance, response, context, do_clarify, modules, parameters, response_template, has_video_link, is_ticket = await chat_responder_(
                        history=selected_history,
                        user_utterance=selected_module,         # <-- the clicked module = actual user input
                        retrieval_query=previous_paraphrased,   # <-- NEW: used only for retrieval + answer
                        database_index=matched_index,
                        company_name=company_name,
                        assistant_name=assistant_name,
                        response_type=chat_request.response_type,
                        use_cache=chat_request.use_cache,
                        detected_module=selected_module,
                        sql_mode=chat_request.sql_mode,
                        use_video_link=chat_request.use_video_links,
                        ticket_mode=chat_request.ticket_mode,
                        on_click=True,
                        business_object=business_object_raw,
                    )
                    assert do_clarify == False, "on_click should not return do_clarify=True"
                    assert len(modules) <= 1, "on_click should not return modules"

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
                        json.dumps(parameters),
                        has_video_link
                    )

                else:
                    # Regular SQL agent processing
                    message_id = await postgres.insert_chat_row(
                        session_id=session_id,
                        user_query=chat_request.query,
                    )
                    is_sql, paraphrased_utterance, response, context, do_clarify, modules, parameters, response_template, has_video_link, is_ticket = await chat_responder_(
                        history=selected_history,
                        is_first_message=is_first_message,
                        user_utterance=chat_request.query,
                        database_index=matched_index,
                        company_name=company_name,
                        assistant_name=assistant_name,
                        response_type=chat_request.response_type,
                        use_cache=chat_request.use_cache,
                        detected_module="",
                        sql_mode=chat_request.sql_mode,
                        use_video_link=chat_request.use_video_links,
                        ticket_mode=chat_request.ticket_mode,
                        business_object=business_object_raw,
                    )
                    if do_clarify:
                        do_suggest = True
                        elapsed_time = time.time() - start_time
                        _ = await postgres.insert_message_choices(message_id, *modules)
                        modules_str = ",".join(modules) if modules else ""   # <-- add
                        await postgres.update_last_chat_row(
                            session_id=session_id,
                            paraphrased_query=paraphrased_utterance,
                            bot_response=response,
                            is_sql=is_sql,
                            elapsed_time=elapsed_time,
                            do_suggest=do_suggest,
                            selected_module=modules_str,
                            response_template=response_template,
                            parameters=json.dumps(parameters),
                            has_video_link=has_video_link,     # <-- NEW
                        )
                        agent = "module_clarification"
                        message = "modules proposed"
                        choices = modules
                    else:
                        elapsed_time = time.time() - start_time
                        modules_str = modules[0] if modules else "cache"
                        _ = await postgres.update_last_chat_row(
                            session_id,
                            paraphrased_utterance,
                            response,
                            is_sql,
                            elapsed_time,
                            do_suggest,
                            modules_str,
                            response_template,
                            json.dumps(parameters),
                            has_video_link,            # <-- NEW
                        )

        agent = "sql_responder" if is_sql else "chat_responder"
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
                "context_modules": modules,
                "do_clarify": do_clarify,
                "response_templated": response_template, 
                "parameters": parameters,
                "has_video_link": has_video_link
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
                "parameters": parameters,
                "has_video_link": has_video_link
            }
        )
        response = response.replace("→", "←")
        return ChatResponse(
            response=response,
            message_id=message_id,
            query=paraphrased_utterance,
            is_sql=is_sql,
            is_ticket=is_ticket,
            choices=choices,
            do_suggest=do_suggest,
            parameters=parameters,
            response_template=response_template,
            elapsed_time=elapsed_time,
            has_video_link=has_video_link,
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        traceback.print_exc()
        elapsed_time = time.time() - start_time
        REQUEST_LATENCY.labels(endpoint=CHAT_ENDPOINT).observe(elapsed_time)
        
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
                "parameters": parameters,
                "response_template": response_template, 
                "has_video_link": has_video_link
            },
            elapsed_time=elapsed_time,
        )
        raise HTTPException(status_code=500, detail="Unhandled error, Please report")
        
@app.post(
    "/v1/ticket",
    response_model=TicketResponse,
    responses={
        200: {},
        404: {"description": "Session or history not found"},
        422: {"description": "Missing session_id or empty history"},
        500: {"description": "Unhandled error"},
    },
)
@observe()
async def create_ticket(ticket_request: TicketRequest, request: Request):
    try:
        postgres = Postgres()
        session_id = get_session_id(request, ticket_request)

        # 1) Session must exist
        if not await postgres.exist_session(session_id):
            raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

        # 2) Pull recent history (newest first, includes paraphrased_query)
        history_records = await postgres.get_history(
            session_id,
            1,
            config["postgres"]["history_length"],
            True,
        )
        if not history_records:
            raise HTTPException(status_code=404, detail="No conversation history for this session")

        # 3) Latest paraphrased query (fallback to raw query if paraphrase is missing)
        latest = history_records[0]
        paraphrased_query = (latest.get("paraphrased_query") or latest.get("query") or "").strip()
        if not paraphrased_query:
            raise HTTPException(status_code=422, detail="No paraphrased query available for this session")

        # 4) Build history in the same (q, a) shape chat_responder uses
        selected_history = [
            [h["query"], h["response"]] if len(h["query"]) < 60
            else [h["paraphrased_query"], h["response"]]
            for h in history_records
        ]

        # 5) Resolve the session's Qdrant collection
        database_id_dict = await postgres.find_database_id(session_id)
        matched_index, _, _ = await find_database_collection_with_postgres(
            database_id_dict["database_id"]
        )

        # 6) Generate the ticket
        ticket = await ticket_responder_(
            history=selected_history,
            paraphrased_utterance=paraphrased_query,
            database_index=matched_index,
        )
        return TicketResponse(**ticket)

    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=UNHANDLED_ERROR_MESSAGE)

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


# ===== Main Endpoint Handler and helper functions =====
import uuid

def _normalize_session_database_id(database_id: Optional[str]) -> Optional[str]:
    """
    Normalize a user-supplied database_id for the sessions table.

    The sessions.database_id column is a UUID. The default collection lives
    only in config (no PostgreSQL row), so any input that *means* "use the
    default collection" must be stored as NULL — otherwise asyncpg raises a
    UUID validation error.

    - None / "" / "None" / "null" / the configured default collection name
        → None (session will be routed to the default collection at read time)
    - A valid UUID string → returned as-is
    - Anything else → 422 with a helpful message
    """
    if not database_id:
        return None

    default_name = config["database"]["collection_name"]
    if database_id in ("None", "null", default_name):
        return None

    try:
        uuid.UUID(database_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=422,
            detail=(
                f"database_id '{database_id}' is not a valid UUID. "
                "Either pass a UUID returned from /v1/chat/create/database, "
                "or omit the field to use the default collection."
            ),
        )
    return database_id

async def _resolve_database_id(
    default_collection: bool,
    postgres,
    company_name: str,
    assistant_name: str,
) -> str:
    """
    Resolve the database_id for a vector-database creation request.

    - default_collection=True : use the fixed name from config; NO PostgreSQL row,
      NO UUID. The default collection is purely a config-level concept.
    - default_collection=False: create a new PostgreSQL row and use its UUID as
      the Qdrant collection name.
    """
    if default_collection:
        database_id = config["database"]["collection_name"]
        logger.info(f"Using default collection name from config: {database_id}")
        return database_id

    try:
        database_id_dict = await postgres.create_database(company_name, assistant_name)
        database_id = database_id_dict["database_id"]
        logger.info(f"✅ Created PostgreSQL database entry: {database_id}")
        return database_id
    except Exception as e:
        logger.error(f"❌ Failed to create database entry in PostgreSQL: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create database entry: {str(e)}",
        )

WRITE_MODE_RECREATE = "recreate"
WRITE_MODE_APPEND = "append"
WRITE_MODE_UPDATE_FILES = "update_files"
VALID_WRITE_MODES = {WRITE_MODE_RECREATE, WRITE_MODE_APPEND, WRITE_MODE_UPDATE_FILES}


def _resolve_write_mode(write_mode: Optional[str], recreate: bool) -> str:
    """
    `write_mode` wins when supplied; otherwise fall back to the legacy
    `recreate` boolean so existing callers keep working:
        recreate=True  -> "recreate"
        recreate=False -> "append"
    """
    if write_mode:
        mode = write_mode.strip().lower()
        if mode not in VALID_WRITE_MODES:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Invalid write_mode '{write_mode}'. "
                    f"Choose one of: {sorted(VALID_WRITE_MODES)}."
                ),
            )
        return mode
    return WRITE_MODE_RECREATE if recreate else WRITE_MODE_APPEND

async def _rollback_database_id(
    default_collection: bool,
    postgres,
    database_id: str,
) -> None:
    """Undo the PostgreSQL row when Qdrant creation fails. No-op for default collection."""
    if default_collection:
        logger.info(
            f"Default collection '{database_id}' creation failed; "
            "nothing to roll back in PostgreSQL."
        )
        return

    try:
        await postgres.delete_database(database_id)
        logger.info(f"Rolled back PostgreSQL entry for database_id: {database_id}")
    except Exception as rollback_error:
        logger.error(f"Failed to rollback PostgreSQL entry: {rollback_error}")


async def create_database_endpoint(
    files: List[UploadFile],
    company_name: str,
    assistant_name: str,
    postgres,
    use_config: bool = True,
    recreate: bool = True,
    batch_size: int = 100,
    default_collection: bool = False,
    write_mode: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Write modes (via `write_mode`, falling back to legacy `recreate` when omitted):
      * "recreate"     - wipe the whole collection and rebuild it.
      * "append"       - add the new chunks, touch nothing else.
      * "update_files" - delete only the vectors whose metadata.source matches the
                         uploaded filenames, then insert the new chunks. Every
                         other file in the collection is preserved.

    Collection selection is unchanged:
      * default_collection=True  -> fixed config name (no UUID / no PG row).
      * default_collection=False -> a brand-new UUID collection; since it cannot
        pre-exist, the mode is forced to "recreate".
    """
    try:
        effective_mode = _resolve_write_mode(write_mode, recreate)

        # Step 1: process + chunk uploaded files
        logger.info("=" * 60)
        logger.info("STEP 1: Processing uploaded files")
        logger.info("=" * 60)
        processed_files = await process_uploaded_files(
            files=files,
            company_name=company_name,
            assistant_name=assistant_name,
        )

        all_documents = []
        for documents in processed_files.values():
            all_documents.extend(documents)

        logger.info(f"Total documents created: {len(all_documents)}")
        logger.info(f"Files processed: {list(processed_files.keys())}")
        if len(all_documents) == 0:
            raise HTTPException(
                status_code=422,
                detail="No documents were extracted from the uploaded files",
            )

        # Step 2: resolve database_id (default -> config, else -> new UUID)
        logger.info("STEP 2: Resolving database_id")
        database_id = await _resolve_database_id(
            default_collection=default_collection,
            postgres=postgres,
            company_name=company_name,
            assistant_name=assistant_name,
        )

        # Step 3: a fresh UUID collection can only be created from scratch
        if not default_collection and effective_mode != WRITE_MODE_RECREATE:
            logger.info(
                f"Forcing write_mode='recreate' for new UUID collection "
                f"(requested '{effective_mode}')."
            )
            effective_mode = WRITE_MODE_RECREATE

        # Step 4: write to Qdrant
        logger.info(f"STEP 4: Writing to Qdrant (mode={effective_mode})")
        vectors_deleted = None
        try:
            if effective_mode == WRITE_MODE_UPDATE_FILES:
                summary = upsert_documents_by_source(
                    database_id=database_id,
                    documents=all_documents,
                    qdrant_client=qdrant_client,
                    embedding_model=None,        # use config default
                    batch_size=batch_size,
                    create_if_missing=True,
                )
                vectors_deleted = summary["deleted"]
                collection_name = database_id
            else:
                recreate_flag = (effective_mode == WRITE_MODE_RECREATE)
                if use_config:
                    collection_name = create_vector_database_from_config(
                        database_id=database_id,
                        all_documents=all_documents,
                        recreate=recreate_flag,
                        batch_size=batch_size,
                    )
                else:
                    model_manager = ModelManager()
                    collection_name = create_vector_database(
                        database_id=database_id,
                        all_documents=all_documents,
                        qdrant_client=qdrant_client,
                        embedding_model=model_manager.embedding_model,
                        recreate=recreate_flag,
                        batch_size=batch_size,
                    )
        except Exception as e:
            logger.error(f"❌ Failed to write to Qdrant: {e}")
            await _rollback_database_id(default_collection, postgres, database_id)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create vector database: {str(e)}",
            )

        assert collection_name == database_id, "Collection name should match database_id"

        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info(f"Database ID:        {database_id}")
        logger.info(f"Write mode:         {effective_mode}")
        logger.info(f"Vectors deleted:    {vectors_deleted}")
        logger.info(f"Total documents:    {len(all_documents)}")
        logger.info("=" * 60)

        return {
            "database_id": database_id,
            "collection_name": collection_name,
            "message": f"Database written successfully (mode={effective_mode}).",
            "total_documents": len(all_documents),
            "files_processed": list(processed_files.keys()),
            "write_mode": effective_mode,
            "vectors_deleted": vectors_deleted,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error creating database: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create database: {str(e)}",
        )

async def create_nl2sql_database(
    files: List[UploadFile] = File(..., description="JSON files containing NL2SQL examples"),
    collection_name: str = Query(
        default=config["database"]["sql_collection_name"],
        description="Name for the Qdrant collection"
    ),
    recreate: bool = Query(
        default=True,
        description="Recreate collection if it already exists"
    ),
    batch_size: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Batch size for processing documents"
    )
) -> NL2SQLDatabaseResponse:
    """
    Create a Qdrant vector database from NL2SQL JSON files.
    
    Each JSON file should contain an array of objects with:
    - id: (excluded - may differ across files)
    - complexity: Query complexity level
    - module: Business module name (e.g., "دفتر کل")
    - table: Database table name(s)
    - question: Natural language question (embedded for similarity search)
    - sql: Object with "SQL" query string and "parameters" dict
    
    Example JSON structure:
    ```json
    [
      {
        "id": 1,
        "complexity": "simple",
        "module": "دفتر کل",
        "table": "financial_vouchers",
        "question": "تعداد کل اقلام سند حسابداری چقدر است؟",
        "sql": {
          "SQL": "SELECT COUNT(fv.id) AS fv_id_count FROM financial_vouchers AS fv",
          "parameters": {}
        }
      }
    ]
    ```
    """
    try:
        # Validate input
        if not files:
            raise HTTPException(status_code=422, detail="No files provided")
        
        # Process JSON files to Documents
        logger.info(f"Processing {len(files)} JSON files for NL2SQL database")
        documents = await process_nl2sql_json_files(files)
        
        if not documents:
            raise HTTPException(
                status_code=422,
                detail="No valid NL2SQL examples found in uploaded files"
            )
        
        logger.info(f"Creating NL2SQL database '{collection_name}' with {len(documents)} examples")
        
        # Create vector database using existing function
        result_collection = create_vector_database_from_config(
            database_id=collection_name,
            all_documents=documents,
            recreate=recreate,
            batch_size=batch_size,
            qdrant_client=qdrant_client,
            embedding_model=None  # Will use config default
        )
        
        # Get collection info
        info = get_collection_info(result_collection, qdrant_client)
        
        return NL2SQLDatabaseResponse(
            success=True,
            message=f"Successfully created NL2SQL database '{result_collection}'",
            collection_name=result_collection,
            documents_count=len(documents),
            total_documents=info.get("points_count") if info else len(documents)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating NL2SQL database: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create NL2SQL database: {str(e)}"
        )


async def add_nl2sql_documents(
    database_id: str,
    files: List[UploadFile] = File(..., description="Additional JSON files to add"),
    batch_size: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Batch size for processing"
    )
) -> NL2SQLDatabaseResponse:
    """
    Add more NL2SQL examples to an existing vector database.
    
    Args:
        database_id: The existing collection to add documents to
        files: JSON files containing additional NL2SQL examples
        batch_size: Number of documents to process in each batch
    """
    try:
        # Check if collection exists
        collections = list_vector_databases(qdrant_client)
        if database_id not in collections:
            raise HTTPException(
                status_code=404,
                detail=f"Database '{database_id}' not found"
            )
        
        # Process JSON files
        logger.info(f"Processing {len(files)} JSON files for database: {database_id}")
        documents = await process_nl2sql_json_files(files)
        
        if not documents:
            raise HTTPException(
                status_code=422,
                detail="No valid NL2SQL examples found in uploaded files"
            )
        
        logger.info(f"Adding {len(documents)} examples to database '{database_id}'")
        
        # Add documents to existing collection
        success = add_documents_to_existing_collection(
            database_id=database_id,
            documents=documents,
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
        
        return NL2SQLDatabaseResponse(
            success=True,
            message=f"Successfully added {len(documents)} examples to '{database_id}'",
            collection_name=database_id,
            documents_count=len(documents),
            total_documents=info.get("points_count") if info else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding NL2SQL documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add documents: {str(e)}"
        )

# ===== FastAPI Endpoints =====

@app.post("/v1/chat/create/database", response_model=CreateDatabaseResponse)
async def create_database(
    files: List[UploadFile] = File(...),
    company_name: str = Query(...),
    assistant_name: str = Query(...),
    write_mode: str = Query("update_files", description="recreate | append | update_files"),
    batch_size: int = Query(100, ge=1, le=1000),
    default_collection: bool = Query(True, description="Write to the shared default collection."),
):
    postgres = Postgres()
    return await create_database_endpoint(
        files=files, company_name=company_name, assistant_name=assistant_name,
        postgres=postgres, use_config=True, batch_size=batch_size,
        default_collection=default_collection, write_mode=write_mode,
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
            company_name="",  # Not needed for adding to existing DB
            assistant_name=""  # Not needed for adding to existing DB
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
    response_model=ModulesInfoResponse,
    responses={
        200: {"description": "Modules listed successfully"},
        404: {"description": "Database not found"},
        500: {"description": "Internal server error"},
    },
    summary="List modules in database with chunk counts",
    description="Get all unique module names in a database along with the number of chunks per module"
)
async def list_database_modules(database_id: str):
    """
    Get all unique module names (metadata.module) in a database, plus the
    number of chunks belonging to each module and the total chunk count.
    Useful for filtered retrieval and inspecting data distribution.
    """
    from src.retriever import Retriever

    try:
        # 1) Check if collection exists
        collection_names = list_vector_databases(qdrant_client)
        if database_id not in collection_names:
            raise HTTPException(
                status_code=404,
                detail=f"Database '{database_id}' not found"
            )

        # 2) Get the unique module names already known by the retriever
        retriever = Retriever()
        modules = retriever.get_available_modules(collection_name=database_id)

        # 3) Count chunks per module via Qdrant's payload-filtered count.
        #    This avoids streaming all payloads back to the app.
        module_counts: Dict[str, int] = {}
        for module in modules:
            try:
                count_result = qdrant_client.count(
                    collection_name=database_id,
                    count_filter=Filter(
                        must=[
                            FieldCondition(
                                key="metadata.module",
                                match=MatchValue(value=module),
                            )
                        ]
                    ),
                    exact=True,
                )
                module_counts[module] = count_result.count
            except Exception as e:
                # Don't fail the whole endpoint if one module count fails
                logger.warning(
                    f"Failed to count chunks for module '{module}' "
                    f"in '{database_id}': {e}"
                )
                module_counts[module] = 0

        total_chunks = sum(module_counts.values())

        return ModulesInfoResponse(
            database_id=database_id,
            modules=modules,
            count=len(modules),
            module_counts=module_counts,
            total_chunks=total_chunks,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing modules: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list modules: {str(e)}"
        )

@app.post(
    "/v1/chat/database/chunks",
    response_model=ModuleChunksResponse,
    responses={
        200: {"description": "Chunks retrieved successfully"},
        404: {"description": "Database not found"},
        422: {"description": "Invalid module name"},
        500: {"description": "Internal server error"},
    },
    summary="Get chunks for a module",
    description="Retrieve chunks belonging to a specific module within a database.",
)
async def get_module_chunks(
    module_request: ModuleChunksRequest,
    database_id: str = Query(..., description="Database (collection) identifier"),
    limit: int = Query(100, description="Maximum number of chunks to return", ge=1, le=10000),
):
    try:
        module_name = (module_request.module or "").strip()
        if not module_name:
            raise HTTPException(status_code=422, detail="Module name is empty")

        # Verify the collection exists
        collection_names = list_vector_databases(qdrant_client)
        if database_id not in collection_names:
            raise HTTPException(
                status_code=404,
                detail=f"Database '{database_id}' not found",
            )

        module_filter = Filter(
            must=[
                FieldCondition(
                    key="metadata.module",
                    match=MatchValue(value=module_name),
                )
            ]
        )

        chunks: List[ChunkInfo] = []
        next_offset = None
        remaining = limit

        # Page through Qdrant in case `limit` exceeds a single scroll batch.
        while remaining > 0:
            batch_size = min(remaining, 256)
            points, next_offset = qdrant_client.scroll(
                collection_name=database_id,
                scroll_filter=module_filter,
                limit=batch_size,
                offset=next_offset,
                with_payload=True,
                with_vectors=False,
            )

            for point in points:
                payload = point.payload or {}
                # LangChain's Qdrant integration stores docs as
                # {"page_content": ..., "metadata": {...}}
                chunks.append(
                    ChunkInfo(
                        text=payload.get("page_content", ""),
                        metadata=payload.get("metadata", {}) or {},
                    )
                )

            remaining -= len(points)
            if not points or next_offset is None:
                break

        return ModuleChunksResponse(
            database_id=database_id,
            module=module_name,
            count=len(chunks),
            chunks=chunks,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chunks for module '{module_request.module}': {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve chunks: {str(e)}",
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


@app.post(
    "/v1/nl2sql/database/create",
    response_model=NL2SQLDatabaseResponse,
    responses={
        200: {"description": "NL2SQL database created successfully"},
        422: {"description": "Invalid JSON or no valid examples found"},
        500: {"description": "Internal server error"},
    },
    summary="Create NL2SQL vector database",
    description="Upload JSON files containing NL2SQL examples and create a vector database for few-shot retrieval",
    tags=["NL2SQL"]
)
async def create_nl2sql_database_endpoint(
    files: List[UploadFile] = File(..., description="JSON files containing NL2SQL examples"),
    collection_name: str = Query(
        default=config["database"]["sql_collection_name"],
        description="Name for the Qdrant collection"
    ),
    recreate: bool = Query(default=True, description="Recreate collection if exists"),
    batch_size: int = Query(default=100, description="Batch size for processing", ge=1, le=1000)
):
    """
    Create a vector database from NL2SQL JSON files.
    
    JSON Structure:
    ```json
    [
      {
        "id": 1,
        "complexity": "simple",
        "module": "دفتر کل",
        "table": "financial_vouchers",
        "question": "سوال به بان طبیعی",
        "sql": {
          "SQL": "SELECT ...",
          "parameters": {"1": "value"}
        }
      }
    ]
    ```
    """
    return await create_nl2sql_database(
        files=files,
        collection_name=collection_name,
        recreate=recreate,
        batch_size=batch_size
    )

@app.post(
    "/v1/nl2sql/database/{database_id}/add",
    response_model=NL2SQLDatabaseResponse,
    responses={
        200: {"description": "Examples added successfully"},
        404: {"description": "Database not found"},
        422: {"description": "Invalid JSON or no valid examples"},
        500: {"description": "Internal server error"},
    },
    summary="Add NL2SQL examples to existing database",
    description="Upload additional JSON files to add more examples to an existing NL2SQL database",
    tags=["NL2SQL"]
)
async def add_nl2sql_documents_endpoint(
    database_id: str,
    files: List[UploadFile] = File(..., description="Additional JSON files"),
    batch_size: int = Query(default=100, description="Batch size", ge=1, le=1000)
):
    """Add more NL2SQL examples to an existing database."""
    return await add_nl2sql_documents(
        database_id=database_id,
        files=files,
        batch_size=batch_size
    )

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
    FEEDBACK_ENDPOINT,
    responses={
        200: {"content": {"application/json": {"example": {"message": "Feedback received"}}}},
        422: {"description": "Invalid feedback", "content": {"application/json": {"example": {"detail": "No Session-ID"}}}},
        404: {"description": "Message not found", "content": {"application/json": {"example": {"detail": "Message not found"}}}},
        500: {"description": "Unhandled error"},
    },
)
@observe()
async def feedback(feedback_request: FeedbackRequest, request: Request):
    endpoint = FEEDBACK_ENDPOINT
    REQUEST_COUNT.labels(endpoint=endpoint).inc()
    start_time = time.time()
    postgres = Postgres()
    try:

        session_id = get_session_id(request, feedback_request)
        if session_id is None:
            session_id = feedback_request.session_id


            if session_id is None:
                raise HTTPException(status_code=422, detail="No Session-ID")

        message_fields = await fetch_message_fields(
            session_id, feedback_request.message_id
        )

        # log_feedback_request(session_id)
        result = await process_feedback(feedback_request)
        user_code, tenant_name = await get_user_code_tenant_name(session_id, postgres)
        log_feedback_response(session_id, user_code, tenant_name, feedback_request, message_fields, start_time)
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        handle_unexpected_error(e, feedback_request.tenant_name, feedback_request.user_code, session_id, feedback_request, start_time)



def validate_feedback(feedback_request: FeedbackRequest):
    if feedback_request.feedback_type not in ["thumb_up", "thumb_down", "flag"]:
        raise HTTPException(status_code=422, detail="Invalid feedback")


async def fetch_message_fields(session_id, message_id):
    postgres = Postgres()
    message_fields = await postgres.get_message_fields(session_id, message_id)

    if not message_fields:
        raise HTTPException(status_code=404, detail="Message not found")

    return message_fields


async def process_feedback(feedback_request):
    message_id = feedback_request.message_id
    postgres = Postgres()
    result = await postgres.set_feedback(message_id, feedback_request.feedback_type)

    if result:
        return FeedbackResponse(message="feedback received")
    return FeedbackResponse(message="duplicate feedback")


def log_feedback_request(session_id):
    simple_logger("Received feedback request", session_id)


def log_feedback_response(session_id, tenant_name, user_code, feedback_request, message_fields, start_time):
    elapsed_time = time.time() - start_time
    REQUEST_LATENCY.labels(endpoint=FEEDBACK_ENDPOINT).observe(elapsed_time)

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
    REQUEST_LATENCY.labels(endpoint=FEEDBACK_ENDPOINT).observe(elapsed_time)

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
    raise HTTPException(status_code=500, detail=UNHANDLED_ERROR_MESSAGE)
