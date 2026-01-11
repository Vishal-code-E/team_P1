# System Architecture

## Enterprise RAG + Agentic AI with Next.js Frontend

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│                     http://localhost:3000                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    NEXT.JS FRONTEND (CLIENT)                     │
├─────────────────────────────────────────────────────────────────┤
│  UI Components:                                                  │
│  • ChatMessage.tsx    → Display user/AI messages                │
│  • ChatInput.tsx      → Input + file upload                     │
│  • SourceBadge.tsx    → Show document sources                   │
│  • ConfidenceBadge.tsx → Show confidence level                  │
│  • LoadingIndicator.tsx → AI thinking animation                 │
│                                                                  │
│  Main Page:                                                      │
│  • app/page.tsx       → Chat interface + state management       │
│                                                                  │
│  API Routes (Proxy):                                             │
│  • /api/chat          → Forward to Python backend               │
│  • /api/upload        → Forward file uploads to Python          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP Requests
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PYTHON BACKEND (BRAIN)                         │
│                  Flask API Server (Port 8000)                    │
├─────────────────────────────────────────────────────────────────┤
│  API Endpoints:                                                  │
│  • POST /chat         → Process user questions                  │
│  • POST /upload       → Upload docs + re-index                  │
│  • GET /health        → Health check                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AGENTIC AI LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  Intent Router:                                                  │
│  • Analyzes question intent                                     │
│  • Decides: RETRIEVE | REFUSE | ANSWER_DIRECTLY                 │
│                                                                  │
│  Answer Verifier:                                                │
│  • Validates answer against sources                             │
│  • Prevents hallucinations                                      │
│  • Ensures factual accuracy                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       RAG PIPELINE                               │
├─────────────────────────────────────────────────────────────────┤
│  Document Ingestion:                                             │
│  • Load documents from data/raw/                                │
│  • Chunk into 1000 token segments                               │
│  • Generate embeddings (Google Gemini)                          │
│                                                                  │
│  Vector Store (ChromaDB):                                        │
│  • Store document embeddings                                    │
│  • Semantic similarity search                                   │
│  • Retrieve top-k relevant chunks                               │
│                                                                  │
│  QA Chain (LangChain):                                           │
│  • Combine query + retrieved docs                               │
│  • Generate answer via LLM                                      │
│  • Return answer + sources                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GOOGLE GEMINI API                             │
│                  (LLM + Embeddings)                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Request Flow: User Question

```
1. User types question in ChatInput
   ↓
2. Frontend: POST /api/chat {"message": "..."}
   ↓
3. Next.js API Route: Proxy to backend
   ↓
4. Python Backend: Receive at /chat endpoint
   ↓
5. Intent Router: Analyze question intent
   ├── REFUSE → Return "I don't know"
   ├── ANSWER_DIRECTLY → Return conversational answer
   └── RETRIEVE_AND_ANSWER → Continue to RAG
       ↓
6. RAG Pipeline:
   ├── Query vectorstore for relevant docs
   ├── Retrieve top chunks
   ├── Send to LLM with context
   └── Get answer
       ↓
7. Answer Verifier: Validate answer
   ├── Valid → Return answer
   └── Invalid → Return "I don't know"
       ↓
8. Backend: Format response
   {
     "answer": "...",
     "sources": ["doc1.md"],
     "confidence": "High"
   }
   ↓
9. Frontend: Display in ChatMessage component
```

---

## Request Flow: Document Upload

```
1. User selects file in ChatInput
   ↓
2. Frontend: POST /api/upload (multipart/form-data)
   ↓
3. Next.js API Route: Forward file to backend
   ↓
4. Python Backend: Receive at /upload endpoint
   ↓
5. Save file to data/raw/
   ↓
6. Delete old vectorstore
   ↓
7. Re-ingest all documents
   ├── Load all files from data/raw/
   ├── Chunk documents
   ├── Generate embeddings
   └── Create new vectorstore
       ↓
8. Re-initialize QA chain
   ↓
9. Backend: Return success
   {
     "success": true,
     "message": "Successfully uploaded and indexed"
   }
   ↓
10. Frontend: Show success notification
```

---

## Technology Stack

### Frontend
- **Framework**: Next.js 14 (React 18)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **API**: Next.js API Routes (serverless functions)
- **State**: React Hooks (useState, useEffect)

### Backend
- **Framework**: Flask (Python web framework)
- **CORS**: Flask-CORS (cross-origin requests)
- **RAG**: LangChain (orchestration)
- **LLM**: Google Gemini Pro
- **Embeddings**: Google Gemini Embeddings
- **Vector DB**: ChromaDB
- **Agents**: Custom LangChain chains

---

## Data Flow

### Documents
```
User uploads .md/.pdf/.txt
    ↓
Saved to: data/raw/<filename>
    ↓
Ingested by: ingest/load_docs.py
    ↓
Chunked into: ~1000 token segments
    ↓
Embedded by: Google Gemini Embeddings
    ↓
Stored in: data/vectorstore/ (ChromaDB)
```

### Queries
```
User question
    ↓
Intent routing
    ↓
Query vectorstore (semantic search)
    ↓
Retrieve top 3 most similar chunks
    ↓
Combine with question → prompt
    ↓
Send to Google Gemini Pro
    ↓
Generate answer
    ↓
Verify answer validity
    ↓
Return with sources + confidence
```

---

## Security & Separation of Concerns

### ✅ Frontend Responsibilities
- Display UI
- Handle user input
- Show loading states
- Display errors
- Upload files
- **NO BUSINESS LOGIC**

### ✅ Backend Responsibilities
- Intent routing
- Document retrieval
- Answer generation
- Answer verification
- Confidence calculation
- **ALL BUSINESS LOGIC**

### 🔒 Security Notes
- API keys: Backend only (GOOGLE_API_KEY)
- LLM calls: Backend only
- Vector DB: Backend only
- CORS: Configured for localhost only
- File validation: Both frontend and backend
- No authentication (out of scope)

---

## Deployment Architecture

### Development
```
Frontend: localhost:3000 (npm run dev)
Backend:  localhost:8000 (python api_server.py)
```

### Production
```
Frontend: Vercel / AWS / Netlify
Backend:  Cloud Run / EC2 / Heroku
Vector DB: Persistent volume or managed service
```

---

## Key Design Decisions

1. **Frontend as Pure Client**
   - No LLM logic on frontend
   - All AI behavior controlled by backend
   - Frontend just displays results

2. **API Routes as Proxy**
   - Next.js API routes forward to Python
   - Keeps backend URL hidden from browser
   - Enables future authentication middleware

3. **Stateless Backend**
   - Each request is independent
   - No session management needed
   - Scales horizontally easily

4. **Agentic Workflow**
   - Intent routing before retrieval
   - Answer verification after generation
   - Confidence scoring for transparency

5. **Single-Page Application**
   - No routing complexity
   - All interactions in one view
   - Simple state management

---

## Performance Considerations

- **Frontend**: Static pages cached by Next.js
- **Backend**: QA chain initialized once on startup
- **Vector DB**: Persisted to disk, loaded once
- **LLM Calls**: Cached by LangChain (optional)
- **File Uploads**: Re-indexing blocks until complete

---

**This architecture ensures clean separation, scalability, and maintainability.**
