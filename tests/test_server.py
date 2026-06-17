"""Tests for server tools using DI and mocks."""

import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import server
from server import create_server, mcp


@pytest.fixture(autouse=True)
def mock_service():
    """Inject a fresh mock service before each test."""
    mock = MagicMock()
    create_server(service=mock)
    yield mock
    # Restore default after test
    from utils import get_downloads_path
    from services import DownloadsService
    create_server(service=DownloadsService(get_downloads_path()))


# ==================== scan_downloads ====================

@pytest.mark.asyncio
async def test_scan_downloads_success(mock_service):
    mock_service.scan_downloads.return_value = {
        'success': True,
        'stats': {
            'total_files': 5,
            'total_size_mb': 12.5,
            'by_category': {'documents': {'count': 3, 'size_mb': 8.0}},
            'by_extension': {'.pdf': {'count': 3, 'size_mb': 8.0}},
        }
    }
    result = await server.scan_downloads()
    assert 'Total Files: 5' in result
    assert 'DOCUMENTS' in result
    mock_service.scan_downloads.assert_called_once()


@pytest.mark.asyncio
async def test_scan_downloads_failure(mock_service):
    mock_service.scan_downloads.return_value = {'success': False, 'message': 'not found'}
    result = await server.scan_downloads()
    assert result == 'not found'


# ==================== smart_sort_files ====================

@pytest.mark.asyncio
async def test_smart_sort_success(mock_service):
    mock_service.smart_sort_files.return_value = {
        'success': True, 'count': 10, 'errors': None
    }
    result = await server.smart_sort_files()
    assert '✅' in result
    assert 'Moved 10 files' in result


@pytest.mark.asyncio
async def test_smart_sort_with_errors(mock_service):
    mock_service.smart_sort_files.return_value = {
        'success': True, 'count': 3, 'errors': ['Error moving file.txt: permission denied']
    }
    result = await server.smart_sort_files()
    assert '⚠️' in result
    assert 'permission denied' in result


# ==================== deduplicate_by_hash ====================

@pytest.mark.asyncio
async def test_deduplicate_by_hash(mock_service):
    mock_service.deduplicate_by_hash.return_value = {'success': True, 'count': 4}
    result = await server.deduplicate_by_hash()
    assert 'Removed 4 duplicate files' in result


# ==================== auto_extract_and_cleanup ====================

@pytest.mark.asyncio
async def test_auto_extract_success(mock_service):
    mock_service.auto_extract_and_cleanup.return_value = {
        'success': True, 'count': 2, 'errors': None
    }
    result = await server.auto_extract_and_cleanup()
    assert 'Extracted 2 archive files' in result
    assert 'Cleaned up' in result


@pytest.mark.asyncio
async def test_auto_extract_no_files(mock_service):
    mock_service.auto_extract_and_cleanup.return_value = {
        'success': True, 'count': 0, 'errors': None
    }
    result = await server.auto_extract_and_cleanup()
    assert 'Extracted 0' in result
    assert 'Cleaned up' not in result


# ==================== clear_installers ====================

@pytest.mark.asyncio
async def test_clear_installers(mock_service):
    mock_service.clear_installers.return_value = {'success': True, 'count': 3}
    result = await server.clear_installers()
    assert 'Removed 3 old installer files' in result


# ==================== find_large_files ====================

@pytest.mark.asyncio
async def test_find_large_files_with_results(mock_service):
    mock_service.find_large_files.return_value = {
        'success': True,
        'count': 2,
        'files': [('bigfile.iso', 1200.0), ('video.mkv', 800.5)],
        'total_size_mb': 2000.5,
    }
    result = await server.find_large_files(500)
    assert 'bigfile.iso' in result
    assert 'video.mkv' in result
    assert '2000.50 MB' in result
    mock_service.find_large_files.assert_called_once_with(500)


@pytest.mark.asyncio
async def test_find_large_files_empty(mock_service):
    mock_service.find_large_files.return_value = {
        'success': True, 'count': 0, 'files': [], 'total_size_mb': 0
    }
    result = await server.find_large_files(500)
    assert 'Found 0 large files' in result


@pytest.mark.asyncio
async def test_find_large_files_failure(mock_service):
    mock_service.find_large_files.return_value = {
        'success': False, 'message': 'scan error'
    }
    result = await server.find_large_files(500)
    assert result == 'scan error'


# ==================== deduplicate_folders ====================

@pytest.mark.asyncio
async def test_deduplicate_folders(mock_service):
    mock_service.deduplicate_folders.return_value = {
        'success': True, 'count': 1, 'errors': None
    }
    result = await server.deduplicate_folders()
    assert 'Removed 1 duplicate folders' in result


@pytest.mark.asyncio
async def test_deduplicate_folders_with_errors(mock_service):
    mock_service.deduplicate_folders.return_value = {
        'success': True, 'count': 0, 'errors': ['Error deleting folder: access denied']
    }
    result = await server.deduplicate_folders()
    assert 'access denied' in result


# ==================== DI wiring ====================

def test_create_server_injects_service():
    """Verify create_server replaces the global service."""
    custom_mock = MagicMock()
    create_server(service=custom_mock)
    assert server.downloads_service is custom_mock


def test_create_server_with_path_resolver():
    """Verify create_server accepts a path resolver callable."""
    from services import DownloadsService
    create_server(service=DownloadsService('/tmp/fake_downloads'))
    assert isinstance(server.downloads_service, DownloadsService)
