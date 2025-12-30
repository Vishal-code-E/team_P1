# Data Ingestion Platform - Technical Reference

## Component Interaction Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                    IngestionOrchestrator                             │
│                   (High-Level Workflow API)                          │
│                                                                       │
│  Methods:                                                             │
│  - ingest_slack_channel()                                            │
│  - ingest_confluence_space()                                         │
│  - ingest_file()                                                     │
│  - initialize_vector_index()                                         │
│  - rebuild_vector_index()                                            │
└────────┬────────────┬────────────┬──────────────┬───────────────────┘
         │            │            │              │
         ▼            ▼            ▼              ▼
┌─────────────┐ ┌──────────┐ ┌─────────┐  ┌───────────────┐
│   Slack     │ │Confluence│ │Document │  │    Vector     │
│ Ingestion   │ │Ingestion │ │Ingestion│  │   Manager     │
└──────┬──────┘ └────┬─────┘ └────┬────┘  └───────┬───────┘
       │             │            │               │
       │             │            │               │
       └─────────────┴────────────┴───────────────┘
                          │
                          ▼
                ┌──────────────────┐
                │   RawDataStore   │
                │                  │
                │ - create_batch() │
                │ - store_doc()    │
                │ - log()          │
                └────────┬─────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │      Filesystem Storage        │
        │                                │
        │  data/raw/{source}/{batch}/   │
        │    ├── doc.json                │
        │    ├── doc.meta.json           │
        │    └── metadata.json           │
        └────────────────────────────────┘
```

## Data Flow Sequence

### Ingestion Flow

```
User Action
    │
    ▼
┌─────────────────────────────────┐
│ orchestrator.ingest_slack_*()   │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│ SlackIngestion.ingest_*()       │
│ - Fetch from API/files          │
│ - Group by threads              │
│ - Build conversation objects    │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│ storage.create_ingestion_batch()│
│ Returns: batch_path             │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│ For each thread:                │
│   storage.store_raw_document()  │
│   - Save thread.json            │
│   - Save thread.meta.json       │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│ storage.log_ingestion()         │
│ - Create ingestion record       │
│ - Save to ingestion_logs/       │
└─────────────────────────────────┘
```

### Processing & Indexing Flow

```
Vector Index Operation
    │
    ▼
┌──────────────────────────────────┐
│ vector_manager.initialize_index()│
└─────────────┬────────────────────┘
              │
              ▼
┌──────────────────────────────────┐
│ For each batch in raw storage:  │
│   processor.process_batch()      │
└─────────────┬────────────────────┘
              │
              ▼
┌──────────────────────────────────┐
│ DocumentProcessor                │
│ 1. Load raw JSON                 │
│ 2. Load metadata JSON            │
│ 3. Format content                │
│ 4. Chunk text                    │
│ 5. Enrich with metadata          │
│ Returns: List[Document]          │
└─────────────┬────────────────────┘
              │
              ▼
┌──────────────────────────────────┐
│ Chroma.from_documents()          │
│ - Generate embeddings            │
│ - Store in vector DB             │
│ - Preserve metadata              │
└─────────────┬────────────────────┘
              │
              ▼
┌──────────────────────────────────┐
│ Save version info                │
│ vectorstore_version.json         │
└──────────────────────────────────┘
```

## Metadata Lifecycle

```
Source Document
    │
    ▼
┌────────────────────────────────┐
│ DocumentMetadata Object        │
│                                │
│ - source_type: SourceType     │
│ - source_id: str               │
│ - source_name: str             │
│ - ingested_at: datetime        │
│ - source_timestamp: datetime?  │
│ - author: str?                 │
│ - title: str?                  │
│ - url: str?                    │
│ - extra: dict                  │
└──────────┬─────────────────────┘
           │
           │ Stored as JSON
           ▼
┌────────────────────────────────┐
│ {doc}.meta.json                │
│                                │
│ {                              │
│   "source_type": "slack",      │
│   "source_id": "1234.5678",    │
│   "source_name": "#eng",       │
│   "ingested_at": "2024-...",   │
│   "extra": {                   │
│     "channel_id": "C123",      │
│     "participants": [...]      │
│   }                             │
│ }                               │
└──────────┬─────────────────────┘
           │
           │ Loaded during processing
           ▼
┌────────────────────────────────┐
│ LangChain Document.metadata    │
│                                │
│ {                              │
│   "source": "#engineering",    │
│   "source_type": "slack",      │
│   "source_id": "1234.5678",    │
│   "channel_name": "engineering"│
│   "participants": [...]        │
│   "ingested_at": "2024-..."    │
│ }                               │
└──────────┬─────────────────────┘
           │
           │ Embedded with chunks
           ▼
