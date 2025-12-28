# Enterprise AI Knowledge Assistant

**RAG + Agentic AI with Professional Next.js Frontend**

Company wikis are where docs go to die. Point this tool at your Confluence, PDFs, and Slack history; ask "What's our AWS spending limit?" and get an instant, source-linked answer instead of ten blue links nobody clicks.

## 🚀 Quick Start (30 Seconds)

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
Navigate to **http://localhost:3000**

---

## ✨ What's New - Professional Frontend

This project now includes a **production-ready Next.js frontend** that provides:

- ✅ **ChatGPT-style interface** - Clean, modern, professional UI
- ✅ **Real-time chat** - Smooth message flow with loading indicators
- ✅ **Document upload** - Drag-and-drop file upload with live re-indexing
- ✅ **Source attribution** - Clear display of document sources
- ✅ **Confidence levels** - Color-coded High/Medium/Low badges
- ✅ **Error handling** - Graceful degradation when backend unavailable
- ✅ **Responsive design** - Works perfectly on desktop, tablet, mobile

---

## 📂 Project Structure

```
team_P1/
├── enterprise-rag/              # Python Backend (RAG + Agents)
│   ├── api_server.py           # Flask API server (NEW)
│   ├── app.py                  # CLI chatbot (original)
│   ├── agent/                  # Intent routing & verification
│   ├── rag/                    # RAG pipeline
│   └── data/                   # Documents & vectorstore
│
├── enterprise-rag-frontend/     # Next.js Frontend (NEW)
│   ├── app/                    # Pages & API routes
│   ├── components/             # React components
│   └── types/                  # TypeScript definitions
│
├── QUICKSTART.md               # 30-second setup guide
├── SETUP_GUIDE.md              # Detailed installation
├── ARCHITECTURE.md             # System architecture
├── DEMO_GUIDE.md               # Testing & demo scenarios
├── VISUAL_GUIDE.md             # Visual diagrams
└── PROJECT_SUMMARY.md          # Complete project summary
```

---

## 🎯 Key Features

### Agentic AI
- **Intent Routing**: Decides whether to retrieve, refuse, or answer directly
- **Answer Verification**: Validates all claims against sources
- **No Hallucinations**: Refuses to answer when uncertain

### RAG Pipeline
- **Document Ingestion**: Markdown, PDF, TXT support
- **Vector Search**: Semantic similarity with ChromaDB
- **LLM Generation**: Google Gemini Pro for answers
- **Source Tracking**: Clear attribution to source documents

### Professional Frontend
- **Modern UI**: ChatGPT-inspired interface
- **Type Safety**: Full TypeScript coverage
- **Responsive**: Mobile-first design with Tailwind CSS
- **Production Ready**: Optimized, accessible, scalable

---

## 🛠️ Technology Stack

**Frontend**:
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- React 18

**Backend**:
- Flask (API server)
- LangChain (RAG orchestration)
- Google Gemini Pro (LLM)
- ChromaDB (Vector database)
- Python 3.9+

---

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 30 seconds
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup instructions
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and data flow
- **[DEMO_GUIDE.md](DEMO_GUIDE.md)** - Testing and demo scenarios
- **[VISUAL_GUIDE.md](VISUAL_GUIDE.md)** - Visual diagrams
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete overview

---

## 🎯 Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Browser shows chat interface
- [ ] Status indicator shows "Connected"
- [ ] Can send a test message
- [ ] Can upload a document
- [ ] AI responds with sources and confidence

---

## 🎓 Demo Tips

1. **Prepare**: Upload 2-3 documents before demo
2. **Test**: Try sample questions beforehand
3. **Highlight**: Show sources and confidence levels
4. **Upload**: Demonstrate live document upload
5. **Error**: Show graceful error handling

---

## 🔒 Security Notes

- All API keys kept on backend only
- No LLM calls from frontend
- File upload validation (client & server)
- CORS configured for localhost
- No authentication (demo scope)

---

## 🚢 Deployment

### Frontend Options
- Vercel (recommended)
- Netlify
- AWS Amplify
- Docker

### Backend Options
- Google Cloud Run
- AWS EC2
- Heroku
- Docker

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for deployment instructions.

---

## 🤝 Contributing

This is a demo/competition project. The frontend was built with:
- **Discipline**: No over-engineering
- **Focus**: Only essential features
- **Quality**: Production-ready code
- **Purpose**: Demo-ready and judge-friendly

---

## 📄 License

See individual component licenses. This project combines open-source technologies for educational/demo purposes.

---

**Built with discipline. Built like a professional product. Ready to impress.** 🚀
