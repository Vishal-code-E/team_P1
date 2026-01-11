# MemOrg AI - Backend Deployment Guide (Render)

## ✅ PHASE 1: BACKEND PREPARATION - COMPLETED

### Changes Made to Backend:
1. ✅ Dynamic PORT configuration (reads from environment)
2. ✅ Domain-specific CORS for Vercel frontend
3. ✅ Health check endpoint at `/api/health`
4. ✅ Render configuration file (`render.yaml`)

**Files Modified:**
- `enterprise-rag/api_server.py` - PORT env var + CORS config
- `enterprise-rag/render.yaml` - NEW (deployment config)

---

## 🚀 PHASE 2: DEPLOY BACKEND TO RENDER

### Prerequisites:
- GitHub repository pushed (all latest code)
- Render account (free tier: https://render.com)
- OpenAI API key ready

### Step-by-Step Deployment:

**1. Create Render Account & Service**

Go to: https://render.com

```bash
# Login/Signup → Dashboard → "New +" → "Web Service"
```

**2. Connect GitHub Repository**

- Click "Connect GitHub"
- Authorize Render to access your repositories
- Select repository: `team_P1` (or your repo name)
- Click "Connect"

**3. Configure Service Settings**

Fill in the form:

| Field | Value |
|-------|-------|
| **Name** | `memorg-ai-backend` |
| **Region** | Oregon (US West) or closest to you |
| **Branch** | `main` |
| **Root Directory** | `enterprise-rag` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python api_server.py` |

**4. Set Environment Variables**

Click "Advanced" → "Add Environment Variable":

| Key | Value |
|-----|-------|
| `OPENAI_API_KEY` | `sk-proj-...` (your OpenAI key) |
| `PYTHON_VERSION` | `3.9.18` (optional, but recommended) |

**5. Deploy**

- Click "Create Web Service"
- Wait 3-5 minutes for deployment
- Render will:
  1. Clone your repo
  2. Install dependencies
  3. Run `python api_server.py`
  4. Assign a public URL

**Expected URL Format:**
```
https://memorg-ai-backend.onrender.com
```

**6. Verify Backend Deployment**

Test health endpoint:
```bash
curl https://memorg-ai-backend.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "qa_chain_initialized": true
}
```

---

## 🔗 PHASE 3: CONNECT FRONTEND TO BACKEND

### Update Vercel Environment Variable

**Option A: Via Vercel Dashboard (Recommended)**

1. Go to: https://vercel.com/sriram182719-gmailcoms-projects/enterprise-rag-frontend
2. Click "Settings" → "Environment Variables"
3. Find `NEXT_PUBLIC_API_URL` or click "Add New"
4. Set:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://memorg-ai-backend.onrender.com` (your Render URL)
   - **Environment**: Production, Preview, Development (check all)
5. Click "Save"
6. Go to "Deployments" → Click "..." on latest → "Redeploy"

**Option B: Via Vercel CLI**

```bash
cd /Users/vishale/team_P1/enterprise-rag-frontend

# Set environment variable
vercel env add NEXT_PUBLIC_API_URL production

# Paste your Render URL when prompted:
# https://memorg-ai-backend.onrender.com

# Redeploy
vercel --prod
```

---

## ✅ PHASE 4: END-TO-END VERIFICATION

### Verification Checklist

**1. Backend Health Check**
```bash
curl https://memorg-ai-backend.onrender.com/api/health
```
✅ Should return: `{"status": "healthy", "qa_chain_initialized": true}`

**2. Frontend Loads**
- Visit: https://enterprise-rag-frontend-pux7d4p5y.vercel.app
- ✅ Page loads without errors
- ✅ Chat interface appears
- ✅ No CORS errors in browser console (F12 → Console)

**3. Test Chat Functionality**
- Type a question: "What is AWS Budget Policy?"
- Click "Send"
- ✅ Backend receives request (check Render logs)
- ✅ AI response appears
- ✅ Sources shown (if available)
- ✅ Confidence badge displays

**4. Test File Upload (if applicable)**
- Click upload button
- Select a `.md`, `.pdf`, or `.txt` file
- ✅ Upload succeeds
- ✅ File indexed into vector store
- ✅ Can query new content

**5. Check Backend Logs**
```bash
# Go to Render dashboard → Your service → "Logs"
# You should see:
# - "API Server starting on http://0.0.0.0:10000"
# - "QA chain initialized successfully"
# - Incoming requests from frontend
```

**6. Verify No Errors**
- ❌ No CORS errors
- ❌ No ECONNREFUSED errors
- ❌ No 404 errors
- ❌ No authentication errors

---

## 🏗️ FINAL ARCHITECTURE

