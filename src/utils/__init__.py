
from pathlib import Path
from .file_utils import get_file_category, calculate_file_hash, get_file_size_mb


def get_downloads_path() -> Path:
    """Get the user's Downloads folder path."""
    return Path.home() / "Downloads"


__all__ = ['get_downloads_path', 'get_file_category', 'calculate_file_hash', 'get_file_size_mb']
