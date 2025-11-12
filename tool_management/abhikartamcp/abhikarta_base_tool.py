"""
Abhikarta LLM - Tool Management Framework
Abhikarta Base Tool - MCP Tool Wrapper

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
"""

import asyncio
import logging
from typing import Any, Dict, Optional
import httpx

# Import from the tool management framework
try:
    from tool_management.core.base import BaseTool
    from tool_management.core.types import ToolType, ExecutionMode
    from tool_management.core.parameters import ToolParameter, ParameterType
    from tool_management.core.results import ToolResult, ResultStatus
except ImportError:
    # Fallback for demonstration
    class BaseTool:
        def __init__(self, name, description, tool_type, execution_mode, version="1.0.0"):
            self.name = name
            self.description = description
            self.tool_type = tool_type
            self.execution_mode = execution_mode
            self.version = version
            self._parameters = None
        
        def add_parameter(self, param):
            pass
        
        def execute(self, **kwargs):
            raise NotImplementedError()
    
    class ToolType:
        ABHIKARTAMCP = "abhikartamcp"
    
    class ExecutionMode:
        ASYNC = "async"
    
    class ToolResult:
        @staticmethod
        def success_result(data, tool_name=None):
            return {"status": "success", "data": data}
        
        @staticmethod
        def failure_result(error, error_type, tool_name=None):
            return {"status": "failure", "error": error, "error_type": error_type}


logger = logging.getLogger(__name__)


