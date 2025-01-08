import math
import re
# from markitdown import MarkItDown
from typing import Dict, List, Optional, Tuple

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from langchain_text_splitters import (MarkdownHeaderTextSplitter,
                                      RecursiveCharacterTextSplitter)

from .config import config


def is_excluded_format(text: str) -> bool:
    """Check if the text matches any excluded patterns."""
    # Regular expression patterns for different heading number formats
    # Patterns to exclude (bullet points and simple list markers)
    exclude_patterns = [
        r'^\•\s',        # Bullet point
        r'^\-\s',        # Hyphen bullet
        r'^\*\s',        # Asterisk bullet
        r'^\○\s',        # Circle bullet
        r'^\◆\s',        # Diamond bullet
        r'^[a-z]\.\s',   # a. b. c. format
        r'^[A-Z]\.\s',   # A. B. C. format
        r'^\(\d+\)\s',   # (1) (2) format
        r'^\([a-z]\)\s', # (a) (b) format
        r'^\([A-Z]\)\s'  # (A) (B) format
    ]
    return any(re.match(pattern, text) for pattern in exclude_patterns)


def get_heading_level_from_paragraph_style(style_name: str) -> Optional[int]:
    """Determine heading level from paragraph style name."""
    if not style_name:
        return ""
        
    style_lower = style_name.lower()
    
    # Direct heading style matching
    if 'heading' in style_lower:
        try:
            level = int(style_lower.replace('heading', '').strip())
            if 1 <= level <= 9:  # Valid heading levels in Word
                return level
        except ValueError:
            raise("error happend finding header")
    return ""

def get_heading_level_from_text(doc: Document, index: int) -> Optional[int]:
    """
    Determine heading level from paragraph numbering pattern,
    considering the context and style.
    """
    def is_likely_heading(doc, paragraph):
        text = paragraph.text.strip()
        
        if not text:
            return 0
        
        score = 0
        
        if paragraph.style.name == 'List Paragraph':
            score += 2

        # Exclude known non-heading styles
        if any(term in style_lower for term in ['bullet', 'normal', 'body']):
            score -= 1
        
        if len(text) < 60:
            score += 1
            
        if text.istitle():
            score += 2

        # Check for formatting
        if any(run.bold or run.italic for run in paragraph.runs):
            score += 1
                
        return score

    heading_patterns = {
            1: r'^\d+\.?\s',           # 1. or 1
            2: r'^\d+\.\d+\.?\s',      # 1.1. or 1.1
            3: r'^\d+\.\d+\.\d+\.?\s', # 1.1.1. or 1.1.1
            4: r'^\d+\.\d+\.\d+\.\d+\.?\s',  # 1.1.1.1. or 1.1.1.1
        }
    
    paragraph_text = doc.paragraphs[index].text
    if is_excluded_format(paragraph_text):
        return ""
        
    # Check if the style suggests this is not a heading
    style_lower = doc.paragraphs[index].style.name.lower()
    # if any(term in style_lower for term in ['bullet', 'list paragraph']):
    #     return None
    
    # Match against heading patterns
    for level, pattern in heading_patterns.items():
        if re.match(pattern, paragraph_text):
            # Additional validation for numbered headings
            # Check if the content after the number suggests this is a heading
            # (e.g., longer than just a list item, contains significant text)
            content_after_number = re.sub(pattern, '', paragraph_text).strip()
            if len(content_after_number) > 3 and not content_after_number.endswith(':'):
                return level

    score = is_likely_heading(doc, doc.paragraphs[index])
    if score >= 4:  # Minimum confidence threshold
        # Additional context validation
        prev_style = doc.paragraphs[max(0, index - 1)].style.name
        next_style = doc.paragraphs[min(len(doc.paragraphs)-1, index + 1)].style.name
        
        # If surrounded by normal paragraphs or other headings, more likely to be a heading
        if (('normal' in prev_style.lower() or 'heading' in prev_style.lower()) and
            ('normal' in next_style.lower() or 'heading' in next_style.lower())):
            
            for level, pattern in heading_patterns.items():
                if re.match(pattern, paragraph_text):
                    return level
            return "" # if score is compatible with a potential heading but level cannot directly be extracted from the paragraph
    return ""

