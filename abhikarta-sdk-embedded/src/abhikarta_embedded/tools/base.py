"""Base Tool classes."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable

@dataclass
class BaseTool(ABC):
    name: str
    description: str
    parameters: Dict[str, Any] = None
    
    @abstractmethod
    def execute(self, args: Dict[str, Any]) -> Any:
        pass

class Tool(BaseTool):
    """Simple tool wrapper for functions."""
    def __init__(self, name: str, description: str, func: Callable, parameters: Dict = None):
        self.name = name
        self.description = description
        self.func = func
        self.parameters = parameters or {}
    
    def execute(self, args: Dict[str, Any]) -> Any:
        return self.func(**args)
    
    @classmethod
    def from_function(cls, func: Callable, name: str = None, description: str = None) -> "Tool":
        return cls(name=name or func.__name__, description=description or func.__doc__ or "", func=func)

class ToolRegistry:
    """Registry for managing tools."""
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)
    
    def list(self) -> List[str]:
        return list(self._tools.keys())
    
    def all(self) -> List[BaseTool]:
        return list(self._tools.values())
