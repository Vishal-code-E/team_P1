from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os


def create_vectorstore(documents, persist_directory="data/vectorstore"):
    """
    Create and persist a Chroma vector store from documents.
    
    Args:
        documents: List of chunked documents
        persist_directory: Directory to persist the vector store
        
    Returns:
        Chroma vectorstore object
    """
    # Initialize OpenAI embeddings
    embeddings = OpenAIEmbeddings()
    
    # Create Chroma vector store
    vectordb = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    return vectordb


def load_vectorstore(persist_directory="data/vectorstore"):
    """
    Load an existing Chroma vector store.
    
    Args:
        persist_directory: Directory where vector store is persisted
        
    Returns:
        Chroma vectorstore object
    """
    embeddings = OpenAIEmbeddings()
    
    vectordb = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    
    return vectordb