# specially for other documents 
def get_paragraph_number(paragraph):
    """
    Attempt to extract the numbering information from a paragraph.
    Returns dictionary of {number_text_level, correspondig_id, success_flag}
    """
    # Try to get the numbering element
    p = paragraph._p  # Access the underlying XML
    numPr = p.xpath('.//w:numPr')
    
    if numPr:
        try:
            # Get the numbering properties
            ilvl = numPr[0].xpath('.//w:ilvl')[0].get(qn('w:val'))  # Numbering level
            numId = numPr[0].xpath('.//w:numId')[0].get(qn('w:val'))  # Numbering ID
            
            # Unfortunately, there's no direct way to get the rendered number
            # through python-docx as it's calculated by Word during rendering
            return {"level": int(ilvl) + 1, "NumId": int(numId.replace("NumId", "")), "success_flag": True}
        except (IndexError, AttributeError):
            return {"level": "", "NumId": "", "success_flag":False}
    return {"level": "", "NumId": "", "success_flag": False}


def extract_potential_list_paragraph_headings(paragraph):
    """
    Extract potential headings from a DOCX file where headings are styled as 'List Paragraph'.
    
    Args:
        doc (obj): docx paragraph object
        
    Returns:
        list: List of tuples containing (paragraph info, numbering info, confidence score)
    """
    level = ""
    if paragraph.style.name == "List Paragraph":
        paragraph_info = get_paragraph_number(paragraph)
        if paragraph_info["success_flag"]:
            if int(paragraph_info["NumId"]) <= 4:
                if paragraph_info["NumId"] == 1 or len(paragraph.text) > 50: # for prevent bullet points 
                    return ""
                level = paragraph_info["level"]
                return level
    return level
    
        
# for heading based documents
def extract_heading_level(document: Document, index: int) -> int:
    """
    Extract headings from a DOCX file considering both styles and numbering patterns,
    while excluding bullet points and regular list items.
    
    Args:
        file_path (str): Path to the DOCX file
        
    Returns:
        List[Tuple[str, int, str]]: List of tuples containing (heading_text, level, style_name)
    """
    
    # First check style-based headings (more reliable)
    style_level = get_heading_level_from_paragraph_style(document.paragraphs[index].style.name)
    if style_level:
        return style_level
    
    # then check the xml numbering output
    number_level = extract_potential_list_paragraph_headings(document.paragraphs[index])
    if number_level:
        return number_level
    
    # Then check numbering-based headings from text with additional validation
    numbering_level_from_text = get_heading_level_from_text(document, index)
    if numbering_level_from_text:
        return numbering_level_from_text

    return 0


# def extract_content_from_making_markdown(path):
#     md = MarkItDown()
#     result = md.convert(path)
    
#     headers_to_split_on = [
#         ("#", "Header 1"),
#         ("##", "Header 2"),
#         ("###", "Header 3"),
#         ("####", "Header 4"),
#     ]
    
#     markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

#     # Split the document into chunks

#     md_header_splits = markdown_splitter.split_text(result.text_content)
#     return md_header_splits


def perform(file_path): 
    doc = Document(file_path)
    headings = []
    for index in range(len(doc.paragraphs)):
        text = doc.paragraphs[index].text.strip()
        if not text:
            continue
        heading_level = extract_heading_level(doc, index)
        if heading_level != 0:
            indent = "  " * heading_level
            print(indent , doc.paragraphs[index].text, f"heading {heading_level}")
        

def format_heading_output(headings: List[Tuple[str, int, str]]) -> str:
    """
    Format the extracted headings into a readable structure.
    
    Args:
        headings (List[Tuple[str, int, str]]): List of heading tuples
        
    Returns:
        str: Formatted string representation of the heading structure
    """
    output = []
    for text, level, style in headings:
        indent = "  " * (level - 1)
        output.append(f"{indent}{text} [{style}]")
    return "\n".join(output)


