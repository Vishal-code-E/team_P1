"""
Confluence data ingestion module.

Supports Confluence Cloud and Server via REST API.
Preserves page hierarchy, metadata, and converts HTML to clean text.
"""

import html2text
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
from atlassian import Confluence

from ..storage.raw_storage import RawDataStore
from ..storage.metadata import DocumentMetadata, IngestionRecord, SourceType
import uuid

logger = logging.getLogger(__name__)


class ConfluenceIngestion:
    """
    Ingest Confluence pages and spaces.
    
    Handles:
    - Confluence REST API (Cloud & Server)
    - HTML to clean text conversion
    - Page hierarchy preservation
    - Metadata tracking (author, last update, space)
    """
    
    def __init__(
        self,
        storage: RawDataStore,
        confluence_url: Optional[str] = None,
        username: Optional[str] = None,
        api_token: Optional[str] = None,
        cloud: bool = True
    ):
        """
        Initialize Confluence ingestion.
        
        Args:
            storage: RawDataStore instance
            confluence_url: Confluence instance URL
            username: Username or email (for Cloud)
            api_token: API token or password
            cloud: True for Cloud, False for Server
        """
        self.storage = storage
        self.confluence = None
        
        # Initialize HTML converter
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        self.html_converter.ignore_emphasis = False
        self.html_converter.body_width = 0  # Don't wrap text
        
        # Connect if credentials provided
        if all([confluence_url, username, api_token]):
            self.confluence = Confluence(
                url=confluence_url,
                username=username,
                password=api_token,
                cloud=cloud
            )
            self.base_url = confluence_url
            logger.info(f"ConfluenceIngestion initialized ({confluence_url})")
        else:
            logger.warning("ConfluenceIngestion initialized without credentials")
    
    def ingest_space(
        self,
        space_key: str,
        limit: int = 500,
        include_archived: bool = False
    ) -> IngestionRecord:
        """
        Ingest all pages from a Confluence space.
        
        Args:
            space_key: Confluence space key (e.g., "ENG", "PRODUCT")
            limit: Maximum pages to retrieve
            include_archived: Include archived pages
        
        Returns:
            IngestionRecord with ingestion metrics
        """
        if not self.confluence:
            raise ValueError("Confluence client not configured. Provide credentials.")
        
        ingestion_id = f"confluence_space_{space_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        record = IngestionRecord(
            source_type=SourceType.CONFLUENCE,
            ingestion_id=ingestion_id,
            started_at=datetime.now(),
            source_identifiers=[space_key]
        )
        
        try:
            logger.info(f"Ingesting Confluence space: {space_key}")
            
            # Create batch
            batch_path = self.storage.create_ingestion_batch(
                source_type=SourceType.CONFLUENCE,
                batch_name=space_key
            )
            
            # Get all pages in space
            pages = self.confluence.get_all_pages_from_space(
                space=space_key,
                start=0,
                limit=limit,
                status="current" if not include_archived else None,
                expand="body.storage,version,space,ancestors"
            )
            
            logger.info(f"Retrieved {len(pages)} pages from space {space_key}")
            
            # Process each page
            for page in pages:
                try:
                    self._store_page(page, space_key, batch_path)
                    record.documents_ingested += 1
                    
                except Exception as e:
                    logger.error(f"Failed to process page {page.get('id')}: {e}")
                    record.documents_failed += 1
            
            record.status = "completed"
            record.completed_at = datetime.now()
            
        except Exception as e:
            record.status = "failed"
            record.error_message = str(e)
            record.completed_at = datetime.now()
            logger.error(f"Confluence space ingestion failed: {e}")
        
        finally:
            self.storage.log_ingestion(record)
        
        return record
    
    def ingest_page(self, page_id: str) -> IngestionRecord:
        """
        Ingest a single Confluence page.
        
        Args:
            page_id: Confluence page ID
        
        Returns:
            IngestionRecord with ingestion metrics
        """
        if not self.confluence:
            raise ValueError("Confluence client not configured. Provide credentials.")
        
        ingestion_id = f"confluence_page_{page_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        record = IngestionRecord(
            source_type=SourceType.CONFLUENCE,
            ingestion_id=ingestion_id,
            started_at=datetime.now(),
            source_identifiers=[page_id]
        )
        
        try:
            logger.info(f"Ingesting Confluence page: {page_id}")
            
            # Get page content
            page = self.confluence.get_page_by_id(
                page_id=page_id,
                expand="body.storage,version,space,ancestors"
            )
            
            space_key = page.get("space", {}).get("key", "unknown")
            
            # Create batch
            batch_path = self.storage.create_ingestion_batch(
                source_type=SourceType.CONFLUENCE,
                batch_name=f"{space_key}_page_{page_id}"
            )
            
            # Store page
            self._store_page(page, space_key, batch_path)
            record.documents_ingested = 1
            record.status = "completed"
            record.completed_at = datetime.now()
            
        except Exception as e:
            record.status = "failed"
            record.error_message = str(e)
            record.completed_at = datetime.now()
            logger.error(f"Confluence page ingestion failed: {e}")
        
        finally:
            self.storage.log_ingestion(record)
        
        return record
    
    def _store_page(self, page: Dict, space_key: str, batch_path: str):
        """Store a Confluence page as raw data."""
        page_id = page.get("id")
        page_title = page.get("title", "Untitled")
        
        # Extract HTML content
        html_content = page.get("body", {}).get("storage", {}).get("value", "")
        
        # Convert HTML to clean text
        try:
            text_content = self.html_converter.handle(html_content)
        except Exception as e:
            logger.warning(f"HTML conversion failed for page {page_id}: {e}")
            text_content = html_content  # Fallback to raw HTML
        
        # Extract version info
        version = page.get("version", {})
        last_updated = version.get("when", datetime.now().isoformat())
        author = version.get("by", {}).get("displayName", "Unknown")
        
        # Build page hierarchy path
        hierarchy_path = self._build_hierarchy_path(page)
        
        # Prepare page data
        page_data = {
            "page_id": page_id,
            "title": page_title,
            "space_key": space_key,
            "html_content": html_content,
            "text_content": text_content,
            "version_number": version.get("number", 1),
            "last_updated": last_updated,
            "author": author,
            "hierarchy_path": hierarchy_path,
            "url": f"{self.base_url}/wiki{page.get('_links', {}).get('webui', '')}"
        }
        
        # Create metadata
        metadata = DocumentMetadata(
            source_type=SourceType.CONFLUENCE,
            source_id=page_id,
            source_name=page_title,
            ingested_at=datetime.now(),
            source_timestamp=datetime.fromisoformat(last_updated.replace("Z", "+00:00")),
            author=author,
            title=page_title,
            url=page_data["url"],
            extra={
                "space_key": space_key,
                "version": version.get("number", 1),
                "hierarchy_path": hierarchy_path
            }
        )
        
        # Store
        self.storage.store_raw_document(
            batch_path=batch_path,
            document_id=f"page_{page_id}",
            content=page_data,
            metadata=metadata,
            file_extension="json"
        )
        
        logger.debug(f"Stored Confluence page: {page_title} ({page_id})")
    
    def _build_hierarchy_path(self, page: Dict) -> str:
        """
        Build hierarchical path from page ancestors.
        
        Example: "Engineering / Backend / API Documentation"
        """
        ancestors = page.get("ancestors", [])
        
        if not ancestors:
            return page.get("title", "")
        
        # Build path from ancestors
        path_parts = [a.get("title", "Unknown") for a in ancestors]
        path_parts.append(page.get("title", ""))
        
        return " / ".join(path_parts)
