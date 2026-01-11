# 📋 INSTALLATION CHECKLIST

Use this checklist to ensure everything is properly set up.

---

## Pre-Installation Requirements

### System Requirements
- [ ] macOS, Linux, or Windows with WSL
- [ ] 4GB RAM minimum
- [ ] 1GB free disk space
- [ ] Internet connection (for package installation)

### Software Requirements
- [ ] Python 3.9 or higher installed
  ```bash
  python --version  # Should show 3.9+
  ```
- [ ] Node.js 18 or higher installed
  ```bash
  node --version    # Should show 18+
  ```
- [ ] npm or yarn installed
  ```bash
  npm --version     # Should show 8+
  ```
- [ ] pip installed
  ```bash
  pip --version     # Should be included with Python
  ```

### API Keys
- [ ] Google API key obtained
  - Visit: https://makersuite.google.com/app/apikey
  - Create new API key
  - Enable "Generative Language API"

---

## Backend Setup (Python)

### 1. Navigate to Backend Directory
- [ ] Open terminal
- [ ] Run: `cd enterprise-rag`
- [ ] Verify location with `pwd`

### 2. Install Python Dependencies
- [ ] Run: `pip install -r requirements.txt`
- [ ] Wait for installation to complete
- [ ] No errors should appear

### 3. Install Flask (NEW)
- [ ] Run: `pip install flask flask-cors`
- [ ] Verify installation: `python -c "import flask"`
- [ ] Should complete without error

### 4. Configure Environment
- [ ] Create `.env` file in `enterprise-rag/` directory
- [ ] Add line: `GOOGLE_API_KEY=your_api_key_here`
- [ ] Replace `your_api_key_here` with actual key
- [ ] Save file

### 5. Prepare Documents
- [ ] Check `data/raw/` directory exists
- [ ] Add at least one `.md` or `.txt` file
- [ ] Example: `aws_budget_policy.md` should be present

### 6. Test Backend Startup
- [ ] Run: `python api_server.py`
- [ ] Wait for initialization
- [ ] Should see: "Running on http://0.0.0.0:8000"
- [ ] Should see: "QA chain initialized successfully"
- [ ] No errors should appear

### 7. Test Backend Health
- [ ] Keep backend running
- [ ] Open new terminal
- [ ] Run: `curl http://localhost:8000/health`
- [ ] Should return: `{"status":"healthy","qa_chain_initialized":true}`

---

## Frontend Setup (Next.js)

### 1. Navigate to Frontend Directory
- [ ] Open new terminal (keep backend running!)
- [ ] Run: `cd enterprise-rag-frontend`
- [ ] Verify location with `pwd`

### 2. Install Node Dependencies
- [ ] Run: `npm install`
- [ ] Wait for installation (may take 1-2 minutes)
- [ ] Should see "added XXX packages"
- [ ] No errors should appear

### 3. Verify Environment Configuration
- [ ] Check `.env.local` file exists
- [ ] Should contain: `BACKEND_URL=http://localhost:8000`
- [ ] No changes needed (already configured)

### 4. Test Frontend Startup
- [ ] Run: `npm run dev`
- [ ] Should see: "Ready in X.Xs"
- [ ] Should see: "Local: http://localhost:3000"
- [ ] No errors should appear

### 5. Test Frontend in Browser
- [ ] Open browser
- [ ] Navigate to: http://localhost:3000
- [ ] Should see chat interface
- [ ] Should see "Enterprise AI Knowledge Assistant" header
- [ ] Status should show "Connected" (green dot)

---

## Integration Testing

### 1. Chat Functionality
- [ ] Type: "What documents do you have?"
- [ ] Press Enter
- [ ] Loading indicator appears
- [ ] AI response appears within 5 seconds
- [ ] Response includes answer
- [ ] Sources shown (if applicable)
- [ ] Confidence level shown

