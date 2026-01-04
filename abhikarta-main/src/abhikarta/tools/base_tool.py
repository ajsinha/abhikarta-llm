"""
Base Tool - Abstract base class for all tools in Abhikarta.

All tools must extend BaseTool to be usable by agents, workflows, and other components.
This ensures a consistent interface for tool discovery, validation, and execution.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import logging
import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List, Callable, Union
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ToolType(Enum):
    """Types of tools supported by the system."""
    FUNCTION = "function"           # Python function-based tool
    MCP = "mcp"                     # Model Context Protocol tool
    CODE_FRAGMENT = "code_fragment" # Code fragment from database
    HTTP = "http"                   # HTTP/REST API tool
    LANGCHAIN = "langchain"         # LangChain wrapped tool
    PLUGIN = "plugin"               # Plugin-based tool
    CUSTOM = "custom"               # Custom implementation


class ToolCategory(Enum):
    """Categories for organizing tools."""
    UTILITY = "utility"
    DATA = "data"
    AI = "ai"
    INTEGRATION = "integration"
    FILE = "file"
    COMMUNICATION = "communication"
    SEARCH = "search"
    DATABASE = "database"
    CUSTOM = "custom"


@dataclass
class ToolParameter:
    """Definition of a tool parameter."""
    name: str
    param_type: str  # string, integer, number, boolean, array, object
    description: str = ""
    required: bool = True
    default: Any = None
    enum: List[Any] = None
    
    def to_json_schema(self) -> Dict[str, Any]:
        """Convert to JSON Schema format."""
        schema = {
            "type": self.param_type,
            "description": self.description
        }
        if self.enum:
            schema["enum"] = self.enum
        if self.default is not None:
            schema["default"] = self.default
        return schema


@dataclass
class ToolSchema:
    """Schema definition for a tool's input parameters."""
    parameters: List[ToolParameter] = field(default_factory=list)
    
    def to_json_schema(self) -> Dict[str, Any]:
        """Convert to JSON Schema format for tool calling."""
        properties = {}
        required = []
        
        for param in self.parameters:
            properties[param.name] = param.to_json_schema()
            if param.required:
                required.append(param.name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }
    
    @classmethod
    def from_json_schema(cls, schema: Dict[str, Any]) -> 'ToolSchema':
        """Create ToolSchema from JSON Schema."""
        parameters = []
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        for name, prop in properties.items():
            param = ToolParameter(
                name=name,
                param_type=prop.get("type", "string"),
                description=prop.get("description", ""),
                required=name in required,
                default=prop.get("default"),
                enum=prop.get("enum")
            )
            parameters.append(param)
        
        return cls(parameters=parameters)


@dataclass
class ToolResult:
    """Result of a tool execution."""
    success: bool
    output: Any = None
    error: str = None
    execution_time_ms: float = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def success_result(cls, output: Any, execution_time_ms: float = 0,
                      metadata: Dict = None) -> 'ToolResult':
        """Create a successful result."""
        return cls(
            success=True,
            output=output,
            execution_time_ms=execution_time_ms,
            metadata=metadata or {}
        )
    
    @classmethod
    def error_result(cls, error: str, execution_time_ms: float = 0,
                    metadata: Dict = None) -> 'ToolResult':
        """Create an error result."""
        return cls(
            success=False,
            error=error,
            execution_time_ms=execution_time_ms,
            metadata=metadata or {}
        )


@dataclass
class ToolMetadata:
    """Metadata about a tool."""
    tool_id: str
    name: str
    description: str
    tool_type: ToolType
    category: ToolCategory = ToolCategory.UTILITY
    version: str = "1.0.0"
    author: str = ""
    source: str = ""  # e.g., "mcp:server_name", "plugin:plugin_id"
    tags: List[str] = field(default_factory=list)
    is_async: bool = False
    requires_auth: bool = False
    rate_limit: int = 0  # calls per minute, 0 = unlimited
    timeout_seconds: int = 30
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['tool_type'] = self.tool_type.value
        data['category'] = self.category.value
        return data


