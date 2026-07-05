"""
PDF collector for reports and brochures
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import pdfplumber
import requests
from datetime import datetime
from src.collectors.base import BaseCollector
from src.utils.models import Document, SourceType
from src.utils.logger import get_logger
from src.utils.helpers import clean_text
from config.settings import REQUEST_TIMEOUT, MAX_RETRIES
import time

logger = get_logger("collectors.pdf")


class PDFCollector(BaseCollector):
    """Collector for PDF documents (reports, brochures)
    
    Supports both:
    - Remote PDFs from URLs
    - Local PDF files from file system
    """
    
    def __init__(self, company: str, pdf_urls: Optional[List[str]] = None, 
                 pdf_files: Optional[List[str]] = None):
        """Initialize PDF collector
        
        Args:
            company: Company name
            pdf_urls: List of PDF URLs
            pdf_files: List of local PDF file paths
        """
        super().__init__(company, SourceType.PDF_REPORT)
        self.pdf_urls = pdf_urls or []
        self.pdf_files = pdf_files or []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def add_pdf_url(self, url: str) -> None:
        """Add PDF URL to collection list"""
        if url not in self.pdf_urls:
            self.pdf_urls.append(url)
            logger.debug(f"Added PDF URL: {url}")
    
    def add_pdf_urls(self, urls: List[str]) -> None:
        """Add multiple PDF URLs"""
        for url in urls:
            self.add_pdf_url(url)
    
    def add_pdf_file(self, file_path: str) -> bool:
        """Add local PDF file to collection list
        
        Args:
            file_path: Path to local PDF file
            
        Returns:
            True if file exists and was added, False otherwise
        """
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            logger.error(f"PDF file not found: {file_path}")
            return False
        
        if not file_path_obj.suffix.lower() == '.pdf':
            logger.error(f"File is not a PDF: {file_path}")
            return False
        
        file_path_str = str(file_path_obj.absolute())
        if file_path_str not in self.pdf_files:
            self.pdf_files.append(file_path_str)
            logger.debug(f"Added local PDF file: {file_path}")
            return True
        
        return False
    
    def add_pdf_files(self, file_paths: List[str]) -> Dict[str, bool]:
        """Add multiple local PDF files
        
        Args:
            file_paths: List of local PDF file paths
            
        Returns:
            Dictionary mapping file paths to success status
        """
        results = {}
        for file_path in file_paths:
            results[file_path] = self.add_pdf_file(file_path)
        return results
    
    def collect(self) -> List[Document]:
        """Collect data from PDF files (both URLs and local files)"""
        logger.info(f"Starting PDF collection for {self.company}")
        logger.info(f"  URLs: {len(self.pdf_urls)}")
        logger.info(f"  Local files: {len(self.pdf_files)}")
        
        # Process URLs
        for url in self.pdf_urls:
            try:
                self._process_pdf_url(url)
                time.sleep(1)  # Be polite
            except Exception as e:
                logger.error(f"Error processing PDF URL {url}: {str(e)}")
        
        # Process local files
        for file_path in self.pdf_files:
            try:
                self._process_pdf_file(file_path)
            except Exception as e:
                logger.error(f"Error processing PDF file {file_path}: {str(e)}")
        
        logger.info(f"Collected {len(self.documents)} documents from PDFs")
        return self.documents
    
    def _process_pdf_url(self, url: str) -> None:
        """Download and process PDF from URL"""
        logger.info(f"Processing PDF URL: {url}")
        
        pdf_content = self._download_pdf(url)
        if pdf_content:
            text_content = self._extract_text_from_pdf(pdf_content)
            if text_content:
                self._create_document_from_pdf(url, text_content)
    
    def _process_pdf_file(self, file_path: str) -> None:
        """Read and process PDF from local file system
        
        Args:
            file_path: Path to local PDF file
        """
        logger.info(f"Processing local PDF file: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                pdf_content = f.read()
            
            text_content = self._extract_text_from_pdf(pdf_content)
            if text_content:
                # Use file path as identifier instead of URL
                self._create_document_from_pdf(file_path, text_content, is_local=True)
        
        except FileNotFoundError:
            logger.error(f"PDF file not found: {file_path}")
        except Exception as e:
            logger.error(f"Error reading PDF file {file_path}: {str(e)}")
    
    def _download_pdf(self, url: str) -> Optional[bytes]:
        """Download PDF file"""
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(
                    url,
                    timeout=REQUEST_TIMEOUT,
                    allow_redirects=True
                )
                response.raise_for_status()
                
                # Check if content is actually PDF
                if 'application/pdf' in response.headers.get('content-type', ''):
                    return response.content
                
                logger.warning(f"URL {url} did not return PDF content")
                return None
            
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed to download {url}: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
        
        return None
    
    def _extract_text_from_pdf(self, pdf_content: bytes) -> Optional[str]:
        """Extract text from PDF content"""
        try:
            import io
            pdf_file = io.BytesIO(pdf_content)
            
            text_parts = []
            with pdfplumber.open(pdf_file) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num}: {str(e)}")
            
            full_text = '\n'.join(text_parts)
            return clean_text(full_text) if full_text else None
        
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return None
    
    def _create_document_from_pdf(self, source: str, text_content: str, is_local: bool = False) -> None:
        """Create document from PDF text
        
        Args:
            source: URL or file path
            text_content: Extracted text content
            is_local: Whether source is a local file path
        """
        # Extract filename
        if is_local:
            # Local file path
            file_path_obj = Path(source)
            filename = file_path_obj.name
            source_url = f"local://{file_path_obj.absolute()}"
        else:
            # URL
            filename = source.split('/')[-1] or 'document.pdf'
            source_url = source
        
        metadata = {
            "source_url": source_url,
            "file_type": "pdf",
            "source_type": "local_file" if is_local else "url"
        }
        
        doc = self.create_document(
            source_url=source_url,
            document_name=f"{self.company}_{filename}",
            raw_text=text_content,
            metadata=metadata
        )
        self.add_document(doc)


__all__ = ["PDFCollector"]
