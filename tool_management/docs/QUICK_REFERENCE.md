# Abhikarta LLM - Tool Management Framework
## Quick Reference Guide

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha (ajsinha@gmail.com)**

---

## Installation

```bash
pip install -e .
```

Or directly:
```bash
pip install abhikarta-tool-management
```

---

## Quick Start

### 1. Basic Setup

```python
from tool_management import ToolRegistry, BaseTool, ToolParameter, ToolResult, ToolType, ParameterType

# Create registry
registry = ToolRegistry()
```

### 2. Create a Simple Tool

```python
class GreetingTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="greeting",
            description="Generate a greeting message",
            tool_type=ToolType.CUSTOM
        )
        
        self.add_parameter(ToolParameter(
            name="name",
            param_type=ParameterType.STRING,
            description="Name to greet",
            required=True
        ))
    
    def execute(self, name: str) -> ToolResult:
        message = f"Hello, {name}!"
        return ToolResult.success_result(
            data={"message": message},
            tool_name=self.name
        )

# Register the tool
registry.register(GreetingTool())
```

### 3. Use the Tool

```python
import asyncio

async def main():
    result = await registry.execute("greeting", name="World")
    print(result.data)  # {"message": "Hello, World!"}

asyncio.run(main())
```

---

## Common Patterns

### Creating Tools

#### Pattern 1: Simple Synchronous Tool

```python
class SimpleTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="simple_tool",
            description="A simple tool",
            tool_type=ToolType.CUSTOM
        )
        
        self.add_parameter(ToolParameter(
            name="input",
            param_type=ParameterType.STRING,
            required=True,
            description="Input string"
        ))
    
    def execute(self, input: str) -> ToolResult:
        result = input.upper()
        return ToolResult.success_result(data=result)
```

#### Pattern 2: Async Tool

```python
from tool_management import ExecutionMode
import httpx

class APITool(BaseTool):
    def __init__(self):
        super().__init__(
            name="api_tool",
            description="Calls an external API",
            tool_type=ToolType.API,
            execution_mode=ExecutionMode.ASYNC
        )
        
        self.add_parameter(ToolParameter(
            name="url",
            param_type=ParameterType.STRING,
            required=True,
            description="API URL"
        ))
    
    async def execute_async(self, url: str) -> ToolResult:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return ToolResult.success_result(data=response.json())
```

#### Pattern 3: Tool with Complex Parameters

```python
class DataProcessorTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="data_processor",
            description="Process data with options",
            tool_type=ToolType.DATA_PROCESSING
        )
        
        # Simple parameter
        self.add_parameter(ToolParameter(
            name="data",
            param_type=ParameterType.ARRAY,
            required=True,
            description="Data to process"
        ))
        
        # Enum parameter
        self.add_parameter(ToolParameter(
            name="operation",
            param_type=ParameterType.STRING,
            required=True,
            description="Operation to perform",
            enum=["sum", "average", "max", "min"]
        ))
        
        # Optional parameter with default
        self.add_parameter(ToolParameter(
            name="precision",
            param_type=ParameterType.INTEGER,
            required=False,
            default=2,
            description="Decimal precision",
            minimum=0,
            maximum=10
        ))
    
    def execute(self, data: list, operation: str, precision: int = 2) -> ToolResult:
        if operation == "sum":
            result = round(sum(data), precision)
        elif operation == "average":
            result = round(sum(data) / len(data), precision)
        elif operation == "max":
            result = max(data)
        elif operation == "min":
            result = min(data)
        
        return ToolResult.success_result(data=result)
```

---

## Registry Operations

### Registration

```python
# Basic registration
registry.register(my_tool)

# With group
registry.register(my_tool, group="utilities")

# With tags
registry.register(my_tool, tags=["math", "helper"])

# With alias
registry.register(my_tool, alias="calc")

# All together
registry.register(
    my_tool,
    group="computation",
    tags=["math", "calculator"],
    alias="calc"
)
```

### Discovery

```python
# Get by name
tool = registry.get("calculator")

# Get or raise exception
tool = registry.get_or_raise("calculator")

# List all enabled tools
tools = registry.list_all(enabled_only=True)

# List by type
math_tools = registry.list_by_type(ToolType.COMPUTATION)

# List by group
utils = registry.list_by_group("utilities")

# List by tag
helpers = registry.list_by_tag("helper")

# Search
results = registry.search("calculate")
```

