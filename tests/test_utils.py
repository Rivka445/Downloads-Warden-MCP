"""Tests for utility functions."""

from src.utils import get_file_category, get_downloads_path, get_file_size_mb


class TestUtilityFunctions:
    """Test suite for utility functions."""
    
    def test_get_file_category_documents(self):
        """Test document file categorization."""
        assert get_file_category("file.pdf") == "documents"
        assert get_file_category("file.docx") == "documents"
        assert get_file_category("file.txt") == "documents"
    
    def test_get_file_category_media(self):
        """Test media file categorization."""
        assert get_file_category("image.jpg") == "media"
        assert get_file_category("video.mp4") == "media"
        assert get_file_category("audio.mp3") == "media"
    
    def test_get_file_category_installers(self):
        """Test installer file categorization."""
        assert get_file_category("setup.exe") == "installers"
        assert get_file_category("installer.msi") == "installers"
    
    def test_get_file_category_code(self):
        """Test code file categorization."""
        assert get_file_category("script.py") == "code"
        assert get_file_category("app.js") == "code"
    
    def test_get_file_category_archives(self):
        """Test archive file categorization."""
        assert get_file_category("archive.zip") == "archives"
        assert get_file_category("backup.tar") == "archives"
    
    def test_get_file_category_unknown(self):
        """Test unknown file categorization."""
        assert get_file_category("unknown.xyz") == "other"
        assert get_file_category("noextension") == "other"
    
    def test_get_downloads_path(self):
        """Test getting downloads path."""
        path = get_downloads_path()
        assert path is not None
        assert isinstance(path, str)
        assert "Downloads" in path
