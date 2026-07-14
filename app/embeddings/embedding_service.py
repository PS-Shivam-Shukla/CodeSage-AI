from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from app.config.embedding_config import (
    EMBEDDING_MODEL_NAME,
    DEVICE,
    NORMALIZE_EMBEDDINGS,
    CACHE_FOLDER,
)


class EmbeddingService:
    """
    Service responsible for generating embeddings.

    The embedding model is loaded only once and reused
    throughout the application.
    """

    @staticmethod
    @lru_cache(maxsize=1)
    def get_model() -> HuggingFaceEmbeddings:
        """
        Load and cache the embedding model.

        Returns:
            HuggingFaceEmbeddings
        """

        return HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={
                "device": DEVICE,
            },
            encode_kwargs={
                "normalize_embeddings": NORMALIZE_EMBEDDINGS,
            },
            cache_folder=CACHE_FOLDER,
        )

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        """

        return self.get_model().embed_documents(texts)

    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        """
        Generate embedding for a single query.
        """

        return self.get_model().embed_query(query)