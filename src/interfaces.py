"""Abstract interfaces for dependency injection."""

from abc import ABC, abstractmethod
from models import ScanResult, OperationResult, LargeFilesResult


class IDownloadsService(ABC):

    @abstractmethod
    def scan_downloads(self) -> ScanResult: ...

    @abstractmethod
    def smart_sort_files(self) -> OperationResult: ...

    @abstractmethod
    def deduplicate_by_hash(self) -> OperationResult: ...

    @abstractmethod
    def deduplicate_folders(self) -> OperationResult: ...

    @abstractmethod
    def auto_extract_and_cleanup(self) -> OperationResult: ...

    @abstractmethod
    def clear_installers(self) -> OperationResult: ...

    @abstractmethod
    def find_large_files(self, min_size_mb: float) -> LargeFilesResult: ...
