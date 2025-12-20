import re
import os
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import logging

# Core dependency for document conversion
try:
    from markitdown import MarkItDown
except ImportError:
    logging.error("MarkItDown library not found. Install with: pip install markitdown")
    raise ImportError("Please install markitdown: pip install markitdown")

@dataclass
class ChunkMetadata:
    """
    Comprehensive metadata for each chunk including hierarchical context.
    This metadata allows us to reconstruct the document's logical structure
    and provides rich context for downstream processing.
    """
    chunk_id: str
    hierarchy_path: List[str]  # Complete path from document root to current section
    level: int  # Depth in the hierarchy (1 for top-level, 2 for subsection, etc.)
    parent_headers: List[str]  # All ancestor headers leading to this chunk
    start_line: int
    end_line: int
    content_type: str  # 'header', 'content', 'table', 'list', etc.
    file_source: str
    word_count: int
    character_count: int
    
    def get_hierarchy_string(self) -> str:
        """Returns a human-readable hierarchy path like 'Chapter 1 > Section 1.1 > Subsection A'"""
        return " > ".join(self.hierarchy_path) if self.hierarchy_path else "Root"

@dataclass
class DocumentChunk:
    """
    A document chunk that maintains its hierarchical context.
    The key innovation here is that each chunk can reconstruct its full
    contextual meaning by including its ancestral headers.
    """
    content: str
    metadata: ChunkMetadata
    
    def get_contextual_content(self, include_hierarchy: bool = True) -> str:
        """
        Returns content with full hierarchical context prepended.
        This is the core feature that makes our chunks self-contained and meaningful.
        
        Args:
            include_hierarchy: Whether to include the full header hierarchy
        """
        if not include_hierarchy or not self.metadata.parent_headers:
            return self.content
        
        # Build the hierarchical context with proper markdown formatting
        context_lines = []
        
        # Add each level of the hierarchy with appropriate header depth
        for i, header in enumerate(self.metadata.parent_headers):
            header_level = "#" * (i + 1)  # Convert level to markdown header syntax
            context_lines.append(f"{header_level} {header}")
        
        # Add a separator line to distinguish context from actual content
        context_lines.append("")
        context_lines.append(self.content)
        
        return "\n".join(context_lines)
    
    def get_summary_info(self) -> Dict[str, Union[str, int]]:
        """Returns a summary of this chunk's key information"""
        return {
            "chunk_id": self.metadata.chunk_id,
            "hierarchy": self.metadata.get_hierarchy_string(),
            "level": self.metadata.level,
            "word_count": self.metadata.word_count,
            "character_count": self.metadata.character_count,
            "content_preview": self.content[:100] + "..." if len(self.content) > 100 else self.content
        }

class EnhancedMarkdownConverter:
    """
    Wrapper around MarkItDown that provides additional processing capabilities
    for better hierarchical structure preservation.
    """
    
    def __init__(self):
        """
        Initialize the converter with MarkItDown as the core engine.
        We'll enhance its output with additional structure detection.
        """
        self.markitdown = MarkItDown()
        self.supported_extensions = {
            # Document formats
            '.pdf', '.docx', '.doc', '.pptx', '.ppt',
            # Spreadsheet formats  
            '.xlsx', '.xls', '.csv',
            # Web formats
            '.html', '.htm', '.xml',
            # Text formats
            '.txt', '.md', '.markdown', '.rtf',
            # Image formats (MarkItDown can extract text from images)
            '.png', '.jpg', '.jpeg', '.gif', '.bmp',
            # Audio formats (MarkItDown can transcribe)
            '.mp3', '.wav', '.m4a',
            # Other formats
            '.json', '.yaml', '.yml'
        }
    
    def convert_to_markdown(self, file_path: str) -> str:
        """
        Convert any supported file to markdown using MarkItDown.
        This is our Phase 1 processing - format normalization.
        
        Args:
            file_path: Path to the file to convert
            
        Returns:
            Clean markdown content with preserved structure
        """
        file_path = Path(file_path)
        
        # Validate file existence and format support
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        try:
            # Use MarkItDown to perform the conversion
            # This handles all the complex format-specific logic
            result = self.markitdown.convert(str(file_path))
            markdown_content = result.text_content
            
            # Post-process the markdown to ensure consistent structure
            enhanced_markdown = self._enhance_markdown_structure(markdown_content)
            
            logging.info(f"Successfully converted {file_path} to markdown ({len(enhanced_markdown)} characters)")
            return enhanced_markdown
            
        except Exception as e:
            logging.error(f"Failed to convert {file_path}: {str(e)}")
            raise RuntimeError(f"Conversion failed for {file_path}: {str(e)}")
    
    def _enhance_markdown_structure(self, markdown_content: str) -> str:
        """
        Post-process MarkItDown output to ensure optimal structure for chunking.
        This handles edge cases and normalizes the markdown format.
        """
        lines = markdown_content.split('\n')
        enhanced_lines = []
        
        for i, line in enumerate(lines):
            # Normalize header formatting - ensure single space after #
            if re.match(r'^#+', line):
                # Extract header level and content
                header_match = re.match(r'^(#+)\s*(.+)', line)
                if header_match:
                    level_marks = header_match.group(1)
                    header_text = header_match.group(2).strip()
                    enhanced_lines.append(f"{level_marks} {header_text}")
                else:
                    enhanced_lines.append(line)
            else:
                enhanced_lines.append(line)
        
        # Join lines and clean up excessive whitespace
        enhanced_content = '\n'.join(enhanced_lines)
        
        # Remove excessive blank lines (more than 2 consecutive)
        enhanced_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', enhanced_content)
        
        return enhanced_content.strip()
    
    def get_conversion_info(self, file_path: str) -> Dict[str, Union[str, bool]]:
        """
        Get information about whether a file can be converted and what type it is.
        This is useful for batch processing and error handling.
        """
        file_path = Path(file_path)
        
        return {
            "file_path": str(file_path),
            "file_extension": file_path.suffix.lower(),
            "is_supported": file_path.suffix.lower() in self.supported_extensions,
            "exists": file_path.exists(),
            "file_size": file_path.stat().st_size if file_path.exists() else 0,
            "estimated_conversion_time": self._estimate_conversion_time(file_path)
        }
    
    def _estimate_conversion_time(self, file_path: Path) -> str:
        """
        Provide a rough estimate of conversion time based on file size and type.
        This helps users understand what to expect for large files.
        """
        if not file_path.exists():
            return "Unknown - file not found"
        
        file_size = file_path.stat().st_size
        extension = file_path.suffix.lower()
        
        # Rough estimates based on file type and size
        if extension in ['.txt', '.md', '.markdown']:
            return "< 1 second"
        elif extension in ['.pdf', '.docx', '.html']:
            if file_size < 1_000_000:  # < 1MB
                return "1-5 seconds"
            elif file_size < 10_000_000:  # < 10MB
                return "5-30 seconds"
            else:
                return "30+ seconds"
        elif extension in ['.mp3', '.wav', '.m4a']:
            return "Variable (depends on audio length)"
        else:
            return "5-15 seconds"

