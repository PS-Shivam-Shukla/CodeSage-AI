from pathlib import Path

from langchain_core.documents import Document

from .constants import (
    SUPPORTED_EXTENSIONS,
    IGNORED_DIRECTORIES,
    MAX_FILE_SIZE,
)

from .loaders import (
    load_pdf,
    load_text_file,
)


class RepositoryIngestionService:

    def __init__(self, repository_path: str):

        self.repository = Path(repository_path)

    def load(self):

        documents = []

        for file_path in self.repository.rglob("*"):

            if not file_path.is_file():
                continue

            if any(
                ignored in file_path.parts
                for ignored in IGNORED_DIRECTORIES
            ):
                continue

            if file_path.suffix not in SUPPORTED_EXTENSIONS:
                continue

            if file_path.stat().st_size > MAX_FILE_SIZE:
                continue

            try:

                if file_path.suffix == ".pdf":

                    documents.extend(load_pdf(file_path))

                else:

                    documents.extend(load_text_file(file_path))

            except Exception as e:

                print(f"Failed to load {file_path}: {e}")

        return documents