"""
Abhikarta MCP Module - Model Context Protocol integration.

This module provides:
- MCP server configuration and state management
- HTTP and WebSocket clients for MCP communication
- Centralized MCPServerManager for server lifecycle
- Automatic tool discovery and registration

Version: 1.2.5
Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

# Server models
from .server import (
    MCPServer,
    MCPServerConfig,
    MCPServerState,
    MCPServerStatus,
    MCPTransportType,
    MCPAuthType,
    MCPToolDefinition
)

# Clients
from .client import (
    MCPClientBase,
    HTTPMCPClient,
    WebSocketMCPClient,
    create_mcp_client
)

# Manager
from .manager import (
    MCPServerManager,
    get_mcp_manager
)

__all__ = [
    # Server
    'MCPServer',
    'MCPServerConfig',
    'MCPServerState',
    'MCPServerStatus',
    'MCPTransportType',
    'MCPAuthType',
    'MCPToolDefinition',
    
    # Clients
    'MCPClientBase',
    'HTTPMCPClient',
    'WebSocketMCPClient',
    'create_mcp_client',
    
    # Manager
    'MCPServerManager',
    'get_mcp_manager',
]

__version__ = '1.2.5'
