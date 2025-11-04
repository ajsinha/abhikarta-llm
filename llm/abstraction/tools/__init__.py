"""
Function Calling / Tool Use System

Enables LLMs to call external functions and tools.

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

from typing import Callable, Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import inspect


class ToolParameterType(Enum):
    """Types for tool parameters"""
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


@dataclass
class ToolParameter:
    """Parameter definition for a tool"""
    name: str
    type: ToolParameterType
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        param = {
            'type': self.type.value,
            'description': self.description
        }
        if self.enum:
            param['enum'] = self.enum
        return param


@dataclass
class Tool:
    """Definition of a callable tool"""
    name: str
    description: str
    function: Callable
    parameters: List[ToolParameter] = field(default_factory=list)
    returns: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Auto-generate parameters from function signature if not provided"""
        if not self.parameters:
            self.parameters = self._extract_parameters()
    
    def _extract_parameters(self) -> List[ToolParameter]:
        """Extract parameters from function signature"""
        sig = inspect.signature(self.function)
        params = []
        
        for param_name, param in sig.parameters.items():
            if param_name in ['self', 'cls']:
                continue
            
            # Infer type from annotation
            param_type = ToolParameterType.STRING
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = ToolParameterType.INTEGER
                elif param.annotation == float:
                    param_type = ToolParameterType.NUMBER
                elif param.annotation == bool:
                    param_type = ToolParameterType.BOOLEAN
                elif param.annotation == list:
                    param_type = ToolParameterType.ARRAY
                elif param.annotation == dict:
                    param_type = ToolParameterType.OBJECT
            
            required = param.default == inspect.Parameter.empty
            default = None if required else param.default
            
            params.append(ToolParameter(
                name=param_name,
                type=param_type,
                description=f"Parameter {param_name}",
                required=required,
                default=default
            ))
        
        return params
    
    def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters"""
        # Validate parameters
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                raise ValueError(f"Required parameter '{param.name}' not provided")
            
            if param.name not in kwargs and param.default is not None:
                kwargs[param.name] = param.default
        
        # Execute function
        try:
            result = self.function(**kwargs)
            return result
        except Exception as e:
            raise RuntimeError(f"Tool execution failed: {str(e)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary format for LLM"""
        required_params = [p.name for p in self.parameters if p.required]
        
        return {
            'name': self.name,
            'description': self.description,
            'parameters': {
                'type': 'object',
                'properties': {
                    p.name: p.to_dict() for p in self.parameters
                },
                'required': required_params
            }
        }


class ToolRegistry:
    """Registry for managing available tools"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.execution_history: List[Dict[str, Any]] = []
    
    def register(self, tool: Tool) -> None:
        """Register a tool"""
        if tool.name in self.tools:
            raise ValueError(f"Tool '{tool.name}' already registered")
        self.tools[tool.name] = tool
    
    def register_function(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: Optional[List[ToolParameter]] = None
    ) -> Tool:
        """Register a function as a tool"""
        tool = Tool(
            name=name,
            description=description,
            function=function,
            parameters=parameters or []
        )
        self.register(tool)
        return tool
    
    def unregister(self, name: str) -> None:
        """Unregister a tool"""
        if name in self.tools:
            del self.tools[name]
    
    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self.tools.keys())
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Get schema for all tools (for LLM)"""
        return [tool.to_dict() for tool in self.tools.values()]
    
    def execute(self, name: str, **kwargs) -> Any:
        """Execute a tool by name"""
        tool = self.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")
        
        # Log execution
        start_time = datetime.now()
        
        try:
            result = tool.execute(**kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
            raise
        finally:
            self.execution_history.append({
                'tool': name,
                'parameters': kwargs,
                'result': result,
                'success': success,
                'error': error,
                'timestamp': start_time,
                'duration_ms': (datetime.now() - start_time).total_seconds() * 1000
            })
        
        return result
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get tool execution history"""
        return self.execution_history.copy()
    
    def clear_history(self) -> None:
        """Clear execution history"""
        self.execution_history.clear()
    
    def get_all_tools(self) -> List[Tool]:
        """Get all registered tools"""
        return list(self.tools.values())
    
    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Convert all tools to dictionary format"""
        return [tool.to_dict() for tool in self.tools.values()]


@dataclass
class ToolCall:
    """Represents a tool call from the LLM"""
    tool_name: str
    parameters: Dict[str, Any]
    call_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'tool_name': self.tool_name,
            'parameters': self.parameters,
            'call_id': self.call_id
        }


@dataclass
class ToolResult:
    """Result from tool execution"""
    tool_name: str
    result: Any
    success: bool = True
    error: Optional[str] = None
    call_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'tool_name': self.tool_name,
            'result': self.result,
            'success': self.success,
            'error': self.error,
            'call_id': self.call_id
        }


