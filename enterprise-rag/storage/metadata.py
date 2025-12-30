"""
Metadata models for tracking ingested documents.

These models define the structure for metadata that flows through
the ingestion pipeline, from raw storage through to vector indexing.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
import json


class SourceType(Enum):
    """Enumeration of supported data sources."""
    SLACK = "slack"
    CONFLUENCE = "confluence"
    PDF = "pdf"
    MARKDOWN = "markdown"
    TEXT = "text"
    UNKNOWN = "unknown"


@dataclass
class DocumentMetadata:
    """
    Metadata for a single document.
    
    This structure is attached to every document throughout the pipeline
    and enables source attribution, version tracking, and filtering.
    """
    source_type: SourceType
    source_id: str  # Unique identifier within source (e.g., Slack thread_ts, Confluence page_id)
    source_name: str  # Human-readable source (e.g., "#engineering", "AWS Budget Policy")
    
    # Temporal tracking
    ingested_at: datetime
    source_timestamp: Optional[datetime] = None  # When content was created/modified at source
    
    # Content metadata
    author: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    
    # Source-specific metadata (flexible extension point)
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data["source_type"] = self.source_type.value
        data["ingested_at"] = self.ingested_at.isoformat() if self.ingested_at else None
        data["source_timestamp"] = self.source_timestamp.isoformat() if self.source_timestamp else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentMetadata":
        """Reconstruct from dictionary."""
        data = data.copy()
        data["source_type"] = SourceType(data["source_type"])
        if data.get("ingested_at"):
            data["ingested_at"] = datetime.fromisoformat(data["ingested_at"])
        if data.get("source_timestamp"):
            data["source_timestamp"] = datetime.fromisoformat(data["source_timestamp"])
        return cls(**data)


@dataclass
class IngestionRecord:
    """
    Record of an ingestion operation.
    
    Tracks what was ingested, when, and the outcome.
    Used for debugging, auditing, and managing re-indexing.
    """
    source_type: SourceType
    ingestion_id: str  # Unique ID for this ingestion run
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    # Metrics
    documents_ingested: int = 0
    documents_failed: int = 0
    bytes_processed: int = 0
    
    # Status
    status: str = "in_progress"  # in_progress, completed, failed
    error_message: Optional[str] = None
    
    # Details
    source_identifiers: List[str] = field(default_factory=list)  # e.g., channel IDs, space keys
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data["source_type"] = self.source_type.value
        data["started_at"] = self.started_at.isoformat()
        data["completed_at"] = self.completed_at.isoformat() if self.completed_at else None
        return data
    
    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), indent=2)
