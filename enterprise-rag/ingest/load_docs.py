"""
Legacy document loading - DEPRECATED

This module is kept for backward compatibility.
New implementations should use the ingestion pipeline in:
- enterprise-rag/ingest/orchestrator.py

See INGESTION_PLATFORM.md for migration guide.
"""

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import warnings


def load_and_chunk_documents(data_dir="data/raw"):
    """
    [DEPRECATED] Load markdown files from data/raw/ and chunk them.
    
    Use IngestionOrchestrator for new implementations.
    
    Args:
        data_dir: Directory containing raw markdown files
        
    Returns:
        List of chunked documents
    """
    warnings.warn(
        "load_and_chunk_documents is deprecated. Use IngestionOrchestrator instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    documents = []
    
    # Load all markdown files from the data directory
    for filename in os.listdir(data_dir):
        if filename.endswith(".md"):
            file_path = os.path.join(data_dir, filename)
            loader = TextLoader(file_path, encoding="utf-8")
            documents.extend(loader.load())
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100
    )
    
    chunked_docs = text_splitter.split_documents(documents)
    
    return chunked_docs