class AdvancedHierarchicalChunker:
    """
    Advanced chunking system that creates hierarchically-aware chunks from markdown.
    This is our Phase 2 processing - intelligent content segmentation.
    """
    
    def __init__(self, max_chunk_size: int = 1000, overlap_size: int = 100, 
                 respect_section_boundaries: bool = True):
        """
        Initialize the chunker with configurable parameters.
        
        Args:
            max_chunk_size: Maximum characters per chunk
            overlap_size: Characters to overlap between adjacent chunks
            respect_section_boundaries: Whether to avoid splitting sections across chunks
        """
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        self.respect_section_boundaries = respect_section_boundaries
        
        # Regex patterns for different markdown elements
        self.header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        self.list_pattern = re.compile(r'^[\s]*[-*+]\s+(.+)$', re.MULTILINE)
        self.table_pattern = re.compile(r'^\|(.+)\|$', re.MULTILINE)
        self.code_block_pattern = re.compile(r'^```[\s\S]*?^```$', re.MULTILINE)
    
    def chunk_markdown(self, markdown_content: str, file_source: str = "") -> List[DocumentChunk]:
        """
        The main chunking method that processes markdown content into hierarchical chunks.
        This is where the magic happens - we preserve document structure while
        creating manageable chunks for downstream processing.
        
        Args:
            markdown_content: The markdown content to chunk
            file_source: Original file path for traceability
            
        Returns:
            List of DocumentChunk objects with hierarchical context
        """
        if not markdown_content.strip():
            return []
        
        # Step 1: Parse the document structure into a hierarchical tree
        document_tree = self._build_document_tree(markdown_content)
        
        # Step 2: Generate chunks that preserve hierarchical relationships
        chunks = self._generate_contextual_chunks(document_tree, file_source)
        
        # Step 3: Post-process chunks to ensure quality and consistency
        optimized_chunks = self._optimize_chunks(chunks)
        
        logging.info(f"Generated {len(optimized_chunks)} hierarchical chunks from {file_source}")
        return optimized_chunks
    
    def _build_document_tree(self, markdown_content: str) -> List[Dict]:
        """
        Parse markdown content into a hierarchical tree structure.
        This tree captures the logical organization of the document.
        
        The tree structure allows us to understand relationships between sections
        and ensure each chunk includes appropriate context from its ancestors.
        """
        lines = markdown_content.split('\n')
        tree = []
        hierarchy_stack = []  # Stack to track current position in hierarchy
        current_content = []
        current_content_type = 'text'
        
        for line_num, line in enumerate(lines):
            # Check if this line represents a structural element
            header_match = self.header_pattern.match(line)
            
            if header_match:
                # We've found a header - process any accumulated content first
                if current_content:
                    content_text = '\n'.join(current_content).strip()
                    if content_text:
                        tree.append({
                            'type': 'content',
                            'content': content_text,
                            'content_type': current_content_type,
                            'hierarchy_path': [item['title'] for item in hierarchy_stack],
                            'line_start': line_num - len(current_content),
                            'line_end': line_num - 1,
                            'level': len(hierarchy_stack)
                        })
                    current_content = []
                
                # Process the header
                level = len(header_match.group(1))  # Count the # symbols
                title = header_match.group(2).strip()
                
                # Adjust hierarchy stack based on header level
                # This ensures we maintain proper nesting relationships
                hierarchy_stack = hierarchy_stack[:level-1]  # Remove deeper levels
                
                # Add current header to appropriate level
                header_info = {
                    'level': level,
                    'title': title,
                    'line_num': line_num
                }
                
                if len(hierarchy_stack) == level - 1:
                    hierarchy_stack.append(header_info)
                else:
                    # Handle inconsistent header levels (e.g., jumping from # to ###)
                    hierarchy_stack = hierarchy_stack[:level-1] + [header_info]
                
                # Add header to tree
                tree.append({
                    'type': 'header',
                    'level': level,
                    'title': title,
                    'hierarchy_path': [item['title'] for item in hierarchy_stack],
                    'line_num': line_num
                })
                
                current_content_type = 'text'  # Reset content type
            
            else:
                # This is content - determine what type and accumulate
                if self.table_pattern.match(line):
                    current_content_type = 'table'
                elif self.list_pattern.match(line):
                    current_content_type = 'list'
                elif line.strip().startswith('```'):
                    current_content_type = 'code'
                
                current_content.append(line)
        
        # Handle any remaining content at the end of the document
        if current_content:
            content_text = '\n'.join(current_content).strip()
            if content_text:
                tree.append({
                    'type': 'content',
                    'content': content_text,
                    'content_type': current_content_type,
                    'hierarchy_path': [item['title'] for item in hierarchy_stack],
                    'line_start': len(lines) - len(current_content),
                    'line_end': len(lines) - 1,
                    'level': len(hierarchy_stack)
                })
        
        return tree
    
    def _generate_contextual_chunks(self, document_tree: List[Dict], file_source: str) -> List[DocumentChunk]:
        """
        Generate chunks from the document tree, ensuring each chunk includes
        its full hierarchical context. This is the core innovation of our approach.
        """
        chunks = []
        chunk_counter = 0
        
        for node in document_tree:
            if node['type'] == 'content':
                content = node['content'].strip()
                if not content:
                    continue
                
                # Determine if we need to split this content into multiple chunks
                if len(content) <= self.max_chunk_size:
                    # Content fits in a single chunk
                    chunk_parts = [content]
                else:
                    # Split large content while preserving structure
                    chunk_parts = self._intelligently_split_content(content, node['content_type'])
                
                # Create chunks with hierarchical context
                for chunk_content in chunk_parts:
                    chunk_id = f"chunk_{chunk_counter:04d}"
                    chunk_counter += 1
                    
                    # Calculate content statistics
                    word_count = len(chunk_content.split())
                    char_count = len(chunk_content)
                    
                    # Create comprehensive metadata
                    metadata = ChunkMetadata(
                        chunk_id=chunk_id,
                        hierarchy_path=node['hierarchy_path'].copy(),
                        level=node['level'],
                        parent_headers=node['hierarchy_path'].copy(),
                        start_line=node['line_start'],
                        end_line=node['line_end'],
                        content_type=node['content_type'],
                        file_source=file_source,
                        word_count=word_count,
                        character_count=char_count
                    )
                    
                    # Create the chunk object
                    chunk = DocumentChunk(
                        content=chunk_content,
                        metadata=metadata
                    )
                    
                    chunks.append(chunk)
        
        return chunks
    
    def _intelligently_split_content(self, content: str, content_type: str) -> List[str]:
        """
        Split content intelligently based on its type and structure.
        Different content types require different splitting strategies.
        """
        if content_type == 'table':
            return self._split_table_content(content)
        elif content_type == 'list':
            return self._split_list_content(content)
        elif content_type == 'code':
            return self._split_code_content(content)
        else:
            return self._split_text_content(content)
    
    def _split_text_content(self, content: str) -> List[str]:
        """
        Split regular text content at natural boundaries (sentences, paragraphs).
        This preserves readability and meaning.
        """
        # First, try to split by paragraphs
        paragraphs = content.split('\n\n')
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # Check if adding this paragraph would exceed our limit
            potential_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph
            
            if len(potential_chunk) <= self.max_chunk_size:
                current_chunk = potential_chunk
            else:
                # Current chunk is full, start a new one
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Handle case where single paragraph is too long
                if len(paragraph) > self.max_chunk_size:
                    # Split by sentences
                    sentence_chunks = self._split_by_sentences(paragraph)
                    chunks.extend(sentence_chunks)
                    current_chunk = ""
                else:
                    current_chunk = paragraph
        
        # Add the final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return self._add_overlap_to_chunks(chunks)
    
    def _split_by_sentences(self, text: str) -> List[str]:
        """
        Split text by sentences when paragraph-level splitting isn't sufficient.
        """
        # Simple sentence splitting - could be enhanced with more sophisticated NLP
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            potential_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if len(potential_chunk) <= self.max_chunk_size:
                current_chunk = potential_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _split_table_content(self, content: str) -> List[str]:
        """
        Split table content by rows while preserving table structure.
        """
        lines = content.split('\n')
        header_lines = []
        data_lines = []
        
        # Separate header from data
        for i, line in enumerate(lines):
            if i < 2 or '|---' in line or '|:-' in line:
                header_lines.append(line)
            else:
                data_lines.append(line)
        
        # Calculate how many data rows we can fit per chunk
        header_size = len('\n'.join(header_lines))
        available_space = self.max_chunk_size - header_size - 100  # Buffer
        
        chunks = []
        current_rows = []
        current_size = 0
        
        for row in data_lines:
            if current_size + len(row) <= available_space:
                current_rows.append(row)
                current_size += len(row)
            else:
                # Create chunk with current rows
                if current_rows:
                    chunk_content = '\n'.join(header_lines + current_rows)
                    chunks.append(chunk_content)
                
                # Start new chunk
                current_rows = [row]
                current_size = len(row)
        
        # Add final chunk
        if current_rows:
            chunk_content = '\n'.join(header_lines + current_rows)
            chunks.append(chunk_content)
        
        return chunks
    
    def _split_list_content(self, content: str) -> List[str]:
        """
        Split list content by items while preserving list structure.
        """
        lines = content.split('\n')
        chunks = []
        current_chunk_lines = []
        current_size = 0
        
        for line in lines:
            if current_size + len(line) <= self.max_chunk_size:
                current_chunk_lines.append(line)
                current_size += len(line)
            else:
                if current_chunk_lines:
                    chunks.append('\n'.join(current_chunk_lines))
                current_chunk_lines = [line]
                current_size = len(line)
        
        if current_chunk_lines:
            chunks.append('\n'.join(current_chunk_lines))
        
        return chunks
    
    def _split_code_content(self, content: str) -> List[str]:
        """
        Split code content carefully to preserve syntax and meaning.
        """
        # For code blocks, we're more conservative about splitting
        if len(content) <= self.max_chunk_size:
            return [content]
        
        # Try to split by logical sections (functions, classes, etc.)
        lines = content.split('\n')
        chunks = []
        current_chunk_lines = []
        current_size = 0
        
        for line in lines:
            if current_size + len(line) <= self.max_chunk_size:
                current_chunk_lines.append(line)
                current_size += len(line)
            else:
                if current_chunk_lines:
                    chunks.append('\n'.join(current_chunk_lines))
                current_chunk_lines = [line]
                current_size = len(line)
        
        if current_chunk_lines:
            chunks.append('\n'.join(current_chunk_lines))
        
        return chunks
    
    def _add_overlap_to_chunks(self, chunks: List[str]) -> List[str]:
        """
        Add overlap between adjacent chunks to provide continuity.
        This helps downstream processing by providing additional context.
        """
        if len(chunks) <= 1 or self.overlap_size <= 0:
            return chunks
        
        overlapped_chunks = [chunks[0]]  # First chunk remains unchanged
        
        for i in range(1, len(chunks)):
            previous_chunk = chunks[i-1]
            current_chunk = chunks[i]
            
            # Get overlap from previous chunk
            overlap = self._extract_overlap(previous_chunk)
            
            # Combine overlap with current chunk
            if overlap:
                combined_chunk = overlap + "\n\n" + current_chunk
                overlapped_chunks.append(combined_chunk)
            else:
                overlapped_chunks.append(current_chunk)
        
        return overlapped_chunks
    
    def _extract_overlap(self, text: str) -> str:
        """
        Extract overlap content from the end of a chunk.
        We try to find natural boundaries for meaningful overlap.
        """
        if len(text) <= self.overlap_size:
            return text
        
        # Try to find sentence boundaries for natural overlap
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        overlap = ""
        for sentence in reversed(sentences):
            potential_overlap = sentence + " " + overlap if overlap else sentence
            if len(potential_overlap) <= self.overlap_size:
                overlap = potential_overlap
            else:
                break
        
        return overlap.strip()
    
    def _optimize_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """
        Post-process chunks to ensure optimal size and quality.
        This final step refines the chunking results.
        """
        optimized = []
        
        for chunk in chunks:
            # Skip empty chunks
            if not chunk.content.strip():
                continue
            
            # Skip chunks that are too small (unless they're the only content)
            if len(chunk.content) < 50 and len(chunks) > 1:
                # Try to merge with previous chunk if possible
                if optimized and len(optimized[-1].content) + len(chunk.content) <= self.max_chunk_size:
                    # Merge with previous chunk
                    previous_chunk = optimized[-1]
                    merged_content = previous_chunk.content + "\n\n" + chunk.content
                    
                    # Update metadata
                    updated_metadata = previous_chunk.metadata
                    updated_metadata.character_count = len(merged_content)
                    updated_metadata.word_count = len(merged_content.split())
                    updated_metadata.end_line = chunk.metadata.end_line
                    
                    # Create new merged chunk
                    merged_chunk = DocumentChunk(
                        content=merged_content,
                        metadata=updated_metadata
                    )
                    
                    optimized[-1] = merged_chunk
                    continue
            
            optimized.append(chunk)
        
        return optimized