class AbhikartaBaseTool(BaseTool):
    """
    Base tool class for Abhikarta MCP tools.
    
    This class wraps tools from the Abhikarta MCP server and provides
    seamless integration with the tool management framework.
    
    Features:
    - Automatic tool type (ABHIKARTAMCP)
    - JSON-RPC communication with MCP server
    - Authentication handling
    - Schema-based parameter validation
    - Async execution support
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        mcp_base_url: str,
        mcp_endpoint: str = "/mcp",
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        auth_token: Optional[str] = None,
        timeout: float = 30.0,
        version: str = "1.0.0"
    ):
        """
        Initialize an Abhikarta MCP tool.
        
        Args:
            name: Tool name (should include :abhikartamcp suffix)
            description: Tool description
            mcp_base_url: Base URL of the MCP server
            mcp_endpoint: MCP JSON-RPC endpoint path
            input_schema: JSON schema for input parameters
            output_schema: JSON schema for output
            auth_token: Optional authentication token
            timeout: HTTP request timeout in seconds
            version: Tool version
        """
        # Extract original tool name (remove suffix)
        self.original_tool_name = name
        if name.endswith(":abhikartamcp"):
            self.original_tool_name = name[:-13]  # Remove ":abhikartamcp" (13 chars)
        
        # Initialize base tool with ABHIKARTAMCP type
        super().__init__(
            name=name,
            description=description,
            tool_type=ToolType.ABHIKARTAMCP,
            execution_mode=ExecutionMode.ASYNC,
            version=version
        )
        
        # MCP configuration
        self.mcp_base_url = mcp_base_url
        self.mcp_endpoint = mcp_endpoint
        self.mcp_url = f"{mcp_base_url}{mcp_endpoint}"
        self.auth_token = auth_token
        self.timeout = timeout
        
        # Schema information
        self.input_schema = input_schema or {}
        self.output_schema = output_schema or {}
        
        # HTTP client (lazy initialization)
        self._http_client: Optional[httpx.AsyncClient] = None
        self._request_id = 0
        
        # Parse input schema to create parameters
        if input_schema and "properties" in input_schema:
            self._parse_input_schema(input_schema)
        
        logger.debug(f"Initialized AbhikartaBaseTool: {name}")
    
    def _next_id(self) -> int:
        """Generate next request ID"""
        self._request_id += 1
        return self._request_id
    
    async def _ensure_http_client(self):
        """Ensure HTTP client is initialized"""
        if self._http_client is None:
            headers = {"Content-Type": "application/json"}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            self._http_client = httpx.AsyncClient(
                timeout=self.timeout,
                headers=headers
            )
    
    def _parse_input_schema(self, schema: Dict[str, Any]):
        """
        Parse JSON schema and create ToolParameters.
        
        Args:
            schema: JSON schema for input parameters
        """
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        for param_name, param_def in properties.items():
            # Determine parameter type
            param_type = param_def.get("type", "string")
            
            # Create parameter
            try:
                param = ToolParameter(
                    name=param_name,
                    param_type=param_type,
                    description=param_def.get("description", ""),
                    required=param_name in required
                )
                
                # Add constraints
                if "enum" in param_def:
                    param.enum = param_def["enum"]
                if "default" in param_def:
                    param.default = param_def["default"]
                if "minimum" in param_def:
                    param.minimum = param_def["minimum"]
                if "maximum" in param_def:
                    param.maximum = param_def["maximum"]
                if "minLength" in param_def:
                    param.min_length = param_def["minLength"]
                if "maxLength" in param_def:
                    param.max_length = param_def["maxLength"]
                if "pattern" in param_def:
                    param.pattern = param_def["pattern"]
                
                self.add_parameter(param)
                
            except Exception as e:
                logger.warning(
                    f"Failed to create parameter '{param_name}' for tool '{self.name}': {e}"
                )
    
    def set_auth_token(self, token: str):
        """
        Update the authentication token.
        
        Args:
            token: New authentication token
        """
        self.auth_token = token
        
        # Update HTTP client headers if already initialized
        if self._http_client is not None:
            self._http_client.headers["Authorization"] = f"Bearer {token}"
    
    async def _send_mcp_request(
        self,
        method: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send a JSON-RPC request to the MCP server.
        
        Args:
            method: JSON-RPC method name
            params: Method parameters
            
        Returns:
            Response result
            
        Raises:
            Exception: If request fails
        """
        await self._ensure_http_client()
        
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params
        }
        
        try:
            response = await self._http_client.post(
                self.mcp_url,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Check for JSON-RPC errors
            if "error" in data:
                error = data["error"]
                raise Exception(
                    f"MCP Error {error.get('code', 'unknown')}: "
                    f"{error.get('message', 'Unknown error')}"
                )
            
            return data.get("result", {})
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error in MCP request: {e}")
            raise
        except Exception as e:
            logger.error(f"MCP request failed: {e}")
            raise
    
    async def ping(self) -> bool:
        """
        Ping the MCP server to check connectivity.
        
        Returns:
            True if server is responsive
        """
        try:
            result = await self._send_mcp_request("ping", {})
            return result.get("status") == "ok"
        except Exception as e:
            logger.warning(f"Ping failed for tool '{self.name}': {e}")
            return False
    
    def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool synchronously.
        
        This wraps the async execution in a synchronous context.
        
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
        Execute the tool asynchronously.
        
        This sends a tools/call request to the MCP server with the
        original tool name (without suffix).
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            ToolResult with execution results
        """
        try:
            # Call the MCP server's tools/call endpoint
            result = await self._send_mcp_request(
                method="tools/call",
                params={
                    "name": self.original_tool_name,
                    "arguments": kwargs
                }
            )
            
            # Extract content from MCP response
            content = result.get("content", [])
            
            # Process content based on type
            result_data = []
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        result_data.append(item.get("text", ""))
                    elif item.get("type") == "image":
                        result_data.append({
                            "type": "image",
                            "data": item.get("data", "")
                        })
                    else:
                        result_data.append(item)
                else:
                    result_data.append(str(item))
            
            # Create success result
            if len(result_data) == 1 and isinstance(result_data[0], str):
                output = result_data[0]
            else:
                output = result_data
            
            return ToolResult.success_result(
                data=output,
                tool_name=self.name
            )
            
        except Exception as e:
            logger.error(f"Error executing tool '{self.name}': {e}", exc_info=True)
            return ToolResult.failure_result(
                error=str(e),
                error_type=type(e).__name__,
                tool_name=self.name
            )
    
    async def cleanup(self):
        """Cleanup resources"""
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None
    
    def __del__(self):
        """Cleanup on deletion"""
        if self._http_client is not None:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.cleanup())
                else:
                    loop.run_until_complete(self.cleanup())
            except Exception:
                pass
    
    def __repr__(self) -> str:
        return (
            f"<AbhikartaBaseTool name='{self.name}' "
            f"original='{self.original_tool_name}' "
            f"type={self.tool_type}>"
        )
