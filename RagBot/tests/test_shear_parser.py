import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
from pathlib import Path

# Import the classes to be tested
from src.shear_parser import ProcessDocs, HierarchicalChunker, SoleChunker, convert_word_to_markdown

class TestProcessDocs(unittest.TestCase):

    def test_remove_stray_backslashes(self):
        """Test the removal of stray backslashes."""
        input_str = r"this is a test with a stray \ and another one \. Keep \\n and \\t."
        expected_str = r"this is a test with a stray  and another one . Keep \\n and \\t."
        self.assertEqual(ProcessDocs.remove_stray_backslashes(input_str), expected_str)

    def test_remove_table_of_contents(self):
        """Test the removal of the table of contents."""
        input_text = "Contents\n[Chapter 1](#_Toc123)\n\n# Chapter 1\nSome content."
        expected_text = "# Chapter 1\nSome content."
        self.assertEqual(ProcessDocs.remove_table_of_contents(input_text).strip(), expected_text)

    @patch('src.shear_parser.MarkItDown')
    def test_process_doc(self, mock_markitdown):
        """Test the main document processing function."""
        # Create a dummy docx file
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

class TestChunkers(unittest.TestCase):

    def setUp(self):
        """Create a dummy markdown file for testing."""
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
        """Remove the dummy markdown file."""
        os.remove(self.md_file_path)

    def test_hierarchical_chunker(self):
        """Test the HierarchicalChunker."""
        chunker = HierarchicalChunker(self.md_file_path)
        chunks = chunker(retain_only_headers=False)

        self.assertIsInstance(chunks, list)
        self.assertIsInstance(chunks[0], dict)
        # Based on the md_content, we expect 2 chunks
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0][1], '# Level 1\nContent 1\n')
        self.assertEqual(chunks[0][2], '## Level 2\nContent 2\n')

    @patch('src.shear_parser.AutoTokenizer.from_pretrained')
    def test_sole_chunker(self, mock_tokenizer):
        """Test the SoleChunker."""
        # Mock the tokenizer to avoid downloading it
        mock_tokenizer.return_value = MagicMock()
        
        chunker = SoleChunker(self.md_file_path)
        chunks = chunker()

        self.assertIsInstance(chunks, list)
        # The number of chunks will depend on the logic, but it should be a list of strings
        self.assertIsInstance(chunks[0], str)

class TestMarkdownConversion(unittest.TestCase):

    @patch('src.shear_parser.ProcessDocs')
    def test_convert_word_to_markdown(self, mock_process_docs):
        """Test the Word to Markdown conversion function."""
        # Mock the ProcessDocs class
        mock_processor_instance = MagicMock()
        mock_processor_instance.process_doc.return_value = "# Mocked Markdown"
        mock_process_docs.return_value = mock_processor_instance

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a dummy docx file
            docx_path = Path(tmpdir) / "test.docx"
            with open(docx_path, "w") as f:
                f.write("dummy")

            output_dir = Path(tmpdir) / "output"
            results = convert_word_to_markdown([docx_path], str(output_dir))

            self.assertIn(str(docx_path), results)
            self.assertEqual(results[str(docx_path)]["status"], "success")
            
            output_md_path = output_dir / "test.md"
            self.assertTrue(output_md_path.exists())
            with open(output_md_path, "r") as f:
                content = f.read()
            self.assertEqual(content, "# Mocked Markdown")

if __name__ == '__main__':
    unittest.main()