class DocumentProcessor:
    """
    Main orchestrator class that coordinates the entire document processing pipeline.
    This class brings together format conversion and hierarchical chunking.
    """
    
    def __init__(self, max_chunk_size: int = 100000, overlap_size: int = 100, 
                 respect_section_boundaries: bool = True):
        """
        Initialize the document processor with configurable parameters.
        
        Args:
            max_chunk_size: Maximum characters per chunk
            overlap_size: Characters to overlap between chunks
            respect_section_boundaries: Whether to preserve section boundaries
        """
        self.converter = EnhancedMarkdownConverter()
        self.chunker = AdvancedHierarchicalChunker(
            max_chunk_size=max_chunk_size,
            overlap_size=overlap_size,
            respect_section_boundaries=respect_section_boundaries
        )
        
        # Setup logging for the processing pipeline
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def process_file(self, file_path: str) -> List[DocumentChunk]:
        """
        Process a single file through the complete pipeline:
        1. Convert to markdown (Phase 1)
        2. Chunk hierarchically (Phase 2)
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            List of hierarchical document chunks
        """
        start_time = time.time()
        
        try:
            logging.info(f"Starting processing of {file_path}")
            
            # Phase 1: Convert to markdown using MarkItDown
            markdown_content = self.converter.convert_to_markdown(file_path)
            
            if not markdown_content.strip():
                logging.warning(f"No content extracted from {file_path}")
                return []
            
            # Phase 2: Create hierarchical chunks
            chunks = self.chunker.chunk_markdown(markdown_content, file_path)
            
            processing_time = time.time() - start_time
            logging.info(f"Successfully processed {file_path}: {len(chunks)} chunks in {processing_time:.2f} seconds")
            
            return chunks
            
        except Exception as e:
            logging.error(f"Failed to process {file_path}: {str(e)}")
            raise
    
    def process_directory(self, directory_path: str, recursive: bool = True) -> Dict[str, List[DocumentChunk]]:
        """
        Process all supported files in a directory.
        
        Args:
            directory_path: Path to directory containing files
            recursive: Whether to process subdirectories
            
        Returns:
            Dictionary mapping file paths to their chunks
        """
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        results = {}
        file_pattern = "**/*" if recursive else "*"
        
        for file_path in directory.glob(file_pattern):
            if file_path.is_file():
                # Check if file is supported
                conversion_info = self.converter.get_conversion_info(str(file_path))
                
                if conversion_info['is_supported']:
                    try:
                        logging.info(f"Processing {file_path} (estimated time: {conversion_info['estimated_conversion_time']})")
                        chunks = self.process_file(str(file_path))
                        results[str(file_path)] = chunks
                    except Exception as e:
                        logging.error(f"Skipping {file_path} due to error: {e}")
                else:
                    logging.debug(f"Skipping unsupported file: {file_path}")
        
        logging.info(f"Processed {len(results)} files from {directory_path}")
        return results
    
    def export_chunks(self, chunks: List[DocumentChunk], output_format: str = 'json', 
                     include_contextual_content: bool = True) -> str:
        """
        Export chunks in various formats for downstream use.
        
        Args:
            chunks: List of chunks to export
            output_format: Format for export ('json', 'markdown', 'csv')
            include_contextual_content: Whether to include hierarchical context
            
        Returns:
            Formatted string representation of the chunks
        """
        if output_format == 'json':
            return self._export_as_json(chunks, include_contextual_content)
        elif output_format == 'markdown':
            return self._export_as_markdown(chunks, include_contextual_content)
        elif output_format == 'csv':
            return self._export_as_csv(chunks, include_contextual_content)
        else:
            raise ValueError(f"Unsupported export format: {output_format}")
    
    def _export_as_json(self, chunks: List[DocumentChunk], include_contextual: bool) -> str:
        """
        Export chunks as JSON format - ideal for programmatic processing.
        This format preserves all metadata and is perfect for feeding into
        vector databases, search engines, or other processing pipelines.
        """
        import json
        
        exported_data = {
            "metadata": {
                "total_chunks": len(chunks),
                "export_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "includes_contextual_content": include_contextual
            },
            "chunks": []
        }
        
        for chunk in chunks:
            chunk_data = {
                # Core chunk information
                "chunk_id": chunk.metadata.chunk_id,
                "content": chunk.content,
                "file_source": chunk.metadata.file_source,
                
                # Hierarchical context - this is what makes our chunks special
                "hierarchy_path": chunk.metadata.hierarchy_path,
                "parent_headers": chunk.metadata.parent_headers,
                "hierarchy_string": chunk.metadata.get_hierarchy_string(),
                "level": chunk.metadata.level,
                
                # Content statistics for downstream processing
                "word_count": chunk.metadata.word_count,
                "character_count": chunk.metadata.character_count,
                "content_type": chunk.metadata.content_type,
                
                # Location information for traceability
                "start_line": chunk.metadata.start_line,
                "end_line": chunk.metadata.end_line
            }
            
            # Add contextual content if requested
            if include_contextual:
                chunk_data["contextual_content"] = chunk.get_contextual_content()
            
            exported_data["chunks"].append(chunk_data)
        
        return json.dumps(exported_data, indent=2, ensure_ascii=False)
    
    def _export_as_markdown(self, chunks: List[DocumentChunk], include_contextual: bool) -> str:
        """
        Export chunks as a markdown document - great for human review and documentation.
        This format makes it easy to see how the hierarchical chunking worked
        and verify that the context preservation is working correctly.
        """
        output_lines = [
            "# Hierarchical Document Chunks",
            f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total chunks: {len(chunks)}",
            f"Contextual content included: {include_contextual}",
            "",
            "---",
            ""
        ]
        
        for i, chunk in enumerate(chunks, 1):
            # Chunk header with metadata
            output_lines.extend([
                f"## Chunk {i}: {chunk.metadata.chunk_id}",
                "",
                f"**Source:** {chunk.metadata.file_source}",
                f"**Hierarchy:** {chunk.metadata.get_hierarchy_string()}",
                f"**Level:** {chunk.metadata.level}",
                f"**Content Type:** {chunk.metadata.content_type}",
                f"**Size:** {chunk.metadata.word_count} words, {chunk.metadata.character_count} characters",
                f"**Lines:** {chunk.metadata.start_line}-{chunk.metadata.end_line}",
                ""
            ])
            
            # Show hierarchy path if it exists
            if chunk.metadata.parent_headers:
                output_lines.extend([
                    "**Hierarchical Context:**",
                    ""
                ])
                for level, header in enumerate(chunk.metadata.parent_headers, 1):
                    output_lines.append(f"{'  ' * (level-1)}{level}. {header}")
                output_lines.append("")
            
            # Include the actual content
            if include_contextual:
                output_lines.extend([
                    "### Contextual Content:",
                    "```markdown",
                    chunk.get_contextual_content(),
                    "```",
                    ""
                ])
            else:
                output_lines.extend([
                    "### Content:",
                    "```markdown",
                    chunk.content,
                    "```",
                    ""
                ])
            
            output_lines.extend(["---", ""])
        
        return "\n".join(output_lines)
    
    def _export_as_csv(self, chunks: List[DocumentChunk], include_contextual: bool) -> str:
        """
        Export chunks as CSV format - perfect for analysis in spreadsheet applications
        or for importing into data analysis tools like pandas, R, or Excel.
        """
        import csv
        from io import StringIO
        
        output = StringIO()
        
        # Define CSV headers - these represent all the key information about each chunk
        headers = [
            'chunk_id',
            'file_source', 
            'hierarchy_string',
            'level',
            'content_type',
            'word_count',
            'character_count',
            'start_line',
            'end_line',
            'content'
        ]
        
        if include_contextual:
            headers.append('contextual_content')
        
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow(headers)
        
        # Write chunk data
        for chunk in chunks:
            row = [
                chunk.metadata.chunk_id,
                chunk.metadata.file_source,
                chunk.metadata.get_hierarchy_string(),
                chunk.metadata.level,
                chunk.metadata.content_type,
                chunk.metadata.word_count,
                chunk.metadata.character_count,
                chunk.metadata.start_line,
                chunk.metadata.end_line,
                chunk.content.replace('\n', '\\n')  # Escape newlines for CSV
            ]
            
            if include_contextual:
                row.append(chunk.get_contextual_content().replace('\n', '\\n'))
            
            writer.writerow(row)
        
        return output.getvalue()
    
    def get_processing_stats(self, chunks: List[DocumentChunk]) -> Dict[str, Union[int, float, str]]:
        """
        Generate comprehensive statistics about the chunking results.
        This helps you understand how well the hierarchical chunking worked
        and identify any potential issues or optimizations.
        """
        if not chunks:
            return {"error": "No chunks to analyze"}
        
        # Calculate basic statistics
        total_chunks = len(chunks)
        total_words = sum(chunk.metadata.word_count for chunk in chunks)
        total_characters = sum(chunk.metadata.character_count for chunk in chunks)
        
        # Analyze chunk sizes
        chunk_sizes = [chunk.metadata.character_count for chunk in chunks]
        avg_chunk_size = sum(chunk_sizes) / len(chunk_sizes)
        min_chunk_size = min(chunk_sizes)
        max_chunk_size = max(chunk_sizes)
        
        # Analyze hierarchy distribution
        hierarchy_levels = [chunk.metadata.level for chunk in chunks]
        max_hierarchy_depth = max(hierarchy_levels) if hierarchy_levels else 0
        
        # Count chunks by level
        level_distribution = {}
        for level in hierarchy_levels:
            level_distribution[level] = level_distribution.get(level, 0) + 1
        
        # Analyze content types
        content_types = [chunk.metadata.content_type for chunk in chunks]
        content_type_distribution = {}
        for content_type in content_types:
            content_type_distribution[content_type] = content_type_distribution.get(content_type, 0) + 1
        
        # Find unique source files
        source_files = set(chunk.metadata.file_source for chunk in chunks)
        
        return {
            "total_chunks": total_chunks,
            "total_words": total_words,
            "total_characters": total_characters,
            "average_chunk_size_chars": round(avg_chunk_size, 2),
            "min_chunk_size_chars": min_chunk_size,
            "max_chunk_size_chars": max_chunk_size,
            "max_hierarchy_depth": max_hierarchy_depth,
            "hierarchy_level_distribution": level_distribution,
            "content_type_distribution": content_type_distribution,
            "unique_source_files": len(source_files),
            "source_files": list(source_files)
        }


