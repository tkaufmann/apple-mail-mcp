"""
ABOUTME: Central MCP server instance
Provides a single FastMCP instance used by all tool modules.
"""

from mcp.server.fastmcp import FastMCP

# Create single MCP server instance used by all tool modules
mcp = FastMCP("Apple Mail MCP")
