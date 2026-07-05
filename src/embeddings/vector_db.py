"""
Embeddings and vector database management - FREE LOCAL VERSION
Uses sentence-transformers for embeddings (no API costs)
"""

from typing import List, Dict, Optional, Any
from pathlib import Path

from src.utils.models import ProcessedChunk
from src.utils.logger import get_logger
from config.settings import (
    CHROMADB_PATH, LOCAL_EMBEDDING_MODEL, EMBEDDING_DEVICE,
    EMBEDDING_BATCH_SIZE
)

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    raise ImportError("chromadb not installed. Install it with: pip install chromadb")

try:
    from sentence_transformers import SentenceTransformer
except ImportError as exc:
    raise ImportError(
        "sentence-transformers could not be imported. "
        "Run: pip install -r requirements.txt. "
        f"Original error: {exc}"
    )

logger = get_logger("embeddings.vector_db")


class EmbeddingManager:
    """Manage embeddings creation using free local models"""
    
    def __init__(self, model_name: str = LOCAL_EMBEDDING_MODEL):
        """Initialize embedding manager with local model"""
        logger.info(f"Loading sentence-transformers model: {model_name}")
        logger.info("This is FREE - no API costs!")
        
        try:
            self.model = SentenceTransformer(model_name, device=EMBEDDING_DEVICE)
            logger.info(f"Successfully loaded embeddings model: {model_name}")
            logger.info(f"Running on device: {EMBEDDING_DEVICE}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """Create embedding for single text"""
        if not text or len(text.strip()) == 0:
            logger.warning("Empty text provided for embedding")
            return []
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            return []
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts (batched)"""
        logger.info(f"Creating embeddings for {len(texts)} texts using {LOCAL_EMBEDDING_MODEL}")
        
        embeddings = []
        for i in range(0, len(texts), EMBEDDING_BATCH_SIZE):
            batch = texts[i:i + EMBEDDING_BATCH_SIZE]
            try:
                # Filter out empty texts
                batch_clean = [t for t in batch if t and len(t.strip()) > 0]
                
                if batch_clean:
                    batch_embeddings = self.model.encode(batch_clean, convert_to_numpy=False)
                    for idx, text in enumerate(batch):
                        if text and len(text.strip()) > 0:
                            embeddings.append(batch_embeddings[len([b for b in batch[:idx] if b and len(b.strip()) > 0])].tolist())
                        else:
                            embeddings.append([])
                else:
                    embeddings.extend([[] for _ in batch])
                
                logger.info(f"Embedded batch {i//EMBEDDING_BATCH_SIZE + 1}/{(len(texts)-1)//EMBEDDING_BATCH_SIZE + 1}")
            except Exception as e:
                logger.error(f"Error embedding batch: {str(e)}")
                embeddings.extend([[] for _ in batch])
        
        logger.info(f"Created {len([e for e in embeddings if e])} valid embeddings")
        return embeddings


class VectorDatabase:
    """Vector database for storing and retrieving embeddings"""
    
    def __init__(self, db_path: Optional[str] = None, load_embedding_model: bool = True):
        """Initialize vector database"""
        if db_path is None:
            db_path = CHROMADB_PATH
        
        self.db_path = db_path
        Path(db_path).mkdir(parents=True, exist_ok=True)
        
        # Chroma 0.4+ uses PersistentClient for local durable storage.
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False),
        )
        
        self.embedding_manager = EmbeddingManager() if load_embedding_model else None
        self.collections: Dict[str, Any] = {}
        
        logger.info(f"Initialized VectorDatabase at {db_path}")
    
    def create_collection(self, name: str, metadata: Optional[Dict] = None) -> None:
        """Create a new collection"""
        try:
            if name not in self.collections:
                collection = self.client.get_or_create_collection(
                    name=name,
                    metadata=metadata or {"type": "brand_documents"}
                )
                self.collections[name] = collection
                logger.info(f"Created collection: {name}")
            else:
                logger.warning(f"Collection {name} already exists")
        except Exception as e:
            logger.error(f"Error creating collection {name}: {str(e)}")
    
    def get_collection(self, name: str) -> Optional[Any]:
        """Get collection by name"""
        if name not in self.collections:
            try:
                collection = self.client.get_collection(name=name)
                self.collections[name] = collection
            except Exception as e:
                logger.warning(f"Collection {name} not found: {str(e)}")
                return None
        
        return self.collections.get(name)
    
    def add_chunks(self, collection_name: str, chunks: List[ProcessedChunk]) -> None:
        """Add processed chunks to collection with embeddings"""
        logger.info(f"Adding {len(chunks)} chunks to collection {collection_name}")

        if self.embedding_manager is None:
            self.embedding_manager = EmbeddingManager()
        
        collection = self.get_collection(collection_name)
        if not collection:
            self.create_collection(collection_name)
            collection = self.get_collection(collection_name)
        
        # Prepare data for insertion
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        texts_to_embed = []
        for chunk in chunks:
            ids.append(chunk.id)
            documents.append(chunk.text)
            texts_to_embed.append(chunk.text)
            
            metadata = chunk.metadata.copy()
            metadata['company'] = chunk.company
            metadata['source_type'] = chunk.source_type.value
            metadata['document_name'] = chunk.document_name
            metadata['chunk_index'] = chunk.chunk_index
            metadatas.append(metadata)
        
        # Create embeddings
        embeddings = self.embedding_manager.embed_texts(texts_to_embed)
        
        # Add to collection
        try:
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"Added {len(ids)} chunks to {collection_name}")
        except Exception as e:
            logger.error(f"Error adding chunks to collection: {str(e)}")
    
    def search(
        self,
        collection_name: str,
        query_text: str,
        top_k: int = 5,
        where: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks"""
        collection = self.get_collection(collection_name)
        if not collection:
            logger.warning(f"Collection {collection_name} not found")
            return []
        
        try:
            if self.embedding_manager is None:
                self.embedding_manager = EmbeddingManager()

            # Create query embedding
            query_embedding = self.embedding_manager.embed_text(query_text)
            
            if not query_embedding:
                logger.warning("Failed to create query embedding")
                return []
            
            # Search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and len(results['ids']) > 0:
                for idx, doc_id in enumerate(results['ids'][0]):
                    formatted_results.append({
                        'id': doc_id,
                        'text': results['documents'][0][idx] if idx < len(results['documents'][0]) else '',
                        'metadata': results['metadatas'][0][idx] if idx < len(results['metadatas'][0]) else {},
                        'distance': results['distances'][0][idx] if idx < len(results['distances'][0]) else 0.0,
                        'relevance_score': 1 - (results['distances'][0][idx] if idx < len(results['distances'][0]) else 0.5)
                    })
            
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error searching collection: {str(e)}")
            return []
    
    def search_by_company(
        self,
        collection_name: str,
        query_text: str,
        company: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks within a company"""
        return self.search(
            collection_name,
            query_text,
            top_k=top_k,
            where={"company": company}
        )
    
    def list_collections(self) -> List[str]:
        """List all collections"""
        try:
            collections = self.client.list_collections()
            return [c.name for c in collections]
        except Exception as e:
            logger.error(f"Error listing collections: {str(e)}")
            return []
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics for a collection"""
        collection = self.get_collection(collection_name)
        if not collection:
            return {}
        
        try:
            # Get count
            count = collection.count()
            
            # Sample to get metadata distribution
            if count > 0:
                samples = collection.get(limit=min(100, count))
                companies = set()
                sources = set()
                
                if samples['metadatas']:
                    for metadata in samples['metadatas']:
                        companies.add(metadata.get('company', 'unknown'))
                        sources.add(metadata.get('source_type', 'unknown'))
                
                return {
                    'total_chunks': count,
                    'companies': list(companies),
                    'source_types': list(sources)
                }
            
            return {'total_chunks': count}
        
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {}
    
    def persist(self) -> None:
        """Persist database if the installed Chroma client requires it."""
        try:
            if hasattr(self.client, "persist"):
                self.client.persist()
                logger.info("Database persisted")
            else:
                logger.info("Database persistence is automatic for this Chroma client")
        except Exception as e:
            logger.error(f"Error persisting database: {str(e)}")


__all__ = ["EmbeddingManager", "VectorDatabase"]
