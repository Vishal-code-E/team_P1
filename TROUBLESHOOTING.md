# 🔧 TROUBLESHOOTING GUIDE

Quick solutions to common issues.

---

## Table of Contents
1. [Backend Issues](#backend-issues)
2. [Frontend Issues](#frontend-issues)
3. [Integration Issues](#integration-issues)
4. [Performance Issues](#performance-issues)
5. [Browser Issues](#browser-issues)
6. [Deployment Issues](#deployment-issues)

---

## Backend Issues

### Backend won't start

**Symptoms**: Error when running `python api_server.py`

**Common Causes**:

1. **Missing Flask**
   ```
   Error: ModuleNotFoundError: No module named 'flask'
   ```
   **Solution**:
   ```bash
   pip install flask flask-cors
   ```

2. **Missing other dependencies**
   ```
   Error: ModuleNotFoundError: No module named 'langchain'
   ```
   **Solution**:
   ```bash
   cd enterprise-rag
   pip install -r requirements.txt
   ```

3. **Python version too old**
   ```
   Error: SyntaxError or f-string issues
   ```
   **Solution**:
   ```bash
   python --version  # Must be 3.9+
   # Upgrade Python if needed
   ```

4. **Missing API key**
   ```
   Error: API key not found
   ```
   **Solution**:
   ```bash
   # Create .env file in enterprise-rag/
   echo "GOOGLE_API_KEY=your_key_here" > .env
   ```

---

### Vectorstore initialization fails

**Symptoms**: "Creating new vector store..." never completes

**Solutions**:

1. **No documents found**
   ```bash
   # Add documents to data/raw/
   ls data/raw/
   # Should show at least one .md or .txt file
   ```

2. **Quota exceeded**
   ```
   Error: 429 Quota exceeded
   ```
   - Wait 24 hours
   - Use different API key
   - Enable billing on Google Cloud

3. **Corrupted vectorstore**
   ```bash
   # Delete and recreate
   rm -rf data/vectorstore
   python api_server.py
   ```

---

### Port 8000 already in use

**Symptoms**: "Address already in use"

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
# Edit api_server.py, change last line:
# app.run(host='0.0.0.0', port=8001, debug=True)
```

---

## Frontend Issues

### Frontend won't start

**Symptoms**: Error when running `npm run dev`

**Common Causes**:

1. **Dependencies not installed**
   ```
   Error: Cannot find module 'next'
   ```
   **Solution**:
   ```bash
   npm install
   ```

2. **Node version too old**
   ```
   Error: Unsupported engine
   ```
   **Solution**:
   ```bash
   node --version  # Must be 18+
   # Upgrade Node.js if needed
   ```

3. **Corrupted node_modules**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Port 3000 in use**
   ```bash
   # Use different port
   npm run dev -- -p 3001
   ```

---

### Build errors

**Symptoms**: TypeScript or build errors

**Solutions**:

1. **Type errors**
   ```bash
   # Check tsconfig.json is correct
   # Re-install dependencies
   npm install
   ```

2. **Missing types**
   ```bash
   npm install --save-dev @types/react @types/node
   ```

3. **Cache issues**
   ```bash
   rm -rf .next
   npm run dev
   ```

---

## Integration Issues

### Frontend can't connect to backend

**Symptoms**: "❌ Sorry, I encountered an error" or "Disconnected" status

**Diagnosis**:
```bash
# Test 1: Is backend running?
curl http://localhost:8000/health

# Test 2: Check environment variable
cat .env.local
# Should show: BACKEND_URL=http://localhost:8000

# Test 3: Check browser console (F12)
# Look for CORS or network errors
```

**Solutions**:

1. **Backend not running**
   ```bash
   cd enterprise-rag
   python api_server.py
   ```

2. **Wrong backend URL**
   ```bash
   # Edit .env.local
   echo "BACKEND_URL=http://localhost:8000" > .env.local
   # Restart frontend
   ```

3. **CORS issues**
   - Backend should have `CORS(app)` enabled
   - Check `api_server.py` has `from flask_cors import CORS`
   - Restart both servers

4. **Firewall blocking**
   - Allow connections to ports 3000 and 8000
   - Try accessing from same machine first

---

### Chat not working

**Symptoms**: Messages don't send or no response

**Diagnosis**:
```bash
# Check backend logs (terminal running api_server.py)
# Look for error messages

# Check browser console (F12 > Console)
# Look for JavaScript errors or failed requests
```

**Solutions**:

1. **Backend errors**
   - Check backend terminal for error traces
   - Restart backend if needed

2. **Network errors**
   - Check backend is on port 8000: `curl http://localhost:8000/health`
   - Refresh browser page

3. **JavaScript errors**
   - Hard refresh: Cmd/Ctrl + Shift + R
   - Clear browser cache
   - Try different browser

---

### Upload not working

**Symptoms**: File upload fails or returns error

**Solutions**:

1. **Invalid file type**
   - Only .md, .pdf, .txt allowed
   - Check file extension

2. **File too large**
   - Default limit: 16MB
   - Compress or split file

3. **Backend permission issues**
   ```bash
   # Check write permissions
   ls -la data/raw/
   # Should be writable
   chmod -R 755 data/raw/
   ```

4. **Backend not re-indexing**
   - Check backend logs during upload
   - Should show "Re-indexing documents..."
   - May take 30-60 seconds for large files

---

## Performance Issues

### Slow responses

**Symptoms**: AI takes >10 seconds to respond

**Causes**:

1. **First request after startup**
   - First request initializes models
   - Subsequent requests faster

2. **Large document collection**
   - More documents = slower retrieval
   - Consider limiting to most relevant docs

3. **API rate limiting**
   - Google API has rate limits
   - Responses slowed when approaching limit

4. **Network latency**
   - Check internet connection
   - Google API calls require internet

**Solutions**:
- Wait for warmup (first request)
- Reduce number of documents
- Upgrade Google API quota
- Use caching (LangChain supports this)

---

### High memory usage

**Symptoms**: Backend using >2GB RAM

**Causes**:
- Large vectorstore
- Many documents indexed
- Embeddings cached in memory

**Solutions**:
```bash
# Reduce document set
# Keep only essential documents in data/raw/

# Restart backend periodically
# Clears memory cache
```

---

## Browser Issues

### UI looks broken

**Symptoms**: Layout issues, missing styles

**Solutions**:

1. **CSS not loading**
   ```bash
   # Hard refresh
   Cmd/Ctrl + Shift + R
   ```

2. **Tailwind not compiled**
   ```bash
   cd enterprise-rag-frontend
   rm -rf .next
   npm run dev
   ```

3. **Browser compatibility**
   - Use Chrome, Firefox, or Safari
   - Update to latest version
   - Avoid Internet Explorer

---

### Can't type in input box

**Symptoms**: Input box disabled or unresponsive

**Solutions**:

1. **AI is responding**
   - Input disabled while AI processes
   - Wait for response to complete

2. **JavaScript error**
   - Check console (F12)
   - Refresh page
   - Clear cache

3. **Focus issue**
   - Click directly in input box
   - Reload page

---

### Messages not scrolling

**Symptoms**: Can't see latest messages

**Solutions**:
- Scroll down manually
- Refresh page
- Check browser console for errors

---

## Deployment Issues

### Vercel deployment fails

**Symptoms**: Build errors on Vercel

**Solutions**:

1. **Environment variables**
   - Add `BACKEND_URL` in Vercel dashboard
   - Use production backend URL

2. **Build settings**
   ```
   Framework Preset: Next.js
   Build Command: npm run build
   Output Directory: .next
   Node Version: 18.x
   ```

3. **Missing dependencies**
   - Ensure `package.json` is committed
   - Run `npm install` locally first

---

### Backend won't deploy

**Symptoms**: Cloud deployment fails

**Solutions**:

1. **Missing requirements**
   ```bash
   # Ensure requirements.txt is complete
   pip freeze > requirements.txt
   ```

2. **Port binding**
   ```python
   # In api_server.py, use environment port
   port = int(os.environ.get('PORT', 8000))
   app.run(host='0.0.0.0', port=port)
   ```

3. **Vectorstore path**
   - Use persistent storage for vectorstore
   - Or rebuild on each deploy

---

## Emergency Recovery

### Complete Reset

If nothing works, start fresh:

```bash
# Backend
cd enterprise-rag
rm -rf data/vectorstore
pip install -r requirements.txt
python api_server.py

# Frontend
cd enterprise-rag-frontend
rm -rf node_modules .next
npm install
npm run dev
```

---

## Getting Help

### Before asking for help:

1. **Check logs**
   - Backend terminal output
   - Browser console (F12)
   - Network tab (F12 > Network)

2. **Try basic debugging**
   - Restart both servers
   - Refresh browser
   - Check ports (8000, 3000)

3. **Verify setup**
   - Review INSTALLATION_CHECKLIST.md
   - Confirm all requirements met

### What to include:

- Error message (exact text)
- Steps to reproduce
- Terminal output
- Browser console errors
- System info (OS, Python version, Node version)

---

## Quick Diagnostic Commands

```bash
# Check Python version
python --version

# Check Node version
node --version

# Check backend health
curl http://localhost:8000/health

# Check frontend running
curl http://localhost:3000

# List documents
ls enterprise-rag/data/raw/

# Check vectorstore exists
ls enterprise-rag/data/vectorstore/

# Check ports in use
lsof -i :3000
lsof -i :8000

# Check Python packages
pip list | grep -E "flask|langchain|chromadb"

# Check Node packages
cd enterprise-rag-frontend && npm list --depth=0
```

---

## Common Error Messages

### `EADDRINUSE: address already in use`
**Solution**: Port in use, kill process or use different port

### `ModuleNotFoundError: No module named 'X'`
**Solution**: Missing Python package, run `pip install X`

### `Cannot find module 'X'`
**Solution**: Missing Node package, run `npm install`

### `429 Resource has been exhausted`
**Solution**: Google API quota exceeded, wait or change key

### `Failed to fetch`
**Solution**: Backend not running or CORS issue

### `Unexpected token`
**Solution**: JavaScript syntax error, check browser compatibility

---

**Most issues are solved by restarting both servers and refreshing the browser.** 🔄