┌────────────────────────────────┐
│ Vector Store Metadata          │
│                                │
│ Retrieved with each chunk      │
│ Used for source attribution    │
└────────────────────────────────┘
```

## Error Handling Strategy

```
Operation
    │
    ├─── Try
    │      │
    │      ▼
    │    Execute
    │      │
    │      ├─── Success ──────────────────┐
    │      │                               │
    │      └─── Exception                  │
    │             │                        │
    │             ▼                        │
    └─── Except                            │
          │                                │
          ├─ Log error                     │
          │  (logger.error())              │
          │                                │
          ├─ Update record                 │
          │  (status = "failed")           │
          │                                │
          └─ Save partial results          │
                                           │
    ┌──────────────────────────────────────┘
    │
    ▼
Finally
    │
    ├─ Complete record
    │  (completed_at = now)
    │
    └─ Log record
       (storage.log_ingestion())
```

**Key Principles:**
1. Never fail silently
2. Always log ingestion records
3. Preserve partial successes
4. Enable recovery from failures

## Storage Layout

```
data/
├── raw/                          # Immutable source data
│   ├── slack/
│   │   └── 20241230_151030_engineering/
│   │       ├── metadata.json     # Batch metadata
│   │       ├── thread_1234567890.json
│   │       ├── thread_1234567890.meta.json
│   │       ├── thread_9876543210.json
│   │       └── thread_9876543210.meta.json
│   │
│   ├── confluence/
│   │   └── 20241230_160045_ENG/
│   │       ├── metadata.json
│   │       ├── page_123456.json
│   │       ├── page_123456.meta.json
│   │       ├── page_234567.json
│   │       └── page_234567.meta.json
│   │
│   └── uploads/
│       └── 20241230_170000/
│           ├── metadata.json
│           ├── document_abc123.pdf
│           ├── document_abc123.json     # Extracted text
│           └── document_abc123.meta.json
│
├── ingestion_logs/               # Audit trail
│   ├── slack_api_C123456_20241230_151030.json
│   ├── confluence_space_ENG_20241230_160045.json
│   └── upload_pdf_20241230_170000.json
│
├── vectorstore/                  # Vector database
│   ├── chroma.sqlite3
│   └── {uuid}/
│       └── ... (Chroma internals)
│
└── vectorstore_version.json      # Index metadata
```

## Class Hierarchy

```
RawDataStore
├── Methods:
│   ├── create_ingestion_batch(source_type, batch_name) → str
│   ├── store_raw_document(batch_path, doc_id, content, metadata) → str
│   ├── store_binary_file(batch_path, filename, content, metadata) → str
│   ├── log_ingestion(record: IngestionRecord)
│   ├── get_ingestion_history(source_type?) → List[IngestionRecord]
│   └── list_batches(source_type) → List[Dict]
│
└── Storage Structure:
    └── {base_path}/raw/{source}/{batch}/

DocumentMetadata (dataclass)
├── source_type: SourceType
├── source_id: str
├── source_name: str
├── ingested_at: datetime
├── source_timestamp: datetime?
├── author: str?
├── title: str?
├── url: str?
└── extra: Dict[str, Any]

IngestionRecord (dataclass)
├── source_type: SourceType
├── ingestion_id: str
├── started_at: datetime
├── completed_at: datetime?
├── documents_ingested: int
├── documents_failed: int
├── status: str
└── source_identifiers: List[str]

SlackIngestion
├── __init__(storage, slack_token?)
├── ingest_export(export_path) → IngestionRecord
├── ingest_channel_api(channel_id, days, limit) → IngestionRecord
└── [Private helpers]

ConfluenceIngestion
├── __init__(storage, url?, username?, token?, cloud?)
├── ingest_space(space_key, limit) → IngestionRecord
├── ingest_page(page_id) → IngestionRecord
└── [Private helpers]

DocumentUploadIngestion
├── __init__(storage)
├── ingest_file(file_path, uploaded_by?) → IngestionRecord
├── ingest_files(file_paths, uploaded_by?) → IngestionRecord
├── ingest_bytes(filename, content, uploaded_by?) → IngestionRecord
└── [Private helpers]

DocumentProcessor
├── __init__(storage, chunk_size, chunk_overlap)
├── process_batch(batch_path) → List[Document]
└── [Private processors per source type]

VectorStoreManager
├── __init__(storage, processor, vectorstore_path, model)
├── initialize_index(source_batches?) → Dict
├── update_index(new_batch_paths) → Dict
├── rebuild_index(source_batches?, backup?) → Dict
├── reindex_source(source_type) → Dict
├── get_index_info() → Dict
└── [Private helpers]

