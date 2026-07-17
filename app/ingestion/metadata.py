from pathlib import Path

from app.constants.metadata_key import (
    FILE_NAME,
    FILE_PATH,
    FILE_EXTENSION,
    FILE_SIZE,
)


def create_metadata(file_path: Path) -> dict:
    """
    Generate metadata for a file.
    """

    return {
        FILE_NAME: file_path.name,
        FILE_PATH: str(file_path),
        FILE_EXTENSION: file_path.suffix,
        FILE_SIZE: file_path.stat().st_size,
    }