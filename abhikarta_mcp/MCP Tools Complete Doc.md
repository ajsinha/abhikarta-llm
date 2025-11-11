# MCP Tools System - Complete Documentation

**Copyright © 2025-2030 Ashutosh Sinha (ajsinha@gmail.com)**

---

## 🎯 Overview

The MCP Tools system provides a generic way to convert **Model Context Protocol (MCP)** endpoint schemas into LLM-compatible tool definitions. This allows you to seamlessly integrate your MCP endpoints with any LLM provider (OpenAI, Anthropic, Google, etc.).

### Key Components

1. **BaseMCPTool** - Abstract base class for MCP tools
2. **MCPTool** - Concrete implementation wrapping an MCP endpoint
3. **MCPToolFactory** - Factory for creating tools from MCP schemas
4. **MCPToolRegistry** - Registry for managing multiple tools
5. **Helper utilities** - Schema conversion, validation, execution

---

## 📋 Architecture

```
MCP Endpoint Schema
        ↓
MCPToolFactory.create_tool_from_mcp_schema()
        ↓
MCPTool (with executor function)
        ↓
tool.to_llm_tool_definition()
        ↓
LLM Tool Definition
        ↓
LLM (OpenAI, Anthropic, etc.)
        ↓
Tool Call
        ↓
tool.execute(arguments)
        ↓
MCPToolResult
```

---

## 🚀 Quick Start

### Basic Usage (3 Steps)

```python
from mcp_tools import create_tool_from_mcp

# Step 1: Your MCP endpoint schema
mcp_schema = {
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

# Step 2: Define executor (calls your actual MCP endpoint)
def get_weather_executor(args):
    # Call your MCP server here
    return {"temp": 22, "location": args["location"]}

# Step 3: Create tool
tool = create_tool_from_mcp(mcp_schema, get_weather_executor)

# Use with LLM
llm_tool_def = tool.to_llm_tool_definition()
# Pass llm_tool_def to your LLM's chat_completion
```

---

## 📚 Detailed Usage

### Pattern 1: Simple Tool Creation

```python
from mcp_tools import MCPToolFactory

# Create factory
factory = MCPToolFactory()

# Register executor
factory.register_executor("get_weather", lambda args: {...})

# Create tool from schema
tool = factory.create_tool_from_mcp_schema(mcp_schema)

# Get LLM format
llm_tool = tool.to_llm_tool_definition()

# Execute
result = tool.execute({"location": "Paris"})
print(result.data)  # Weather data
```

### Pattern 2: Multiple Tools with Registry

```python
from mcp_tools import MCPToolFactory, MCPToolRegistry

# Create factory with executors
factory = MCPToolFactory({
    "get_weather": weather_executor,
    "search_docs": search_executor,
    "create_task": task_executor
})

# Create registry
registry = MCPToolRegistry()

# Create and register tools
tools = factory.create_tools_from_mcp_schemas(mcp_schemas)
registry.register_multiple(tools)

# Get all tool definitions for LLM
llm_tools = registry.get_all_tool_definitions()

# Execute by name
result = registry.execute("get_weather", {"location": "Tokyo"})
```

### Pattern 3: Direct Schema Conversion

```python
from mcp_tools import mcp_schemas_to_llm_tools

# Convert schemas directly (no executors needed)
llm_tools = mcp_schemas_to_llm_tools(mcp_schemas)

# Use immediately with LLM
response = llm.chat_completion(
    messages=[{"role": "user", "content": "What's the weather?"}],
    tools=llm_tools
)
```

### Pattern 4: Complete LLM Integration

```python
from mcp_tools_integration import MCPToolEnabledLLM

# Wrap your LLM facade
enhanced_llm = MCPToolEnabledLLM(openai_facade)

# Register MCP endpoints
enhanced_llm.register_mcp_endpoints(mcp_schemas, executor_map)

# Chat with automatic tool handling
response = enhanced_llm.chat(
    "What's the weather in Paris and create a task to check forecast?"
)
# Automatically handles tool calls and returns final response
```

---

## 🔧 API Reference

### BaseMCPTool

Abstract base class for MCP tools.

```python
class BaseMCPTool(ABC):
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    )
    
    @abstractmethod
    def execute(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """Execute the tool."""
        pass
    
    def to_llm_tool_definition(self) -> Dict[str, Any]:
        """Convert to LLM tool format."""
        pass
    
    def validate_arguments(self, arguments: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate arguments against schema."""
        pass
```

### MCPTool

Concrete implementation.

```python
class MCPTool(BaseMCPTool):
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        executor: Callable[[Dict[str, Any]], Any],
        metadata: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        retry_count: int = 0
    )
    
    def execute(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """Execute with validation and error handling."""
        pass
```

### MCPToolFactory

Factory for creating tools.

```python
class MCPToolFactory:
    def __init__(self, executor_registry: Optional[Dict[str, Callable]] = None)
    
    def create_tool_from_mcp_schema(
        self,
        mcp_schema: Dict[str, Any],
        executor: Optional[Callable] = None
    ) -> MCPTool:
        """Create single tool from MCP schema."""
        pass
    
    def create_tools_from_mcp_schemas(
        self,
        mcp_schemas: List[Dict[str, Any]]
    ) -> List[MCPTool]:
        """Create multiple tools."""
        pass
    
    def register_executor(self, tool_name: str, executor: Callable):
        """Register executor for a tool."""
        pass
    
    def create_llm_tool_definitions(
        self,
        mcp_schemas: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Convert schemas directly to LLM format."""
        pass
```

### MCPToolRegistry