### Execution

```python
# Simple execution
result = await registry.execute("calculator", expression="2 + 2")

# Check result
if result.success:
    print(result.data)
else:
    print(f"Error: {result.error}")

# Access metadata
print(f"Execution time: {result.execution_time}s")
```

---

## Using Built-in Tools

### Calculator

```python
from tool_management.builtin import CalculatorTool

calc = CalculatorTool()
registry.register(calc)

result = await registry.execute(
    "calculator",
    expression="sqrt(16) + 10"
)
print(result.data)  # {"expression": "sqrt(16) + 10", "result": 14.0}
```

### JSON Validator

```python
from tool_management.builtin import JSONValidatorTool

validator = JSONValidatorTool()
registry.register(validator)

result = await registry.execute(
    "json_validator",
    json_string='{"name": "test"}',
    format=True
)
print(result.data["formatted"])
```

### Text Analyzer

```python
from tool_management.builtin import TextAnalyzerTool

analyzer = TextAnalyzerTool()
registry.register(analyzer)

result = await registry.execute(
    "text_analyzer",
    text="The quick brown fox jumps over the lazy dog"
)
print(result.data)
# {
#   "character_count": 43,
#   "word_count": 9,
#   "sentence_count": 1,
#   ...
# }
```

---

## Middleware

### Using Built-in Middleware

```python
from tool_management.execution import (
    logging_middleware,
    timing_middleware,
    RateLimiter,
    CachingMiddleware
)

# Add logging
registry.add_middleware(logging_middleware)

# Add timing
registry.add_middleware(timing_middleware)

# Add rate limiting (100 calls per 60 seconds per tool)
limiter = RateLimiter(max_calls=100, time_window=60, per_tool=True)
registry.add_middleware(limiter)

# Add caching (5 minute TTL)
cache = CachingMiddleware(ttl=300)
registry.add_middleware(cache)
```

### Creating Custom Middleware

```python
async def audit_middleware(context):
    """Log all tool executions to audit log"""
    tool = context["tool"]
    params = context["params"]
    
    # Log to audit system
    audit_log.info(f"Tool: {tool.name}, Params: {params}")
    
    return context

registry.add_middleware(audit_middleware)
```

### Conditional Execution Middleware

```python
async def business_hours_middleware(context):
    """Only allow execution during business hours"""
    from datetime import datetime
    
    hour = datetime.now().hour
    
    if not (9 <= hour < 17):  # 9 AM to 5 PM
        context["skip"] = True
        context["result"] = ToolResult.failure_result(
            error="Tool only available during business hours",
            tool_name=context["tool"].name
        )
    
    return context

registry.add_middleware(business_hours_middleware)
```

---

## MCP Integration

### Connecting to MCP Server

The framework supports multiple MCP transport protocols:

#### HTTP Transport (Recommended for Production)

```python
from tool_management.mcp import MCPClient, discover_mcp_tools

# Create HTTP client
async with MCPClient(
    server_url="https://mcp.example.com/api",
    transport="http",
    timeout=30.0,
    headers={"Authorization": "Bearer your-token"}
) as client:
    # Auto-connect and auto-disconnect with context manager
    
    # Discover tools from MCP server
    mcp_tools = await discover_mcp_tools(client, prefix="mcp_")
    
    # Register all discovered tools
    for tool in mcp_tools:
        registry.register(tool, group="mcp")
    
    # Use MCP tools like any other tool
    result = await registry.execute("mcp_database_query", query="SELECT * FROM users")
```

#### SSE Transport (Server-Sent Events)

```python
client = MCPClient(
    server_url="https://mcp.example.com/sse",
    transport="sse"
)
await client.connect()
```

#### stdio Transport (Local Process)

```python
client = MCPClient(
    server_url="/path/to/mcp-server",
    transport="stdio"
)
await client.connect()
```

### Transport Comparison

