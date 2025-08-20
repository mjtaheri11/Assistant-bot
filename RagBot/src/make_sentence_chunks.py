import concurrent.futures
import math
import os
import re
import subprocess
import tempfile
from io import BytesIO
# from markitdown import MarkItDown
from typing import Dict, List, Optional, Tuple

from docx import Document
from docx.document import Document as DocxDocument
from docx.oxml import CT_P, CT_Tbl, OxmlElement
from docx.oxml.ns import qn
from langchain_text_splitters import (MarkdownHeaderTextSplitter,
                                      RecursiveCharacterTextSplitter)
from langchain_core.documents import Document as DocLangChain
from markitdown import MarkItDown

from .config import config
from .chunker_algorithm import SoleChunker

DICT_OF_TITLES = {"راهنمای سیستم CRM": "مدیریت ارتباط با مشتری",
                  "راهنمای کاربری دفتر کل نسل 4": "دفتر کل",
                  "راهنمای کاربری ماژول خزانه داری نسل 4": "خزانه داری",
                  "راهنمای فروش": "فروش",
                  "راهنمای آموزش ابزار گزارش ساز در نسل 4": "گزارش ساز",
                  "راهنمای انبار و حسابداری انبار نسل 4": "انبار",
                  "معرفی سیستم یکپارچه نسل 4": "مقدمه",
                  "راهنمای استفاده از دستیار دیجیتال": "راهنما",
                  "راهنمای امکانات عمومی سیستم": "پلتفرم",
                  "سامانه مودیان مالیاتی": "مودیان"}


