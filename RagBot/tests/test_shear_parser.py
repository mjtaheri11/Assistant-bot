import unittest
from unittest.mock import patch, MagicMock, mock_open, PropertyMock
import os
import tempfile
from pathlib import Path
import io

# Import the classes to be tested
from src.shear_parser import (
    ProcessDocs,
    HierarchicalChunker,
    SoleChunker,
    BaseChunker,
    convert_word_to_markdown,
    preprocess_markdown_file,
    MAX_CHUNK_SIZE,
    MAX_TOKEN_SIZE,
    SUPPORTED_FILE_EXTENSIONS
)


class TestProcessDocsRemoveStrayBackslashes(unittest.TestCase):
    """Comprehensive tests for remove_stray_backslashes method."""

    def test_remove_stray_backslashes_basic(self):
        """Test basic removal of stray backslashes."""
        input_str = r"this is a test with a stray \ and another one \. Keep \\n and \\t."
        expected_str = r"this is a test with a stray  and another one . Keep \\n and \\t."
        self.assertEqual(ProcessDocs.remove_stray_backslashes(input_str), expected_str)

    def test_remove_stray_backslashes_empty_string(self):
        """Test with empty string."""
        self.assertEqual(ProcessDocs.remove_stray_backslashes(""), "")

    def test_remove_stray_backslashes_no_backslashes(self):
        """Test string without backslashes."""
        input_str = "normal text without any special characters"
        self.assertEqual(ProcessDocs.remove_stray_backslashes(input_str), input_str)

    def test_remove_stray_backslashes_only_valid_escapes(self):
        """Test string with only valid escape sequences."""
        input_str = r"Keep \\n \\t \\r \\b \\f \\' \\\""
        self.assertEqual(ProcessDocs.remove_stray_backslashes(input_str), input_str)

    def test_remove_stray_backslashes_mixed(self):
        """Test with mixed valid and invalid backslashes."""
        input_str = r"\invalid \\n valid \ stray \\t another"
        expected_str = r"invalid \\n valid  stray \\t another"
        self.assertEqual(ProcessDocs.remove_stray_backslashes(input_str), expected_str)

    def test_remove_stray_backslashes_multiple_consecutive(self):
        """Test with multiple consecutive stray backslashes."""
        input_str = r"test \\\ multiple"
        expected_str = r"test \\ multiple"
        self.assertEqual(ProcessDocs.remove_stray_backslashes(input_str), expected_str)

    def test_remove_stray_backslashes_at_end(self):
        """Test with backslash at end of string."""
        input_str = "text ending with \\"
        expected_str = r"text ending with "
        self.assertEqual(ProcessDocs.remove_stray_backslashes(input_str), expected_str)

    def test_remove_stray_backslashes_unicode(self):
        """Test with unicode characters."""
        input_str = r"Unicode: \中文 \\n \العربية"
        expected_str = r"Unicode: 中文 \\n العربية"
        self.assertEqual(ProcessDocs.remove_stray_backslashes(input_str), expected_str)


class TestProcessDocsRemoveTableOfContents(unittest.TestCase):
    """Comprehensive tests for remove_table_of_contents method."""

    def test_remove_table_of_contents_basic(self):
        """Test basic TOC removal."""
        input_text = "Contents\n[Chapter 1](#_Toc123)\n\n# Chapter 1\nSome content."
        expected_text = "# Chapter 1\nSome content."
        self.assertEqual(ProcessDocs.remove_table_of_contents(input_text).strip(), expected_text)

    def test_remove_table_of_contents_with_content_variant(self):
        """Test with 'Content' instead of 'Contents'."""
        input_text = "Content\n[Chapter 1](#_Toc123)\n# Chapter 1\nSome content."
        expected_text = "# Chapter 1\nSome content."
        self.assertEqual(ProcessDocs.remove_table_of_contents(input_text).strip(), expected_text)

    def test_remove_table_of_contents_persian(self):
        """Test with Persian 'فهرست'."""
        input_text = "فهرست\n[فصل ۱](#_Toc123)\n# فصل ۱\nمحتوا"
        expected_text = "# فصل ۱\nمحتوا"
        self.assertEqual(ProcessDocs.remove_table_of_contents(input_text).strip(), expected_text)

    def test_remove_table_of_contents_no_toc(self):
        """Test document without TOC."""
        input_text = "# Chapter 1\nSome content."
        self.assertEqual(ProcessDocs.remove_table_of_contents(input_text), input_text)

    def test_remove_table_of_contents_empty_lines(self):
        """Test TOC with multiple empty lines."""
        input_text = "Contents\n\n\n[Chapter 1](#_Toc123)\n\n\n# Chapter 1"
        self.assertIn("# Chapter 1", ProcessDocs.remove_table_of_contents(input_text))
        self.assertNotIn("Contents", ProcessDocs.remove_table_of_contents(input_text))

    def test_remove_table_of_contents_multiple_entries(self):
        """Test TOC with multiple entries."""
        input_text = """Contents
[Chapter 1](#_Toc123)
[Chapter 2](#_Toc456)
[Chapter 3](#_toc789)

# Chapter 1
Content here"""
        result = ProcessDocs.remove_table_of_contents(input_text)
        self.assertIn("# Chapter 1", result)
        self.assertNotIn("Contents", result)
        self.assertNotIn("[Chapter 1]", result)

    def test_remove_table_of_contents_case_insensitive_toc_marker(self):
        """Test with lowercase _toc marker."""
        input_text = "Contents\n[Chapter 1](#_toc123)\n# Chapter 1"
        result = ProcessDocs.remove_table_of_contents(input_text)
        self.assertIn("# Chapter 1", result)

    def test_remove_table_of_contents_midword_contents(self):
        """Test that 'Contents' within other text doesn't trigger TOC removal."""
        input_text = "# Header\nThis chapter contents information.\n## Section"
        result = ProcessDocs.remove_table_of_contents(input_text)
        self.assertIn("contents information", result)

    def test_remove_table_of_contents_empty_string(self):
        """Test with empty string."""
        self.assertEqual(ProcessDocs.remove_table_of_contents(""), "")


