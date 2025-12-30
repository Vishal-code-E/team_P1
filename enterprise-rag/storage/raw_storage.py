"""
Raw data storage layer.

This module manages persistent storage of raw, unprocessed data from all sources.
It ensures data preservation, prevents overwrites, and maintains a complete audit trail.

WHY RAW DATA MUST BE PRESERVED:
1. Re-indexing: Vector embeddings may need to be regenerated with different models
2. Processing changes: Chunking strategies or cleaning logic may evolve
3. Debugging: Original content helps diagnose pipeline issues
4. Compliance: Audit trails require immutable source data
5. Recovery: Corrupted vector stores can be rebuilt from raw data
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

from .metadata import SourceType, DocumentMetadata, IngestionRecord

logger = logging.getLogger(__name__)


class RawDataStore:
    """
    Manages raw data storage with source-aware organization.
    
    Directory structure:
        data/
            raw/
                slack/
                    YYYYMMDD_HHMMSS_{channel_name}/
                        metadata.json
                        {thread_ts}.json
                confluence/
                    YYYYMMDD_HHMMSS_{space_key}/
                        metadata.json
                        {page_id}.json
                uploads/
                    YYYYMMDD_HHMMSS/
                        metadata.json
                        {filename}.{ext}
                        {filename}.meta.json
            processed/
                {ingestion_id}/
                    documents.json
            ingestion_logs/
                {ingestion_id}.json
    """
    
    def __init__(self, base_path: str = "data"):
        """
        Initialize the raw data store.
        
        Args:
            base_path: Base directory for all data storage
        """
        self.base_path = Path(base_path)
        self.raw_path = self.base_path / "raw"
        self.processed_path = self.base_path / "processed"
        self.logs_path = self.base_path / "ingestion_logs"
        
        # Create directory structure
        self._initialize_directories()
    
    def _initialize_directories(self):
        """Create the storage directory structure."""
        for source_type in SourceType:
            if source_type != SourceType.UNKNOWN:
                (self.raw_path / source_type.value).mkdir(parents=True, exist_ok=True)
        
        self.processed_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized data storage at {self.base_path}")
    
    def create_ingestion_batch(self, source_type: SourceType, batch_name: Optional[str] = None) -> str:
        """
        Create a new batch directory for an ingestion run.
        
        Args:
            source_type: Type of data source
            batch_name: Optional human-readable name (e.g., channel name, space key)
        
        Returns:
            Batch directory path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if batch_name:
            # Sanitize batch name for filesystem
            safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in batch_name)
            batch_dir = f"{timestamp}_{safe_name}"
        else:
            batch_dir = timestamp
        
        batch_path = self.raw_path / source_type.value / batch_dir
        batch_path.mkdir(parents=True, exist_ok=True)
        
        # Create metadata file
        metadata = {
            "source_type": source_type.value,
            "batch_name": batch_name,
            "created_at": datetime.now().isoformat(),
            "documents": []
        }
        
        with open(batch_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Created ingestion batch: {batch_path}")
        return str(batch_path)
    
    def store_raw_document(
        self,
        batch_path: str,
        document_id: str,
        content: Any,
        metadata: DocumentMetadata,
        file_extension: str = "json"
    ) -> str:
        """
        Store a raw document with its metadata.
        
        Args:
            batch_path: Path to the batch directory
            document_id: Unique identifier for this document
            content: Raw content (will be JSON-serialized if dict/list)
            metadata: Document metadata
            file_extension: File extension (default: json)
        
        Returns:
            Path to stored document
        """
        batch_dir = Path(batch_path)
        
        # Sanitize document ID for filename
        safe_id = "".join(c if c.isalnum() or c in "-_." else "_" for c in document_id)
        
        # Store content
        if file_extension == "json" and isinstance(content, (dict, list)):
            content_path = batch_dir / f"{safe_id}.json"
            with open(content_path, "w") as f:
                json.dump(content, f, indent=2)
        else:
            content_path = batch_dir / f"{safe_id}.{file_extension}"
            if isinstance(content, str):
                with open(content_path, "w") as f:
                    f.write(content)
            else:
                with open(content_path, "wb") as f:
                    f.write(content)
        
        # Store metadata alongside
        meta_path = batch_dir / f"{safe_id}.meta.json"
        with open(meta_path, "w") as f:
            json.dump(metadata.to_dict(), f, indent=2)
        
        # Update batch metadata
        batch_meta_path = batch_dir / "metadata.json"
        with open(batch_meta_path, "r") as f:
            batch_meta = json.load(f)
        
        batch_meta["documents"].append({
            "id": document_id,
            "filename": content_path.name,
            "stored_at": datetime.now().isoformat()
        })
        
        with open(batch_meta_path, "w") as f:
            json.dump(batch_meta, f, indent=2)
        
        logger.debug(f"Stored document: {content_path}")
        return str(content_path)
    
    def store_binary_file(
        self,
        batch_path: str,
        filename: str,
        content: bytes,
        metadata: DocumentMetadata
    ) -> str:
        """
        Store a binary file (PDF, images, etc.) with metadata.
        
        Args:
            batch_path: Path to the batch directory
            filename: Original filename
            content: Binary content
            metadata: Document metadata
        
        Returns:
            Path to stored file
        """
        batch_dir = Path(batch_path)
        
        # Use hash to detect duplicates
        content_hash = hashlib.sha256(content).hexdigest()[:16]
        
        # Preserve original extension
        ext = Path(filename).suffix
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in Path(filename).stem)
        
        file_path = batch_dir / f"{safe_name}_{content_hash}{ext}"
        
        # Store file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Store metadata
        meta_path = batch_dir / f"{safe_name}_{content_hash}.meta.json"
        meta_dict = metadata.to_dict()
        meta_dict["original_filename"] = filename
        meta_dict["content_hash"] = content_hash
        meta_dict["size_bytes"] = len(content)
        
        with open(meta_path, "w") as f:
            json.dump(meta_dict, f, indent=2)
        
        logger.info(f"Stored binary file: {file_path} ({len(content)} bytes)")
        return str(file_path)
    
    def log_ingestion(self, record: IngestionRecord):
        """
        Log an ingestion operation for auditing.
        
        Args:
            record: Ingestion record to log
        """
        log_path = self.logs_path / f"{record.ingestion_id}.json"
        
        with open(log_path, "w") as f:
            f.write(record.to_json())
        
        logger.info(f"Logged ingestion: {record.ingestion_id} ({record.status})")
    
    def get_ingestion_history(self, source_type: Optional[SourceType] = None) -> List[IngestionRecord]:
        """
        Retrieve ingestion history, optionally filtered by source type.
        
        Args:
            source_type: Optional filter by source type
        
        Returns:
            List of ingestion records
        """
        records = []
        
        for log_file in self.logs_path.glob("*.json"):
            with open(log_file, "r") as f:
                data = json.load(f)
                
            if source_type is None or data["source_type"] == source_type.value:
                records.append(data)
        
        # Sort by started_at descending
        records.sort(key=lambda x: x["started_at"], reverse=True)
        return records
    
    def list_batches(self, source_type: SourceType) -> List[Dict[str, Any]]:
        """
        List all ingestion batches for a source type.
        
        Args:
            source_type: Type of data source
        
        Returns:
            List of batch metadata
        """
        source_dir = self.raw_path / source_type.value
        batches = []
        
        for batch_dir in sorted(source_dir.iterdir(), reverse=True):
            if batch_dir.is_dir():
                meta_file = batch_dir / "metadata.json"
                if meta_file.exists():
                    with open(meta_file, "r") as f:
                        batches.append(json.load(f))
        
        return batches