def process_single_document(
    doc_path: str,
    target_chunk_size: int = config["retriever"]["chunk_size"],
    max_chunk_size: int = config["retriever"]["max_chunk_size"],
) -> List[Document]:
    """
    Process a single Word document and return chunks as Document objects.
    
    :param doc_path: Path to the Word document
    :param target_chunk_size: Target size of each chunk
    :param max_chunk_size: Maximum allowed size of a chunk
    :return: List of Document objects
    """
    chunks = []
    current_chunk = {"h1": "", "h2": "", "h3": "", "h4": "", "content": []}
    
    doc = Document(doc_path)
    current_heading_level = float("inf") # Initialize current heading level

    for index in range(len(doc.paragraphs)):
        text = doc.paragraphs[index].text.strip()
        if not text:
            continue
        
        heading_level = extract_heading_level(doc, index)

        # Handle chunk finalization        
        if (current_heading_level == 0) and (heading_level > current_heading_level):
            chunks.extend(
                finalize_chunk(
                    current_chunk, target_chunk_size, max_chunk_size, doc_path
                )
            )
        
        if heading_level == 1:
            current_chunk["h1"] = doc.paragraphs[index].text
            current_chunk["h2"] = ""
            current_chunk["h3"] = "" 
            current_chunk["h4"] = "" 
            current_chunk["content"] = []
                                
        elif heading_level == 2:
            current_chunk["h2"] = doc.paragraphs[index].text 
            current_chunk["h3"] = "" 
            current_chunk["h4"] = "" 
            current_chunk["content"] = []
                    
        elif heading_level == 3:
            current_chunk["h3"] = doc.paragraphs[index].text 
            current_chunk["h4"] = "" 
            current_chunk["content"] = []
            
        elif heading_level == 4:
            current_chunk["h4"] = doc.paragraphs[index].text
            current_chunk["content"] = []
            
        else:
            current_chunk["content"].append(doc.paragraphs[index].text)
                
        current_heading_level = heading_level
    
    chunks.extend(finalize_chunk(
        current_chunk, target_chunk_size, max_chunk_size, doc_path
        )
                  )
    return chunks


def finalize_chunk(chunk, target_chunk_size, max_chunk_size, source_file):
    """
    Finalize a chunk, splitting it if necessary based on sentences and paragraphs, with 2-sentence overlap.

    :param chunk: Dictionary containing heading and content information
    :param target_chunk_size: Target size of each chunk
    :param max_chunk_size: Maximum allowed size of a chunk
    :param source_file: Path of the source document
    :return: List of Document objects
    """
    chunk_overlap = 50 # TODO: change it as soon as possible
    finalized_chunks = []
    headers = ""
    if chunk["h1"].strip() != "":
        headers += chunk["h1"] + "\n"

    if chunk["h2"].strip() != "":
        headers += chunk["h2"] + "\n"

    if chunk["h3"].strip() != "":
        headers += chunk["h3"] + "\n"

    if chunk["h4"].strip() != "":
        headers += chunk["h4"] + "\n"

    # make paragraph from the content
    paragraph = "\n".join(chunk["content"])
    paragraph_length = len(paragraph)
    
    #  having normalized chunks based on the length of sentences
    chunk_size_residue = paragraph_length // max_chunk_size + 1 # normalize chunk size based on the length of the content 
    chunk_size = math.ceil(paragraph_length / chunk_size_residue)
    if chunk_size < chunk_overlap:
        chunk_size = target_chunk_size
    
    text_splitter = RecursiveCharacterTextSplitter(
        # Set a really small chunk size, just to show.
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=r'^(\d+(\.\d+)*)\s+(.*)',
    )
    documents = text_splitter.create_documents([paragraph])
    for i in range(len(documents)):
        documents[i].page_content = headers + documents[i].page_content
        documents[i].metadata ={"source": source_file}    
    return documents


def chunk_document(doc_settings: Dict[str, Dict[str, int]]) -> List["Document"]:
    """
    Process multiple Word documents. 
    Uses parallel processing (ProcessPoolExecutor) to speed up large-scale runs.
    """
    all_chunks = []

    # --- NEW: Parallelize the per-document process using concurrent.futures ---
    import concurrent.futures

    # A ProcessPoolExecutor sidesteps the GIL for CPU-bound tasks, which can help 
    # since python-docx parsing and chunking can be CPU-intensive on large docs.
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Collect futures for each document
        future_to_doc = {}
        for doc_path, settings in doc_settings.items():
            print(f"Submitting {doc_path} for processing...")
            future = executor.submit(
                process_single_document,
                doc_path,
                settings["target_chunk_size"],
                settings["max_chunk_size"]
            )
            future_to_doc[future] = doc_path

        # As futures complete, retrieve their results
        for future in concurrent.futures.as_completed(future_to_doc):
            doc_path = future_to_doc[future]
            try:
                result = future.result()
            except Exception as e:
                print(f"Exception occurred while processing {doc_path}: {e}")
            else:
                all_chunks.extend(result)
                print(f"Successfully processed: {doc_path}")

    return all_chunks


