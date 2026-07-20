from typing import List, Dict, Set, Tuple
from langchain_core.documents import Document

from app.vectorstore.chroma_service import ChromaService
from app.retriever.query_expander import QueryExpander
from app.config.vectorstore_config import CANDIDATE_K, HIGH_VALUE_FILES, STRUCTURAL_FILES


class RetrievalService:
    """
    Enhanced service for retrieving the most relevant documents from
    the vector database with query expansion, intelligent re-ranking,
    and file-type prioritization.
    
    Improvements over basic retrieval:
    1. Query expansion for better recall (adaptive based on query type)
    2. Multi-query retrieval with deduplication
    3. Candidate-k → final-k filtering with re-ranking
    4. File-type prioritization (README, docs, configs)
    5. Adjacent chunk merging for better context
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
        Retrieve the top-k most relevant documents using enhanced retrieval
        with adaptive expansion and intelligent re-ranking.

        Args:
            query: User query.
            k: Number of documents to retrieve.
            use_expansion: Whether to use query expansion (default: True).

        Returns:
            List of relevant LangChain Documents, deduplicated, re-ranked, and merged.
        """
        # Determine if this is a broad query that needs more context
        is_broad_query = self._is_broad_query(query)
        
        # Adaptive expansion: use expansion sparingly for specific queries
        if not use_expansion or self._is_specific_query(query):
            # Simple retrieval with re-ranking for specific queries
            candidate_k = min(CANDIDATE_K, k * 2)
            docs_with_scores = self.vector_store.similarity_search_with_score(
                query=query, k=candidate_k
            )
            return self._rerank_and_filter(docs_with_scores, query, k, is_broad_query)
        
        # Multi-query retrieval with expansion for complex queries
        queries = self.query_expander.expand_query(query)
        
        # Retrieve documents for each query variation with scores
        candidate_k = min(CANDIDATE_K, k * 2)
        per_query_k = max(candidate_k // len(queries) + 2, 8)
        
        all_docs_with_scores: List[Tuple[Document, float]] = []
        seen_content: Set[str] = set()
        
        for q in queries:
            docs_with_scores = self.vector_store.similarity_search_with_score(
                query=q, k=per_query_k
            )
            
            for doc, score in docs_with_scores:
                # Deduplicate by content
                content_hash = hash(doc.page_content)
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    all_docs_with_scores.append((doc, score))
        
        # Re-rank and filter to final k
        return self._rerank_and_filter(all_docs_with_scores, query, k, is_broad_query)
    
    def _is_broad_query(self, query: str) -> bool:
        """
        Detect if query asks about repository structure or high-level organization.
        These queries benefit from more diverse chunks.
        """
        query_lower = query.lower()
        broad_indicators = [
            "directory", "structure", "organization", "architecture",
            "all", "list all", "what are", "overview", "components",
            "main", "entire", "whole", "complete", "overall"
        ]
        return any(indicator in query_lower for indicator in broad_indicators)
    
    def _is_specific_query(self, query: str) -> bool:
        """
        Detect if query is very specific and doesn't need query expansion.
        """
        query_lower = query.lower()
        specific_indicators = [
            "how does", "explain how", "implementation of", 
            "function", "method", "class", "specific"
        ]
        return any(indicator in query_lower for indicator in specific_indicators)
    
    def _rerank_and_filter(
        self,
        docs_with_scores: List[Tuple[Document, float]],
        query: str,
        k: int,
        is_broad_query: bool,
    ) -> List[Document]:
        """
        Intelligent re-ranking with file-type prioritization and adjacent chunk merging.
        
        Args:
            docs_with_scores: List of (Document, similarity_score) tuples
            query: Original query for relevance assessment
            k: Final number of documents to return
            is_broad_query: Whether query asks for broad/structural information
            
        Returns:
            Re-ranked and filtered list of top-k documents
        """
        if not docs_with_scores:
            return []
        
        # Calculate boost scores for each document
        scored_docs = []
        for doc, similarity_score in docs_with_scores:
            boost = self._calculate_document_boost(doc, query, is_broad_query)
            final_score = similarity_score * (1.0 + boost)
            scored_docs.append((doc, final_score))
        
        # Sort by final score (lower distance = higher similarity)
        scored_docs.sort(key=lambda x: x[1])
        
        # Extract just the documents
        ranked_docs = [doc for doc, _ in scored_docs]
        
        # Merge adjacent chunks from same file
        merged_docs = self._merge_adjacent_chunks(ranked_docs)
        
        # Return top-k after merging
        return merged_docs[:k]
    
    def _calculate_document_boost(
        self, 
        doc: Document, 
        query: str,
        is_broad_query: bool,
    ) -> float:
        """
        Calculate boost score based on file type and query relevance.
        
        Returns:
            Boost multiplier (0.0 to 0.4) where higher = more important
        """
        source = doc.metadata.get("source", "").lower()
        boost = 0.0
        
        # High-value files get significant boost
        if any(pattern.lower() in source for pattern in HIGH_VALUE_FILES):
            boost += 0.25
        
        # Structural files get extra boost for broad queries
        if is_broad_query and any(pattern.lower() in source for pattern in STRUCTURAL_FILES):
            boost += 0.15
        
        # Configuration-related queries boost config files
        query_lower = query.lower()
        if any(term in query_lower for term in ["config", "environment", "variable", "setting"]):
            if any(term in source for term in ["config", ".env", "settings", "setup"]):
                boost += 0.20
        
        # API/endpoint queries boost route definition files
        if any(term in query_lower for term in ["api", "endpoint", "route", "http"]):
            if any(term in source for term in ["api", "route", "endpoint", "router"]):
                boost += 0.20
        
        return min(boost, 0.4)  # Cap total boost at 40%
    
    def _merge_adjacent_chunks(self, docs: List[Document]) -> List[Document]:
        """
        Merge adjacent chunks from the same source file to provide better context.
        
        Args:
            docs: List of documents sorted by relevance
            
        Returns:
            List with adjacent chunks merged where beneficial
        """
        if len(docs) <= 1:
            return docs
        
        merged = []
        skip_next = False
        
        for i in range(len(docs)):
            if skip_next:
                skip_next = False
                continue
            
            current_doc = docs[i]
            
            # Check if next chunk is from same file and adjacent
            if i < len(docs) - 1:
                next_doc = docs[i + 1]
                
                current_source = current_doc.metadata.get("source", "")
                next_source = next_doc.metadata.get("source", "")
                
                current_chunk_num = current_doc.metadata.get("chunk_number", 0)
                next_chunk_num = next_doc.metadata.get("chunk_number", 0)
                
                # Merge if same file and chunks are adjacent or close
                if (current_source == next_source and 
                    next_chunk_num - current_chunk_num <= 2 and
                    len(current_doc.page_content) + len(next_doc.page_content) <= 1500):
                    
                    # Create merged document
                    merged_content = f"{current_doc.page_content}\n\n{next_doc.page_content}"
                    merged_doc = Document(
                        page_content=merged_content,
                        metadata={
                            **current_doc.metadata,
                            "chunk_label": f"{current_chunk_num}-{next_chunk_num}",
                            "merged": True,
                        }
                    )
                    merged.append(merged_doc)
                    skip_next = True
                    continue
            
            merged.append(current_doc)
        
        return merged
    
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