| Feature | HTTP | SSE | stdio |
|---------|------|-----|-------|
| Network-based | ✅ | ✅ | ❌ |
| Production-ready | ✅ | ✅ | ⚠️ |
| Authentication | ✅ | ✅ | ❌ |
| Load balancing | ✅ | ✅ | ❌ |
| Streaming | ❌ | ✅ | ✅ |
| Latency | Medium | Medium | Low |

**Recommendation**: Use HTTP transport for production deployments.

### Authentication

#### Bearer Token (OAuth 2.0 / JWT)

```python
client = MCPClient(
    server_url="https://mcp.example.com",
    transport="http",
    headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIs..."}
)
```

#### API Key

```python
client = MCPClient(
    server_url="https://mcp.example.com",
    transport="http",
    headers={"X-API-Key": "your-api-key-here"}
)
```

#### Basic Authentication

```python
import base64

credentials = base64.b64encode(b"username:password").decode()
client = MCPClient(
    server_url="https://mcp.example.com",
    transport="http",
    headers={"Authorization": f"Basic {credentials}"}
)
```

### Production MCP Setup

```python
import os
from tool_management.mcp import MCPClient, discover_mcp_tools

async def setup_mcp():
    # Use environment variables
    client = MCPClient(
        server_url=os.getenv("MCP_SERVER_URL"),
        transport="http",
        timeout=30.0,
        headers={
            "Authorization": f"Bearer {os.getenv('MCP_API_TOKEN')}",
            "X-Environment": "production",
            "X-Client-Version": "1.0.0"
        }
    )
    
    # Connect
    await client.connect()
    
    # Discover and register tools
    tools = await discover_mcp_tools(client, prefix="mcp_")
    
    registry = ToolRegistry()
    for tool in tools:
        registry.register(tool, group="mcp", tags=["production"])
    
    return client, registry

# Usage
client, registry = await setup_mcp()
```

### Manual MCP Tool Creation

```python
from tool_management.mcp import MCPTool

# Create MCP tool manually
mcp_tool = MCPTool(
    name="my_mcp_tool",
    description="Custom MCP tool",
    mcp_client=client,
    mcp_tool_name="original_tool_name",
    input_schema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "First parameter"}
        },
        "required": ["param1"]
    }
)

registry.register(mcp_tool)
```

---

## Schema Generation

### For Anthropic

```python
schemas = registry.get_all_schemas(format="anthropic")

# Use with Anthropic API
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    tools=schemas,
    messages=[{"role": "user", "content": "Calculate 2+2"}]
)
```

### For OpenAI

```python
schemas = registry.get_all_schemas(format="openai")

# Use with OpenAI API
import openai

response = openai.chat.completions.create(
    model="gpt-4",
    tools=schemas,
    messages=[{"role": "user", "content": "Calculate 2+2"}]
)
```

### Standard Format

```python
schemas = registry.get_all_schemas(format="standard")
# Returns detailed schema with all metadata
```

---

## Tool Management

### Enable/Disable Tools

```python
tool = registry.get("calculator")

# Disable
tool.disable()

# Enable
tool.enable()

# Set to maintenance
tool.set_maintenance()

# Deprecate
tool.deprecate()

# Check status
if tool.enabled:
    print("Tool is ready")
```

### Tool Metadata

```python
tool = registry.get("calculator")

# Set metadata
tool.set_metadata("version", "2.0")
tool.set_metadata("author", "Team A")

# Get metadata
version = tool.get_metadata("version")

# Add tags
tool.add_tag("production")
tool.add_tag("critical")

# Check tag
if tool.has_tag("critical"):
    print("Critical tool!")
```

### Tool Statistics

```python
# Get tool stats
stats = tool.get_stats()
print(stats)
# {
#   "execution_count": 42,
#   "total_execution_time": 1.5,
#   "average_execution_time": 0.036,
#   "last_executed": "2025-01-15T10:30:00"
# }

# Reset stats
tool.reset_stats()

# Get registry statistics
registry_stats = registry.get_statistics()
print(registry_stats)
# {
#   "total_tools": 10,
#   "total_groups": 3,
#   "total_executions": 100,
#   ...
# }
```

---

## Error Handling

### Check Result Status

```python
result = await registry.execute("calculator", expression="2+2")

if result.success:
    print(f"Result: {result.data}")
else:
    print(f"Error: {result.error}")
    print(f"Error Type: {result.error_type}")
```

