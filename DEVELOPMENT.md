# Development Guide

## Project Structure

```
team_P1/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
├── README.md              # Main documentation
├── example.py             # Example usage script
├── src/                   # Source code
│   ├── __init__.py
│   ├── api/               # FastAPI routes
│   │   ├── __init__.py
│   │   └── routes.py      # API endpoints
│   ├── core/              # Core RAG system
│   │   ├── __init__.py
│   │   ├── config.py      # Configuration management
│   │   ├── rag.py         # RAG system implementation
│   │   └── vector_store.py # Vector database wrapper
│   └── connectors/        # Data source connectors
│       ├── __init__.py
│       ├── pdf_loader.py       # PDF document loader
│       ├── confluence_connector.py # Confluence integration
│       └── slack_connector.py      # Slack integration
├── static/                # Frontend assets
│   ├── app.js            # JavaScript application
│   └── styles.css        # Stylesheets
├── templates/             # HTML templates
│   └── index.html        # Main chat interface
├── data/                  # Data storage
│   └── chroma/           # ChromaDB persistence
└── uploads/              # Uploaded files
```

## Development Setup

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run Development Server

```bash
python main.py
```

The server will start at `http://localhost:8000`

## API Endpoints

### Health Check
- **GET** `/health`
- Returns: `{"status": "healthy"}`

### System Status
- **GET** `/api/status`
- Returns: System status and configuration

### Query Knowledge Base
- **POST** `/api/query`
- Body: `{"question": "string", "source_type": "optional"}`
- Returns: Answer with sources

### Upload PDFs
- **POST** `/api/upload/pdf`
- Body: multipart/form-data with PDF files
- Returns: Upload status

### Load Confluence
- **POST** `/api/load/confluence`
- Body: `{"space_key": "string", "limit": 100}`
- Returns: Load status

### Load Slack
- **POST** `/api/load/slack`
- Body: `{"channel_id": "string", "days": 30}`
- Returns: Load status

## Core Components

### RAG System (`src/core/rag.py`)

The RAG (Retrieval-Augmented Generation) system combines:
1. **Retrieval**: Find relevant documents using vector similarity
2. **Augmentation**: Add retrieved context to the prompt
3. **Generation**: Use LLM to generate an answer

### Vector Store (`src/core/vector_store.py`)

Manages document embeddings using ChromaDB:
- Stores document chunks as vectors
- Performs similarity search
- Persists data to disk

### Document Connectors

#### PDF Loader (`src/connectors/pdf_loader.py`)
- Extracts text from PDF files
- Splits into manageable chunks
- Preserves metadata (page numbers, filename)

#### Confluence Connector (`src/connectors/confluence_connector.py`)
- Connects to Confluence Cloud/Server
- Loads entire spaces or individual pages
- Converts HTML to text

#### Slack Connector (`src/connectors/slack_connector.py`)
- Connects to Slack workspace
- Loads channel history
- Groups messages into conversations

## Configuration Options

All configuration is done via environment variables (`.env` file):

```env
# Required
OPENAI_API_KEY=sk-...

# Optional - Model Selection
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4-turbo-preview

# Optional - Chunking
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Optional - Server
APP_HOST=0.0.0.0
APP_PORT=8000
```

## Testing

### Manual Testing

1. Start the server: `python main.py`
2. Open browser: `http://localhost:8000`
3. Upload a PDF or add sample data
4. Ask questions in the chat interface

### Programmatic Testing

Use the example script:

```bash
python example.py
```

## Adding New Data Sources

To add a new data source connector:

1. Create a new file in `src/connectors/`
2. Implement a class with a `load()` method
3. Return list of `Document` objects
4. Add API endpoint in `src/api/routes.py`

Example:

```python
from langchain.docstore.document import Document

class MyConnector:
    def load_data(self, source_id: str) -> List[Document]:
        # Fetch data from source
        data = fetch_from_source(source_id)
        
        # Convert to documents
        documents = []
        for item in data:
            doc = Document(
                page_content=item.text,
                metadata={
                    "source": item.name,
                    "source_type": "my_source",
                    "id": item.id
                }
            )
            documents.append(doc)
        
        return documents
```

## Troubleshooting

### ChromaDB Issues

If you encounter ChromaDB errors:
```bash
rm -rf data/chroma
# Restart the application
```

### Import Errors

Make sure you're running from the project root:
```bash
cd /path/to/team_P1
python main.py
```

### API Key Errors

Verify your `.env` file:
```bash
cat .env | grep OPENAI_API_KEY
```

## Best Practices

1. **Document Chunking**: Keep chunks between 500-1500 tokens for best results
2. **Metadata**: Always include rich metadata for source attribution
3. **Error Handling**: Wrap connector calls in try-except blocks
4. **Rate Limiting**: Be mindful of API rate limits for Confluence/Slack
5. **Security**: Never commit `.env` file or API keys

## Contributing

When contributing code:

1. Follow existing code style
2. Add docstrings to functions
3. Update documentation for new features
4. Test with sample data before committing
