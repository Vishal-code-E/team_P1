"""
Document upload ingestion module.

Supports PDF, Markdown, and plain text file uploads.
Handles file parsing, metadata extraction, and safe storage.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
import logging
from pypdf import PdfReader

from ..storage.raw_storage import RawDataStore
from ..storage.metadata import DocumentMetadata, IngestionRecord, SourceType
import uuid

logger = logging.getLogger(__name__)


class DocumentUploadIngestion:
    """
    Ingest uploaded documents (PDF, Markdown, Text).
    
    Handles:
    - PDF text extraction
    - Markdown preservation
    - Plain text files
    - Metadata attachment
    - Deduplication via content hashing
    """
    
    SUPPORTED_EXTENSIONS = {
        ".pdf": SourceType.PDF,
        ".md": SourceType.MARKDOWN,
        ".markdown": SourceType.MARKDOWN,
        ".txt": SourceType.TEXT,
    }
    
    def __init__(self, storage: RawDataStore):
        """
        Initialize document upload ingestion.
        
        Args:
            storage: RawDataStore instance
        """
        self.storage = storage
        logger.info("DocumentUploadIngestion initialized")
    
    def ingest_file(
        self,
        file_path: Union[str, Path],
        uploaded_by: Optional[str] = None,
        metadata_overrides: Optional[Dict[str, Any]] = None
    ) -> IngestionRecord:
        """
        Ingest a single uploaded file.
        
        Args:
            file_path: Path to the file
            uploaded_by: Optional user identifier
            metadata_overrides: Optional metadata to attach
        
        Returns:
            IngestionRecord with ingestion metrics
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Determine source type
        source_type = self._get_source_type(file_path)
        
        ingestion_id = f"upload_{source_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        record = IngestionRecord(
            source_type=source_type,
            ingestion_id=ingestion_id,
            started_at=datetime.now(),
            source_identifiers=[file_path.name]
        )
        
        try:
            # Create batch
            batch_path = self.storage.create_ingestion_batch(
                source_type=source_type,
                batch_name="uploads"
            )
            
            # Process based on type
            if source_type == SourceType.PDF:
                self._ingest_pdf(file_path, batch_path, uploaded_by, metadata_overrides)
            elif source_type in (SourceType.MARKDOWN, SourceType.TEXT):
                self._ingest_text_file(file_path, batch_path, uploaded_by, metadata_overrides, source_type)
            else:
                raise ValueError(f"Unsupported file type: {file_path.suffix}")
            
            record.documents_ingested = 1
            record.bytes_processed = file_path.stat().st_size
            record.status = "completed"
            record.completed_at = datetime.now()
            
            logger.info(f"Ingested file: {file_path.name} ({record.bytes_processed} bytes)")
            
        except Exception as e:
            record.status = "failed"
            record.error_message = str(e)
            record.documents_failed = 1
            record.completed_at = datetime.now()
            logger.error(f"File ingestion failed: {e}")
        
        finally:
            self.storage.log_ingestion(record)
        
        return record
    
    def ingest_files(
        self,
        file_paths: List[Union[str, Path]],
        uploaded_by: Optional[str] = None
    ) -> IngestionRecord:
        """
        Ingest multiple uploaded files.
        
        Args:
            file_paths: List of file paths
            uploaded_by: Optional user identifier
        
        Returns:
            Aggregated IngestionRecord
        """
        ingestion_id = f"upload_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        record = IngestionRecord(
            source_type=SourceType.UNKNOWN,  # Mixed types
            ingestion_id=ingestion_id,
            started_at=datetime.now()
        )
        
        for file_path in file_paths:
            try:
                file_record = self.ingest_file(file_path, uploaded_by)
                record.documents_ingested += file_record.documents_ingested
                record.documents_failed += file_record.documents_failed
                record.bytes_processed += file_record.bytes_processed
                record.source_identifiers.append(Path(file_path).name)
                
            except Exception as e:
                logger.error(f"Failed to ingest {file_path}: {e}")
                record.documents_failed += 1
        
        record.status = "completed" if record.documents_failed == 0 else "partial"
        record.completed_at = datetime.now()
        
        self.storage.log_ingestion(record)
        return record
    
    def ingest_bytes(
        self,
        filename: str,
        content: bytes,
        uploaded_by: Optional[str] = None,
        metadata_overrides: Optional[Dict[str, Any]] = None
    ) -> IngestionRecord:
        """
        Ingest file from bytes (for API uploads).
        
        Args:
            filename: Original filename
            content: File content as bytes
            uploaded_by: Optional user identifier
            metadata_overrides: Optional metadata to attach
        
        Returns:
            IngestionRecord with ingestion metrics
        """
        # Determine source type from filename
        ext = Path(filename).suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {ext}")
        
        source_type = self.SUPPORTED_EXTENSIONS[ext]
        
        ingestion_id = f"upload_{source_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        record = IngestionRecord(
            source_type=source_type,
            ingestion_id=ingestion_id,
            started_at=datetime.now(),
            source_identifiers=[filename]
        )
        
        try:
            # Create batch
            batch_path = self.storage.create_ingestion_batch(
                source_type=source_type,
                batch_name="uploads"
            )
            
            # Create metadata
            metadata = DocumentMetadata(
                source_type=source_type,
                source_id=f"upload_{uuid.uuid4().hex[:12]}",
                source_name=filename,
                ingested_at=datetime.now(),
                extra={
                    "uploaded_by": uploaded_by,
                    "original_filename": filename,
                    **(metadata_overrides or {})
                }
            )
            
            # Store binary file
            self.storage.store_binary_file(
                batch_path=batch_path,
                filename=filename,
                content=content,
                metadata=metadata
            )
            
            record.documents_ingested = 1
            record.bytes_processed = len(content)
            record.status = "completed"
            record.completed_at = datetime.now()
            
            logger.info(f"Ingested bytes as {filename} ({len(content)} bytes)")
            
        except Exception as e:
            record.status = "failed"
            record.error_message = str(e)
            record.documents_failed = 1
            record.completed_at = datetime.now()
            logger.error(f"Bytes ingestion failed: {e}")
        
        finally:
            self.storage.log_ingestion(record)
        
        return record
    
    def _get_source_type(self, file_path: Path) -> SourceType:
        """Determine source type from file extension."""
        ext = file_path.suffix.lower()
        
        if ext in self.SUPPORTED_EXTENSIONS:
            return self.SUPPORTED_EXTENSIONS[ext]
        
        raise ValueError(f"Unsupported file extension: {ext}")
    
    def _ingest_pdf(
        self,
        file_path: Path,
        batch_path: str,
        uploaded_by: Optional[str],
        metadata_overrides: Optional[Dict[str, Any]]
    ):
        """Ingest a PDF file."""
        try:
            # Read PDF
            with open(file_path, "rb") as f:
                content = f.read()
            
            # Extract text
            reader = PdfReader(file_path)
            
            # Extract metadata from PDF
            pdf_info = reader.metadata if reader.metadata else {}
            
            # Build extracted text
            pages_text = []
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if text.strip():
                    pages_text.append({
                        "page": page_num,
                        "text": text
                    })
            
            # Create document data
            doc_data = {
                "filename": file_path.name,
                "total_pages": len(reader.pages),
                "extracted_pages": len(pages_text),
                "pdf_metadata": {
                    "author": pdf_info.get("/Author", "Unknown"),
                    "title": pdf_info.get("/Title", file_path.stem),
                    "subject": pdf_info.get("/Subject", ""),
                    "creator": pdf_info.get("/Creator", "")
                },
                "pages": pages_text
            }
            
            # Create metadata
            metadata = DocumentMetadata(
                source_type=SourceType.PDF,
                source_id=f"upload_{uuid.uuid4().hex[:12]}",
                source_name=file_path.name,
                ingested_at=datetime.now(),
                author=pdf_info.get("/Author", uploaded_by),
                title=pdf_info.get("/Title", file_path.stem),
                extra={
                    "uploaded_by": uploaded_by,
                    "total_pages": len(reader.pages),
                    "file_size_bytes": len(content),
                    **(metadata_overrides or {})
                }
            )
            
            # Store as JSON (parsed content)
            self.storage.store_raw_document(
                batch_path=batch_path,
                document_id=file_path.stem,
                content=doc_data,
                metadata=metadata,
                file_extension="json"
            )
            
            # Also store original binary
            self.storage.store_binary_file(
                batch_path=batch_path,
                filename=file_path.name,
                content=content,
                metadata=metadata
            )
            
        except Exception as e:
            raise Exception(f"PDF processing failed: {e}")
    
    def _ingest_text_file(
        self,
        file_path: Path,
        batch_path: str,
        uploaded_by: Optional[str],
        metadata_overrides: Optional[Dict[str, Any]],
        source_type: SourceType
    ):
        """Ingest a text or markdown file."""
        try:
            # Read text content
            with open(file_path, "r", encoding="utf-8") as f:
                text_content = f.read()
            
            # Create document data
            doc_data = {
                "filename": file_path.name,
                "content": text_content,
                "encoding": "utf-8",
                "line_count": len(text_content.splitlines()),
                "char_count": len(text_content)
            }
            
            # Create metadata
            metadata = DocumentMetadata(
                source_type=source_type,
                source_id=f"upload_{uuid.uuid4().hex[:12]}",
                source_name=file_path.name,
                ingested_at=datetime.now(),
                title=file_path.stem,
                extra={
                    "uploaded_by": uploaded_by,
                    "file_size_bytes": file_path.stat().st_size,
                    **(metadata_overrides or {})
                }
            )
            
            # Store
            self.storage.store_raw_document(
                batch_path=batch_path,
                document_id=file_path.stem,
                content=doc_data,
                metadata=metadata,
                file_extension="json"
            )
            
        except UnicodeDecodeError:
            raise Exception(f"File encoding error - expected UTF-8")
        except Exception as e:
            raise Exception(f"Text file processing failed: {e}")