Registry for managing tools.

```python
class MCPToolRegistry:
    def __init__(self)
    
    def register(self, tool: MCPTool):
        """Register a tool."""
        pass
    
    def register_multiple(self, tools: List[MCPTool]):
        """Register multiple tools."""
        pass
    
    def get(self, name: str) -> Optional[MCPTool]:
        """Get tool by name."""
        pass
    
    def execute(self, name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """Execute tool by name."""
        pass
    
    def get_all_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get all tools in LLM format."""
        pass
    
    def list_tools(self) -> List[str]:
        """List tool names."""
        pass
```

### MCPToolResult

Result from tool execution.

```python
@dataclass
class MCPToolResult:
    status: MCPToolStatus  # SUCCESS, FAILED, etc.
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_success(self) -> bool:
        """Check if successful."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        pass
```

---

## 💡 Schema Formats

### MCP Endpoint Schema (Input)

```json
{
  "name": "tool_name",
  "description": "What the tool does",
  "inputSchema": {
    "type": "object",
    "properties": {
      "param1": {
        "type": "string",
        "description": "Parameter description"
      },
      "param2": {
        "type": "number",
        "description": "Another parameter"
      }
    },
    "required": ["param1"]
  }
}
```

### LLM Tool Definition (Output)

```json
{
  "type": "function",
  "function": {
    "name": "tool_name",
    "description": "What the tool does",
    "parameters": {
      "type": "object",
      "properties": {
        "param1": {
          "type": "string",
          "description": "Parameter description"
        },
        "param2": {
          "type": "number",
          "description": "Another parameter"
        }
      },
      "required": ["param1"]
    }
  }
}
```

---

## 🎯 Common Use Cases

### Use Case 1: Simple Schema Conversion

**Scenario**: You have MCP schemas and just need LLM tool definitions.

```python
from mcp_tools import mcp_schemas_to_llm_tools

llm_tools = mcp_schemas_to_llm_tools(mcp_schemas)

# Use with any LLM
response = llm.chat_completion(messages, tools=llm_tools)
```

### Use Case 2: Full Execution Pipeline

**Scenario**: You want to handle the entire tool execution flow.

```python
from mcp_tools import MCPToolFactory, MCPToolRegistry

# Setup
factory = MCPToolFactory(executor_map)
registry = MCPToolRegistry()
tools = factory.create_tools_from_mcp_schemas(schemas)
registry.register_multiple(tools)

# Use
llm_tools = registry.get_all_tool_definitions()
response = llm.chat_completion(messages, tools=llm_tools)

# Execute tools
if "tool_calls" in response:
    for call in response["tool_calls"]:
        result = registry.execute(
            call["function"]["name"],
            json.loads(call["function"]["arguments"])
        )
```

### Use Case 3: Automatic Tool Loop

**Scenario**: Let the system handle tool calls automatically.

```python
from mcp_tools_integration import MCPToolEnabledLLM

llm = MCPToolEnabledLLM(openai_facade)
llm.register_mcp_endpoints(schemas, executors)

# Automatic tool handling
response = llm.chat("What's the weather and create a reminder?")
```

---

## ✅ Features

### Validation
- ✅ Automatic schema validation
- ✅ Type checking
- ✅ Required field validation
- ✅ Enum validation

### Error Handling
- ✅ Execution errors caught
- ✅ Validation errors reported
- ✅ Detailed error messages
- ✅ Status tracking

### Execution
- ✅ Retry support
- ✅ Timeout support (planned)
- ✅ Execution time tracking
- ✅ Metadata tracking

### Integration
- ✅ Works with all LLM providers
- ✅ Compatible with LLM facades
- ✅ Flexible executor system
- ✅ Registry for management

---

## 📁 Files Provided

1. **mcp_tools.py** - Core system implementation
2. **mcp_tools_examples.py** - 6 comprehensive examples
3. **mcp_tools_integration.py** - Practical integration patterns
4. **MCP_TOOLS_DOCUMENTATION.md** - This file

---

## 🚀 Getting Started Checklist

- [ ] Review `mcp_tools.py` for core classes
- [ ] Run `mcp_tools_examples.py` to see all patterns
- [ ] Check `mcp_tools_integration.py` for practical usage
- [ ] Adapt Pattern 3 or 4 for your use case
- [ ] Replace mock executors with real MCP calls
- [ ] Integrate with your LLM facade
- [ ] Test and deploy!

---

## 💼 Production Considerations

### Security
- Validate all inputs
- Sanitize tool arguments
- Limit tool execution permissions
- Add authentication/authorization

### Performance
- Cache tool definitions
- Implement connection pooling for MCP calls
- Add timeout handling
- Monitor execution times

### Reliability
- Implement retry logic
- Add circuit breakers
- Log all tool executions
- Handle partial failures

### Monitoring
- Track tool usage
- Monitor success/failure rates
- Log execution times
- Alert on errors

---

## 📞 Support

**Author**: Ashutosh Sinha  
**Email**: ajsinha@gmail.com

---

## 🎉 Summary

The MCP Tools system provides a clean, generic way to:

1. ✅ Convert MCP endpoint schemas to LLM tools
2. ✅ Execute MCP endpoints as LLM tool calls
3. ✅ Validate arguments automatically
4. ✅ Handle errors gracefully
5. ✅ Work with any LLM provider

**Three simple patterns to choose from:**

1. **Direct Conversion** - Just convert schemas
2. **Full Pipeline** - Handle execution yourself
3. **Automatic** - Let the system handle everything

Pick the pattern that fits your architecture and start building!

---

**Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.**