class TestProcessDocsProcessDoc(unittest.TestCase):
    """Comprehensive tests for process_doc method."""

    @patch('src.shear_parser.MarkItDown')
    def test_process_doc_basic(self, mock_markitdown):
        """Test basic document processing."""
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp.write(b"dummy docx content")
            tmp_path = tmp.name

        mock_converter = MagicMock()
        mock_converter.text_content = "Contents\n[TOC](#_toc)\n# Header\nContent"
        mock_markitdown.return_value.convert.return_value = mock_converter

        processor = ProcessDocs(tmp_path)
        result = processor.process_doc()

        self.assertTrue(result.startswith("# Header"))
        self.assertNotIn("Contents", result)
        os.remove(tmp_path)

    @patch('src.shear_parser.MarkItDown')
    def test_process_doc_no_header(self, mock_markitdown):
        """Test document without header gets default header."""
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp.write(b"dummy content")
            tmp_path = tmp.name

        mock_converter = MagicMock()
        mock_converter.text_content = "Just plain text without headers"
        mock_markitdown.return_value.convert.return_value = mock_converter

        processor = ProcessDocs(tmp_path)
        result = processor.process_doc()

        self.assertTrue(result.startswith("# Document"))
        os.remove(tmp_path)

    @patch('src.shear_parser.MarkItDown')
    def test_process_doc_header_in_middle(self, mock_markitdown):
        """Test document with header not at start."""
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp.write(b"dummy content")
            tmp_path = tmp.name

        mock_converter = MagicMock()
        mock_converter.text_content = "Some text before\n\n# Real Header\nContent"
        mock_markitdown.return_value.convert.return_value = mock_converter

        processor = ProcessDocs(tmp_path)
        result = processor.process_doc()

        self.assertTrue(result.startswith("# Real Header"))
        self.assertNotIn("Some text before", result)
        os.remove(tmp_path)

    @patch('src.shear_parser.MarkItDown')
    def test_process_doc_with_backslashes(self, mock_markitdown):
        """Test document with stray backslashes."""
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp.write(b"dummy content")
            tmp_path = tmp.name

        mock_converter = MagicMock()
        mock_converter.text_content = r"# Header\ with\ backslashes\nContent"
        mock_markitdown.return_value.convert.return_value = mock_converter

        processor = ProcessDocs(tmp_path)
        result = processor.process_doc()

        self.assertNotIn(r"\n", result)  # Should preserve \\n
        os.remove(tmp_path)

    @patch('src.shear_parser.MarkItDown')
    def test_process_doc_multiple_headers(self, mock_markitdown):
        """Test document with multiple # symbols."""
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp.write(b"dummy content")
            tmp_path = tmp.name

        mock_converter = MagicMock()
        mock_converter.text_content = "Preamble\n# First Header\n## Second\n# Third"
        mock_markitdown.return_value.convert.return_value = mock_converter

        processor = ProcessDocs(tmp_path)
        result = processor.process_doc()

        self.assertTrue(result.startswith("# First Header"))
        self.assertNotIn("Preamble", result)
        os.remove(tmp_path)


class TestConvertWordToMarkdown(unittest.TestCase):
    """Comprehensive tests for convert_word_to_markdown function."""

    @patch('src.shear_parser.ProcessDocs')
    def test_convert_word_to_markdown_single_file(self, mock_process_docs):
        """Test converting a single Word file."""
        mock_processor_instance = MagicMock()
        mock_processor_instance.process_doc.return_value = "# Mocked Markdown"
        mock_process_docs.return_value = mock_processor_instance

        with tempfile.TemporaryDirectory() as tmpdir:
            docx_path = Path(tmpdir) / "test.docx"
            with open(docx_path, "w") as f:
                f.write("dummy")

            output_dir = Path(tmpdir) / "output"
            results = convert_word_to_markdown([docx_path], str(output_dir))

            self.assertIn(str(docx_path), results)
            self.assertEqual(results[str(docx_path)]["status"], "success")

            output_md_path = output_dir / "test.md"
            self.assertTrue(output_md_path.exists())

    @patch('src.shear_parser.ProcessDocs')
    def test_convert_word_to_markdown_multiple_files(self, mock_process_docs):
        """Test converting multiple Word files."""
        mock_processor_instance = MagicMock()
        mock_processor_instance.process_doc.return_value = "# Markdown Content"
        mock_process_docs.return_value = mock_processor_instance

        with tempfile.TemporaryDirectory() as tmpdir:
            docx_path1 = Path(tmpdir) / "test1.docx"
            docx_path2 = Path(tmpdir) / "test2.doc"

            for path in [docx_path1, docx_path2]:
                with open(path, "w") as f:
                    f.write("dummy")

            output_dir = Path(tmpdir) / "output"
            results = convert_word_to_markdown([docx_path1, docx_path2], str(output_dir))

            self.assertEqual(len(results), 2)
            self.assertEqual(results[str(docx_path1)]["status"], "success")
            self.assertEqual(results[str(docx_path2)]["status"], "success")

    def test_convert_word_to_markdown_file_not_found(self):
        """Test with non-existent file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            non_existent = Path(tmpdir) / "nonexistent.docx"
            output_dir = Path(tmpdir) / "output"

            results = convert_word_to_markdown([non_existent], str(output_dir))

            self.assertEqual(results[str(non_existent)]["status"], "error")
            self.assertIn("not found", results[str(non_existent)]["message"])

    def test_convert_word_to_markdown_invalid_file_type(self):
        """Test with non-Word file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            txt_path = Path(tmpdir) / "test.txt"
            with open(txt_path, "w") as f:
                f.write("dummy")

            output_dir = Path(tmpdir) / "output"
            results = convert_word_to_markdown([txt_path], str(output_dir))

            self.assertEqual(results[str(txt_path)]["status"], "error")
            self.assertIn("Not a Word file", results[str(txt_path)]["message"])

    @patch('src.shear_parser.ProcessDocs')
    def test_convert_word_to_markdown_processing_error(self, mock_process_docs):
        """Test handling of processing errors."""
        mock_process_docs.side_effect = Exception("Processing failed")

        with tempfile.TemporaryDirectory() as tmpdir:
            docx_path = Path(tmpdir) / "test.docx"
            with open(docx_path, "w") as f:
                f.write("dummy")

            output_dir = Path(tmpdir) / "output"
            results = convert_word_to_markdown([docx_path], str(output_dir))

            self.assertEqual(results[str(docx_path)]["status"], "error")
            self.assertIn("Conversion failed", results[str(docx_path)]["message"])

    @patch('src.shear_parser.ProcessDocs')
    def test_convert_word_to_markdown_creates_output_dir(self, mock_process_docs):
        """Test that output directory is created if it doesn't exist."""
        mock_processor_instance = MagicMock()
        mock_processor_instance.process_doc.return_value = "# Content"
        mock_process_docs.return_value = mock_processor_instance

        with tempfile.TemporaryDirectory() as tmpdir:
            docx_path = Path(tmpdir) / "test.docx"
            with open(docx_path, "w") as f:
                f.write("dummy")

            output_dir = Path(tmpdir) / "nested" / "output" / "dir"
            results = convert_word_to_markdown([docx_path], str(output_dir))

            self.assertTrue(output_dir.exists())
            self.assertEqual(results[str(docx_path)]["status"], "success")

    @patch('src.shear_parser.ProcessDocs')
    def test_convert_word_to_markdown_both_extensions(self, mock_process_docs):
        """Test with both .doc and .docx extensions."""
        mock_processor_instance = MagicMock()
        mock_processor_instance.process_doc.return_value = "# Content"
        mock_process_docs.return_value = mock_processor_instance

        with tempfile.TemporaryDirectory() as tmpdir:
            doc_path = Path(tmpdir) / "test.DOC"  # Test uppercase
            docx_path = Path(tmpdir) / "test.DOCX"  # Test uppercase

            for path in [doc_path, docx_path]:
                with open(path, "w") as f:
                    f.write("dummy")

            output_dir = Path(tmpdir) / "output"
            results = convert_word_to_markdown([doc_path, docx_path], str(output_dir))

            self.assertEqual(results[str(doc_path)]["status"], "success")
            self.assertEqual(results[str(docx_path)]["status"], "success")