class AgentExecutor:
    """Executes agent loops with tool calling"""
    
    def __init__(
        self,
        llm_client: Any,
        tools: ToolRegistry,
        max_iterations: int = 10,
        verbose: bool = False
    ):
        self.llm_client = llm_client
        self.tools = tools
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.iteration_history: List[Dict[str, Any]] = []
    
    def execute(self, prompt: str, **kwargs) -> str:
        """Execute agent with tool calling"""
        conversation = [{'role': 'user', 'content': prompt}]
        
        for iteration in range(self.max_iterations):
            if self.verbose:
                print(f"\n--- Iteration {iteration + 1} ---")
            
            # Get LLM response with available tools
            response = self._call_llm_with_tools(conversation, **kwargs)
            
            # Check if LLM wants to use tools
            tool_calls = self._parse_tool_calls(response)
            
            if not tool_calls:
                # LLM provided final answer
                if self.verbose:
                    print("Final answer received")
                return response
            
            # Execute tool calls
            for tool_call in tool_calls:
                if self.verbose:
                    print(f"Calling tool: {tool_call.tool_name}")
                    print(f"Parameters: {tool_call.parameters}")
                
                try:
                    result = self.tools.execute(
                        tool_call.tool_name,
                        **tool_call.parameters
                    )
                    tool_result = ToolResult(
                        tool_name=tool_call.tool_name,
                        result=result,
                        success=True,
                        call_id=tool_call.call_id
                    )
                except Exception as e:
                    if self.verbose:
                        print(f"Tool error: {e}")
                    tool_result = ToolResult(
                        tool_name=tool_call.tool_name,
                        result=None,
                        success=False,
                        error=str(e),
                        call_id=tool_call.call_id
                    )
                
                # Add tool result to conversation
                conversation.append({
                    'role': 'tool',
                    'content': json.dumps(tool_result.to_dict()),
                    'tool_call_id': tool_call.call_id
                })
            
            # Log iteration
            self.iteration_history.append({
                'iteration': iteration,
                'response': response,
                'tool_calls': [tc.to_dict() for tc in tool_calls],
                'timestamp': datetime.now()
            })
        
        raise RuntimeError(f"Max iterations ({self.max_iterations}) reached")
    
    def _call_llm_with_tools(
        self,
        conversation: List[Dict[str, Any]],
        **kwargs
    ) -> str:
        """Call LLM with tools available"""
        # Get tools schema
        tools_schema = self.tools.get_tools_schema()
        
        # Add tools to system message
        system_message = f"""You are a helpful assistant with access to the following tools:

{json.dumps(tools_schema, indent=2)}

To use a tool, respond with JSON in this format:
{{"tool": "tool_name", "parameters": {{"param1": "value1"}}}}

If you don't need to use a tool, respond normally."""
        
        conversation_with_system = [
            {'role': 'system', 'content': system_message}
        ] + conversation
        
        # Call LLM (simplified - actual implementation would use facade)
        # This is a placeholder for the actual LLM call
        response = "Mock response"
        
        return response
    
    def _parse_tool_calls(self, response: str) -> List[ToolCall]:
        """Parse tool calls from LLM response"""
        tool_calls = []
        
        # Try to parse JSON tool calls
        try:
            # Look for JSON blocks in response
            if '{' in response and '}' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
                
                data = json.loads(json_str)
                
                if 'tool' in data:
                    tool_calls.append(ToolCall(
                        tool_name=data['tool'],
                        parameters=data.get('parameters', {}),
                        call_id=data.get('call_id')
                    ))
        except json.JSONDecodeError:
            pass
        
        return tool_calls
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get iteration history"""
        return self.iteration_history.copy()
    
    def clear_history(self) -> None:
        """Clear iteration history"""
        self.iteration_history.clear()


# Built-in tools

def create_calculator_tool() -> Tool:
    """Create a calculator tool"""
    def calculate(expression: str) -> float:
        """Safely evaluate a mathematical expression"""
        try:
            # Remove any dangerous operations
            allowed_chars = set('0123456789+-*/().,% ')
            if not all(c in allowed_chars for c in expression):
                raise ValueError("Invalid characters in expression")
            
            result = eval(expression, {"__builtins__": {}}, {})
            return float(result)
        except Exception as e:
            raise ValueError(f"Invalid expression: {e}")
    
    return Tool(
        name="calculator",
        description="Evaluate mathematical expressions. Supports +, -, *, /, %, and parentheses.",
        function=calculate,
        parameters=[
            ToolParameter(
                name="expression",
                type=ToolParameterType.STRING,
                description="Mathematical expression to evaluate",
                required=True
            )
        ]
    )


def create_search_tool(search_function: Callable[[str], List[str]]) -> Tool:
    """Create a search tool"""
    return Tool(
        name="search",
        description="Search for information",
        function=search_function,
        parameters=[
            ToolParameter(
                name="query",
                type=ToolParameterType.STRING,
                description="Search query",
                required=True
            )
        ]
    )


def create_datetime_tool() -> Tool:
    """Create a datetime tool"""
    def get_current_time() -> str:
        """Get current date and time"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return Tool(
        name="get_current_time",
        description="Get the current date and time",
        function=get_current_time,
        parameters=[]
    )
