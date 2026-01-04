"""
MCP Tool - Tool implementation for Model Context Protocol tools.

Wraps tools from MCP servers as BaseTool instances.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import logging
import uuid
import json
import requests
from typing import Dict, Any, Optional, List

from .base_tool import (
    BaseTool, ToolMetadata, ToolSchema, ToolParameter,
    ToolResult, ToolType, ToolCategory
)

logger = logging.getLogger(__name__)


class MCPTool(BaseTool):
    """
    Tool that wraps an MCP server tool.
    
    Communicates with MCP servers via HTTP to execute tools.
    Automatically handles authentication, retries, and error handling.
    """
    
    def __init__(self, metadata: ToolMetadata, schema: ToolSchema,
                 server_url: str, tool_name: str,
                 call_endpoint: str = "/api/tools/call",
                 auth_token: str = None, auth_header: str = None,
                 timeout: int = 30):
        """
        Initialize MCPTool.
        
        Args:
            metadata: Tool metadata
            schema: Parameter schema
            server_url: Base URL of the MCP server
            tool_name: Name of the tool on the server
            call_endpoint: Endpoint for tool calls
            auth_token: Optional authentication token
            auth_header: Optional auth header name
            timeout: Request timeout in seconds
        """
        super().__init__(metadata)
        self._schema = schema
        self._server_url = server_url.rstrip('/')
        self._tool_name = tool_name
        self._call_endpoint = call_endpoint
        self._auth_token = auth_token
        self._auth_header = auth_header or "Authorization"
        self._timeout = timeout
    
    @property
    def server_url(self) -> str:
        """MCP server URL."""
        return self._server_url
    
    @property
    def server_tool_name(self) -> str:
        """Tool name on the MCP server."""
        return self._tool_name
    
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool via MCP server."""
        import time
        start_time = time.time()
        
        try:
            url = f"{self._server_url}{self._call_endpoint}"
            
            headers = {"Content-Type": "application/json"}
            if self._auth_token:
                headers[self._auth_header] = f"Bearer {self._auth_token}"
            
            payload = {
                "tool": self._tool_name,
                "parameters": kwargs
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self._timeout
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success', True):
                    return ToolResult.success_result(
                        data.get('result', data.get('output', data)),
                        execution_time
                    )
                else:
                    return ToolResult.error_result(
                        data.get('error', 'Tool execution failed'),
                        execution_time
                    )
            else:
                return ToolResult.error_result(
                    f"HTTP {response.status_code}: {response.text}",
                    execution_time
                )
                
        except requests.Timeout:
            execution_time = (time.time() - start_time) * 1000
            return ToolResult.error_result(
                f"Request timed out after {self._timeout}s",
                execution_time
            )
        except requests.RequestException as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"MCPTool {self.name} request error: {e}")
            return ToolResult.error_result(str(e), execution_time)
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"MCPTool {self.name} error: {e}")
            return ToolResult.error_result(str(e), execution_time)
    
    def get_schema(self) -> ToolSchema:
        """Get the parameter schema."""
        return self._schema
    
    def test_connection(self) -> bool:
        """Test connection to the MCP server."""
        try:
            response = requests.get(
                f"{self._server_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    @classmethod
    def from_mcp_tool_definition(cls, tool_def: Dict[str, Any],
                                 server_url: str, server_name: str,
                                 auth_token: str = None,
                                 auth_header: str = None) -> 'MCPTool':
        """
        Create MCPTool from MCP tool definition.
        
        Args:
            tool_def: Tool definition from MCP server
            server_url: Server base URL
            server_name: Server name for identification
            auth_token: Optional auth token
            auth_header: Optional auth header name
            
        Returns:
            MCPTool instance
        """
        tool_name = tool_def.get('name', 'unknown')
        
        # Parse schema
        input_schema = tool_def.get('inputSchema', tool_def.get('input_schema', {}))
        schema = ToolSchema.from_json_schema(input_schema)
        
        # Determine category from tool name/description
        category = cls._infer_category(tool_name, tool_def.get('description', ''))
        
        metadata = ToolMetadata(
            tool_id=f"mcp_{server_name}_{tool_name}_{uuid.uuid4().hex[:8]}",
            name=f"{server_name}_{tool_name}",
            description=tool_def.get('description', f"MCP tool: {tool_name}"),
            tool_type=ToolType.MCP,
            category=category,
            source=f"mcp:{server_name}",
            tags=["mcp", server_name],
            requires_auth=bool(auth_token)
        )
        
        return cls(
            metadata=metadata,
            schema=schema,
            server_url=server_url,
            tool_name=tool_name,
            auth_token=auth_token,
            auth_header=auth_header
        )
    
    @staticmethod
    def _infer_category(name: str, description: str) -> ToolCategory:
        """Infer tool category from name and description."""
        text = f"{name} {description}".lower()
        
        if any(k in text for k in ['search', 'find', 'query', 'lookup']):
            return ToolCategory.SEARCH
        elif any(k in text for k in ['file', 'read', 'write', 'save', 'load']):
            return ToolCategory.FILE
        elif any(k in text for k in ['database', 'sql', 'db', 'table']):
            return ToolCategory.DATABASE
        elif any(k in text for k in ['api', 'http', 'request', 'webhook']):
            return ToolCategory.INTEGRATION
        elif any(k in text for k in ['email', 'slack', 'notify', 'message']):
            return ToolCategory.COMMUNICATION
        elif any(k in text for k in ['ai', 'llm', 'model', 'generate']):
            return ToolCategory.AI
        elif any(k in text for k in ['data', 'transform', 'parse', 'convert']):
            return ToolCategory.DATA
        else:
            return ToolCategory.UTILITY


class MCPPluginTool(MCPTool):
    """
    Tool from an MCP plugin (locally loaded).
    
    Similar to MCPTool but executes locally via plugin.
    """
    
    def __init__(self, metadata: ToolMetadata, schema: ToolSchema,
                 plugin_id: str, tool_name: str, executor: callable):
        """
        Initialize MCPPluginTool.
        
        Args:
            metadata: Tool metadata
            schema: Parameter schema
            plugin_id: Plugin identifier
            tool_name: Tool name in plugin
            executor: Callable to execute the tool
        """
        # Initialize without server URL
        super(MCPTool, self).__init__(metadata)
        self._schema = schema
        self._plugin_id = plugin_id
        self._tool_name = tool_name
        self._executor = executor
    
    @property
    def plugin_id(self) -> str:
        """Plugin identifier."""
        return self._plugin_id
    
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool via plugin executor."""
        import time
        start_time = time.time()
        
        try:
            result = self._executor(self._tool_name, kwargs)
            execution_time = (time.time() - start_time) * 1000
            
            if isinstance(result, dict) and 'error' in result:
                return ToolResult.error_result(result['error'], execution_time)
            
            return ToolResult.success_result(result, execution_time)
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"MCPPluginTool {self.name} error: {e}")
            return ToolResult.error_result(str(e), execution_time)
    
    @classmethod
    def from_plugin_tool(cls, tool_def: Dict[str, Any], plugin_id: str,
                        plugin_name: str, executor: callable) -> 'MCPPluginTool':
        """Create from plugin tool definition."""
        tool_name = tool_def.get('name', 'unknown')
        
        input_schema = tool_def.get('inputSchema', tool_def.get('input_schema', {}))
        schema = ToolSchema.from_json_schema(input_schema)
        
        metadata = ToolMetadata(
            tool_id=f"plugin_{plugin_id}_{tool_name}_{uuid.uuid4().hex[:8]}",
            name=f"{plugin_name}_{tool_name}",
            description=tool_def.get('description', f"Plugin tool: {tool_name}"),
            tool_type=ToolType.PLUGIN,
            category=ToolCategory.UTILITY,
            source=f"plugin:{plugin_id}",
            tags=["plugin", plugin_name]
        )
        
        return cls(
            metadata=metadata,
            schema=schema,
            plugin_id=plugin_id,
            tool_name=tool_name,
            executor=executor
        )
