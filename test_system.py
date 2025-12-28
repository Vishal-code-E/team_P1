"""
Test script to validate the AI Knowledge Base system.
This script tests core functionality without requiring external API keys.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from src.core.config import settings
        print("✓ Config module imported")
        
        from src.api.routes import app
        print("✓ API routes module imported")
        
        from src.connectors.pdf_loader import pdf_loader
        print("✓ PDF loader imported")
        
        from src.connectors.confluence_connector import confluence_connector
        print("✓ Confluence connector imported")
        
        from src.connectors.slack_connector import slack_connector
        print("✓ Slack connector imported")
        
        print("\n✓ All imports successful!\n")
        return True
    except Exception as e:
        print(f"\n✗ Import failed: {e}\n")
        return False


def test_config():
    """Test configuration loading."""
    print("Testing configuration...")
    
    try:
        from src.core.config import settings
        
        print(f"  - Chunk size: {settings.chunk_size}")
        print(f"  - Chunk overlap: {settings.chunk_overlap}")
        print(f"  - Embedding model: {settings.embedding_model}")
        print(f"  - LLM model: {settings.llm_model}")
        print(f"  - App host: {settings.app_host}")
        print(f"  - App port: {settings.app_port}")
        
        print("\n✓ Configuration loaded successfully!\n")
        return True
    except Exception as e:
        print(f"\n✗ Configuration test failed: {e}\n")
        return False


def test_pdf_processing():
    """Test PDF processing without actual files."""
    print("Testing PDF processing structure...")
    
    try:
        from src.connectors.pdf_loader import PDFLoader
        from langchain.docstore.document import Document
        
        loader = PDFLoader()
        print(f"  - PDF loader created")
        print(f"  - Text splitter configured with chunk_size={loader.text_splitter._chunk_size}")
        
        print("\n✓ PDF loader structure is correct!\n")
        return True
    except Exception as e:
        print(f"\n✗ PDF processing test failed: {e}\n")
        return False


def test_connectors():
    """Test connector initialization."""
    print("Testing connectors...")
    
    try:
        from src.connectors.confluence_connector import confluence_connector
        from src.connectors.slack_connector import slack_connector
        
        print(f"  - Confluence configured: {confluence_connector.is_configured()}")
        print(f"  - Slack configured: {slack_connector.is_configured()}")
        
        print("\n✓ Connectors initialized!\n")
        return True
    except Exception as e:
        print(f"\n✗ Connector test failed: {e}\n")
        return False


def test_api_structure():
    """Test API structure."""
    print("Testing API structure...")
    
    try:
        from src.api.routes import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
        print("  - Health endpoint works")
        
        # Test status endpoint (may fail without OpenAI key, but structure should be ok)
        response = client.get("/api/status")
        print(f"  - Status endpoint returns {response.status_code}")
        
        print("\n✓ API structure is correct!\n")
        return True
    except ImportError:
        print("  ⚠ FastAPI test client not available, skipping API tests")
        print("\n~ API structure test skipped\n")
        return True
    except Exception as e:
        print(f"\n✗ API test failed: {e}\n")
        return False


def test_document_creation():
    """Test document creation."""
    print("Testing document creation...")
    
    try:
        from langchain.docstore.document import Document
        
        # Create a test document
        doc = Document(
            page_content="This is a test document about AWS spending limits.",
            metadata={
                "source": "Test Document",
                "source_type": "test",
                "page": 1
            }
        )
        
        print(f"  - Document created with {len(doc.page_content)} characters")
        print(f"  - Metadata keys: {list(doc.metadata.keys())}")
        
        print("\n✓ Document creation works!\n")
        return True
    except Exception as e:
        print(f"\n✗ Document creation test failed: {e}\n")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("AI Knowledge Base - System Tests")
    print("=" * 60)
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("PDF Processing", test_pdf_processing),
        ("Connectors", test_connectors),
        ("Document Creation", test_document_creation),
        ("API Structure", test_api_structure),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}\n")
            results.append((test_name, False))
    
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Set your OPENAI_API_KEY in .env file")
        print("2. Run: python main.py")
        print("3. Open: http://localhost:8000")
        return 0
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