# Import time module for timestamp functionality
import time


def get_document_chunks(file_path: str) -> List[DocumentChunk]:
    """
    Initializes the processor, processes a single document file,
    and returns the generated hierarchical chunks.

    This function serves as a straightforward interface to the chunking system,
    making it easy to get chunks from a file to inspect their quality.

    Args:
        file_path: The full path to the .docx or other supported document.

    Returns:
        A list of DocumentChunk objects, or an empty list if an error occurs.
    """
    # 1. Initialize the main document processor with desired settings.
    # These settings can be fine-tuned to adjust the chunking behavior.
    processor = DocumentProcessor(
        max_chunk_size=10000,
        overlap_size=150,
        respect_section_boundaries=True
    )

    # 2. Process the file using the processor's main method.
    # This handles both the conversion to markdown and the hierarchical chunking.
    try:
        logging.info(f"Starting to process and chunk the document at: {file_path}")
        
        # The process_file method returns a list of DocumentChunk objects.
        chunks = processor.process_file(file_path)
        
        logging.info(f"Successfully generated {len(chunks)} chunks for {file_path}.")
        return chunks
        
    except FileNotFoundError:
        logging.error(f"Error: The file was not found at the specified path: {file_path}")
        return []
    except Exception as e:
        # Catch any other exceptions that might occur during the complex processing pipeline.
        logging.error(f"An unexpected error occurred while processing {file_path}: {e}")
        return []


