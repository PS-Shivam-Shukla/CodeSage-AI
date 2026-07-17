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
        print("\n[1/3] Loading documents from repository...")
        ingestion_service = RepositoryIngestionService(repository_path)
        documents = ingestion_service.load()

        print(f"✓ Loaded {len(documents)} document(s).")

        # Step 2: Split documents
        print("\n[2/3] Chunking documents...")
        chunks = self.document_splitter.split(documents)

        print(f"✓ Generated {len(chunks)} chunk(s).")

        # Step 3: Store in ChromaDB
        print(f"\n[3/3] Storing chunks in ChromaDB (batches of 100)...")
        print("This may take a few minutes depending on chunk count...")
        
        self.vector_store.add_documents(chunks)

        print(f"✓ Successfully stored all chunks in vector database.")

        print("\n" + "=" * 80)
        print("Repository Indexing Completed Successfully.")
        print("=" * 80)