"""
Document collection orchestrator
"""

from typing import List, Dict, Optional
from src.collectors.base import BaseCollector
from src.collectors.web_collector import WebCollector
from src.collectors.pdf_collector import PDFCollector
from src.utils.models import Document
from src.utils.logger import get_logger
from config.settings import COMPANIES, DATA_DIR
from pathlib import Path
import json

logger = get_logger("collectors.orchestrator")


class CollectionOrchestrator:
    """Orchestrate data collection from multiple sources"""
    
    def __init__(self):
        self.collectors: Dict[str, List[BaseCollector]] = {}
        self.all_documents: List[Document] = []
    
    def add_web_collector(self, company: str, website_url: str) -> WebCollector:
        """Add web collector for company"""
        collector = WebCollector(company, website_url)
        if company not in self.collectors:
            self.collectors[company] = []
        self.collectors[company].append(collector)
        logger.info(f"Added web collector for {company}")
        return collector
    
    def add_pdf_collector(self, company: str, pdf_urls: Optional[List[str]] = None, pdf_files: Optional[List[str]] = None) -> PDFCollector:
        """Add PDF collector for company"""
        collector = PDFCollector(company, pdf_urls, pdf_files)
        if company not in self.collectors:
            self.collectors[company] = []
        self.collectors[company].append(collector)
        logger.info(f"Added PDF collector for {company}")
        return collector
    
    def setup_default_collectors(self) -> None:
        """Setup collectors for all configured companies"""
        logger.info("Setting up default collectors")
        
        for company_name, company_info in COMPANIES.items():
            # Add web collector
            self.add_web_collector(company_name, company_info["website"])
            
            # Add PDF collector (initially empty, will be populated with specific URLs)
            self.add_pdf_collector(company_name, pdf_urls=company_info.get("pdf_urls"), pdf_files=company_info.get("pdf_files"))
            
            logger.info(f"Configured collectors for {company_name}")
    
    def collect_all(self) -> Dict[str, List[Document]]:
        """Collect data from all collectors"""
        logger.info("Starting collection from all sources")
        collected_data = {}
        
        for company, collectors in self.collectors.items():
            logger.info(f"Collecting data for {company}")
            company_documents = []
            
            for collector in collectors:
                try:
                    documents = collector.collect()
                    company_documents.extend(documents)
                    logger.info(f"Collected {len(documents)} documents from {collector.__class__.__name__}")
                except Exception as e:
                    logger.error(f"Error in {collector.__class__.__name__}: {str(e)}")
            
            collected_data[company] = company_documents
            self.all_documents.extend(company_documents)
            logger.info(f"Total documents for {company}: {len(company_documents)}")
        
        logger.info(f"Total documents collected: {len(self.all_documents)}")
        return collected_data
    
    def save_raw_documents(self, output_dir: Optional[Path] = None) -> None:
        """Save collected documents to storage"""
        if output_dir is None:
            output_dir = DATA_DIR / "raw"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for company, documents in self.collectors.items():
            company_docs = []
            for collector in self.collectors[company]:
                company_docs.extend(collector.get_documents())
            
            if company_docs:
                output_file = output_dir / f"{company.replace(' ', '_')}_raw.jsonl"
                with open(output_file, 'w', encoding='utf-8') as f:
                    for doc in company_docs:
                        doc_dict = doc.dict()
                        doc_dict['ingested_at'] = doc_dict['ingested_at'].isoformat()
                        if doc_dict['publication_date']:
                            doc_dict['publication_date'] = doc_dict['publication_date'].isoformat()
                        f.write(json.dumps(doc_dict, ensure_ascii=False) + '\n')
                
                logger.info(f"Saved {len(company_docs)} documents for {company}")
    
    def get_documents_by_company(self, company: str) -> List[Document]:
        """Get all documents for a specific company"""
        documents = []
        if company in self.collectors:
            for collector in self.collectors[company]:
                documents.extend(collector.get_documents())
        return documents
    
    def get_all_documents(self) -> List[Document]:
        """Get all collected documents"""
        return self.all_documents
    
    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics about collection"""
        stats = {}
        for company, documents in self.collectors.items():
            total_docs = sum(len(collector.get_documents()) for collector in documents)
            stats[company] = total_docs
        return stats


__all__ = ["CollectionOrchestrator"]
