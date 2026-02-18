#!/usr/bin/env python3
"""
Downloads Warden MCP Server
A Model Context Protocol server for intelligent Downloads folder management
"""

import sys
import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from src.utils import get_downloads_path
from src.services import DownloadsService

# Setup logging to stderr to avoid corrupting stdio-based MCP
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("downloads-warden")

# Initialize downloads service
downloads_path = get_downloads_path()
downloads_service = DownloadsService(downloads_path)


@mcp.tool()
async def scan_downloads() -> str:
    """Scan the Downloads folder and return detailed statistics about files.
    
    Returns a report with:
    - Total number of files
    - Total folder size in MB
    - Breakdown by file category
    - Top file types
    """
    logger.info("Scanning downloads folder")
    result = downloads_service.scan_downloads()
    
    if not result.success:
        return result.message
    
    stats = result.data
    
    # Format output
    report = f"""📊 Downloads Folder Analysis Report
{'='*50}

📈 Overall Statistics:
   Total Files: {stats.total_files}
   Total Size: {stats.total_size_mb:.2f} MB

📁 Files by Category:
"""
    for category, data in sorted(stats.by_category.items()):
        report += f"   • {category.upper()}: {data['count']} files ({data['size_mb']:.2f} MB)\n"
    
    report += "\n📄 Top 10 File Types:\n"
    sorted_exts = sorted(stats.by_extension.items(), key=lambda x: x[1]['count'], reverse=True)[:10]
    for ext, data in sorted_exts:
        report += f"   • {ext}: {data['count']} files ({data['size_mb']:.2f} MB)\n"
    
    return report


@mcp.tool()
async def smart_sort_files() -> str:
    """Intelligently sort all files in Downloads into category folders.
    
    Organizes files into these categories:
    - documents: PDF, DOCX, TXT, XLSX, PPTX
    - media: JPG, PNG, MP4, MP3
    - installers: EXE, MSI, DMG
    - code: PY, JS, TS, HTML, CSS
    - archives: ZIP, RAR, 7Z
    - other: Miscellaneous files
    """
    logger.info("Starting smart sort operation")
    result = downloads_service.smart_sort_files()
    
    report = f"{'✅' if result.success else '❌'} Smart Sort Complete!\n\n"
    report += f"Moved {result.count} files into organized categories:\n"
    report += f"  • documents/\n"
    report += f"  • media/\n"
    report += f"  • installers/\n"
    report += f"  • code/\n"
    report += f"  • archives/\n"
    report += f"  • other/\n"
    
    if result.errors:
        report += f"\n⚠️ Errors:\n"
        for error in result.errors:
            report += f"  • {error}\n"
    
    return report


@mcp.tool()
async def deduplicate_by_hash() -> str:
    """Find and remove duplicate files based on SHA-256 hash.
    
    This tool:
    - Calculates SHA-256 hash for all files
    - Identifies exact duplicates
    - Keeps one copy and removes all others
    - Safely handles errors during deletion
    """
    logger.info("Starting deduplication")
    result = downloads_service.deduplicate_by_hash()
    
    report = f"🗑️ Deduplication Complete!\n\n"
    report += f"Removed {result.count} duplicate files\n"
    report += f"Saved space by eliminating exact copies\n"
    
    return report


@mcp.tool()
async def auto_extract_and_cleanup() -> str:
    """Extract all ZIP files and remove the original archives.
    
    This tool:
    - Finds all ZIP files
    - Extracts each to a folder with the same name
    - Removes the original archive
    - Reports any extraction errors
    """
    logger.info("Starting auto-extraction")
    result = downloads_service.auto_extract_and_cleanup()
    
    report = f"📦 Extraction Complete!\n\n"
    report += f"Extracted {result.count} archive files\n"
    if result.count > 0:
        report += f"Cleaned up original archive files\n"
    
    if result.errors:
        report += f"\n⚠️ Errors:\n"
        for error in result.errors:
            report += f"  • {error}\n"
    
    return report


@mcp.tool()
async def clear_installers() -> str:
    """Remove old installer files (exe, msi, dmg) older than 7 days.
    
    This tool:
    - Identifies installer files (.exe, .msi, .dmg, .pkg, .deb, .rpm)
    - Checks modification date
    - Removes installers older than 7 days
    - Frees up disk space from unused installations
    """
    logger.info("Starting installer cleanup")
    result = downloads_service.clear_installers()
    
    report = f"🧹 Installer Cleanup Complete!\n\n"
    report += f"Removed {result.count} old installer files (older than 7 days)\n"
    report += f"Freed up space from unused installation files\n"
    
    return report


@mcp.tool()
async def find_large_files(min_size_mb: float = 500) -> str:
    """Find files larger than specified size threshold.
    
    Args:
        min_size_mb: Minimum file size in MB (default: 500)
    
    Returns a list of large files with their sizes.
    """
    logger.info(f"Finding files larger than {min_size_mb}MB")
    result = downloads_service.find_large_files(min_size_mb)
    
    if not result.success:
        return result.message
    
    # Get detailed file list
    from pathlib import Path
    from src.utils import get_file_size_mb
    
    large_files = []
    for file_path in Path(downloads_path).rglob('*'):
        if file_path.is_file():
            size_mb = get_file_size_mb(str(file_path))
            if size_mb >= min_size_mb:
                large_files.append((file_path, size_mb))
    
    large_files.sort(key=lambda x: x[1], reverse=True)
    
    report = f"🔍 Large Files Report (>{min_size_mb}MB)\n"
    report += f"{'='*50}\n\n"
    report += f"Found {len(large_files)} large files:\n\n"
    
    total_size = 0
    for file_path, size_mb in large_files[:20]:  # Top 20
        total_size += size_mb
        report += f"   📄 {file_path.name}\n      Size: {size_mb:.2f} MB\n\n"
    
    if len(large_files) > 20:
        report += f"   ... and {len(large_files) - 20} more files\n"
    
    report += f"\nTotal size of large files: {total_size:.2f} MB\n"
    
    return report


def main():
    """Initialize and run the MCP server."""
    logger.info("Starting Downloads Warden MCP Server")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
