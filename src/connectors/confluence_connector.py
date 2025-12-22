"""Confluence connector for loading wiki pages."""
from typing import List, Optional
from atlassian import Confluence
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import html2text

from ..core.config import settings


class ConfluenceConnector:
    """Connect to Confluence and load wiki pages."""
    
    def __init__(self):
        """Initialize the Confluence connector."""
        self.confluence = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
        )
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        
        # Initialize connection if credentials are available
        if all([settings.confluence_url, settings.confluence_username, settings.confluence_api_token]):
            self.confluence = Confluence(
                url=settings.confluence_url,
                username=settings.confluence_username,
                password=settings.confluence_api_token,
                cloud=True
            )
    
    def is_configured(self) -> bool:
        """Check if Confluence is properly configured."""
        return self.confluence is not None
    
    def load_space(self, space_key: str, limit: int = 100) -> List[Document]:
        """
        Load all pages from a Confluence space.
        
        Args:
            space_key: Confluence space key
            limit: Maximum number of pages to load
            
        Returns:
            List of Document objects
        """
        if not self.is_configured():
            raise ValueError("Confluence is not configured. Please set credentials in .env file.")
        
        documents = []
        
        try:
            # Get all pages in the space
            pages = self.confluence.get_all_pages_from_space(
                space=space_key,
                start=0,
                limit=limit,
                expand='body.storage,version'
            )
            
            for page in pages:
                doc = self._process_page(page)
                if doc:
                    documents.extend(doc)
            
            return documents
            
        except Exception as e:
            raise Exception(f"Error loading Confluence space {space_key}: {str(e)}")
    
    def load_page(self, page_id: str) -> List[Document]:
        """
        Load a single Confluence page.
        
        Args:
            page_id: Confluence page ID
            
        Returns:
            List of Document objects (chunked)
        """
        if not self.is_configured():
            raise ValueError("Confluence is not configured. Please set credentials in .env file.")
        
        try:
            page = self.confluence.get_page_by_id(
                page_id=page_id,
                expand='body.storage,version'
            )
            
            return self._process_page(page)
            
        except Exception as e:
            raise Exception(f"Error loading Confluence page {page_id}: {str(e)}")
    
    def _process_page(self, page: dict) -> List[Document]:
        """
        Process a Confluence page into documents.
        
        Args:
            page: Confluence page data
            
        Returns:
            List of Document objects
        """
        try:
            # Extract HTML content
            html_content = page.get('body', {}).get('storage', {}).get('value', '')
            
            # Convert HTML to markdown/text
            text_content = self.html_converter.handle(html_content)
            
            if not text_content.strip():
                return []
            
            # Create metadata
            metadata = {
                "source": page.get('title', 'Unknown'),
                "source_type": "confluence",
                "page_id": page.get('id'),
                "space_key": page.get('space', {}).get('key'),
                "url": f"{settings.confluence_url}/wiki{page.get('_links', {}).get('webui', '')}",
                "last_updated": page.get('version', {}).get('when', '')
            }
            
            # Create document
            doc = Document(
                page_content=text_content,
                metadata=metadata
            )
            
            # Split into chunks
            split_documents = self.text_splitter.split_documents([doc])
            
            return split_documents
            
        except Exception as e:
            print(f"Warning: Failed to process page: {str(e)}")
            return []


confluence_connector = ConfluenceConnector()
