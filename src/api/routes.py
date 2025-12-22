"""FastAPI application and routes."""
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil

from ..core.config import settings
from ..core.rag import rag_system
from ..core.vector_store import vector_store
from ..connectors.pdf_loader import pdf_loader
from ..connectors.confluence_connector import confluence_connector
from ..connectors.slack_connector import slack_connector


# Create FastAPI app
app = FastAPI(
    title="AI Knowledge Base + Chatbot",
    description="RAG-based chatbot for querying company knowledge from Confluence, PDFs, and Slack",
    version="1.0.0"
)

# Add CORS middleware
# Note: For production, configure specific allowed origins instead of "*"
# and set allow_credentials=False when using wildcard origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Disabled for security with wildcard origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Pydantic models
class QueryRequest(BaseModel):
    """Request model for querying the knowledge base."""
    question: str
    source_type: Optional[str] = None


class QueryResponse(BaseModel):
    """Response model for query results."""
    answer: str
    sources: List[dict]
    question: str


class ConfluenceLoadRequest(BaseModel):
    """Request model for loading Confluence data."""
    space_key: Optional[str] = None
    page_id: Optional[str] = None
    limit: int = 100


class SlackLoadRequest(BaseModel):
    """Request model for loading Slack data."""
    channel_id: str
    days: int = 30
    limit: int = 1000


class StatusResponse(BaseModel):
    """Response model for system status."""
    status: str
    document_count: int
    confluence_configured: bool
    slack_configured: bool


# Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main chat interface."""
    try:
        with open("templates/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <head><title>AI Knowledge Base</title></head>
            <body>
                <h1>AI Knowledge Base + Chatbot</h1>
                <p>Frontend not found. Please access the API at /docs</p>
                <a href="/docs">API Documentation</a>
            </body>
        </html>
        """


@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """Get system status and configuration."""
    try:
        doc_count = vector_store.get_collection_count()
    except:
        doc_count = 0
    
    return StatusResponse(
        status="operational",
        document_count=doc_count,
        confluence_configured=confluence_connector.is_configured(),
        slack_configured=slack_connector.is_configured()
    )


@app.post("/api/query", response_model=QueryResponse)
async def query_knowledge_base(request: QueryRequest):
    """
    Query the knowledge base with a question.
    
    Args:
        request: Query request with question and optional source filter
        
    Returns:
        Answer with source citations
    """
    try:
        if request.source_type:
            result = rag_system.query_with_filter(
                request.question,
                request.source_type
            )
        else:
            result = rag_system.query(request.question)
        
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload/pdf")
async def upload_pdf(files: List[UploadFile] = File(...)):
    """
    Upload and process PDF files.
    
    Args:
        files: List of PDF files to upload
        
    Returns:
        Status message with number of documents processed
    """
    try:
        uploaded_files = []
        
        # Save uploaded files
        os.makedirs("uploads", exist_ok=True)
        
        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
            
            file_path = f"uploads/{file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append(file_path)
        
        # Process PDFs
        documents = pdf_loader.load_multiple_pdfs(uploaded_files)
        
        # Add to vector store
        doc_ids = vector_store.add_documents(documents)
        
        return {
            "status": "success",
            "message": f"Processed {len(files)} PDF file(s)",
            "documents_added": len(doc_ids),
            "files": [f.filename for f in files]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/load/confluence")
async def load_confluence(request: ConfluenceLoadRequest):
    """
    Load data from Confluence.
    
    Args:
        request: Confluence load request with space_key or page_id
        
    Returns:
        Status message with number of documents processed
    """
    try:
        if not confluence_connector.is_configured():
            raise HTTPException(
                status_code=400,
                detail="Confluence is not configured. Please set credentials in .env file."
            )
        
        documents = []
        
        if request.space_key:
            documents = confluence_connector.load_space(
                request.space_key,
                request.limit
            )
        elif request.page_id:
            documents = confluence_connector.load_page(request.page_id)
        else:
            raise HTTPException(
                status_code=400,
                detail="Either space_key or page_id must be provided"
            )
        
        # Add to vector store
        doc_ids = vector_store.add_documents(documents)
        
        return {
            "status": "success",
            "message": "Confluence data loaded successfully",
            "documents_added": len(doc_ids)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/load/slack")
async def load_slack(request: SlackLoadRequest):
    """
    Load data from Slack.
    
    Args:
        request: Slack load request with channel_id
        
    Returns:
        Status message with number of documents processed
    """
    try:
        if not slack_connector.is_configured():
            raise HTTPException(
                status_code=400,
                detail="Slack is not configured. Please set SLACK_BOT_TOKEN in .env file."
            )
        
        documents = slack_connector.load_channel_history(
            request.channel_id,
            request.days,
            request.limit
        )
        
        # Add to vector store
        doc_ids = vector_store.add_documents(documents)
        
        return {
            "status": "success",
            "message": f"Loaded {len(documents)} conversations from Slack",
            "documents_added": len(doc_ids)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
