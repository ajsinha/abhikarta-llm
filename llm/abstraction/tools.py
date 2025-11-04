"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.4

Tool System for Function Calling
"""

from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field


class ToolParameterType(Enum):
    """Parameter types for tools"""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


@dataclass
class ToolParameter:
    """
    Parameter definition for a tool.
    
    Attributes:
        name: Parameter name
        type: Parameter type
        description: Parameter description
        required: Whether parameter is required
        enum: Optional list of allowed values
    """
    name: str
    type: ToolParameterType
    description: str
    required: bool = True
    enum: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        result = {
            "type": self.type.value,
            "description": self.description
        }
        if self.enum:
            result["enum"] = self.enum
        return result


@dataclass
class Tool:
    """
    Tool definition for function calling.
    
    Attributes:
        name: Tool name
        description: Tool description
        function: The callable function
        parameters: List of parameters
    """
    name: str
    description: str
    function: Callable
    parameters: List[ToolParameter] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        param.name: param.to_dict()
                        for param in self.parameters
                    },
                    "required": [
                        param.name
                        for param in self.parameters
                        if param.required
                    ]
                }
            }
        }
    
    def execute(self, **kwargs) -> Any:
        """Execute the tool with given arguments"""
        return self.function(**kwargs)


class ToolRegistry:
    """
    Registry for managing tools.
    
    Example:
        registry = ToolRegistry()
        registry.register(Tool(
            name="get_weather",
            description="Get weather info",
            function=get_weather_func,
            parameters=[
                ToolParameter("location", ToolParameterType.STRING, "City name")
            ]
        ))
    """
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool):
        """Register a tool"""
        self.tools[tool.name] = tool
    
    def unregister(self, name: str):
        """Unregister a tool by name"""
        if name in self.tools:
            del self.tools[name]
    
    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self.tools.keys())
    
    def get_all_tools(self) -> List[Tool]:
        """Get all registered tools"""
        return list(self.tools.values())
    
    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Convert all tools to dictionary format"""
        return [tool.to_dict() for tool in self.tools.values()]
    
    def execute(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool by name"""
        tool = self.get(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        return tool.execute(**kwargs)


def create_tool(
    name: str,
    description: str,
    function: Callable,
    parameters: Optional[List[ToolParameter]] = None
) -> Tool:
    """
    Helper function to create a tool.
    
    Args:
        name: Tool name
        description: Tool description
        function: The callable function
        parameters: Optional list of parameters
    
    Returns:
        Tool instance
    
    Example:
        tool = create_tool(
            "get_weather",
            "Get weather information",
            get_weather_func,
            [ToolParameter("location", ToolParameterType.STRING, "City name")]
        )
    """
    return Tool(
        name=name,
        description=description,
        function=function,
        parameters=parameters or []
    )


__all__ = [
    'Tool',
    'ToolRegistry',
    'ToolParameter',
    'ToolParameterType',
    'create_tool',
]


"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.4
"""
