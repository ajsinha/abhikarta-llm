# Abhikarta MCP Integration - Technical Documentation

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Component Design](#component-design)
3. [Protocol Specification](#protocol-specification)
4. [Authentication Flow](#authentication-flow)
5. [Cache Management](#cache-management)
6. [Registry Synchronization](#registry-synchronization)
7. [Performance Considerations](#performance-considerations)
8. [Security](#security)

---

## System Architecture

### Overview

The Abhikarta MCP Integration follows a layered architecture:

```
┌─────────────────────────────────────────────────┐
│         Application Layer                        │
│  (User Code, Tool Execution, Workflows)         │
└─────────────────────────────────────────────────┘
                     ↕
┌─────────────────────────────────────────────────┐
│       Tool Registry (Framework Layer)            │
│    (Tool Management, Execution, Lifecycle)      │
└─────────────────────────────────────────────────┘
                     ↕
┌─────────────────────────────────────────────────┐
│     MCP Integration Layer (This Module)         │
│  ┌──────────────────┐  ┌───────────────────┐  │
│  │ MCPAutoSync      │  │ MCPRegistry       │  │
│  │                  │  │ Integration       │  │
│  └──────────────────┘  └───────────────────┘  │
│  ┌──────────────────┐  ┌───────────────────┐  │
│  │ AbhikartaBase    │  │ AbhikartaMCP      │  │
│  │ Tool             │  │ ToolBuilder       │  │
│  └──────────────────┘  └───────────────────┘  │
└─────────────────────────────────────────────────┘
                     ↕
┌─────────────────────────────────────────────────┐
│      MCP Server (JSON-RPC over HTTP)            │
│  (Tool Discovery, Schema, Execution)            │
└─────────────────────────────────────────────────┘
```

### Data Flow

1. **Discovery Flow**
   ```
   Builder → MCP Server (tools/list) → Cache Update → 
   Registry Integration → Tool Registration → Registry
   ```

2. **Execution Flow**
   ```
   Application → Registry → Tool Instance → MCP Client →
   MCP Server (tools/call) → Response → ToolResult
   ```

3. **Refresh Flow**
   ```
   Periodic Timer → Builder → MCP Server → Cache Diff →
   Registry Integration → Add/Remove/Update → Registry
   ```

---

## Component Design

### 1. AbhikartaMCPToolBuilder

**Purpose:** Central discovery and caching service

**Design Pattern:** Singleton

**Key Responsibilities:**
- Connection management
- Authentication handling
- Tool discovery
- Schema caching
- Periodic refresh

**Thread Safety:** Uses `threading.Lock` for singleton creation

**State Management:**
```python
_tool_cache: Dict[str, MCPToolSchema]
_auth_token: Optional[str]
_token_expires_at: Optional[datetime]
_refresh_task: Optional[asyncio.Task]
_running: bool
```

**Lifecycle:**
```
Initialize → Configure → Start → 
(Periodic Refresh Loop) → Stop → Cleanup
```

### 2. AbhikartaBaseTool

**Purpose:** Tool execution wrapper

**Design Pattern:** Adapter

**Key Responsibilities:**
- Parameter validation
- JSON-RPC communication
- Result transformation
- Error handling

**Execution Modes:**
- Synchronous (via `execute`)
- Asynchronous (via `execute_async`)

**Tool Naming Convention:**
```
Original: "calculate"
Registered: "calculate:abhikartamcp"
```

### 3. MCPRegistryIntegration

**Purpose:** Registry synchronization manager

**Key Responsibilities:**
- Tool registration
- Tool removal
- Update detection
- Group/tag management

**Synchronization Algorithm:**
```python
1. Get current cached tools (C)
2. Get registered tools (R)
3. New tools = C - R → Register
4. Removed tools = R - C → Unregister
5. Existing tools = R ∩ C → Check for updates
```

### 4. MCPAutoSync

**Purpose:** Background synchronization service

**Key Responsibilities:**
- Periodic sync execution
- Error recovery
- Manual sync triggers

**Timing:**
```
Builder Refresh: Every 600s (default)
Registry Sync: Every 60s (default)
```

---

## Protocol Specification

### JSON-RPC 2.0

All communication uses JSON-RPC 2.0 format.

#### Request Structure

```json
{
    "jsonrpc": "2.0",
    "id": <integer>,
    "method": "<method_name>",
    "params": {
        "<param_key>": "<param_value>"
    }
}
```

#### Response Structure

**Success:**
```json
{
    "jsonrpc": "2.0",
    "id": <integer>,
    "result": {
        "<result_key>": "<result_value>"
    }
}
```

**Error:**
```json
{
    "jsonrpc": "2.0",
    "id": <integer>,
    "error": {
        "code": <error_code>,
        "message": "<error_message>",
        "data": <optional_data>
    }
}
```

### Methods

#### 1. initialize

**Purpose:** Initialize connection

**Request:**
```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "1.0",
        "capabilities": {
            "tools": {}
        }
    }
}
```

**Response:**
```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "protocolVersion": "1.0",
        "serverName": "SAJHA MCP Server",
        "serverVersion": "1.0.0",
        "capabilities": {
            "tools": {
                "listChanged": true
            }
        }
    }
}
```

#### 2. tools/list

**Purpose:** List available tools

**Request:**
```json
{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
}
```

**Response:**
```json
{
    "jsonrpc": "2.0",
    "id": 2,
    "result": {
        "tools": [
            {
                "name": "tool_name",
                "description": "Tool description"
            }
        ]
    }
}
```

#### 3. tool/schema

**Purpose:** Get tool schema

**Request:**
```json
{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tool/schema",
    "params": {
        "name": "tool_name"
    }
}
```

**Response:**
```json
{
    "jsonrpc": "2.0",
    "id": 3,
    "result": {
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "output_schema": {
            "type": "object",
            "properties": {}
        }
    }
}
```

#### 4. tools/call

**Purpose:** Execute a tool

**Request:**
```json
{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
        "name": "tool_name",
        "arguments": {
            "param1": "value1"
        }
    }
}
```

**Response:**
```json
{
    "jsonrpc": "2.0",
    "id": 4,
    "result": {
        "content": [
            {
                "type": "text",
                "text": "Result text"
            }
        ]
    }
}
```

#### 5. ping

**Purpose:** Health check

**Request:**
```json
{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "ping",
    "params": {}
}
```

**Response:**
```json
{
    "jsonrpc": "2.0",
    "id": 5,
    "result": {
        "status": "OK",
        "timestamp": "2025-01-01T00:00:00.000Z"
    }
}
```

---

## Authentication Flow

### Token-Based Authentication

```
┌──────────┐                    ┌──────────┐
│  Client  │                    │  Server  │
└────┬─────┘                    └────┬─────┘
     │                               │
     │  POST /api/auth/login         │
     │  {username, password}         │
     ├──────────────────────────────>│
     │                               │
     │  {token, expires_in}          │
     │<──────────────────────────────┤
     │                               │
     │  POST /mcp                    │
     │  Authorization: Bearer token  │
     ├──────────────────────────────>│
     │                               │
     │  Response                     │
     │<──────────────────────────────┤
     │                               │
```

### Token Management

1. **Acquisition:**
   - Credentials sent to `/api/auth/login`
   - Token stored in `_auth_token`
   - Expiry tracked in `_token_expires_at`

2. **Usage:**
   - Added to HTTP headers: `Authorization: Bearer {token}`
   - Included in all MCP requests

3. **Renewal:**
   - Checked before each request
   - Auto-renewed when `datetime.now() >= _token_expires_at`
   - Expiry set to current time + 50 minutes

---

## Cache Management

### Cache Structure

```python
{
    "tool_name:abhikartamcp": MCPToolSchema(
        name="tool_name:abhikartamcp",
        description="Tool description",
        input_schema={...},
        output_schema={...},
        last_updated=datetime(2025, 1, 1, 0, 0, 0)
    )
}
```

### Refresh Algorithm

```python
async def _refresh_tool_cache():
    # 1. Ping server
    if not await _ping_server():
        return
    
    # 2. List tools
    tool_names = await _list_tools()
    
    # 3. Track current tools
    current_tools = set()
    
    # 4. For each tool:
    for tool_name in tool_names:
        # Get schema
        schema = await _get_tool_schema(tool_name)
        
        # Create cache key
        cache_key = f"{tool_name}:abhikartamcp"
        current_tools.add(cache_key)
        
        # Update or create cache entry
        if cache_key in cache:
            cache[cache_key].update(schema)
        else:
            cache[cache_key] = create_schema(schema)
    
    # 5. Remove stale entries
    for tool_name in (cache.keys() - current_tools):
        del cache[tool_name]
```

### Cache Invalidation

- **Time-based:** Every `refresh_interval_seconds`
- **Manual:** Via `force_refresh()`
- **On-demand:** Individual tool schema updates

---

## Registry Synchronization

### Sync Algorithm

```python
def sync_tools():
    # Get current state
    cached_tools = builder.get_all_schemas()
    cached_names = set(cached_tools.keys())
    registered_names = integration._registered_tools
    
    # Compute differences
    to_add = cached_names - registered_names
    to_remove = registered_names - cached_names
    to_update = cached_names & registered_names
    
    # Apply changes
    for name in to_add:
        tool = create_tool_from_schema(cached_tools[name])
        registry.register(tool, group, tags)
        registered_names.add(name)
    
    for name in to_remove:
        registry.unregister(name)
        registered_names.discard(name)
    
    for name in to_update:
        # Check if update needed
        if needs_update(name):
            registry.unregister(name)
            tool = create_tool_from_schema(cached_tools[name])
            registry.register(tool, group, tags)
```

### Concurrency Considerations

- Builder refresh and sync are separate operations
- Registry operations are assumed to be thread-safe
- No locking between builder and integration

---

## Performance Considerations

### Optimization Strategies

1. **Connection Pooling**
   - Single `httpx.AsyncClient` per builder
   - Reused across all requests
   - Closed on shutdown

2. **Batch Operations**
   - Sync processes all tools in one pass
   - Minimal registry operations

3. **Async I/O**
   - All network operations are async
   - Non-blocking tool execution
   - Concurrent schema retrieval possible

4. **Caching**
   - In-memory tool cache
   - No database overhead
   - Fast lookups

### Scalability

**Single Server:**
- Supports 100s of tools efficiently
- Limited by MCP server capacity

**Multiple Servers:**
- One builder per server
- Separate registries or shared registry
- Independent refresh cycles

### Benchmarks

Typical performance (local network):

```
Tool Discovery: ~100ms per tool
Schema Retrieval: ~50ms per tool
Full Refresh (10 tools): ~1-2 seconds
Tool Execution: Depends on tool (typically 50-500ms)
```

---

## Security

### Authentication

- Token-based authentication
- Tokens expire after 1 hour
- Automatic renewal before expiry
- Credentials stored in memory only

### Network Security

- HTTPS support via httpx
- Configurable timeouts
- No credential logging
- Token in header, not URL

### Error Handling

- Sensitive data not in error messages
- Failed auth doesn't expose credentials
- Proper exception handling throughout

### Best Practices

1. Use HTTPS in production
2. Store credentials in environment variables
3. Use short token expiry times
4. Monitor for authentication failures
5. Implement rate limiting
6. Validate all tool parameters

---

## Error Codes

### JSON-RPC Standard Errors

- `-32700`: Parse error
- `-32600`: Invalid request
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error

### Custom Errors

- `-32001`: Unauthorized
- `-32002`: Forbidden

---

## Future Enhancements

1. **Connection Pooling**: Multiple MCP servers
2. **Caching Strategies**: Redis support
3. **Metrics**: Prometheus integration
4. **Tracing**: OpenTelemetry support
5. **Retry Logic**: Exponential backoff
6. **Circuit Breaker**: Fault tolerance

---

## References

- MCP Specification: (Internal Document)
- JSON-RPC 2.0: https://www.jsonrpc.org/specification
- Abhikarta Tool Framework: (Internal Document)

---

**Document Version:** 1.0.0  
**Last Updated:** 2025-01-01  
**Author:** Ashutosh Sinha (ajsinha@gmail.com)
