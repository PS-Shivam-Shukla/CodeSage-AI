from pathlib import Path

from app.ingestion.repository_ingestion import RepositoryIngestionService
from app.splitters.document_splitter import DocumentSplitter
from app.vectorstore.chroma_service import ChromaService


class IndexingService:
    """
    Orchestrates the complete indexing pipeline.

    Pipeline:
        Repository
            ↓
        Load Documents
            ↓
        Split Documents
            ↓
        Store in ChromaDB
    """

    def __init__(self) -> None:
        self.document_splitter = DocumentSplitter()
        self.vector_store = ChromaService()

    def index_repository(self, repository_path: str) -> None:
        """
        Index an entire repository into the vector database.

        Args:
            repository_path: Path to the repository.
        """

        print("=" * 80)
        print("Starting Repository Indexing...")
        print("=" * 80)

        # Step 1: Load documents
        ingestion_service = RepositoryIngestionService(repository_path)
        documents = ingestion_service.load()

        print(f"Loaded {len(documents)} document(s).")

        # Step 2: Split documents
        chunks = self.document_splitter.split(documents)

        print(f"Generated {len(chunks)} chunk(s).")

        # Step 3: Store in ChromaDB
        self.vector_store.add_documents(chunks)

        print("Documents successfully stored in ChromaDB.")

        print("=" * 80)
        print("Repository Indexing Completed Successfully.")
        print("=" * 80)