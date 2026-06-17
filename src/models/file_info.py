"""File info model."""

from dataclasses import dataclass


@dataclass
class FileInfo:
    name: str
    size_mb: float
