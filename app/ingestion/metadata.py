from pathlib import Path


def create_metadata(file_path: Path) -> dict:
    """
    Generate metadata for a file.
    """

    return {
        "file_name": file_path.name,
        "file_path": str(file_path),
        "extension": file_path.suffix,
        "size": file_path.stat().st_size,
    }