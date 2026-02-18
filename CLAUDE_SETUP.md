# 🚀 Claude Desktop Integration

## ✅ Setup Instructions

### 1. Locate Claude Desktop Config File

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

Which expands to:
```
C:\Users\<YourUsername>\AppData\Roaming\Claude\claude_desktop_config.json
```

### 2. Add Downloads Warden Server

Copy the contents from `claude_desktop_config.json` in this project and merge with your existing config:

```json
{
  "mcpServers": {
    "downloads-warden": {
      "command": "python",
      "args": [
        "C:\\Users\\330580861\\Desktop\\ריקי ורבקה\\downloads-warden\\src\\server.py"
      ],
      "env": {
        "PYTHONPATH": "C:\\Users\\330580861\\Desktop\\ריקי ורבקה\\downloads-warden"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

- Close Claude Desktop completely
- Wait 5 seconds
- Reopen Claude Desktop
- The server will automatically load

### 4. Test Connection

In Claude, ask:
```
What tools are available to me?
```

You should see "downloads-warden" listed with 6 tools:
1. scan_downloads
2. smart_sort_files
3. deduplicate_by_hash
4. auto_extract_and_cleanup
5. clear_installers
6. find_large_files

### 5. Use the Tools

Natural language examples:
```
"מה המצב בתיקיית ההורדות שלי?"
```

English examples:
```
"Organize my Downloads folder"
"How much space can I save?"
"Show me large files"
"Remove duplicates"
```

---

## 🔍 Troubleshooting

### Server Not Connecting

**Check 1: Python Path**
Make sure Python is installed and accessible:
```bash
python --version
```

**Check 2: MCP Installation**
Verify MCP SDK is installed:
```bash
python -c "import mcp; print(mcp.__version__)"
```

**Check 3: Server Syntax**
Test the server directly:
```bash
cd "C:\Users\330580861\Desktop\ריקי ורבקה\downloads-warden"
python src/server.py
```
(It will wait for input - Ctrl+C to exit)

**Check 4: Config JSON**
Validate JSON syntax:
- Use VS Code JSON validator
- Check for matching quotes
- Ensure paths use double backslashes

### Tools Not Showing

1. Restart Claude Desktop
2. Check the config file exists
3. Verify paths are correct
4. Check file permissions

### Permission Denied

On Windows, you may need to:
- Run Claude Desktop as Administrator
- Or grant folder permissions to your user account

---

## 📊 Testing Workflow

### Method 1: MCP Inspector (Recommended)
```bash
cd "C:\Users\330580861\Desktop\ריקי ורבקה\downloads-warden"
mcp-inspector python src/server.py
```
Then visit: http://localhost:3000

### Method 2: Claude Desktop
1. Open Claude Desktop
2. Ask: "What tools do I have?"
3. Test each tool with natural language

### Method 3: Command Line
```bash
# Test syntax
python -m py_compile src/server.py

# List tools (using inspector or Claude)
# Each tool has clear error messages
```

---

## 📚 Reference

- [MCP Documentation](https://modelcontextprotocol.io)
- [Claude Desktop Config](https://claude.ai/docs)
- [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)

---

## ✨ Features

Once configured, you can:

✅ **Read-only Operations**
- Scan Downloads folder
- Find large files
- Detect duplicates

✅ **Write Operations**
- Sort files automatically
- Remove duplicates safely
- Clean up old installers
- Extract archives

✅ **Natural Language**
- Ask in Hebrew or English
- Full context support
- Smart recommendations

✅ **Safety**
- Hash verification before deletion
- Keeps backups of extracted files
- Age-based checks for installers
- Clear reporting

---

**Status: READY TO USE**

Restart Claude Desktop and start managing your Downloads folder intelligently!
