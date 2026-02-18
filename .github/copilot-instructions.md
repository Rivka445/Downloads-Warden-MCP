# Copilot Instructions for Downloads Warden MCP

## Project Overview
Downloads Warden is a Model Context Protocol (MCP) server written in Python that provides intelligent file management tools for the Downloads folder. This project uses the Python MCP SDK to expose 6 specialized tools through Claude.

## Key Documentation
- [MCP SDK for Python](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Specification](https://spec.modelcontextprotocol.io/)

## Project Structure
- `src/server.py` - Main MCP server with all 6 tools implemented
- `.vscode/mcp.json` - MCP server configuration for Claude Desktop
- `pyproject.toml` - Project metadata and dependencies
- `requirements.txt` - Python dependencies (mcp SDK)

## Implementation Details

### Tools Implemented
1. **scan_downloads** - Analyze folder statistics
2. **smart_sort_files** - Organize files by category
3. **deduplicate_by_hash** - Remove duplicate files
4. **auto_extract_and_cleanup** - Extract archives
5. **clear_installers** - Remove old installers
6. **find_large_files** - Identify large files

### Key Technologies
- **Python 3.10+** - Language
- **MCP SDK** - Server framework
- **asyncio** - Asynchronous operations
- **pathlib** - File operations
- **hashlib** - SHA-256 hashing

## Setup Instructions

### 1. Install Dependencies
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configure Claude Desktop
Edit `%APPDATA%\Claude\claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "downloads-warden": {
      "command": "python",
      "args": ["C:\\path\\to\\downloads-warden\\src\\server.py"]
    }
  }
}
```

### 3. Restart Claude Desktop

## Running & Testing
- Run server: `python src/server.py`
- Test with Claude Desktop after configuration
- All operations are local and safe (with backups recommended)

## Development Notes
- Use asyncio for all I/O operations
- All tools follow MCP Tool schema
- File operations use pathlib for cross-platform compatibility
- Hashing uses SHA-256 for deduplication

## Security Considerations
- All operations are local (no cloud communication)
- Requires file system permissions
- Hash-based deduplication for accuracy
- Recommended to test on non-critical files first
