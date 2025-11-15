"""
Abhikarta LLM - Tool Management Framework
Abhikarta MCP Tool Builder - Dynamic Tool Discovery and Management

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
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx

from tool_management.mcp_server_proxy import MCPServerProxy, MCPToolSchema, MCPServerConfig

logger = logging.getLogger(__name__)

'''
@dataclass
class AbhikartaMCPServerConfig(MCPServerConfig):
    """Configuration for MCP server connection"""
    base_url: str = "http://localhost:3002"
    mcp_endpoint: str = "/mcp"
    login_endpoint: str = "/api/auth/login"
    tool_list_endpoint: str = "/api/tools/list"
    tool_schema_endpoint_template: str = "/api/tools/{tool_name}/schema"
    username: Optional[str] = None
    password: Optional[str] = None
    refresh_interval_seconds: int = 600  # 10 minutes
    timeout_seconds: float = 30.0
    tool_name_suffix: str = ":abhikartamcp"
'''

class AbhikartaMCPServerProxy(MCPServerProxy):
    """
    Singleton class for managing MCP tool discovery and caching.
    
    This builder:
    - Connects to the Abhikarta MCP server
    - Discovers available tools via JSON-RPC calls
    - Retrieves and caches tool schemas
    - Periodically refreshes the tool cache
    - Provides convenience methods for tool access
    
    The builder maintains authentication tokens and handles automatic
    re-authentication when needed.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, config: MCPServerConfig):
        """Singleton pattern implementation"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config: MCPServerConfig):
        """Initialize the builder (only once)"""
        super().__init__(config)
        if self._initialized:
            return
        
        self._initialized = True

        self._auth_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._refresh_task: Optional[asyncio.Task] = None
        self._running = False
        self._http_client: Optional[httpx.AsyncClient] = None
        self._request_id = 0
        
        logger.info("AbhikartaMCPToolBuilder initialized")

    def _next_id(self) -> int:
        """Generate next request ID"""
        self._request_id += 1
        return self._request_id
    
    async def _ensure_http_client(self):
        """Ensure HTTP client is initialized"""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=self._config.timeout_seconds,
                headers={"Content-Type": "application/json"}
            )
    
    async def _authenticate(self) -> bool:
        """
        Authenticate with the MCP server.
        
        Returns:
            True if authentication successful
        """
        if not self._config.username or not self._config.password:
            logger.warning("No credentials configured for authentication")
            return False
        
        await self._ensure_http_client()
        
        try:
            url = f"{self._config.base_url}{self._config.login_endpoint}"
            response = await self._http_client.post(
                url,
                json={
                    "user_id": self._config.username,
                    "password": self._config.password
                }
            )
            response.raise_for_status()
            
            data = response.json()
            self._auth_token = data.get("token")
            
            # Token typically expires in 1 hour, refresh before that
            self._token_expires_at = datetime.now() + timedelta(minutes=50)
            
            logger.info("Successfully authenticated with MCP server")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    async def _ensure_authenticated(self):
        """Ensure we have a valid authentication token"""
        if self._auth_token is None or \
           (self._token_expires_at and datetime.now() >= self._token_expires_at):
            await self._authenticate()
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers if token is available"""
        if self._auth_token:
            return {"Authorization": f"Bearer {self._auth_token}"}
        return {}
    
    async def _send_mcp_request(
        self,
        method: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send a JSON-RPC request to the MCP endpoint.
        
        Args:
            method: JSON-RPC method name
            params: Method parameters
            
        Returns:
            Response result
            
        Raises:
            Exception: If request fails
        """
        await self._ensure_http_client()
        await self._ensure_authenticated()
        
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params
        }
        
        url = f"{self._config.base_url}{self._config.mcp_endpoint}"
        headers = {
            **self._http_client.headers,
            **self._get_auth_headers()
        }
        
        try:
            response = await self._http_client.post(
                url,
                json=payload,
                headers=headers
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
    
    async def _ping_server(self) -> bool:
        """
        Ping the MCP server to check connectivity.
        
        Returns:
            True if server is responsive
        """
        self.set_last_check_time()

        try:
            result = await self._send_mcp_request("ping", {})
            self.set_health_status("OK")
            return result.get("status") == "OK"
        except Exception as e:
            self.set_health_status("error")
            logger.warning(f"Ping failed: {e}")
            return False
    
    async def _list_tools(self) -> List[str]:
        """
        List all available tools from the MCP server.
        
        Returns:
            List of tool names
        """
        try:
            result = await self._send_mcp_request(self._config.tool_list_endpoint, {}) #"tools/list"
            tools = result.get("tools", [])
            
            # Extract tool names
            tool_names = []
            for tool in tools:
                if isinstance(tool, dict):
                    tool_names.append(tool.get("name", ""))
                elif isinstance(tool, str):
                    tool_names.append(tool)
            
            return [name for name in tool_names if name]
            
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return []
    
    async def _get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the schema for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool schema dictionary or None if failed
        """
        try:
            result = await self._send_mcp_request("tool/schema", {"name": tool_name})
            return result
            
        except Exception as e:
            logger.error(f"Failed to get schema for tool '{tool_name}': {e}")
            return None
    
    async def _refresh_tool_cache(self):
        """Refresh the tool cache by querying the MCP server"""
        logger.info("Refreshing tool cache...")
        
        # Check server connectivity
        if not await self._ping_server():
            logger.warning("Server ping failed, skipping cache refresh")
            return
        
        # Get list of available tools
        tool_names = await self._list_tools()
        logger.info(f"Found {len(tool_names)} tools on MCP server")
        
        # Track which tools are still available
        current_tools = set()
        
        # Update cache for each tool
        for tool_name in tool_names:
            # Get schema
            schema = await self._get_tool_schema(tool_name)
            if not schema:
                logger.warning(f"Skipping tool '{tool_name}' - no schema available")
                continue
            
            # Create cache key with suffix
            cache_key = self.tool_cache_key(tool_name)
            current_tools.add(cache_key)
            
            # Extract schemas
            input_schema = schema.get("input_schema", {})
            output_schema = schema.get("output_schema")
            
            # Get description from input schema or use default
            description = input_schema.get("description", f"Tool: {tool_name}")
            
            # Update or create cache entry
            if cache_key in self._tool_cache:
                # Update existing entry
                self._tool_cache[cache_key].input_schema = input_schema
                self._tool_cache[cache_key].output_schema = output_schema
                self._tool_cache[cache_key].last_updated = datetime.now()
                logger.debug(f"Updated cached tool: {cache_key}")
            else:
                # Create new entry
                self._tool_cache[cache_key] = MCPToolSchema(
                    name=cache_key,
                    description=description,
                    input_schema=input_schema,
                    output_schema=output_schema
                )
                logger.info(f"Added new tool to cache: {cache_key}")
        
        # Remove tools that are no longer available
        tools_to_remove = set(self._tool_cache.keys()) - current_tools
        for tool_name in tools_to_remove:
            del self._tool_cache[tool_name]
            logger.info(f"Removed tool from cache: {tool_name}")
        
        logger.info(
            f"Cache refresh complete. Total tools: {len(self._tool_cache)}"
        )
    
    async def _periodic_refresh_loop(self):
        """Background task for periodic cache refresh"""
        logger.info(
            f"Starting periodic refresh (interval: "
            f"{self._config.refresh_interval_seconds}s)"
        )
        
        while self._running:
            try:
                await self._refresh_tool_cache()
            except Exception as e:
                logger.error(f"Error in periodic refresh: {e}", exc_info=True)
            
            # Wait for next refresh
            await asyncio.sleep(self._config.refresh_interval_seconds)
        
        logger.info("Periodic refresh loop stopped")
    
    async def start(self):
        """
        Start the builder and begin periodic tool discovery.
        
        This will:
        1. Authenticate with the MCP server
        2. Perform initial tool discovery
        3. Start periodic refresh background task
        """
        if self._running:
            logger.warning("Builder already running")
            return
        
        logger.info("Starting AbhikartaMCPToolBuilder...")
        
        # Authenticate
        if self._config.username and self._config.password:
            await self._authenticate()
        
        # Initial cache refresh
        await self._refresh_tool_cache()
        
        # Start periodic refresh
        self._running = True
        self._refresh_task = asyncio.create_task(self._periodic_refresh_loop())
        
        logger.info("Builder started successfully")
    
    async def stop(self):
        """Stop the builder and cleanup resources"""
        if not self._running:
            return
        
        logger.info("Stopping AbhikartaMCPToolBuilder...")
        
        self._running = False
        
        # Cancel refresh task
        if self._refresh_task:
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except asyncio.CancelledError:
                pass
            self._refresh_task = None
        
        # Close HTTP client
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
        
        logger.info("Builder stopped")
    
    def get_tool_schema(self, tool_name: str) -> Optional[MCPToolSchema]:
        """
        Get cached schema for a tool.
        
        Args:
            tool_name: Name of the tool (with or without suffix)
            
        Returns:
            MCPToolSchema or None if not found
        """
        # Try with suffix
        if not tool_name.endswith(self._config.tool_name_suffix):
            tool_name = self.tool_cache_key(tool_name)
        
        return self._tool_cache.get(tool_name)
    
    def list_cached_tools(self) -> List[str]:
        """
        Get list of all cached tool names.
        
        Returns:
            List of tool names
        """
        return list(self._tool_cache.keys())
    
    def get_all_schemas(self) -> Dict[str, MCPToolSchema]:
        """
        Get all cached tool schemas.
        
        Returns:
            Dictionary mapping tool names to schemas
        """
        return self._tool_cache.copy()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the tool cache.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            "total_tools": len(self._tool_cache),
            "tool_names": self.list_cached_tools(),
            "running": self._running,
            "authenticated": self._auth_token is not None,
            "refresh_interval_seconds": self._config.refresh_interval_seconds,
            "last_refresh": max(
                (schema.last_updated for schema in self._tool_cache.values()),
                default=None
            )
        }
    
    async def force_refresh(self):
        """Force an immediate cache refresh"""
        logger.info("Forcing cache refresh...")
        await self._refresh_tool_cache()
    
    def __repr__(self) -> str:
        return (
            f"<AbhikartaMCPToolBuilder "
            f"tools={len(self._tool_cache)} "
            f"running={self._running}>"
        )
