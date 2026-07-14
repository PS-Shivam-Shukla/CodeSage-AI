from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

from .metadata import create_metadata


def load_text_file(file_path: Path):
    """
    Load any text-based file.
    """

    content = file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    return [
        Document(
            page_content=content,
            metadata=create_metadata(file_path)
        )
    ]


def load_pdf(file_path: Path):
    """
    Load a PDF file.
    """

    loader = PyPDFLoader(str(file_path))

    return loader.load()