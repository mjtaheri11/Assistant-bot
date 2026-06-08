from src.initiate_vdb import (
    create_vector_database,
    create_vector_database_from_config,
    delete_vector_database,
    list_vector_databases,
    get_collection_info,
    add_documents_to_existing_collection,
    upsert_documents_by_source
)

__all__ = [
    'create_vector_database',
    'create_vector_database_from_config',
    'delete_vector_database',
    'list_vector_databases',
    'get_collection_info',
    'add_documents_to_existing_collection',
    'upsert_documents_by_source'
]

# create database via API
# curl -X POST "http://localhost:8000/v1/chat/create/database?company_name=Acme&assistant_name=sales-bot" \
#   -F "files=@document1.pdf" \
#   -F "files=@document2.docx" \
#   -F "files=@document3.txt"

# =============================
# ADD DATABASE VIA API
# curl -X POST "http://localhost:8000/v1/chat/database/db-12345/add-documents" \
#   -F "files=@new-document1.pdf" \
#   -F "files=@new-document2.docx"

# =============================
# LIST All databases
# curl -X GET "http://localhost:8000/v1/chat/list/collections"

# =============================
# get database info
# curl -X GET "http://localhost:8000/v1/chat/database/db-12345/info"

# =============================
# Delete only Qdrant collection
# curl -X DELETE "http://localhost:8000/v1/chat/delete/database/db-12345"

# Delete both Qdrant collection and PostgreSQL entry
# curl -X DELETE "http://localhost:8000/v1/chat/delete/database/db-12345?delete_postgres=true"

# =============================
# curl -X GET "http://localhost:8000/v1/chat/health"
