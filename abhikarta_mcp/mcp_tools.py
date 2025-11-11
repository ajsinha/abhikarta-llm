"""
MCP Tool Integration System

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

This module provides a generic system for converting MCP (Model Context Protocol)
endpoint schemas into LLM tool definitions and handling their execution.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, Union
import json
import logging
from dataclasses import dataclass, field
from enum import Enum


class MCPToolStatus(Enum):
    """Tool execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class MCPToolResult:
    """Result from MCP tool execution."""
    status: MCPToolStatus
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "data": self.data,
            "error": self.error,
            "execution_time": self.execution_time,
            "metadata": self.metadata
        }
    
    def is_success(self) -> bool:
        """Check if execution was successful."""
        return self.status == MCPToolStatus.SUCCESS


class BaseMCPTool(ABC):
    """
    Abstract base class for MCP tools.
    
    Defines the interface that all MCP tools must implement.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize base MCP tool.
        
        Args:
            name: Tool name (must be unique)
            description: Human-readable description
            input_schema: JSON schema for input parameters
            metadata: Optional metadata about the tool
        """
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.metadata = metadata or {}
        self.logger = logging.getLogger(f"MCPTool.{name}")
    
    @abstractmethod
    def execute(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """
        Execute the tool with given arguments.
        
        Args:
            arguments: Validated arguments for the tool
        
        Returns:
            MCPToolResult with execution results
        """
        pass
    
    def to_llm_tool_definition(self) -> Dict[str, Any]:
        """
        Convert to LLM tool definition format.
        
        Returns:
            Tool definition in LLM-compatible format
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema
            }
        }
    
    def validate_arguments(self, arguments: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate arguments against input schema.
        
        Args:
            arguments: Arguments to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check required fields
            required_fields = self.input_schema.get("required", [])
            for field in required_fields:
                if field not in arguments:
                    return False, f"Missing required field: {field}"
            
            # Check field types
            properties = self.input_schema.get("properties", {})
            for key, value in arguments.items():
                if key in properties:
                    expected_type = properties[key].get("type")
                    if not self._check_type(value, expected_type):
                        return False, f"Invalid type for {key}: expected {expected_type}"
            
            return True, None
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected JSON schema type."""
        type_mapping = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None)
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type is None:
            return True  # Unknown type, skip validation
        
        return isinstance(value, expected_python_type)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"


class MCPTool(BaseMCPTool):
    """
    Concrete implementation of MCP tool.
    
    Wraps an MCP endpoint and provides execution capabilities.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        executor: Callable[[Dict[str, Any]], Any],
        metadata: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        retry_count: int = 0
    ):
        """
        Initialize MCP tool.
        
        Args:
            name: Tool name
            description: Tool description
            input_schema: JSON schema for inputs
            executor: Callable that executes the tool (receives validated arguments)
            metadata: Optional metadata
            timeout: Optional timeout in seconds
            retry_count: Number of retries on failure
        """
        super().__init__(name, description, input_schema, metadata)
        self.executor = executor
        self.timeout = timeout
        self.retry_count = retry_count
    
    def execute(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """
        Execute the tool with given arguments.
        
        Args:
            arguments: Arguments for the tool
        
        Returns:
            MCPToolResult with execution results
        """
        import time
        
        start_time = time.time()
        
        # Validate arguments
        is_valid, error_msg = self.validate_arguments(arguments)
        if not is_valid:
            return MCPToolResult(
                status=MCPToolStatus.FAILED,
                error=f"Validation failed: {error_msg}",
                execution_time=time.time() - start_time
            )
        
        # Execute with retries
        attempts = 0
        max_attempts = self.retry_count + 1
        last_error = None
        
        while attempts < max_attempts:
            try:
                self.logger.info(f"Executing tool '{self.name}' (attempt {attempts + 1}/{max_attempts})")
                
                # Execute the tool
                if self.timeout:
                    # TODO: Implement timeout mechanism
                    result = self.executor(arguments)
                else:
                    result = self.executor(arguments)
                
                execution_time = time.time() - start_time
                
                return MCPToolResult(
                    status=MCPToolStatus.SUCCESS,
                    data=result,
                    execution_time=execution_time,
                    metadata={"attempts": attempts + 1}
                )
                
            except Exception as e:
                last_error = str(e)
                attempts += 1
                self.logger.error(f"Tool execution failed (attempt {attempts}): {e}")
                
                if attempts >= max_attempts:
                    break
        
        # All attempts failed
        execution_time = time.time() - start_time
        return MCPToolResult(
            status=MCPToolStatus.FAILED,
            error=f"Execution failed after {attempts} attempts: {last_error}",
            execution_time=execution_time,
            metadata={"attempts": attempts}
        )


class MCPToolFactory:
    """
    Factory for creating MCP tools from schemas.
    
    Converts MCP endpoint schemas into MCPTool instances.
    """
    
    def __init__(self, executor_registry: Optional[Dict[str, Callable]] = None):
        """
        Initialize tool factory.
        
        Args:
            executor_registry: Optional mapping of tool names to executor functions
        """
        self.executor_registry = executor_registry or {}
        self.logger = logging.getLogger("MCPToolFactory")
    
    def create_tool_from_mcp_schema(
        self,
        mcp_schema: Dict[str, Any],
        executor: Optional[Callable] = None
    ) -> MCPTool:
        """
        Create a tool from an MCP endpoint schema.
        
        Args:
            mcp_schema: MCP endpoint schema containing:
                - name: Tool name
                - description: Tool description
                - inputSchema: JSON schema for parameters
            executor: Optional custom executor function
        
        Returns:
            MCPTool instance
        
        Example MCP schema:
            {
                "name": "get_weather",
                "description": "Get current weather for a location",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "City name"},
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                    },
                    "required": ["location"]
                }
            }
        """
        # Extract fields from MCP schema
        name = mcp_schema.get("name")
        description = mcp_schema.get("description", "")
        input_schema = mcp_schema.get("inputSchema", {})
        
        if not name:
            raise ValueError("MCP schema must have 'name' field")
        
        # Get executor
        if executor is None:
            executor = self.executor_registry.get(name)
        
        if executor is None:
            # Create a default executor that raises NotImplementedError
            def default_executor(args):
                raise NotImplementedError(f"No executor provided for tool '{name}'")
            executor = default_executor
        
        # Extract metadata
        metadata = {
            "mcp_schema": mcp_schema,
            "created_from": "mcp_endpoint"
        }
        
        # Create and return tool
        return MCPTool(
            name=name,
            description=description,
            input_schema=input_schema,
            executor=executor,
            metadata=metadata
        )
    
    def create_tools_from_mcp_schemas(
        self,
        mcp_schemas: List[Dict[str, Any]]
    ) -> List[MCPTool]:
        """
        Create multiple tools from a list of MCP schemas.
        
        Args:
            mcp_schemas: List of MCP endpoint schemas
        
        Returns:
            List of MCPTool instances
        """
        tools = []
        for schema in mcp_schemas:
            try:
                tool = self.create_tool_from_mcp_schema(schema)
                tools.append(tool)
                self.logger.info(f"Created tool: {tool.name}")
            except Exception as e:
                self.logger.error(f"Failed to create tool from schema: {e}")
        
        return tools
    
    def register_executor(self, tool_name: str, executor: Callable):
        """
        Register an executor function for a tool.
        
        Args:
            tool_name: Name of the tool
            executor: Function that executes the tool
        """
        self.executor_registry[tool_name] = executor
        self.logger.info(f"Registered executor for tool: {tool_name}")
    
    def create_llm_tool_definitions(
        self,
        mcp_schemas: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Convert MCP schemas directly to LLM tool definitions.
        
        Args:
            mcp_schemas: List of MCP endpoint schemas
        
        Returns:
            List of LLM tool definitions
        """
        tool_definitions = []
        
        for schema in mcp_schemas:
            try:
                tool_def = {
                    "type": "function",
                    "function": {
                        "name": schema.get("name"),
                        "description": schema.get("description", ""),
                        "parameters": schema.get("inputSchema", {})
                    }
                }
                tool_definitions.append(tool_def)
            except Exception as e:
                self.logger.error(f"Failed to convert schema to tool definition: {e}")
        
        return tool_definitions


