"""
Text preprocessing and chunking module
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime
from src.utils.models import Document, ProcessedChunk, SourceType
from src.utils.logger import get_logger
from src.utils.helpers import (
    clean_text, chunk_text, deduplicate_texts, generate_id,
    save_jsonl, load_jsonl
)
from config.settings import (
    PROCESSED_DATA_DIR, EMBEDDING_CHUNK_SIZE, EMBEDDING_OVERLAP
)

logger = get_logger("processors.text_processor")


class TextProcessor:
    """Process raw documents into clean, chunked format"""
    
    def __init__(
        self,
        chunk_size: int = EMBEDDING_CHUNK_SIZE,
        chunk_overlap: int = EMBEDDING_OVERLAP,
        deduplication_threshold: float = 0.9
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.deduplication_threshold = deduplication_threshold
        self.processed_chunks: List[ProcessedChunk] = []
    
    def process_documents(self, documents: List[Document]) -> List[ProcessedChunk]:
        """Process multiple documents"""
        logger.info(f"Processing {len(documents)} documents")
        
        for doc in documents:
            chunks = self.process_document(doc)
            self.processed_chunks.extend(chunks)
        
        logger.info(f"Created {len(self.processed_chunks)} chunks")
        return self.processed_chunks
    
    def process_document(self, document: Document) -> List[ProcessedChunk]:
        """Process a single document into chunks"""
        logger.debug(f"Processing document: {document.document_name}")
        
        # Clean text
        cleaned_text = clean_text(document.raw_text)
        
        # Create chunks
        text_chunks = chunk_text(
            cleaned_text,
            chunk_size=self.chunk_size,
            overlap=self.chunk_overlap
        )
        
        # Deduplicate chunks
        unique_chunks = deduplicate_texts(text_chunks, self.deduplication_threshold)
        
        logger.debug(f"Created {len(text_chunks)} chunks, {len(unique_chunks)} after deduplication")
        
        # Create ProcessedChunk objects
        processed_chunks = []
        for chunk_idx, chunk_text_content in enumerate(unique_chunks):
            chunk = ProcessedChunk(
                document_id=document.id,
                company=document.company,
                source_type=document.source_type,
                source_url=document.source_url,
                publication_date=document.publication_date,
                document_name=document.document_name,
                chunk_index=chunk_idx,
                text=chunk_text_content,
                chunk_size=len(chunk_text_content),
                metadata=self._enrich_metadata(document.metadata, chunk_idx)
            )
            processed_chunks.append(chunk)
        
        return processed_chunks
    
    def _enrich_metadata(self, base_metadata: Dict[str, Any], chunk_index: int) -> Dict[str, Any]:
        """Enrich metadata with processing information"""
        metadata = base_metadata.copy()
        metadata['chunk_index'] = chunk_index
        metadata['chunk_size'] = self.chunk_size
        metadata['processed_at'] = datetime.now().isoformat()
        return metadata
    
    def save_processed_chunks(
        self,
        output_dir: Optional[Path] = None,
        by_company: bool = True
    ) -> None:
        """Save processed chunks to storage"""
        if output_dir is None:
            output_dir = PROCESSED_DATA_DIR
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if by_company:
            # Group by company
            chunks_by_company = {}
            for chunk in self.processed_chunks:
                if chunk.company not in chunks_by_company:
                    chunks_by_company[chunk.company] = []
                chunks_by_company[chunk.company].append(chunk)
            
            # Save each company's chunks
            for company, chunks in chunks_by_company.items():
                output_file = output_dir / f"{company.replace(' ', '_')}_chunks.jsonl"
                self._save_chunks(output_file, chunks)
                logger.info(f"Saved {len(chunks)} chunks for {company}")
        else:
            # Save all chunks together
            output_file = output_dir / "all_chunks.jsonl"
            self._save_chunks(output_file, self.processed_chunks)
            logger.info(f"Saved {len(self.processed_chunks)} chunks")
    
    def _save_chunks(self, filepath: Path, chunks: List[ProcessedChunk]) -> None:
        """Save chunks to JSONL file"""
        chunks_data = []
        for chunk in chunks:
            chunk_dict = chunk.dict()
            chunk_dict['processed_at'] = chunk_dict['processed_at'].isoformat()
            if chunk_dict['publication_date']:
                chunk_dict['publication_date'] = chunk_dict['publication_date'].isoformat()
            chunks_data.append(chunk_dict)
        
        save_jsonl(chunks_data, filepath)
    
    def load_processed_chunks(self, filepath: Path) -> List[ProcessedChunk]:
        """Load processed chunks from file"""
        logger.info(f"Loading chunks from {filepath}")
        chunks_data = load_jsonl(filepath)
        
        chunks = []
        for chunk_data in chunks_data:
            chunk = ProcessedChunk(**chunk_data)
            chunks.append(chunk)
        
        logger.info(f"Loaded {len(chunks)} chunks")
        return chunks
    
    def get_chunks_by_company(self, company: str) -> List[ProcessedChunk]:
        """Get all chunks for a company"""
        return [c for c in self.processed_chunks if c.company == company]
    
    def get_chunks_by_source(self, source_type: SourceType) -> List[ProcessedChunk]:
        """Get all chunks from a source type"""
        return [c for c in self.processed_chunks if c.source_type == source_type]
    
    def get_chunks_stats(self) -> Dict[str, Any]:
        """Get statistics about processed chunks"""
        return {
            "total_chunks": len(self.processed_chunks),
            "total_characters": sum(c.chunk_size for c in self.processed_chunks),
            "by_company": {
                company: len(self.get_chunks_by_company(company))
                for company in set(c.company for c in self.processed_chunks)
            },
            "by_source": {
                source.value: len(self.get_chunks_by_source(source))
                for source in set(c.source_type for c in self.processed_chunks)
            }
        }


__all__ = ["TextProcessor"]
