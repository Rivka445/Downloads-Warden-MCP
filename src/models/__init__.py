"""Data models for Downloads Warden MCP."""

from dataclasses import dataclass


@dataclass
class FileStatistics:
    """File statistics model."""
    total_files: int
    total_size_mb: float
    by_category: dict
    by_extension: dict


@dataclass
class ScanResult:
    """Result of scanning Downloads folder."""
    success: bool
    message: str
    data: FileStatistics | None = None


@dataclass
class ProcessingResult:
    """Result of a file processing operation."""
    success: bool
    message: str
    count: int = 0
    errors: list[str] | None = None
