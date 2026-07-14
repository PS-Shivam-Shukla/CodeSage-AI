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
    "venv",
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

__all__ = ["SUPPORTED_EXTENSIONS", "IGNORED_DIRECTORIES", "MAX_FILE_SIZE"]