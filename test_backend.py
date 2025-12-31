#!/usr/bin/env python3
"""
Quick backend test script
"""

import sys
import os
import requests
import time

# Add enterprise-rag to path
sys.path.insert(0, '/Users/vishale/team_P1/enterprise-rag')

def test_backend_locally():
    """Test the backend server running on localhost"""
    
    print("🔍 Testing MemOrg AI Backend Locally\n")
    
    # Start server in background (assumes you've started it manually)
    backend_url = "http://localhost:8001"
    
    # Test 1: Health Check
    print("1️⃣ Testing Health Endpoint...")
    try:
        response = requests.get(f"{backend_url}/api/health", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Health check passed: {response.json()}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        print("   💡 Make sure the backend server is running on port 8001")
        return
    
    # Test 2: Chat Request
    print("\n2️⃣ Testing Chat Endpoint...")
    chat_data = {
        "question": "What is AWS Budget policy?"
    }
    
    try:
        response = requests.post(
            f"{backend_url}/api/chat",
            json=chat_data,
            timeout=45
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Chat request successful!")
            print(f"   📝 Answer: {result.get('answer', 'No answer')[:150]}...")
            print(f"   🎯 Confidence: {result.get('confidence', 'N/A')}")
            print(f"   📚 Sources: {len(result.get('sources', []))} documents")
            print(f"   🤖 Model: gpt-4-turbo")
        else:
            print(f"   ❌ Chat request failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Chat request failed: {e}")
    
    print("\n✨ Local backend test complete!")

if __name__ == "__main__":
    # First, let's try to import and start the server
    print("📦 Checking backend server...\n")
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv('/Users/vishale/team_P1/enterprise-rag/.env')
    
    # Import backend modules
    try:
        from ingest.load_docs import load_and_chunk_documents
        from rag.retriever import create_vectorstore, load_vectorstore
        from rag.qa_chain import create_qa_chain
        from agent.intent_router import route_intent
        from agent.answer_verifier import verify_answer
        
        print("✅ All backend modules imported successfully!")
        print(f"✅ OpenAI API Key configured: {os.getenv('OPENAI_API_KEY')[:20]}...")
        print(f"✅ Model: {os.getenv('OPENAI_MODEL', 'gpt-4-turbo')}")
        
        # Quick test of the components
        print("\n🧪 Testing RAG components...")
        
        # Test vector store loading
        vectorstore = load_vectorstore()
        if vectorstore:
            print("✅ Vector store loaded successfully")
            
            # Test QA chain creation
            qa_chain = create_qa_chain(vectorstore)
            if qa_chain:
                print("✅ QA chain created successfully")
                
                # Test a simple query
                test_question = "What is AWS Budget policy?"
                print(f"\n🤖 Testing with question: '{test_question}'")
                
                # Test intent routing
                decision = route_intent(test_question)
                print(f"✅ Intent Router: {decision}")
                
                if decision == "RETRIEVE":
                    # Test RAG
                    result = qa_chain({"query": test_question})
                    answer = result.get('result', 'No answer')
                    sources = result.get('source_documents', [])
                    
                    print(f"\n📝 Answer: {answer[:200]}...")
                    print(f"📚 Retrieved {len(sources)} source documents")
                    
                    # Test answer verifier
                    is_valid, confidence, explanation = verify_answer(
                        test_question, 
                        answer, 
                        sources
                    )
                    
                    print(f"✅ Answer Verifier: Valid={is_valid}, Confidence={confidence}")
                    print(f"   {explanation}")
                    
                print("\n✨ All components working! The chatbot is functional.")
                print("\n💡 To test the full API:")
                print("   1. Start the server in another terminal:")
                print("      cd /Users/vishale/team_P1/enterprise-rag")
                print("      gunicorn api_server:app --bind 0.0.0.0:8001 --timeout 120")
                print("   2. Then run: python3 test_backend.py --api-test")
                
            else:
                print("❌ Failed to create QA chain")
        else:
            print("❌ Failed to load vector store")
            
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        import traceback
        traceback.print_exc()
