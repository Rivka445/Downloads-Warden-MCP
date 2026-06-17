"""Scan result model."""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class CategoryStats:
    count: int = 0
    size_mb: float = 0.0


@dataclass
class ScanResult:
    success: bool
    message: str
    total_files: int = 0
    total_size_mb: float = 0.0
    by_category: Dict[str, CategoryStats] = field(default_factory=dict)
    by_extension: Dict[str, CategoryStats] = field(default_factory=dict)
