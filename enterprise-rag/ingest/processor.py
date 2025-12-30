"""
Unified document processing pipeline.

Transforms raw data from any source into standardized, chunked documents
ready for vector indexing. Ensures consistent metadata flows through
the entire pipeline.

WHY METADATA IS CRITICAL:
1. Source Attribution: Enables "Retrieved from: #engineering, 2024-12-15"
2. Filtering: Allows queries like "search only Confluence pages from Q4"
3. Agent Reasoning: Verifies answer quality based on source reliability
4. Debugging: Traces bad answers back to specific source documents
5. Re-indexing: Rebuilds subsets without reprocessing everything
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

from ..storage.raw_storage import RawDataStore
from ..storage.metadata import SourceType, DocumentMetadata

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Process raw documents into chunked, metadata-enriched documents.
    
    This is the bridge between raw storage and vector indexing.
    """
    
    def __init__(
        self,
        storage: RawDataStore,
        chunk_size: int = 700,
        chunk_overlap: int = 100
    ):
        """
        Initialize document processor.
        
        Args:
            storage: RawDataStore instance
            chunk_size: Characters per chunk
            chunk_overlap: Overlap between chunks
        """
        self.storage = storage
        
        # Configure text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        logger.info(f"DocumentProcessor initialized (chunk_size={chunk_size})")
    
    def process_batch(self, batch_path: str) -> List[Document]:
        """
        Process all documents from a raw data batch.
        
        Args:
            batch_path: Path to batch directory
        
        Returns:
            List of processed, chunked Document objects
        """
        batch_dir = Path(batch_path)
        
        if not batch_dir.exists():
            raise ValueError(f"Batch directory not found: {batch_path}")
        
        # Load batch metadata
        meta_file = batch_dir / "metadata.json"
        if not meta_file.exists():
            raise ValueError(f"Batch metadata not found: {meta_file}")
        
        with open(meta_file, "r") as f:
            batch_meta = json.load(f)
        
        source_type = SourceType(batch_meta["source_type"])
        
        logger.info(f"Processing batch: {batch_dir.name} ({source_type.value})")
        
        # Process based on source type
        if source_type == SourceType.SLACK:
            return self._process_slack_batch(batch_dir)
        elif source_type == SourceType.CONFLUENCE:
            return self._process_confluence_batch(batch_dir)
        elif source_type == SourceType.PDF:
            return self._process_pdf_batch(batch_dir)
        elif source_type in (SourceType.MARKDOWN, SourceType.TEXT):
            return self._process_text_batch(batch_dir)
        else:
            raise ValueError(f"Unknown source type: {source_type}")
    
    def _process_slack_batch(self, batch_dir: Path) -> List[Document]:
        """Process Slack conversation threads."""
        documents = []
        
        # Find all thread JSON files
        for thread_file in batch_dir.glob("thread_*.json"):
            try:
                # Load thread data
                with open(thread_file, "r") as f:
                    thread_data = json.load(f)
                
                # Load metadata
                meta_file = thread_file.with_suffix(".meta.json")
                with open(meta_file, "r") as f:
                    metadata_dict = json.load(f)
                
                metadata = DocumentMetadata.from_dict(metadata_dict)
                
                # Build conversation text
                conversation_text = self._format_slack_conversation(thread_data)
                
                # Create document
                doc = Document(
                    page_content=conversation_text,
                    metadata=self._build_langchain_metadata(metadata, thread_data)
                )
                
                # Chunk if needed
                chunks = self.text_splitter.split_documents([doc])
                documents.extend(chunks)
                
                logger.debug(f"Processed Slack thread: {thread_data['thread_ts']} -> {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Failed to process {thread_file}: {e}")
        
        logger.info(f"Processed {len(documents)} chunks from Slack batch")
        return documents
    
    def _process_confluence_batch(self, batch_dir: Path) -> List[Document]:
        """Process Confluence pages."""
        documents = []
        
        # Find all page JSON files
        for page_file in batch_dir.glob("page_*.json"):
            try:
                # Load page data
                with open(page_file, "r") as f:
                    page_data = json.load(f)
                
                # Load metadata
                meta_file = page_file.with_suffix(".meta.json")
                with open(meta_file, "r") as f:
                    metadata_dict = json.load(f)
                
                metadata = DocumentMetadata.from_dict(metadata_dict)
                
                # Use text content
                text_content = page_data.get("text_content", "")
                
                if not text_content.strip():
                    logger.warning(f"Empty content in {page_file}")
                    continue
                
                # Add page header for context
                formatted_content = self._format_confluence_page(page_data)
                
                # Create document
                doc = Document(
                    page_content=formatted_content,
                    metadata=self._build_langchain_metadata(metadata, page_data)
                )
                
                # Chunk
                chunks = self.text_splitter.split_documents([doc])
                documents.extend(chunks)
                
                logger.debug(f"Processed Confluence page: {page_data['title']} -> {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Failed to process {page_file}: {e}")
        
        logger.info(f"Processed {len(documents)} chunks from Confluence batch")
        return documents
    
    def _process_pdf_batch(self, batch_dir: Path) -> List[Document]:
        """Process PDF documents."""
        documents = []
        
        # Find all PDF JSON files (parsed content)
        for pdf_file in batch_dir.glob("*.json"):
            if pdf_file.name == "metadata.json":
                continue
            
            try:
                # Load PDF data
                with open(pdf_file, "r") as f:
                    pdf_data = json.load(f)
                
                # Skip if not PDF structure
                if "pages" not in pdf_data:
                    continue
                
                # Load metadata
                meta_file = pdf_file.with_suffix(".meta.json")
                with open(meta_file, "r") as f:
                    metadata_dict = json.load(f)
                
                metadata = DocumentMetadata.from_dict(metadata_dict)
                
                # Combine all page text
                full_text = self._format_pdf_content(pdf_data)
                
                # Create document
                doc = Document(
                    page_content=full_text,
                    metadata=self._build_langchain_metadata(metadata, pdf_data)
                )
                
                # Chunk
                chunks = self.text_splitter.split_documents([doc])
                documents.extend(chunks)
                
                logger.debug(f"Processed PDF: {pdf_data['filename']} -> {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Failed to process {pdf_file}: {e}")
        
        logger.info(f"Processed {len(documents)} chunks from PDF batch")
        return documents
    
    def _process_text_batch(self, batch_dir: Path) -> List[Document]:
        """Process text/markdown files."""
        documents = []
        
        # Find all text JSON files
        for text_file in batch_dir.glob("*.json"):
            if text_file.name == "metadata.json":
                continue
            
            try:
                # Load text data
                with open(text_file, "r") as f:
                    text_data = json.load(f)
                
                # Skip if not text structure
                if "content" not in text_data:
                    continue
                
                # Load metadata
                meta_file = text_file.with_suffix(".meta.json")
                with open(meta_file, "r") as f:
                    metadata_dict = json.load(f)
                
                metadata = DocumentMetadata.from_dict(metadata_dict)
                
                content = text_data["content"]
                
                # Create document
                doc = Document(
                    page_content=content,
                    metadata=self._build_langchain_metadata(metadata, text_data)
                )
                
                # Chunk
                chunks = self.text_splitter.split_documents([doc])
                documents.extend(chunks)
                
                logger.debug(f"Processed text file: {text_data['filename']} -> {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Failed to process {text_file}: {e}")
        
        logger.info(f"Processed {len(documents)} chunks from text batch")
        return documents
    
    def _format_slack_conversation(self, thread_data: Dict) -> str:
        """Format Slack thread into readable conversation."""
        lines = [
            f"# Slack Conversation: #{thread_data['channel_name']}",
            f"Thread ID: {thread_data['thread_ts']}",
            f"Participants: {', '.join(thread_data.get('participants', []))}",
            "",
            "---",
            ""
        ]
        
        for msg in thread_data.get("messages", []):
            lines.append(f"[{msg['timestamp']}] {msg['user_name']}: {msg['text']}")
        
        return "\n".join(lines)
    
    def _format_confluence_page(self, page_data: Dict) -> str:
        """Format Confluence page with metadata header."""
        lines = [
            f"# {page_data['title']}",
            f"Space: {page_data['space_key']}",
            f"Path: {page_data.get('hierarchy_path', page_data['title'])}",
            f"Last Updated: {page_data['last_updated']} by {page_data['author']}",
            "",
            "---",
            "",
            page_data["text_content"]
        ]
        
        return "\n".join(lines)
    
    def _format_pdf_content(self, pdf_data: Dict) -> str:
        """Format PDF content with metadata."""
        lines = [
            f"# {pdf_data.get('pdf_metadata', {}).get('title', pdf_data['filename'])}",
            f"Author: {pdf_data.get('pdf_metadata', {}).get('author', 'Unknown')}",
            f"Pages: {pdf_data['total_pages']}",
            "",
            "---",
            ""
        ]
        
        for page in pdf_data.get("pages", []):
            lines.append(f"\n--- Page {page['page']} ---\n")
            lines.append(page["text"])
        
        return "\n".join(lines)
    
    def _build_langchain_metadata(
        self,
        doc_metadata: DocumentMetadata,
        source_data: Dict
    ) -> Dict[str, Any]:
        """
        Build LangChain-compatible metadata dictionary.
        
        This metadata flows through to the vector store and enables
        source attribution in retrieval.
        """
        metadata = {
            # Core identification
            "source": doc_metadata.source_name,
            "source_type": doc_metadata.source_type.value,
            "source_id": doc_metadata.source_id,
            
            # Temporal
            "ingested_at": doc_metadata.ingested_at.isoformat(),
        }
        
        # Optional fields
        if doc_metadata.source_timestamp:
            metadata["source_timestamp"] = doc_metadata.source_timestamp.isoformat()
        
        if doc_metadata.author:
            metadata["author"] = doc_metadata.author
        
        if doc_metadata.title:
            metadata["title"] = doc_metadata.title
        
        if doc_metadata.url:
            metadata["url"] = doc_metadata.url
        
        # Merge extra metadata
        metadata.update(doc_metadata.extra)
        
        return metadata
