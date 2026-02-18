import io
import re
import functools
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Union
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer#, AutoModel

from markitdown import MarkItDown

from .config import config


MAX_CHUNK_SIZE = config["embedding_model"]["max_length"]
MAX_TOKEN_SIZE = config["embedding_model"]["max_length"]
MAX_SUB_HEADER_TOKEN_PERCENTAGE = 0.3


SUPPORTED_FILE_EXTENSIONS = ['.docx', '.doc', '.md']
tokenizer = AutoTokenizer.from_pretrained(config["embedding_model"]["tokenizer_path"], padding_side='left')
# model = AutoModel.from_pretrained(config["embedding_model"]["model_path"]).eval()

# ============================================================================
# DOCUMENT PREPROCESSING
# ============================================================================

class ProcessDocs:
    """
    Preprocesses Word documents before chunking to ensure proper formatting.
    
    This class:
    - Converts Word documents to Markdown using MarkItDown
    - Removes table of contents sections
    - Removes stray backslashes
    - Ensures document starts with a markdown header (#)
    """
    
    def __init__(self, filename):
        with open(filename, "rb") as file:
            self.doc = file.read()
        self.md = MarkItDown(enable_plugins=False)
        # filename = filename.replace(".docx", ".md")
        # with open(filename, "w", encoding="utf-8") as file:
        #     self.doc = file.write(self.md)
    
    @staticmethod
    def remove_stray_backslashes(input_string: str) -> str:
        """
        Removes backslash characters from a string unless they are part of a
        recognized escape sequence (e.g., \\n, \\t, \\\\, \\", \\').
        """
        # This regex finds a `\` that is NOT followed by n, t, r, b, f, ', ", or another \.
        # The `(?!...)` syntax is a "negative lookahead".
        pattern = r'\\(?![ntrbf\'"\\])'
        return re.sub(pattern, '', input_string)
    
    @staticmethod
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
        toc_pattern = re.compile(r'\[.*\]\(#_[Tt]oc\d*\)')
        for line in lines:
            stripped_line = line.strip()
            # Check for the start of the table of contents.
            if "Contents" in stripped_line or "فهرست" in stripped_line or "Content" in stripped_line:
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
    
    def process_doc(self):
        """
        Process the Word document and return cleaned markdown text.
        
        Returns:
            str: Cleaned markdown text that starts with a header (#)
        """
        docx_bytes_io = io.BytesIO(self.doc)
        result = self.md.convert(docx_bytes_io).text_content
        
        # Remove stray backslashes
        output_result = self.remove_stray_backslashes(result)
        # Remove table of contents
        output_result = self.remove_table_of_contents(output_result)
        
        # Ensure document starts with '#' header
        index = output_result.find('#')
        if index != -1:
            output_result = output_result[index:]
        else:
            # If no header found, add a default one
            output_result = "# Document\n\n" + output_result
        
        return output_result


# ============================================================================
# MARKDOWN CONVERSION
# ============================================================================

def convert_word_to_markdown(file_paths: List[Union[str, Path]], output_dir: str) -> dict:
    """
    Convert multiple Word files to Markdown format using ProcessDocs.
    
    ProcessDocs ensures:
    - Table of contents is removed
    - Stray backslashes are cleaned
    - Document starts with a markdown header (#)
    
    Args:
        file_paths: List of file paths to Word documents (.docx or .doc)
        output_dir: Directory to save markdown files
    
    Returns:
        dict: Dictionary with file paths as keys and conversion status/output path as values
    """
    results = {}
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    for file_path in file_paths:
        file_path = Path(file_path)
        
        try:
            # Check if file exists
            if not file_path.exists():
                results[str(file_path)] = {"status": "error", "message": "File not found"}
                continue
            
            # Check if file is a Word document
            if file_path.suffix.lower() not in ['.docx', '.doc']:
                results[str(file_path)] = {"status": "error", "message": "Not a Word file"}
                continue
            
            # Use ProcessDocs to convert and preprocess the document
            processor = ProcessDocs(str(file_path))
            markdown_content = processor.process_doc()
            
            # Determine output path
            output_path = Path(output_dir) / f"{file_path.stem}.md"
            
            # Write markdown content to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            results[str(file_path)] = {
                "status": "success",
                "output_path": str(output_path),
                "message": f"Converted successfully to {output_path}"
            }
            
        except Exception as e:
            results[str(file_path)] = {
                "status": "error",
                "message": f"Conversion failed: {str(e)}"
            }
    
    return results


