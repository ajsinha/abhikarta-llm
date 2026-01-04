"""
Tools Registry - Centralized management for all tools in Abhikarta.

The ToolsRegistry provides:
- Centralized registration and discovery of tools
- Tool lifecycle management
- Tool execution routing
- Integration with MCP servers and plugins
- Tool statistics and monitoring

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import logging
import threading
from typing import Dict, Any, Optional, List, Callable, Type
from datetime import datetime

from .base_tool import (
    BaseTool, ToolMetadata, ToolSchema, ToolResult,
    ToolType, ToolCategory
)
from .function_tool import FunctionTool, AsyncFunctionTool
from .mcp_tool import MCPTool, MCPPluginTool
from .http_tool import HTTPTool, WebhookTool
from .code_fragment_tool import CodeFragmentTool, PythonExpressionTool
from .langchain_tool import LangChainToolWrapper, wrap_langchain_tools

logger = logging.getLogger(__name__)


class ToolsRegistry:
    """
    Centralized registry for all tools in the system.
    
    Provides thread-safe tool registration, discovery, and execution.
    Singleton pattern ensures single registry across the application.
    
    Usage:
        registry = ToolsRegistry.get_instance()
        
        # Register a tool
        registry.register(my_tool)
        
        # Get a tool
        tool = registry.get("tool_name")
        
        # Execute a tool
        result = registry.execute("tool_name", param1="value1")
        
        # List all tools
        tools = registry.list_tools()
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the registry."""
        if self._initialized:
            return
        
        self._tools: Dict[str, BaseTool] = {}
        self._tools_by_type: Dict[ToolType, List[str]] = {t: [] for t in ToolType}
        self._tools_by_category: Dict[ToolCategory, List[str]] = {c: [] for c in ToolCategory}
        self._tools_by_source: Dict[str, List[str]] = {}
        
        self._listeners: List[Callable] = []
        self._execution_log: List[Dict] = []
        self._max_log_size = 1000
        
        self._db_facade = None
        self._initialized = True
        
        logger.info("ToolsRegistry initialized")
    
    @classmethod
    def get_instance(cls) -> 'ToolsRegistry':
        """Get the singleton instance."""
        return cls()
    
    def set_db_facade(self, db_facade):
        """Set database facade for persistence."""
        self._db_facade = db_facade
    
    # =========================================================================
    # Tool Registration
    # =========================================================================
    
    def register(self, tool: BaseTool, replace: bool = False) -> bool:
        """
        Register a tool in the registry.
        
        Args:
            tool: BaseTool instance to register
            replace: Whether to replace existing tool with same name
            
        Returns:
            True if registered successfully
        """
        if not isinstance(tool, BaseTool):
            raise TypeError(f"Tool must extend BaseTool, got {type(tool)}")
        
        name = tool.name
        
        with self._lock:
            if name in self._tools and not replace:
                logger.warning(f"Tool '{name}' already registered, skipping")
                return False
            
            # Unregister old tool if replacing
            if name in self._tools:
                self._unregister_indexes(self._tools[name])
            
            # Register new tool
            self._tools[name] = tool
            self._register_indexes(tool)
            
            # Notify listeners
            self._notify_listeners('register', tool)
            
            logger.info(f"Registered tool: {name} (type={tool.tool_type.value})")
            return True
    
    def register_many(self, tools: List[BaseTool], replace: bool = False) -> int:
        """
        Register multiple tools.
        
        Returns:
            Count of successfully registered tools
        """
        count = 0
        for tool in tools:
            if self.register(tool, replace):
                count += 1
        return count
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a tool by name.
        
        Returns:
            True if unregistered successfully
        """
        with self._lock:
            if name not in self._tools:
                return False
            
            tool = self._tools[name]
            self._unregister_indexes(tool)
            del self._tools[name]
            
            self._notify_listeners('unregister', tool)
            
            logger.info(f"Unregistered tool: {name}")
            return True
    
    def _register_indexes(self, tool: BaseTool):
        """Add tool to indexes."""
        name = tool.name
        
        # By type
        self._tools_by_type[tool.tool_type].append(name)
        
        # By category
        self._tools_by_category[tool.category].append(name)
        
        # By source
        source = tool.metadata.source.split(':')[0] if tool.metadata.source else 'unknown'
        if source not in self._tools_by_source:
            self._tools_by_source[source] = []
        self._tools_by_source[source].append(name)
    
    def _unregister_indexes(self, tool: BaseTool):
        """Remove tool from indexes."""
        name = tool.name
        
        if name in self._tools_by_type[tool.tool_type]:
            self._tools_by_type[tool.tool_type].remove(name)
        
        if name in self._tools_by_category[tool.category]:
            self._tools_by_category[tool.category].remove(name)
        
        source = tool.metadata.source.split(':')[0] if tool.metadata.source else 'unknown'
        if source in self._tools_by_source and name in self._tools_by_source[source]:
            self._tools_by_source[source].remove(name)
    
    # =========================================================================
    # Tool Discovery
    # =========================================================================
    
    def get(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def get_by_id(self, tool_id: str) -> Optional[BaseTool]:
        """Get a tool by ID."""
        for tool in self._tools.values():
            if tool.tool_id == tool_id:
                return tool
        return None
    
    def has(self, name: str) -> bool:
        """Check if a tool exists."""
        return name in self._tools
    
    def list_tools(self, enabled_only: bool = False) -> List[BaseTool]:
        """
        List all registered tools.
        
        Args:
            enabled_only: Only return enabled tools
            
        Returns:
            List of BaseTool instances
        """
        tools = list(self._tools.values())
        if enabled_only:
            tools = [t for t in tools if t.is_enabled]
        return tools
    
    def list_by_type(self, tool_type: ToolType) -> List[BaseTool]:
        """List tools by type."""
        names = self._tools_by_type.get(tool_type, [])
        return [self._tools[n] for n in names if n in self._tools]
    
    def list_by_category(self, category: ToolCategory) -> List[BaseTool]:
        """List tools by category."""
        names = self._tools_by_category.get(category, [])
        return [self._tools[n] for n in names if n in self._tools]
    
    def list_by_source(self, source: str) -> List[BaseTool]:
        """List tools by source prefix."""
        names = self._tools_by_source.get(source, [])
        return [self._tools[n] for n in names if n in self._tools]
    
    def search(self, query: str, limit: int = 20) -> List[BaseTool]:
        """
        Search tools by name or description.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            Matching tools sorted by relevance
        """
        query_lower = query.lower()
        results = []
        
        for tool in self._tools.values():
            score = 0
            
            # Name match
            if query_lower in tool.name.lower():
                score += 10
                if tool.name.lower().startswith(query_lower):
                    score += 5
            
            # Description match
            if query_lower in tool.description.lower():
                score += 3
            
            # Tag match
            for tag in tool.metadata.tags:
                if query_lower in tag.lower():
                    score += 2
            
            if score > 0:
                results.append((score, tool))
        
        results.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in results[:limit]]
    
    def get_names(self) -> List[str]:
        """Get all tool names."""
        return list(self._tools.keys())
    
    def count(self) -> int:
        """Get total number of registered tools."""
        return len(self._tools)
    
    # =========================================================================
    # Tool Execution
    # =========================================================================
    
    def execute(self, name: str, **kwargs) -> ToolResult:
        """
        Execute a tool by name.
        
        Args:
            name: Tool name
            **kwargs: Tool parameters
            
        Returns:
            ToolResult with execution outcome
        """
        tool = self.get(name)
        if not tool:
            return ToolResult.error_result(f"Tool '{name}' not found")
        
        if not tool.is_enabled:
            return ToolResult.error_result(f"Tool '{name}' is disabled")
        
        # Execute and log
        result = tool.safe_execute(**kwargs)
        self._log_execution(tool, kwargs, result)
        
        return result
    
    async def async_execute(self, name: str, **kwargs) -> ToolResult:
        """
        Execute a tool asynchronously.
        
        Args:
            name: Tool name
            **kwargs: Tool parameters
            
        Returns:
            ToolResult with execution outcome
        """
        tool = self.get(name)
        if not tool:
            return ToolResult.error_result(f"Tool '{name}' not found")
        
        if not tool.is_enabled:
            return ToolResult.error_result(f"Tool '{name}' is disabled")
        
        result = await tool.async_execute(**kwargs)
        self._log_execution(tool, kwargs, result)
        
        return result
    
    def _log_execution(self, tool: BaseTool, params: Dict, result: ToolResult):
        """Log tool execution."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'tool_name': tool.name,
            'tool_type': tool.tool_type.value,
            'success': result.success,
            'execution_time_ms': result.execution_time_ms,
            'error': result.error
        }
        
        with self._lock:
            self._execution_log.append(log_entry)
            if len(self._execution_log) > self._max_log_size:
                self._execution_log = self._execution_log[-self._max_log_size:]
    
    # =========================================================================
    # Bulk Registration Helpers
    # =========================================================================
    
    def register_function(self, func: Callable, name: str = None,
                         description: str = None, 
                         category: ToolCategory = None) -> BaseTool:
        """
        Register a Python function as a tool.
        
        Returns:
            The registered FunctionTool
        """
        tool = FunctionTool.from_function(
            func, name=name, description=description, category=category
        )
        self.register(tool)
        return tool
    
    def register_from_mcp_server(self, server_url: str, server_name: str,
                                auth_token: str = None) -> int:
        """
        Register all tools from an MCP server.
        
        Returns:
            Count of registered tools
        """
        import requests
        
        try:
            headers = {}
            if auth_token:
                headers['Authorization'] = f"Bearer {auth_token}"
            
            # Fetch tools list
            response = requests.get(
                f"{server_url.rstrip('/')}/api/tools",
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch tools from {server_url}: {response.status_code}")
                return 0
            
            tools_data = response.json()
            tools = tools_data.get('tools', tools_data) if isinstance(tools_data, dict) else tools_data
            
            count = 0
            for tool_def in tools:
                try:
                    mcp_tool = MCPTool.from_mcp_tool_definition(
                        tool_def, server_url, server_name, auth_token
                    )
                    if self.register(mcp_tool):
                        count += 1
                except Exception as e:
                    logger.error(f"Failed to wrap MCP tool: {e}")
            
            logger.info(f"Registered {count} tools from MCP server {server_name}")
            return count
            
        except Exception as e:
            logger.error(f"Error connecting to MCP server {server_url}: {e}")
            return 0
    
    def register_from_code_fragments(self) -> int:
        """
        Register tools from database code fragments.
        
        Returns:
            Count of registered tools
        """
        if not self._db_facade:
            logger.warning("No database facade configured")
            return 0
        
        try:
            fragments = self._db_facade.fetch_all(
                "SELECT * FROM code_fragments WHERE status = 'active'"
            ) or []
            
            count = 0
            for fragment in fragments:
                try:
                    tool = CodeFragmentTool.from_db_fragment(fragment)
                    if self.register(tool):
                        count += 1
                except Exception as e:
                    logger.error(f"Failed to create tool from fragment: {e}")
            
            logger.info(f"Registered {count} tools from code fragments")
            return count
            
        except Exception as e:
            logger.error(f"Error loading code fragments: {e}")
            return 0
    
    def register_langchain_tools(self, tools: List[Any]) -> int:
        """
        Register LangChain tools.
        
        Returns:
            Count of registered tools
        """
        wrapped = wrap_langchain_tools(tools)
        return self.register_many(wrapped)
    
    # =========================================================================
    # Tool Format Conversion
    # =========================================================================
    
    def to_openai_functions(self, names: List[str] = None) -> List[Dict]:
        """Convert tools to OpenAI function calling format."""
        tools = [self.get(n) for n in (names or self.get_names())]
        return [t.to_openai_function() for t in tools if t and t.is_enabled]
    
    def to_anthropic_tools(self, names: List[str] = None) -> List[Dict]:
        """Convert tools to Anthropic tool format."""
        tools = [self.get(n) for n in (names or self.get_names())]
        return [t.to_anthropic_tool() for t in tools if t and t.is_enabled]
    
    def to_langchain_tools(self, names: List[str] = None) -> List[Any]:
        """Convert tools to LangChain StructuredTool format."""
        tools = [self.get(n) for n in (names or self.get_names())]
        lc_tools = []
        for tool in tools:
            if tool and tool.is_enabled:
                lc = tool.to_langchain_tool()
                if lc:
                    lc_tools.append(lc)
        return lc_tools
    
    # =========================================================================
    # Listeners
    # =========================================================================
    
    def add_listener(self, callback: Callable):
        """Add a listener for tool events."""
        self._listeners.append(callback)
    
    def remove_listener(self, callback: Callable):
        """Remove a listener."""
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def _notify_listeners(self, event: str, tool: BaseTool):
        """Notify all listeners of an event."""
        for listener in self._listeners:
            try:
                listener(event, tool)
            except Exception as e:
                logger.error(f"Listener error: {e}")
    
    # =========================================================================
    # Statistics
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        type_counts = {t.value: len(v) for t, v in self._tools_by_type.items() if v}
        category_counts = {c.value: len(v) for c, v in self._tools_by_category.items() if v}
        
        # Recent executions
        recent_executions = self._execution_log[-100:] if self._execution_log else []
        success_count = sum(1 for e in recent_executions if e['success'])
        
        return {
            'total_tools': len(self._tools),
            'enabled_tools': sum(1 for t in self._tools.values() if t.is_enabled),
            'by_type': type_counts,
            'by_category': category_counts,
            'sources': list(self._tools_by_source.keys()),
            'recent_executions': len(recent_executions),
            'success_rate': success_count / len(recent_executions) if recent_executions else 0
        }
    
    def get_execution_log(self, limit: int = 100) -> List[Dict]:
        """Get recent execution log."""
        return self._execution_log[-limit:]
    
    # =========================================================================
    # Serialization
    # =========================================================================
    
    def export_catalog(self) -> List[Dict]:
        """Export tool catalog as serializable dict."""
        catalog = []
        for tool in self._tools.values():
            catalog.append({
                'name': tool.name,
                'tool_id': tool.tool_id,
                'description': tool.description,
                'type': tool.tool_type.value,
                'category': tool.category.value,
                'enabled': tool.is_enabled,
                'metadata': tool.metadata.to_dict(),
                'schema': tool.get_schema().to_json_schema()
            })
        return catalog
    
    def clear(self):
        """Clear all registered tools."""
        with self._lock:
            self._tools.clear()
            for lst in self._tools_by_type.values():
                lst.clear()
            for lst in self._tools_by_category.values():
                lst.clear()
            self._tools_by_source.clear()
        
        logger.info("ToolsRegistry cleared")


# Convenience function
def get_tools_registry() -> ToolsRegistry:
    """Get the global ToolsRegistry instance."""
    return ToolsRegistry.get_instance()
