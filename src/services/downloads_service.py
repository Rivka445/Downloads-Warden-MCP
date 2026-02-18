"""Downloads folder management service."""

import shutil
import zipfile
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

from src.utils import get_file_category, calculate_file_hash, get_file_size_mb
from src.models import FileStatistics, ScanResult, ProcessingResult


class DownloadsService:
    """Service for managing Downloads folder operations."""
    
    def __init__(self, downloads_path: str):
        """Initialize with downloads path."""
        self.downloads_path = Path(downloads_path)
    
    def scan_downloads(self) -> ScanResult:
        """Scan and analyze Downloads folder."""
        try:
            if not self.downloads_path.exists():
                return ScanResult(
                    success=False,
                    message=f"Downloads folder not found at {self.downloads_path}"
                )
            
            stats = {
                'total_files': 0,
                'total_size_mb': 0,
                'by_category': defaultdict(lambda: {'count': 0, 'size_mb': 0}),
                'by_extension': defaultdict(lambda: {'count': 0, 'size_mb': 0})
            }
            
            for file_path in self.downloads_path.rglob('*'):
                if file_path.is_file():
                    stats['total_files'] += 1
                    size_mb = get_file_size_mb(str(file_path))
                    stats['total_size_mb'] += size_mb
                    
                    category = get_file_category(str(file_path))
                    stats['by_category'][category]['count'] += 1
                    stats['by_category'][category]['size_mb'] += size_mb
                    
                    ext = file_path.suffix.lower() or 'no_extension'
                    stats['by_extension'][ext]['count'] += 1
                    stats['by_extension'][ext]['size_mb'] += size_mb
            
            file_stats = FileStatistics(
                total_files=stats['total_files'],
                total_size_mb=stats['total_size_mb'],
                by_category=dict(stats['by_category']),
                by_extension=dict(stats['by_extension'])
            )
            
            return ScanResult(
                success=True,
                message="Successfully scanned downloads folder",
                data=file_stats
            )
        
        except Exception as e:
            return ScanResult(
                success=False,
                message=f"Error scanning downloads: {str(e)}"
            )
    
    def smart_sort_files(self) -> ProcessingResult:
        """Sort files into category folders."""
        try:
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
                        errors.append(f"Error moving {file_path.name}: {str(e)}")
            
            return ProcessingResult(
                success=True,
                message=f"Sorted {moved_count} files",
                count=moved_count,
                errors=errors if errors else None
            )
        
        except Exception as e:
            return ProcessingResult(
                success=False,
                message=f"Error sorting files: {str(e)}"
            )
    
    def deduplicate_by_hash(self) -> ProcessingResult:
        """Remove duplicate files based on SHA-256 hash."""
        try:
            hash_map = defaultdict(list)
            deleted_count = 0
            
            # Calculate hashes for all files
            for file_path in self.downloads_path.rglob('*'):
                if file_path.is_file():
                    try:
                        file_hash = calculate_file_hash(str(file_path))
                        hash_map[file_hash].append(file_path)
                    except Exception:
                        pass
            
            # Remove duplicates, keeping the first occurrence
            for file_hash, file_list in hash_map.items():
                if len(file_list) > 1:
                    for duplicate_file in file_list[1:]:
                        duplicate_file.unlink()
                        deleted_count += 1
            
            return ProcessingResult(
                success=True,
                message=f"Removed {deleted_count} duplicate files",
                count=deleted_count
            )
        
        except Exception as e:
            return ProcessingResult(
                success=False,
                message=f"Error deduplicating files: {str(e)}"
            )
    
    def auto_extract_and_cleanup(self) -> ProcessingResult:
        """Extract ZIP files and remove originals."""
        try:
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
                    errors.append(f"Error extracting {archive_file.name}: {str(e)}")
            
            return ProcessingResult(
                success=True,
                message=f"Extracted {extracted_count} archives",
                count=extracted_count,
                errors=errors if errors else None
            )
        
        except Exception as e:
            return ProcessingResult(
                success=False,
                message=f"Error extracting archives: {str(e)}"
            )
    
    def clear_installers(self) -> ProcessingResult:
        """Remove old installer files (older than 7 days)."""
        try:
            deleted_count = 0
            one_week_ago = datetime.now() - timedelta(days=7)
            installer_extensions = ['.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm']
            
            for file_path in self.downloads_path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in installer_extensions:
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < one_week_ago:
                        file_path.unlink()
                        deleted_count += 1
            
            return ProcessingResult(
                success=True,
                message=f"Removed {deleted_count} old installer files",
                count=deleted_count
            )
        
        except Exception as e:
            return ProcessingResult(
                success=False,
                message=f"Error clearing installers: {str(e)}"
            )
    
    def find_large_files(self, min_size_mb: float = 500) -> ProcessingResult:
        """Find files larger than specified size."""
        try:
            large_files = []
            
            for file_path in self.downloads_path.rglob('*'):
                if file_path.is_file():
                    size_mb = get_file_size_mb(str(file_path))
                    if size_mb >= min_size_mb:
                        large_files.append((file_path, size_mb))
            
            large_files.sort(key=lambda x: x[1], reverse=True)
            
            result_text = f"Found {len(large_files)} files larger than {min_size_mb}MB"
            
            return ProcessingResult(
                success=True,
                message=result_text,
                count=len(large_files)
            )
        
        except Exception as e:
            return ProcessingResult(
                success=False,
                message=f"Error finding large files: {str(e)}"
            )
