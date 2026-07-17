from typing import List, Dict, Set
from langchain_core.documents import Document

from app.vectorstore.chroma_service import ChromaService
from app.retriever.query_expander import QueryExpander


class RetrievalService:
    """
    Enhanced service for retrieving the most relevant documents from
    the vector database with query expansion and multi-query retrieval.
    
    Improvements over basic retrieval:
    1. Query expansion for better recall
    2. Multi-query retrieval with deduplication
    3. Result merging and ranking
    """

    def __init__(self) -> None:
        self.vector_store = ChromaService()
        self.query_expander = QueryExpander()

    def retrieve(
        self,
        query: str,
        k: int = 10,
        use_expansion: bool = True,
    ) -> List[Document]:
        """
        Retrieve the top-k most relevant documents using enhanced retrieval.

        Args:
            query: User query.
            k: Number of documents to retrieve.
            use_expansion: Whether to use query expansion (default: True).

        Returns:
            List of relevant LangChain Documents, deduplicated and ranked.
        """
        if not use_expansion:
            # Simple retrieval without expansion
            return self.vector_store.similarity_search(query=query, k=k)
        
        # Multi-query retrieval with expansion
        queries = self.query_expander.expand_query(query)
        
        # Retrieve documents for each query variation
        # Get more per query to ensure we have enough after deduplication
        per_query_k = max(k // len(queries) + 2, 5)
        
        all_docs = []
        seen_content: Set[str] = set()
        
        for q in queries:
            docs = self.vector_store.similarity_search(query=q, k=per_query_k)
            
            for doc in docs:
                # Deduplicate by content
                content_hash = hash(doc.page_content)
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    all_docs.append(doc)
        
        # Return top-k documents
        # Documents are already roughly ranked by similarity from each query
        return all_docs[:k]
    
    def retrieve_with_metadata_filter(
        self,
        query: str,
        k: int = 10,
        metadata_filter: Dict[str, any] = None,
    ) -> List[Document]:
        """
        Retrieve documents with optional metadata filtering.
        
        Args:
            query: User query.
            k: Number of documents to retrieve.
            metadata_filter: Dictionary of metadata key-value pairs to filter by.
        
        Returns:
            Filtered list of relevant documents.
        """
        # Get expanded documents
        docs = self.retrieve(query, k=k * 2)  # Get more initially for filtering
        
        if metadata_filter:
            filtered_docs = [
                doc for doc in docs
                if all(doc.metadata.get(key) == value for key, value in metadata_filter.items())
            ]
            return filtered_docs[:k]
        
        return docs[:k]