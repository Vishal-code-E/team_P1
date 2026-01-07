"""
Flask API Server for Enterprise RAG Chatbot
Provides REST endpoints for the Next.js frontend

CRITICAL: All OpenAI/Chroma imports are DEFERRED to function scope
to prevent gunicorn worker crashes on cold start.
"""

import os
import shutil
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables at import time (safe - no API calls)
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for Vercel frontend and localhost dev
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://enterprise-rag-frontend-pux7d4p5y.vercel.app",
            "https://*.vercel.app",
            "http://localhost:3000",
            "http://localhost:3001",
            "*"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuration
UPLOAD_FOLDER = 'data/raw'
VECTORSTORE_PATH = 'data/vectorstore'
ALLOWED_EXTENSIONS = {'md', 'pdf', 'txt'}

# Global QA chain (lazy-initialized on first /chat request)
qa_chain = None
initialization_error = None


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_confidence(source_documents):
    """Calculate confidence level based on number of retrieved sources"""
    num_sources = len(source_documents) if source_documents else 0
    
    if num_sources >= 2:
        return "High"
    elif num_sources == 1:
        return "Medium"
    else:
        return "Low"


def format_sources(source_documents):
    """Format source documents as a list of filenames"""
    if not source_documents:
        return []
    
    sources = []
    seen = set()
    
    for doc in source_documents:
        source_file = os.path.basename(doc.metadata.get("source", "Unknown"))
        if source_file not in seen:
            seen.add(source_file)
            sources.append(source_file)
    
    return sources


