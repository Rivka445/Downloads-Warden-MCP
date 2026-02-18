"""File utility functions."""

import hashlib
from pathlib import Path
from collections import defaultdict


def get_file_category(filepath: str) -> str:
    """Categorize file by extension."""
    ext = Path(filepath).suffix.lower()
    
    categories = {
        'documents': ['.pdf', '.docx', '.doc', '.txt', '.xlsx', '.xls', '.pptx', '.ppt', '.rtf'],
        'media': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.mp4', '.avi', '.mov', '.mkv', '.mp3', '.flac', '.wav'],
        'installers': ['.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm'],
        'code': ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.html', '.css', '.json', '.yaml', '.yml'],
        'archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
    }
    
    for category, extensions in categories.items():
        if ext in extensions:
            return category
    
    return 'other'


def calculate_file_hash(filepath: str) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_file_size_mb(filepath: str) -> float:
    """Get file size in MB."""
    return Path(filepath).stat().st_size / (1024 * 1024)
