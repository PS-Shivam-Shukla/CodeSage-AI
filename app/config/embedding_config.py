"""
Embedding model configuration.

All embedding-related settings are centralized here so that
switching models or hardware requires changing only this file.
"""

# Hugging Face model name
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"

# cpu / cuda
DEVICE = "cpu"

# Normalize vectors for cosine similarity
NORMALIZE_EMBEDDINGS = True

# Show download progress when model is downloaded
SHOW_PROGRESS = True

# Cache directory (optional)
CACHE_FOLDER = "./models"