### Handle Different Error Types

```python
from tool_management.core import (
    ToolNotFoundError,
    ToolDisabledError,
    ParameterValidationError
)

try:
    result = await registry.execute("calculator", expression="2+2")
except ToolNotFoundError as e:
    print(f"Tool not found: {e.tool_name}")
except ToolDisabledError as e:
    print(f"Tool disabled: {e.tool_name}")
except ParameterValidationError as e:
    print(f"Invalid parameter: {e.parameter_name}")
```

### Creating Error Results

```python
def execute(self, **kwargs) -> ToolResult:
    try:
        # Process
        result = process_data()
        return ToolResult.success_result(data=result)
    except ValueError as e:
        return ToolResult.failure_result(
            error=str(e),
            error_type="ValueError"
        )
    except TimeoutError:
        return ToolResult.timeout_result(timeout_seconds=30)
```

---

## Advanced Features

### Result Aggregation

```python
from tool_management.core import ResultAggregator

aggregator = ResultAggregator()

# Execute multiple tools
for tool_name, params in tool_calls:
    result = await registry.execute(tool_name, **params)
    aggregator.add(result)

# Get statistics
print(f"Success rate: {aggregator.success_rate()}")
print(f"Total time: {aggregator.total_execution_time()}")

# Get summary
summary = aggregator.to_summary()
```

### Batch Execution

```python
import asyncio

# Execute multiple tools in parallel
tool_calls = [
    ("calculator", {"expression": "2+2"}),
    ("text_analyzer", {"text": "Hello world"}),
    ("json_validator", {"json_string": '{"test": true}'})
]

results = await asyncio.gather(*[
    registry.execute(name, **params)
    for name, params in tool_calls
])

for result in results:
    print(result.data)
```

---

## Best Practices

### 1. Always Use Type Hints

```python
def execute(self, name: str, age: int) -> ToolResult:
    pass
```

### 2. Validate Early

```python
def execute(self, data: list) -> ToolResult:
    if not data:
        return ToolResult.failure_result(
            error="Data cannot be empty"
        )
    # Process...
```

### 3. Provide Clear Descriptions

```python
self.add_parameter(ToolParameter(
    name="threshold",
    param_type=ParameterType.NUMBER,
    description="Confidence threshold (0.0 to 1.0). Values above this will be included.",
    required=False,
    default=0.5,
    minimum=0.0,
    maximum=1.0
))
```

### 4. Use Appropriate Tool Types

```python
# For APIs
tool_type=ToolType.API

# For computation
tool_type=ToolType.COMPUTATION

# For data processing
tool_type=ToolType.DATA_PROCESSING
```

### 5. Add Meaningful Metadata

```python
tool.set_metadata("rate_limit", "100/minute")
tool.set_metadata("cost", "0.001")
tool.add_tag("production")
```

---

## Troubleshooting

### Tool Not Found

```python
# Check if tool is registered
if "calculator" in registry:
    print("Tool is registered")

# List all tools
for tool in registry.list_all():
    print(tool.name)
```

### Tool Disabled

```python
tool = registry.get("calculator")
if not tool.enabled:
    tool.enable()
```

### Parameter Validation Errors

```python
# Check parameter schema
schema = tool.get_schema()
print(schema["parameters"])

# Manually validate
try:
    params = tool._parameters.validate_values(**kwargs)
except ParameterValidationError as e:
    print(f"Validation error: {e}")
```

### Slow Execution

```python
# Check stats
stats = tool.get_stats()
print(f"Average time: {stats['average_execution_time']}s")

# Add caching
cache = CachingMiddleware(ttl=300)
registry.add_middleware(cache)
```

---

## API Reference

For complete API documentation, see the [Architecture Documentation](ARCHITECTURE.md).

---

## Examples

See the `examples/` directory for complete working examples:
- `basic_usage.py` - Basic tool creation and usage
- `custom_tools.py` - Creating custom tools
- `mcp_integration.py` - MCP integration example

---

## Support

For issues, questions, or contributions:
- Email: ajsinha@gmail.com

---

**Copyright © 2025-2030, All Rights Reserved - Ashutosh Sinha**