# def finalize_chunk(chunk, target_chunk_size, max_chunk_size, source_file):
#     """
#     Finalize a chunk, splitting it if necessary based on sentences and paragraphs, with 2-sentence overlap.

#     :param chunk: Dictionary containing heading and content information
#     :param target_chunk_size: Target size of each chunk
#     :param max_chunk_size: Maximum allowed size of a chunk
#     :param source_file: Path of the source document
#     :return: List of Document objects
#     """
#     finalized_chunks = []
#     headers = ""
#     if chunk["h1"].strip() != "":
#         headers += chunk["h1"] + "\n"

#     if chunk["h2"].strip() != "":
#         headers += chunk["h2"] + "\n"

#     if chunk["h3"].strip() != "":
#         headers += chunk["h3"] + "\n"

#     if chunk["h4"].strip() != "":
#         headers += chunk["h4"] + "\n"

#     all_sentences = []
#     for paragraph in chunk["content"]:
#         if paragraph.strip() == "":
#             continue
#         sentences = split_into_sentences(paragraph)
#         # to preserve the paragraphs in each chunk
#         if not sentences[-1].endswith("\n"):
#             sentences[-1] += "\n"
#         all_sentences.extend(sentences)

#     current_chunk_sentences = []
#     current_size = 0

#     for i, sentence in enumerate(all_sentences):
#         sentence_size = len(sentence)

#         if current_size + sentence_size > max_chunk_size and current_chunk_sentences:
#             # Finalize the current chunk
#             chunk_text = headers + " ".join(current_chunk_sentences)
#             finalized_chunks.append(
#                 Document(page_content=chunk_text, metadata={"source": source_file})
#             )

#             # Start new chunk with r-sentence overlap
#             overlap_sentences = (
#                 current_chunk_sentences[-config["retriever"]["sentence_overlap"] :]
#                 if len(current_chunk_sentences)
#                 >= config["retriever"]["sentence_overlap"]
#                 else current_chunk_sentences[-1:]
#             )
#             current_chunk_sentences = overlap_sentences + [sentence]
#             current_size = sum(len(s) for s in current_chunk_sentences)

#         # Check if we've reached the target chunk size
#         elif current_size >= target_chunk_size and i < len(all_sentences) - 1:
#             chunk_text = headers + " ".join(current_chunk_sentences)
#             finalized_chunks.append(
#                 Document(page_content=chunk_text, metadata={"source": source_file})
#             )

#             # Start new chunk with r-sentence overlap
#             overlap_sentences = (
#                 current_chunk_sentences[-config["retriever"]["sentence_overlap"] :]
#                 if len(current_chunk_sentences)
#                 >= config["retriever"]["sentence_overlap"]
#                 else current_chunk_sentences[-1:]
#             )
#             current_chunk_sentences = overlap_sentences + [sentence]
#             current_size = sum(len(s) for s in current_chunk_sentences)

#         else:
#             current_chunk_sentences.append(sentence)
#             current_size += sentence_size

#     # Add any remaining content
#     if current_chunk_sentences:
#         chunk_text = headers + " ".join(current_chunk_sentences)
#         finalized_chunks.append(
#             Document(page_content=chunk_text, metadata={"source": source_file})
#         )

#     return finalized_chunks


# if __name__ == "__main__":
#     chunks = chunk_document(
#         {
#             "/home/user01/mj-workspace/Assistant-bot/knowledge_base/new-KB/ReportBuilder_Help_14030925.docx": {
#                 "target_chunk_size": 800,
#                 "max_chunk_size": 1200,
#                 "sentence_overlap": 1,
#             }
#         }
#     )



# Example usage
# if __name__ == "__main__":
#     # Replace with your document path
#     docx_path = "/home/user01/mj-workspace/Assistant-bot/knowledge_base/new-KB/Usermanual-v3.docx"
#     try:
#         headings = extract_potential_headings(docx_path)
#         print_results(headings)
#     except Exception as e:
#         print(f"Error processing document: {str(e)}")
        
