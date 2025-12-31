"""
Flask API Server for Enterprise RAG Chatbot
Provides REST endpoints for the Next.js frontend
"""

import os
import shutil
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Import existing chatbot modules
from ingest.load_docs import load_and_chunk_documents
from rag.retriever import create_vectorstore, load_vectorstore
from rag.qa_chain import create_qa_chain
from agent.intent_router import route_intent, get_direct_answer
from agent.answer_verifier import verify_answer

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for Vercel frontend and localhost dev
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

# Global QA chain (initialized on startup)
qa_chain = None


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
    """Initialize the QA chain on startup"""
    global qa_chain
    
    try:
        if os.path.exists(VECTORSTORE_PATH) and os.listdir(VECTORSTORE_PATH):
            print("Loading existing vector store...")
            vectorstore = load_vectorstore(VECTORSTORE_PATH)
        else:
            print("Creating new vector store...")
            documents = load_and_chunk_documents(UPLOAD_FOLDER)
            print(f"Loaded {len(documents)} document chunks")
            vectorstore = create_vectorstore(documents, VECTORSTORE_PATH)
            print("Vector store created and persisted")
        
        qa_chain = create_qa_chain(vectorstore)
        print("QA chain initialized successfully")
        return True
        
    except Exception as e:
        print(f"Initialization error: {str(e)}")
        qa_chain = None
        return False


@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'qa_chain_initialized': qa_chain is not None
    })


@app.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint
    Expects: {"message": "user question"}
    Returns: {"answer": "...", "sources": [...], "confidence": "..."}
    """
    if not qa_chain:
        return jsonify({
            'answer': 'System not initialized. Please check backend logs.',
            'sources': [],
            'confidence': 'Low',
            'error': 'QA chain not initialized'
        }), 500
    
    try:
        data = request.get_json()
        question = data.get('message', '').strip()
        
        if not question:
            return jsonify({'error': 'Message is required'}), 400
        
        # INTENT ROUTING: Decide action before RAG
        intent_decision = route_intent(question)
        decision = intent_decision.get("decision")
        
        print(f"[Intent Router] Decision: {decision}")
        
        # Handle based on intent decision
        if decision == "ANSWER_DIRECTLY":
            # Conversational query - answer without retrieval
            answer = get_direct_answer(question)
            return jsonify({
                'answer': answer,
                'sources': [],
                'confidence': 'High'
            })
            
        elif decision == "REFUSE":
            # Out-of-scope query - refuse safely
            return jsonify({
                'answer': "I don't know based on the provided documents.",
                'sources': [],
                'confidence': 'Low'
            })
        
        # decision == "RETRIEVE_AND_ANSWER": proceed to RAG pipeline
        print("[Agent] Proceeding to document retrieval...")
        
        # Get answer from QA chain
        result = qa_chain.invoke({"query": question})
        
        # Get source documents and calculate confidence
        source_docs = result.get("source_documents", [])
        confidence = get_confidence(source_docs)
        answer = result["result"]
        
        # ANSWER VERIFICATION: Validate answer is fully supported by sources
        is_valid = verify_answer(question, answer, source_docs)
        
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
        
        # Format response
        return jsonify({
            'answer': answer,
            'sources': format_sources(source_docs),
            'confidence': confidence
        })
        
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({
            'answer': f'Error processing request: {str(e)}',
            'sources': [],
            'confidence': 'Low',
            'error': str(e)
        }), 500


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    File upload endpoint
    Accepts multipart/form-data with 'file' field
    Returns: {"success": true, "message": "..."}
    """
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
    
    try:
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
        
        # Reinitialize QA chain with new documents
        success = initialize_qa_chain()
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Successfully uploaded and indexed {filename}'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'File uploaded but indexing failed. Check backend logs.'
            }), 500
            
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Upload failed: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("Initializing Enterprise RAG API Server...")
    print("=" * 60)
    
    # Initialize QA chain on startup
    initialize_qa_chain()
    
    # Get port from environment (Render, Railway, etc.) or default to 8000
    port = int(os.environ.get('PORT', 8000))
    
    print("=" * 60)
    print(f"API Server starting on http://0.0.0.0:{port}")
    print("=" * 60)
    
    # Run Flask app (debug=False to avoid reloader issues)
    app.run(host='0.0.0.0', port=port, debug=False)