```
┌─────────────────────────────────────────────────────┐
│                    USER BROWSER                     │
└────────────────────┬────────────────────────────────┘
                     │
                     │ HTTPS
                     ▼
┌─────────────────────────────────────────────────────┐
│           VERCEL (Frontend - Next.js)               │
│  https://enterprise-rag-frontend-pux7d4p5y.vercel.app│
│                                                     │
│  • Serves React UI                                  │
│  • Handles user interactions                        │
│  • Proxies API calls to backend                     │
└────────────────────┬────────────────────────────────┘
                     │
                     │ HTTPS (NEXT_PUBLIC_API_URL)
                     ▼
┌─────────────────────────────────────────────────────┐
│          RENDER (Backend - Flask API)               │
│      https://memorg-ai-backend.onrender.com         │
│                                                     │
│  • /api/health - Health check                       │
│  • /chat       - AI chat endpoint                   │
│  • /upload     - Document ingestion                 │
│                                                     │
│  Components:                                        │
│  ├── Intent Router (decides RAG vs Direct)          │
│  ├── Answer Verifier (validates responses)          │
│  ├── ChromaDB (vector store)                        │
│  └── OpenAI API (GPT-4 + embeddings)                │
└────────────────────┬────────────────────────────────┘
                     │
                     │ HTTPS API Key
                     ▼
┌─────────────────────────────────────────────────────┐
│               OPENAI API                            │
│         (GPT-4 + text-embedding-3-small)            │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 SUCCESS CRITERIA

Your deployment is complete when:

- ✅ **Frontend URL works**: https://enterprise-rag-frontend-pux7d4p5y.vercel.app
- ✅ **Backend URL works**: https://memorg-ai-backend.onrender.com/api/health
- ✅ **Frontend → Backend communication**: No CORS errors
- ✅ **AI responses work**: Chat returns intelligent answers
- ✅ **Sources displayed**: Retrieved documents shown in UI
- ✅ **No localhost dependencies**: Fully cloud-based
- ✅ **Stable URLs**: Both services have persistent public URLs
- ✅ **One product experience**: Seamless user interaction

---

## 🚨 COMMON ISSUES & FIXES

### Issue 1: CORS Errors in Browser Console
```
Access to fetch at 'https://...' from origin 'https://...' has been blocked
```

**Fix:**
- Verify CORS configuration in `api_server.py` includes your Vercel domain
- Check backend logs for CORS-related errors
- Redeploy backend if CORS config was changed

### Issue 2: Backend Health Check Fails
```bash
curl https://memorg-ai-backend.onrender.com/api/health
# Returns 404 or timeout
```

**Fix:**
- Check Render deployment logs for startup errors
- Verify `OPENAI_API_KEY` is set in Render environment variables
- Ensure `Start Command` is `python api_server.py`
- Check Root Directory is set to `enterprise-rag`

### Issue 3: Frontend Shows "System not initialized"
**Fix:**
- Backend QA chain failed to initialize
- Check Render logs: Look for "QA chain initialized successfully"
- Verify vector store exists or can be created
- Check OpenAI API key is valid

### Issue 4: 502 Bad Gateway on Backend
**Fix:**
- Render service crashed during startup
- Check Render logs for Python errors
- Verify all dependencies in `requirements.txt` are installable
- Ensure Python version compatibility (3.9+)

---

## 📊 MONITORING & MAINTENANCE

### Check Backend Health (Anytime)
```bash
curl https://memorg-ai-backend.onrender.com/api/health
```

### View Live Logs
- Render Dashboard → Your Service → "Logs" tab
- Real-time request/response monitoring
- Error tracking

### Redeploy Backend (After Code Changes)
```bash
git add .
git commit -m "Update backend"
git push origin main

# Render auto-deploys on push to main branch
# Or manually trigger: Render Dashboard → "Manual Deploy"
```

### Redeploy Frontend (After Env Var Changes)
```bash
cd enterprise-rag-frontend
vercel --prod
```

---

## 🎉 DEPLOYMENT COMPLETE

**Your MemOrg AI platform is now live!**

- **Frontend**: https://enterprise-rag-frontend-pux7d4p5y.vercel.app
- **Backend**: https://memorg-ai-backend.onrender.com

Share the frontend URL with your team and start using your organization's memory!

---

## 📝 DEPLOYMENT SUMMARY

| Component | Platform | URL | Status |
|-----------|----------|-----|--------|
| Frontend | Vercel | https://enterprise-rag-frontend-pux7d4p5y.vercel.app | ✅ Live |
| Backend | Render | https://memorg-ai-backend.onrender.com | 🚀 Ready to Deploy |
| Database | ChromaDB (on Render) | - | Embedded |
| AI Model | OpenAI GPT-4 | - | API-based |

**Next Steps**: Follow Phase 2 instructions to deploy backend to Render.
