# Abhikarta LLM - Tool Management Framework
## Architecture Documentation

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha (ajsinha@gmail.com)**

---

## Table of Contents

1. [Overview](#overview)
2. [Design Principles](#design-principles)
3. [Architecture](#architecture)
4. [Core Components](#core-components)
5. [Tool Lifecycle](#tool-lifecycle)
6. [MCP Integration](#mcp-integration)
7. [Execution Pipeline](#execution-pipeline)
8. [Extension Points](#extension-points)
9. [Performance Considerations](#performance-considerations)
10. [Security](#security)

---

## Overview

The Abhikarta Tool Management Framework is a comprehensive, enterprise-grade system for managing LLM tools. It provides a modular, extensible architecture that supports all tool types, including Model Context Protocol (MCP) tools.

### Key Features

- **Universal Tool Support**: Supports API, computation, data processing, communication, MCP, and custom tools
- **Standards-Based**: Follows JSON Schema and industry standards
- **Modular Design**: Clean separation of concerns with pluggable components
- **Production-Ready**: Includes middleware, caching, rate limiting, authentication
- **MCP Native**: First-class support for Model Context Protocol
- **Type-Safe**: Full type hints and validation
- **Observable**: Built-in metrics, logging, and monitoring

---

## Design Principles

### 1. Abstraction & Extensibility

All tools inherit from `BaseTool`, providing a consistent interface while allowing custom implementations.

```python
class BaseTool(ABC):
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        pass
```

### 2. Composition Over Inheritance

The framework favors composition patterns:
- **ParameterSet**: Manages tool parameters
- **ToolRegistry**: Manages tool collections
- **Middleware**: Composes cross-cutting concerns

### 3. Type Safety

Strong typing throughout:
```python
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
```

### 4. Fail-Safe Defaults

- Tools are enabled by default
- Parameters are validated before execution
- Errors return structured ToolResult objects
- Middleware failures don't crash the pipeline

### 5. Observable by Design

Every operation is tracked:
- Execution counts
- Timing metrics
- Success/failure rates
- Last execution timestamps

---

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      LLM Application                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Tool Management Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Registry   │  │   Executor   │  │  Middleware  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Built-in    │    │   Custom     │    │     MCP      │
│    Tools     │    │    Tools     │    │    Tools     │
└──────────────┘    └──────────────┘    └──────┬───────┘
                                               │
                                               ▼
                                        ┌──────────────┐
                                        │ MCP Servers  │
                                        └──────────────┘
```

### Module Structure

```
tool_management/
├── core/              # Core abstractions and types
│   ├── types.py       # Enumerations and type aliases
│   ├── exceptions.py  # Custom exceptions
│   ├── parameters.py  # Parameter management
│   ├── results.py     # Result handling
│   └── base.py        # BaseTool abstract class
│
├── registry/          # Tool registry and discovery
│   └── registry.py    # ToolRegistry implementation
│
├── execution/         # Execution engine and middleware
│   ├── context.py     # Execution context
│   └── middleware.py  # Middleware system
│
├── mcp/              # Model Context Protocol
│   └── client.py     # MCP client and tools
│
├── builtin/          # Built-in tools
│   └── computation.py # Computational tools
│
└── utils/            # Utilities
```

---

## Core Components

### 1. BaseTool

The foundation of all tools. Provides:
- Parameter management
- Schema generation (Anthropic, OpenAI, standard formats)
- Execution tracking
- Status management
- Metadata handling

**Key Methods:**
```python
execute(**kwargs) -> ToolResult              # Sync execution
execute_async(**kwargs) -> ToolResult        # Async execution
stream_execute(**kwargs) -> AsyncIterator    # Streaming execution
get_schema() -> Dict                         # Get tool schema
```

### 2. ToolParameter

Comprehensive parameter definition with JSON Schema support:
```python
ToolParameter(
    name="query",
    param_type=ParameterType.STRING,
    description="Search query",
    required=True,
    min_length=1,
    max_length=500
)
```

**Supports:**
- All JSON Schema types
- Validation constraints (min/max, length, pattern, enum)
- Nested objects and arrays
- Default values
- Examples

### 3. ToolResult

Standardized result structure:
```python
ToolResult(
    success=True,
    data=result_data,
    execution_time=0.123,
    metadata={...}
)
```

**Features:**
- Success/failure status
- Error tracking with types
- Execution metrics
- Pagination support
- Helper methods for common patterns

### 4. ToolRegistry

Central management system:
```python
registry = ToolRegistry()
registry.register(tool, group="computation", tags=["math"])
registry.execute("calculator", expression="2 + 2")
```

**Capabilities:**
- Tool registration/unregistration
- Grouping and tagging
- Search and discovery
- Middleware management
- Schema generation for LLMs
- Statistics and metrics

---

## Tool Lifecycle

### 1. Tool Creation

```python
class CustomTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="custom_tool",
            description="Does something useful",
            tool_type=ToolType.CUSTOM
        )
        
        self.add_parameter(ToolParameter(
            name="input",
            param_type=ParameterType.STRING,
            description="Input data",
            required=True
        ))
    
    def execute(self, input: str) -> ToolResult:
        # Implementation
        return ToolResult.success_result(data=result)
```

### 2. Registration

```python
registry = ToolRegistry()
registry.register(
    CustomTool(),
    group="utilities",
    tags=["helper", "data"]
)
```

### 3. Discovery

Tools can be discovered by:
- Name/alias
- Type
- Group
- Tag
- Search query

```python
tools = registry.list_by_tag("math")
tool = registry.get("calculator")
```

### 4. Execution

```python
result = await registry.execute(
    "calculator",
    expression="sqrt(16)"
)
```

### 5. Monitoring

```python
stats = tool.get_stats()
# {
#   "execution_count": 42,
#   "total_execution_time": 1.23,
#   "average_execution_time": 0.029,
#   "last_executed": "2025-01-15T10:30:00"
# }
```

---

## MCP Integration

### Architecture

The framework provides native MCP support with multiple transport options:

1. **MCPClient**: Handles protocol communication with support for:
   - **HTTP/REST transport** (recommended for production)
   - **SSE transport** (Server-Sent Events)
   - **stdio transport** (local process communication)
2. **MCPTool**: Wraps MCP server tools
3. **discover_mcp_tools()**: Auto-discovery function

### Transport Options

#### 1. HTTP Transport (Recommended)

**Best for**: Production deployments, remote servers, load-balanced environments

```python
client = MCPClient(
    server_url="https://mcp-server.com/api",
    transport="http",
    timeout=30.0,
    headers={"Authorization": "Bearer token"}
)
```

**Features**:
- Network-based communication
- HTTPS/TLS security
- Standard authentication (OAuth, API keys, JWT)
- Load balancing support
- Firewall-friendly
- Production-ready

#### 2. SSE Transport

**Best for**: Real-time streaming, server push notifications

```python
client = MCPClient(
    server_url="https://mcp-server.com/sse",
    transport="sse"
)
```

**Features**:
- Server-Sent Events protocol
- Real-time updates
- Efficient for streaming data
- Uses standard HTTP

#### 3. stdio Transport

**Best for**: Local development, single-machine deployments

```python
client = MCPClient(
    server_url="/path/to/mcp-server",
    transport="stdio"
)
```

**Features**:
- Direct process communication
- Low latency
- No network overhead
- Local only

### Usage Pattern

```python
# Connect to MCP server with HTTP transport
async with MCPClient("https://mcp.example.com", transport="http") as client:
    # Discover tools
    mcp_tools = await discover_mcp_tools(client, prefix="mcp_")
    
    # Register in registry
    for tool in mcp_tools:
        registry.register(tool, group="mcp")
    
    # Use like any other tool
    result = await registry.execute("mcp_database_query", query="SELECT *...")
```

### MCP Protocol Flow

```
Application → MCPClient (HTTP/SSE/stdio) → MCP Server
     ↓
  MCPTool (wraps MCP tool)
     ↓
  ToolRegistry (manages like any tool)
     ↓
  LLM (uses tool via standard interface)
```

### Production Deployment

For production MCP deployments using HTTP transport:

```python
from tool_management.mcp import MCPClient, discover_mcp_tools
import os

async def setup_production_mcp():
    # Use environment variables for configuration
    client = MCPClient(
        server_url=os.getenv("MCP_SERVER_URL"),
        transport="http",
        timeout=30.0,
        headers={
            "Authorization": f"Bearer {os.getenv('MCP_API_TOKEN')}",
            "X-Environment": "production"
        }
    )
    
    await client.connect()
    tools = await discover_mcp_tools(client)
    
    return client, tools
```

**Production Checklist**:
- ✅ Use HTTPS (not HTTP)
- ✅ Implement authentication (Bearer tokens, API keys)
- ✅ Set appropriate timeouts
- ✅ Add retry logic
- ✅ Monitor connection health
- ✅ Log all interactions
- ✅ Handle failures gracefully

### Authentication Examples

**Bearer Token (OAuth 2.0 / JWT)**:
```python
headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIs..."}
```

**API Key**:
```python
headers = {"X-API-Key": "your-api-key-here"}
```

**Basic Auth**:
```python
import base64
credentials = base64.b64encode(b"username:password").decode()
headers = {"Authorization": f"Basic {credentials}"}
```

---

## Execution Pipeline

### Standard Execution Flow

```
1. Tool Request
   ↓
2. Registry Lookup
   ↓
3. Middleware Chain (pre-execution)
   ├── Authentication
   ├── Rate Limiting
   ├── Caching (check)
   ├── Validation
   └── Logging
   ↓
4. Parameter Validation
   ↓
5. Tool Execution
   ↓
6. Result Processing
   ↓
7. Middleware Chain (post-execution)
   ├── Caching (store)
   ├── Metrics
   └── Logging
   ↓
8. Return ToolResult
```

### Middleware System

Middleware functions intercept execution:

```python
async def custom_middleware(context: Dict) -> Dict:
    tool = context["tool"]
    params = context["params"]
    
    # Pre-execution logic
    logger.info(f"Executing {tool.name}")
    
    # Optionally skip execution
    if some_condition:
        context["skip"] = True
        context["result"] = cached_result
    
    return context

registry.add_middleware(custom_middleware)
```

**Built-in Middleware:**
- `logging_middleware`: Execution logging
- `timing_middleware`: Performance tracking
- `RateLimiter`: Token bucket rate limiting
- `CachingMiddleware`: Result caching with TTL
- `AuthenticationMiddleware`: Auth verification
- `ErrorHandlingMiddleware`: Retry logic

---

## Extension Points

### 1. Custom Tools

Extend `BaseTool`:
```python
class MyTool(BaseTool):
    def execute(self, **kwargs) -> ToolResult:
        # Custom logic
        pass
```

### 2. Custom Middleware

Implement middleware pattern:
```python
async def my_middleware(context: Dict) -> Dict:
    # Custom logic
    return context
```

### 3. Custom Result Types

Extend `ToolResult`:
```python
class StreamingResult(ToolResult):
    def __init__(self, stream):
        super().__init__(...)
        self.stream = stream
```

### 4. Custom Parameter Types

Extend `ToolParameter` for complex validation:
```python
class EmailParameter(ToolParameter):
    def validate(self, value):
        # Email validation logic
        super().validate(value)
```

---

## Performance Considerations

### 1. Caching

Use `CachingMiddleware` for expensive operations:
```python
cache = CachingMiddleware(ttl=300)  # 5 minutes
registry.add_middleware(cache)
```

### 2. Async Execution

Use async tools for I/O-bound operations:
```python
class AsyncTool(BaseTool):
    def __init__(self):
        super().__init__(execution_mode=ExecutionMode.ASYNC)
    
    async def execute_async(self, **kwargs):
        # Async implementation
        pass
```

### 3. Batch Processing

For multiple tool calls:
```python
results = await asyncio.gather(*[
    registry.execute(tool, **params)
    for tool, params in tool_calls
])
```

### 4. Streaming

For large results:
```python
async for chunk in tool.stream_execute(**params):
    process(chunk)
```

---

## Security

### 1. Parameter Validation

All parameters are validated before execution:
- Type checking
- Range validation
- Pattern matching
- Required field verification

### 2. Authentication

Use `AuthenticationMiddleware`:
```python
def check_auth(token):
    return verify_jwt(token)

auth = AuthenticationMiddleware(check_auth)
registry.add_middleware(auth)
```

### 3. Rate Limiting

Prevent abuse with `RateLimiter`:
```python
limiter = RateLimiter(max_calls=100, time_window=60)
registry.add_middleware(limiter)
```

### 4. Sandboxing

Built-in tools use safe execution:
```python
# CalculatorTool uses restricted eval with safe_dict
safe_dict = {"__builtins__": {}, "sqrt": math.sqrt, ...}
result = eval(expression, safe_dict, {})
```

### 5. MCP Security

MCP connections should use:
- HTTPS/TLS for network transport
- Authentication tokens
- Input validation on both sides

---

## Best Practices

1. **Always validate parameters**: Use `ToolParameter` constraints
2. **Handle errors gracefully**: Return `ToolResult.failure_result()`
3. **Add metrics**: Track execution for monitoring
4. **Use middleware**: Don't repeat cross-cutting logic
5. **Document tools**: Provide clear descriptions
6. **Test thoroughly**: Unit test all custom tools
7. **Monitor performance**: Use `get_stats()` regularly
8. **Secure by default**: Add auth and rate limiting in production

---

## Conclusion

The Abhikarta Tool Management Framework provides a robust, scalable foundation for LLM tool integration. Its modular architecture, comprehensive feature set, and MCP support make it suitable for both prototyping and production deployments.

For implementation details, see the [Quick Reference Guide](QUICK_REFERENCE.md).

---

**Patent Pending**: Certain architectural patterns described herein may be subject to patent applications.
