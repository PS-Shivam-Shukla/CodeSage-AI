"""
app/retriever/query_expander.py
================================

Query expansion module to improve retrieval precision by reformulating
user questions into more specific, vector-search-friendly queries.

Why Query Expansion?
--------------------
User questions are often high-level or vague. Vector search works better
with specific, contextual queries. This module preprocesses questions to:
1. Add relevant technical keywords
2. Expand acronyms and domain-specific terms
3. Create multiple query variants for better recall

Techniques Used:
- Keyword augmentation for technical terms
- Context-aware reformulation
- Multi-query generation for comprehensive retrieval
"""

from __future__ import annotations

import re
from typing import List


class QueryExpander:
    """
    Expands user queries to improve retrieval quality.
    
    Uses rule-based expansion for common patterns in code-related questions.
    """
    
    # Domain-specific expansions for common terms
    TERM_EXPANSIONS = {
        "API": ["API", "endpoint", "route", "REST", "HTTP"],
        "auth": ["authentication", "authorization", "JWT", "token", "login"],
        "config": ["configuration", "environment variable", "settings", ".env"],
        "eval": ["evaluation", "metrics", "scoring", "assessment"],
        "RAG": ["RAG", "retrieval", "augmented generation", "vector search"],
        "LLM": ["LLM", "language model", "NVIDIA", "model", "AI"],
        "class": ["class", "service", "module", "component"],
        "error": ["error", "exception", "failure", "handling", "retry"],
        "pipeline": ["pipeline", "workflow", "process", "flow"],
    }
    
    @staticmethod
    def expand_query(query: str) -> List[str]:
        """
        Generate multiple query variations to improve retrieval recall.
        
        Args:
            query: Original user question
            
        Returns:
            List of query variations (original + expanded versions)
        """
        queries = [query]  # Always include original
        
        # Normalize query
        query_lower = query.lower()
        
        # Add keyword-enhanced version
        enhanced = QueryExpander._add_keywords(query)
        if enhanced != query:
            queries.append(enhanced)
        
        # Add specific reformulations based on question patterns
        if any(word in query_lower for word in ["what is", "what are"]):
            # Descriptive questions -> focus on definitions
            reformulated = query.replace("What is", "Explain").replace("what is", "explain")
            reformulated = reformulated.replace("What are", "List").replace("what are", "list")
            queries.append(reformulated)
        
        if "how does" in query_lower or "how to" in query_lower:
            # Process questions -> focus on implementation
            queries.append(f"implementation of {query.split('how')[-1]}")
            queries.append(f"code for {query.split('how')[-1]}")
        
        if "list" in query_lower or "all" in query_lower:
            # Enumeration questions -> be more specific
            if "endpoint" in query_lower:
                queries.append("@router POST GET PUT DELETE endpoint route")
            if "class" in query_lower:
                queries.append("class Service Pipeline Adapter Evaluator")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for q in queries:
            if q not in seen:
                seen.add(q)
                unique_queries.append(q)
        
        return unique_queries
    
    @staticmethod
    def _add_keywords(query: str) -> str:
        """
        Add relevant technical keywords to the query based on detected terms.
        
        Args:
            query: Original query
            
        Returns:
            Query with added keywords
        """
        added_terms = []
        query_lower = query.lower()
        
        for term, expansions in QueryExpander.TERM_EXPANSIONS.items():
            if term.lower() in query_lower:
                # Add the most relevant expansion terms (max 2 per term)
                added_terms.extend(expansions[:2])
        
        if added_terms:
            # Add terms to the end to preserve original query structure
            return f"{query} {' '.join(set(added_terms))}"
        
        return query
    
    @staticmethod
    def extract_key_terms(query: str) -> List[str]:
        """
        Extract important technical terms from the query for filtering.
        
        Args:
            query: User query
            
        Returns:
            List of key terms
        """
        # Remove common words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will", "would",
            "should", "could", "may", "might", "can", "this", "that", "these",
            "those", "what", "which", "who", "when", "where", "why", "how",
        }
        
        # Tokenize and filter
        words = re.findall(r'\b\w+\b', query.lower())
        key_terms = [w for w in words if w not in stop_words and len(w) > 2]
        
        return key_terms
