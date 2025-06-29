import os
import uuid

import numpy as np
import yaml
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import config
from .make_sentence_chunks import chunk_document

embedding_model = HuggingFaceEmbeddings(
    model_name=config["embedding_model"]["model_name"],
    model_kwargs={"device": config["embedding_model"]["device"], "trust_remote_code": config["embedding_model"]["trust_remote_code"]},
)


def create_vector_database(
    settings: dict,
    database_id: str,
    collection_path: str = "../RaaS_vectorDB",
    ):
    os.makedirs(collection_path, exist_ok=True)
    company_name = settings.pop("company_name")
    assistant_name = settings.pop("assistant_name")
    database_path = os.path.join(
        collection_path,
        database_id
        + "."
        + company_name
        + "."
        + assistant_name,
    )

    os.makedirs(database_path)
    chunks = chunk_document(settings)
    
    vdb = Chroma(persist_directory=database_path, embedding_function=embedding_model)

    if len(vdb.get()["ids"]) > 0:
        print(
            f'VectorDB has {len(vdb.get()["ids"])} documents already, deleting them ...'
        )
        vdb._collection.delete(vdb.get()["ids"])

    vdb.add_documents(chunks)

import pandas as pd
import os
from langchain_core.documents import Document

def create_documents_from_csvs(directory_path="../knowledge_base/qa-questions"):
    """
    Reads all CSV files from a directory and converts each question-answer
    pair into a LangChain Document object with metadata.

    Args:
        directory_path (str): The path to the directory with the CSV files.

    Returns:
        list[Document]: A list of LangChain Document objects ready for a
                        vector store. Each document's metadata contains the
                        source filename.
    """
    all_docs = []
    
    # Check if the directory exists
    if not os.path.isdir(directory_path):
        print(f"❌ Error: Directory not found at '{directory_path}'")
        return all_docs

    # Loop through each file in the specified directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory_path, filename)
            
            try:
                df = pd.read_csv(file_path)

                if 'Question' in df.columns and 'Answer' in df.columns:
                    for index, row in df.iterrows():
                        # The text content for the vector store
                        page_content = f"{{'QUESTION': {row['Question']}, 'Answer':  {row['Answer']}}}"
                        
                        # The metadata, including the source filename
                        metadata = {"source": filename}
                        
                        # Create the Document object
                        doc = Document(page_content=page_content, metadata=metadata)
                        
                        all_docs.append(doc)
                else:
                    print(f"⚠️ Warning: Skipping '{filename}' because it lacks 'Question' or 'Answer' columns.")

            except Exception as e:
                print(f"❌ Error processing file '{filename}': {e}")
                
    return all_docs

# --- --- --- Usage Example --- --- ---

# # 1. Define the path to your knowledge base directory
# faq_directory = "./knowledge_base/faq_questions"

# # 2. Call the new function to get the list of Document objects
# documents = create_documents_from_csvs(faq_directory)

# # 3. (Optional) Inspect the first Document object to verify its structure
# if documents:
#     print(f"✅ Successfully created {len(documents)} Document objects.")
#     print("\n--- Structure of the First Document ---")
#     print(documents[0])


def main(args):
    collection_path = args.persist_directory
    os.makedirs(collection_path, exist_ok=True)

    print(f"Creating a vector DB in {collection_path} ...")
    chunks = create_documents_from_csvs() # (config["database"]["documents"])
    print(f"Generated {len(chunks)} chunks")

    vdb = Chroma(persist_directory=collection_path, embedding_function=embedding_model)

    if len(vdb.get()["ids"]) > 0:
        print(
            f'VectorDB has {len(vdb.get()["ids"])} documents already, deleting them ...'
        )
        vdb._collection.delete(vdb.get()["ids"])

    vdb.add_documents(chunks)
    print(f"{len(chunks)} documents have been added to the vector DB")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Let us build an app")
    parser.add_argument(
        "-p",
        "--persist_directory",
        default=config["database"]["persist_directory"],
        type=str,
        help="The path of the persist directory",
    )
    args = parser.parse_args()
    main(args)
