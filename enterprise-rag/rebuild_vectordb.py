#!/usr/bin/env python3
"""
Rebuild Vector Database Script
Loads all documents from data/raw/ and creates fresh embeddings
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import RAG modules
from ingest.load_docs import load_and_chunk_documents
from rag.retriever import create_vectorstore

def main():
    """Rebuild vector database from scratch"""
    
    print("=" * 60)
    print("VECTOR DATABASE REBUILD")
    print("=" * 60)
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("ERROR: OPENAI_API_KEY not configured")
        print("Set OPENAI_API_KEY in .env file")
        sys.exit(1)
    
    print(f"✓ OpenAI API key configured")
    
    # Paths
    raw_docs_path = "data/raw"
    vectorstore_path = "data/vectorstore"
    
    # Check raw documents exist
    if not os.path.exists(raw_docs_path):
        print(f"ERROR: {raw_docs_path} directory not found")
        sys.exit(1)
    
    raw_files = [f for f in os.listdir(raw_docs_path) if f.endswith(('.md', '.pdf', '.txt'))]
    if not raw_files:
        print(f"ERROR: No documents found in {raw_docs_path}")
        sys.exit(1)
    
    print(f"✓ Found {len(raw_files)} documents in {raw_docs_path}")
    for f in raw_files:
        print(f"  - {f}")
    
    # Load and chunk documents
    print("\nLoading and chunking documents...")
    try:
        documents = load_and_chunk_documents(raw_docs_path)
        print(f"✓ Created {len(documents)} document chunks")
    except Exception as e:
        print(f"ERROR loading documents: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Create vector store
    print("\nCreating vector embeddings (this may take 1-2 minutes)...")
    try:
        vectorstore = create_vectorstore(documents, vectorstore_path)
        print(f"✓ Vector store created and saved to {vectorstore_path}")
    except Exception as e:
        print(f"ERROR creating vector store: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("SUCCESS: Vector database rebuilt successfully!")
    print("=" * 60)
    print(f"\nDocuments indexed: {len(raw_files)}")
    print(f"Document chunks: {len(documents)}")
    print(f"Vector store location: {vectorstore_path}")
    print("\nYou can now start the API server with:")
    print("  python api_server.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
