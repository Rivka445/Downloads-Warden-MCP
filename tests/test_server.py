"""Tests for server tools using DI and mocks."""

import sys
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import server
from server import create_server
from models import ScanResult, OperationResult, LargeFilesResult, CategoryStats, FileInfo
from rate_limiter import clear_rate_limit_cache, _last_calls


@pytest.fixture(autouse=True)
def mock_service():
    mock = MagicMock()
    create_server(service=mock)
    clear_rate_limit_cache()
    yield mock
    clear_rate_limit_cache()
    from utils import get_downloads_path
    from services import DownloadsService
    create_server(service=DownloadsService(get_downloads_path()))


# ==================== scan_downloads ====================

@pytest.mark.asyncio
async def test_scan_downloads_success(mock_service):
    mock_service.scan_downloads.return_value = ScanResult(
        success=True,
        message='ok',
        total_files=5,
        total_size_mb=12.5,
        by_category={'documents': CategoryStats(count=3, size_mb=8.0)},
        by_extension={'.pdf': CategoryStats(count=3, size_mb=8.0)},
    )
    result = await server.scan_downloads()
    assert 'Total Files: 5' in result
    assert 'DOCUMENTS' in result
    mock_service.scan_downloads.assert_called_once()


@pytest.mark.asyncio
async def test_scan_downloads_failure(mock_service):
    from exceptions import PathNotFoundError
    mock_service.scan_downloads.side_effect = PathNotFoundError('/fake')
    with pytest.raises(PathNotFoundError):
        await server.scan_downloads()


# ==================== smart_sort_files ====================

@pytest.mark.asyncio
async def test_smart_sort_success(mock_service):
    mock_service.smart_sort_files.return_value = OperationResult(
        success=True, message='ok', count=10
    )
    result = await server.smart_sort_files()
    assert '✅' in result
    assert 'Moved 10 files' in result


@pytest.mark.asyncio
async def test_smart_sort_with_errors(mock_service):
    mock_service.smart_sort_files.return_value = OperationResult(
        success=True, message='ok', count=3,
        errors=['Error moving file.txt: permission denied']
    )
    result = await server.smart_sort_files()
    assert '⚠️' in result
    assert 'permission denied' in result


# ==================== deduplicate_by_hash ====================

@pytest.mark.asyncio
async def test_deduplicate_by_hash(mock_service):
    mock_service.deduplicate_by_hash.return_value = OperationResult(
        success=True, message='ok', count=4
    )
    result = await server.deduplicate_by_hash()
    assert 'Removed 4 duplicate files' in result


# ==================== auto_extract_and_cleanup ====================

@pytest.mark.asyncio
async def test_auto_extract_success(mock_service):
    mock_service.auto_extract_and_cleanup.return_value = OperationResult(
        success=True, message='ok', count=2
    )
    result = await server.auto_extract_and_cleanup()
    assert 'Extracted 2 archive files' in result
    assert 'Cleaned up' in result


@pytest.mark.asyncio
async def test_auto_extract_no_files(mock_service):
    mock_service.auto_extract_and_cleanup.return_value = OperationResult(
        success=True, message='ok', count=0
    )
    result = await server.auto_extract_and_cleanup()
    assert 'Extracted 0' in result
    assert 'Cleaned up' not in result


# ==================== clear_installers ====================

@pytest.mark.asyncio
async def test_clear_installers(mock_service):
    mock_service.clear_installers.return_value = OperationResult(
        success=True, message='ok', count=3
    )
    result = await server.clear_installers()
    assert 'Removed 3 old installer files' in result


# ==================== find_large_files ====================

@pytest.mark.asyncio
async def test_find_large_files_with_results(mock_service):
    mock_service.find_large_files.return_value = LargeFilesResult(
        success=True,
        message='ok',
        count=2,
        files=[FileInfo('bigfile.iso', 1200.0), FileInfo('video.mkv', 800.5)],
        total_size_mb=2000.5,
    )
    result = await server.find_large_files(500)
    assert 'bigfile.iso' in result
    assert 'video.mkv' in result
    assert '2000.50 MB' in result
    mock_service.find_large_files.assert_called_once_with(500)


@pytest.mark.asyncio
async def test_find_large_files_empty(mock_service):
    mock_service.find_large_files.return_value = LargeFilesResult(
        success=True, message='ok', count=0, files=[], total_size_mb=0
    )
    result = await server.find_large_files(500)
    assert 'Found 0 large files' in result


@pytest.mark.asyncio
async def test_find_large_files_failure(mock_service):
    from exceptions import PathNotFoundError
    mock_service.find_large_files.side_effect = PathNotFoundError('/fake')
    with pytest.raises(PathNotFoundError):
        await server.find_large_files(500)


# ==================== deduplicate_folders ====================

@pytest.mark.asyncio
async def test_deduplicate_folders(mock_service):
    mock_service.deduplicate_folders.return_value = OperationResult(
        success=True, message='ok', count=1
    )
    result = await server.deduplicate_folders()
    assert 'Removed 1 duplicate folders' in result


@pytest.mark.asyncio
async def test_deduplicate_folders_with_errors(mock_service):
    mock_service.deduplicate_folders.return_value = OperationResult(
        success=True, message='ok', count=0,
        errors=['Error deleting folder: access denied']
    )
    result = await server.deduplicate_folders()
    assert 'access denied' in result


# ==================== DI wiring ====================

def test_create_server_injects_service():
    custom_mock = MagicMock()
    create_server(service=custom_mock)
    assert server.downloads_service is custom_mock


def test_create_server_with_path_resolver():
    from services import DownloadsService
    create_server(service=DownloadsService('/tmp/fake_downloads'))
    assert isinstance(server.downloads_service, DownloadsService)


# ==================== Rate limiting ====================

@pytest.mark.asyncio
async def test_rate_limit_blocks_second_call(mock_service):
    """Second call within rate limit window should raise DownloadsWardenError."""
    from exceptions import DownloadsWardenError
    mock_service.smart_sort_files.return_value = OperationResult(
        success=True, message='ok', count=0
    )
    clear_rate_limit_cache()
    await server.smart_sort_files()
    with pytest.raises(DownloadsWardenError, match="too recently"):
        await server.smart_sort_files()


@pytest.mark.asyncio
async def test_rate_limit_allows_call_after_window(mock_service):
    """Call after rate limit window has passed should succeed."""
    from datetime import timedelta
    mock_service.smart_sort_files.return_value = OperationResult(
        success=True, message='ok', count=0
    )
    _last_calls['smart_sort_files'] = datetime.now() - timedelta(seconds=10)
    result = await server.smart_sort_files()
    assert result is not None


@pytest.mark.asyncio
async def test_rate_limit_read_only_tools_not_limited(mock_service):
    """Read-only tools scan_downloads and find_large_files are not rate limited."""
    mock_service.scan_downloads.return_value = ScanResult(
        success=True, message='ok', total_files=0, total_size_mb=0.0,
        by_category={}, by_extension={}
    )
    _last_calls.clear()
    await server.scan_downloads()
    await server.scan_downloads()  # should not raise
