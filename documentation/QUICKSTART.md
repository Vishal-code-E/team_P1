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
# Quick Reference Guide

## Installation

```bash
# Clone repository
git clone https://github.com/Vishal-code-E/team_P1.git
cd team_P1

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# Run
python main.py
```

## Quick Commands

### Start Application
```bash
# Linux/Mac
./start.sh

# Windows
start.bat

# Docker
docker-compose up -d
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/health` | GET | Health check |
| `/api/status` | GET | System status |
| `/api/query` | POST | Query knowledge base |
| `/api/upload/pdf` | POST | Upload PDFs |
| `/api/load/confluence` | POST | Load Confluence data |
| `/api/load/slack` | POST | Load Slack data |
| `/docs` | GET | API documentation |

## Example Queries

### Query via API
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is our AWS spending limit?"}'
```

### Upload PDF
```bash
curl -X POST http://localhost:8000/api/upload/pdf \
  -F "files=@document.pdf"
```

### Load Confluence
```bash
curl -X POST http://localhost:8000/api/load/confluence \
  -H "Content-Type: application/json" \
  -d '{"space_key": "ENG", "limit": 100}'
```

## Python Usage

```python
from src.core.rag import rag_system
from src.core.vector_store import vector_store
from src.connectors.pdf_loader import pdf_loader
from langchain.docstore.document import Document

# Add a document
doc = Document(
    page_content="AWS spending limit is $50,000/month",
    metadata={"source": "Policy", "source_type": "confluence"}
)
vector_store.add_documents([doc])

# Query
result = rag_system.query("What is the AWS spending limit?")
print(result['answer'])
print(result['sources'])

# Load PDF
documents = pdf_loader.load_pdf("document.pdf")
vector_store.add_documents(documents)
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `CONFLUENCE_URL` | No | Confluence URL |
| `CONFLUENCE_USERNAME` | No | Confluence username |
| `CONFLUENCE_API_TOKEN` | No | Confluence API token |
| `SLACK_BOT_TOKEN` | No | Slack bot token |
| `APP_PORT` | No | Port (default: 8000) |

## File Structure

```
team_P1/
├── src/                    # Source code
│   ├── api/               # API routes
│   ├── connectors/        # Data connectors
│   └── core/              # Core RAG system
├── static/                # Frontend assets
├── templates/             # HTML templates
├── data/chroma/          # Vector database
├── uploads/              # Uploaded files
├── main.py               # Entry point
└── requirements.txt      # Dependencies
```

## Troubleshooting

### Module not found
```bash
pip install -r requirements.txt
```

### Port in use
```bash
# Change port in .env
APP_PORT=8080
```

### OpenAI errors
```bash
# Verify API key
echo $OPENAI_API_KEY
```

### Confluence connection fails
- Use full URL: `https://domain.atlassian.net`
- Use email as username for Cloud
- Verify API token permissions

### Slack connection fails
- Ensure bot has `channels:history` scope
- Use channel ID, not name
- Add bot to channel first

## Getting Help

- **Documentation**: See README.md
- **API Docs**: Visit `/docs` when running
- **Development**: See DEVELOPMENT.md
- **Deployment**: See DEPLOYMENT.md
- **Issues**: GitHub Issues

## Common Use Cases

### 1. Ask about AWS costs
```
Question: "What's our AWS spending limit?"
```

### 2. Find development guidelines
```
Question: "What's our code review process?"
```

### 3. Search Slack history
```
Question: "What did the team discuss about the new feature?"
```

### 4. Query company policies
```
Question: "What's our remote work policy?"
```

## Performance Tips

1. **Chunk size**: 1000 tokens works well for most use cases
2. **Embedding model**: `text-embedding-3-small` is fast and accurate
3. **LLM model**: `gpt-4-turbo-preview` for best quality
4. **Search results**: 4 documents provides good context

## Security Checklist

- [ ] Never commit `.env` file
- [ ] Use strong API tokens
- [ ] Enable HTTPS in production
- [ ] Add authentication for public deployments
- [ ] Limit API token permissions
- [ ] Regular security updates

## Next Steps

1. ✓ Install and configure
2. ✓ Upload your first documents
3. ✓ Ask your first question
4. ✓ Integrate Confluence/Slack
5. ✓ Deploy to production

For detailed guides, see the documentation files in the repository.
