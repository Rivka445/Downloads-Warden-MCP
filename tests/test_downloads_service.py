"""Unit tests for DownloadsService."""

import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from services import DownloadsService
from models import ScanResult, OperationResult, LargeFilesResult, FileInfo
from exceptions import PathNotFoundError


class TestDownloadsService:

    # ==================== scan_downloads ====================

    def test_scan_downloads_invalid_path(self):
        service = DownloadsService("/invalid/path/that/does/not/exist")
        with pytest.raises(PathNotFoundError):
            service.scan_downloads()

    def test_scan_downloads_empty_folder(self, tmp_path):
        result = DownloadsService(str(tmp_path)).scan_downloads()
        assert isinstance(result, ScanResult)
        assert result.success
        assert result.total_files == 0
        assert result.total_size_mb == 0

    def test_scan_downloads_with_files(self, tmp_path):
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.pdf").write_text("content2")
        (tmp_path / "file3.jpg").write_text("content3")
        result = DownloadsService(str(tmp_path)).scan_downloads()
        assert result.success
        assert result.total_files == 3
        assert result.by_category
        assert result.by_extension

    def test_scan_downloads_categories(self, tmp_path):
        (tmp_path / "file1.pdf").write_text("content")
        (tmp_path / "file2.txt").write_text("content")
        (tmp_path / "file3.py").write_text("content")
        result = DownloadsService(str(tmp_path)).scan_downloads()
        assert result.success
        category_names = [c.lower() for c in result.by_category]
        assert any('document' in c for c in category_names)
        assert any('code' in c for c in category_names)

    # ==================== smart_sort_files ====================

    def test_smart_sort_empty_folder(self, tmp_path):
        result = DownloadsService(str(tmp_path)).smart_sort_files()
        assert isinstance(result, OperationResult)
        assert result.success
        assert result.count == 0

    def test_smart_sort_creates_categories(self, tmp_path):
        (tmp_path / "file1.pdf").write_text("content")
        (tmp_path / "file2.py").write_text("content")
        (tmp_path / "file3.jpg").write_text("content")
        result = DownloadsService(str(tmp_path)).smart_sort_files()
        assert result.success
        assert result.count == 3
        folders = [f.name for f in tmp_path.iterdir() if f.is_dir()]
        assert any('document' in f.lower() for f in folders)
        assert any('code' in f.lower() for f in folders)

    def test_smart_sort_moves_files(self, tmp_path):
        pdf_file = tmp_path / "document.pdf"
        pdf_file.write_text("content")
        result = DownloadsService(str(tmp_path)).smart_sort_files()
        assert result.success
        assert not pdf_file.exists()
        assert (tmp_path / "documents" / "document.pdf").exists()

    # ==================== deduplicate_by_hash ====================

    def test_deduplicate_no_duplicates(self, tmp_path):
        (tmp_path / "test1.txt").write_text("unique content 1")
        (tmp_path / "test2.txt").write_text("unique content 2")
        result = DownloadsService(str(tmp_path)).deduplicate_by_hash()
        assert isinstance(result, OperationResult)
        assert result.success
        assert result.count == 0

    def test_deduplicate_finds_duplicates(self, tmp_path):
        content = "identical content"
        (tmp_path / "file1.txt").write_text(content)
        (tmp_path / "file2.txt").write_text(content)
        (tmp_path / "file3.txt").write_text(content)
        result = DownloadsService(str(tmp_path)).deduplicate_by_hash()
        assert result.success
        assert result.count == 2
        assert len(list(tmp_path.glob("*.txt"))) == 1

    def test_deduplicate_keeps_one_copy(self, tmp_path):
        content = "same"
        (tmp_path / "dup1.txt").write_text(content)
        (tmp_path / "dup2.txt").write_text(content)
        result = DownloadsService(str(tmp_path)).deduplicate_by_hash()
        assert result.success
        assert result.count == 1
        assert len(list(tmp_path.glob("*.txt"))) == 1

    # ==================== auto_extract_and_cleanup ====================

    def test_auto_extract_no_zips(self, tmp_path):
        (tmp_path / "file.txt").write_text("content")
        result = DownloadsService(str(tmp_path)).auto_extract_and_cleanup()
        assert isinstance(result, OperationResult)
        assert result.success
        assert result.count == 0

    def test_auto_extract_creates_folder(self, tmp_path):
        import zipfile
        zip_path = tmp_path / "archive.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("file1.txt", "content1")
            zf.writestr("file2.txt", "content2")
        result = DownloadsService(str(tmp_path)).auto_extract_and_cleanup()
        assert result.success
        assert result.count == 1
        assert (tmp_path / "archive").exists()
        assert (tmp_path / "archive" / "file1.txt").exists()
        assert not zip_path.exists()

    # ==================== clear_installers ====================

    def test_clear_installers_no_installers(self, tmp_path):
        (tmp_path / "document.pdf").write_text("content")
        result = DownloadsService(str(tmp_path)).clear_installers()
        assert isinstance(result, OperationResult)
        assert result.success
        assert result.count == 0

    def test_clear_installers_removes_old(self, tmp_path):
        import os
        from datetime import datetime, timedelta
        exe_file = tmp_path / "setup.exe"
        exe_file.write_text("content")
        old_time = (datetime.now() - timedelta(days=8)).timestamp()
        os.utime(exe_file, (old_time, old_time))
        result = DownloadsService(str(tmp_path)).clear_installers()
        assert result.success
        assert result.count == 1
        assert not exe_file.exists()

    def test_clear_installers_keeps_recent(self, tmp_path):
        msi_file = tmp_path / "setup.msi"
        msi_file.write_text("content")
        result = DownloadsService(str(tmp_path)).clear_installers()
        assert result.success
        assert result.count == 0
        assert msi_file.exists()

    # ==================== find_large_files ====================

    def test_find_large_files_empty_folder(self, tmp_path):
        result = DownloadsService(str(tmp_path)).find_large_files(500)
        assert isinstance(result, LargeFilesResult)
        assert result.success
        assert result.count == 0
        assert result.files == []

    def test_find_large_files_with_small_files(self, tmp_path):
        (tmp_path / "small1.txt").write_text("x" * 100)
        (tmp_path / "small2.txt").write_text("x" * 100)
        result = DownloadsService(str(tmp_path)).find_large_files(1)
        assert result.success
        assert result.count == 0

    def test_find_large_files_default_threshold(self, tmp_path):
        result = DownloadsService(str(tmp_path)).find_large_files()
        assert result.success
        assert result.count == 0

    # ==================== deduplicate_folders ====================

    def test_deduplicate_folders_no_folders(self, tmp_path):
        (tmp_path / "file.txt").write_text("content")
        result = DownloadsService(str(tmp_path)).deduplicate_folders()
        assert isinstance(result, OperationResult)
        assert result.success
        assert result.count == 0

    def test_deduplicate_folders_unique_folders(self, tmp_path):
        (tmp_path / "folder1").mkdir()
        (tmp_path / "folder1" / "file.txt").write_text("content1")
        (tmp_path / "folder2").mkdir()
        (tmp_path / "folder2" / "file.txt").write_text("content2")
        result = DownloadsService(str(tmp_path)).deduplicate_folders()
        assert result.success
        assert result.count == 0
        assert (tmp_path / "folder1").exists()
        assert (tmp_path / "folder2").exists()

    def test_deduplicate_folders_finds_duplicates(self, tmp_path):
        content = "identical"
        (tmp_path / "folder1").mkdir()
        (tmp_path / "folder1" / "file.txt").write_text(content)
        (tmp_path / "folder2").mkdir()
        (tmp_path / "folder2" / "file.txt").write_text(content)
        result = DownloadsService(str(tmp_path)).deduplicate_folders()
        assert result.success
        assert result.count == 1

    def test_deduplicate_folders_keeps_original(self, tmp_path):
        content = "same"
        (tmp_path / "original").mkdir()
        (tmp_path / "original" / "data.txt").write_text(content)
        (tmp_path / "duplicate").mkdir()
        (tmp_path / "duplicate" / "data.txt").write_text(content)
        result = DownloadsService(str(tmp_path)).deduplicate_folders()
        assert result.success
        assert result.count == 1
        remaining = [f for f in tmp_path.iterdir() if f.is_dir()]
        assert len(remaining) == 1

    def test_deduplicate_folders_nested_files(self, tmp_path):
        (tmp_path / "folder1").mkdir()
        (tmp_path / "folder1" / "subdir").mkdir()
        (tmp_path / "folder1" / "subdir" / "file.txt").write_text("content")
        (tmp_path / "folder2").mkdir()
        (tmp_path / "folder2" / "subdir").mkdir()
        (tmp_path / "folder2" / "subdir" / "file.txt").write_text("content")
        result = DownloadsService(str(tmp_path)).deduplicate_folders()
        assert result.success
        assert result.count == 1
