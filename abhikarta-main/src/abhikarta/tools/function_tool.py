"""
Function Tool - Tool implementation for Python functions.

Allows wrapping any Python function as a BaseTool.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import logging
import inspect
import uuid
from typing import Callable, Dict, Any, Optional, List, get_type_hints
from functools import wraps

from .base_tool import (
    BaseTool, ToolMetadata, ToolSchema, ToolParameter, 
    ToolResult, ToolType, ToolCategory
)

logger = logging.getLogger(__name__)


class FunctionTool(BaseTool):
    """
    Tool that wraps a Python function.
    
    Automatically extracts parameter schema from function signature
    and type hints.
    
    Example:
        def search(query: str, limit: int = 10) -> str:
            '''Search for items.'''
            return f"Found results for {query}"
        
        tool = FunctionTool.from_function(search)
    """
    
    def __init__(self, func: Callable, metadata: ToolMetadata, 
                 schema: ToolSchema = None):
        """
        Initialize FunctionTool.
        
        Args:
            func: The function to wrap
            metadata: Tool metadata
            schema: Optional schema (auto-generated if not provided)
        """
        super().__init__(metadata)
        self._func = func
        self._schema = schema or self._generate_schema()
    
    def execute(self, **kwargs) -> ToolResult:
        """Execute the wrapped function."""
        try:
            result = self._func(**kwargs)
            return ToolResult.success_result(result)
        except Exception as e:
            logger.error(f"FunctionTool {self.name} error: {e}")
            return ToolResult.error_result(str(e))
    
    def get_schema(self) -> ToolSchema:
        """Get the parameter schema."""
        return self._schema
    
    def _generate_schema(self) -> ToolSchema:
        """Generate schema from function signature."""
        parameters = []
        sig = inspect.signature(self._func)
        
        try:
            hints = get_type_hints(self._func)
        except:
            hints = {}
        
        for name, param in sig.parameters.items():
            if name in ('self', 'cls'):
                continue
            
            # Determine type from hints
            param_type = "string"
            if name in hints:
                hint = hints[name]
                type_map = {
                    str: "string",
                    int: "integer",
                    float: "number",
                    bool: "boolean",
                    list: "array",
                    dict: "object"
                }
                param_type = type_map.get(hint, "string")
            
            # Check if required (no default value)
            required = param.default == inspect.Parameter.empty
            default = None if required else param.default
            
            tool_param = ToolParameter(
                name=name,
                param_type=param_type,
                description=f"Parameter: {name}",
                required=required,
                default=default
            )
            parameters.append(tool_param)
        
        return ToolSchema(parameters=parameters)
    
    @classmethod
    def from_function(cls, func: Callable, name: str = None, 
                     description: str = None, category: ToolCategory = None,
                     tags: List[str] = None) -> 'FunctionTool':
        """
        Create a FunctionTool from a Python function.
        
        Args:
            func: The function to wrap
            name: Tool name (defaults to function name)
            description: Tool description (defaults to docstring)
            category: Tool category
            tags: Optional tags
            
        Returns:
            FunctionTool instance
        """
        tool_name = name or func.__name__
        tool_desc = description or (func.__doc__ or f"Execute {tool_name}")
        
        metadata = ToolMetadata(
            tool_id=f"func_{uuid.uuid4().hex[:12]}",
            name=tool_name,
            description=tool_desc.strip(),
            tool_type=ToolType.FUNCTION,
            category=category or ToolCategory.UTILITY,
            source=f"function:{func.__module__}.{func.__name__}",
            tags=tags or []
        )
        
        return cls(func, metadata)


def tool(name: str = None, description: str = None, 
         category: ToolCategory = None, tags: List[str] = None):
    """
    Decorator to convert a function to a FunctionTool.
    
    Example:
        @tool(name="search", description="Search for items")
        def search_items(query: str, limit: int = 10) -> str:
            return f"Results for {query}"
    """
    def decorator(func: Callable) -> FunctionTool:
        return FunctionTool.from_function(
            func, name=name, description=description,
            category=category, tags=tags
        )
    return decorator


class AsyncFunctionTool(FunctionTool):
    """
    Tool that wraps an async Python function.
    """
    
    def __init__(self, func: Callable, metadata: ToolMetadata,
                 schema: ToolSchema = None):
        metadata.is_async = True
        super().__init__(func, metadata, schema)
    
    def execute(self, **kwargs) -> ToolResult:
        """Execute sync (runs async in event loop)."""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Create a new loop in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run, self._func(**kwargs)
                    )
                    result = future.result()
            else:
                result = loop.run_until_complete(self._func(**kwargs))
            
            return ToolResult.success_result(result)
        except Exception as e:
            logger.error(f"AsyncFunctionTool {self.name} error: {e}")
            return ToolResult.error_result(str(e))
    
    async def async_execute(self, **kwargs) -> ToolResult:
        """Execute the async function directly."""
        try:
            result = await self._func(**kwargs)
            return ToolResult.success_result(result)
        except Exception as e:
            logger.error(f"AsyncFunctionTool {self.name} error: {e}")
            return ToolResult.error_result(str(e))
    
    @classmethod
    def from_async_function(cls, func: Callable, name: str = None,
                           description: str = None, 
                           category: ToolCategory = None,
                           tags: List[str] = None) -> 'AsyncFunctionTool':
        """Create from async function."""
        tool_name = name or func.__name__
        tool_desc = description or (func.__doc__ or f"Execute {tool_name}")
        
        metadata = ToolMetadata(
            tool_id=f"async_{uuid.uuid4().hex[:12]}",
            name=tool_name,
            description=tool_desc.strip(),
            tool_type=ToolType.FUNCTION,
            category=category or ToolCategory.UTILITY,
            source=f"async:{func.__module__}.{func.__name__}",
            tags=tags or [],
            is_async=True
        )
        
        return cls(func, metadata)


def async_tool(name: str = None, description: str = None,
               category: ToolCategory = None, tags: List[str] = None):
    """Decorator for async functions."""
    def decorator(func: Callable) -> AsyncFunctionTool:
        return AsyncFunctionTool.from_async_function(
            func, name=name, description=description,
            category=category, tags=tags
        )
    return decorator
