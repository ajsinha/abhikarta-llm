"""
MCP Server Manager - Centralized management for all MCP servers.

Provides:
- Server lifecycle management (connect, disconnect, reconnect)
- Tool discovery and registration
- Health monitoring
- Integration with ToolsRegistry

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import logging
import threading
import time
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from .server import (
    MCPServer, MCPServerConfig, MCPServerState, MCPServerStatus,
    MCPToolDefinition
)
from .client import MCPClientBase, create_mcp_client

logger = logging.getLogger(__name__)


class MCPServerManager:
    """
    Centralized manager for all MCP servers.
    
    Handles:
    - Server registration and configuration
    - Connection lifecycle
    - Tool discovery and wrapping
    - Health monitoring
    - Automatic reconnection
    
    Usage:
        manager = MCPServerManager.get_instance()
        
        # Add a server
        manager.add_server(MCPServerConfig(
            server_id="my_server",
            name="My MCP Server",
            url="http://localhost:8000"
        ))
        
        # Connect and load tools
        manager.connect_server("my_server")
        
        # Get tools
        tools = manager.get_server_tools("my_server")
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the manager."""
        if self._initialized:
            return
        
        self._servers: Dict[str, MCPServer] = {}
        self._clients: Dict[str, MCPClientBase] = {}
        self._listeners: List[Callable] = []
        self._db_facade = None
        self._tools_registry = None
        self._monitor_thread = None
        self._monitor_running = False
        self._executor = ThreadPoolExecutor(max_workers=10)
        
        self._initialized = True
        logger.info("MCPServerManager initialized")
    
    @classmethod
    def get_instance(cls) -> 'MCPServerManager':
        """Get singleton instance."""
        return cls()
    
    def set_db_facade(self, db_facade):
        """Set database facade for persistence."""
        self._db_facade = db_facade
    
    def set_tools_registry(self, registry):
        """Set tools registry for tool registration."""
        self._tools_registry = registry
    
    # =========================================================================
    # Server Management
    # =========================================================================
    
    def add_server(self, config: MCPServerConfig, connect: bool = False) -> MCPServer:
        """
        Add a new MCP server.
        
        Args:
            config: Server configuration
            connect: Whether to connect immediately
            
        Returns:
            MCPServer instance
        """
        with self._lock:
            if config.server_id in self._servers:
                logger.warning(f"Server {config.server_id} already exists, updating")
                self._servers[config.server_id].config = config
            else:
                server = MCPServer.from_config(config)
                self._servers[config.server_id] = server
                logger.info(f"Added MCP server: {config.name}")
        
        if connect or config.auto_connect:
            self.connect_server(config.server_id)
        
        return self._servers[config.server_id]
    
    def remove_server(self, server_id: str) -> bool:
        """
        Remove an MCP server.
        
        Args:
            server_id: Server identifier
            
        Returns:
            True if removed successfully
        """
        with self._lock:
            if server_id not in self._servers:
                return False
            
            # Disconnect first
            self.disconnect_server(server_id)
            
            # Remove from registry
            del self._servers[server_id]
            
            logger.info(f"Removed MCP server: {server_id}")
            return True
    
    def get_server(self, server_id: str) -> Optional[MCPServer]:
        """Get a server by ID."""
        return self._servers.get(server_id)
    
    def list_servers(self, connected_only: bool = False) -> List[MCPServer]:
        """
        List all servers.
        
        Args:
            connected_only: Only return connected servers
            
        Returns:
            List of MCPServer instances
        """
        servers = list(self._servers.values())
        if connected_only:
            servers = [s for s in servers if s.is_connected]
        return servers
    
    def get_server_ids(self) -> List[str]:
        """Get all server IDs."""
        return list(self._servers.keys())
    
    # =========================================================================
    # Connection Management
    # =========================================================================
    
    def connect_server(self, server_id: str) -> bool:
        """
        Connect to an MCP server.
        
        Args:
            server_id: Server identifier
            
        Returns:
            True if connected successfully
        """
        server = self._servers.get(server_id)
        if not server:
            logger.error(f"Server {server_id} not found")
            return False
        
        try:
            # Create client if needed
            if server_id not in self._clients:
                self._clients[server_id] = create_mcp_client(server.config)
            
            client = self._clients[server_id]
            
            # Update state
            server.state.status = MCPServerStatus.CONNECTING
            self._notify_listeners('connecting', server)
            
            # Attempt connection
            if client.connect():
                server.state.status = MCPServerStatus.CONNECTED
                server.state.last_connected = datetime.utcnow()
                server.state.error_count = 0
                
                # Load tools
                self._load_server_tools(server_id)
                
                self._notify_listeners('connected', server)
                logger.info(f"Connected to MCP server: {server.name}")
                return True
            else:
                server.state.status = MCPServerStatus.ERROR
                server.state.last_error = "Connection failed"
                server.state.error_count += 1
                
                self._notify_listeners('error', server)
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to {server_id}: {e}")
            server.state.status = MCPServerStatus.ERROR
            server.state.last_error = str(e)
            server.state.error_count += 1
            
            self._notify_listeners('error', server)
            return False
    
    def disconnect_server(self, server_id: str) -> bool:
        """
        Disconnect from an MCP server.
        
        Args:
            server_id: Server identifier
            
        Returns:
            True if disconnected successfully
        """
        server = self._servers.get(server_id)
        if not server:
            return False
        
        try:
            # Disconnect client
            if server_id in self._clients:
                self._clients[server_id].disconnect()
                del self._clients[server_id]
            
            # Unregister tools from registry
            self._unregister_server_tools(server_id)
            
            # Update state
            server.state.status = MCPServerStatus.DISCONNECTED
            server.tools = []
            server.state.tools_loaded = False
            
            self._notify_listeners('disconnected', server)
            logger.info(f"Disconnected from MCP server: {server.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from {server_id}: {e}")
            return False
    
    def reconnect_server(self, server_id: str) -> bool:
        """Reconnect to a server."""
        self.disconnect_server(server_id)
        return self.connect_server(server_id)
    
    def connect_all(self) -> Dict[str, bool]:
        """
        Connect to all servers with auto_connect enabled.
        
        Returns:
            Dict of server_id -> success
        """
        results = {}
        for server_id, server in self._servers.items():
            if server.config.auto_connect:
                results[server_id] = self.connect_server(server_id)
        return results
    
    def disconnect_all(self):
        """Disconnect from all servers."""
        for server_id in list(self._servers.keys()):
            self.disconnect_server(server_id)
    
    # =========================================================================
    # Tool Management
    # =========================================================================
    
    def _load_server_tools(self, server_id: str):
        """Load tools from a connected server."""
        server = self._servers.get(server_id)
        client = self._clients.get(server_id)
        
        if not server or not client:
            return
        
        try:
            # Fetch tools from server
            tool_defs = client.list_tools()
            server.tools = tool_defs
            server.state.tool_count = len(tool_defs)
            server.state.tools_loaded = True
            
            # Register tools with registry
            self._register_server_tools(server_id)
            
            logger.info(f"Loaded {len(tool_defs)} tools from {server.name}")
            
        except Exception as e:
            logger.error(f"Error loading tools from {server_id}: {e}")
    
    def _register_server_tools(self, server_id: str):
        """Register server tools with ToolsRegistry."""
        if not self._tools_registry:
            return
        
        server = self._servers.get(server_id)
        if not server:
            return
        
        from ..tools import MCPTool
        
        for tool_def in server.tools:
            try:
                mcp_tool = MCPTool.from_mcp_tool_definition(
                    tool_def.to_dict(),
                    server.config.url,
                    server.config.name,
                    server.config.auth_token
                )
                self._tools_registry.register(mcp_tool, replace=True)
                
            except Exception as e:
                logger.error(f"Failed to register tool {tool_def.name}: {e}")
    
    def _unregister_server_tools(self, server_id: str):
        """Unregister server tools from ToolsRegistry."""
        if not self._tools_registry:
            return
        
        server = self._servers.get(server_id)
        if not server:
            return
        
        # Find and unregister tools from this server
        source_prefix = f"mcp:{server.config.name}"
        tools = self._tools_registry.list_by_source('mcp')
        
        for tool in tools:
            if tool.metadata.source.startswith(source_prefix):
                self._tools_registry.unregister(tool.name)
    
    def get_server_tools(self, server_id: str) -> List[MCPToolDefinition]:
        """Get tools from a specific server."""
        server = self._servers.get(server_id)
        return server.tools if server else []
    
    def get_all_tools(self) -> List[MCPToolDefinition]:
        """Get tools from all connected servers."""
        tools = []
        for server in self._servers.values():
            if server.is_connected:
                tools.extend(server.tools)
        return tools
    
    def call_tool(self, server_id: str, tool_name: str, 
                 parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on a specific server.
        
        Args:
            server_id: Server identifier
            tool_name: Tool name
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        client = self._clients.get(server_id)
        if not client:
            return {'success': False, 'error': f'Server {server_id} not connected'}
        
        return client.call_tool(tool_name, parameters)
    
    # =========================================================================
    # Health Monitoring
    # =========================================================================
    
    def check_health(self, server_id: str) -> tuple[bool, float]:
        """
        Check health of a server.
        
        Returns:
            (healthy, latency_ms)
        """
        client = self._clients.get(server_id)
        if not client:
            return False, 0
        
        healthy, latency = client.health_check()
        
        server = self._servers.get(server_id)
        if server:
            server.state.latency_ms = latency
            if not healthy and server.is_connected:
                server.state.status = MCPServerStatus.ERROR
                self._notify_listeners('error', server)
        
        return healthy, latency
    
    def check_all_health(self) -> Dict[str, tuple[bool, float]]:
        """Check health of all servers."""
        results = {}
        for server_id in self._servers.keys():
            results[server_id] = self.check_health(server_id)
        return results
    
    def start_health_monitor(self, interval_seconds: int = 30):
        """Start background health monitoring."""
        if self._monitor_running:
            return
        
        self._monitor_running = True
        
        def monitor_loop():
            while self._monitor_running:
                try:
                    self.check_all_health()
                    
                    # Attempt reconnection for errored servers
                    for server_id, server in self._servers.items():
                        if (server.state.status == MCPServerStatus.ERROR and
                            server.config.auto_connect):
                            self.connect_server(server_id)
                            
                except Exception as e:
                    logger.error(f"Health monitor error: {e}")
                
                time.sleep(interval_seconds)
        
        self._monitor_thread = threading.Thread(
            target=monitor_loop, daemon=True
        )
        self._monitor_thread.start()
        logger.info("Health monitor started")
    
    def stop_health_monitor(self):
        """Stop background health monitoring."""
        self._monitor_running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
            self._monitor_thread = None
        logger.info("Health monitor stopped")
    
    # =========================================================================
    # Database Persistence
    # =========================================================================
    
    def load_from_database(self) -> int:
        """
        Load servers from database.
        
        Returns:
            Number of servers loaded
        """
        if not self._db_facade:
            return 0
        
        try:
            records = self._db_facade.fetch_all(
                "SELECT * FROM mcp_tool_servers WHERE status = 'active'"
            ) or []
            
            count = 0
            for record in records:
                try:
                    config = MCPServerConfig.from_db_record(record)
                    self.add_server(config, connect=False)
                    count += 1
                except Exception as e:
                    logger.error(f"Failed to load server: {e}")
            
            logger.info(f"Loaded {count} MCP servers from database")
            return count
            
        except Exception as e:
            logger.error(f"Error loading servers from database: {e}")
            return 0
    
    def save_to_database(self, server_id: str) -> bool:
        """Save server configuration to database."""
        if not self._db_facade:
            return False
        
        server = self._servers.get(server_id)
        if not server:
            return False
        
        try:
            import json
            
            self._db_facade.execute("""
                INSERT OR REPLACE INTO mcp_tool_servers 
                (server_id, name, description, url, transport, auth_type,
                 auth_token, auth_header, timeout_seconds, auto_connect,
                 tools_endpoint, call_endpoint, health_endpoint, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
            """, (
                server.config.server_id,
                server.config.name,
                server.config.description,
                server.config.url,
                server.config.transport.value,
                server.config.auth_type.value,
                server.config.auth_token,
                server.config.auth_header,
                server.config.timeout_seconds,
                server.config.auto_connect,
                server.config.tools_endpoint,
                server.config.call_endpoint,
                server.config.health_endpoint
            ))
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving server to database: {e}")
            return False
    
    # =========================================================================
    # Listeners
    # =========================================================================
    
    def add_listener(self, callback: Callable):
        """Add event listener."""
        self._listeners.append(callback)
    
    def remove_listener(self, callback: Callable):
        """Remove event listener."""
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def _notify_listeners(self, event: str, server: MCPServer):
        """Notify all listeners."""
        for listener in self._listeners:
            try:
                listener(event, server)
            except Exception as e:
                logger.error(f"Listener error: {e}")
    
    # =========================================================================
    # Statistics
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics."""
        total = len(self._servers)
        connected = sum(1 for s in self._servers.values() if s.is_connected)
        total_tools = sum(s.state.tool_count for s in self._servers.values())
        
        return {
            'total_servers': total,
            'connected_servers': connected,
            'disconnected_servers': total - connected,
            'total_tools': total_tools,
            'servers': {
                sid: {
                    'name': s.name,
                    'status': s.state.status.value,
                    'tool_count': s.state.tool_count,
                    'latency_ms': s.state.latency_ms
                }
                for sid, s in self._servers.items()
            }
        }
    
    def shutdown(self):
        """Shutdown the manager."""
        self.stop_health_monitor()
        self.disconnect_all()
        self._executor.shutdown(wait=False)
        logger.info("MCPServerManager shutdown")


# Convenience function
def get_mcp_manager() -> MCPServerManager:
    """Get the global MCPServerManager instance."""
    return MCPServerManager.get_instance()
