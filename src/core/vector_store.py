"""Vector store management using ChromaDB."""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional, Tuple
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document

from ..core.config import settings


class VectorStore:
    """Manages vector storage and retrieval using ChromaDB."""
    
    def __init__(self):
        """Initialize the vector store."""
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            model=settings.embedding_model
        )
        
        # Initialize ChromaDB client
        self.client = chromadb.Client(ChromaSettings(
            persist_directory=settings.chroma_persist_directory,
            anonymized_telemetry=False
        ))
        
        # Initialize Langchain Chroma wrapper
        self.vectorstore = Chroma(
            client=self.client,
            collection_name="knowledge_base",
            embedding_function=self.embeddings,
            persist_directory=settings.chroma_persist_directory
        )
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of Document objects to add
            
        Returns:
            List of document IDs
        """
        return self.vectorstore.add_documents(documents)
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of similar documents
        """
        return self.vectorstore.similarity_search(query, k=k, filter=filter)
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Document, float]]:
        """
        Search for similar documents with relevance scores.
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of tuples (document, score)
        """
        return self.vectorstore.similarity_search_with_score(query, k=k, filter=filter)
    
    def delete_collection(self):
        """Delete the entire collection."""
        self.vectorstore.delete_collection()
    
    def get_collection_count(self) -> int:
        """Get the number of documents in the collection."""
        collection = self.client.get_collection("knowledge_base")
        return collection.count()


# Global vector store instance
vector_store = VectorStore()
