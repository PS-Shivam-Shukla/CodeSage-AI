from typing import List, Optional
from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.config.vectorstore_config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIRECTORY,
)
from app.embeddings.embedding_service import EmbeddingService


class ChromaService:
    """
    Handles all interactions with ChromaDB with optimized retrieval.
    
    Optimizations:
    - Cached embedding model
    - Efficient batch operations
    - Pre-filtered searches when possible
    """

    def __init__(self):
        self.vector_store = Chroma(
            collection_name=CHROMA_COLLECTION_NAME,
            persist_directory=CHROMA_PERSIST_DIRECTORY,
            embedding_function=EmbeddingService.get_model(),
        )

    def add_documents(self, documents: List[Document]) -> None:
        """
        Store chunked documents in batches for better performance.
        
        Args:
            documents: List of Document objects to store
        """
        # Process in batches to avoid memory issues with large repositories
        batch_size = 100
        total_batches = (len(documents) + batch_size - 1) // batch_size
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            print(f"  Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)...", end='\r')
            
            self.vector_store.add_documents(batch)
        
        print(f"\n  ✓ All {len(documents)} chunks indexed successfully")

    def similarity_search(
        self,
        query: str,
        k: int = 10,
        filter: Optional[dict] = None,
    ) -> List[Document]:
        """
        Retrieve the top-k most relevant chunks with optional filtering.
        
        Args:
            query: Query text
            k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of relevant Document objects
        """
        if filter:
            return self.vector_store.similarity_search(
                query=query,
                k=k,
                filter=filter,
            )
        
        return self.vector_store.similarity_search(
            query=query,
            k=k,
        )
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 10,
    ) -> List[tuple[Document, float]]:
        """
        Retrieve documents with similarity scores for ranking.
        
        Args:
            query: Query text
            k: Number of results
            
        Returns:
            List of (Document, score) tuples
        """
        return self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
        )
    
    def delete_collection(self) -> None:
        """
        Delete the entire collection (use for re-indexing).
        """
        self.vector_store.delete_collection()
    
    def get_collection_count(self) -> int:
        """
        Get the number of documents in the collection.
        
        Returns:
            Number of documents
        """
        try:
            collection = self.vector_store._collection
            return collection.count()
        except:
            return 0