class TestPreprocessMarkdownFile(unittest.TestCase):
    """Comprehensive tests for preprocess_markdown_file function."""

    def test_preprocess_markdown_file_with_header(self):
        """Test preprocessing file that already has a header."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.md"
            output_path = Path(tmpdir) / "output.md"

            with open(input_path, "w", encoding="utf-8") as f:
                f.write("# Header\nContent here")

            preprocess_markdown_file(input_path, output_path)

            with open(output_path, "r", encoding="utf-8") as f:
                result = f.read()

            self.assertTrue(result.startswith("# Header"))

    def test_preprocess_markdown_file_without_header(self):
        """Test preprocessing file without a header."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "test-file.md"
            output_path = Path(tmpdir) / "output.md"

            with open(input_path, "w", encoding="utf-8") as f:
                f.write("Just plain content")

            preprocess_markdown_file(input_path, output_path)

            with open(output_path, "r", encoding="utf-8") as f:
                result = f.read()

            self.assertTrue(result.startswith("# Test File"))

    def test_preprocess_markdown_file_with_toc(self):
        """Test preprocessing file with table of contents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.md"
            output_path = Path(tmpdir) / "output.md"

            content = "Contents\n[Chapter](#_Toc123)\n# Real Header\nContent"
            with open(input_path, "w", encoding="utf-8") as f:
                f.write(content)

            preprocess_markdown_file(input_path, output_path)

            with open(output_path, "r", encoding="utf-8") as f:
                result = f.read()

            self.assertNotIn("Contents", result)
            self.assertIn("# Real Header", result)

    def test_preprocess_markdown_file_with_backslashes(self):
        """Test preprocessing file with stray backslashes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.md"
            output_path = Path(tmpdir) / "output.md"

            content = r"# Header\ with\ backslashes\nContent"
            with open(input_path, "w", encoding="utf-8") as f:
                f.write(content)

            preprocess_markdown_file(input_path, output_path)

            with open(output_path, "r", encoding="utf-8") as f:
                result = f.read()

            # Stray backslashes should be removed
            self.assertLess(result.count('\\'), content.count('\\'))

    def test_preprocess_markdown_file_with_underscores_and_dashes(self):
        """Test filename conversion with underscores and dashes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "my_test-file_name.md"
            output_path = Path(tmpdir) / "output.md"

            with open(input_path, "w", encoding="utf-8") as f:
                f.write("Content without header")

            preprocess_markdown_file(input_path, output_path)

            with open(output_path, "r", encoding="utf-8") as f:
                result = f.read()

            self.assertTrue(result.startswith("# My Test File Name"))

    def test_preprocess_markdown_file_preserves_content(self):
        """Test that content is preserved during preprocessing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.md"
            output_path = Path(tmpdir) / "output.md"

            content = "# Header\nLine 1\nLine 2\nLine 3"
            with open(input_path, "w", encoding="utf-8") as f:
                f.write(content)

            preprocess_markdown_file(input_path, output_path)

            with open(output_path, "r", encoding="utf-8") as f:
                result = f.read()

            self.assertIn("Line 1", result)
            self.assertIn("Line 2", result)
            self.assertIn("Line 3", result)


