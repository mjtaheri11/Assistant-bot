import docx
from docx.enum.style import WD_STYLE_TYPE
from typing import List, Dict
import re

from langchain.schema import Document

from config import config


def get_heading_level(paragraph):
    """Determine the heading level of a paragraph."""
    if paragraph.style.name.startswith('Heading'):
        return int(paragraph.style.name[-1])
    return 0

def split_into_sentences(text):
    """Split text into sentences."""
    return re.split(r'(?<=[.!?])\s+', text)

def process_single_document(doc_path: str, target_chunk_size: int=config["retriever"]["chunk_size"], max_chunk_size: int=config["retriever"]["max_chunk_size"]) -> List[Document]:
    """
    Process a single Word document and return chunks as Document objects.
    
    :param doc_path: Path to the Word document
    :param target_chunk_size: Target size of each chunk
    :param max_chunk_size: Maximum allowed size of a chunk
    :return: List of Document objects
    """
    doc = docx.Document(doc_path)
    chunks = []
    current_chunk = {
        'h1': '',
        'h2': '',
        'h3': '',
        'content': []
    }
    
    for paragraph in doc.paragraphs:
        heading_level = get_heading_level(paragraph)
        if heading_level == 1:
            if current_chunk['content']:
                chunks.extend(finalize_chunk(current_chunk, target_chunk_size, max_chunk_size, doc_path))
            current_chunk = {'h1': paragraph.text, 'h2': '', 'h3': '', 'content': []}
        elif heading_level == 2:
            if current_chunk['content']:
                chunks.extend(finalize_chunk(current_chunk, target_chunk_size, max_chunk_size, doc_path))
            current_chunk['h2'] = paragraph.text
            current_chunk['h3'] = ''
            current_chunk['content'] = []
        elif heading_level == 3:
            if current_chunk['content']:
                chunks.extend(finalize_chunk(current_chunk, target_chunk_size, max_chunk_size, doc_path))
            current_chunk['h3'] = paragraph.text
            current_chunk['content'] = []
        else:
            current_chunk['content'].append(paragraph.text)
    
    # Add any remaining content
    if current_chunk['content']:
        chunks.extend(finalize_chunk(current_chunk, target_chunk_size, max_chunk_size, doc_path))
    
    return chunks

def chunk_document(doc_paths: List[str], target_chunk_size: int = 1000, max_chunk_size: int = 1500) -> List[Document]:
    """
    Process multiple Word documents and return chunks as Document objects.
    
    :param doc_paths: List of paths to Word documents
    :param target_chunk_size: Target size of each chunk
    :param max_chunk_size: Maximum allowed size of a chunk
    :return: List of Document objects
    """
    all_chunks = []
    
    for doc_path in doc_paths:
        try:
            chunks = process_single_document(doc_path, target_chunk_size, max_chunk_size)
            all_chunks.extend(chunks)
            print(f"Successfully processed: {doc_path}")
        except Exception as e:
            print(f"Error processing {doc_path}: {str(e)}")
    
    return all_chunks

def finalize_chunk(chunk, target_chunk_size, max_chunk_size, source_file):
    """
    Finalize a chunk, splitting it if necessary based on sentences and paragraphs, with 2-sentence overlap.
    
    :param chunk: Dictionary containing heading and content information
    :param target_chunk_size: Target size of each chunk
    :param max_chunk_size: Maximum allowed size of a chunk
    :param source_file: Path of the source document
    :return: List of Document objects
    """
    finalized_chunks = []
    headers = ""
    if chunk['h1'].strip() != "":
        headers += chunk['h1'] + '\n'

    if chunk['h2'].strip() != "":
        headers += chunk['h2'] + '\n'

    if chunk['h3'].strip() != "":
        headers += chunk['h3'] + '\n'
    
    all_sentences = []
    for paragraph in chunk['content']:
        all_sentences.extend(split_into_sentences(paragraph))
    
    current_chunk_sentences = []
    current_size = 0
    
    for i, sentence in enumerate(all_sentences):
        sentence_size = len(sentence)
        
        if current_size + sentence_size > max_chunk_size and current_chunk_sentences:
            # Finalize the current chunk
            chunk_text = headers + ' '.join(current_chunk_sentences)
            finalized_chunks.append(Document(page_content=chunk_text, metadata={"source": source_file}))
            
            # Start new chunk with 2-sentence overlap
            overlap_sentences = current_chunk_sentences[-config["retriever"]["sentence_overlap"]:] if len(current_chunk_sentences) >= config["retriever"]["sentence_overlap"] else current_chunk_sentences[-1:]
            current_chunk_sentences = overlap_sentences + [sentence]
            current_size = sum(len(s) for s in current_chunk_sentences)
            
        else:
            current_chunk_sentences.append(sentence)
            current_size += sentence_size
        
        # Check if we've reached the target chunk size
        if current_size >= target_chunk_size and i < len(all_sentences) - 1:
            chunk_text = headers + ' '.join(current_chunk_sentences)
            finalized_chunks.append(Document(page_content=chunk_text, metadata={"source": source_file}))
            
            # Start new chunk with 2-sentence overlap
            overlap_sentences = current_chunk_sentences[-config["retriever"]["sentence_overlap"]:] if len(current_chunk_sentences) >= config["retriever"]["sentence_overlap"] else current_chunk_sentences[-1:]
            current_chunk_sentences = overlap_sentences
            current_size = sum(len(s) for s in current_chunk_sentences)
    
    # Add any remaining content
    if current_chunk_sentences:
        chunk_text = headers + ' '.join(current_chunk_sentences)
        finalized_chunks.append(Document(page_content=chunk_text, metadata={"source": source_file}))
    
    return finalized_chunks

# # Example usage
# doc_path = 'path/to/your/document.docx'
# chunks = chunk_document(doc_path)

# # Print chunks (for demonstration)
# for i, chunk in enumerate(chunks):
#     print(f"Chunk {i + 1}:")
#     print(chunk)
#     print("-" * 50)

# Here you would typically add code to insert these chunks into your Chroma vector database