"""
Common metadata keys used throughout the RAG pipeline.

Keeping metadata keys in one place avoids typos,
improves consistency, and makes future refactoring easier.
"""

# ---------- File Metadata ----------

FILE_NAME = "file_name"
FILE_PATH = "file_path"
FILE_EXTENSION = "extension"
FILE_SIZE = "size"
LANGUAGE = "language"

# ---------- Chunk Metadata ----------

CHUNK_INDEX = "chunk_index"
CHUNK_NUMBER = "chunk_number"
TOTAL_CHUNKS = "total_chunks"
CHUNK_LABEL = "chunk_label"