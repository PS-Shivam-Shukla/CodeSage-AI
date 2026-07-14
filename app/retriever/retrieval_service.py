from langchain_core.documents import Document

from app.vectorstore.chroma_service import ChromaService


class RetrievalService:
    """
    Service responsible for retrieving the most relevant
    documents from the vector database.
    """

    def __init__(self) -> None:
        self.vector_store = ChromaService()

    def retrieve(
        self,
        query: str,
        k: int = 5,
    ) -> list[Document]:
        """
        Retrieve the top-k most relevant documents.

        Args:
            query: User query.
            k: Number of documents to retrieve.

        Returns:
            List of relevant LangChain Documents.
        """

        return self.vector_store.similarity_search(
            query=query,
            k=k,
        )