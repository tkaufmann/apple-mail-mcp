#!/usr/bin/env python3
"""
ABOUTME: Main entry point for Apple Mail MCP Server
Imports all tool modules and runs the unified MCP server.
"""

# Import the central MCP instance
from mcp_instance import mcp

# Import all tool modules to register their tools with the central mcp instance
# The @mcp.tool() decorators in each module automatically register the tools
import tools.inbox_tools
import tools.search_tools
import tools.composition_tools
import tools.organization_tools
import tools.draft_tools
import tools.attachment_tools
import tools.trash_tools
import tools.analytics_tools

if __name__ == "__main__":
    # Run the MCP server with all registered tools
    mcp.run()
