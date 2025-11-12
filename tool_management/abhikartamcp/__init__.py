"""
Abhikarta LLM - Tool Management Framework
AbhikartaMCP Module - MCP Server Integration

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This document and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use of this document or the software
system it describes is strictly prohibited without explicit written permission from the
copyright holder. This document is provided "as is" without warranty of any kind, either
expressed or implied. The copyright holder shall not be liable for any damages arising
from the use of this document or the software system it describes.

Patent Pending: Certain architectural patterns and implementations described in this
document may be subject to patent applications.

This module provides seamless integration between the Abhikarta Tool Management
Framework and Abhikarta MCP servers using the Model Context Protocol (MCP).

Key Components:
- AbhikartaMCPToolBuilder: Discovers and caches tools from MCP server
- AbhikartaBaseTool: Wraps MCP tools as framework tools
- MCPRegistryIntegration: Manages tool registration
- MCPAutoSync: Automatic synchronization service
"""

__version__ = "1.0.2"
__author__ = "Ashutosh Sinha"
__email__ = "ajsinha@gmail.com"

from .abhikarta_mcp_tool_builder import (
    AbhikartaMCPToolBuilder,
    MCPToolSchema,
    MCPServerConfig
)

from .abhikarta_base_tool import AbhikartaBaseTool

from .registry_integration import (
    MCPRegistryIntegration,
    MCPAutoSync
)

__all__ = [
    "AbhikartaMCPToolBuilder",
    "MCPToolSchema",
    "MCPServerConfig",
    "AbhikartaBaseTool",
    "MCPRegistryIntegration",
    "MCPAutoSync",
]
