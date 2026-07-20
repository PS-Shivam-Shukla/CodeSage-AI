"""
Configuration for ChromaDB with performance optimizations.
"""

# Directory where the vector database will be stored
CHROMA_PERSIST_DIRECTORY = "./chroma_db"

# Collection name
CHROMA_COLLECTION_NAME = "repository_chunks"

# Batch size for adding documents (prevents memory issues)
CHROMA_BATCH_SIZE = 100

# Default number of results to retrieve (increased for better coverage)
DEFAULT_K = 15

# Candidate retrieval for re-ranking (retrieve more, filter down)
CANDIDATE_K = 20

# High-value file patterns that should be prioritized in retrieval
HIGH_VALUE_FILES = [
    "README",
    "CONTRIBUTING",
    "CHANGELOG",
    "LICENSE",
    "setup.py",
    "pyproject.toml",
    "package.json",
    "requirements.txt",
    ".env",
    "config",
    "settings",
    "__init__.py",
    "main.py",
    "app.py",
]

# File patterns that contain structural/organizational information
STRUCTURAL_FILES = [
    "README",
    "docs/",
    "documentation/",
    "architecture",
    "structure",
    "organization",
]