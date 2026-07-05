"""
Base collector interface and utilities
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import datetime
from src.utils.models import Document, SourceType
from src.utils.logger import get_logger

logger = get_logger("collectors.base")


class BaseCollector(ABC):
    """Abstract base class for all collectors"""
    
    def __init__(self, company: str, source_type: SourceType):
        self.company = company
        self.source_type = source_type
        self.documents: List[Document] = []
    
    @abstractmethod
    def collect(self) -> List[Document]:
        """Collect data from source"""
        pass
    
    def create_document(
        self,
        source_url: str,
        document_name: str,
        raw_text: str,
        publication_date: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Document:
        """Helper method to create document"""
        if metadata is None:
            metadata = {}
        
        return Document(
            company=self.company,
            source_type=self.source_type,
            source_url=source_url,
            publication_date=publication_date,
            document_name=document_name,
            raw_text=raw_text,
            metadata=metadata
        )
    
    def validate_document(self, doc: Document) -> bool:
        """Validate document before storing"""
        if not doc.raw_text or len(doc.raw_text.strip()) < 50:
            logger.warning(f"Document {doc.document_name} too short or empty")
            return False
        return True
    
    def add_document(self, doc: Document) -> None:
        """Add document to collection"""
        if self.validate_document(doc):
            self.documents.append(doc)
            logger.info(f"Added document: {doc.document_name}")
    
    def get_documents(self) -> List[Document]:
        """Get all collected documents"""
        return self.documents


__all__ = ["BaseCollector"]
