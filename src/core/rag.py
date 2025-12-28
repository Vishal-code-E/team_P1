"""RAG (Retrieval-Augmented Generation) system implementation."""
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from ..core.config import settings
from ..core.vector_store import vector_store


class RAGSystem:
    """Retrieval-Augmented Generation system for question answering."""
    
    def __init__(self):
        """Initialize the RAG system."""
        self.llm = ChatOpenAI(
            openai_api_key=settings.openai_api_key,
            model_name=settings.llm_model,
            temperature=0.3
        )
        
        # Custom prompt template for better answers
        self.prompt_template = """You are a helpful AI assistant that answers questions based on the company's knowledge base.
Use the following pieces of context to answer the question at the end. If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.

Always cite your sources by mentioning which document or source the information came from.

Context:
{context}

Question: {question}

Helpful Answer with Sources:"""
        
        self.PROMPT = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create retrieval chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vector_store.vectorstore.as_retriever(
                search_kwargs={"k": 4}
            ),
            chain_type_kwargs={"prompt": self.PROMPT},
            return_source_documents=True
        )
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the knowledge base and get an answer.
        
        Args:
            question: User's question
            
        Returns:
            Dictionary containing answer and source documents
        """
        result = self.qa_chain.invoke({"query": question})
        
        # Format the response with sources
        sources = []
        for doc in result.get("source_documents", []):
            source_info = {
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "metadata": doc.metadata
            }
            sources.append(source_info)
        
        return {
            "answer": result["result"],
            "sources": sources,
            "question": question
        }
    
    def query_with_filter(
        self, 
        question: str, 
        source_type: str = None
    ) -> Dict[str, Any]:
        """
        Query with optional filtering by source type.
        
        Args:
            question: User's question
            source_type: Optional filter (e.g., 'pdf', 'confluence', 'slack')
            
        Returns:
            Dictionary containing answer and source documents
        """
        # Get relevant documents with filtering
        search_kwargs = {"k": 4}
        if source_type:
            search_kwargs["filter"] = {"source_type": source_type}
        
        retriever = vector_store.vectorstore.as_retriever(
            search_kwargs=search_kwargs
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": self.PROMPT},
            return_source_documents=True
        )
        
        result = qa_chain.invoke({"query": question})
        
        # Format the response with sources
        sources = []
        for doc in result.get("source_documents", []):
            source_info = {
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "metadata": doc.metadata
            }
            sources.append(source_info)
        
        return {
            "answer": result["result"],
            "sources": sources,
            "question": question
        }


# Global RAG system instance
rag_system = RAGSystem()
