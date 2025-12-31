#!/usr/bin/env python3
"""
Regenerate vector store with OpenAI embeddings
"""

import sys
import os

# Set up paths
sys.path.insert(0, '/Users/vishale/team_P1/enterprise-rag')
os.chdir('/Users/vishale/team_P1/enterprise-rag')

from dotenv import load_dotenv
load_dotenv('/Users/vishale/team_P1/enterprise-rag/.env')

print("🔄 Regenerating Vector Store with OpenAI Embeddings\n")

# Check environment
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("❌ No OpenAI API key found!")
    sys.exit(1)

print(f"✅ OpenAI API Key: {api_key[:20]}...{api_key[-10:]}")
print(f"✅ Model: text-embedding-3-small (1536 dimensions)\n")

# Import required modules (avoiding __init__ imports)
import importlib.util

# Load load_docs directly
spec = importlib.util.spec_from_file_location("load_docs", "/Users/vishale/team_P1/enterprise-rag/ingest/load_docs.py")
load_docs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(load_docs)
load_and_chunk_documents = load_docs.load_and_chunk_documents

from rag.retriever import create_vectorstore

try:
    # Step 1: Load and chunk documents
    print("1️⃣ Loading documents from data/raw/...")
    documents = load_and_chunk_documents("data/raw")
    print(f"   ✅ Loaded {len(documents)} document chunks\n")
    
    # Step 2: Create vector store with OpenAI embeddings
    print("2️⃣ Creating vector store with OpenAI embeddings...")
    print("   (This may take a minute...)")
    vectorstore = create_vectorstore(documents, "data/vectorstore")
    print(f"   ✅ Vector store created successfully!\n")
    
    # Step 3: Verify the vector store
    print("3️⃣ Verifying vector store...")
    from rag.retriever import load_vectorstore
    loaded_vs = load_vectorstore("data/vectorstore")
    
    # Test a simple query
    test_results = loaded_vs.similarity_search("AWS Budget policy", k=2)
    print(f"   ✅ Vector store working! Retrieved {len(test_results)} documents")
    if test_results:
        print(f"   📄 Sample result: {test_results[0].page_content[:100]}...\n")
    
    print("="*60)
    print("✨ SUCCESS! Vector store regenerated with OpenAI embeddings")
    print("="*60)
    print("\n🚀 Your chatbot is now ready to use!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
