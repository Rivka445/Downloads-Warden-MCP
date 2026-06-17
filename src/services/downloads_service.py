"""Downloads folder management service."""

import shutil
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

from utils.file_utils import get_file_category, calculate_file_hash, get_file_size_mb
from interfaces import IDownloadsService
from models import ScanResult, CategoryStats, OperationResult, LargeFilesResult, FileInfo
from exceptions import (
    DownloadsWardenError,
    PathNotFoundError,
    FileMoveError,
    HashCalculationError,
    ExtractionError,
    FolderDeletionError,
)


class DownloadsService(IDownloadsService):
    """Service for managing Downloads folder operations."""

    def __init__(self, downloads_path: str) -> None:
        self.downloads_path = Path(downloads_path)

    def scan_downloads(self) -> ScanResult:
        """Scan and analyze Downloads folder."""
        if not self.downloads_path.exists():
            raise PathNotFoundError(str(self.downloads_path))

        by_category: dict[str, CategoryStats] = defaultdict(CategoryStats)
        by_extension: dict[str, CategoryStats] = defaultdict(CategoryStats)
        total_files = 0
        total_size_mb = 0.0

        for file_path in self.downloads_path.rglob('*'):
            if file_path.is_file():
                total_files += 1
                size_mb = get_file_size_mb(str(file_path))
                total_size_mb += size_mb

                category = get_file_category(str(file_path))
                by_category[category].count += 1
                by_category[category].size_mb += size_mb

                ext = file_path.suffix.lower() or 'no_extension'
                by_extension[ext].count += 1
                by_extension[ext].size_mb += size_mb

        return ScanResult(
            success=True,
            message='Successfully scanned downloads folder',
            total_files=total_files,
            total_size_mb=total_size_mb,
            by_category=dict(by_category),
            by_extension=dict(by_extension),
        )

    def smart_sort_files(self) -> OperationResult:
        """Sort files into category folders."""
        moved_count = 0
        errors = []

        for file_path in self.downloads_path.iterdir():
            if file_path.is_file():
                try:
                    category = get_file_category(str(file_path))
                    category_dir = self.downloads_path / category
                    category_dir.mkdir(exist_ok=True)
                    dest_path = category_dir / file_path.name
                    if dest_path != file_path:
                        shutil.move(str(file_path), str(dest_path))
                        moved_count += 1
                except Exception as e:
                    errors.append(FileMoveError(file_path.name, str(e)).args[0])

        return OperationResult(
            success=True,
            message=f'Sorted {moved_count} files',
            count=moved_count,
            errors=errors,
        )

    def deduplicate_by_hash(self) -> OperationResult:
        """Remove duplicate files based on SHA-256 hash."""
        hash_map: dict[str, list[Path]] = defaultdict(list)
        deleted_count = 0

        for file_path in self.downloads_path.rglob('*'):
            if file_path.is_file():
                try:
                    file_hash = calculate_file_hash(str(file_path))
                    hash_map[file_hash].append(file_path)
                except Exception as e:
                    raise HashCalculationError(file_path.name, str(e)) from e

        for file_list in hash_map.values():
            if len(file_list) > 1:
                for duplicate_file in file_list[1:]:
                    duplicate_file.unlink()
                    deleted_count += 1

        return OperationResult(
            success=True,
            message=f'Removed {deleted_count} duplicate files',
            count=deleted_count,
        )

    def auto_extract_and_cleanup(self) -> OperationResult:
        """Extract ZIP files and remove originals."""
        extracted_count = 0
        errors = []

        for archive_file in self.downloads_path.rglob('*.zip'):
            try:
                extract_dir = self.downloads_path / archive_file.stem
                extract_dir.mkdir(exist_ok=True)
                with zipfile.ZipFile(archive_file, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                archive_file.unlink()
                extracted_count += 1
            except Exception as e:
                errors.append(ExtractionError(archive_file.name, str(e)).args[0])

        return OperationResult(
            success=True,
            message=f'Extracted {extracted_count} archives',
            count=extracted_count,
            errors=errors,
        )

    def clear_installers(self) -> OperationResult:
        """Remove old installer files (older than 7 days)."""
        deleted_count = 0
        one_week_ago = datetime.now() - timedelta(days=7)
        installer_extensions = {'.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm'}

        for file_path in self.downloads_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in installer_extensions:
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < one_week_ago:
                    file_path.unlink()
                    deleted_count += 1

        return OperationResult(
            success=True,
            message=f'Removed {deleted_count} old installer files',
            count=deleted_count,
        )

    def find_large_files(self, min_size_mb: float = 500) -> LargeFilesResult:
        """Find files larger than specified size."""
        large_files: list[FileInfo] = []

        for file_path in self.downloads_path.rglob('*'):
            if file_path.is_file():
                size_mb = get_file_size_mb(str(file_path))
                if size_mb >= min_size_mb:
                    large_files.append(FileInfo(name=file_path.name, size_mb=size_mb))

        large_files.sort(key=lambda f: f.size_mb, reverse=True)
        total_size_mb = sum(f.size_mb for f in large_files)

        return LargeFilesResult(
            success=True,
            message=f'Found {len(large_files)} files larger than {min_size_mb}MB',
            count=len(large_files),
            files=large_files,
            total_size_mb=total_size_mb,
        )

    def deduplicate_folders(self) -> OperationResult:
        """Remove duplicate folders based on their contents."""
        folder_hashes: dict[str, Path] = {}
        duplicate_folders: list[Path] = []

        for folder_path in sorted(self.downloads_path.iterdir()):
            if folder_path.is_dir() and not folder_path.name.startswith('.'):
                try:
                    folder_hash = self._calculate_folder_hash(folder_path)
                    if folder_hash in folder_hashes:
                        duplicate_folders.append(folder_path)
                    else:
                        folder_hashes[folder_hash] = folder_path
                except Exception:
                    pass

        deleted_count = 0
        errors = []
        for duplicate_folder in duplicate_folders:
            try:
                shutil.rmtree(str(duplicate_folder))
                deleted_count += 1
            except Exception as e:
                errors.append(FolderDeletionError(duplicate_folder.name, str(e)).args[0])

        return OperationResult(
            success=True,
            message=f'Removed {deleted_count} duplicate folders',
            count=deleted_count,
            errors=errors,
        )

    def _calculate_folder_hash(self, folder_path: Path) -> str:
        """Calculate hash based on folder structure and contents."""
        hash_obj = hashlib.sha256()
        for file_path in sorted(folder_path.rglob('*')):
            if file_path.is_file():
                try:
                    file_hash = calculate_file_hash(str(file_path))
                    hash_obj.update(file_hash.encode())
                except Exception:
                    pass
        return hash_obj.hexdigest()