def preprocess_markdown_file(file_path: Path, output_path: Path) -> None:
    """
    Preprocess markdown files to ensure they start with a header and are properly formatted.
    
    Args:
        file_path: Path to the original markdown file
        output_path: Path where the preprocessed markdown should be saved
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove stray backslashes
    content = ProcessDocs.remove_stray_backslashes(content)
    
    # Remove table of contents if present
    content = ProcessDocs.remove_table_of_contents(content)
    # Ensure document starts with '#' header
    index = content.find('#')
    if index != -1:
        content = content[index:]
    else:
        # If no header found, add a default one
        filename_without_ext = file_path.stem.replace('_', ' ').replace('-', ' ').title()
        content = f"# {filename_without_ext}\n\n" + content
    
    # Write preprocessed content
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


# ============================================================================
# CHUNKING CLASSES
# ============================================================================

class BaseChunker(ABC):
    def __init__(self, md_file_address):
        self.tokenizer = AutoTokenizer.from_pretrained(config['embedding_model']['model_path'])
        with open(md_file_address, "r", encoding="utf-8") as f:
            self._all_of_doc_list = f.readlines()
            # self._all_of_doc_list = self._handle_no_title(self._all_of_doc_list)
            self._retain_only_headers = True

    @staticmethod
    def _handle_no_title(list_to_revise):
        list_to_revise_new = []
        if list_to_revise[0].startswith("#"):
            list_to_revise_new.append("Dummy Title")
            list_to_revise_new.append("\n")
        list_to_revise_new.extend(list_to_revise)
        return list_to_revise_new

    @staticmethod
    def get_number_of_sharps(my_string):
        original_len = len(my_string)
        stripped_len = len(my_string.lstrip('#'))
        sharp_count = original_len - stripped_len
        return sharp_count

    @property
    def all_lines(self):
        return self._all_of_doc_list

    @functools.cached_property
    def regex_images(self):
        return r"!\[[^\]]*\]\([^\)]*\)|<img[^>]*>"

    def remove_image_if_needed(self, text, remove_image_flag):
        if remove_image_flag:
            result = re.sub(self.regex_images, "", text)
        else:
            result = text
        return result

    @abstractmethod
    def __call__(self, retain_only_headers=True, remove_imgs=True):
        pass


class HierarchicalChunker(BaseChunker):
    def __init__(self, md_file_address):
        super().__init__(md_file_address)

    @staticmethod
    def get_chunks_to_only_header(current_level_dict, current_cum):
        for i in range(1, current_cum):
            current_level_dict[i] = current_level_dict[i].split("\n")[0].strip()

    @staticmethod
    def new_num_sharps_is_greater_than_prev_actions(text, num_sharps, current_level_dict):
        current_level_dict[num_sharps] = text

    def new_num_sharps_is_less_than_prev_actions(self, text, num_sharps, current_level_dict, list_to_expand):
        if self._retain_only_headers:
            dict_to_add = current_level_dict.copy()
            self.get_chunks_to_only_header(dict_to_add, num_sharps)
            list_to_expand.append(dict_to_add)
        else:
            list_to_expand.append(current_level_dict.copy())
        current_level_dict[num_sharps] = text
        for i in range(num_sharps + 1, 7):
            current_level_dict[i] = ""
        
    def new_num_sharps_is_equal_to_prev_actions(self, text, num_sharps, current_level_dict, list_to_expand):
        if self._retain_only_headers:
            dict_to_add = current_level_dict.copy()
            self.get_chunks_to_only_header(dict_to_add, num_sharps)
            list_to_expand.append(dict_to_add)
        else:
            list_to_expand.append(current_level_dict.copy())
        current_level_dict[num_sharps] = text

    def __call__(self, retain_only_headers=True, remove_imgs=True):
        self._retain_only_headers = retain_only_headers
        current_level_dict = {1: "", 2: "", 3: "", 4: "", 5: "", 6: ""}
        list_to_expand = []
        prev_num_sharps = 0
        for text in self.all_lines:
            text = self.remove_image_if_needed(text, remove_imgs)
            text = text.lstrip()
            text = text.lstrip("\\")
            if text.startswith("#"):
                get_num_sharps = self.get_number_of_sharps(text)
                if get_num_sharps < prev_num_sharps:
                    self.new_num_sharps_is_less_than_prev_actions(text, get_num_sharps, current_level_dict, list_to_expand)
                elif get_num_sharps == prev_num_sharps:
                    self.new_num_sharps_is_equal_to_prev_actions(text, get_num_sharps, current_level_dict,
                                                                 list_to_expand)
                elif get_num_sharps > prev_num_sharps:
                    self.new_num_sharps_is_greater_than_prev_actions(text, get_num_sharps, current_level_dict)
                prev_num_sharps = get_num_sharps
            else:
                try:
                    current_level_dict[prev_num_sharps] = current_level_dict[prev_num_sharps] + text
                except KeyError:
                    raise KeyError("The document does not start with #")

        dict_now = current_level_dict.copy()
        list_to_expand.append(dict_now)
        return list_to_expand


class HierarchicalChunker(BaseChunker):
    def __init__(self, md_file_address):
        super().__init__(md_file_address)

    @staticmethod
    def get_chunks_to_only_header(current_level_dict, current_cum):
        for i in range(1, current_cum):
            current_level_dict[i] = current_level_dict[i].split("\n")[0].strip()

    @staticmethod
    def new_num_sharps_is_greater_than_prev_actions(text, num_sharps, current_level_dict):
        current_level_dict[num_sharps] = text

    def new_num_sharps_is_less_than_prev_actions(self, text, num_sharps, current_level_dict, list_to_expand):
        if self._retain_only_headers:
            dict_to_add = current_level_dict.copy()
            self.get_chunks_to_only_header(dict_to_add, num_sharps)
            list_to_expand.append(dict_to_add)
        else:
            list_to_expand.append(current_level_dict.copy())
        current_level_dict[num_sharps] = text
        for i in range(num_sharps + 1, 7):
            current_level_dict[i] = ""
        
    def new_num_sharps_is_equal_to_prev_actions(self, text, num_sharps, current_level_dict, list_to_expand):
        if self._retain_only_headers:
            dict_to_add = current_level_dict.copy()
            self.get_chunks_to_only_header(dict_to_add, num_sharps)
            list_to_expand.append(dict_to_add)
        else:
            list_to_expand.append(current_level_dict.copy())
        current_level_dict[num_sharps] = text

    def __call__(self, retain_only_headers=True, remove_imgs=True):
        self._retain_only_headers = retain_only_headers
        current_level_dict = {1: "", 2: "", 3: "", 4: "", 5: "", 6: ""}
        list_to_expand = []
        prev_num_sharps = 0
        for text in self.all_lines:
            text = self.remove_image_if_needed(text, remove_imgs)
            text = text.lstrip()
            text = text.lstrip("\\")
            if text.startswith("#"):
                get_num_sharps = self.get_number_of_sharps(text)
                if get_num_sharps < prev_num_sharps:
                    self.new_num_sharps_is_less_than_prev_actions(text, get_num_sharps, current_level_dict, list_to_expand)
                elif get_num_sharps == prev_num_sharps:
                    self.new_num_sharps_is_equal_to_prev_actions(text, get_num_sharps, current_level_dict,
                                                                 list_to_expand)

                elif get_num_sharps > prev_num_sharps:
                    self.new_num_sharps_is_greater_than_prev_actions(text, get_num_sharps, current_level_dict)
                prev_num_sharps = get_num_sharps
            else:
                try:
                    current_level_dict[prev_num_sharps] = current_level_dict[prev_num_sharps] + text
                except KeyError:
                    raise KeyError("The document does not start with #")

        dict_now = current_level_dict.copy()
        list_to_expand.append(dict_now)
        return list_to_expand


class SoleChunker(HierarchicalChunker):
    def __init__(self, md_file_address):
        super().__init__(md_file_address)

    def hierarchy_to_sole(self, list_to_expand):
        list_final = [[]]
        list_of_done_values = []
        for counter_of_list, dict_elem in enumerate(list_to_expand):
            for key in range(1,7):
                value = dict_elem[key]
                if len(value) == 0 or value in list_of_done_values:
                    continue
                counter_of_pointer = counter_of_list
                while True:
                    if counter_of_pointer == len(list_to_expand) or list_to_expand[counter_of_pointer][key] != value:
                        break
                    dict_to_consider = list_to_expand[counter_of_pointer]
                    self._update_list_final(value, dict_to_consider, list_final)
                    counter_of_pointer = counter_of_pointer + 1
                list_final.append([])
                list_of_done_values.append(value)
        return list_final

    @staticmethod
    def _update_list_final(value, dict_to_consider, list_final):
        for i in range(1, 7):
            if len(dict_to_consider[i]) == 0:
                continue
            if dict_to_consider[i] == value:
                value_to_append = dict_to_consider[i]
                is_main_part = 1
            else:
                value_to_append = dict_to_consider[i].split("\n")[0]
                is_main_part = 0
            texts_in_last = [w[0] for w in list_final[-1]]
            if len(list_final[-1]) == 0 or value_to_append not in texts_in_last:
                list_final[-1].append((value_to_append, is_main_part))

    @staticmethod
    def __get_chunk_list__(paragraph, max_allowed_tokens):
        max_allowed_characters = max_allowed_tokens * 2
        separators = [
            r"[.!؟]",  # Punctuation marks indicating sentence end
            "\n\n",
            r",",  
            "\n"
        ]
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                # Set a really small chunk size, just to show.
                separators=separators,
                keep_separator=True,
                chunk_size=max_allowed_characters,
                chunk_overlap=0,
                length_function=len,
                is_separator_regex=True
            )
            splitted_text = text_splitter.split_text(paragraph)
        except Exception:
            print("error splitting paragraph:", paragraph)
            splitted_text = [paragraph]

        return splitted_text

    def get_splitted_text(self, reserved_part_max_len_token, rest_part, need_rechunk_yet):
        if reserved_part_max_len_token < 0:
            splitted_text = self.__get_chunk_list__(rest_part, max_allowed_tokens=20)
        else:
            need_rechunk_yet = False
            splitted_text = self.__get_chunk_list__(rest_part, max_allowed_tokens=reserved_part_max_len_token)
        return splitted_text, need_rechunk_yet

    def __rechunk__(self, list_to_rechunk):
        bag_of_chunks = []
        count_num_tokens = 0
        is_chunked = False
        need_rechunk_yet = True
        max_length = MAX_CHUNK_SIZE
        for elem in list_to_rechunk:
            len_elems = len(tokenizer.tokenize(elem))
            count_num_tokens = count_num_tokens + len_elems

        if count_num_tokens >= MAX_TOKEN_SIZE:
            max_elem = max(list_to_rechunk, key=len)
            index_to_cut = max_elem.find("\n")
            max_elem_header = max_elem[:index_to_cut]
            rest_part = max_elem[index_to_cut:]
            rest_part_len_token = len(
                tokenizer.tokenize(rest_part))
            other_part_len_token = count_num_tokens - rest_part_len_token
            reserved_part_max_len_token = MAX_TOKEN_SIZE - other_part_len_token
            splitted_text, need_rechunk_yet = self.get_splitted_text(reserved_part_max_len_token, rest_part, need_rechunk_yet)
            index_of_max = list_to_rechunk.index(max_elem)
            for text_splitted in splitted_text:
                list_new = []
                for i, elem in enumerate(list_to_rechunk):
                    if i == index_of_max:
                        list_new.append(max_elem_header + "\n" + text_splitted)
                    else:
                        list_new.append(elem)
                bag_of_chunks.append(list_new)
            is_chunked = True
        else:
            bag_of_chunks = list_to_rechunk
        return bag_of_chunks, is_chunked, need_rechunk_yet

    @staticmethod
    def chunk_piece_collector(chunk_pieces):
        if isinstance(chunk_pieces[0], str):
            return "\n".join(chunk_pieces)
        else:
            return ["\n".join(w) for w in chunk_pieces]

    @staticmethod
    def __count_num_hashtags__(elem):
        num_headings = len(elem) - len(elem.lstrip("#"))
        return num_headings

    def __remove_more_than_next_level_headings(self, list_final):
        num_headings_main = None
        list_final_removed = [[]]
        number_of_tokens_main = 0
        number_of_tokens_headings = 0
        for chunk_list in list_final:
            for elem, is_main in chunk_list:
                if is_main:
                    num_headings_main = self.__count_num_hashtags__(elem)
                if num_headings_main is None:
                    list_final_removed[-1].append(elem)
                else:
                    num_headings_elem = self.__count_num_hashtags__(elem)
                    if num_headings_elem <= num_headings_main + 1:
                        length_of_texts = len(tokenizer.tokenize(elem))
                        number_of_tokens_main = number_of_tokens_main + length_of_texts
                        if num_headings_elem == num_headings_main + 1:
                            number_of_tokens_headings = number_of_tokens_headings + length_of_texts
                            if number_of_tokens_headings / number_of_tokens_main > MAX_SUB_HEADER_TOKEN_PERCENTAGE:
                                break
                        list_final_removed[-1].append(elem)
            list_final_removed.append([])
        return list_final_removed

    def __cut_more_than_top_headings(self, list_final):
        pass

    def __call__(self, retain_only_headers=True, remove_imgs=True, remove_grandsons=True):
        list_to_expand = super().__call__(retain_only_headers, remove_imgs)
        list_final = self.hierarchy_to_sole(list_to_expand)
        list_final = [w for w in list_final if len(w) > 0]
        list_final = self.__remove_more_than_next_level_headings(list_final)
        list_final = [w for w in list_final if len(w) > 0]
        last_chunks = []
        for chunk in list_final:
            list_rechunked, is_chunked, need_rechunk_yet = self.__rechunk__(chunk)
            if is_chunked and need_rechunk_yet:
                for new_chunk in list_rechunked:
                    list_rechunked_2, is_chunked, need_rechunk_yet = self.__rechunk__(new_chunk)
                    if is_chunked:
                        last_chunks.extend(self.chunk_piece_collector(list_rechunked_2))
                    else:
                        last_chunks.append(self.chunk_piece_collector(list_rechunked_2))
            elif is_chunked:
                last_chunks.extend(self.chunk_piece_collector(list_rechunked))
            else:
                last_chunks.append(self.chunk_piece_collector(list_rechunked))
        alaki = [(len(tokenizer.tokenize(w)), w) for w in last_chunks if len(tokenizer.tokenize(w)) > MAX_CHUNK_SIZE]
        if len(alaki) != 0:
            print("bibi")
        return last_chunks

if __name__ == '__main__':
    from glob import glob
    from tqdm import tqdm
    # output_dir = r"E:\AI-DA-14041028\mds"
    # file_paths = glob(r"E:\AI-DA-14041028\*.docx")
    # convert_word_to_markdown(file_paths, output_dir)
    list_of_all = glob(r"E:\AI-DA-14041028\mds\*.md")
    # list_of_all = [r"E:\AI-DA-14041028\mds\CRM.md"]
    for w in tqdm(list_of_all):
        new_obj = SoleChunker(w)
        chunked = new_obj(retain_only_headers=False, remove_imgs=True)