# # Example usage and comprehensive testing framework
# if __name__ == "__main__":
#     """
#     This example demonstrates the complete hierarchical chunking pipeline.
#     Think of this as a complete tutorial on how to use the system effectively.
#     """
    
#     # Setup comprehensive logging to track the processing pipeline
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(levelname)s - %(message)s',
#         handlers=[
#             logging.FileHandler('chunking_process.log'),
#             logging.StreamHandler()
#         ]
#     )
    
#     # Initialize the document processor with custom parameters
#     # These parameters control the balance between chunk size and context preservation
#     processor = DocumentProcessor(
#         max_chunk_size=1000,  # Smaller chunks for better granularity
#         overlap_size=100,    # Overlap to maintain continuity
#         respect_section_boundaries=True  # Preserve document structure
#     )
    
#     def demonstrate_single_file_processing():
#         """
#         Demonstrate processing a single file through the complete pipeline.
#         This shows how Phase 1 (conversion) and Phase 2 (chunking) work together.
#         """
#         print("\n=== Single File Processing Demo ===")
        
#         # You would replace this with an actual file path
#         sample_file = "sample_document.pdf"  # Could be any supported format
        
#         try:
#             # Process the file through the complete pipeline
#             chunks = processor.process_file(sample_file)
            
#             if chunks:
#                 print(f"Successfully generated {len(chunks)} hierarchical chunks")
                
