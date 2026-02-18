# 🧪 Testing Downloads Warden MCP

## Using MCP Inspector

The MCP Inspector is a tool to test and debug your MCP server.

### Start Inspector
```bash
mcp-inspector python "c:\Users\330580861\Desktop\ריקי ורבקה\downloads-warden\src\server.py"
```

Or if you're in the project directory:
```bash
mcp-inspector python src/server.py
```

This will open a web interface where you can:
1. See all available tools
2. Call each tool with parameters
3. View responses in real-time
4. Debug any issues

### Testing Tools

#### 1. scan_downloads
No parameters needed. Returns folder statistics.

#### 2. smart_sort_files
No parameters needed. Sorts files into categories.

#### 3. deduplicate_by_hash
No parameters needed. Removes duplicate files.

#### 4. auto_extract_and_cleanup
No parameters needed. Extracts ZIP files.

#### 5. clear_installers
No parameters needed. Removes old installers (>7 days).

#### 6. find_large_files
Parameter: `min_size_mb` (number, default: 500)

## Verification Checklist

- [ ] All 6 tools appear in Inspector
- [ ] scan_downloads returns folder stats
- [ ] Tools can be called without errors
- [ ] Response format is valid
- [ ] Integration with Claude Desktop works

## Next Steps

1. Use Inspector to test each tool
2. Verify with Claude Desktop
3. Test natural language queries in Claude
