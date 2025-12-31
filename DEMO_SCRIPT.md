# DEMO QUICK REFERENCE

**MemOrg AI - 5-Minute Demo Script**

**Live Demo**: https://memorg-ai.vercel.app

---

## 🎯 ELEVATOR PITCH (30 seconds)

*"This is MemOrg AI - Your Organization's Memory. It transforms scattered documentation into instant, verified answers. Unlike basic chatbots, our system makes intelligent decisions about how to respond—it refuses out-of-scope questions, retrieves from your knowledge base when needed, and verifies every answer against source documents before responding. No hallucinations, no hunting through wikis."*

**Tech Stack**: OpenAI GPT-4, Flask backend, Next.js frontend  
**Key Differentiator**: Agentic decision-making with answer verification

---

## 🚀 DEMO FLOW (5 minutes)

### 1. Show the UI (30 seconds)
*"Modern ChatGPT-style interface with confidence badges and source attribution."*

- Navigate to http://localhost:3000
- Point out chat interface
- Show document upload area
- Highlight confidence indicator

### 2. Demonstrate Agentic Behavior (90 seconds)

**A. REFUSE Path - Out of Scope**
```
You: "What's the weather in San Francisco?"
Agent: "I'm focused on your organization's knowledge base. 
        I can't answer questions about weather or general topics 
        outside your documents."
```
*"Notice it REFUSED rather than hallucinating. This is autonomous decision-making."*

**B. RETRIEVE Path - Knowledge Base Query**
```
You: "What's our AWS spending limit?"
Agent: "According to the AWS Budget Policy document, 
        your spending limit is $10,000 per month..."
        [Shows source: aws_budget_policy.md]
        [Confidence: High]
```
*"It retrieved the context, verified the claim, and cited the source. No hallucination possible."*

**C. ANSWER_DIRECTLY Path - General Knowledge**
```
You: "What is Kubernetes?"
Agent: "Kubernetes is a container orchestration platform... 
        (Note: This is general knowledge, not from your documents)"
```
*"Explicitly tells you when it's using general knowledge vs. your data."*

### 3. Show Multi-Source Ingestion (60 seconds)

**Terminal Demo:**
```bash
python examples/ingestion_demo.py
```

*"Watch it ingest from multiple sources:"*
- ✅ Slack conversations (preserves threads)
- ✅ Confluence wiki pages (HTML → clean text)
- ✅ Uploaded PDFs (text extraction)

*"All raw data preserved here:"*
```bash
ls -la data/raw/slack/
ls -la data/raw/confluence/
ls -la data/raw/uploads/
```

*"Audit trail logged:"*
```bash
tail data/ingestion_logs/ingestion_*.log
```

### 4. Show Authentication (30 seconds)

**Admin User (full access):**
```bash
curl -H "X-API-Key: demo_admin_key_12345" \
     http://localhost:8000/api/health
# Returns: 200 OK
```

**Query-Only User (denied on ingest):**
```bash
curl -H "X-API-Key: demo_user1_key_67890" \
     -X POST http://localhost:8000/api/ingest
# Returns: 403 Forbidden - Insufficient permissions
```

*"Three permission levels: QUERY, INGEST, ADMIN. Full isolation."*

### 5. Show Conversation Memory (30 seconds)

```
You: "What's our AWS budget?"
Agent: "$10,000 per month according to aws_budget_policy.md"

You: "What about the approval process?"
Agent: "For the AWS budget you asked about, approvals require..."
```

*"Notice it remembered the context—user-scoped conversations with 10-message history."*

---

## 🎓 KEY TALKING POINTS

### Why This is "Agentic"
- **Autonomous Routing**: LLM decides REFUSE/RETRIEVE/ANSWER paths
- **Self-Verification**: Validates own answers against sources
- **No Hallucinations**: Refuses when uncertain
- **Transparent**: Explains reasoning (source citations, confidence levels)