def initialize_qa_chain():
    """
    Initialize the QA chain with DEFERRED imports.
    
    CRITICAL: All AI/DB imports happen INSIDE this function
    to prevent import-time crashes in gunicorn workers.
    
    Returns:
        bool: True if successful, False otherwise
    """
    global qa_chain, initialization_error
    
    # If already initialized, skip
    if qa_chain is not None:
        return True
    
    # If previous initialization failed, don't retry every request
    if initialization_error is not None:
        return False
    
    try:
        print("=" * 60)
        print("INITIALIZING QA CHAIN (lazy load on first request)")
        print("=" * 60)
        
        # DEFERRED IMPORTS: Only import when actually needed
        from ingest.load_docs import load_and_chunk_documents
        from rag.retriever import create_vectorstore, load_vectorstore
        from rag.qa_chain import create_qa_chain
        
        # Validate OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            error_msg = "OPENAI_API_KEY not configured in environment"
            print(f"ERROR: {error_msg}")
            initialization_error = error_msg
            return False
        
        # Check if raw documents exist
        if not os.path.exists(UPLOAD_FOLDER):
            print(f"Creating upload folder: {UPLOAD_FOLDER}")
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        raw_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(('.md', '.pdf', '.txt'))]
        if not raw_files:
            error_msg = "No documents found in data/raw/"
            print(f"WARNING: {error_msg}")
            initialization_error = error_msg
            return False
        
        print(f"Found {len(raw_files)} documents in {UPLOAD_FOLDER}")
        
        # Load or create vector store
        if os.path.exists(VECTORSTORE_PATH) and os.listdir(VECTORSTORE_PATH):
            print("Loading existing vector store...")
            vectorstore = load_vectorstore(VECTORSTORE_PATH)
        else:
            print("Creating new vector store...")
            documents = load_and_chunk_documents(UPLOAD_FOLDER)
            print(f"Loaded {len(documents)} document chunks")
            
            if len(documents) == 0:
                error_msg = "No document chunks created"
                print(f"ERROR: {error_msg}")
                initialization_error = error_msg
                return False
            
            vectorstore = create_vectorstore(documents, VECTORSTORE_PATH)
            print("Vector store created and persisted")
        
        # Create QA chain
        qa_chain = create_qa_chain(vectorstore)
        print("=" * 60)
        print("✓ QA chain initialized successfully")
        print(f"✓ Ready to answer questions from {len(raw_files)} documents")
        print("=" * 60)
        return True
        
    except Exception as e:
        error_msg = str(e)
        print("=" * 60)
        print(f"INITIALIZATION ERROR: {error_msg}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        initialization_error = error_msg
        return False


@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health_check():
    """
    FAST health check endpoint for cold start detection.
    
    CRITICAL: Returns immediately without touching LLM/DB/vectorstore.
    No imports, no API calls, no file I/O.
    Essential for Render free tier wake-up.
    """
    return jsonify({
        'status': 'healthy',
        'service': 'memorg-ai-backend',
        'qa_chain_initialized': qa_chain is not None
    }), 200


@app.route('/chat', methods=['POST'])
@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint with lazy initialization and comprehensive error handling.
    
    ALWAYS returns JSON, even on errors.
    Expects: {"message": "user question"}
    Returns: {"answer": "...", "sources": [...], "confidence": "..."}
    """
    try:
        print(f"[REQUEST] POST /chat received from {request.remote_addr}")
        
        # Lazy initialization on first request
        if qa_chain is None:
            print("[INIT] QA chain not initialized, attempting lazy load...")
            success = initialize_qa_chain()
            if not success:
                return jsonify({
                    'answer': 'System initialization failed. Please contact support.',
                    'sources': [],
                    'confidence': 'Low',
                    'error': initialization_error or 'Initialization failed'
                }), 503
        
        # Parse request
        data = request.get_json()
        if not data:
            return jsonify({
                'answer': 'Invalid request format',
                'sources': [],
                'confidence': 'Low',
                'error': 'Request body must be JSON'
            }), 400
        
        question = data.get('message', '').strip()
        if not question:
            return jsonify({
                'answer': 'Please provide a message',
                'sources': [],
                'confidence': 'Low',
                'error': 'Message field is required'
            }), 400
        
        print(f"[CHAT START] Question: {question[:100]}...")
        
        # DEFERRED IMPORTS: Only import agent modules when needed
        from agent.intent_router import route_intent, get_direct_answer
        from agent.answer_verifier import verify_answer
        
        # INTENT ROUTING: Decide action before RAG
        try:
            intent_decision = route_intent(question)
            decision = intent_decision.get("decision")
            print(f"[Intent Router] Decision: {decision}")
        except Exception as e:
            print(f"[Intent Router ERROR] {str(e)} - defaulting to RETRIEVE_AND_ANSWER")
            decision = "RETRIEVE_AND_ANSWER"
        
        # Handle based on intent decision
        if decision == "ANSWER_DIRECTLY":
            # Conversational query - answer without retrieval
            try:
                answer = get_direct_answer(question)
                print(f"[CHAT END] Direct answer provided")
                return jsonify({
                    'answer': answer,
                    'sources': [],
                    'confidence': 'High'
                }), 200
            except Exception as e:
                print(f"[Direct Answer ERROR] {str(e)} - falling back to RAG")
                decision = "RETRIEVE_AND_ANSWER"
            
        if decision == "REFUSE":
            # Out-of-scope query - refuse safely
            print(f"[CHAT END] Query refused (out of scope)")
            return jsonify({
                'answer': "I don't know based on the provided documents.",
                'sources': [],
                'confidence': 'Low'
            }), 200
        
        # decision == "RETRIEVE_AND_ANSWER": proceed to RAG pipeline
        print("[RAG] Starting document retrieval...")
        
        # Get answer from QA chain with error handling
        try:
            result = qa_chain.invoke({"query": question})
        except Exception as e:
            print(f"[RAG ERROR] OpenAI API call failed: {str(e)}")
            return jsonify({
                'answer': "I'm experiencing technical difficulties. Please try again in a moment.",
                'sources': [],
                'confidence': 'Low',
                'error': f'OpenAI API error: {str(e)}'
            }), 500
        
        # Get source documents and calculate confidence
        source_docs = result.get("source_documents", [])
        confidence = get_confidence(source_docs)
        answer = result.get("result", "I don't know based on the provided documents.")
        
        print(f"[RAG] Retrieved {len(source_docs)} source documents")
        
        # ANSWER VERIFICATION: Validate answer is fully supported by sources
        try:
            is_valid = verify_answer(question, answer, source_docs)
        except Exception as e:
            print(f"[Verifier ERROR] {str(e)} - defaulting to INVALID")
            is_valid = False
        
        if not is_valid:
            # Answer contains unsupported claims - override with safe refusal
            print("[Verifier] Answer INVALID - contains unsupported claims")
            answer = "I don't know based on the provided documents."
            confidence = "Low"
        else:
            print("[Verifier] Answer VALID - all claims supported by sources")
        
        # Handle negative case - force "I don't know" for low confidence
        if confidence == "Low" and is_valid:
            answer = "I don't know based on the provided documents."
        
        print(f"[CHAT END] Response ready (confidence: {confidence})")
        
        # Format response
        return jsonify({
            'answer': answer,
            'sources': format_sources(source_docs),
            'confidence': confidence
        }), 200
        
    except Exception as e:
        # Catch-all error handler - ALWAYS return JSON
        print(f"[CRITICAL ERROR] Unhandled exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'answer': 'An unexpected error occurred. Please try again.',
            'sources': [],
            'confidence': 'Low',
            'error': str(e)
        }), 500


@app.route('/upload', methods=['POST'])
@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    File upload endpoint with automatic re-indexing.
    
    ALWAYS returns JSON.
    Accepts multipart/form-data with 'file' field.
    Returns: {"success": true, "message": "..."}
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save file
        filename = secure_filename(file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        print(f"File uploaded: {filename}")
        
        # Re-index: reload documents and recreate vectorstore
        print("Re-indexing documents...")
        
        # Remove old vectorstore
        if os.path.exists(VECTORSTORE_PATH):
            shutil.rmtree(VECTORSTORE_PATH)
        
        # Reset global state to force re-initialization
        global qa_chain, initialization_error
        qa_chain = None
        initialization_error = None
        
        # Reinitialize QA chain with new documents
        success = initialize_qa_chain()
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Successfully uploaded and indexed {filename}'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': f'File uploaded but indexing failed: {initialization_error}'
            }), 500
            
    except Exception as e:
        print(f"Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Upload failed: {str(e)}'
        }), 500


# Gunicorn entry point - NO initialization here
# QA chain will be lazy-loaded on first /chat request
if __name__ == '__main__':
    # Only runs in development mode (not under gunicorn)
    print("=" * 60)
    print("DEVELOPMENT MODE: Flask dev server")
    print("=" * 60)
    
    # Pre-initialize in dev mode for faster first request
    initialize_qa_chain()
    
    # Get port from environment or default to 8000
    port = int(os.environ.get('PORT', 8000))
    
    print("=" * 60)
    print(f"API Server starting on http://0.0.0.0:{port}")
    print("=" * 60)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=False)
