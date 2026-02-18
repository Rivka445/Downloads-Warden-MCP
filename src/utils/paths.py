"""Path utilities."""

import sys
from pathlib import Path


def get_downloads_path() -> str:
    """Get the user's Downloads folder path."""
    return str(Path.home() / "Downloads")


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent
