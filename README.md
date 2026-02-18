# 📥 Downloads Warden MCP

Professional MCP server for intelligent Downloads folder management using FastMCP and Python 3.10+.

## 🎯 Overview

Downloads Warden is a Model Context Protocol (MCP) server that transforms your Downloads folder from chaos into an organized, efficient system. By connecting to Claude through MCP, the AI agent can automatically manage your files with intelligent operations.

## ✨ Features

### 6 Powerful Tools

| Tool | Description | Type |
|------|-------------|------|
| **scan_downloads** | Analyze folder structure and statistics | Read-only |
| **smart_sort_files** | Organize files into intelligent categories | Write |
| **deduplicate_by_hash** | Find and remove exact duplicates | Write |
| **auto_extract_and_cleanup** | Extract ZIP files automatically | Write |
| **clear_installers** | Remove old installation files | Write |
| **find_large_files** | Identify space-hogging files | Read-only |

### Smart Organization

Automatically sorts files into categories:
- 📄 **documents** - PDF, DOCX, TXT, XLSX, PPTX
- 🎬 **media** - JPG, PNG, MP4, MP3, GIF
- 🔧 **installers** - EXE, MSI, DMG, PKG
- 💻 **code** - PY, JS, TS, HTML, CSS, JSON
- 📦 **archives** - ZIP, RAR, 7Z, TAR, GZ
- 📂 **other** - Miscellaneous files

## 📋 Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- Claude Desktop with MCP support

## 🚀 Installation & Setup

### 1. Clone/Create the Project
```bash
# Navigate to your projects directory
cd ~/projects

# Create project directory
mkdir downloads-warden
cd downloads-warden
```

### 2. Install Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip or uv package manager
- Claude Desktop (for testing)

### Installation

```bash
# Clone or navigate to project
cd downloads-warden

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Run the Server

```bash
# Direct run
python src/server.py

# Or with uv (if installed)
uv run src/server.py
```

## 🧪 Testing

### Unit Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src
```

**Test Results:** ✅ 13/13 tests passing

### With MCP Inspector

```bash
mcp-inspector python src/server.py
```

Open http://localhost:3000 for interactive tool testing.

## 💡 Usage Examples

Once configured, you can chat with Claude naturally:

**Example 1: Full Analysis**
> "קלאוד, תנתח את תיקיית ההורדות שלי ותגיד לי איך אני יכול לחסוך מקום"

Claude will:
1. Run `scan_downloads` to get statistics
2. Run `deduplicate_by_hash` to find duplicates
3. Run `find_large_files` to identify space hogs
4. Provide recommendations

**Example 2: Quick Cleanup**
> "תנקה לי את התיקייה - תמיין, תחלץ זיפים, ותמחק כפילויות"

Claude will:
1. Run `smart_sort_files`
2. Run `auto_extract_and_cleanup`
3. Run `deduplicate_by_hash`
4. Report progress

**Example 3: Space Management**
> "כמה מקום אני יכול לחסוך?"

Claude will:
1. Run `find_large_files`
2. Run `deduplicate_by_hash`
3. Run `clear_installers`
4. Calculate potential savings

## 🏗 Project Structure

```
downloads-warden/
├── src/
│   └── server.py           # Main MCP server implementation
├── .vscode/
│   └── mcp.json            # MCP server configuration
├── pyproject.toml          # Project metadata
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 Development

### Run in Development Mode

```bash
# With virtual environment activated
python src/server.py
```

### Test Tools Locally

```python
# Example Python script to test a tool
import asyncio
from src.server import handle_scan_downloads

async def test():
    result = await handle_scan_downloads(os.path.expanduser("~/Downloads"))
    print(result)

asyncio.run(test())
```

## 📝 API Reference

### Tool: scan_downloads
- **Input:** None
- **Output:** Report with file statistics
- **Side Effects:** None (read-only)

### Tool: smart_sort_files
- **Input:** None
- **Output:** Summary of moved files
- **Side Effects:** Modifies folder structure

### Tool: deduplicate_by_hash
- **Input:** None
- **Output:** Number of deleted duplicates
- **Side Effects:** Removes files

### Tool: auto_extract_and_cleanup
- **Input:** None
- **Output:** Number of extracted files
- **Side Effects:** Creates directories, removes archives

### Tool: clear_installers
- **Input:** None
- **Output:** Number of deleted installers
- **Side Effects:** Removes old installer files

### Tool: find_large_files
- **Input:** `min_size_mb` (number, default: 500)
- **Output:** List of large files
- **Side Effects:** None (read-only)

## ⚠️ Important Notes

- **Backups:** Always backup important files before using cleanup tools
- **Permissions:** Requires read/write access to Downloads folder
- **Privacy:** All operations run locally on your machine
- **Safety:** Duplicate files are verified before deletion
- **Testing:** Test on non-critical files first

## 🔐 Privacy & Security

- No data is sent to external servers
- All operations occur locally on your machine
- Files are only deleted after verification
- Hash-based deduplication ensures accuracy

## 🐛 Troubleshooting

### Server doesn't start
```bash
# Check Python version
python --version  # Should be 3.10+

# Verify MCP is installed
pip list | grep mcp

# Try running directly
python src/server.py
```

### Claude doesn't see the tool
- Restart Claude Desktop
- Check claude_desktop_config.json syntax
- Verify file paths in config are correct
- Check virtual environment is active

### Permission denied errors
- Run with appropriate permissions
- Check file/folder ownership
- On Windows, may need admin privileges

## 📚 References

- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [Python pathlib Documentation](https://docs.python.org/3/library/pathlib.html)
- [Async/Await in Python](https://docs.python.org/3/library/asyncio.html)

## 📄 License

MIT License - Feel free to use and modify for your needs

## 🤝 Contributing

Contributions welcome! Please feel free to submit pull requests or open issues.

---

**Made with ❤️ for organized Downloads folders everywhere**