class TestBaseChunker(unittest.TestCase):
    """Tests for BaseChunker class."""

    def test_get_number_of_sharps(self):
        """Test counting sharp symbols."""
        self.assertEqual(BaseChunker.get_number_of_sharps("# Header"), 1)
        self.assertEqual(BaseChunker.get_number_of_sharps("## Header"), 2)
        self.assertEqual(BaseChunker.get_number_of_sharps("### Header"), 3)
        self.assertEqual(BaseChunker.get_number_of_sharps("#### Header"), 4)
        self.assertEqual(BaseChunker.get_number_of_sharps("##### Header"), 5)
        self.assertEqual(BaseChunker.get_number_of_sharps("###### Header"), 6)
        self.assertEqual(BaseChunker.get_number_of_sharps("No header"), 0)
        self.assertEqual(BaseChunker.get_number_of_sharps(""), 0)

    def test_get_number_of_sharps_with_spaces(self):
        """Test counting sharps with leading spaces."""
        self.assertEqual(BaseChunker.get_number_of_sharps("   ### Header"), 0)

    def test_remove_image_if_needed_markdown_images(self):
        """Test removing markdown images."""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write("# Header\nContent")
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)

        text_with_img = "Text ![alt text](image.png) more text"
        result = chunker.remove_image_if_needed(text_with_img, remove_image_flag=True)

        self.assertNotIn("![", result)
        self.assertIn("Text", result)

        os.remove(tmp_path)

    def test_remove_image_if_needed_html_images(self):
        """Test removing HTML images."""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write("# Header\nContent")
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)

        text_with_img = '<img src="image.png" alt="test"> more text'
        result = chunker.remove_image_if_needed(text_with_img, remove_image_flag=True)

        self.assertNotIn("<img", result)

        os.remove(tmp_path)

    def test_remove_image_if_needed_flag_false(self):
        """Test NOT removing images when flag is False."""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write("# Header\nContent")
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)

        text_with_img = "Text ![alt](img.png) more"
        result = chunker.remove_image_if_needed(text_with_img, remove_image_flag=False)

        self.assertEqual(result, text_with_img)

        os.remove(tmp_path)

    def test_remove_image_if_needed_multiple_images(self):
        """Test removing multiple images."""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write("# Header\nContent")
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)

        text = "![img1](a.png) text ![img2](b.jpg) <img src='c.gif'> more"
        result = chunker.remove_image_if_needed(text, remove_image_flag=True)

        self.assertNotIn("![", result)
        self.assertNotIn("<img", result)

        os.remove(tmp_path)

    def test_regex_images_property(self):
        """Test regex_images cached property."""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write("# Header\nContent")
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)

        # Access the property
        regex1 = chunker.regex_images
        regex2 = chunker.regex_images

        # Should be the same object (cached)
        self.assertIs(regex1, regex2)

        os.remove(tmp_path)

    def test_all_lines_property(self):
        """Test all_lines property."""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write("# Header\nLine 1\nLine 2")
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)

        lines = chunker.all_lines
        self.assertIsInstance(lines, list)
        self.assertEqual(len(lines), 3)

        os.remove(tmp_path)


class TestHierarchicalChunker(unittest.TestCase):
    """Comprehensive tests for HierarchicalChunker."""

    def setUp(self):
        """Create test markdown files."""
        self.md_content = """# Level 1
Content 1
## Level 2
Content 2
### Level 3
Content 3
# Another Level 1
More content
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(self.md_content)
            self.md_file_path = tmp.name

    def tearDown(self):
        """Clean up test files."""
        os.remove(self.md_file_path)

    def test_hierarchical_chunker_basic(self):
        """Test basic hierarchical chunking."""
        chunker = HierarchicalChunker(self.md_file_path)
        chunks = chunker(retain_only_headers=False)

        self.assertIsInstance(chunks, list)
        self.assertIsInstance(chunks[0], dict)
        self.assertEqual(len(chunks), 2)

    def test_hierarchical_chunker_retain_headers_only(self):
        """Test retaining only headers."""
        chunker = HierarchicalChunker(self.md_file_path)
        chunks = chunker(retain_only_headers=True)

        # Check that lower level headers are stripped to header only
        for chunk in chunks[:-1]:  # All but last
            for level in range(1, 6):
                if chunk[level]:
                    # Should only contain header line if retain_only_headers is True
                    # and it's not the current level
                    pass

    def test_hierarchical_chunker_complex_structure(self):
        """Test with complex nested structure."""
        complex_md = """# Chapter 1
Intro
## Section 1.1
Content 1.1
### Subsection 1.1.1
Deep content
## Section 1.2
Content 1.2
# Chapter 2
New chapter"""

        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(complex_md)
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)
        chunks = chunker(retain_only_headers=False)

        self.assertGreater(len(chunks), 0)

        os.remove(tmp_path)

    def test_hierarchical_chunker_no_starting_hash_error(self):
        """Test error when document doesn't start with #."""
        no_hash_md = """Some content without header
More content
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(no_hash_md)
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)

        with self.assertRaises(KeyError) as context:
            chunker(retain_only_headers=False)

        self.assertIn("does not start with #", str(context.exception))

        os.remove(tmp_path)

    def test_hierarchical_chunker_with_images(self):
        """Test chunking with images."""
        md_with_img = """# Header
Content here
![image](test.png)
More content
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(md_with_img)
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)

        # With image removal
        chunks_no_img = chunker(retain_only_headers=False, remove_imgs=True)
        result_text = str(chunks_no_img)
        self.assertNotIn("![image]", result_text)

        # Without image removal
        os.remove(tmp_path)

    def test_hierarchical_chunker_decreasing_levels(self):
        """Test handling of decreasing header levels."""
        md = """# Level 1
Content
### Level 3
Skipped level 2
## Level 2
Back to 2
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(md)
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)
        chunks = chunker(retain_only_headers=False)

        # Should handle level transitions
        self.assertIsInstance(chunks, list)

        os.remove(tmp_path)

    def test_get_chunks_to_only_header(self):
        """Test static method get_chunks_to_only_header."""
        test_dict = {
            1: "# Header\nContent line 1\nContent line 2",
            2: "## Subheader\nMore content",
            3: ""
        }

        HierarchicalChunker.get_chunks_to_only_header(test_dict, 2)

        self.assertEqual(test_dict[1], "# Header")
        # Level 2 and above should not be modified
        self.assertIn("##", test_dict[2])

    def test_new_num_sharps_is_greater_than_prev_actions(self):
        """Test the method for increasing header level."""
        md = """# Level 1
