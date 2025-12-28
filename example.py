"""
Example script demonstrating how to use the AI Knowledge Base system programmatically.
"""
import os
from src.core.config import settings
from src.core.vector_store import vector_store
from src.core.rag import rag_system
from src.connectors.pdf_loader import pdf_loader
from langchain.docstore.document import Document


def example_add_sample_documents():
    """Add sample documents to the knowledge base."""
    print("Adding sample documents to knowledge base...")
    
    # Create sample documents
    sample_docs = [
        Document(
            page_content="Our AWS spending limit is $50,000 per month. This includes all EC2 instances, S3 storage, and RDS databases.",
            metadata={
                "source": "Company Policy",
                "source_type": "confluence",
                "page_id": "12345"
            }
        ),
        Document(
            page_content="The development team uses Python 3.9+ for all backend services. FastAPI is our preferred framework for REST APIs.",
            metadata={
                "source": "Tech Stack Guide",
                "source_type": "confluence",
                "page_id": "67890"
            }
        ),
        Document(
            page_content="All pull requests require at least 2 approvals before merging. Code reviews must be completed within 24 hours.",
            metadata={
                "source": "Development Process",
                "source_type": "pdf",
                "page": 5
            }
        )
    ]
    
    # Add documents to vector store
    doc_ids = vector_store.add_documents(sample_docs)
    print(f"✓ Added {len(doc_ids)} sample documents to the knowledge base")
    return doc_ids


def example_query():
    """Query the knowledge base."""
    print("\nQuerying the knowledge base...")
    
    questions = [
        "What is our AWS spending limit?",
        "What programming language do we use?",
        "How many approvals do pull requests need?"
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        result = rag_system.query(question)
        print(f"Answer: {result['answer']}")
        print(f"Sources: {len(result['sources'])} source(s) found")


def example_pdf_ingestion():
    """Example of ingesting a PDF file."""
    print("\nExample PDF ingestion:")
    print("To ingest a PDF file:")
    print("  documents = pdf_loader.load_pdf('path/to/your/file.pdf')")
    print("  vector_store.add_documents(documents)")


def main():
    """Run examples."""
    print("=" * 60)
    print("AI Knowledge Base - Example Usage")
    print("=" * 60)
    
    # Check if OpenAI API key is configured
    if not settings.openai_api_key:
        print("\n⚠ Warning: OPENAI_API_KEY not set in .env file")
        print("Please set your OpenAI API key to run this example.")
        print("\nExample .env configuration:")
        print("OPENAI_API_KEY=sk-your-api-key-here")
        return
    
    print(f"\n✓ Configuration loaded")
    print(f"  - Embedding Model: {settings.embedding_model}")
    print(f"  - LLM Model: {settings.llm_model}")
    print(f"  - Chunk Size: {settings.chunk_size}")
    
    # Add sample documents
    example_add_sample_documents()
    
    # Query examples
    example_query()
    
    # PDF example
    example_pdf_ingestion()
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
