# 📥 Downloads Warden — MCP Server

MCP server for intelligent Downloads folder management using FastMCP and Python 3.10+.

---

## 🏗 Architecture

```
src/
├── server.py               # MCP entry point — exposes 7 tools, wires DI in main()
├── interfaces.py           # IDownloadsService — abstract interface
├── exceptions.py           # Custom exceptions hierarchy
├── services/
│   └── downloads_service.py  # Business logic — implements IDownloadsService
├── models/
│   ├── file_info.py          # FileInfo dataclass
│   ├── scan_result.py        # ScanResult, CategoryStats dataclasses
│   └── operation_result.py   # OperationResult, LargeFilesResult dataclasses
└── utils/
    └── file_utils.py         # get_file_category, calculate_file_hash, get_file_size_mb

tests/
├── test_downloads_service.py  # Unit tests for DownloadsService
├── test_server.py             # Unit tests for MCP tools (mock injection via DI)
└── test_utils.py              # Unit tests for utility functions
```

---

## ✨ Tools

| Tool | Description | Type |
|------|-------------|------|
| `scan_downloads` | Analyze folder structure and statistics | Read |
| `smart_sort_files` | Organize files into category folders | Write |
| `deduplicate_by_hash` | Remove exact duplicate files (SHA-256) | Write |
| `deduplicate_folders` | Remove duplicate folders by content hash | Write |
| `auto_extract_and_cleanup` | Extract ZIP files and remove archives | Write |
| `clear_installers` | Remove installer files older than 7 days | Write |
| `find_large_files` | Find files above a size threshold (default 500MB) | Read |

---

## 🚀 Quick Start

### Local

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python src/server.py
```

### Docker

```bash
docker build -t downloads-warden .
docker run --rm -v ~/Downloads:/root/Downloads downloads-warden
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=term-missing
```

**46 tests — all passing.**

---

## 🔧 Code Quality

```bash
# Lint
ruff check src/

# Type check
mypy src/
```

---

## 🧩 Dependency Injection

The server uses constructor injection. `main()` is the single composition root:

```python
def main() -> None:
    service = DownloadsService(get_downloads_path())
    create_server(service=service)
    mcp.run(transport="stdio")
```

In tests, a mock is injected directly:

```python
mock_service = MagicMock(spec=IDownloadsService)
create_server(service=mock_service)
```

---

## 📦 Models

| Model | Fields |
|-------|--------|
| `FileInfo` | `name`, `size_mb` |
| `CategoryStats` | `count`, `size_mb` |
| `ScanResult` | `success`, `message`, `total_files`, `total_size_mb`, `by_category`, `by_extension` |
| `OperationResult` | `success`, `message`, `count`, `errors` |
| `LargeFilesResult` | inherits `OperationResult` + `files`, `total_size_mb` |

---

## ⚠️ Exceptions

```
DownloadsWardenError
├── PathNotFoundError
├── FileMoveError
├── HashCalculationError
├── ExtractionError
├── InstallerCleanupError
└── FolderDeletionError
```

---

## ⚙️ Claude Desktop Setup

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "downloads-warden": {
      "command": "python",
      "args": ["C:/path/to/src/server.py"]
    }
  }
}
```

---

## 🔐 Privacy

All operations run **locally**. No data is sent to external servers.
