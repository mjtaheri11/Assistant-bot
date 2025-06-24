import pandas as pd
import os
from collections import defaultdict
import chromadb
from chromadb.types import Collection


def retrieve_chunks_and_save_to_csv(collection: Collection, output_directory: str):
    """
    Retrieves all text chunks from a ChromaDB collection, parses them,
    and saves them to the corresponding CSV files based on metadata.

    Args:
        collection (chromadb.types.Collection): The ChromaDB collection object.
        output_directory (str): The directory where the CSV files will be saved.
    """
    # 1. Fetch all items from the collection
    retrieved_results = collection.get()

    import pdb
    pdb.set_trace()
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # 2. Group data by source filename
    grouped_data = defaultdict(list)

    for i in range(len(retrieved_results['ids'])):
        doc = retrieved_results['documents'][i]
        metadata = retrieved_results['metadatas'][i]
        source_file = metadata.get("source", "unknown_source.csv")

        # 3. Parse the "Question" and "Answer" from the page_content
        try:
            # Split the document content to separate Question and Answer
            parts = doc.split('\nAnswer: ')
            question = parts[0].replace('Question: ', '').strip()
            answer = parts[1].strip() if len(parts) > 1 else ""
            
            grouped_data[source_file].append({"Question": question, "Answer": answer})

        except IndexError:
            print(f"⚠️ Warning: Could not parse document with ID {retrieved_results['ids'][i]}. Content: '{doc}'")


    # 4. Write the grouped data into respective CSV files
    for filename, data in grouped_data.items():
        output_path = os.path.join(output_directory, filename)
        
        try:
            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False)
            print(f"✅ Successfully saved {len(data)} rows to '{output_path}'")
        except Exception as e:
            print(f"❌ Error saving file '{output_path}': {e}")


if __name__ == "__main__":
    retrieve_chunks_and_save_to_csv("/home/user01/mj-workspace/Assistant-bot/VectorDB")