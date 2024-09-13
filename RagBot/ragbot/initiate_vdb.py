import os
import yaml

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import config
from make_sentence_chunks import chunk_document


embedding_model = HuggingFaceEmbeddings(
    model_name=config["embedding_model"]["model_name"],
    model_kwargs={"device": config["embedding_model"]["device"]},
)


def main(args):
    collection_path = args.persist_directory
    os.makedirs(collection_path, exist_ok=True)

    print(f"Creating a vector DB in {collection_path} ...")
    # document_loader = DirectoryLoader(
    #     path=config["database"]["documents_addr"],
    #     glob="**/*.txt",
    #     loader_cls=TextLoader,
    # )
    # documents = document_loader.load()
    # text_splitter = RecursiveCharacterTextSplitter(
    #     chunk_size=config["retriever"]["chunk_size"],
    #     chunk_overlap=config["retriever"]["chunk_overlap"],
    # )
    # chunks = text_splitter.split_documents(documents)
    chunks = chunk_document(config["database"]["documents"])
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
    parser = argparse.ArgumentParser(description='Let us build an app')
    parser.add_argument('-p', '--persist_directory', default=config["database"]["persist_directory"],
                    type=str, help='The path of the persist directory')
    args = parser.parse_args()
    main(args)
