"""
LangChain Tool - Tool wrapper for LangChain tools.

Allows using any LangChain tool as a BaseTool and vice versa.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import logging
import uuid
from typing import Dict, Any, Optional, List, Union

from .base_tool import (
    BaseTool, ToolMetadata, ToolSchema, ToolParameter,
    ToolResult, ToolType, ToolCategory
)

logger = logging.getLogger(__name__)


class LangChainToolWrapper(BaseTool):
    """
    Wrapper that converts a LangChain tool to a BaseTool.
    
    This allows integration of any existing LangChain tool
    into the Abhikarta tools system.
    
    Example:
        from langchain_community.tools import WikipediaQueryRun
        lc_tool = WikipediaQueryRun()
        wrapped = LangChainToolWrapper.from_langchain_tool(lc_tool)
    """
    
    def __init__(self, metadata: ToolMetadata, schema: ToolSchema,
                 langchain_tool: Any):
        """
        Initialize LangChainToolWrapper.
        
        Args:
            metadata: Tool metadata
            schema: Parameter schema
            langchain_tool: The LangChain tool instance
        """
        super().__init__(metadata)
        self._schema = schema
        self._lc_tool = langchain_tool
    
    @property
    def langchain_tool(self) -> Any:
        """Get the underlying LangChain tool."""
        return self._lc_tool
    
    def execute(self, **kwargs) -> ToolResult:
        """Execute the LangChain tool."""
        import time
        start_time = time.time()
        
        try:
            # LangChain tools can be invoked different ways
            if hasattr(self._lc_tool, 'invoke'):
                # New style
                if len(kwargs) == 1 and 'input' in kwargs:
                    result = self._lc_tool.invoke(kwargs['input'])
                else:
                    result = self._lc_tool.invoke(kwargs)
            elif hasattr(self._lc_tool, 'run'):
                # Old style
                if len(kwargs) == 1:
                    key = list(kwargs.keys())[0]
                    result = self._lc_tool.run(kwargs[key])
                else:
                    result = self._lc_tool.run(kwargs)
            elif callable(self._lc_tool):
                result = self._lc_tool(**kwargs)
            else:
                return ToolResult.error_result("Tool is not callable")
            
            execution_time = (time.time() - start_time) * 1000
            return ToolResult.success_result(result, execution_time)
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"LangChainToolWrapper {self.name} error: {e}")
            return ToolResult.error_result(str(e), execution_time)
    
    def get_schema(self) -> ToolSchema:
        """Get the parameter schema."""
        return self._schema
    
    @classmethod
    def from_langchain_tool(cls, lc_tool: Any, 
                           category: ToolCategory = None,
                           tags: List[str] = None) -> 'LangChainToolWrapper':
        """
        Create wrapper from LangChain tool.
        
        Args:
            lc_tool: LangChain tool instance
            category: Tool category
            tags: Tool tags
            
        Returns:
            LangChainToolWrapper instance
        """
        # Extract name and description
        name = getattr(lc_tool, 'name', lc_tool.__class__.__name__)
        description = getattr(lc_tool, 'description', f"LangChain tool: {name}")
        
        # Extract schema
        schema_params = []
        
        if hasattr(lc_tool, 'args_schema'):
            # Has Pydantic schema
            args_schema = lc_tool.args_schema
            if hasattr(args_schema, 'schema'):
                json_schema = args_schema.schema()
                for field_name, field_info in json_schema.get('properties', {}).items():
                    required = field_name in json_schema.get('required', [])
                    schema_params.append(ToolParameter(
                        name=field_name,
                        param_type=field_info.get('type', 'string'),
                        description=field_info.get('description', ''),
                        required=required,
                        default=field_info.get('default')
                    ))
        else:
            # Default to single input parameter
            schema_params.append(ToolParameter(
                name='input',
                param_type='string',
                description='Input to the tool',
                required=True
            ))
        
        schema = ToolSchema(parameters=schema_params)
        
        metadata = ToolMetadata(
            tool_id=f"lc_{uuid.uuid4().hex[:12]}",
            name=name,
            description=description,
            tool_type=ToolType.LANGCHAIN,
            category=category or ToolCategory.UTILITY,
            source=f"langchain:{lc_tool.__class__.__module__}.{lc_tool.__class__.__name__}",
            tags=['langchain'] + (tags or [])
        )
        
        return cls(
            metadata=metadata,
            schema=schema,
            langchain_tool=lc_tool
        )


class AsyncLangChainToolWrapper(LangChainToolWrapper):
    """
    Async wrapper for LangChain tools that support async.
    """
    
    def __init__(self, metadata: ToolMetadata, schema: ToolSchema,
                 langchain_tool: Any):
        metadata.is_async = True
        super().__init__(metadata, schema, langchain_tool)
    
    async def async_execute(self, **kwargs) -> ToolResult:
        """Execute the LangChain tool asynchronously."""
        import time
        start_time = time.time()
        
        try:
            if hasattr(self._lc_tool, 'ainvoke'):
                if len(kwargs) == 1 and 'input' in kwargs:
                    result = await self._lc_tool.ainvoke(kwargs['input'])
                else:
                    result = await self._lc_tool.ainvoke(kwargs)
            elif hasattr(self._lc_tool, 'arun'):
                if len(kwargs) == 1:
                    key = list(kwargs.keys())[0]
                    result = await self._lc_tool.arun(kwargs[key])
                else:
                    result = await self._lc_tool.arun(kwargs)
            else:
                # Fallback to sync
                return await super().async_execute(**kwargs)
            
            execution_time = (time.time() - start_time) * 1000
            return ToolResult.success_result(result, execution_time)
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"AsyncLangChainToolWrapper {self.name} error: {e}")
            return ToolResult.error_result(str(e), execution_time)


def wrap_langchain_tools(tools: List[Any]) -> List[LangChainToolWrapper]:
    """
    Wrap multiple LangChain tools.
    
    Args:
        tools: List of LangChain tools
        
    Returns:
        List of wrapped tools
    """
    wrapped = []
    for tool in tools:
        try:
            if hasattr(tool, 'ainvoke') or hasattr(tool, 'arun'):
                wrapped.append(AsyncLangChainToolWrapper.from_langchain_tool(tool))
            else:
                wrapped.append(LangChainToolWrapper.from_langchain_tool(tool))
        except Exception as e:
            logger.error(f"Failed to wrap LangChain tool {tool}: {e}")
    return wrapped


def create_langchain_tools(base_tools: List[BaseTool]) -> List[Any]:
    """
    Convert BaseTools to LangChain tools.
    
    Args:
        base_tools: List of BaseTool instances
        
    Returns:
        List of LangChain StructuredTool instances
    """
    lc_tools = []
    for tool in base_tools:
        try:
            lc_tool = tool.to_langchain_tool()
            if lc_tool:
                lc_tools.append(lc_tool)
        except Exception as e:
            logger.error(f"Failed to convert {tool.name} to LangChain: {e}")
    return lc_tools
