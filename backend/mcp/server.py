"""MCP Server for Todo task tools."""

from mcp.server import Server
from mcp.types import Tool


class MCPServer:
    """MCP Server that exposes task management tools."""

    def __init__(self):
        self.server = Server("todo-mcp-server")
        self._register_tools()

    def _register_tools(self):
        """Register all available tools with the MCP server."""
        # Tools will be registered by the tools module
        pass

    def get_tools(self) -> list[Tool]:
        """Get list of available tools."""
        # This will be populated by the tools module
        return []

    def start(self):
        """Start the MCP server."""
        # Server startup logic
        pass
