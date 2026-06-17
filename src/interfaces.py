"""Abstract interfaces for dependency injection."""

from abc import ABC, abstractmethod


class IDownloadsService(ABC):

    @abstractmethod
    def scan_downloads(self) -> dict: ...

    @abstractmethod
    def smart_sort_files(self) -> dict: ...

    @abstractmethod
    def deduplicate_by_hash(self) -> dict: ...

    @abstractmethod
    def deduplicate_folders(self) -> dict: ...

    @abstractmethod
    def auto_extract_and_cleanup(self) -> dict: ...

    @abstractmethod
    def clear_installers(self) -> dict: ...

    @abstractmethod
    def find_large_files(self, min_size_mb: float) -> dict: ...
