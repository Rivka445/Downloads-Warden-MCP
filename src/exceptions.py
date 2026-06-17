"""Custom exceptions for Downloads Warden."""


class DownloadsWardenError(Exception):
    """Base exception for all Downloads Warden errors."""


class PathNotFoundError(DownloadsWardenError):
    """Raised when the downloads folder path does not exist."""

    def __init__(self, path: str) -> None:
        super().__init__(f"Downloads folder not found at: {path}")
        self.path = path


class FileMoveError(DownloadsWardenError):
    """Raised when a file cannot be moved during sorting."""

    def __init__(self, filename: str, reason: str) -> None:
        super().__init__(f"Error moving '{filename}': {reason}")
        self.filename = filename
        self.reason = reason


class HashCalculationError(DownloadsWardenError):
    """Raised when SHA-256 hash cannot be calculated for a file."""

    def __init__(self, filename: str, reason: str) -> None:
        super().__init__(f"Error calculating hash for '{filename}': {reason}")
        self.filename = filename
        self.reason = reason


class ExtractionError(DownloadsWardenError):
    """Raised when a ZIP archive cannot be extracted."""

    def __init__(self, filename: str, reason: str) -> None:
        super().__init__(f"Error extracting '{filename}': {reason}")
        self.filename = filename
        self.reason = reason


class InstallerCleanupError(DownloadsWardenError):
    """Raised when an installer file cannot be deleted."""

    def __init__(self, filename: str, reason: str) -> None:
        super().__init__(f"Error deleting installer '{filename}': {reason}")
        self.filename = filename
        self.reason = reason


class FolderDeletionError(DownloadsWardenError):
    """Raised when a duplicate folder cannot be deleted."""

    def __init__(self, folder_name: str, reason: str) -> None:
        super().__init__(f"Error deleting folder '{folder_name}': {reason}")
        self.folder_name = folder_name
        self.reason = reason
