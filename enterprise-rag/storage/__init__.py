"""
Storage layer for raw and processed data.

This module provides persistent storage management for all data sources
before and after processing. It ensures data preservation, versioning,
and auditability.
"""

from .raw_storage import RawDataStore
from .metadata import DocumentMetadata, IngestionRecord

__all__ = [
    "RawDataStore",
    "DocumentMetadata",
    "IngestionRecord",
]
