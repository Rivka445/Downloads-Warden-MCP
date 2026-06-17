"""Operation result model for write operations."""

from dataclasses import dataclass, field
from typing import List, Optional
from models.file_info import FileInfo


@dataclass
class OperationResult:
    success: bool
    message: str
    count: int = 0
    errors: List[str] = field(default_factory=list)


@dataclass
class LargeFilesResult(OperationResult):
    files: List[FileInfo] = field(default_factory=list)
    total_size_mb: float = 0.0
