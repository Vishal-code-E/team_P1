"""PDF document loader and processor."""
import os
from typing import List
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

from ..core.config import settings


class PDFLoader:
    """Load and process PDF documents."""
    
    def __init__(self):
        """Initialize the PDF loader."""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
        )
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """
        Load a PDF file and convert it to documents.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of Document objects
        """
        documents = []
        
        try:
            reader = PdfReader(file_path)
            filename = os.path.basename(file_path)
            
            # Extract text from each page
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                
                if text.strip():  # Only process non-empty pages
                    metadata = {
                        "source": filename,
                        "source_type": "pdf",
                        "page": page_num + 1,
                        "total_pages": len(reader.pages)
                    }
                    
                    # Create document for this page
                    doc = Document(
                        page_content=text,
                        metadata=metadata
                    )
                    documents.append(doc)
            
            # Split documents into chunks
            split_documents = self.text_splitter.split_documents(documents)
            
            return split_documents
            
        except Exception as e:
            raise Exception(f"Error loading PDF {file_path}: {str(e)}")
    
    def load_multiple_pdfs(self, file_paths: List[str]) -> List[Document]:
        """
        Load multiple PDF files.
        
        Args:
            file_paths: List of paths to PDF files
            
        Returns:
            List of Document objects from all PDFs
        """
        all_documents = []
        
        for file_path in file_paths:
            try:
                documents = self.load_pdf(file_path)
                all_documents.extend(documents)
            except Exception as e:
                print(f"Warning: Failed to load {file_path}: {str(e)}")
                continue
        
        return all_documents


pdf_loader = PDFLoader()
