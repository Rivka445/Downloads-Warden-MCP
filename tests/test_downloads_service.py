"""Unit tests for DownloadsService."""

import pytest
from pathlib import Path
from src.services import DownloadsService


class TestDownloadsService:
    """Test suite for DownloadsService."""
    
    def test_scan_downloads_invalid_path(self):
        """Test scan with invalid path."""
        service = DownloadsService("/invalid/path/that/does/not/exist")
        result = service.scan_downloads()
        assert not result.success
        assert "not found" in result.message.lower()
    
    def test_scan_downloads_empty_folder(self, tmp_path):
        """Test scan on empty folder."""
        service = DownloadsService(str(tmp_path))
        result = service.scan_downloads()
        assert result.success
        assert result.data.total_files == 0
        assert result.data.total_size_mb == 0
    
    def test_smart_sort_empty_folder(self, tmp_path):
        """Test sort on empty folder."""
        service = DownloadsService(str(tmp_path))
        result = service.smart_sort_files()
        assert result.success
        assert result.count == 0
    
    def test_deduplicate_no_duplicates(self, tmp_path):
        """Test deduplication with no duplicates."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("unique content")
        
        service = DownloadsService(str(tmp_path))
        result = service.deduplicate_by_hash()
        assert result.success
        assert result.count == 0
    
    def test_clear_installers_no_installers(self, tmp_path):
        """Test installer cleanup with no installers."""
        test_file = tmp_path / "document.pdf"
        test_file.write_text("content")
        
        service = DownloadsService(str(tmp_path))
        result = service.clear_installers()
        assert result.success
        assert result.count == 0
    
    def test_find_large_files_empty_folder(self, tmp_path):
        """Test finding large files in empty folder."""
        service = DownloadsService(str(tmp_path))
        result = service.find_large_files(500)
        assert result.success
        assert result.count == 0
