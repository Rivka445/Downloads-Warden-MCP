#!/usr/bin/env python3
"""
Downloads Warden MCP Server
A Model Context Protocol server for intelligent Downloads folder management
"""

import os
import sys
import json
import asyncio
import hashlib
import shutil
import zipfile
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

try:
    from mcp.server.stdio import stdio_server
    from mcp.server import Server
    import mcp.types as types
except ImportError as e:
    print(f"Error importing MCP: {e}")
    print("Please install MCP SDK: pip install mcp")
    sys.exit(1)


# Initialize MCP Server
server = Server("downloads-warden")


def get_downloads_path():
    """Get the user's Downloads folder path"""
    if sys.platform == "win32":
        return str(Path.home() / "Downloads")
    elif sys.platform == "darwin":
        return str(Path.home() / "Downloads")
    else:
        return str(Path.home() / "Downloads")


def get_file_category(filepath: str) -> str:
    """Categorize file by extension"""
    ext = Path(filepath).suffix.lower()
    
    categories = {
        'documents': ['.pdf', '.docx', '.doc', '.txt', '.xlsx', '.xls', '.pptx', '.ppt', '.rtf'],
        'media': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.mp4', '.avi', '.mov', '.mkv', '.mp3', '.flac', '.wav'],
        'installers': ['.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm'],
        'code': ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.html', '.css', '.json', '.yaml', '.yml'],
        'archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
    }
    
    for category, extensions in categories.items():
        if ext in extensions:
            return category
    
    return 'other'


def calculate_file_hash(filepath: str) -> str:
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List all available tools"""
    return [
        types.Tool(
            name="scan_downloads",
            description="Scan the Downloads folder and return detailed statistics about files",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="smart_sort_files",
            description="Intelligently sort all files in Downloads into category folders",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="deduplicate_by_hash",
            description="Find and remove duplicate files based on SHA-256 hash",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="auto_extract_and_cleanup",
            description="Extract all ZIP/RAR files and remove the original archives",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="clear_installers",
            description="Remove old installer files (exe, msi, dmg) older than 7 days",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="find_large_files",
            description="Find files larger than specified size threshold",
            inputSchema={
                "type": "object",
                "properties": {
                    "min_size_mb": {
                        "type": "number",
                        "description": "Minimum file size in MB (default: 500)",
                        "default": 500
                    }
                },
                "required": []
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls"""
    
    downloads_path = get_downloads_path()
    
    if name == "scan_downloads":
        return await handle_scan_downloads(downloads_path)
    
    elif name == "smart_sort_files":
        return await handle_smart_sort_files(downloads_path)
    
    elif name == "deduplicate_by_hash":
        return await handle_deduplicate_by_hash(downloads_path)
    
    elif name == "auto_extract_and_cleanup":
        return await handle_auto_extract_and_cleanup(downloads_path)
    
    elif name == "clear_installers":
        return await handle_clear_installers(downloads_path)
    
    elif name == "find_large_files":
        min_size_mb = arguments.get("min_size_mb", 500)
        return await handle_find_large_files(downloads_path, min_size_mb)
    
    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def handle_scan_downloads(path: str) -> list[types.TextContent]:
    """Implement scan_downloads tool"""
    try:
        downloads_dir = Path(path)
        if not downloads_dir.exists():
            return [types.TextContent(type="text", text=f"Downloads folder not found at {path}")]
        
        stats = {
            'total_files': 0,
            'total_size_mb': 0,
            'by_category': defaultdict(lambda: {'count': 0, 'size_mb': 0}),
            'by_extension': defaultdict(lambda: {'count': 0, 'size_mb': 0})
        }
        
        for file_path in downloads_dir.rglob('*'):
            if file_path.is_file():
                stats['total_files'] += 1
                size_bytes = file_path.stat().st_size
                size_mb = size_bytes / (1024 * 1024)
                stats['total_size_mb'] += size_mb
                
                category = get_file_category(str(file_path))
                stats['by_category'][category]['count'] += 1
                stats['by_category'][category]['size_mb'] += size_mb
                
                ext = file_path.suffix.lower() or 'no_extension'
                stats['by_extension'][ext]['count'] += 1
                stats['by_extension'][ext]['size_mb'] += size_mb
        
        # Format output
        report = f"""📊 Downloads Folder Analysis Report
{'='*50}

📈 Overall Statistics:
   Total Files: {stats['total_files']}
   Total Size: {stats['total_size_mb']:.2f} MB

📁 Files by Category:
"""
        for category, data in sorted(stats['by_category'].items()):
            report += f"   • {category.upper()}: {data['count']} files ({data['size_mb']:.2f} MB)\n"
        
        report += "\n📄 Top 10 File Types:\n"
        sorted_exts = sorted(stats['by_extension'].items(), key=lambda x: x[1]['count'], reverse=True)[:10]
        for ext, data in sorted_exts:
            report += f"   • {ext}: {data['count']} files ({data['size_mb']:.2f} MB)\n"
        
        return [types.TextContent(type="text", text=report)]
    
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error scanning downloads: {str(e)}")]


