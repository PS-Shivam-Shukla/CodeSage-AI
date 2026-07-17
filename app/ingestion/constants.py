from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".py",
    ".java",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".json",
    ".xml",
    ".yml",
    ".yaml",
    ".properties",
    ".toml",
    ".ini",
    ".md",
    ".txt",
    ".sql",
    ".html",
    ".css",
    ".pdf",
}

IGNORED_DIRECTORIES = {
    ".git",
    ".github",
    "node_modules",
    "target",
    "build",
    "dist",
    "coverage",
    ".idea",
    ".vscode",
    "__pycache__",
    ".venv",
    ".venv_backend",  # Backend virtual environment
    "venv",
    ".pytest_cache",  # Pytest cache
    ".mypy_cache",    # MyPy cache
    "chroma_db",      # Don't index the vector database itself
    "evaluation_reports",  # Don't index evaluation reports
    ".hypothesis",    # Hypothesis testing cache
    "htmlcov",        # Coverage HTML reports
    ".tox",           # Tox environments
    "wheels",         # Python wheels
    "eggs",           # Python eggs
    ".eggs",          # Egg info
    "*.egg-info",     # Egg metadata
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

__all__ = ["SUPPORTED_EXTENSIONS", "IGNORED_DIRECTORIES", "MAX_FILE_SIZE"]