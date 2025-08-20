import functools
import re
from abc import ABC, abstractmethod
from time import time
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

MAX_CHUNK_SIZE = 5000
MAX_TOKEN_SIZE = 512
import json

class BaseChunker(ABC):
    def __init__(self, md_file_address):
        if isinstance(md_file_address, str):
            self._all_of_doc_list = md_file_address.splitlines(True)
            self._retain_only_headers = True
        else:
            raise TypeError("md_file_address must be a path-like object or str of a file-like object")

    @staticmethod
    def get_number_of_sharps(my_string):
        original_len = len(my_string)

        # Length after removing leading '#'
        stripped_len = len(my_string.lstrip('#'))

        # The difference is the count of starting sharps
        sharp_count = original_len - stripped_len
        return sharp_count

    @property
    def all_lines(self):
        return self._all_of_doc_list

    @functools.cached_property
    def regex_images(self):
        return r"!\\?\[[^\]]*\]\([^\)]*\)?|<img[^>]*>"

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

    @staticmethod
    def hierarchy_to_sole(list_to_expand):
        list_final = [[]]
        list_of_done_values = []
        for counter_of_list, dict_elem in enumerate(list_to_expand):
            for key in range(1,7):
                value = dict_elem[key]
                if len(value) == 0 or value in list_of_done_values:
                    continue
                counter_of_pointer = counter_of_list
                while True:
                    if counter_of_pointer == len(list_to_expand):
                        break
                    dict_to_consider = list_to_expand[counter_of_pointer]
                    if dict_to_consider[key] != value:
                        break
                    for i in range(1, 7):
                        if len(dict_to_consider[i]) == 0:
                            continue
                        if dict_to_consider[i] == value:
                            value_to_append = dict_to_consider[i]
                        else:
                            # value_to_append = dict_to_consider[i].split("\n")[0].strip()
                            value_to_append = dict_to_consider[i].split("\n")[0]
                        if value_to_append not in list_final[-1]:
                            list_final[-1].append(value_to_append)
                    counter_of_pointer = counter_of_pointer + 1
                list_final.append([])
                list_of_done_values.append(value)
        return list_final

    @staticmethod
    def __get_chunk_list__(paragraph, max_allowed_tokens):
        max_allowed_characters = max_allowed_tokens * 2
        separators = [
            r"[.!؟]",  # Punctuation marks indicating sentence end
            "\n\n",
            r",",  # Comma
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
        except:
            print("kk")
            splitted_text = "|"

        return splitted_text

    @staticmethod
    def calculate_reserved_chunk_size(list_to_rechunk, num_total_token):
        max_elem = max(list_to_rechunk, key=len)
        index_to_cut = max_elem.find("\n")
        max_elem_header = max_elem[:index_to_cut]
        rest_part = max_elem[index_to_cut:]
        rest_part_len_token = len(rest_part.split())
        other_part_len_token = num_total_token - rest_part_len_token
        reserved_part_max_len_token = MAX_TOKEN_SIZE - other_part_len_token

    def __rechunk__(self, list_to_rechunk):
        bag_of_chunks = []
        count_num_tokens = 0
        is_chunked = False
        need_rechunk_yet = True
        for elem in list_to_rechunk:
            elems = elem.split()
            count_num_tokens = count_num_tokens + len(elems)

        if count_num_tokens >= MAX_TOKEN_SIZE:
            max_elem = max(list_to_rechunk, key=len)
            index_to_cut = max_elem.find("\n")
            max_elem_header = max_elem[:index_to_cut]
            rest_part = max_elem[index_to_cut:]
            rest_part_len_token = len(rest_part.split())
            other_part_len_token = count_num_tokens - rest_part_len_token
            reserved_part_max_len_token = MAX_TOKEN_SIZE - other_part_len_token
            if reserved_part_max_len_token < 0:
                splitted_text = self.__get_chunk_list__(rest_part, max_allowed_tokens=20)
            else:
                need_rechunk_yet = False
                splitted_text = self.__get_chunk_list__(rest_part, max_allowed_tokens=reserved_part_max_len_token)
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
        return "\n".join(chunk_pieces)


    def __call__(self, retain_only_headers=True, remove_imgs=True):
        list_to_expand = super().__call__(retain_only_headers, remove_imgs)
        list_final = self.hierarchy_to_sole(list_to_expand)
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
        return last_chunks



if __name__ == '__main__':
    files_to_chunk = [
                      r"E:\QA\resources\4thG-Intro\4thG-Intro_new.md",
                      r"E:\QA\resources\AboutSG\AboutSG_new.md",
                      r"E:\QA\resources\CRM\CRM_new.md",
                      r"E:\QA\resources\DA-Help\DA-Help_new.md",
                      r"E:\QA\resources\INV\INV_new.md",
                      r"E:\QA\resources\Report_builder\report_builder_corrected.md",
                      r"E:\QA\resources\Sales\Sales_new.md",
                      r"E:\QA\resources\TaxPayer\TaxPayer_new.md",
                      r"E:\QA\resources\Treasury_14040231\Treasury_14040231_new.md",
                      r"E:\QA\resources\راهنمای دفتر کل نسل 4\راهنمای دفتر کل نسل 4 (1).md",
                      ]

    # file_address = r"E:\QA\resources\راهنمای دفتر کل نسل 4\راهنمای دفتر کل نسل 4 (1).md"
    # file_address = r"E:\QA\resources\DA-Help\DA-Help.md"
    # t0 = time()
    # chunker = HierarchicalChunker(file_address)
    # list_to_expand = chunker(False, True)
    # t1 = time()
    # print("time for first procedure is: %s" % (t1 - t0))
    total_time = 0
    counter = 0
    list_of_all_chunks = []
    for address in files_to_chunk:
        address_suffix = address.split("\\")[3]
        t3 = time()
        chunker = SoleChunker(address)
        list_to_expand = chunker(False, True)
        list_to_expand = [(w, address_suffix) for w in list_to_expand]
        list_of_all_chunks.extend(list_to_expand)
        t4 = time()
        total_time = total_time + t4 - t3
        counter = counter + 1
        print("time for first procedure is: %s" % (t4 - t3))
    with open("all_chunks_extracted.json", "w", encoding="utf-8") as outfile:
        json.dump(list_of_all_chunks, outfile, ensure_ascii=False)
    # for i, chunk in enumerate(list_of_all_chunks):
    #     with open(rf"E:\ragtest\input_4thgen_chunks\{i}.txt", "w", encoding="utf-8") as f:
    #         f.write(chunk)
    print("ok")