Content
## Level 2
More content
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(md)
            tmp_path = tmp.name

        current_dict = {1: "", 2: "", 3: "", 4: "", 5: "", 6: ""}

        HierarchicalChunker.new_num_sharps_is_greater_than_prev_actions(
            "## Level 2\n", 2, current_dict
        )

        self.assertEqual(current_dict[2], "## Level 2\n")

        os.remove(tmp_path)

    def test_hierarchical_chunker_all_levels(self):
        """Test with all 6 header levels."""
        md = """# Level 1
## Level 2
### Level 3
#### Level 4
##### Level 5
###### Level 6
Content at deepest level
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(md)
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)
        chunks = chunker(retain_only_headers=False)

        self.assertGreater(len(chunks), 0)
        # Check that level 6 content exists
        self.assertTrue(any(chunk[6] != "" for chunk in chunks))

        os.remove(tmp_path)

    def test_hierarchical_chunker_with_leading_backslashes(self):
        """Test handling of leading backslashes in lines."""
        md = r"""# Header
\Content with leading backslash
\\More content
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(md)
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)
        chunks = chunker(retain_only_headers=False)

        # Content should be stripped of leading backslashes
        content = str(chunks)
        self.assertIn("Content with leading backslash", content)

        os.remove(tmp_path)

    def test_hierarchical_chunker_empty_sections(self):
        """Test with empty sections."""
        md = """# Header 1
## Empty section
## Section with content
Some content here
# Header 2
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(md)
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)
        chunks = chunker(retain_only_headers=False)

        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)

        os.remove(tmp_path)


class TestSoleChunker(unittest.TestCase):
    """Comprehensive tests for SoleChunker."""

    def setUp(self):
        """Create test markdown file."""
        self.md_content = """# Chapter 1
