"""
Configuration for ChromaDB with performance optimizations.
"""

# Directory where the vector database will be stored
CHROMA_PERSIST_DIRECTORY = "./chroma_db"

# Collection name
CHROMA_COLLECTION_NAME = "repository_chunks"

# Batch size for adding documents (prevents memory issues)
CHROMA_BATCH_SIZE = 100

# Default number of results to retrieve
DEFAULT_K = 10