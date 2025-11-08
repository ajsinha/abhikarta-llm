"""
Abhikarta LLM - Tool Management Framework
Tool Registry

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

This module provides the central registry for managing all tools in the system.
"""

from typing import Dict, List, Optional, Set, Callable
from collections import defaultdict
import logging

from ..core import (
    BaseTool,
    ToolType,
    ToolStatus,
    ToolResult,
    ToolNotFoundError,
    ToolDisabledError,
    ToolRegistrationError
)


logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Central registry for managing all tools in the Abhikarta framework.
    
    Provides registration, discovery, grouping, and lifecycle management
    for tools. Supports middleware for cross-cutting concerns.
    """
    
    def __init__(self):
        """Initialize an empty tool registry"""
        self._tools: Dict[str, BaseTool] = {}
        self._groups: Dict[str, Set[str]] = defaultdict(set)
        self._tags: Dict[str, Set[str]] = defaultdict(set)
        self._middleware: List[Callable] = []
        self._aliases: Dict[str, str] = {}
        
    def register(
        self,
        tool: BaseTool,
        group: Optional[str] = None,
        tags: Optional[List[str]] = None,
        alias: Optional[str] = None
    ) -> 'ToolRegistry':
        """
        Register a tool in the registry.
        
        Args:
            tool: BaseTool instance to register
            group: Optional group name for organization
            tags: Optional list of tags
            alias: Optional alias name for the tool
            
        Returns:
            Self for method chaining
            
        Raises:
            ToolRegistrationError: If tool name already exists
        """
        if tool.name in self._tools:
            raise ToolRegistrationError(
                f"Tool with name '{tool.name}' already registered"
            )
        
        # Register tool
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name} (type: {tool.tool_type.value})")
        
        # Add to group
        if group:
            self._groups[group].add(tool.name)
            logger.debug(f"Added tool '{tool.name}' to group '{group}'")
        
        # Add tags
        if tags:
            for tag in tags:
                self._tags[tag].add(tool.name)
                tool.add_tag(tag)
        
        # Register alias
        if alias:
            if alias in self._aliases:
                raise ToolRegistrationError(
                    f"Alias '{alias}' already exists"
                )
            self._aliases[alias] = tool.name
            logger.debug(f"Registered alias '{alias}' for tool '{tool.name}'")
        
        return self
    
    def unregister(self, tool_name: str) -> 'ToolRegistry':
        """
        Unregister a tool from the registry.
        
        Args:
            tool_name: Name of tool to unregister
            
        Returns:
            Self for method chaining
        """
        if tool_name not in self._tools:
            logger.warning(f"Attempted to unregister unknown tool: {tool_name}")
            return self
        
        # Remove from tools
        del self._tools[tool_name]
        
        # Remove from groups
        for group_tools in self._groups.values():
            group_tools.discard(tool_name)
        
        # Remove from tags
        for tag_tools in self._tags.values():
            tag_tools.discard(tool_name)
        
        # Remove aliases
        aliases_to_remove = [
            alias for alias, name in self._aliases.items()
            if name == tool_name
        ]
        for alias in aliases_to_remove:
            del self._aliases[alias]
        
        logger.info(f"Unregistered tool: {tool_name}")
        return self
    
    def get(self, name_or_alias: str) -> Optional[BaseTool]:
        """
        Get a tool by name or alias.
        
        Args:
            name_or_alias: Tool name or registered alias
            
        Returns:
            BaseTool instance or None if not found
        """
        # Check if it's an alias
        if name_or_alias in self._aliases:
            name_or_alias = self._aliases[name_or_alias]
        
        return self._tools.get(name_or_alias)
    
    def get_or_raise(self, name_or_alias: str) -> BaseTool:
        """
        Get a tool by name or raise exception if not found.
        
        Args:
            name_or_alias: Tool name or registered alias
            
        Returns:
            BaseTool instance
            
        Raises:
            ToolNotFoundError: If tool not found
        """
        tool = self.get(name_or_alias)
        if tool is None:
            raise ToolNotFoundError(name_or_alias)
        return tool
    
    def list_all(
        self,
        enabled_only: bool = False,
        include_deprecated: bool = False
    ) -> List[BaseTool]:
        """
        List all registered tools.
        
        Args:
            enabled_only: If True, only return enabled tools
            include_deprecated: If True, include deprecated tools
            
        Returns:
            List of BaseTool instances
        """
        tools = list(self._tools.values())
        
        if enabled_only:
            tools = [t for t in tools if t.enabled]
        
        if not include_deprecated:
            tools = [t for t in tools if t.status != ToolStatus.DEPRECATED]
        
        return tools
    
    def list_by_type(self, tool_type: ToolType) -> List[BaseTool]:
        """
        Get all tools of a specific type.
        
        Args:
            tool_type: ToolType to filter by
            
        Returns:
            List of matching tools
        """
        return [t for t in self._tools.values() if t.tool_type == tool_type]
    
    def list_by_group(self, group: str) -> List[BaseTool]:
        """
        Get all tools in a specific group.
        
        Args:
            group: Group name
            
        Returns:
            List of tools in the group
        """
        tool_names = self._groups.get(group, set())
        return [self._tools[name] for name in tool_names if name in self._tools]
    
    def list_by_tag(self, tag: str) -> List[BaseTool]:
        """
        Get all tools with a specific tag.
        
        Args:
            tag: Tag to filter by
            
        Returns:
            List of matching tools
        """
        tool_names = self._tags.get(tag, set())
        return [self._tools[name] for name in tool_names if name in self._tools]
    
    def search(self, query: str) -> List[BaseTool]:
        """
        Search for tools by name or description.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching tools
        """
        query_lower = query.lower()
        results = []
        
        for tool in self._tools.values():
            if (query_lower in tool.name.lower() or
                query_lower in tool.description.lower()):
                results.append(tool)
        
        return results
    
    def get_all_schemas(
        self,
        format: str = "standard",
        enabled_only: bool = True
    ) -> List[Dict]:
        """
        Get schemas for all tools.
        
        Args:
            format: Schema format ('standard', 'anthropic', or 'openai')
            enabled_only: If True, only include enabled tools
            
        Returns:
            List of tool schemas
        """
        tools = self.list_all(enabled_only=enabled_only)
        
        if format == "anthropic":
            return [t.get_anthropic_schema() for t in tools]
        elif format == "openai":
            return [t.get_openai_schema() for t in tools]
        else:
            return [t.get_schema() for t in tools]
    
    def add_middleware(self, middleware: Callable) -> 'ToolRegistry':
        """
        Add middleware to the registry.
        
        Middleware functions receive and can modify the execution context.
        
        Args:
            middleware: Callable middleware function
            
        Returns:
            Self for method chaining
        """
        self._middleware.append(middleware)
        logger.info(f"Added middleware: {middleware.__name__}")
        return self
    
    def remove_middleware(self, middleware: Callable) -> 'ToolRegistry':
        """Remove middleware from the registry"""
        if middleware in self._middleware:
            self._middleware.remove(middleware)
            logger.info(f"Removed middleware: {middleware.__name__}")
        return self
    
    def clear_middleware(self) -> 'ToolRegistry':
        """Remove all middleware"""
        self._middleware.clear()
        logger.info("Cleared all middleware")
        return self
    
    async def execute(
        self,
        tool_name: str,
        **kwargs
    ) -> ToolResult:
        """
        Execute a tool by name with middleware support.
        
        Args:
            tool_name: Name or alias of tool to execute
            **kwargs: Tool parameters
            
        Returns:
            ToolResult from execution
            
        Raises:
            ToolNotFoundError: If tool not found
            ToolDisabledError: If tool is disabled
        """
        # Resolve alias
        if tool_name in self._aliases:
            tool_name = self._aliases[tool_name]
        
        # Get tool
        tool = self.get_or_raise(tool_name)
        
        # Check if enabled
        if not tool.enabled:
            raise ToolDisabledError(tool_name)
        
        # Build execution context
        context = {
            "tool": tool,
            "params": kwargs,
            "skip": False,
            "result": None
        }
        
        # Apply middleware
        for middleware in self._middleware:
            context = await middleware(context)
            if context.get("skip"):
                return context.get("result")
        
        # Execute tool
        if tool.execution_mode.value == "async":
            result = await tool._execute_async_with_tracking(**kwargs)
        else:
            result = tool._execute_with_tracking(**kwargs)
        
        return result
    
    def get_statistics(self) -> Dict:
        """
        Get registry statistics.
        
        Returns:
            Dictionary with registry metrics
        """
        total_executions = sum(t._execution_count for t in self._tools.values())
        total_time = sum(t._total_execution_time for t in self._tools.values())
        
        type_counts = defaultdict(int)
        for tool in self._tools.values():
            type_counts[tool.tool_type.value] += 1
        
        status_counts = defaultdict(int)
        for tool in self._tools.values():
            status_counts[tool.status.value] += 1
        
        return {
            "total_tools": len(self._tools),
            "total_groups": len(self._groups),
            "total_tags": len(self._tags),
            "total_executions": total_executions,
            "total_execution_time": total_time,
            "tools_by_type": dict(type_counts),
            "tools_by_status": dict(status_counts),
            "middleware_count": len(self._middleware)
        }
    
    def __len__(self) -> int:
        """Return number of registered tools"""
        return len(self._tools)
    
    def __contains__(self, tool_name: str) -> bool:
        """Check if tool is registered"""
        return tool_name in self._tools or tool_name in self._aliases
    
    def __repr__(self) -> str:
        return f"<ToolRegistry tools={len(self._tools)} groups={len(self._groups)}>"
