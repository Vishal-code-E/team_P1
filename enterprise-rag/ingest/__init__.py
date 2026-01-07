"""
Enterprise RAG Ingestion Pipeline

High-level API for data ingestion and vector indexing.
"""

# Try to import advanced ingestion modules
# These may fail if running in simple mode (api_server.py only needs load_docs)
try:
    from .orchestrator import IngestionOrchestrator
    from .slack_ingestion import SlackIngestion
    from .confluence_ingestion import ConfluenceIngestion
    from .document_ingestion import DocumentUploadIngestion
    from .processor import DocumentProcessor
    from .vector_manager import VectorStoreManager
    
    __all__ = [
        "IngestionOrchestrator",
        "SlackIngestion",
        "ConfluenceIngestion",
        "DocumentUploadIngestion",
        "DocumentProcessor",
        "VectorStoreManager",
    ]
except ImportError as e:
    # Advanced ingestion modules not available
    # This is OK for basic RAG functionality
    __all__ = []

