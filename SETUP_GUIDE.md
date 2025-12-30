# 🚀 SETUP GUIDE - Enterprise RAG Frontend + Backend

## Complete System Startup (Both Servers)

This guide shows you how to run the **complete system** with both the Python backend and Next.js frontend.

---

## ⚡ Quick Start (5 Minutes)

### Step 1: Start Python Backend

```bash
# Navigate to backend directory
cd enterprise-rag

# Install Flask dependencies (FIRST TIME ONLY)
pip install flask flask-cors

# Start the API server
python api_server.py
```

**Expected Output**:
```
Initializing Enterprise RAG API Server...
============================================================
Loading existing vector store...
QA chain initialized successfully
============================================================
API Server starting on http://localhost:8000
============================================================
 * Running on http://0.0.0.0:8000
```

**✅ Backend is ready** when you see "Running on http://0.0.0.0:8000"

---

### Step 2: Start Next.js Frontend (New Terminal)

```bash
# Open NEW terminal window
cd enterprise-rag-frontend

# Install dependencies (FIRST TIME ONLY)
npm install

# Start development server
npm run dev
```

**Expected Output**:
```
  ▲ Next.js 14.2.5
  - Local:        http://localhost:3000
  - Network:      http://192.168.x.x:3000

 ✓ Ready in 2.1s
```

**✅ Frontend is ready** when you see "Ready in X.Xs"

---

### Step 3: Open Browser

Navigate to: **http://localhost:3000**

You should see the Enterprise AI Knowledge Assistant chat interface!

---

## 🔍 Verify Everything Works

### Test 1: Health Check
Visit http://localhost:8000/health in your browser.

**Expected Response**:
```json
{
  "status": "healthy",
  "qa_chain_initialized": true
}
```

### Test 2: Send a Chat Message
In the frontend (http://localhost:3000), type:
```
What documents do you have access to?
```

You should get a response from the AI!

### Test 3: Upload a Document
1. Click the paperclip icon (📎) in the chat input
2. Select a `.md`, `.pdf`, or `.txt` file
3. Wait for "✅ Successfully uploaded..." message
4. Ask a question about the uploaded document

---

## 📁 Project Structure

```
team_P1/
├── enterprise-rag/              # Python Backend
│   ├── api_server.py           # Flask API (NEW)
│   ├── app.py                  # CLI chatbot (original)
│   ├── requirements.txt        # Python dependencies
│   ├── agent/                  # Intent routing & verification
│   ├── rag/                    # RAG pipeline
│   ├── ingest/                 # Document loading
│   └── data/
│       ├── raw/                # Upload documents here
│       └── vectorstore/        # Vector DB
│
└── enterprise-rag-frontend/     # Next.js Frontend
    ├── app/                    # Next.js app directory
    │   ├── page.tsx           # Main chat page
    │   ├── layout.tsx         # Root layout
    │   └── api/               # API routes (proxy)
    ├── components/             # React components
    ├── types/                  # TypeScript types
    ├── package.json           # Node dependencies
    └── .env.local             # Environment config
```

---

## 🛠️ Troubleshooting

### Issue: Backend fails to start

**Error**: `ModuleNotFoundError: No module named 'flask'`

**Solution**:
```bash
cd enterprise-rag
pip install flask flask-cors
```

---

### Issue: Frontend can't connect to backend

**Symptoms**: 
- Chat shows "❌ Sorry, I encountered an error"
- Status shows "Disconnected" in top right

**Solution**:
1. Check backend is running: http://localhost:8000/health
2. Verify `.env.local` in frontend:
   ```
   BACKEND_URL=http://localhost:8000
   ```
3. Restart both servers

---

### Issue: Port 3000 or 8000 already in use

**Solution**:

For **port 8000** (backend):
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

For **port 3000** (frontend):
```bash
# Start on different port
npm run dev -- -p 3001
```

---

### Issue: Vectorstore not found

**Error**: Backend shows "Creating new vector store..."

**Solution**:
This is normal for first run. The backend will:
1. Load documents from `data/raw/`
2. Create embeddings
3. Save to `data/vectorstore/`

**Wait 30-60 seconds** for initialization to complete.

---

### Issue: Upload returns error

**Symptoms**: Upload fails with 500 error

**Checklist**:
- ✅ File is .md, .pdf, or .txt
- ✅ Backend has write permissions to `data/raw/`
- ✅ Backend is running (check http://localhost:8000/health)
- ✅ File size < 16MB

---

## 🎯 Production Deployment

### Backend (Python/Flask)

**Option 1: Gunicorn (Recommended)**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 api_server:app
```

**Option 2: Docker**
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "api_server:app"]
```

---

### Frontend (Next.js)

**Option 1: Vercel (1-Click Deploy)**
```bash
npm install -g vercel
vercel
```

**Option 2: Docker**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

**Option 3: Build + Deploy**
```bash
npm run build
npm run start  # Production mode on port 3000
```

---

## 🔐 Environment Variables

### Backend (.env)
```bash
GOOGLE_API_KEY=your_google_api_key_here
```

### Frontend (.env.local)
```bash
# Development
BACKEND_URL=http://localhost:8000

# Production
BACKEND_URL=https://your-backend-domain.com
```

---

## 📊 System Requirements

### Backend
- Python 3.9+
- 2GB RAM minimum
- 500MB disk space

### Frontend
- Node.js 18+
- 1GB RAM minimum
- 100MB disk space

---

## 🎓 Demo Checklist

Before presenting:

- [ ] Both servers running
- [ ] Test chat with sample question
- [ ] Upload a document successfully
- [ ] Sources and confidence display correctly
- [ ] No errors in browser console
- [ ] No errors in terminal outputs
- [ ] Prepare 3-5 sample questions
- [ ] Have extra documents ready to upload

---

## 🆘 Still Having Issues?

### Check Logs

**Backend logs**: Check the terminal where you ran `python api_server.py`

**Frontend logs**: Check browser console (F12 > Console)

### Common Log Messages

**Backend**:
- ✅ "QA chain initialized successfully" - Good!
- ❌ "Initialization error" - Check vectorstore and API key
- ✅ "[Intent Router] Decision: RETRIEVE_AND_ANSWER" - Working!

**Frontend**:
- ✅ "POST /api/chat 200" - Success
- ❌ "POST /api/chat 500" - Backend error
- ❌ "Failed to fetch" - Backend not running

---

## 📞 Support

For competition/demo support, check:
1. README.md files in each directory
2. Code comments in key files
3. Error messages in terminal/console

---

**System Ready! Build with Discipline. Demo with Confidence.** 🚀
