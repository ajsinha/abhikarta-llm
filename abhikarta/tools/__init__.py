"""
Abhikarta Tools Module - Centralized tool management and execution.

This module provides:
- BaseTool abstract class for all tools
- Concrete tool implementations (FunctionTool, MCPTool, HTTPTool, etc.)
- ToolsRegistry for centralized tool management
- Tool format converters for LLM integrations

Version: 1.2.0
Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

# Base classes and types
from .base_tool import (
    BaseTool,
    ToolMetadata,
    ToolSchema,
    ToolParameter,
    ToolResult,
    ToolType,
    ToolCategory
)

# Function-based tools
from .function_tool import (
    FunctionTool,
    AsyncFunctionTool,
    tool,
    async_tool
)

# MCP tools
from .mcp_tool import (
    MCPTool,
    MCPPluginTool
)

# HTTP tools
from .http_tool import (
    HTTPTool,
    HTTPMethod,
    WebhookTool
)

# Code fragment tools
from .code_fragment_tool import (
    CodeFragmentTool,
    PythonExpressionTool
)

# LangChain integration
from .langchain_tool import (
    LangChainToolWrapper,
    AsyncLangChainToolWrapper,
    wrap_langchain_tools,
    create_langchain_tools
)

# Registry
from .registry import (
    ToolsRegistry,
    get_tools_registry
)

__all__ = [
    # Base
    'BaseTool',
    'ToolMetadata',
    'ToolSchema',
    'ToolParameter',
    'ToolResult',
    'ToolType',
    'ToolCategory',
    
    # Function tools
    'FunctionTool',
    'AsyncFunctionTool',
    'tool',
    'async_tool',
    
    # MCP tools
    'MCPTool',
    'MCPPluginTool',
    
    # HTTP tools
    'HTTPTool',
    'HTTPMethod',
    'WebhookTool',
    
    # Code tools
    'CodeFragmentTool',
    'PythonExpressionTool',
    
    # LangChain
    'LangChainToolWrapper',
    'AsyncLangChainToolWrapper',
    'wrap_langchain_tools',
    'create_langchain_tools',
    
    # Registry
    'ToolsRegistry',
    'get_tools_registry',
]

__version__ = '1.2.0'