#                 # Show detailed information about the first few chunks
#                 print("\n--- Sample Chunk Analysis ---")
#                 for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
#                     print(f"\nChunk {i+1}:")
#                     print(f"  ID: {chunk.metadata.chunk_id}")
#                     print(f"  Hierarchy: {chunk.metadata.get_hierarchy_string()}")
#                     print(f"  Level: {chunk.metadata.level}")
#                     print(f"  Size: {chunk.metadata.word_count} words")
#                     print(f"  Content preview: {chunk.content[:100]}...")
                    
#                     # Show how contextual content works
#                     contextual = chunk.get_contextual_content()
#                     if len(contextual) > len(chunk.content):
#                         print(f"  Contextual content adds {len(contextual) - len(chunk.content)} characters of hierarchy")
                
#                 # Generate and display processing statistics
#                 stats = processor.get_processing_stats(chunks)
#                 print(f"\n--- Processing Statistics ---")
#                 print(f"Total chunks: {stats['total_chunks']}")
#                 print(f"Average chunk size: {stats['average_chunk_size_chars']} characters")
#                 print(f"Hierarchy depth: {stats['max_hierarchy_depth']} levels")
#                 print(f"Content types: {list(stats['content_type_distribution'].keys())}")
                
#                 # Export in different formats to show versatility
#                 print(f"\n--- Export Examples ---")
                
