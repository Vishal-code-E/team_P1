# Enterprise RAG Chatbot

A minimal RAG chatbot that answers internal finance/dev questions from company documents.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your Google API key in `.env`:
```
GOOGLE_API_KEY=your_actual_api_key
```

## Run

```bash
python app.py
```

## Example Usage

```
You: What is our AWS spending limit?

ANSWER:
The monthly AWS spending limit for the organization is ₹18,00,000. Alerts are triggered at 80% usage.

SOURCES:
- aws_budget_policy.md
```

## Project Structure

- `ingest/load_docs.py` - Document loading and chunking
- `rag/retriever.py` - Embeddings and vector store
- `rag/qa_chain.py` - QA chain with retrieval
- `data/raw/` - Source documents
- `data/vectorstore/` - Persisted vector database
- `app.py` - CLI chatbot
