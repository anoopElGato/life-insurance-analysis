"""
RAG system for retrieval and LLM analysis
"""

from typing import List, Dict, Optional, Any
from src.embeddings.vector_db import VectorDatabase
from src.utils.logger import get_logger
from config.settings import RAG_TOP_K, RAG_RELEVANCE_THRESHOLD

logger = get_logger("rag.retriever")


class DocumentRetriever:
    """Retrieve relevant documents from vector database"""
    
    def __init__(self, vector_db: VectorDatabase, collection_name: str = "brand_documents"):
        self.vector_db = vector_db
        self.collection_name = collection_name
    
    def retrieve(
        self,
        query: str,
        top_k: int = RAG_TOP_K,
        company: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for query"""
        logger.debug(f"Retrieving documents for query: {query}")
        
        if company:
            results = self.vector_db.search_by_company(
                self.collection_name,
                query,
                company,
                top_k=top_k
            )
        else:
            results = self.vector_db.search(
                self.collection_name,
                query,
                top_k=top_k
            )
        
        # Filter by relevance threshold
        relevant_results = [
            r for r in results
            if r.get('relevance_score', 0) >= RAG_RELEVANCE_THRESHOLD
        ]
        
        logger.debug(f"Retrieved {len(relevant_results)} relevant documents")
        return relevant_results
    
    def retrieve_for_analysis(
        self,
        query: str,
        company: str,
        top_k: int = RAG_TOP_K
    ) -> str:
        """Retrieve documents formatted for LLM analysis"""
        results = self.retrieve(query, top_k=top_k, company=company)
        
        if not results:
            return "No relevant documents found."
        
        formatted_context = "RELEVANT DOCUMENTS:\n"
        formatted_context += "=" * 80 + "\n"
        
        for idx, result in enumerate(results, 1):
            formatted_context += f"\n[Document {idx}]\n"
            formatted_context += f"Source: {result['metadata'].get('document_name', 'Unknown')}\n"
            formatted_context += f"Type: {result['metadata'].get('source_type', 'Unknown')}\n"
            formatted_context += f"Relevance: {result['relevance_score']:.2%}\n"
            formatted_context += f"Content:\n{result['text']}\n"
            formatted_context += "-" * 80 + "\n"
        
        return formatted_context


__all__ = ["DocumentRetriever"]