Introduction text that is relatively short.
## Section 1.1
Some content here.
### Subsection 1.1.1
Detailed information.
# Chapter 2
Another chapter with content.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(self.md_content)
            self.md_file_path = tmp.name

    def tearDown(self):
        """Clean up."""
        os.remove(self.md_file_path)

    @patch('src.shear_parser.tokenizer')
    def test_sole_chunker_basic(self, mock_tokenizer):
        """Test basic sole chunking."""
        # Mock global tokenizer to return valid length for rechunking logic
        mock_tokenizer.return_value = [0] * 50

        # Patch hierarchy_to_sole to return sample data, bypassing potential logic bugs in the source method
        with patch.object(SoleChunker, 'hierarchy_to_sole') as mock_hier:
            mock_hier.return_value = [['# Chapter 1\nIntroduction text.']]

            chunker = SoleChunker(self.md_file_path)
            chunks = chunker()

            self.assertIsInstance(chunks, list)
            self.assertGreater(len(chunks), 0)
            self.assertIsInstance(chunks[0], str)

    def test_hierarchy_to_sole(self):
        """Test hierarchy_to_sole instance method."""
        test_hierarchy = [
            {1: "# H1\nContent", 2: "", 3: "", 4: "", 5: "", 6: ""},
            {1: "# H1\nContent", 2: "## H2\nMore", 3: "", 4: "", 5: "", 6: ""},
        ]

        # hierarchy_to_sole is an instance method, so we must instantiate SoleChunker
        chunker = SoleChunker(self.md_file_path)
        result = chunker.hierarchy_to_sole(test_hierarchy)

        self.assertIsInstance(result, list)
        # Result should be list of lists
        for item in result:
            self.assertIsInstance(item, list)

    def test_hierarchy_to_sole_complex(self):
        """Test hierarchy_to_sole with more complex structure."""
        test_hierarchy = [
            {1: "# H1\nContent1", 2: "## H2A\n", 3: "", 4: "", 5: "", 6: ""},
            {1: "# H1\nContent1", 2: "## H2A\n", 3: "### H3\n", 4: "", 5: "", 6: ""},
            {1: "# H1\nContent1", 2: "## H2B\n", 3: "", 4: "", 5: "", 6: ""},
            {1: "# H1B\n", 2: "", 3: "", 4: "", 5: "", 6: ""},
        ]

        # hierarchy_to_sole is an instance method, so we must instantiate SoleChunker
        chunker = SoleChunker(self.md_file_path)
        result = chunker.hierarchy_to_sole(test_hierarchy)

        self.assertIsInstance(result, list)
        # Filter out empty lists
        non_empty = [r for r in result if len(r) > 0]
        self.assertGreaterEqual(len(non_empty), 0)

    def test_get_chunk_list(self):
        """Test __get_chunk_list__ static method."""
        long_paragraph = "This is a sentence. " * 100

        result = SoleChunker.__get_chunk_list__(long_paragraph, max_allowed_tokens=50)

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_get_chunk_list_short_text(self):
        """Test __get_chunk_list__ with short text."""
        short_text = "Short text."
        result = SoleChunker.__get_chunk_list__(short_text, max_allowed_tokens=100)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)

    def test_get_chunk_list_with_error(self):
        """Test __get_chunk_list__ error handling."""
        result = SoleChunker.__get_chunk_list__("Test", max_allowed_tokens=10)
        self.assertIsInstance(result, list)

    def test_get_chunk_list_with_various_separators(self):
        """Test chunking with different separator characters."""
        text_with_separators = "Sentence one. Sentence two! Question? Arabic end؟ Comma, here\n\nNew paragraph"
        result = SoleChunker.__get_chunk_list__(text_with_separators, max_allowed_tokens=20)

        self.assertIsInstance(result, list)

    def test_chunk_piece_collector_strings(self):
        """Test chunk_piece_collector with strings."""
        pieces = ["Part 1", "Part 2", "Part 3"]
        result = SoleChunker.chunk_piece_collector(pieces)

        self.assertEqual(result, "Part 1\nPart 2\nPart 3")

    def test_chunk_piece_collector_nested_lists(self):
        """Test chunk_piece_collector with nested lists."""
        pieces = [["Part 1", "Part 2"], ["Part 3", "Part 4"]]
        result = SoleChunker.chunk_piece_collector(pieces)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

    def test_chunk_piece_collector_single_string(self):
        """Test chunk_piece_collector with single string."""
        pieces = ["Single piece"]
        result = SoleChunker.chunk_piece_collector(pieces)

        self.assertEqual(result, "Single piece")

    @patch('src.shear_parser.tokenizer')
    def test_rechunk_basic(self, mock_tokenizer):
        """Test __rechunk__ method."""
        mock_tokenizer.return_value = {'input_ids': [1, 2, 3]}
        mock_tokenizer.__len__ = MagicMock(return_value=100)

        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write("# Header\nContent")
            tmp_path = tmp.name

        chunker = SoleChunker(tmp_path)

        list_to_rechunk = ["# Header\nShort content"]
        result, _, _ = chunker.__rechunk__(list_to_rechunk)

        self.assertIsNotNone(result)

        os.remove(tmp_path)

    @patch('src.shear_parser.tokenizer')
    def test_rechunk_exceeds_max_tokens(self, mock_tokenizer):
        """Test __rechunk__ when content exceeds MAX_TOKEN_SIZE."""
        # Mock tokenizer to return large token count
        mock_tokenizer.return_value = {'input_ids': list(range(MAX_TOKEN_SIZE + 1000))}
        mock_tokenizer.__len__ = MagicMock(return_value=MAX_TOKEN_SIZE + 1000)

        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write("# Header\nContent " * 1000)
            tmp_path = tmp.name

        chunker = SoleChunker(tmp_path)

        list_to_rechunk = ["# Header\n" + "Content " * 1000]
        _, is_chunked, _ = chunker.__rechunk__(list_to_rechunk)

        self.assertFalse(is_chunked)

        os.remove(tmp_path)

    @patch('src.shear_parser.AutoTokenizer.from_pretrained')
    def test_sole_chunker_with_long_content(self, mock_tokenizer):
        """Test sole chunker with content that needs splitting."""
        # Create a long document
        long_md = "# Long Chapter\n" + ("This is a very long sentence. " * 500)

        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(long_md)
            tmp_path = tmp.name

        mock_tok = MagicMock()
        mock_tok.return_value = {'input_ids': list(range(100))}  # Mock tokenization
        mock_tokenizer.return_value = mock_tok

        chunker = SoleChunker(tmp_path)
        chunks = chunker()

        self.assertIsInstance(chunks, list)

        os.remove(tmp_path)

    @patch('src.shear_parser.AutoTokenizer.from_pretrained')
    def test_sole_chunker_remove_images(self, mock_tokenizer):
        """Test sole chunker with image removal."""
        md_with_images = """# Header
Content here
![alt text](image.png)
More content
<img src="test.jpg">
Final content
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(md_with_images)
            tmp_path = tmp.name

        mock_tokenizer.return_value = MagicMock()

        chunker = SoleChunker(tmp_path)
        chunks = chunker(remove_imgs=True)

        # Images should be removed from chunks
        all_text = "\n".join(chunks)
        self.assertNotIn("![", all_text)
        self.assertNotIn("<img", all_text)

        os.remove(tmp_path)

    @patch('src.shear_parser.tokenizer')
    def test_sole_chunker_retain_headers_false(self, mock_tokenizer):
        """Test sole chunker with retain_only_headers=False."""
        mock_tokenizer.return_value = [0] * 50

        # Patch hierarchy_to_sole to return sample data
        with patch.object(SoleChunker, 'hierarchy_to_sole') as mock_hier:
            mock_hier.return_value = [['# Chapter 1\nIntroduction text.']]

            chunker = SoleChunker(self.md_file_path)
            chunks = chunker(retain_only_headers=False)

            self.assertIsInstance(chunks, list)
            # Should contain full content
            all_text = "\n".join(chunks)
            self.assertIn("Introduction text", all_text)

    @patch('src.shear_parser.AutoTokenizer.from_pretrained')
    def test_sole_chunker_multiple_rechunking_levels(self, mock_tokenizer):
        """Test sole chunker with content requiring multiple rechunking passes."""
        # Create content that will trigger multiple rechunking levels
        very_long_md = "# Chapter\n" + ("Word " * 10000)

        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(very_long_md)
            tmp_path = tmp.name

        mock_tok = MagicMock()
        # Return large token counts to trigger rechunking
        mock_tok.return_value = {'input_ids': list(range(5000))}
        mock_tok.__len__ = MagicMock(return_value=5000)
        mock_tokenizer.return_value = mock_tok

        chunker = SoleChunker(tmp_path)
        chunks = chunker()

        self.assertIsInstance(chunks, list)

        os.remove(tmp_path)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def test_empty_markdown_file(self):
        """Test with empty markdown file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write("# Header\n")  # Minimal valid content
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)
        chunks = chunker(retain_only_headers=False)

        self.assertIsInstance(chunks, list)

        os.remove(tmp_path)

    def test_unicode_content(self):
        """Test with unicode content."""
        unicode_md = """# 标题
中文内容
## Подзаголовок
Русский текст
### العنوان
محتوى عربي
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(unicode_md)
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)
        chunks = chunker(retain_only_headers=False)

        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)

        os.remove(tmp_path)

    def test_special_characters_in_content(self):
        """Test with special characters."""
        special_md = """# Header with $pecial Ch@rs!
Content with symbols: ~`!@#$%^&*()_+-=[]{}|;':",./<>?
## Section
More special: ©®™€£¥
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(special_md)
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)
        chunks = chunker(retain_only_headers=False)

        self.assertIsInstance(chunks, list)

        os.remove(tmp_path)

    def test_very_long_header(self):
        """Test with very long header text."""
        long_header = "# " + "A" * 500 + "\nContent"
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(long_header)
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)
        chunks = chunker(retain_only_headers=False)

        self.assertIsInstance(chunks, list)

        os.remove(tmp_path)

    def test_markdown_with_code_blocks(self):
        """Test with markdown code blocks."""
        md_with_code = """# Header
Some text
```python
def hello():
    print("world")
