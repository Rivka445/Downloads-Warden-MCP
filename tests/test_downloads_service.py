import sys
import pytest
from pathlib import Path
import shutil

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from services import DownloadsService
from exceptions import PathNotFoundError, HashCalculationError


class TestDownloadsService:
    """Test suite for DownloadsService."""

    # ==================== scan_downloads Tests ====================

    def test_scan_downloads_invalid_path(self):
        """Test scan with invalid path raises PathNotFoundError."""
        service = DownloadsService("/invalid/path/that/does/not/exist")
        with pytest.raises(PathNotFoundError):
            service.scan_downloads()
    
    def test_scan_downloads_empty_folder(self, tmp_path):
        """Test scan on empty folder."""
        service = DownloadsService(str(tmp_path))
        result = service.scan_downloads()
        assert result['success']
        assert result['stats']['total_files'] == 0
        assert result['stats']['total_size_mb'] == 0
    
    def test_scan_downloads_with_files(self, tmp_path):
        """Test scan with multiple files."""
        # Create test files
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.pdf").write_text("content2")
        (tmp_path / "file3.jpg").write_text("content3")
        
        service = DownloadsService(str(tmp_path))
        result = service.scan_downloads()
        assert result['success']
        assert result['stats']['total_files'] == 3
        assert 'by_category' in result['stats']
        assert 'by_extension' in result['stats']
    
    def test_scan_downloads_categories(self, tmp_path):
        """Test scan categorizes files correctly."""
        (tmp_path / "file1.pdf").write_text("content")
        (tmp_path / "file2.txt").write_text("content")
        (tmp_path / "file3.py").write_text("content")
        
        service = DownloadsService(str(tmp_path))
        result = service.scan_downloads()
        assert result['success']
        categories = result['stats']['by_category']
        # Check for capitalized category names
        category_names = [cat.lower() for cat in categories.keys()]
        assert any('document' in cat for cat in category_names)
        assert any('code' in cat for cat in category_names)
    
    # ==================== smart_sort_files Tests ====================
    
    def test_smart_sort_empty_folder(self, tmp_path):
        """Test sort on empty folder."""
        service = DownloadsService(str(tmp_path))
        result = service.smart_sort_files()
        assert result['success']
        assert result['count'] == 0
    
    def test_smart_sort_creates_categories(self, tmp_path):
        """Test sort creates category folders."""
        (tmp_path / "file1.pdf").write_text("content")
        (tmp_path / "file2.py").write_text("content")
        (tmp_path / "file3.jpg").write_text("content")
        
        service = DownloadsService(str(tmp_path))
        result = service.smart_sort_files()
        assert result['success']
        assert result['count'] == 3
        
        # Check folders were created (case-insensitive)
        folders = [f.name for f in tmp_path.iterdir() if f.is_dir()]
        assert any('document' in f.lower() for f in folders)
        assert any('code' in f.lower() for f in folders)
    
    def test_smart_sort_moves_files(self, tmp_path):
        """Test sort actually moves files."""
        pdf_file = tmp_path / "document.pdf"
        pdf_file.write_text("content")
        
        service = DownloadsService(str(tmp_path))
        result = service.smart_sort_files()
        assert result['success']
        
        # Original file should be moved
        assert not pdf_file.exists()
        # File should be in documents folder
        assert (tmp_path / "documents" / "document.pdf").exists()
    
    # ==================== deduplicate_by_hash Tests ====================
    
    def test_deduplicate_no_duplicates(self, tmp_path):
        """Test deduplication with no duplicates."""
        (tmp_path / "test1.txt").write_text("unique content 1")
        (tmp_path / "test2.txt").write_text("unique content 2")
        
        service = DownloadsService(str(tmp_path))
        result = service.deduplicate_by_hash()
        assert result['success']
        assert result['count'] == 0
    
    def test_deduplicate_finds_duplicates(self, tmp_path):
        """Test deduplication finds duplicate files."""
        content = "identical content"
        (tmp_path / "file1.txt").write_text(content)
        (tmp_path / "file2.txt").write_text(content)
        (tmp_path / "file3.txt").write_text(content)
        
        service = DownloadsService(str(tmp_path))
        result = service.deduplicate_by_hash()
        assert result['success']
        # Should remove 2 duplicates (keeping 1)
        assert result['count'] == 2
        # Only 1 file should remain
        assert len(list(tmp_path.glob("*.txt"))) == 1
    
    def test_deduplicate_keeps_one_copy(self, tmp_path):
        """Test deduplication keeps one copy of duplicates."""
        content = "same"
        (tmp_path / "dup1.txt").write_text(content)
        (tmp_path / "dup2.txt").write_text(content)
        
        service = DownloadsService(str(tmp_path))
        result = service.deduplicate_by_hash()
        assert result['success']
        assert result['count'] == 1
        assert len(list(tmp_path.glob("*.txt"))) == 1
    
    # ==================== auto_extract_and_cleanup Tests ====================
    
    def test_auto_extract_no_zips(self, tmp_path):
        """Test extraction with no ZIP files."""
        (tmp_path / "file.txt").write_text("content")
        
        service = DownloadsService(str(tmp_path))
        result = service.auto_extract_and_cleanup()
        assert result['success']
        assert result['count'] == 0
    
    def test_auto_extract_creates_folder(self, tmp_path):
        """Test extraction creates folder."""
        import zipfile
        
        # Create a ZIP file
        zip_path = tmp_path / "archive.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("file1.txt", "content1")
            zf.writestr("file2.txt", "content2")
        
        service = DownloadsService(str(tmp_path))
        result = service.auto_extract_and_cleanup()
        assert result['success']
        assert result['count'] == 1
        
        # Check extraction folder was created
        assert (tmp_path / "archive").exists()
        assert (tmp_path / "archive" / "file1.txt").exists()
        
        # Original ZIP should be removed
        assert not zip_path.exists()
    
    # ==================== clear_installers Tests ====================
    
    def test_clear_installers_no_installers(self, tmp_path):
        """Test installer cleanup with no installers."""
        (tmp_path / "document.pdf").write_text("content")
        
        service = DownloadsService(str(tmp_path))
        result = service.clear_installers()
        assert result['success']
        assert result['count'] == 0
    
    def test_clear_installers_removes_old(self, tmp_path):
        """Test installer cleanup removes old installers."""
        import os
        from datetime import datetime, timedelta
        
        # Create installer files
        exe_file = tmp_path / "setup.exe"
        exe_file.write_text("content")
        
        # Set modification time to 8 days ago
        old_time = (datetime.now() - timedelta(days=8)).timestamp()
        os.utime(exe_file, (old_time, old_time))
        
        service = DownloadsService(str(tmp_path))
        result = service.clear_installers()
        assert result['success']
        assert result['count'] == 1
        assert not exe_file.exists()
    
    def test_clear_installers_keeps_recent(self, tmp_path):
        """Test installer cleanup keeps recent installers."""
        msi_file = tmp_path / "setup.msi"
        msi_file.write_text("content")
        
        service = DownloadsService(str(tmp_path))
        result = service.clear_installers()
        assert result['success']
        assert result['count'] == 0
        # File should still exist
        assert msi_file.exists()
    
    # ==================== find_large_files Tests ====================
    
    def test_find_large_files_empty_folder(self, tmp_path):
        """Test finding large files in empty folder."""
        service = DownloadsService(str(tmp_path))
        result = service.find_large_files(500)
        assert result['success']
        assert result['count'] == 0
    
    def test_find_large_files_with_small_files(self, tmp_path):
        """Test finding large files with only small files."""
        (tmp_path / "small1.txt").write_text("x" * 100)
        (tmp_path / "small2.txt").write_text("x" * 100)
        
        service = DownloadsService(str(tmp_path))
        result = service.find_large_files(1)  # 1 MB threshold
        assert result['success']
        assert result['count'] == 0
    
    def test_find_large_files_default_threshold(self, tmp_path):
        """Test finding large files with default threshold."""
        service = DownloadsService(str(tmp_path))
        result = service.find_large_files()  # Default 500MB
        assert result['success']
        assert result['count'] == 0
    
    # ==================== deduplicate_folders Tests ====================
    
    def test_deduplicate_folders_no_folders(self, tmp_path):
        """Test folder deduplication with no folders."""
        (tmp_path / "file.txt").write_text("content")
        
        service = DownloadsService(str(tmp_path))
        result = service.deduplicate_folders()
        assert result['success']
        assert result['count'] == 0
    
    def test_deduplicate_folders_unique_folders(self, tmp_path):
        """Test folder deduplication with unique folders."""
        (tmp_path / "folder1").mkdir()
        (tmp_path / "folder1" / "file.txt").write_text("content1")
        
        (tmp_path / "folder2").mkdir()
        (tmp_path / "folder2" / "file.txt").write_text("content2")
        
        service = DownloadsService(str(tmp_path))
        result = service.deduplicate_folders()
        assert result['success']
        assert result['count'] == 0
        # Both folders should still exist
        assert (tmp_path / "folder1").exists()
        assert (tmp_path / "folder2").exists()
    
    def test_deduplicate_folders_finds_duplicates(self, tmp_path):
        """Test folder deduplication finds duplicate folders."""
        content = "identical"
        
        # Create folder 1
        folder1 = tmp_path / "folder1"
        folder1.mkdir()
        (folder1 / "file.txt").write_text(content)
        
        # Create folder 2 (duplicate)
        folder2 = tmp_path / "folder2"
        folder2.mkdir()
        (folder2 / "file.txt").write_text(content)
        
        service = DownloadsService(str(tmp_path))
        result = service.deduplicate_folders()
        assert result['success']
        # Should remove 1 duplicate folder
        assert result['count'] == 1
    
    def test_deduplicate_folders_keeps_original(self, tmp_path):
        """Test folder deduplication keeps original."""
        content = "same"
        
        # Create original
        folder1 = tmp_path / "original"
        folder1.mkdir()
        (folder1 / "data.txt").write_text(content)
        
        # Create duplicate
        folder2 = tmp_path / "duplicate"
        folder2.mkdir()
        (folder2 / "data.txt").write_text(content)
        
        service = DownloadsService(str(tmp_path))
        result = service.deduplicate_folders()
        assert result['success']
        
        # One folder should be deleted
        assert result['count'] == 1
        
        # Check that one folder exists and one was removed
        remaining_folders = [f for f in tmp_path.iterdir() if f.is_dir()]
        assert len(remaining_folders) == 1
    
    def test_deduplicate_folders_nested_files(self, tmp_path):
        """Test folder deduplication with nested files."""
        # Create folder 1 with nested structure
        folder1 = tmp_path / "folder1"
        folder1.mkdir()
        (folder1 / "subdir").mkdir()
        (folder1 / "subdir" / "file.txt").write_text("content")
        
        # Create folder 2 with same structure
        folder2 = tmp_path / "folder2"
        folder2.mkdir()
        (folder2 / "subdir").mkdir()
        (folder2 / "subdir" / "file.txt").write_text("content")
        
        service = DownloadsService(str(tmp_path))
        result = service.deduplicate_folders()
        assert result['success']
        assert result['count'] == 1
