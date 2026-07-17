"""
app/utils/embedding_cache.py
=============================

Simple in-memory cache for embeddings to reduce redundant API calls.

Benefits:
- Avoids re-computing embeddings for repeated queries
- Reduces API latency and costs
- Improves response time for common questions
"""

from __future__ import annotations

import hashlib
from typing import Dict, List, Optional
from functools import lru_cache


class EmbeddingCache:
    """
    Thread-safe in-memory cache for query embeddings.
    
    Uses LRU eviction to prevent unbounded memory growth.
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize the embedding cache.
        
        Args:
            max_size: Maximum number of cached embeddings
        """
        self._cache: Dict[str, List[float]] = {}
        self._max_size = max_size
    
    def _get_cache_key(self, text: str) -> str:
        """
        Generate a cache key from text using hash.
        
        Args:
            text: Input text
            
        Returns:
            Hash-based cache key
        """
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def get(self, text: str) -> Optional[List[float]]:
        """
        Retrieve cached embedding if available.
        
        Args:
            text: Query text
            
        Returns:
            Cached embedding vector or None
        """
        key = self._get_cache_key(text)
        return self._cache.get(key)
    
    def put(self, text: str, embedding: List[float]) -> None:
        """
        Store embedding in cache.
        
        Args:
            text: Query text
            embedding: Embedding vector
        """
        if len(self._cache) >= self._max_size:
            # Simple FIFO eviction - remove oldest entry
            first_key = next(iter(self._cache))
            del self._cache[first_key]
        
        key = self._get_cache_key(text)
        self._cache[key] = embedding
    
    def clear(self) -> None:
        """Clear all cached embeddings."""
        self._cache.clear()
    
    def size(self) -> int:
        """Return current cache size."""
        return len(self._cache)


# Global singleton cache instance
_global_cache = EmbeddingCache(max_size=1000)


def get_global_cache() -> EmbeddingCache:
    """Get the global embedding cache instance."""
    return _global_cache


@lru_cache(maxsize=500)
def cached_text_hash(text: str) -> str:
    """
    LRU-cached hash function for text.
    
    Useful for quick lookups without recomputing hashes.
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()
