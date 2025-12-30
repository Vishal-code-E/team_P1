# Ingestion Platform Quick Start

## Installation

Ensure dependencies are installed:

```bash
cd enterprise-rag
pip install -r requirements.txt
```

## Basic Usage

### 1. Initialize Orchestrator

```python
from enterprise_rag.ingest.orchestrator import IngestionOrchestrator

orchestrator = IngestionOrchestrator(
    base_path="data",
    vectorstore_path="data/vectorstore",
    log_level="INFO"
)
```

### 2. Ingest Data

**File Upload:**
```python
record = orchestrator.ingest_file(
    "path/to/document.pdf",
    uploaded_by="user@example.com"
)
```

**Slack Channel:**
```python
# Requires SLACK_BOT_TOKEN env var
record = orchestrator.ingest_slack_channel(
    channel_id="C123456",
    days_history=30
)
```

**Confluence Space:**
```python
# Requires CONFLUENCE_* env vars
record = orchestrator.ingest_confluence_space(
    space_key="ENG",
    limit=500
)
```

### 3. Create Vector Index

```python
# First time
result = orchestrator.initialize_vector_index()

# Add new data
result = orchestrator.update_vector_index(batch_paths)

# Full rebuild
result = orchestrator.rebuild_vector_index(backup=True)
```

### 4. Check Status

```python
# Index info
info = orchestrator.get_index_info()
print(f"Documents: {info['document_count']}")

# Ingestion history
history = orchestrator.get_ingestion_history(limit=10)
```

## Environment Variables

```bash
# .env file
SLACK_BOT_TOKEN=xoxb-...
CONFLUENCE_URL=https://your-domain.atlassian.net
CONFLUENCE_USERNAME=user@example.com
CONFLUENCE_API_TOKEN=...
GOOGLE_API_KEY=...
```

## Run Demo

```bash
cd enterprise-rag
python examples/ingestion_demo.py
```

## Directory Structure After Ingestion

```
data/
├── raw/
│   ├── slack/
│   │   └── 20241230_151030_engineering/
│   ├── confluence/
│   │   └── 20241230_160045_ENG/
│   └── uploads/
│       └── 20241230_170000/
├── ingestion_logs/
│   └── slack_api_C123456_20241230_151030.json
└── vectorstore/
    └── chroma.sqlite3
```

## Troubleshooting

**Check logs:**
```bash
tail -f logs/ingestion_*.log
```

**View ingestion history:**
```python
history = orchestrator.get_ingestion_history()
for record in history:
    print(f"{record['status']}: {record['source_type']}")
```

**Rebuild corrupted index:**
```python
orchestrator.rebuild_vector_index(backup=True)
```

## Full Documentation

See: [INGESTION_PLATFORM.md](./INGESTION_PLATFORM.md)
