from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.splitter_config import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_SEPARATORS,
)

from app.constants.metadata_key import (
    CHUNK_INDEX,
    CHUNK_NUMBER,
    TOTAL_CHUNKS,
    CHUNK_LABEL,
)


class DocumentSplitter:
    """
    Splits LangChain Documents into smaller chunks while preserving
    the original metadata and enriching each chunk with chunk-specific
    metadata for easier debugging, retrieval, and traceability.
    """

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> None:
        """
        Initialize the Recursive Character Text Splitter.

        Args:
            chunk_size: Maximum number of characters per chunk.
            chunk_overlap: Number of overlapping characters between chunks.
        """

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=DEFAULT_SEPARATORS,
        )

    def split(
        self,
        documents: list[Document],
    ) -> list[Document]:
        """
        Split a list of LangChain Documents into smaller chunks.

        Every generated chunk preserves the original metadata and is
        enriched with:

        - chunk_index  : Zero-based index of the chunk
        - chunk_number : Human-readable chunk number (starts from 1)
        - total_chunks : Total chunks generated from the source document
        - chunk_label  : Example -> "3/8"

        Args:
            documents: List of LangChain Documents.

        Returns:
            List[Document]: List of chunked documents.
        """

        all_chunks: list[Document] = []

        for document in documents:

            # Split only one document at a time so that
            # chunk numbering remains specific to that document.
            chunks = self.splitter.split_documents([document])

            total_chunks = len(chunks)

            for chunk_index, chunk in enumerate(chunks):

                chunk.metadata.update(
                    {
                        CHUNK_INDEX: chunk_index,
                        CHUNK_NUMBER: chunk_index + 1,
                        TOTAL_CHUNKS: total_chunks,
                        CHUNK_LABEL: f"{chunk_index + 1}/{total_chunks}",
                    }
                )

                all_chunks.append(chunk)

        return all_chunks