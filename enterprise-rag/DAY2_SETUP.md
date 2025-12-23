# Day 2 Setup Guide

## Environment Setup

1. **Create `.env` file** in the `enterprise-rag/` directory:
```
GOOGLE_API_KEY=your-google-api-key-here
OPENAI_API_KEY=your-openai-key-for-embeddings
```

2. **Install updated requirements**:
```bash
pip install -r requirements.txt
```

## Running the System

```bash
cd enterprise-rag
python app.py
```

## Test Cases

Try these questions to validate the system:

1. **Question with answer:** "What is our AWS spending limit?"
   - Expected: Should answer with high/medium confidence and cite source

2. **Question with answer:** "When was the AWS policy last updated?"
   - Expected: Should answer with confidence and cite source

3. **Negative case:** "Who approved the AWS budget?"
   - Expected: "I don't know based on the provided documents."
   - Sources: None
   - Confidence: Low

## What Changed

- **LLM Migration:** OpenAI → Gemini Flash 1.5
- **Hallucination Control:** Strict prompt prevents outside knowledge use
- **Source Attribution:** Clean display of document filenames
- **Confidence Scoring:** High (≥2 sources), Medium (1 source), Low (0 sources)
- **Negative Case Handling:** Forces "I don't know" response when confidence is Low
