"""
Vector database lifecycle management.

Manages indexing operations with safety, versioning, and rebuild capabilities.

WHEN TO REBUILD VS UPDATE:
- REBUILD: Embedding model change, chunking strategy change, major data corruption
- UPDATE: New documents added, specific source needs refresh
- INCREMENTAL: Regular updates, small additions

This module ensures vector store integrity and provides safe recovery paths.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document

from ..storage.raw_storage import RawDataStore
from ..storage.metadata import SourceType
from .processor import DocumentProcessor

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """
    Manage vector store lifecycle with versioning and safe operations.
    
    Capabilities:
    - Initial indexing from raw data
    - Incremental updates (add new documents)
    - Source-level reindexing (refresh specific source)
    - Full rebuild (safe delete + recreate)
    - Version tracking
    """
    
    def __init__(
        self,
        storage: RawDataStore,
        processor: DocumentProcessor,
        vectorstore_path: str = "data/vectorstore",
        embedding_model: str = "models/text-embedding-004"
    ):
        """
        Initialize vector store manager.
        
        Args:
            storage: RawDataStore instance
            processor: DocumentProcessor instance
            vectorstore_path: Path to vector store directory
            embedding_model: Embedding model identifier
        """
        self.storage = storage
        self.processor = processor
        self.vectorstore_path = Path(vectorstore_path)
        self.embedding_model = embedding_model
        
        # Initialize embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model)
        
        # Version tracking
        self.version_file = self.vectorstore_path.parent / "vectorstore_version.json"
        
        logger.info(f"VectorStoreManager initialized (model={embedding_model})")
    
    def initialize_index(self, source_batches: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create initial vector index from raw data batches.
        
        Args:
            source_batches: Optional list of specific batch paths to index.
                           If None, indexes all available batches.
        
        Returns:
            Index creation report
        """
        logger.info("Starting initial index creation...")
        
        if self.vectorstore_path.exists():
            raise ValueError(
                f"Vector store already exists at {self.vectorstore_path}. "
                "Use update_index() or rebuild_index() instead."
            )
        
        # Collect batches to index
        if source_batches is None:
            source_batches = self._discover_all_batches()
        
        logger.info(f"Indexing {len(source_batches)} batches")
        
        # Process all batches
        all_documents = []
        batch_stats = {}
        
        for batch_path in source_batches:
            try:
                docs = self.processor.process_batch(batch_path)
                all_documents.extend(docs)
                
                batch_name = Path(batch_path).name
                batch_stats[batch_name] = len(docs)
                
                logger.info(f"Processed batch {batch_name}: {len(docs)} chunks")
                
            except Exception as e:
                logger.error(f"Failed to process batch {batch_path}: {e}")
        
        if not all_documents:
            raise ValueError("No documents to index")
        
        logger.info(f"Creating vector index with {len(all_documents)} documents...")
        
        # Create vector store
        vectordb = Chroma.from_documents(
            documents=all_documents,
            embedding=self.embeddings,
            persist_directory=str(self.vectorstore_path)
        )
        
        # Save version info
        version_info = {
            "created_at": datetime.now().isoformat(),
            "embedding_model": self.embedding_model,
            "document_count": len(all_documents),
            "batch_stats": batch_stats,
            "version": 1,
            "operation": "initialize"
        }
        
        self._save_version_info(version_info)
        
        logger.info(f"Index created successfully: {len(all_documents)} documents")
        
        return version_info
    
    def update_index(self, new_batch_paths: List[str]) -> Dict[str, Any]:
        """
        Add new documents to existing index (incremental update).
        
        Args:
            new_batch_paths: Paths to new data batches to add
        
        Returns:
            Update report
        """
        logger.info(f"Updating index with {len(new_batch_paths)} new batches...")
        
        if not self.vectorstore_path.exists():
            raise ValueError(
                f"Vector store does not exist at {self.vectorstore_path}. "
                "Use initialize_index() first."
            )
        
        # Load existing index
        vectordb = Chroma(
            persist_directory=str(self.vectorstore_path),
            embedding_function=self.embeddings
        )
        
        # Process new batches
        new_documents = []
        batch_stats = {}
        
        for batch_path in new_batch_paths:
            try:
                docs = self.processor.process_batch(batch_path)
                new_documents.extend(docs)
                
                batch_name = Path(batch_path).name
                batch_stats[batch_name] = len(docs)
                
                logger.info(f"Processed batch {batch_name}: {len(docs)} chunks")
                
            except Exception as e:
                logger.error(f"Failed to process batch {batch_path}: {e}")
        
        if not new_documents:
            logger.warning("No new documents to add")
            return {"added": 0}
        
        logger.info(f"Adding {len(new_documents)} new documents to index...")
        
        # Add to vector store
        vectordb.add_documents(new_documents)
        
        # Update version info
        version_info = self._load_version_info()
        version_info["last_updated"] = datetime.now().isoformat()
        version_info["document_count"] += len(new_documents)
        version_info["version"] += 1
        version_info["last_operation"] = "update"
        version_info["last_update_stats"] = batch_stats
        
        self._save_version_info(version_info)
        
        logger.info(f"Index updated: +{len(new_documents)} documents")
        
        return {
            "added": len(new_documents),
            "total": version_info["document_count"],
            "batch_stats": batch_stats
        }
    
    def rebuild_index(
        self,
        source_batches: Optional[List[str]] = None,
        backup: bool = True
    ) -> Dict[str, Any]:
        """
        Completely rebuild vector index from raw data.
        
        WHEN TO USE THIS:
        - Embedding model changed
        - Chunking strategy changed
        - Vector store corrupted
        - Major data cleanup performed
        
        Args:
            source_batches: Optional specific batches. If None, uses all.
            backup: Create backup of existing index
        
        Returns:
            Rebuild report
        """
        logger.warning("Starting full index rebuild...")
        
        if not self.vectorstore_path.exists():
            logger.info("No existing index, performing initial creation")
            return self.initialize_index(source_batches)
        
        # Backup existing index
        if backup:
            backup_path = self._backup_index()
            logger.info(f"Backed up existing index to {backup_path}")
        
        # Delete existing index
        logger.info(f"Removing existing index at {self.vectorstore_path}")
        shutil.rmtree(self.vectorstore_path)
        
        # Rebuild
        result = self.initialize_index(source_batches)
        result["operation"] = "rebuild"
        result["backup_created"] = backup
        
        if backup:
            result["backup_path"] = str(backup_path)
        
        logger.info("Index rebuild complete")
        
        return result
    
    def reindex_source(self, source_type: SourceType) -> Dict[str, Any]:
        """
        Reindex all documents from a specific source type.
        
        WARNING: This removes and re-adds documents from this source.
        Use when source data has been updated but you need to refresh the index.
        
        Args:
            source_type: Type of source to reindex
        
        Returns:
            Reindex report
        """
        logger.info(f"Reindexing source: {source_type.value}")
        
        # Find all batches for this source
        batches = self.storage.list_batches(source_type)
        
        if not batches:
            logger.warning(f"No batches found for {source_type.value}")
            return {"reindexed": 0}
        
        batch_paths = [
            str(self.storage.raw_path / source_type.value / batch["batch_name"])
            for batch in batches
            if batch.get("batch_name")
        ]
        
        logger.info(f"Found {len(batch_paths)} batches for {source_type.value}")
        
        # For simplicity, rebuild with fresh processing
        # In production, you might want source-specific deletion from Chroma
        logger.warning(
            f"Full rebuild recommended when reindexing sources. "
            f"Current implementation will ADD to existing index. "
            f"Use rebuild_index() for clean state."
        )
        
        return self.update_index(batch_paths)
    
    def get_index_info(self) -> Dict[str, Any]:
        """
        Get current index information and statistics.
        
        Returns:
            Index metadata and stats
        """
        if not self.vectorstore_path.exists():
            return {
                "exists": False,
                "message": "No index found"
            }
        
        version_info = self._load_version_info()
        
        # Load vector store to get collection stats
        vectordb = Chroma(
            persist_directory=str(self.vectorstore_path),
            embedding_function=self.embeddings
        )
        
        # Get collection info
        collection = vectordb._collection
        
        return {
            "exists": True,
            "path": str(self.vectorstore_path),
            "version": version_info.get("version", "unknown"),
            "created_at": version_info.get("created_at", "unknown"),
            "last_updated": version_info.get("last_updated", version_info.get("created_at")),
            "embedding_model": version_info.get("embedding_model"),
            "document_count": version_info.get("document_count", collection.count()),
            "collection_count": collection.count()
        }
    
    def _discover_all_batches(self) -> List[str]:
        """Discover all raw data batches across all source types."""
        batches = []
        
        for source_type in SourceType:
            if source_type == SourceType.UNKNOWN:
                continue
            
            source_batches = self.storage.list_batches(source_type)
            
            for batch_meta in source_batches:
                # Construct batch path from metadata
                source_dir = self.storage.raw_path / source_type.value
                
                # Find batch directory by timestamp or name
                for batch_dir in source_dir.iterdir():
                    if batch_dir.is_dir():
                        meta_file = batch_dir / "metadata.json"
                        if meta_file.exists():
                            batches.append(str(batch_dir))
        
        return batches
    
    def _backup_index(self) -> Path:
        """Create backup of existing vector index."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.vectorstore_path.parent / f"vectorstore_backup_{timestamp}"
        
        shutil.copytree(self.vectorstore_path, backup_path)
        
        return backup_path
    
    def _load_version_info(self) -> Dict[str, Any]:
        """Load version information."""
        if self.version_file.exists():
            with open(self.version_file, "r") as f:
                return json.load(f)
        return {}
    
    def _save_version_info(self, info: Dict[str, Any]):
        """Save version information."""
        self.version_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.version_file, "w") as f:
            json.dump(info, f, indent=2)