### Production-Ready Architecture
- **Immutable Storage**: Raw data never overwritten → safe re-indexing
- **Audit Trails**: Every ingestion logged
- **Versioning**: Track index versions, rollback capability
- **Auth & Isolation**: Token-based with user-scoped data

### Honest Scope
*"This is designed for enterprise demos and small teams, not production SaaS."*

**Limitations We Explicitly Document:**
1. OpenAI API dependency (can swap to Azure/Anthropic)
2. Local storage only (migration path to S3/GCS)
3. No real-time sync (webhook infrastructure designed)
4. Limited memory (10 messages, 7-day retention)

*"Every limitation has a documented migration path. We're showing production patterns, not claiming to be production SaaS."*

---

## 📊 DIFFERENTIATORS TABLE

| Feature | Standard RAG | This Platform |
|---------|-------------|---------------|
| **Decision Making** | Simple search | Autonomous routing |
| **Verification** | None | Answer verification |
| **Sources** | Single type | Slack + Confluence + PDFs |
| **Storage** | Direct to vector | Raw → Processed → Vector |
| **Re-indexing** | Manual | One-command rebuild |
| **Auth** | None | Token + permissions |
| **Memory** | Stateless | User-scoped conversations |
| **Audit Trail** | None | Complete logs |

---

## 🔑 DEMO CREDENTIALS

### API Keys
```bash
# Admin (all permissions)
X-API-Key: demo_admin_key_12345

# Query-only user (Alice)
X-API-Key: demo_user1_key_67890

# Ingest + query user (Bob)
X-API-Key: demo_user2_key_abcde
```

### Test Documents
- `data/raw/aws_budget_policy.md` - AWS spending limits
- Ingestion demo creates Slack/Confluence examples

---

## 🎬 CLOSING STATEMENT

*"What you just saw is an Agentic AI platform that combines production-grade architecture with demo-appropriate scope. The agent makes autonomous decisions, verifies its own answers, and never hallucinates. Multi-source ingestion with immutable storage means you can re-index safely as models improve. Token-based auth and user-scoped conversations provide enterprise security within demo constraints."*

*"This isn't just a chatbot—it's an intelligent knowledge assistant that knows when to retrieve, when to refuse, and when to verify. Built on OpenAI and Flask, designed for enterprise demos, ready for scrutiny."*

---

## ⚠️ TROUBLESHOOTING (If Demo Issues)

### Backend Won't Start
```bash
cd enterprise-rag
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
python api_server.py
```

### Frontend Won't Start
```bash
cd enterprise-rag-frontend
npm install
npm run dev
```

### No Documents to Query
```bash
cd enterprise-rag
python examples/ingestion_demo.py
```

---

## 📞 FOLLOW-UP QUESTIONS

**Q: "How does this scale to millions of documents?"**  
A: "Current architecture uses local Chroma—designed for demo. Migration path documented: swap storage to S3, vector DB to Pinecone/Weaviate, async processing pipeline. All abstraction layers in place."

**Q: "What about SSO/enterprise auth?"**  
A: "Current API key auth is demo-appropriate. Auth module (`core/auth.py`) designed for JWT/SSO integration—just swap the user database and token validation."

**Q: "How do you prevent hallucinations?"**  
A: "Two mechanisms: (1) Intent router refuses out-of-scope queries, (2) Answer verifier validates every claim against retrieved sources. If verification fails, system refuses to answer."

**Q: "What's the cost at scale?"**  
A: "OpenAI API costs: ~$0.01 per query (GPT-4), ~$0.0001 per embedding. For 10K queries/month, ~$100. Can reduce 80% by using GPT-3.5 or local models (Ollama)."

---

**Demo Time**: 5 minutes  
**Prep Time**: 30 seconds (start backend + frontend)  
**Wow Factor**: High (agentic behavior + source verification)  
**Defensibility**: Maximum (honest limitations, clear architecture)

---

**Ready to impress. Ready for questions. Ready for scrutiny.** 🚀