### 2. Upload Functionality
- [ ] Click paperclip icon (📎)
- [ ] Select a `.md` or `.txt` file
- [ ] Upload progress shown
- [ ] Success message appears: "✅ Successfully uploaded..."
- [ ] No errors appear

### 3. Error Handling
- [ ] Stop backend (Ctrl+C in backend terminal)
- [ ] Try to send a message in frontend
- [ ] Status changes to "Disconnected" (red dot)
- [ ] Error message appears
- [ ] No app crash

### 4. Backend Recovery
- [ ] Restart backend: `python api_server.py`
- [ ] Wait for "Running on http://0.0.0.0:8000"
- [ ] Refresh browser (Cmd/Ctrl+R)
- [ ] Status changes to "Connected" (green)
- [ ] Can send messages again

---

## Common Issues & Solutions

### Issue: Python version too old
**Solution**:
```bash
# Install Python 3.9+
# macOS: brew install python@3.9
# Ubuntu: sudo apt install python3.9
# Windows: Download from python.org
```

### Issue: Node.js version too old
**Solution**:
```bash
# Install Node.js 18+
# Visit: https://nodejs.org/
# Or use nvm: nvm install 18
```

### Issue: `Module not found: flask`
**Solution**:
```bash
cd enterprise-rag
pip install flask flask-cors
```

### Issue: `npm install` fails
**Solution**:
```bash
cd enterprise-rag-frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: Port 8000 already in use
**Solution**:
```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

### Issue: Port 3000 already in use
**Solution**:
```bash
# Start on different port
npm run dev -- -p 3001
# Then visit: http://localhost:3001
```

### Issue: Backend can't find documents
**Solution**:
```bash
# Check documents exist
ls enterprise-rag/data/raw/
# Should show at least one file
# If empty, add a .md or .txt file
```

### Issue: Frontend can't connect to backend
**Solution**:
```bash
# Verify backend is running
curl http://localhost:8000/health
# Check .env.local has correct URL
cat enterprise-rag-frontend/.env.local
# Should show: BACKEND_URL=http://localhost:8000
```

### Issue: Google API quota exceeded
**Solution**:
- Wait 24 hours for quota reset
- OR use different API key
- OR enable billing on Google Cloud project

---

## Final Verification

### Backend Checklist
- [ ] Backend terminal shows no errors
- [ ] Can access http://localhost:8000/health
- [ ] QA chain initialized successfully
- [ ] Vector store loaded

### Frontend Checklist
- [ ] Frontend terminal shows no errors
- [ ] Can access http://localhost:3000
- [ ] Chat interface displays correctly
- [ ] Status shows "Connected"

### Integration Checklist
- [ ] Can send messages
- [ ] AI responds correctly
- [ ] Sources displayed
- [ ] Confidence shown
- [ ] Can upload files
- [ ] Upload success shown

---

## Success Criteria

✅ **Installation is successful if**:
1. Both servers start without errors
2. Health check returns success
3. Browser shows chat interface
4. Can send a message and get response
5. Can upload a file successfully

---

## Next Steps After Installation

1. **Read Documentation**:
   - [ ] QUICKSTART.md - Quick reference
   - [ ] ARCHITECTURE.md - System design
   - [ ] DEMO_GUIDE.md - Testing scenarios

2. **Prepare for Demo**:
   - [ ] Upload 2-3 relevant documents
   - [ ] Test sample questions
   - [ ] Practice demo flow

3. **Customize** (Optional):
   - [ ] Add more documents
   - [ ] Modify UI colors (tailwind.config.ts)
   - [ ] Add custom prompts

---

## Support

If you encounter issues not listed here:
1. Check terminal outputs for error messages
2. Check browser console (F12) for errors
3. Review SETUP_GUIDE.md for detailed instructions
4. Verify all prerequisites are met

---

**Installation Complete! Ready to Demo! 🚀**

Date Completed: ______________
Tested By: ______________
Notes: ______________
