"""
MCP Delegate - Database operations for MCP Plugins and Tool Servers.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Version: 1.3.0
"""

from typing import Any, Dict, List, Optional
import uuid
import json
import logging

from ..database_delegate import DatabaseDelegate

logger = logging.getLogger(__name__)


class MCPDelegate(DatabaseDelegate):
    """
    Delegate for MCP-related database operations.
    
    Handles tables: mcp_plugins, mcp_tool_servers
    """
    
    # =========================================================================
    # MCP PLUGINS
    # =========================================================================
    
    def get_all_plugins(self, status: str = None, 
                        plugin_type: str = None) -> List[Dict]:
        """Get all MCP plugins with optional filters."""
        query = "SELECT * FROM mcp_plugins"
        conditions = []
        params = []
        
        if status:
            conditions.append("status = ?")
            params.append(status)
        if plugin_type:
            conditions.append("plugin_type = ?")
            params.append(plugin_type)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY name"
        return self.fetch_all(query, tuple(params) if params else None) or []
    
    def get_plugin(self, plugin_id: str) -> Optional[Dict]:
        """Get plugin by ID."""
        return self.fetch_one(
            "SELECT * FROM mcp_plugins WHERE plugin_id = ?",
            (plugin_id,)
        )
    
    def get_plugin_by_name(self, name: str) -> Optional[Dict]:
        """Get plugin by name."""
        return self.fetch_one(
            "SELECT * FROM mcp_plugins WHERE name = ?",
            (name,)
        )
    
    def get_plugins_count(self, status: str = None) -> int:
        """Get count of plugins."""
        where = f"status = '{status}'" if status else None
        return self.get_count("mcp_plugins", where)
    
    def create_plugin(self, name: str, created_by: str,
                      description: str = None, version: str = '1.0.0',
                      plugin_type: str = 'tool', status: str = 'active',
                      config: str = '{}', manifest: str = '{}',
                      server_name: str = None, server_url: str = None,
                      capabilities: str = '[]') -> Optional[str]:
        """Create a new MCP plugin and return plugin_id."""
        plugin_id = str(uuid.uuid4())
        try:
            self.execute(
                """INSERT INTO mcp_plugins 
                   (plugin_id, name, description, version, plugin_type, status,
                    config, manifest, server_name, server_url, capabilities, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (plugin_id, name, description, version, plugin_type, status,
                 config, manifest, server_name, server_url, capabilities, created_by)
            )
            return plugin_id
        except Exception as e:
            logger.error(f"Error creating plugin: {e}")
            return None
    
    def update_plugin(self, plugin_id: str, **kwargs) -> bool:
        """Update plugin fields."""
        if not kwargs:
            return False
        
        valid_fields = ['name', 'description', 'version', 'plugin_type', 'status',
                        'config', 'manifest', 'server_name', 'server_url',
                        'capabilities', 'health_status', 'last_health_check']
        
        updates = []
        params = []
        for key, value in kwargs.items():
            if key in valid_fields:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if not updates:
            return False
        
        params.append(plugin_id)
        query = f"UPDATE mcp_plugins SET {', '.join(updates)} WHERE plugin_id = ?"
        
        try:
            self.execute(query, tuple(params))
            return True
        except Exception as e:
            logger.error(f"Error updating plugin: {e}")
            return False
    
    def update_plugin_health(self, plugin_id: str, 
                             health_status: str) -> bool:
        """Update plugin health status."""
        try:
            self.execute(
                """UPDATE mcp_plugins 
                   SET health_status = ?, last_health_check = CURRENT_TIMESTAMP
                   WHERE plugin_id = ?""",
                (health_status, plugin_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error updating plugin health: {e}")
            return False
    
    def activate_plugin(self, plugin_id: str) -> bool:
        """Activate a plugin."""
        return self.update_plugin(plugin_id, status='active')
    
    def deactivate_plugin(self, plugin_id: str) -> bool:
        """Deactivate a plugin."""
        return self.update_plugin(plugin_id, status='disabled')
    
    def delete_plugin(self, plugin_id: str) -> bool:
        """Delete a plugin."""
        try:
            self.execute(
                "DELETE FROM mcp_plugins WHERE plugin_id = ?",
                (plugin_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting plugin: {e}")
            return False
    
    def plugin_exists(self, plugin_id: str) -> bool:
        """Check if plugin exists."""
        return self.exists("mcp_plugins", "plugin_id = ?", (plugin_id,))
    
    # =========================================================================
    # MCP TOOL SERVERS
    # =========================================================================
    
    def get_all_servers(self, is_active: bool = None) -> List[Dict]:
        """Get all MCP tool servers."""
        query = "SELECT * FROM mcp_tool_servers"
        params = []
        
        if is_active is not None:
            query += " WHERE is_active = ?"
            params.append(1 if is_active else 0)
        
        query += " ORDER BY name"
        return self.fetch_all(query, tuple(params) if params else None) or []
    
    def get_server(self, server_id: str) -> Optional[Dict]:
        """Get server by ID."""
        return self.fetch_one(
            "SELECT * FROM mcp_tool_servers WHERE server_id = ?",
            (server_id,)
        )
    
    def get_server_by_name(self, name: str) -> Optional[Dict]:
        """Get server by name."""
        return self.fetch_one(
            "SELECT * FROM mcp_tool_servers WHERE name = ?",
            (name,)
        )
    
    def get_servers_count(self, is_active: bool = None) -> int:
        """Get count of servers."""
        if is_active is not None:
            where = f"is_active = {1 if is_active else 0}"
        else:
            where = None
        return self.get_count("mcp_tool_servers", where)
    
    def create_server(self, name: str, base_url: str, created_by: str,
                      description: str = None, tools_endpoint: str = '/api/tools/list',
                      auth_type: str = 'none', auth_config: str = '{}',
                      is_active: int = 1, auto_refresh: int = 1,
                      refresh_interval_minutes: int = 60,
                      timeout_seconds: int = 30) -> Optional[str]:
        """Create a new MCP tool server and return server_id."""
        server_id = str(uuid.uuid4())
        try:
            self.execute(
                """INSERT INTO mcp_tool_servers 
                   (server_id, name, description, base_url, tools_endpoint,
                    auth_type, auth_config, is_active, auto_refresh,
                    refresh_interval_minutes, timeout_seconds, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (server_id, name, description, base_url, tools_endpoint,
                 auth_type, auth_config, is_active, auto_refresh,
                 refresh_interval_minutes, timeout_seconds, created_by)
            )
            return server_id
        except Exception as e:
            logger.error(f"Error creating server: {e}")
            return None
    
    def update_server(self, server_id: str, **kwargs) -> bool:
        """Update server fields."""
        if not kwargs:
            return False
        
        valid_fields = ['name', 'description', 'base_url', 'tools_endpoint',
                        'auth_type', 'auth_config', 'is_active', 'auto_refresh',
                        'refresh_interval_minutes', 'timeout_seconds',
                        'last_refresh', 'last_refresh_status', 'tool_count',
                        'cached_tools']
        
        updates = []
        params = []
        for key, value in kwargs.items():
            if key in valid_fields:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if not updates:
            return False
        
        params.append(server_id)
        query = f"UPDATE mcp_tool_servers SET {', '.join(updates)} WHERE server_id = ?"
        
        try:
            self.execute(query, tuple(params))
            return True
        except Exception as e:
            logger.error(f"Error updating server: {e}")
            return False
    
    def update_server_tools(self, server_id: str, cached_tools: str,
                            tool_count: int, status: str = 'success') -> bool:
        """Update server's cached tools after refresh."""
        try:
            self.execute(
                """UPDATE mcp_tool_servers 
                   SET cached_tools = ?, tool_count = ?, 
                       last_refresh = CURRENT_TIMESTAMP, last_refresh_status = ?
                   WHERE server_id = ?""",
                (cached_tools, tool_count, status, server_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error updating server tools: {e}")
            return False
    
    def update_server_refresh_status(self, server_id: str, 
                                     status: str) -> bool:
        """Update server refresh status."""
        try:
            self.execute(
                """UPDATE mcp_tool_servers 
                   SET last_refresh = CURRENT_TIMESTAMP, last_refresh_status = ?
                   WHERE server_id = ?""",
                (status, server_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error updating server refresh status: {e}")
            return False
    
    def activate_server(self, server_id: str) -> bool:
        """Activate a server."""
        return self.update_server(server_id, is_active=1)
    
    def deactivate_server(self, server_id: str) -> bool:
        """Deactivate a server."""
        return self.update_server(server_id, is_active=0)
    
    def delete_server(self, server_id: str) -> bool:
        """Delete a server."""
        try:
            self.execute(
                "DELETE FROM mcp_tool_servers WHERE server_id = ?",
                (server_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting server: {e}")
            return False
    
    def server_exists(self, server_id: str) -> bool:
        """Check if server exists."""
        return self.exists("mcp_tool_servers", "server_id = ?", (server_id,))
    
    def get_servers_needing_refresh(self) -> List[Dict]:
        """Get servers that need tool refresh."""
        return self.fetch_all(
            """SELECT * FROM mcp_tool_servers 
               WHERE is_active = 1 AND auto_refresh = 1
               AND (last_refresh IS NULL 
                    OR datetime(last_refresh, '+' || refresh_interval_minutes || ' minutes') 
                       < datetime('now'))
               ORDER BY last_refresh NULLS FIRST"""
        ) or []
