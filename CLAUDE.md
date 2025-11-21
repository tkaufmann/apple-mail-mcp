# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Apple Mail MCP Server - A FastMCP-based Model Context Protocol server that provides AI assistants with natural language access to Apple Mail on macOS. The server provides 18 powerful email management tools.

**Architecture:**
- **MCP Server** (modular structure): FastMCP server using AppleScript to control Apple Mail
  - Entry point: `main.py`
  - Tools organized in `tools/` directory
  - Utilities in `utils/` directory
- **Distribution**: Packaged as `.mcpb` bundle for easy installation in Claude Desktop

## Key Commands

### Development & Testing
```bash
# Run MCP server directly (for testing)
./venv/bin/python3 main.py

# Or use the wrapper script (recommended)
./start_mcp.sh

# Install dependencies
pip install -r requirements.txt
```

### Building Distributable
```bash
# Build .mcpb bundle for distribution
cd apple-mail-mcpb
./build-mcpb.sh

# Creates: apple-mail-mcp-v{version}.mcpb in parent directory
```

### Installation Commands (for users)
```bash
# Install MCP to Claude Desktop (using wrapper script)
claude mcp add --transport stdio apple-mail -- /bin/bash $(pwd)/start_mcp.sh
```

## Architecture

### Core MCP Server (Modular Architecture)

**Modular architecture using FastMCP framework:**
- Entry point: `main.py` - imports all tool modules and runs the MCP server
- Central instance: `mcp_instance.py` - provides single FastMCP instance
- Tool modules in `tools/` directory - each module contains related tools with `@mcp.tool()` decorators
- Utilities in `utils/` directory - shared helpers like AppleScript execution
- All 18 tools organized by category across tool modules

**Tool Categories:**
1. **Overview & Discovery**: `get_inbox_overview`, `list_accounts`, `list_mailboxes`
2. **Reading & Searching**: `list_inbox_emails`, `get_recent_emails`, `get_email_with_content`, `search_emails`, `get_email_thread`
3. **Composing**: `compose_email`, `reply_to_email`, `forward_email`
4. **Organization**: `move_email`, `update_email_status`
5. **Drafts**: `manage_drafts` (list/create/send/delete)
6. **Attachments**: `list_email_attachments`, `save_email_attachment`
7. **Analytics**: `get_statistics`, `export_emails`
8. **Cleanup**: `manage_trash`

**Key Design Patterns:**
- User preferences loaded from `USER_EMAIL_PREFERENCES` env var
- Safety limits on batch operations (max_moves, max_deletes)
- AppleScript timeout: 120 seconds
- Email parsing via structured text output from AppleScript

### Distribution Package (`.mcpb`)

**Build Process (`apple-mail-mcpb/build-mcpb.sh`):**
1. Copies `manifest.json`, `main.py`, `mcp_instance.py`, `requirements.txt`, `start_mcp.sh`
2. Copies tool modules (`tools/`), utilities (`utils/`), and optional directories (`resources/`, `prompts/`)
3. Generates README.md for bundled installation
4. Creates zip archive with `.mcpb` extension
5. Virtual environment is created on user's machine on first run

**Key Files:**
- `manifest.json`: MCP Bundle metadata (version, tools, user_config schema)
- `start_mcp.sh`: Wrapper script that creates venv and runs server

## Configuration

### User Preferences (Optional)
MCP supports user-configurable email preferences via environment variable:
```json
{
  "env": {
    "USER_EMAIL_PREFERENCES": "Default to BCG account, show max 50 emails, prefer Archive folder"
  }
}
```
These preferences are auto-injected into all tool descriptions.

### Safety Limits
Built-in limits to prevent accidental bulk operations:
- `update_email_status`: max 10 updates (default)
- `manage_trash`: max 5 deletions (default)
- `move_email`: max 1 move (default)

Parameters can override these limits when needed.

## Important Patterns

### AppleScript Execution
All Mail interactions go through `run_applescript(script: str)`:
- Subprocess with 120s timeout
- Text output captured and parsed
- Error handling for timeouts and execution failures

### Email Parsing
Structured text format from AppleScript parsed by `parse_email_list()`:
- Unicode indicators: `✉` (unread), `✓` (read)
- Field prefixes: `From:`, `Date:`, `Preview:`
- Handles multi-line output safely

### Tool Decorator Pattern
```python
@mcp.tool()
@inject_preferences
def tool_name(args) -> str:
    """Tool description"""
    # Implementation
```
The `@inject_preferences` decorator appends user preferences to docstring at runtime.

## Version Management

**Current Version:** Check `apple-mail-mcpb/manifest.json` → `"version"` field

When incrementing version:
1. Update `manifest.json` version
2. Update `CHANGELOG.md` with changes
3. Rebuild `.mcpb` bundle: `cd apple-mail-mcpb && ./build-mcpb.sh`
4. Tag git release: `git tag v{version}`

## Platform Requirements

**macOS-only project** (requires Apple Mail):
- Python 3.7+
- macOS with Mail.app configured
- AppleScript support
- System permissions: Mail.app Control + Mail Data Access

## Testing Approach

No formal test suite. Testing approach:
1. Run server directly: `./venv/bin/python3 main.py` or `./start_mcp.sh`
2. Use MCP inspector or Claude Desktop to test tools
3. Test with various Mail account types (Gmail, Exchange, iCloud)
4. Verify nested mailbox paths work correctly
5. Test safety limits trigger correctly

## Common Development Tasks

### Adding a New Tool
1. Choose appropriate tool module in `tools/` directory (or create new module)
2. Add `@mcp.tool()` decorated function in the tool module
3. Import the new module in `main.py` if creating a new module
4. Write AppleScript logic for Mail.app interaction (use utilities from `utils/`)
5. Add tool metadata to `apple-mail-mcpb/manifest.json` → `"tools"` array
6. Update `CHANGELOG.md`
7. Increment version in `manifest.json`
8. Rebuild bundle

### Debugging AppleScript Issues
- Test AppleScript directly: `osascript -e 'tell application "Mail" to ...'`
- Check Mail.app is running
- Verify permissions in System Settings → Privacy & Security → Automation
- Increase timeout if needed (currently 120s in `run_applescript()`)

## Related Documentation

- **MCP Specification**: https://modelcontextprotocol.io
- **FastMCP Framework**: https://github.com/jlowin/fastmcp
- **Claude Code Skills**: https://docs.claude.com/en/docs/claude-code/skills
- **AppleScript Mail Dictionary**: Check in Script Editor → File → Open Dictionary → Mail
- Account Taquiri Tim hat E-Mail-Adresse tk@taquiri.de, meine Hauptadresse für geschäftliche Zwecke