#                 # JSON export (for programmatic use)
#                 json_export = processor.export_chunks(chunks, 'json', include_contextual_content=True)
#                 with open('chunks_export.json', 'w', encoding='utf-8') as f:
#                     f.write(json_export)
#                 print("✓ JSON export saved to 'chunks_export.json'")
                
#                 # Markdown export (for human review)
#                 md_export = processor.export_chunks(chunks, 'markdown', include_contextual_content=True)
#                 with open('chunks_export.md', 'w', encoding='utf-8') as f:
#                     f.write(md_export)
#                 print("✓ Markdown export saved to 'chunks_export.md'")
                
#                 # CSV export (for analysis)
#                 csv_export = processor.export_chunks(chunks, 'csv', include_contextual_content=False)
#                 with open('chunks_export.csv', 'w', encoding='utf-8') as f:
#                     f.write(csv_export)
#                 print("✓ CSV export saved to 'chunks_export.csv'")
                
#             else:
#                 print("No chunks were generated - check if the file contains processable content")
                
#         except FileNotFoundError:
#             print(f"Demo file '{sample_file}' not found. Create a sample file or modify the path.")
#         except Exception as e:
#             print(f"Processing failed: {e}")
    
#     def demonstrate_batch_processing():
#         """
#         Demonstrate processing multiple files in a directory.
#         This shows how the system scales to handle large document collections.
#         """
#         print("\n=== Batch Processing Demo ===")
        
#         documents_directory = "sample_documents"  # Directory containing various file types
        
#         try:
#             # Process all supported files in the directory
#             all_results = processor.process_directory(documents_directory, recursive=True)
            
#             if all_results:
#                 print(f"Processed {len(all_results)} files successfully")
                
#                 # Combine all chunks for analysis
#                 all_chunks = []
#                 for file_path, chunks in all_results.items():
#                     all_chunks.extend(chunks)
#                     print(f"  {file_path}: {len(chunks)} chunks")
                
#                 # Generate comprehensive statistics across all files
#                 combined_stats = processor.get_processing_stats(all_chunks)
#                 print(f"\n--- Combined Statistics ---")
#                 print(f"Total chunks across all files: {combined_stats['total_chunks']}")
#                 print(f"Total content: {combined_stats['total_words']} words")
#                 print(f"File types processed: {combined_stats['unique_source_files']}")
#                 print(f"Content type distribution: {combined_stats['content_type_distribution']}")
                
#                 # Export combined results
#                 combined_export = processor.export_chunks(all_chunks, 'json', include_contextual_content=True)
#                 with open('combined_chunks_export.json', 'w', encoding='utf-8') as f:
#                     f.write(combined_export)
#                 print("✓ Combined export saved to 'combined_chunks_export.json'")
                
#             else:
#                 print(f"No supported files found in '{documents_directory}'")
                
#         except FileNotFoundError:
#             print(f"Directory '{documents_directory}' not found. Create sample documents or modify the path.")
#         except Exception as e:
#             print(f"Batch processing failed: {e}")
    
