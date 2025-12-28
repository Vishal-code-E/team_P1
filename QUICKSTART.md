# 🚀 QUICK START - 30 Seconds

## Start Both Servers

### Terminal 1 - Backend
```bash
cd enterprise-rag
pip install flask flask-cors  # First time only
python api_server.py
```

### Terminal 2 - Frontend
```bash
cd enterprise-rag-frontend
npm install  # First time only
npm run dev
```

### Open Browser
```
http://localhost:3000
```

---

## ✅ Success Checklist

- [ ] Backend shows "Running on http://0.0.0.0:8000"
- [ ] Frontend shows "Ready in X.Xs"
- [ ] Browser opens to chat interface
- [ ] Status indicator shows "Connected" (green dot)
- [ ] Can send a test message
- [ ] Can upload a file

---

## 🎯 Demo Tips

1. **Prepare**: Upload 2-3 documents before demo
2. **Test**: Try sample questions beforehand
3. **Highlight**: Show sources and confidence levels
4. **Upload**: Demonstrate live document upload
5. **Error**: Show graceful error handling (stop backend)

---

## 📂 Project Structure

```
team_P1/
├── enterprise-rag/              ← Python Backend
│   ├── api_server.py           ← Flask API (START THIS)
│   └── data/raw/               ← Upload docs here
│
├── enterprise-rag-frontend/     ← Next.js Frontend
│   ├── app/page.tsx           ← Main chat page
│   └── components/            ← UI components
│
├── SETUP_GUIDE.md              ← Full setup instructions
├── ARCHITECTURE.md             ← System architecture
└── QUICKSTART.md               ← This file
```

---

## 🛠️ Common Issues

**Backend won't start**: Install Flask
```bash
pip install flask flask-cors
```

**Frontend can't connect**: Check backend is running
```bash
curl http://localhost:8000/health
```

**Port in use**: Change port
```bash
npm run dev -- -p 3001
```

---

## 📞 Need Help?

- Full setup: See `SETUP_GUIDE.md`
- Architecture: See `ARCHITECTURE.md`
- Frontend docs: See `enterprise-rag-frontend/README.md`

**Built for judges. Built to impress.** 🏆