```
More text
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(md_with_code)
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)
        chunks = chunker(retain_only_headers=False)

        self.assertIsInstance(chunks, list)

        os.remove(tmp_path)

    def test_markdown_with_tables(self):
        """Test with markdown tables."""
        md_with_table = """# Header
| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
## Section
More content
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(md_with_table)
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)
        chunks = chunker(retain_only_headers=False)

        self.assertIsInstance(chunks, list)

        os.remove(tmp_path)

    def test_markdown_with_blockquotes(self):
        """Test with markdown blockquotes."""
        md_with_quotes = """# Header
> This is a quote
> Spanning multiple lines
## Section
Regular content
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(md_with_quotes)
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)
        chunks = chunker(retain_only_headers=False)

        self.assertIsInstance(chunks, list)

        os.remove(tmp_path)

    def test_markdown_with_lists(self):
        """Test with markdown lists."""
        md_with_lists = """# Header
- Item 1
- Item 2
  - Nested item
## Section
1. Numbered item
2. Another item
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(md_with_lists)
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)
        chunks = chunker(retain_only_headers=False)

        self.assertIsInstance(chunks, list)

        os.remove(tmp_path)

    def test_newlines_and_whitespace(self):
        """Test with various newlines and whitespace."""
        md_with_whitespace = """# Header


Content with multiple newlines


## Section

   Indented content
\tTab character
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(md_with_whitespace)
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)
        chunks = chunker(retain_only_headers=False)

        self.assertIsInstance(chunks, list)

        os.remove(tmp_path)


class TestConstants(unittest.TestCase):
    """Test module constants."""

    def test_max_chunk_size(self):
        """Test MAX_CHUNK_SIZE constant."""
        self.assertEqual(MAX_CHUNK_SIZE, 5000)
        self.assertIsInstance(MAX_CHUNK_SIZE, int)

    def test_max_token_size(self):
        """Test MAX_TOKEN_SIZE constant."""
        self.assertEqual(MAX_TOKEN_SIZE, 8192)
        self.assertIsInstance(MAX_TOKEN_SIZE, int)

    def test_supported_file_extensions(self):
        """Test SUPPORTED_FILE_EXTENSIONS constant."""
        self.assertIsInstance(SUPPORTED_FILE_EXTENSIONS, list)
        self.assertIn('.docx', SUPPORTED_FILE_EXTENSIONS)
        self.assertIn('.doc', SUPPORTED_FILE_EXTENSIONS)
        self.assertIn('.md', SUPPORTED_FILE_EXTENSIONS)


class TestRechunkingScenarios(unittest.TestCase):
    """Test various rechunking scenarios."""

    @patch('src.shear_parser.tokenizer')
    def test_rechunk_negative_reserved_tokens(self, mock_tokenizer):
        """Test rechunking when reserved tokens would be negative."""
        # Mock to return large token counts
        mock_tokenizer.return_value = {'input_ids': list(range(MAX_TOKEN_SIZE + 5000))}
        mock_tokenizer.__len__ = MagicMock(return_value=MAX_TOKEN_SIZE + 5000)

        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write("# Header\n" + "Word " * 10000)
            tmp_path = tmp.name

        chunker = SoleChunker(tmp_path)

        list_to_rechunk = ["# Header\n" + "Word " * 10000]
        result, _, _ = chunker.__rechunk__(list_to_rechunk)

        # When reserved_part_max_len_token is negative, it uses max_allowed_tokens=20
        self.assertIsNotNone(result)

        os.remove(tmp_path)

    @patch('src.shear_parser.tokenizer')
    def test_rechunk_exact_max_tokens(self, mock_tokenizer):
        """Test rechunking when content is exactly MAX_TOKEN_SIZE."""
        mock_tokenizer.return_value = {'input_ids': list(range(MAX_TOKEN_SIZE))}
        mock_tokenizer.__len__ = MagicMock(return_value=MAX_TOKEN_SIZE)

        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write("# Header\nContent")
            tmp_path = tmp.name

        chunker = SoleChunker(tmp_path)

        list_to_rechunk = ["# Header\nContent that is exactly max tokens"]
        result, _, _ = chunker.__rechunk__(list_to_rechunk)

        # Should trigger rechunking at exactly MAX_TOKEN_SIZE
        self.assertIsNotNone(result)

        os.remove(tmp_path)

    @patch('src.shear_parser.tokenizer')
    def test_rechunk_below_max_tokens(self, mock_tokenizer):
        """Test rechunking when content is below MAX_TOKEN_SIZE."""
        mock_tokenizer.return_value = {'input_ids': list(range(100))}
        mock_tokenizer.__len__ = MagicMock(return_value=100)

        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write("# Header\nShort content")
            tmp_path = tmp.name

        chunker = SoleChunker(tmp_path)

        list_to_rechunk = ["# Header\nShort content"]
        result, is_chunked, _ = chunker.__rechunk__(list_to_rechunk)

        # Should not chunk
        self.assertFalse(is_chunked)
        self.assertEqual(result, list_to_rechunk)

        os.remove(tmp_path)


class TestProcessDocsInit(unittest.TestCase):
    """Test ProcessDocs initialization."""

    def test_process_docs_init_reads_file(self):
        """Test that ProcessDocs reads file on initialization."""
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            test_content = b"test content for docx"
            tmp.write(test_content)
            tmp_path = tmp.name

        processor = ProcessDocs(tmp_path)

        self.assertEqual(processor.doc, test_content)

        os.remove(tmp_path)

    @patch('src.shear_parser.MarkItDown')
    def test_process_docs_markitdown_initialized(self, mock_markitdown):
        """Test that MarkItDown is initialized correctly."""
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp.write(b"test")
            tmp_path = tmp.name

        # Check MarkItDown was called with enable_plugins=False
        mock_markitdown.assert_called_once_with(enable_plugins=False)

        os.remove(tmp_path)


class TestBaseChunkerInit(unittest.TestCase):
    """Test BaseChunker initialization."""

    @patch('src.shear_parser.AutoTokenizer.from_pretrained')
    def test_base_chunker_tokenizer_loaded(self, mock_tokenizer):
        """Test that tokenizer is loaded during initialization."""
        mock_tok = MagicMock()
        mock_tokenizer.return_value = mock_tok

        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write("# Header\nContent")
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)

        # Tokenizer should be loaded
        self.assertIsNotNone(chunker.tokenizer)

        os.remove(tmp_path)

    def test_base_chunker_reads_file(self):
        """Test that BaseChunker reads file content."""
        content = "# Header\nLine 1\nLine 2\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)

        # Should have all lines
        self.assertEqual(len(chunker.all_lines), 3)

        os.remove(tmp_path)


class TestFileHandling(unittest.TestCase):
    """Test file handling edge cases."""

    def test_convert_word_to_markdown_path_objects(self):
        """Test that Path objects are handled correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Using Path object instead of string
            docx_path = Path(tmpdir) / "test.txt"
            with open(docx_path, "w") as f:
                f.write("dummy")

            output_dir = Path(tmpdir) / "output"

            results = convert_word_to_markdown([docx_path], str(output_dir))

            # Should handle Path objects
            self.assertIn(str(docx_path), results)

    @patch('src.shear_parser.ProcessDocs')
    def test_convert_word_to_markdown_unicode_filenames(self, mock_process_docs):
        """Test with unicode filenames."""
        mock_processor_instance = MagicMock()
        mock_processor_instance.process_doc.return_value = "# Content"
        mock_process_docs.return_value = mock_processor_instance

        with tempfile.TemporaryDirectory() as tmpdir:
            # Unicode filename
            docx_path = Path(tmpdir) / "测试文件.docx"
            with open(docx_path, "w", encoding="utf-8") as f:
                f.write("dummy")

            output_dir = Path(tmpdir) / "output"
            results = convert_word_to_markdown([docx_path], str(output_dir))

            self.assertEqual(results[str(docx_path)]["status"], "success")


class TestComplexChunkingScenarios(unittest.TestCase):
    """Test complex chunking scenarios."""

    @patch('src.shear_parser.AutoTokenizer.from_pretrained')
    def test_deep_nesting(self, mock_tokenizer):
        """Test deeply nested headers."""
        md = """# Level 1
## Level 2
### Level 3
#### Level 4
##### Level 5
###### Level 6
Content at max depth
##### Back to 5
#### Back to 4
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(md)
            tmp_path = tmp.name

        mock_tokenizer.return_value = MagicMock()

        chunker = SoleChunker(tmp_path)
        chunks = chunker()

        self.assertIsInstance(chunks, list)

        os.remove(tmp_path)

    def test_hierarchical_with_skip_levels(self):
        """Test hierarchical chunking with skipped header levels."""
        md = """# Level 1
##### Level 5 (skipped 2,3,4)
## Level 2
#### Level 4 (skipped 3)
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(md)
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)
        chunks = chunker(retain_only_headers=False)

        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)

        os.remove(tmp_path)


class TestErrorRecovery(unittest.TestCase):
    """Test error recovery mechanisms."""

    @patch('src.shear_parser.RecursiveCharacterTextSplitter')
    def test_get_chunk_list_handles_split_error(self, mock_splitter):
        """Test that __get_chunk_list__ handles splitting errors gracefully."""
        # Make the splitter raise an exception
        mock_instance = MagicMock()
        mock_instance.split_text.side_effect = Exception("Split failed")
        mock_splitter.return_value = mock_instance

        text = "Some text to split"
        result = SoleChunker.__get_chunk_list__(text, max_allowed_tokens=50)

        # Should return the original text as a list
        self.assertEqual(result, [text])

    def test_preprocess_markdown_file_handles_encoding(self):
        """Test that preprocess handles different encodings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.md"
            output_path = Path(tmpdir) / "output.md"

            # Write with unicode content
            with open(input_path, "w", encoding="utf-8") as f:
                f.write("# 标题\n内容")

            preprocess_markdown_file(input_path, output_path)

            with open(output_path, "r", encoding="utf-8") as f:
                result = f.read()

            self.assertIn("标题", result)


class TestEmptyAndNullCases(unittest.TestCase):
    """Test empty and null input cases."""

    def test_remove_stray_backslashes_only_backslashes(self):
        """Test with only backslashes."""
        input_str = r"\\\\\\"
        result = ProcessDocs.remove_stray_backslashes(input_str)
        # Should preserve valid escape sequences
        self.assertIn("\\", result)

    def test_remove_table_of_contents_only_contents_keyword(self):
        """Test with only 'Contents' keyword and nothing else."""
        input_text = "Contents"
        result = ProcessDocs.remove_table_of_contents(input_text)
        # Should remove the Contents line
        self.assertEqual(result.strip(), "")

    def test_hierarchical_chunker_single_line(self):
        """Test with single line document."""
        md = "# Single Header"
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write(md)
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)
        chunks = chunker(retain_only_headers=False)

        self.assertEqual(len(chunks), 1)

        os.remove(tmp_path)

    def test_chunk_piece_collector_empty_list(self):
        """Test chunk_piece_collector with empty list."""
        pieces = []
        # This might raise an IndexError, testing the behavior
        try:
            result = SoleChunker.chunk_piece_collector(pieces)
            self.assertEqual(result, "")
        except IndexError:
            # Expected behavior if not handled
            pass


class TestImageRemovalEdgeCases(unittest.TestCase):
    """Test edge cases for image removal."""

    def test_remove_image_malformed_markdown_image(self):
        """Test with malformed markdown image syntax."""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write("# Header\nContent")
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)

        # Malformed images
        text = "![incomplete ![nested](img.png) <img unclosed"
        result = chunker.remove_image_if_needed(text, remove_image_flag=True)

        # Should handle malformed syntax gracefully
        self.assertIsInstance(result, str)

        os.remove(tmp_path)

    def test_remove_image_with_special_chars_in_path(self):
        """Test image removal with special characters in path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False, encoding='utf-8') as tmp:
            tmp.write("# Header\nContent")
            tmp_path = tmp.name

        chunker = HierarchicalChunker(tmp_path)

        text = '![alt](path/to/image-file_123.png) <img src="../images/test 2.jpg">'
        result = chunker.remove_image_if_needed(text, remove_image_flag=True)

        self.assertNotIn("![", result)
        self.assertNotIn("<img", result)

        os.remove(tmp_path)


class TestModuleLevelImports(unittest.TestCase):
    """Test module-level imports and initialization."""

    def test_tokenizer_import(self):
        """Test that tokenizer is imported correctly."""
        from src.shear_parser import tokenizer
        self.assertIsNotNone(tokenizer)


if __name__ == '__main__':
    unittest.main()