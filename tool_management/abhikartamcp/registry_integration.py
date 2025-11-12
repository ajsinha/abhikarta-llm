"""
Abhikarta LLM - Tool Management Framework
MCP Registry Integration - Automatic Tool Registration

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

import logging
from typing import Dict, List, Optional, Set
import asyncio

from .abhikarta_mcp_tool_builder import AbhikartaMCPToolBuilder, MCPToolSchema
from .abhikarta_base_tool import AbhikartaBaseTool

# Import from tool management framework
try:
    from tool_management.registry.registry import ToolRegistry
except ImportError:
    # Fallback for demonstration
    class ToolRegistry:
        def __init__(self):
            self._tools = {}
        
        def register(self, tool, group=None, tags=None):
            self._tools[tool.name] = tool
            return self
        
        def unregister(self, tool_name):
            if tool_name in self._tools:
                del self._tools[tool_name]
            return self
        
        def get(self, tool_name):
            return self._tools.get(tool_name)


logger = logging.getLogger(__name__)


class MCPRegistryIntegration:
    """
    Manages integration between MCP Tool Builder and Tool Registry.
    
    This class:
    - Monitors the MCP tool builder's cache
    - Automatically registers new tools in the registry
    - Removes tools that are no longer available
    - Handles tool updates and re-registration
    
    The integration runs as a background service that keeps the
    registry synchronized with the MCP server.
    """
    
    def __init__(
        self,
        registry: ToolRegistry,
        builder: Optional[AbhikartaMCPToolBuilder] = None,
        group_name: str = "abhikarta_mcp",
        tags: Optional[List[str]] = None
    ):
        """
        Initialize MCP registry integration.
        
        Args:
            registry: ToolRegistry instance to manage tools
            builder: AbhikartaMCPToolBuilder instance (or None to use singleton)
            group_name: Group name for registered tools
            tags: Optional tags to apply to all registered tools
        """
        self.registry = registry
        self.builder = builder or AbhikartaMCPToolBuilder()
        self.group_name = group_name
        self.tags = tags or ["mcp", "abhikarta"]
        
        # Track registered tools
        self._registered_tools: Set[str] = set()
        
        logger.info("MCPRegistryIntegration initialized")
    
    def _create_tool_from_schema(
        self,
        schema: MCPToolSchema,
        auth_token: Optional[str] = None
    ) -> AbhikartaBaseTool:
        """
        Create an AbhikartaBaseTool from a schema.
        
        Args:
            schema: MCPToolSchema with tool information
            auth_token: Optional authentication token
            
        Returns:
            AbhikartaBaseTool instance
        """
        return AbhikartaBaseTool(
            name=schema.name,
            description=schema.description,
            mcp_base_url=self.builder.config.base_url,
            mcp_endpoint=self.builder.config.mcp_endpoint,
            input_schema=schema.input_schema,
            output_schema=schema.output_schema,
            auth_token=auth_token or self.builder._auth_token,
            timeout=self.builder.config.timeout_seconds
        )
    
    def sync_tools(self):
        """
        Synchronize tools between builder cache and registry.
        
        This method:
        1. Gets all tools from the builder cache
        2. Registers new tools that aren't in the registry
        3. Updates existing tools if schemas changed
        4. Removes tools that are no longer in the cache
        """
        # Get current cached tools
        cached_tools = self.builder.get_all_schemas()
        cached_tool_names = set(cached_tools.keys())
        
        # Find tools to add
        tools_to_add = cached_tool_names - self._registered_tools
        
        # Find tools to remove
        tools_to_remove = self._registered_tools - cached_tool_names
        
        # Register new tools
        for tool_name in tools_to_add:
            schema = cached_tools[tool_name]
            try:
                tool = self._create_tool_from_schema(schema)
                self.registry.register(
                    tool,
                    group=self.group_name,
                    tags=self.tags
                )
                self._registered_tools.add(tool_name)
                logger.info(f"Registered MCP tool: {tool_name}")
            except Exception as e:
                logger.error(f"Failed to register tool '{tool_name}': {e}")
        
        # Remove obsolete tools
        for tool_name in tools_to_remove:
            try:
                self.registry.unregister(tool_name)
                self._registered_tools.discard(tool_name)
                logger.info(f"Unregistered MCP tool: {tool_name}")
            except Exception as e:
                logger.error(f"Failed to unregister tool '{tool_name}': {e}")
        
        # Check for updates to existing tools
        for tool_name in self._registered_tools:
            if tool_name in cached_tools:
                schema = cached_tools[tool_name]
                existing_tool = self.registry.get(tool_name)
                
                # Check if tool needs update (compare last_updated)
                if existing_tool:
                    # For now, we'll re-register if schema changed
                    # In a more sophisticated implementation, we could
                    # compare schemas directly
                    try:
                        # Unregister and re-register
                        self.registry.unregister(tool_name)
                        tool = self._create_tool_from_schema(schema)
                        self.registry.register(
                            tool,
                            group=self.group_name,
                            tags=self.tags
                        )
                        logger.debug(f"Updated MCP tool: {tool_name}")
                    except Exception as e:
                        logger.error(f"Failed to update tool '{tool_name}': {e}")
        
        logger.info(
            f"Tool sync complete: "
            f"{len(tools_to_add)} added, "
            f"{len(tools_to_remove)} removed, "
            f"{len(self._registered_tools)} total"
        )
    
    def get_registered_tool_names(self) -> List[str]:
        """
        Get list of all registered MCP tools.
        
        Returns:
            List of tool names
        """
        return list(self._registered_tools)
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the integration.
        
        Returns:
            Dictionary with integration statistics
        """
        builder_stats = self.builder.get_cache_stats()
        
        return {
            "registered_tools": len(self._registered_tools),
            "cached_tools": builder_stats["total_tools"],
            "group_name": self.group_name,
            "tags": self.tags,
            "builder_running": builder_stats["running"],
            "builder_authenticated": builder_stats["authenticated"]
        }
    
    def __repr__(self) -> str:
        return (
            f"<MCPRegistryIntegration "
            f"registered={len(self._registered_tools)} "
            f"group='{self.group_name}'>"
        )


