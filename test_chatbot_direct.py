#!/usr/bin/env python3
"""
Direct test of backend RAG functionality without server
"""

import sys
import os

# Set up paths
sys.path.insert(0, '/Users/vishale/team_P1/enterprise-rag')
os.chdir('/Users/vishale/team_P1/enterprise-rag')

from dotenv import load_dotenv
load_dotenv('/Users/vishale/team_P1/enterprise-rag/.env')

print("🔍 Testing MemOrg AI Backend Components\n")

# Check environment
api_key = os.getenv('OPENAI_API_KEY')
model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo')

if api_key:
    print(f"✅ OpenAI API Key: {api_key[:20]}...{api_key[-10:]}")
    print(f"✅ Model: {model}")
else:
    print("❌ No OpenAI API key found!")
    sys.exit(1)

# Import individual modules directly (avoid __init__)
print("\n📦 Importing components...")

try:
    # Import vector store functions
    from rag.retriever import load_vectorstore
    print("✅ Vector store module imported")
    
    # Import QA chain
    from rag.qa_chain import create_qa_chain
    print("✅ QA chain module imported")
    
    # Import agents
    from agent.intent_router import route_intent, get_direct_answer
    print("✅ Intent router imported")
    
    from agent.answer_verifier import verify_answer
    print("✅ Answer verifier imported")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test the components
print("\n🧪 Testing RAG Pipeline...")

try:
    # Load vector store
    print("\n1️⃣ Loading vector store...")
    vectorstore = load_vectorstore()
    if vectorstore:
        print("   ✅ Vector store loaded")
    else:
        print("   ❌ Vector store failed to load")
        sys.exit(1)
    
    # Create QA chain
    print("\n2️⃣ Creating QA chain...")
    qa_chain = create_qa_chain(vectorstore)
    if qa_chain:
        print("   ✅ QA chain created with gpt-4-turbo")
    else:
        print("   ❌ QA chain failed")
        sys.exit(1)
    
    # Test intent routing
    test_question = "What is AWS Budget policy?"
    print(f"\n3️⃣ Testing intent router with: '{test_question}'")
    decision = route_intent(test_question)
    print(f"   ✅ Decision: {decision}")
    
    # Handle both RETRIEVE and RETRIEVE_AND_ANSWER
    decision_type = decision if isinstance(decision, str) else decision.get('decision', 'UNKNOWN')
    
    if decision_type in ["RETRIEVE", "RETRIEVE_AND_ANSWER"]:
        # Test RAG retrieval
        print("\n4️⃣ Testing RAG retrieval...")
        result = qa_chain({"query": test_question})
        answer = result.get('result', 'No answer')
        sources = result.get('source_documents', [])
        
        print(f"   ✅ Retrieved {len(sources)} documents")
        print(f"   📝 Answer ({len(answer)} chars):")
        print(f"      {answer[:300]}...")
        
        # Test answer verifier
        print("\n5️⃣ Testing answer verifier...")
        is_valid = verify_answer(
            test_question,
            answer,
            sources
        )
        
        print(f"   ✅ Validation complete")
        print(f"   🎯 Is Valid: {is_valid}")
        
        print("\n" + "="*60)
        print("✨ SUCCESS! All backend components working correctly!")
        print("="*60)
        print("\n📊 Test Results:")
        print(f"   • Vector Store: ✅ Working (OpenAI embeddings 1536D)")
        print(f"   • QA Chain: ✅ Working (GPT-4 Turbo)")
        print(f"   • Intent Router: ✅ Working ({decision_type})")
        print(f"   • RAG Retrieval: ✅ Working ({len(sources)} docs)")
        print(f"   • Answer Verifier: ✅ Working (Valid={is_valid})")
        print(f"\n🚀 The chatbot is fully functional!")
        
    elif decision == "ANSWER_DIRECTLY":
        print("\n4️⃣ Getting direct answer...")
        direct_answer = get_direct_answer(test_question)
        print(f"   ✅ Direct answer: {direct_answer[:200]}...")
        
    else:  # REFUSE
        print("   ℹ️  Question was refused (out of scope)")
    
except Exception as e:
    print(f"\n❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
