from langchain_chroma import Chroma

from app.config.vectorstore_config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIRECTORY,
)
from app.embeddings.embedding_service import EmbeddingService


class ChromaService:
    """
    Handles all interactions with ChromaDB.
    """

    def __init__(self):

        self.vector_store = Chroma(
            collection_name=CHROMA_COLLECTION_NAME,
            persist_directory=CHROMA_PERSIST_DIRECTORY,
            embedding_function=EmbeddingService.get_model(),
        )

    def add_documents(self, documents):
        """
        Store chunked documents.
        """
        self.vector_store.add_documents(documents)

    def similarity_search(
        self,
        query: str,
        k: int = 5,
    ):
        """
        Retrieve the top-k most relevant chunks.
        """
        return self.vector_store.similarity_search(
            query=query,
            k=k,
        )