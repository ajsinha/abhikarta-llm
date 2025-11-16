"""
Abhikarta LLM - Tool Management Framework
Base Tool Abstract Class

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

This module defines the base abstract class that all tools must inherit from.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, AsyncIterator
import asyncio
import time
from datetime import datetime

from .types import ToolType, ExecutionMode, ToolStatus
from .parameters import ParameterSet, ToolParameter
from .results import ToolResult, ResultStatus
from .exceptions import ParameterValidationError, ToolExecutionError


class BaseTool(ABC):
    """
    Abstract base class for all tools in the Abhikarta framework.
    
    All tools must inherit from this class and implement the execute() method.
    This provides a standardized interface for tool registration, execution,
    and management.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        tool_type: ToolType,
        execution_mode: ExecutionMode = ExecutionMode.SYNC,
        version: str = "1.0.0"
    ):
        """
        Initialize a base tool.
        
        Args:
            name: Unique identifier for the tool
            description: Human-readable description of tool functionality
            tool_type: Category/type of the tool
            execution_mode: How the tool executes (sync/async/streaming)
            version: Tool version string
        """
        self.name = name
        self.description = description
        self.tool_type = tool_type
        self.execution_mode = execution_mode
        self.version = version
        
        # Parameter management
        self._parameters = ParameterSet()
        
        # Status and metadata
        self._status = ToolStatus.ENABLED
        self._metadata: Dict[str, Any] = {}
        self._tags: set[str] = set()
        
        # Performance tracking
        self._execution_count = 0
        self._total_execution_time = 0.0
        self._last_executed: Optional[datetime] = None
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with given parameters.
        
        This method must be implemented by all concrete tool classes.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            ToolResult containing execution results
        """
        pass
    
    async def execute_async(self, **kwargs) -> ToolResult:
        """
        Execute the tool asynchronously.
        
        Default implementation wraps synchronous execution in an executor.
        Override this for true async implementation.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            ToolResult containing execution results
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.execute(**kwargs))
    
    async def stream_execute(self, **kwargs) -> AsyncIterator[Any]:
        """
        Execute the tool with streaming results.
        
        Override this for tools that support streaming execution.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Yields:
            Incremental results
            
        Raises:
            NotImplementedError: If streaming is not supported
        """
        raise NotImplementedError(
            f"Streaming execution not supported for tool '{self.name}'"
        )
    
    def _execute_with_tracking(self, **kwargs) -> ToolResult:
        """
        Internal method that wraps execution with tracking.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            ToolResult with tracking metadata
        """
        start_time = time.time()
        self._execution_count += 1
        self._last_executed = datetime.utcnow()
        
        try:
            # Validate parameters
            validated_params = self._parameters.validate_values(**kwargs)
            
            # Execute tool
            result = self.execute(**validated_params)
            
            # Add tracking information
            execution_time = time.time() - start_time
            self._total_execution_time += execution_time
            result.execution_time = execution_time
            result.tool_name = self.name
            
            return result
            
        except ParameterValidationError as e:
            execution_time = time.time() - start_time
            return ToolResult.failure_result(
                error=str(e),
                error_type="ParameterValidationError",
                tool_name=self.name,
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return ToolResult.failure_result(
                error=str(e),
                error_type=type(e).__name__,
                tool_name=self.name,
                execution_time=execution_time
            )
    
    async def _execute_async_with_tracking(self, **kwargs) -> ToolResult:
        """Async version of execute with tracking"""
        start_time = time.time()
        self._execution_count += 1
        self._last_executed = datetime.utcnow()
        
        try:
            validated_params = self._parameters.validate_values(**kwargs)
            result = await self.execute_async(**validated_params)
            
            execution_time = time.time() - start_time
            self._total_execution_time += execution_time
            result.execution_time = execution_time
            result.tool_name = self.name
            
            return result
            
        except ParameterValidationError as e:
            execution_time = time.time() - start_time
            return ToolResult.failure_result(
                error=str(e),
                error_type="ParameterValidationError",
                tool_name=self.name,
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return ToolResult.failure_result(
                error=str(e),
                error_type=type(e).__name__,
                tool_name=self.name,
                execution_time=execution_time
            )
    
    def add_parameter(self, parameter: ToolParameter) -> 'BaseTool':
        """
        Add a parameter to this tool.
        
        Args:
            parameter: ToolParameter to add
            
        Returns:
            Self for method chaining
        """
        self._parameters.add(parameter)
        return self
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the complete tool schema for LLM consumption.
        
        Returns:
            Dictionary containing tool schema in standard format
        """
        schema = {
            "name": self.name,
            "description": self.description,
            "type": self.tool_type.value,
            "execution_mode": self.execution_mode.value,
            "version": self.version,
            "status": self._status.value,
            "parameters": self._parameters.to_json_schema()
        }
        
        if self._tags:
            schema["tags"] = list(self._tags)
        if self._metadata:
            schema["metadata"] = self._metadata
        
        return schema
    
    def get_anthropic_schema(self) -> Dict[str, Any]:
        """
        Get schema in Anthropic's tool format.
        
        Returns:
            Dictionary compatible with Anthropic API
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self._parameters.to_json_schema()
        }
    
    def get_openai_schema(self) -> Dict[str, Any]:
        """
        Get schema in OpenAI's function calling format.
        
        Returns:
            Dictionary compatible with OpenAI API
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self._parameters.to_json_schema()
            }
        }
    
    # Status management
    @property
    def enabled(self) -> bool:
        """Check if tool is enabled"""
        return self._status == ToolStatus.ENABLED
    
    @property
    def status(self) -> ToolStatus:
        """Get current tool status"""
        return self._status
    
    def enable(self) -> 'BaseTool':
        """Enable the tool"""
        self._status = ToolStatus.ENABLED
        return self
    
    def disable(self) -> 'BaseTool':
        """Disable the tool"""
        self._status = ToolStatus.DISABLED
        return self
    
    def set_maintenance(self) -> 'BaseTool':
        """Set tool to maintenance mode"""
        self._status = ToolStatus.MAINTENANCE
        return self
    
    def deprecate(self) -> 'BaseTool':
        """Mark tool as deprecated"""
        self._status = ToolStatus.DEPRECATED
        return self
    
    # Metadata management
    def set_metadata(self, key: str, value: Any) -> 'BaseTool':
        """Set a metadata value"""
        self._metadata[key] = value
        return self
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get a metadata value"""
        return self._metadata.get(key, default)
    
    def add_tag(self, tag: str) -> 'BaseTool':
        """Add a tag to the tool"""
        self._tags.add(tag)
        return self
    
    def remove_tag(self, tag: str) -> 'BaseTool':
        """Remove a tag from the tool"""
        self._tags.discard(tag)
        return self
    
    def has_tag(self, tag: str) -> bool:
        """Check if tool has a specific tag"""
        return tag in self._tags
    
    # Performance metrics
    def get_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics for this tool.
        
        Returns:
            Dictionary containing execution metrics
        """
        avg_time = (
            self._total_execution_time / self._execution_count
            if self._execution_count > 0
            else 0.0
        )
        
        return {
            "execution_count": self._execution_count,
            "total_execution_time": self._total_execution_time,
            "average_execution_time": avg_time,
            "last_executed": self._last_executed.isoformat() if self._last_executed else None
        }
    
    def reset_stats(self) -> 'BaseTool':
        """Reset execution statistics"""
        self._execution_count = 0
        self._total_execution_time = 0.0
        self._last_executed = None
        return self
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.name}' type={self.tool_type.value}>"
