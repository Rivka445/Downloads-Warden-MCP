"""Tests for utility functions."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils import get_file_category, get_downloads_path, get_file_size_mb


class TestUtilityFunctions:
    """Test suite for utility functions."""
    
    def test_get_file_category_documents(self):
        """Test document file categorization."""
        # Categories are capitalized
        category = get_file_category("file.pdf").lower()
        assert "document" in category or "documents" in category
        
        category = get_file_category("file.docx").lower()
        assert "document" in category or "documents" in category
    
    def test_get_file_category_media(self):
        """Test media file categorization."""
        category = get_file_category("image.jpg").lower()
        assert "image" in category or "media" in category or "video" in category
        
        category = get_file_category("video.mp4").lower()
        assert "image" in category or "media" in category or "video" in category
    
    def test_get_file_category_installers(self):
        """Test installer file categorization."""
        category = get_file_category("setup.exe").lower()
        assert "executable" in category or "installer" in category
        
        category = get_file_category("installer.msi").lower()
        assert "executable" in category or "installer" in category
    
    def test_get_file_category_code(self):
        """Test code file categorization."""
        category = get_file_category("script.py").lower()
        assert "code" in category
        
        category = get_file_category("app.js").lower()
        assert "code" in category
    
    def test_get_file_category_archives(self):
        """Test archive file categorization."""
        category = get_file_category("archive.zip").lower()
        assert "archive" in category
        
        category = get_file_category("backup.tar").lower()
        assert "archive" in category
    
    def test_get_file_category_unknown(self):
        """Test unknown file categorization."""
        category = get_file_category("unknown.xyz").lower()
        assert "other" in category
        
        category = get_file_category("noextension").lower()
        assert "other" in category
    
    def test_get_downloads_path(self):
        """Test getting downloads path."""
        path = get_downloads_path()
        assert path is not None
        # Could be string or Path object
        path_str = str(path)
        assert "Downloads" in path_str
    
    def test_get_file_size_mb(self, tmp_path):
        """Test file size calculation."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("x" * 1000)  # 1000 bytes
        
        size = get_file_size_mb(str(test_file))
        assert size > 0
        assert isinstance(size, float)

