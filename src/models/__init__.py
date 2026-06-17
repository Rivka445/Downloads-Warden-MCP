"""Data models."""

from .file_info import FileInfo
from .scan_result import ScanResult, CategoryStats
from .operation_result import OperationResult, LargeFilesResult

__all__ = [
    'FileInfo',
    'ScanResult',
    'CategoryStats',
    'OperationResult',
    'LargeFilesResult',
]