class BaseTool(ABC):
    """
    Abstract base class for all tools in Abhikarta.
    
    All tools must extend this class to be compatible with:
    - ToolsRegistry for centralized management
    - Agent execution
    - Workflow execution
    - LangChain integration
    
    Subclasses must implement:
    - execute() method for tool execution
    - get_schema() to return input parameter schema
    """
    
    def __init__(self, metadata: ToolMetadata):
        """
        Initialize the tool with metadata.
        
        Args:
            metadata: ToolMetadata instance describing the tool
        """
        self._metadata = metadata
        self._execution_count = 0
        self._last_execution = None
        self._enabled = True
    
    @property
    def tool_id(self) -> str:
        """Unique identifier for this tool."""
        return self._metadata.tool_id
    
    @property
    def name(self) -> str:
        """Human-readable name of the tool."""
        return self._metadata.name
    
    @property
    def description(self) -> str:
        """Description of what the tool does."""
        return self._metadata.description
    
    @property
    def tool_type(self) -> ToolType:
        """Type of the tool."""
        return self._metadata.tool_type
    
    @property
    def category(self) -> ToolCategory:
        """Category of the tool."""
        return self._metadata.category
    
    @property
    def metadata(self) -> ToolMetadata:
        """Full metadata of the tool."""
        return self._metadata
    
    @property
    def is_enabled(self) -> bool:
        """Whether the tool is enabled."""
        return self._enabled
    
    def enable(self):
        """Enable the tool."""
        self._enabled = True
    
    def disable(self):
        """Disable the tool."""
        self._enabled = False
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with the given parameters.
        
        Args:
            **kwargs: Tool-specific parameters matching the schema
            
        Returns:
            ToolResult containing the execution outcome
        """
        pass
    
    @abstractmethod
    def get_schema(self) -> ToolSchema:
        """
        Get the parameter schema for this tool.
        
        Returns:
            ToolSchema describing required and optional parameters
        """
        pass
    
    def validate_input(self, **kwargs) -> tuple[bool, str]:
        """
        Validate input against the tool's schema.
        
        Args:
            **kwargs: Input parameters to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        schema = self.get_schema()
        
        for param in schema.parameters:
            if param.required and param.name not in kwargs:
                return False, f"Missing required parameter: {param.name}"
            
            if param.name in kwargs and kwargs[param.name] is not None:
                value = kwargs[param.name]
                
                # Type validation
                type_map = {
                    "string": str,
                    "integer": int,
                    "number": (int, float),
                    "boolean": bool,
                    "array": list,
                    "object": dict
                }
                
                expected_type = type_map.get(param.param_type)
                if expected_type and not isinstance(value, expected_type):
                    return False, f"Parameter {param.name} must be of type {param.param_type}"
                
                # Enum validation
                if param.enum and value not in param.enum:
                    return False, f"Parameter {param.name} must be one of {param.enum}"
        
        return True, ""
    
    def safe_execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with validation and error handling.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            ToolResult with execution outcome
        """
        if not self._enabled:
            return ToolResult.error_result("Tool is disabled")
        
        # Validate input
        is_valid, error = self.validate_input(**kwargs)
        if not is_valid:
            return ToolResult.error_result(f"Validation error: {error}")
        
        # Execute with timing
        import time
        start_time = time.time()
        
        try:
            result = self.execute(**kwargs)
            
            # Update statistics
            self._execution_count += 1
            self._last_execution = datetime.utcnow().isoformat()
            
            # Ensure result has execution time
            if result.execution_time_ms == 0:
                result.execution_time_ms = (time.time() - start_time) * 1000
            
            return result
            
        except Exception as e:
            logger.error(f"Tool {self.name} execution error: {e}")
            execution_time = (time.time() - start_time) * 1000
            return ToolResult.error_result(str(e), execution_time)
    
    async def async_execute(self, **kwargs) -> ToolResult:
        """
        Async version of execute. Override for async tools.
        
        Default implementation wraps sync execute.
        """
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.safe_execute(**kwargs))
    
    def to_openai_function(self) -> Dict[str, Any]:
        """
        Convert to OpenAI function calling format.
        
        Returns:
            Dict in OpenAI function format
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.get_schema().to_json_schema()
            }
        }
    
    def to_anthropic_tool(self) -> Dict[str, Any]:
        """
        Convert to Anthropic tool calling format.
        
        Returns:
            Dict in Anthropic tool format
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.get_schema().to_json_schema()
        }
    
    def to_langchain_tool(self):
        """
        Convert to LangChain StructuredTool.
        
        Returns:
            LangChain StructuredTool instance
        """
        try:
            from langchain_core.tools import StructuredTool
            from pydantic import create_model, Field
            
            # Build Pydantic model from schema
            schema = self.get_schema()
            field_definitions = {}
            
            for param in schema.parameters:
                python_type = {
                    "string": str,
                    "integer": int,
                    "number": float,
                    "boolean": bool,
                    "array": list,
                    "object": dict
                }.get(param.param_type, str)
                
                if param.required:
                    field_definitions[param.name] = (
                        python_type,
                        Field(description=param.description)
                    )
                else:
                    field_definitions[param.name] = (
                        Optional[python_type],
                        Field(default=param.default, description=param.description)
                    )
            
            InputModel = create_model(f"{self.name}Input", **field_definitions)
            
            def _run(**kwargs):
                result = self.safe_execute(**kwargs)
                if result.success:
                    return result.output
                else:
                    raise Exception(result.error)
            
            return StructuredTool(
                name=self.name,
                description=self.description,
                func=_run,
                args_schema=InputModel
            )
            
        except ImportError:
            logger.warning("LangChain not installed, cannot convert to LangChain tool")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return {
            "execution_count": self._execution_count,
            "last_execution": self._last_execution,
            "enabled": self._enabled
        }
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', type={self.tool_type.value})>"