class MCPToolRegistry:
    """
    Registry for managing multiple MCP tools.
    
    Provides lookup, execution, and management of tools.
    """
    
    def __init__(self):
        """Initialize tool registry."""
        self.tools: Dict[str, MCPTool] = {}
        self.logger = logging.getLogger("MCPToolRegistry")
    
    def register(self, tool: MCPTool):
        """
        Register a tool.
        
        Args:
            tool: MCPTool to register
        """
        if tool.name in self.tools:
            self.logger.warning(f"Overwriting existing tool: {tool.name}")
        
        self.tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")
    
    def register_multiple(self, tools: List[MCPTool]):
        """Register multiple tools."""
        for tool in tools:
            self.register(tool)
    
    def get(self, name: str) -> Optional[MCPTool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def execute(self, name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """
        Execute a tool by name.
        
        Args:
            name: Tool name
            arguments: Tool arguments
        
        Returns:
            MCPToolResult
        """
        tool = self.get(name)
        if tool is None:
            return MCPToolResult(
                status=MCPToolStatus.FAILED,
                error=f"Tool not found: {name}"
            )
        
        return tool.execute(arguments)
    
    def get_all_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get LLM tool definitions for all registered tools."""
        return [tool.to_llm_tool_definition() for tool in self.tools.values()]
    
    def list_tools(self) -> List[str]:
        """Get list of registered tool names."""
        return list(self.tools.keys())
    
    def __len__(self) -> int:
        return len(self.tools)
    
    def __contains__(self, name: str) -> bool:
        return name in self.tools


# Convenience functions

def create_tool_from_mcp(
    mcp_schema: Dict[str, Any],
    executor: Callable[[Dict[str, Any]], Any]
) -> MCPTool:
    """
    Convenience function to create a tool from MCP schema.
    
    Args:
        mcp_schema: MCP endpoint schema
        executor: Function to execute the tool
    
    Returns:
        MCPTool instance
    """
    factory = MCPToolFactory()
    return factory.create_tool_from_mcp_schema(mcp_schema, executor)


def mcp_schemas_to_llm_tools(
    mcp_schemas: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Convert MCP schemas directly to LLM tool definitions.
    
    Args:
        mcp_schemas: List of MCP endpoint schemas
    
    Returns:
        List of LLM-compatible tool definitions
    """
    factory = MCPToolFactory()
    return factory.create_llm_tool_definitions(mcp_schemas)


__all__ = [
    'BaseMCPTool',
    'MCPTool',
    'MCPToolFactory',
    'MCPToolRegistry',
    'MCPToolResult',
    'MCPToolStatus',
    'create_tool_from_mcp',
    'mcp_schemas_to_llm_tools'
]
