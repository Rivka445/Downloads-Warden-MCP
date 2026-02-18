"""Utility functions for file operations."""

import hashlib
from pathlib import Path


def get_file_category(file_path: str) -> str:
    """Categorize file by extension."""
    ext = Path(file_path).suffix.lower()
    
    categories = {
        'Documents': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.ppt', '.pptx'],
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
        'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac', '.m4a', '.wma'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
        'Code': ['.py', '.js', '.java', '.cpp', '.c', '.html', '.css', '.json'],
        'Executables': ['.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm'],
    }
    
    for category, extensions in categories.items():
        if ext in extensions:
            return category
    
    return 'Other'


def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes."""
    try:
        size_bytes = Path(file_path).stat().st_size
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0.0


__all__ = ['get_file_category', 'calculate_file_hash', 'get_file_size_mb']