async def handle_smart_sort_files(path: str) -> list[types.TextContent]:
    """Implement smart_sort_files tool"""
    try:
        downloads_dir = Path(path)
        moved_count = 0
        
        for file_path in downloads_dir.iterdir():
            if file_path.is_file():
                category = get_file_category(str(file_path))
                category_dir = downloads_dir / category
                category_dir.mkdir(exist_ok=True)
                
                dest_path = category_dir / file_path.name
                if dest_path != file_path:
                    shutil.move(str(file_path), str(dest_path))
                    moved_count += 1
        
        report = f"✅ Smart Sort Complete!\n\n"
        report += f"Moved {moved_count} files into organized categories:\n"
        report += f"  • documents/\n"
        report += f"  • media/\n"
        report += f"  • installers/\n"
        report += f"  • code/\n"
        report += f"  • archives/\n"
        report += f"  • other/\n"
        
        return [types.TextContent(type="text", text=report)]
    
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error sorting files: {str(e)}")]


async def handle_deduplicate_by_hash(path: str) -> list[types.TextContent]:
    """Implement deduplicate_by_hash tool"""
    try:
        downloads_dir = Path(path)
        hash_map = defaultdict(list)
        deleted_count = 0
        
        # Calculate hashes for all files
        for file_path in downloads_dir.rglob('*'):
            if file_path.is_file():
                try:
                    file_hash = calculate_file_hash(str(file_path))
                    hash_map[file_hash].append(file_path)
                except Exception as e:
                    print(f"Error hashing {file_path}: {e}")
        
        # Remove duplicates, keeping the first occurrence
        for file_hash, file_list in hash_map.items():
            if len(file_list) > 1:
                # Keep the first file, delete the rest
                for duplicate_file in file_list[1:]:
                    duplicate_file.unlink()
                    deleted_count += 1
        
        report = f"🗑️ Deduplication Complete!\n\n"
        report += f"Removed {deleted_count} duplicate files\n"
        report += f"Saved space by eliminating exact copies\n"
        
        return [types.TextContent(type="text", text=report)]
    
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error deduplicating files: {str(e)}")]


async def handle_auto_extract_and_cleanup(path: str) -> list[types.TextContent]:
    """Implement auto_extract_and_cleanup tool"""
    try:
        downloads_dir = Path(path)
        extracted_count = 0
        errors = []
        
        for archive_file in downloads_dir.rglob('*'):
            if archive_file.suffix.lower() == '.zip':
                try:
                    extract_dir = downloads_dir / archive_file.stem
                    extract_dir.mkdir(exist_ok=True)
                    
                    with zipfile.ZipFile(archive_file, 'r') as zip_ref:
                        zip_ref.extractall(extract_dir)
                    archive_file.unlink()
                    extracted_count += 1
                except Exception as e:
                    errors.append(f"Error extracting {archive_file.name}: {str(e)}")
        
        report = f"📦 Extraction Complete!\n\n"
        report += f"Extracted {extracted_count} archive files\n"
        if extracted_count > 0:
            report += f"Cleaned up original archive files\n"
        if errors:
            report += f"\n⚠️ Errors:\n"
            for error in errors:
                report += f"  • {error}\n"
        
        return [types.TextContent(type="text", text=report)]
    
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error extracting archives: {str(e)}")]


async def handle_clear_installers(path: str) -> list[types.TextContent]:
    """Implement clear_installers tool"""
    try:
        downloads_dir = Path(path)
        deleted_count = 0
        one_week_ago = datetime.now() - timedelta(days=7)
        
        installer_extensions = ['.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm']
        
        for file_path in downloads_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in installer_extensions:
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < one_week_ago:
                    file_path.unlink()
                    deleted_count += 1
        
        report = f"🧹 Installer Cleanup Complete!\n\n"
        report += f"Removed {deleted_count} old installer files (older than 7 days)\n"
        report += f"Freed up space from unused installation files\n"
        
        return [types.TextContent(type="text", text=report)]
    
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error clearing installers: {str(e)}")]


async def handle_find_large_files(path: str, min_size_mb: float) -> list[types.TextContent]:
    """Implement find_large_files tool"""
    try:
        downloads_dir = Path(path)
        large_files = []
        
        for file_path in downloads_dir.rglob('*'):
            if file_path.is_file():
                size_mb = file_path.stat().st_size / (1024 * 1024)
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
        
        return [types.TextContent(type="text", text=report)]
    
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error finding large files: {str(e)}")]


async def main():
    """Main server entry point"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            asyncio.Event(),
        )


if __name__ == "__main__":
    asyncio.run(main())
