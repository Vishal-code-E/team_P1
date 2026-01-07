# QUICK REFERENCE - Enterprise RAG Platform
# ==========================================

## REBUILD VECTOR DATABASE

```bash
cd /Users/vishale/team_P1/enterprise-rag

# Delete old vector database
rm -rf data/vectorstore/*

# Start API server (will rebuild automatically)
source venv/bin/activate
python api_server.py
```

**Expected Output:**
```
Found 8 documents in data/raw
Creating new vector store...
Loaded 106 document chunks
Vector store created and persisted
✓ QA chain initialized successfully
✓ Ready to answer questions from 8 documents
```

---

## START BACKEND LOCALLY

```bash
cd /Users/vishale/team_P1/enterprise-rag
source venv/bin/activate
python api_server.py
```

**Server will start on:** http://0.0.0.0:8000

**Health check:** http://localhost:8000/api/health

---

## TEST BACKEND (curl commands)

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Test Chat - AWS Budget Question
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is the monthly AWS budget for Engineering production environment?"}'
```

### Test Chat - Out-of-Scope Question
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is the weather today?"}'
```

### Test Chat - Security Question
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Is MFA required for AWS Console access?"}'
```

---

## DEPLOY TO RENDER

### Update Code
```bash
git add .
git commit -m "Stabilize backend for demo"
git push origin main
```

### Render Auto-Deploys
- Render detects push to `main` branch
- Runs: `pip install -r requirements.txt`
- Starts: `gunicorn api_server:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`

### Set Environment Variables (Render Dashboard)
1. Go to: https://dashboard.render.com
2. Select: `memorg-ai-backend` service
3. Navigate to: Environment tab
4. Add/Update:
   - `OPENAI_API_KEY` = your_actual_key_here
   - `OPENAI_MODEL` = gpt-4-turbo

### Check Deployment Status
- Render Dashboard → Logs tab
- Look for: "✓ QA chain initialized successfully"

---

## FRONTEND DEPLOYMENT

### Frontend URL
```
https://enterprise-rag-frontend-pux7d4p5y.vercel.app
```

### Update Backend URL (if needed)
1. Go to Vercel dashboard
2. Select project: `enterprise-rag-frontend`
3. Settings → Environment Variables
4. Update: `NEXT_PUBLIC_API_URL` = https://YOUR-BACKEND.onrender.com

---

## TROUBLESHOOTING

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -ti:8000

# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Restart backend
source venv/bin/activate
python api_server.py
```

### Vector database missing
```bash
# Check if vector database exists
ls -la data/vectorstore/

# If empty, delete and restart (will rebuild)
rm -rf data/vectorstore/*
python api_server.py
```

### Wrong Python version
```bash
# Check Python version (should be 3.9+)
python --version

# Use Python 3 explicitly
python3 api_server.py
```

### Missing dependencies
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt
```

### OpenAI API errors
```bash
# Check if API key is set
echo $OPENAI_API_KEY

# Set API key (if missing)
export OPENAI_API_KEY=your_key_here

# Or add to .env file
echo "OPENAI_API_KEY=your_key_here" > .env
```

---

## FILE LOCATIONS

### Enterprise Documents
```
data/raw/
├── aws_cloud_budget_policy.md
├── information_security_policy.md
├── employee_leave_policy.md
├── incident_response_plan.md
├── employee_onboarding_guide.md
├── devops_deployment_guidelines.md
├── aws_budget_policy.md (old)
└── REC-CFP_-_Google_Docs.pdf (old)
```

### Vector Database
```
data/vectorstore/
└── chroma.sqlite3 (auto-generated)
```

### Code Files
```
api_server.py           # Main Flask API server
rag/qa_chain.py         # QA chain with GPT-4
rag/retriever.py        # Vector store management
agent/intent_router.py  # Intent classification
agent/answer_verifier.py # Answer validation
```

---

## DEMO QUESTIONS (Copy-Paste Ready)

1. **AWS Budget:**
   ```
   What is the monthly AWS budget for the Engineering department's production environment?
   ```

2. **Security MFA:**
   ```
   Is multi-factor authentication required for accessing AWS Console?
   ```

3. **PTO Policy:**
   ```
   How many PTO days do employees get after 5 years of service?
   ```

4. **Incident Response:**
   ```
   What is the response time required for a P0 critical incident?
   ```

5. **Deployment Schedule:**
   ```
   When are production deployments allowed?
   ```

6. **Out-of-Scope (Should Refuse):**
   ```
   What's the weather like today?
   ```

---

## METRICS TO MONITOR

### During Demo
- Response time: Should be <5 seconds
- Confidence: Should be "High" for policy questions
- Sources: Should cite specific .md files
- Errors: Should be zero

### Backend Logs
```bash
# Watch logs in real-time
tail -f backend.log

# Or if running locally
python api_server.py | tee backend.log
```

### Key Log Messages
- ✅ "✓ QA chain initialized successfully"
- ✅ "[CHAT START] Question: ..."
- ✅ "[RAG] Retrieved X source documents"
- ✅ "[Verifier] Answer VALID"
- ❌ "[ERROR] ..." (investigate immediately)

---

## EMERGENCY CONTACTS

### Services
- **Render:** https://dashboard.render.com
- **Vercel:** https://vercel.com/dashboard
- **OpenAI Status:** https://status.openai.com

### Documentation
- **Demo Script:** DEMO_SCRIPT.md
- **Readiness Checklist:** READINESS_CHECKLIST.md
- **Technical Reference:** TECHNICAL_REFERENCE.md

---

## QUICK WINS

### If demo is going well:
1. Show source citations
2. Demonstrate confidence scoring
3. Test out-of-scope refusal
4. Show conversational handling
5. Highlight zero hallucinations

### If demo has issues:
1. Stay calm
2. Check backend logs
3. Test with curl commands
4. Fall back to prepared answers
5. Explain the fix (shows expertise)

---

**Last Updated:** January 7, 2026  
**Print this page for quick reference during demo!**
