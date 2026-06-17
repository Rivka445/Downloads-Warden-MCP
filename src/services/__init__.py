"""Services package."""

from .downloads_service import DownloadsService
from interfaces import IDownloadsService

__all__ = ["DownloadsService", "IDownloadsService"]
