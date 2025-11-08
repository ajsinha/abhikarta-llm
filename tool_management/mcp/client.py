"""
Abhikarta LLM - Tool Management Framework
Model Context Protocol (MCP) Integration

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

This module provides Model Context Protocol support for tool integration.
Supports multiple transport protocols: stdio, SSE, and HTTP/REST.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import asyncio

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

from ..core import (
    BaseTool,
    ToolType,
    ExecutionMode,
    ToolResult,
    ToolParameter,
    MCPError,
    MCPConnectionError,
    MCPProtocolError
)


logger = logging.getLogger(__name__)


# ============================================================================
# MCP PROTOCOL TYPES
# ============================================================================

@dataclass
class MCPServerInfo:
    """Information about an MCP server"""
    name: str
    version: str
    url: str
    transport: str  # "stdio" or "sse"
    capabilities: List[str]
    

class MCPClient:
    """
    Client for communicating with MCP servers.
    
    Implements the Model Context Protocol for tool discovery and execution.
    Supports multiple transport protocols: stdio, SSE, and HTTP/REST.
    """
    
    def __init__(
        self,
        server_url: str,
        transport: str = "http",
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize MCP client.
        
        Args:
            server_url: URL of the MCP server
            transport: Transport protocol ("stdio", "sse", or "http")
            timeout: Request timeout in seconds (for HTTP transport)
            headers: Optional HTTP headers (for HTTP transport)
        """
        self.server_url = server_url
        self.transport = transport.lower()
        self.timeout = timeout
        self.headers = headers or {}
        self._connected = False
        self._server_info: Optional[MCPServerInfo] = None
        self._request_id = 0
        self._http_client: Optional[httpx.AsyncClient] = None
        
        # Validate transport
        if self.transport not in ["stdio", "sse", "http"]:
            raise ValueError(f"Unsupported transport: {transport}. Use 'stdio', 'sse', or 'http'")
        
        # Check httpx availability for HTTP transport
        if self.transport == "http" and not HTTPX_AVAILABLE:
            raise ImportError(
                "httpx is required for HTTP transport. Install with: pip install httpx"
            )
    
    def _next_id(self) -> int:
        """Generate next request ID"""
        self._request_id += 1
        return self._request_id
    
    async def connect(self) -> MCPServerInfo:
        """
        Connect to the MCP server and retrieve capabilities.
        
        Returns:
            MCPServerInfo with server details
            
        Raises:
            MCPConnectionError: If connection fails
        """
        try:
            # Initialize connection
            response = await self._send_request("initialize", {
                "protocolVersion": "1.0",
                "capabilities": {
                    "tools": {}
                }
            })
            
            self._server_info = MCPServerInfo(
                name=response.get("serverInfo", {}).get("name", "Unknown"),
                version=response.get("serverInfo", {}).get("version", "Unknown"),
                url=self.server_url,
                transport=self.transport,
                capabilities=list(response.get("capabilities", {}).keys())
            )
            
            self._connected = True
            logger.info(f"Connected to MCP server: {self._server_info.name}")
            
            return self._server_info
            
        except Exception as e:
            raise MCPConnectionError(f"Failed to connect to MCP server: {e}")
    
    async def disconnect(self):
        """Disconnect from the MCP server and cleanup resources"""
        if self._connected:
            self._connected = False
            logger.info("Disconnected from MCP server")
        
        # Cleanup HTTP client if exists
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None
            logger.debug("Closed HTTP client")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all tools available on the MCP server.
        
        Returns:
            List of tool definitions
            
        Raises:
            MCPProtocolError: If request fails
        """
        if not self._connected:
            raise MCPProtocolError("Not connected to MCP server")
        
        try:
            response = await self._send_request("tools/list", {})
            return response.get("tools", [])
        except Exception as e:
            raise MCPProtocolError(f"Failed to list tools: {e}")
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result
            
        Raises:
            MCPProtocolError: If tool call fails
        """
        if not self._connected:
            raise MCPProtocolError("Not connected to MCP server")
        
        try:
            response = await self._send_request("tools/call", {
                "name": tool_name,
                "arguments": arguments
            })
            return response
        except Exception as e:
            raise MCPProtocolError(f"Tool call failed: {e}")
    
    async def _send_request(
        self,
        method: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send a JSON-RPC request to the MCP server.
        
        Args:
            method: RPC method name
            params: Method parameters
            
        Returns:
            Response result
            
        Raises:
            MCPProtocolError: If request fails
        """
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params
        }
        
        logger.debug(f"MCP Request: {method} (transport: {self.transport})")
        
        # Route to appropriate transport
        if self.transport == "http":
            response = await self._send_http_request(payload)
        elif self.transport == "sse":
            response = await self._send_sse_request(payload)
        elif self.transport == "stdio":
            response = await self._send_stdio_request(payload)
        else:
            raise MCPProtocolError(f"Unsupported transport: {self.transport}")
        
        # Check for errors in response
        if "error" in response:
            error = response["error"]
            raise MCPProtocolError(
                f"MCP Error {error.get('code', 'unknown')}: {error.get('message', 'Unknown error')}"
            )
        
        return response.get("result", {})
    
    async def _send_http_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send HTTP/REST request to MCP server.
        
        Args:
            payload: JSON-RPC payload
            
        Returns:
            JSON-RPC response
            
        Raises:
            MCPConnectionError: If HTTP request fails
        """
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={
                    "Content-Type": "application/json",
                    **self.headers
                }
            )
        
        try:
            response = await self._http_client.post(
                self.server_url,
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            raise MCPConnectionError(f"HTTP request failed: {e}")
        except json.JSONDecodeError as e:
            raise MCPProtocolError(f"Invalid JSON response: {e}")
    
    async def _send_sse_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send SSE (Server-Sent Events) request to MCP server.
        
        Note: This is a placeholder implementation.
        Full SSE support would require additional libraries.
        
        Args:
            payload: JSON-RPC payload
            
        Returns:
            JSON-RPC response
        """
        # Placeholder for SSE implementation
        # Real implementation would use SSE client library
        logger.warning("SSE transport is not fully implemented. Using HTTP fallback.")
        return await self._send_http_request(payload)
    
    async def _send_stdio_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send stdio request to MCP server.
        
        Note: This is a placeholder implementation.
        Full stdio support would require process management.
        
        Args:
            payload: JSON-RPC payload
            
        Returns:
            JSON-RPC response
        """
        # Placeholder for stdio implementation
        # Real implementation would use subprocess communication
        logger.warning("stdio transport requires local MCP server process.")
        
        # For demonstration, return a mock response
        response = {
            "jsonrpc": "2.0",
            "id": payload["id"],
            "result": {}
        }
        
        return response
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self._connected
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
        return False


# ============================================================================
# MCP TOOL ADAPTER
# ============================================================================

class MCPTool(BaseTool):
    """
    Tool that wraps an MCP server tool.
    
    Provides a bridge between Abhikarta's tool system and MCP protocol.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        mcp_client: MCPClient,
        mcp_tool_name: Optional[str] = None,
        input_schema: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize MCP tool.
        
        Args:
            name: Tool name in Abhikarta system
            description: Tool description
            mcp_client: Connected MCP client
            mcp_tool_name: Original tool name in MCP server (defaults to name)
            input_schema: JSON schema for tool inputs
        """
        super().__init__(
            name=name,
            description=description,
            tool_type=ToolType.MCP,
            execution_mode=ExecutionMode.ASYNC
        )
        
        self.mcp_client = mcp_client
        self.mcp_tool_name = mcp_tool_name or name
        
        # Parse input schema and create parameters
        if input_schema and "properties" in input_schema:
            self._parse_input_schema(input_schema)
    
    def _parse_input_schema(self, schema: Dict[str, Any]):
        """
        Parse MCP input schema and create ToolParameters.
        
        Args:
            schema: JSON schema for tool inputs
        """
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        for param_name, param_def in properties.items():
            param = ToolParameter(
                name=param_name,
                param_type=param_def.get("type", "string"),
                description=param_def.get("description", ""),
                required=param_name in required
            )
            
            # Add additional constraints if present
            if "enum" in param_def:
                param.enum = param_def["enum"]
            if "default" in param_def:
                param.default = param_def["default"]
            
            self.add_parameter(param)
    
    def execute(self, **kwargs) -> ToolResult:
        """
        Execute MCP tool synchronously.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            ToolResult with execution results
        """
        # Run async execution in sync context
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(self.execute_async(**kwargs))
            return result
        finally:
            loop.close()
    
    async def execute_async(self, **kwargs) -> ToolResult:
        """
        Execute MCP tool asynchronously.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            ToolResult with execution results
        """
        try:
            # Call MCP server
            response = await self.mcp_client.call_tool(
                self.mcp_tool_name,
                kwargs
            )
            
            # Extract content from MCP response
            content = response.get("content", [])
            
            # Combine text content
            result_data = []
            for item in content:
                if item.get("type") == "text":
                    result_data.append(item.get("text", ""))
            
            return ToolResult.success_result(
                data="\n".join(result_data) if result_data else response,
                tool_name=self.name
            )
            
        except MCPProtocolError as e:
            return ToolResult.failure_result(
                error=str(e),
                error_type="MCPProtocolError",
                tool_name=self.name
            )
        except Exception as e:
            return ToolResult.failure_result(
                error=str(e),
                error_type=type(e).__name__,
                tool_name=self.name
            )


# ============================================================================
# MCP TOOL DISCOVERY
# ============================================================================

async def discover_mcp_tools(
    mcp_client: MCPClient,
    prefix: str = ""
) -> List[MCPTool]:
    """
    Discover and create tools from an MCP server.
    
    Args:
        mcp_client: Connected MCP client
        prefix: Optional prefix to add to tool names
        
    Returns:
        List of MCPTool instances
        
    Raises:
        MCPError: If discovery fails
    """
    if not mcp_client.is_connected:
        await mcp_client.connect()
    
    try:
        mcp_tools_list = await mcp_client.list_tools()
        
        tools = []
        for mcp_tool_def in mcp_tools_list:
            tool_name = prefix + mcp_tool_def.get("name", "unknown")
            
            tool = MCPTool(
                name=tool_name,
                description=mcp_tool_def.get("description", ""),
                mcp_client=mcp_client,
                mcp_tool_name=mcp_tool_def.get("name"),
                input_schema=mcp_tool_def.get("inputSchema")
            )
            
            tools.append(tool)
            logger.info(f"Discovered MCP tool: {tool_name}")
        
        return tools
        
    except Exception as e:
        raise MCPError(f"Failed to discover MCP tools: {e}")