class MCPAutoSync:
    """
    Automatic synchronization service for MCP tools.
    
    This service runs in the background and periodically synchronizes
    the tool registry with the MCP server.
    """
    
    def __init__(
        self,
        integration: MCPRegistryIntegration,
        sync_interval_seconds: int = 60
    ):
        """
        Initialize auto-sync service.
        
        Args:
            integration: MCPRegistryIntegration instance
            sync_interval_seconds: How often to sync (default: 60 seconds)
        """
        self.integration = integration
        self.sync_interval_seconds = sync_interval_seconds
        self._running = False
        self._sync_task: Optional[asyncio.Task] = None
        
        logger.info(
            f"MCPAutoSync initialized (interval: {sync_interval_seconds}s)"
        )
    
    async def _sync_loop(self):
        """Background task for periodic synchronization"""
        logger.info("Starting auto-sync loop")
        
        while self._running:
            try:
                # Perform sync
                self.integration.sync_tools()
            except Exception as e:
                logger.error(f"Error in auto-sync: {e}", exc_info=True)
            
            # Wait for next sync
            await asyncio.sleep(self.sync_interval_seconds)
        
        logger.info("Auto-sync loop stopped")
    
    async def start(self):
        """Start the auto-sync service"""
        if self._running:
            logger.warning("Auto-sync already running")
            return
        
        logger.info("Starting auto-sync service...")
        
        # Ensure builder is started
        if not self.integration.builder._running:
            await self.integration.builder.start()
        
        # Perform initial sync
        self.integration.sync_tools()
        
        # Start periodic sync
        self._running = True
        self._sync_task = asyncio.create_task(self._sync_loop())
        
        logger.info("Auto-sync service started")
    
    async def stop(self):
        """Stop the auto-sync service"""
        if not self._running:
            return
        
        logger.info("Stopping auto-sync service...")
        
        self._running = False
        
        # Cancel sync task
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
            self._sync_task = None
        
        logger.info("Auto-sync service stopped")
    
    def force_sync(self):
        """Force an immediate synchronization"""
        logger.info("Forcing immediate sync...")
        self.integration.sync_tools()
    
    def __repr__(self) -> str:
        return (
            f"<MCPAutoSync "
            f"running={self._running} "
            f"interval={self.sync_interval_seconds}s>"
        )