IngestionOrchestrator
├── __init__(base_path, vectorstore_path, chunk_size, log_level)
├── [Slack methods]
│   ├── ingest_slack_export(path)
│   └── ingest_slack_channel(channel_id, days)
├── [Confluence methods]
│   ├── ingest_confluence_space(space_key, limit)
│   └── ingest_confluence_page(page_id)
├── [Document methods]
│   ├── ingest_file(path, uploaded_by?)
│   └── ingest_files(paths, uploaded_by?)
├── [Vector methods]
│   ├── initialize_vector_index()
│   ├── update_vector_index(batch_paths)
│   ├── rebuild_vector_index(backup?)
│   └── get_index_info()
└── [History methods]
    ├── get_ingestion_history(source_type?, limit)
    └── get_source_batches(source_type)
```

## Thread Safety & Concurrency

**Current Implementation: Single-threaded**

- All operations are synchronous
- No concurrent access protection
- File I/O is sequential

**Why this is acceptable for demo/small-team:**
- Simple to reason about
- Easy to debug
- No race conditions
- Adequate for <1000 docs/day

**Path to concurrency (future):**
```python
# Async ingestion
async def ingest_slack_channel_async(channel_id):
    async with aiohttp.ClientSession() as session:
        messages = await fetch_messages(session, channel_id)
        await store_async(messages)

# Parallel processing
with ProcessPoolExecutor() as executor:
    futures = [executor.submit(process_batch, path) for path in batches]
    results = [f.result() for f in futures]
```

## Integration Points with Existing System

```
┌──────────────────────────────┐
│   Existing RAG System        │
├──────────────────────────────┤
│                              │
│  ┌────────────────────────┐  │
│  │ agent/                 │  │
│  │ - intent_router.py     │  │
│  │ - answer_verifier.py   │  │
│  └────────────────────────┘  │
│              │               │
│              │ Uses          │
│              ▼               │
│  ┌────────────────────────┐  │
│  │ rag/                   │  │
│  │ - qa_chain.py          │  │
│  │ - retriever.py         │◄─┼─── UNCHANGED
│  └────────────────────────┘  │
│              │               │
│              │ Queries       │
│              ▼               │
│  ┌────────────────────────┐  │
│  │ Vector Store           │  │
│  │ (Chroma)               │◄─┼─── MANAGED BY
│  └────────────────────────┘  │    NEW PLATFORM
│                              │
└──────────────────────────────┘

┌──────────────────────────────┐
│   New Ingestion Platform     │
├──────────────────────────────┤
│                              │
│  ┌────────────────────────┐  │
│  │ ingest/                │  │
│  │ - orchestrator.py      │  │
│  │ - vector_manager.py    │──┼─── CREATES/UPDATES
│  └────────────────────────┘  │    vector store
│                              │
└──────────────────────────────┘
```

**Integration is NON-BREAKING:**
- Same vector store location
- Same embedding model
- Same Document format
- Existing retrieval works unchanged

## Performance Characteristics

### Ingestion Throughput

**Slack:**
- Export: ~500 messages/minute (JSON parsing)
- API: ~100 messages/minute (rate limits)

**Confluence:**
- ~50 pages/minute (API + HTML conversion)

**PDF:**
- ~10 pages/minute (text extraction)

**Bottlenecks:**
1. API rate limits (Slack, Confluence)
2. HTML conversion (Confluence)
3. PDF parsing (complex layouts)

### Vector Indexing

**Embedding Generation:**
- Google API: ~50 chunks/second
- Bottleneck: API quota and network

**Chroma Insertion:**
- ~500 documents/second (local)
- Bottleneck: Disk I/O

**Total indexing:**
- ~1000 documents: 30-60 seconds
- ~10000 documents: 5-10 minutes

### Storage Requirements

**Raw data:**
- Slack: ~1KB per message
- Confluence: ~10KB per page
- PDF: ~size of original file

**Vector store:**
- ~1.5x size of raw text (embeddings overhead)

**Example:**
- 10,000 messages = ~10MB raw + ~15MB vectors = ~25MB total

## Summary

This technical reference provides:

✅ Component interaction maps  
✅ Detailed data flow sequences  
✅ Metadata lifecycle tracking  
✅ Error handling strategies  
✅ Storage layout specification  
✅ Class hierarchy documentation  
✅ Concurrency considerations  
✅ Integration points  
✅ Performance characteristics  

Use this as a reference for:
- Understanding the system architecture
- Debugging issues
- Extending functionality
- Performance optimization
- Team onboarding