#     def create_sample_markdown_for_testing():
#         """
#         Create a sample markdown file to demonstrate the hierarchical chunking capabilities.
#         This helps users understand what the system can do without needing their own files.
#         """
#         sample_content = """# Technical Documentation Guide

# This document demonstrates how hierarchical chunking preserves document structure and context.

# ## Introduction

# Document processing is a critical component of modern information systems. When we break documents into chunks for processing, we need to maintain the logical relationships that give meaning to the content.

# ### Why Hierarchical Chunking Matters

# Traditional chunking methods treat documents as flat sequences of text. This approach loses important structural information that helps readers understand context and meaning.

# ### Our Approach

# We use a two-phase process:
# 1. Convert documents to markdown format
# 2. Create chunks that preserve hierarchical relationships

# ## Implementation Details

# The system consists of several key components that work together to achieve intelligent document segmentation.

# ### Phase 1: Format Conversion

# We use MarkItDown as our foundation for converting various file formats into clean, structured markdown. This choice provides several advantages:

# - Robust handling of multiple file formats
# - Preservation of document structure
# - Consistent output format for processing

# #### Supported File Types

# The system supports a wide range of document formats:

# - PDF documents (.pdf)
# - Microsoft Word documents (.docx, .doc)
# - PowerPoint presentations (.pptx, .ppt)
# - HTML web pages (.html, .htm)
# - Plain text files (.txt)
# - Markdown files (.md, .markdown)

# ### Phase 2: Hierarchical Chunking

# Once we have clean markdown, we parse the document structure and create chunks that maintain their hierarchical context.

# #### Key Features

# Each chunk includes:
# - The actual content
# - Complete hierarchical path
# - Parent header information
# - Metadata for traceability

# ## Advanced Features

# The system includes several advanced capabilities for sophisticated document processing needs.

# ### Content Type Detection

# Different types of content require different chunking strategies:

# - **Tables**: Split by rows while preserving headers
# - **Lists**: Maintain list structure across chunks  
# - **Code blocks**: Preserve syntax and logical boundaries
# - **Regular text**: Split at natural sentence and paragraph boundaries

# ### Overlap Management

# Chunks include configurable overlap to provide continuity and additional context for downstream processing systems.

# ## Conclusion

# Hierarchical chunking represents a significant improvement over traditional text segmentation approaches. By preserving document structure and maintaining contextual relationships, we enable more sophisticated and accurate downstream processing.

# This approach is particularly valuable for:
# - Search and retrieval systems
# - Document analysis pipelines
# - Knowledge management systems
# - AI-powered document processing
# """
        
#         with open('sample_hierarchical_document.md', 'w', encoding='utf-8') as f:
#             f.write(sample_content)
        
#         print("Created sample document: 'sample_hierarchical_document.md'")
#         return 'sample_hierarchical_document.md'
    
#     # Run the demonstration
#     print("=== Hierarchical Document Chunking System Demo ===")
#     print("This demonstration shows how the system processes documents while preserving their logical structure.")
    
#     # Create a sample file for testing
#     sample_file = create_sample_markdown_for_testing()
    
#     # Process the sample file to show the system in action
#     try:
#         print(f"\nProcessing sample file: {sample_file}")
#         chunks = processor.process_file(sample_file)
        
#         if chunks:
#             print(f"\n✓ Generated {len(chunks)} hierarchical chunks")
            
#             # Show how hierarchical context works
#             print("\n--- Hierarchical Context Example ---")
#             for chunk in chunks[:2]:  # Show first 2 chunks
#                 print(f"\nChunk: {chunk.metadata.chunk_id}")
#                 print(f"Hierarchy: {chunk.metadata.get_hierarchy_string()}")
#                 print("Original content length:", len(chunk.content))
#                 print("Contextual content length:", len(chunk.get_contextual_content()))
#                 print("Context adds:", len(chunk.get_contextual_content()) - len(chunk.content), "characters")
                
#                 print("\nContextual content preview:")
#                 contextual = chunk.get_contextual_content()
#                 print(contextual[:200] + "..." if len(contextual) > 200 else contextual)
#                 print("-" * 50)
            
#             # Generate statistics
#             stats = processor.get_processing_stats(chunks)
#             print(f"\n--- Processing Statistics ---")
#             for key, value in stats.items():
#                 if key not in ['source_files']:  # Skip detailed file list
#                     print(f"{key}: {value}")
            
#             # Export examples
#             print(f"\n--- Creating Export Files ---")
            
#             # JSON export for programmatic use
#             json_output = processor.export_chunks(chunks, 'json', True)
#             with open('demo_chunks.json', 'w', encoding='utf-8') as f:
#                 f.write(json_output)
#             print("✓ JSON export: demo_chunks.json")
            
#             # Markdown export for human review  
#             md_output = processor.export_chunks(chunks, 'markdown', True)
#             with open('demo_chunks.md', 'w', encoding='utf-8') as f:
#                 f.write(md_output)
#             print("✓ Markdown export: demo_chunks.md")
            
#             print(f"\n🎉 Demo completed successfully!")
#             print("Check the generated files to see how hierarchical chunking preserves document structure.")
            
#     except Exception as e:
#         print(f"Demo failed: {e}")
#         logging.error(f"Demo error: {e}", exc_info=True)

# if __name__ == "__main__":
#     chunks = get_document_chunks("/home/user01/mj-workspace/Assistant-bot/knowledge_base/new-KB/Treasury_14040116.docx")
#     print("hello world")