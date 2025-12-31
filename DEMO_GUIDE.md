# 🎯 DEMO & TESTING GUIDE

## Pre-Demo Checklist

### 1. Environment Setup
- [ ] Python 3.9+ installed
- [ ] Node.js 18+ installed
- [ ] Google API key configured in `.env`
- [ ] Both servers can start without errors

### 2. Data Preparation
- [ ] At least 2-3 documents in `data/raw/`
- [ ] Vectorstore initialized successfully
- [ ] Test questions prepared
- [ ] Extra documents ready for upload demo

### 3. System Health
- [ ] Backend starts on port 8000
- [ ] Frontend starts on port 3000
- [ ] Health check returns success
- [ ] No console errors
- [ ] Status shows "Connected"

---

## Test Scenarios

### Scenario 1: Basic Chat Interaction

**Test**: Ask a simple question about existing documents

**Steps**:
1. Open http://localhost:3000
2. Type: "What documents do you have access to?"
3. Press Enter

**Expected**:
- Loading indicator appears
- AI responds within 5 seconds
- Response shows sources and confidence
- No errors in console

**Success Criteria**:
- ✅ Answer is relevant
- ✅ Sources are listed
- ✅ Confidence level displayed
- ✅ Timestamp shown

---

### Scenario 2: Document Upload

**Test**: Upload a new document and ask about it

**Steps**:
1. Click paperclip icon (📎)
2. Select a `.md` file
3. Wait for success message
4. Ask a question about the uploaded document

**Expected**:
- Upload progress shown
- Success notification appears
- Backend re-indexes documents
- AI can answer questions about new document

**Success Criteria**:
- ✅ File uploads successfully
- ✅ Green success notification shown
- ✅ New document is searchable
- ✅ AI provides accurate answers

---

### Scenario 3: Error Handling

**Test**: Frontend behavior when backend is down

**Steps**:
1. Stop the Python backend (Ctrl+C)
2. Try to send a message
3. Try to upload a file

**Expected**:
- Status changes to "Disconnected" (red)
- Error message shown
- No app crashes
- Graceful error display

**Success Criteria**:
- ✅ Clear error messages
- ✅ UI remains functional
- ✅ No console crashes
- ✅ Can retry when backend restarts

---

### Scenario 4: Intent Routing

**Test**: Different types of questions

**Steps**:
1. Ask: "Hello, how are you?" (conversational)
2. Ask: "What is the AWS budget policy?" (retrieval)
3. Ask: "Who won the Super Bowl?" (out-of-scope)

**Expected**:
- Conversational: Direct answer, no sources
- Retrieval: Answer with sources, high confidence
- Out-of-scope: "I don't know based on provided documents"

**Success Criteria**:
- ✅ Intent routing works correctly
- ✅ Different responses for different intents
- ✅ Sources shown only for retrieval

---

### Scenario 5: Answer Verification

**Test**: AI doesn't hallucinate

**Steps**:
1. Ask a question not covered in documents
2. Check if AI refuses vs. invents answer

**Expected**:
- AI says "I don't know"
- Low confidence shown
- No made-up sources

**Success Criteria**:
- ✅ No hallucinations
- ✅ Honest "I don't know" responses
- ✅ Confidence accurately reflects knowledge

---

## Performance Testing

### Load Time
- **Target**: < 3 seconds first load
- **Test**: Open in incognito, measure load time
- **Tool**: Chrome DevTools (Network tab)

### Response Time
- **Target**: 2-5 seconds per query (depends on backend)
- **Test**: Ask 5 questions, measure average
- **Tool**: Browser console timestamps

### Upload Time
- **Target**: < 10 seconds for small files (<1MB)
- **Test**: Upload 1MB .md file
- **Tool**: Watch success notification

---

## Browser Compatibility

Test in:
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari

**Expected**: Works identically in all browsers

---

## Responsive Design Testing

Test on:
- [ ] Desktop (1920x1080)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

**Expected**: Layout adapts, all features accessible

**Tool**: Chrome DevTools > Device Toolbar

---

## Demo Script (5 Minutes)

### Minute 1: Introduction
"This is MemOrg AI - Your Organization's Memory - powered by RAG and Agentic AI. It intelligently answers questions about your internal documents with source verification and no hallucinations."

### Minute 2: Basic Interaction
1. Show welcome screen
2. Click suggested question
3. Highlight AI response, sources, confidence

### Minute 3: Agentic Behavior
1. Ask conversational question → Show direct answer
2. Ask out-of-scope question → Show refusal
3. Ask retrieval question → Show full RAG pipeline

### Minute 4: Document Upload
1. Upload new document (live)
2. Show re-indexing process
3. Ask question about new document
4. Highlight sources include new file

### Minute 5: Technical Deep-Dive
1. Show architecture (if asked)
2. Explain frontend/backend separation
3. Highlight no hallucinations
4. Show error handling (optional)

---

## Common Questions from Judges

**Q: How do you prevent hallucinations?**
A: Two-layer approach:
1. Intent routing decides if question is answerable
2. Answer verifier validates claims against sources
3. If validation fails, we return "I don't know"

**Q: Can it handle multiple users?**
A: Current version is single-user. Production would add:
- User authentication
- Session management
- Per-user chat history

**Q: How do you handle large documents?**
A: Documents are chunked into 1000-token segments, embedded, and stored in a vector database for semantic search.

**Q: What if the API quota is exceeded?**
A: Backend detects quota errors and shows clear message. Users can switch API keys or wait for quota reset.

**Q: Why separate frontend and backend?**
A: Clean separation of concerns:
- Frontend = presentation
- Backend = all AI logic
- Easier to scale, test, and maintain

---

## Troubleshooting During Demo

### Issue: Backend not responding

**Quick Fix**:
1. Check terminal: Is it running?
2. Visit http://localhost:8000/health
3. Restart if needed: `python api_server.py`

### Issue: Frontend shows old data

**Quick Fix**:
1. Hard refresh: Cmd/Ctrl + Shift + R
2. Clear browser cache
3. Restart frontend: Stop + `npm run dev`

### Issue: Upload fails

**Quick Fix**:
1. Check file type (.md, .pdf, .txt only)
2. Check file size (< 16MB)
3. Check backend logs for errors

---

## Post-Demo Debrief

### What Went Well
- [ ] UI was responsive and smooth
- [ ] AI responses were accurate
- [ ] Upload worked on first try
- [ ] No errors or crashes
- [ ] Judges understood architecture

### What Could Improve
- [ ] Response time could be faster
- [ ] More documents for variety
- [ ] Better error messages
- [ ] More visual polish

---

## Success Metrics

**Demo is successful if**:
- ✅ All core features work (chat, upload, sources)
- ✅ No crashes or errors
- ✅ Judges understand the value proposition
- ✅ Agentic behavior is clear
- ✅ UI impresses (looks professional)

**Bonus points**:
- ⭐ Show live document upload
- ⭐ Demonstrate error handling
- ⭐ Explain architecture clearly
- ⭐ Show no hallucinations
- ⭐ Highlight enterprise readiness

---

**Practice makes perfect. Test thoroughly. Demo confidently.** 🎯
