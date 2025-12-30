"""
Ingestion orchestrator - High-level API for data ingestion operations.

This module provides a simple interface for common ingestion workflows.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

from ..storage.raw_storage import RawDataStore
from ..storage.metadata import SourceType, IngestionRecord
from .slack_ingestion import SlackIngestion
from .confluence_ingestion import ConfluenceIngestion
from .document_ingestion import DocumentUploadIngestion
from .processor import DocumentProcessor
from .vector_manager import VectorStoreManager
from .logging_config import setup_ingestion_logging, get_logger

logger = get_logger(__name__)


class IngestionOrchestrator:
    """
    High-level orchestrator for data ingestion workflows.
    
    Simplifies common operations and provides unified interface.
    """
    
    def __init__(
        self,
        base_path: str = "data",
        vectorstore_path: str = "data/vectorstore",
        chunk_size: int = 700,
        chunk_overlap: int = 100,
        log_level: str = "INFO"
    ):
        """
        Initialize ingestion orchestrator.
        
        Args:
            base_path: Base directory for data storage
            vectorstore_path: Path to vector store
            chunk_size: Text chunk size
            chunk_overlap: Chunk overlap size
            log_level: Logging level
        """
        # Setup logging
        setup_ingestion_logging(log_level=log_level)
        
        # Initialize components
        self.storage = RawDataStore(base_path=base_path)
        self.processor = DocumentProcessor(
            storage=self.storage,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.vector_manager = VectorStoreManager(
            storage=self.storage,
            processor=self.processor,
            vectorstore_path=vectorstore_path
        )
        
        # Initialize source-specific ingestors
        slack_token = os.getenv("SLACK_BOT_TOKEN")
        self.slack = SlackIngestion(self.storage, slack_token)
        
        confluence_url = os.getenv("CONFLUENCE_URL")
        confluence_user = os.getenv("CONFLUENCE_USERNAME")
        confluence_token = os.getenv("CONFLUENCE_API_TOKEN")
        self.confluence = ConfluenceIngestion(
            self.storage,
            confluence_url,
            confluence_user,
            confluence_token
        )
        
        self.documents = DocumentUploadIngestion(self.storage)
        
        logger.info("IngestionOrchestrator initialized")
    
    # =================================================================
    # SLACK OPERATIONS
    # =================================================================
    
    def ingest_slack_export(self, export_path: str) -> IngestionRecord:
        """
        Ingest Slack export and index to vector store.
        
        Args:
            export_path: Path to Slack export directory
        
        Returns:
            IngestionRecord
        """
        logger.info(f"Starting Slack export ingestion: {export_path}")
        
        # Ingest raw data
        record = self.slack.ingest_export(export_path)
        
        logger.info(f"Slack ingestion complete: {record.documents_ingested} documents")
        
        return record
    
    def ingest_slack_channel(
        self,
        channel_id: str,
        days_history: int = 30,
        auto_index: bool = False
    ) -> IngestionRecord:
        """
        Ingest Slack channel via API.
        
        Args:
            channel_id: Slack channel ID
            days_history: Days of history to retrieve
            auto_index: Automatically add to vector index
        
        Returns:
            IngestionRecord
        """
        logger.info(f"Starting Slack channel ingestion: {channel_id}")
        
        record = self.slack.ingest_channel_api(channel_id, days_history)
        
        logger.info(f"Slack channel ingestion complete: {record.documents_ingested} documents")
        
        return record
    
    # =================================================================
    # CONFLUENCE OPERATIONS
    # =================================================================
    
    def ingest_confluence_space(
        self,
        space_key: str,
        limit: int = 500,
        auto_index: bool = False
    ) -> IngestionRecord:
        """
        Ingest Confluence space.
        
        Args:
            space_key: Confluence space key
            limit: Maximum pages to retrieve
            auto_index: Automatically add to vector index
        
        Returns:
            IngestionRecord
        """
        logger.info(f"Starting Confluence space ingestion: {space_key}")
        
        record = self.confluence.ingest_space(space_key, limit)
        
        logger.info(f"Confluence ingestion complete: {record.documents_ingested} documents")
        
        return record
    
    def ingest_confluence_page(
        self,
        page_id: str,
        auto_index: bool = False
    ) -> IngestionRecord:
        """
        Ingest single Confluence page.
        
        Args:
            page_id: Confluence page ID
            auto_index: Automatically add to vector index
        
        Returns:
            IngestionRecord
        """
        logger.info(f"Starting Confluence page ingestion: {page_id}")
        
        record = self.confluence.ingest_page(page_id)
        
        logger.info("Confluence page ingestion complete")
        
        return record
    
    # =================================================================
    # DOCUMENT UPLOAD OPERATIONS
    # =================================================================
    
    def ingest_file(
        self,
        file_path: str,
        uploaded_by: Optional[str] = None,
        auto_index: bool = False
    ) -> IngestionRecord:
        """
        Ingest uploaded file.
        
        Args:
            file_path: Path to file
            uploaded_by: User identifier
            auto_index: Automatically add to vector index
        
        Returns:
            IngestionRecord
        """
        logger.info(f"Starting file ingestion: {file_path}")
        
        record = self.documents.ingest_file(file_path, uploaded_by)
        
        logger.info("File ingestion complete")
        
        return record
    
    def ingest_files(
        self,
        file_paths: List[str],
        uploaded_by: Optional[str] = None,
        auto_index: bool = False
    ) -> IngestionRecord:
        """
        Ingest multiple files.
        
        Args:
            file_paths: List of file paths
            uploaded_by: User identifier
            auto_index: Automatically add to vector index
        
        Returns:
            Aggregated IngestionRecord
        """
        logger.info(f"Starting batch file ingestion: {len(file_paths)} files")
        
        record = self.documents.ingest_files(file_paths, uploaded_by)
        
        logger.info(f"Batch ingestion complete: {record.documents_ingested} succeeded, {record.documents_failed} failed")
        
        return record
    
    # =================================================================
    # VECTOR INDEXING OPERATIONS
    # =================================================================
    
    def initialize_vector_index(self) -> Dict[str, Any]:
        """
        Create initial vector index from all raw data.
        
        Returns:
            Index creation report
        """
        logger.info("Initializing vector index from all raw data")
        
        result = self.vector_manager.initialize_index()
        
        logger.info(f"Vector index initialized: {result['document_count']} documents")
        
        return result
    
    def update_vector_index(self, batch_paths: List[str]) -> Dict[str, Any]:
        """
        Add new batches to existing vector index.
        
        Args:
            batch_paths: Paths to new data batches
        
        Returns:
            Update report
        """
        logger.info(f"Updating vector index with {len(batch_paths)} batches")
        
        result = self.vector_manager.update_index(batch_paths)
        
        logger.info(f"Vector index updated: +{result['added']} documents")
        
        return result
    
    def rebuild_vector_index(self, backup: bool = True) -> Dict[str, Any]:
        """
        Completely rebuild vector index.
        
        Args:
            backup: Create backup before rebuild
        
        Returns:
            Rebuild report
        """
        logger.warning("Rebuilding vector index (this may take time)")
        
        result = self.vector_manager.rebuild_index(backup=backup)
        
        logger.info("Vector index rebuilt successfully")
        
        return result
    
    def get_index_info(self) -> Dict[str, Any]:
        """
        Get vector index information.
        
        Returns:
            Index metadata
        """
        return self.vector_manager.get_index_info()
    
    # =================================================================
    # INGESTION HISTORY
    # =================================================================
    
    def get_ingestion_history(
        self,
        source_type: Optional[SourceType] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent ingestion history.
        
        Args:
            source_type: Optional filter by source type
            limit: Maximum records to return
        
        Returns:
            List of ingestion records
        """
        history = self.storage.get_ingestion_history(source_type)
        return history[:limit]
    
    def get_source_batches(self, source_type: SourceType) -> List[Dict[str, Any]]:
        """
        List all batches for a source type.
        
        Args:
            source_type: Source type to query
        
        Returns:
            List of batch metadata
        """
        return self.storage.list_batches(source_type)