def convert_doc_bytes_to_docx(doc_bytes: bytes) -> bytes:
    """Converts .doc bytes to .docx bytes using LibreOffice in a temp directory with a unique profile."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a unique LibreOffice user profile directory to prevent conflicts
        profile_dir = os.path.join(tmp_dir, 'lo_profile')
        os.makedirs(profile_dir, exist_ok=True)
        
        # Write input .doc to temp file
        input_path = os.path.join(tmp_dir, "input.doc")
        with open(input_path, "wb") as f:
            f.write(doc_bytes)
        
        # Convert to .docx with isolated LibreOffice profile
        cmd = [
            'libreoffice',
            '--headless',
            f'-env:UserInstallation=file://{profile_dir.replace(os.sep, "/")}',  # URI format
            '--convert-to',
            'docx',
            '--outdir',
            tmp_dir,
            input_path
        ]
        
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise RuntimeError(f"Conversion failed: {result.stderr.decode()}")
        
        # Read converted .docx
        output_path = os.path.join(tmp_dir, "input.docx")
        with open(output_path, "rb") as f:
            return f.read()


def load_document(file_path, **kwargs) -> DocxDocument:
    """Load a DOC or DOCX file into a python-docx Document object."""
    if file_path.lower().endswith('.doc'):
        docx_path = convert_doc_bytes_to_docx(kwargs["doc_obj"])
        return Document(BytesIO(docx_path))
    return Document(BytesIO(kwargs["doc_obj"]))


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
    
    known_styles = ['normal', 'body']
    def is_likely_heading(doc, paragraph):
        text = paragraph.text.strip()
        
        if not text:
            return 0
        
        score = 0
        
        if paragraph.style.name == 'List Paragraph':
            score += 2

        # Exclude known non-heading styles
        style_lower = paragraph.style.name.lower()
        if any(term in style_lower for term in ['bullet', 'normal', 'body']):
            score -= 1
        
        if len(text) < 60:
            score += 1
            
        if text.istitle():
            score += 2

        # Check for formatting
        if any(run.bold or run.italic for run in paragraph.runs) and style_lower in known_styles and len(text) < 40:
            score = 8
                
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
    if score == 8:
        return 1
    if score >= 4:  # Minimum confidence threshold
        # Additional context validation
        prev_paragraph = doc.paragraphs[max(0, index - 1)]
        if prev_paragraph.style != None:
            prev_style = prev_paragraph.style.name
        else:
            prev_style = "Normal"
        next_paragraph = doc.paragraphs[min(len(doc.paragraphs)-1, index + 1)]
        if next_paragraph.style != None:
            next_style = next_paragraph.style.name
        else:
            next_style = "Normal"
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


def convert_table_to_csv(table) -> str:
    """Converts a docx table to CSV format, including cell indices."""
    csv_rows = []
    for row_index, row in enumerate(table.rows):
        row_cells = []
        for col_index, cell in enumerate(row.cells):
            cell_text = cell.text.strip().replace('\n', ' ')
            # Include row and column indices in the cell value
            indexed_cell = f"[{row_index},{col_index}]: {cell_text}"  # Or any format you prefer
            row_cells.append(indexed_cell)
        csv_rows.append(",".join(row_cells))
    return "\n".join(csv_rows)


import json


def convert_table_to_json(table) -> str:
    """Converts a docx table to JSON."""
    table_data = []
    for row_index, row in enumerate(table.rows):
        row_data = {}
        for col_index, cell in enumerate(row.cells):
            # If you have a header row, use the header text as the key
            if row_index == 0:  # Header row
                header_text = cell.text.strip().replace('\n', ' ')
                row_data["header_" + str(col_index)] = header_text #Temporary key
            else:
               header_text = table.rows[0].cells[col_index].text.strip().replace('\n', ' ') if row_index > 0 else "col_" + str(col_index)
               row_data[header_text] = cell.text.strip().replace('\n', ' ')
        if row_index > 0:
            table_data.append(row_data)

    return json.dumps(table_data, indent=4, ensure_ascii=False)  # indent for readability


def convert_table_to_markdown(table) -> str:
    """Converts a docx table to a standard Markdown table format with headers and separators."""
    markdown_rows = []
    for i, row in enumerate(table.rows):
        cells = [cell.text.strip().replace('\n', ' ') for cell in row.cells]
        markdown_rows.append("| " + " | ".join(cells) + " |")
        # Add separator after the header row (first row)
        if i == 0:
            num_columns = len(cells)
            separator = "| " + " | ".join(["---"] * num_columns) + " |"
            markdown_rows.append(separator)
    return "\n".join(markdown_rows)

def remove_stray_backslashes(input_string: str) -> str:
    """
    Removes backslash characters from a string unless they are part of a
    recognized escape sequence (e.g., \\n, \\t, \\\\, \\", \\').
    """
    # This regex finds a `\` that is NOT followed by n, t, r, b, f, ', ", or another \.
    # The `(?!...)` syntax is a "negative lookahead".
    pattern = r'\\(?![ntrbf\'"\\])'

    return re.sub(pattern, '', input_string)

def remove_table_of_contents(text: str) -> str:
    """
    Removes the table of contents from a given text.

    This function identifies the table of contents section starting with
    the word "Contents" and removes all subsequent lines that match the
    TOC entry pattern (e.g., "[...](#_Toc...)").

    Args:
        text: The input string containing the document text.

    Returns:
        The text with the table of contents section removed.
    """
    lines = text.split('\n')

    # This list will hold the lines of the final document.
    output_lines = []

    # A flag to indicate if the current line is within the TOC section.
    in_toc_section = False

    # A regex pattern to identify TOC entry lines.
    toc_pattern = re.compile(r'\[.*\]\(#_Toc\d+\)')

    for line in lines:
        stripped_line = line.strip()

        # Check for the start of the table of contents.
        if "Contents" in stripped_line:
            in_toc_section = True
            # Skip the "Contents" line itself.
            continue

        # If we are in the TOC section, we check if the line is a TOC entry.
        if in_toc_section:
            # If the line is a TOC entry or an empty line within the TOC, we skip it.
            if toc_pattern.search(stripped_line) or not stripped_line:
                continue
            # If it's not a TOC entry, the TOC section has ended.
            else:
                in_toc_section = False

        # Add the line to our output list if it's not part of the TOC.
        output_lines.append(line)

    # Join the lines back into a single string and remove any leading newlines
    # that might have been left after removing the TOC block.
    return '\n'.join(output_lines).lstrip('\n')


def process_single_document(
    doc_obj: object,
    doc_path: str,
    target_chunk_size: int = config["retriever"]["chunk_size"],
    max_chunk_size: int = config["retriever"]["max_chunk_size"],
) -> List[Document]:

    regex_image = r"!\\?\[[^\]]*\]\([^\)]*\)?|<img[^>]*>"
    md = MarkItDown(enable_plugins=False)  # Set to True to enable plugins
    result = md.convert(BytesIO(doc_obj)).text_content
    result = re.sub(regex_image, "", result)
    for keyam in DICT_OF_TITLES:
        index_found = result[:100].find(keyam)
        if index_found != -1:
            metadata_value = DICT_OF_TITLES[keyam]
            metadata = {"source": doc_path}
            metadata["module"] = metadata_value
    output_result = remove_table_of_contents(result)
    index = output_result.find('#')
    output_result = output_result[index:]
    chunker = SoleChunker(output_result)
    chunks = chunker(False, True)
    chunks_final = []
    for w in chunks:
        chunkam = DocLangChain(w)
        chunkam.page_content = w
        chunkam.metadata = metadata
        chunks_final.append(chunkam)
    return chunks_final

def process_single_document_old(
    doc_obj: object,
    doc_path: str,
    target_chunk_size: int = config["retriever"]["chunk_size"],
    max_chunk_size: int = config["retriever"]["max_chunk_size"],
) -> List[Document]:
    """
    Process a single Word document and return chunks as Document objects.
    
    :param doc_obj: Document object/bytes
    :param doc_path: Path to the Word document
    :param target_chunk_size: Target size of each chunk
    :param max_chunk_size: Maximum allowed size of a chunk
    :return: List of Document objects
    """
    chunks = []
    current_chunk = {"h1": "", "h2": "", "h3": "", "h4": "", "content": []}  
    # Load the document, converting DOC to DOCX if necessary
    doc = load_document(doc_path, doc_obj=doc_obj)

    # Extract header text from the first page's header
    header_text = ""
    if doc.sections:
        first_section = doc.sections[0]
        header = first_section.header
        for para in header.paragraphs:
            header_text += para.text.strip() + "\n"
    header_text = header_text.strip()

    current_heading_level = float("inf") # Initialize current heading level

    # Track indices for paragraphs and tables separately
    paragraph_index = 0
    table_index = 0
    current_heading_level = float("inf")

    # Iterate through all document elements in order
    for element in doc.element.body:
        if isinstance(element, CT_P):
            if paragraph_index >= len(doc.paragraphs):
                continue
            text = doc.paragraphs[paragraph_index].text.strip()

            paragraph_index += 1  # Increment here to handle continue cases
            if not text:
                continue
            
            heading_level = extract_heading_level(doc, paragraph_index-1)

            # Handle chunk finalization        
            if (current_heading_level == 0) and (heading_level > current_heading_level):
                chunks.extend(
                    finalize_chunk(
                        current_chunk, target_chunk_size, max_chunk_size, doc_path
                    )
                )
            
            if heading_level == 1:
                current_chunk["h1"] = text
                current_chunk["h2"] = ""
                current_chunk["h3"] = ""
                current_chunk["h4"] = ""
                current_chunk["content"] = []
                                    
            elif heading_level == 2:
                current_chunk["h2"] = text
                current_chunk["h3"] = ""
                current_chunk["h4"] = ""
                current_chunk["content"] = []
                        
            elif heading_level == 3:
                current_chunk["h3"] = text
                current_chunk["h4"] = ""
                current_chunk["content"] = []

            elif heading_level == 4:
                current_chunk["h4"] = text
                current_chunk["content"] = []

            else:
                current_chunk["content"].append(text)
                    
            current_heading_level = heading_level

        elif isinstance(element, CT_Tbl):
            if table_index >= len(doc.tables):
                continue
            table = doc.tables[table_index]
            table_index += 1
            
            # Convert table to compact format and add to content
            compact_table = convert_table_to_json(table)
            table_chunk = current_chunk.copy()
            table_chunk["content"] = []
            if len(current_chunk["content"]) > 0:
                table_chunk["content"].append(current_chunk["content"].pop(-1))
            table_chunk["content"].append(compact_table)
            chunks.extend(finalize_chunk(table_chunk, target_chunk_size, max_chunk_size, doc_path, make_partition=False))

    chunks.extend(finalize_chunk(
        current_chunk, target_chunk_size, max_chunk_size, doc_path
        )
                  )
    # Prepend header text to each chunk's content if header exists
    if header_text:
        for chunk in chunks:
            # Assuming chunk has a 'content' attribute that is a string
            chunk.page_content = f"{header_text}\n{chunk.page_content}"

    return chunks


def finalize_chunk(chunk, target_chunk_size, max_chunk_size, source_file, make_partition=True):
    """
    Finalize a chunk, splitting it if necessary based on sentences and paragraphs, with 2-sentence overlap.

    :param chunk: Dictionary containing heading and content information
    :param target_chunk_size: Target size of each chunk
    :param max_chunk_size: Maximum allowed size of a chunk
    :param source_file: Path of the source document
    :param make_partition: Whether to partition the chunk
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
    
    if make_partition:
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
    else:
        chunk_size = int(1e+5)
        text_splitter = RecursiveCharacterTextSplitter(
            # Set a really small chunk size, just to show.
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        documents = text_splitter.create_documents([paragraph])
        
    for i in range(len(documents)):
        documents[i].page_content = headers + documents[i].page_content
        documents[i].metadata ={"source": source_file if type(source_file) == str else str(source_file)}    
    return documents


def chunk_document(doc_settings: Dict[object, Dict]) -> List["Document"]:
    """
    Process multiple Word documents.
    Uses parallel processing (ProcessPoolExecutor) to speed up large-scale runs.
    """
    all_chunks = []

    # --- NEW: Parallelize the per-document process using concurrent.futures ---

    # A ProcessPoolExecutor sidesteps the GIL for CPU-bound tasks, which can help
    # since python-docx parsing and chunking can be CPU-intensive on large docs.

    # Sequential processing for compatibility with document objects
    # for doc_obj, settings in doc_settings.items():
    #     doc_path = settings["file_name"]
    #     print(f"Submitting {doc_path} for processing...")
    #     try:
    #         result = process_single_document(
    #             doc_obj,
    #             doc_path,
    #             settings["target_chunk_size"],
    #             settings["max_chunk_size"]
    #         )
    #         all_chunks.extend(result)
    #         print(f"Successfully processed: {doc_path}")
    #     except Exception as e:
    #         print(f"Exception occurred while processing {doc_path}: {e}")

    # Optional: Uncomment below for parallel processing if document objects are serializable
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Collect futures for each document
        future_to_doc = {}
        for doc_obj, settings in doc_settings.items():
            doc_path = settings["file_name"]
            future = executor.submit(
                process_single_document,
                doc_obj,
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