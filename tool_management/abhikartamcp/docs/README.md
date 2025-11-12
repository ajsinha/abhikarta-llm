# Abhikarta MCP Integration

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

---

## Legal Notice

This document and the associated software architecture are proprietary and confidential. Unauthorized copying, distribution, modification, or use of this document or the software system it describes is strictly prohibited without explicit written permission from the copyright holder. This document is provided "as is" without warranty of any kind, either expressed or implied. The copyright holder shall not be liable for any damages arising from the use of this document or the software system it describes.

**Patent Pending:** Certain architectural patterns and implementations described in this document may be subject to patent applications.

---

## Overview

The Abhikarta MCP Integration module provides seamless integration between the Abhikarta Tool Management Framework and Abhikarta MCP servers using the Model Context Protocol (MCP). This integration enables dynamic tool discovery, automatic registration, and execution of tools from MCP servers.

### Key Features

- **Dynamic Tool Discovery**: Automatically discovers tools from MCP server
- **Intelligent Caching**: Maintains a local cache of tool schemas with periodic refresh
- **Automatic Registration**: Syncs discovered tools with the Tool Registry
- **Authentication Support**: Handles token-based authentication with automatic renewal
- **Health Monitoring**: Built-in health checks and connectivity monitoring
- **Async Execution**: Fully asynchronous tool execution support
- **Schema Validation**: Automatic parameter validation based on JSON schemas

---

## Architecture

The integration consists of four main components:

### 1. AbhikartaMCPToolBuilder

A singleton class responsible for:
- Connecting to the MCP server via JSON-RPC protocol
- Discovering available tools using `tools/list` calls
- Retrieving tool schemas using `tool/schema` calls
- Maintaining a cache of tool metadata
- Periodic refresh of tool information
- Managing authentication tokens

### 2. AbhikartaBaseTool

A tool wrapper class that:
- Extends the base `BaseTool` class
- Implements `ToolType.ABHIKARTAMCP`
- Executes tools via `tools/call` JSON-RPC requests
- Handles parameter validation
- Provides both sync and async execution modes
- Supports health checks via `ping` requests

### 3. MCPRegistryIntegration

Manages the bridge between builder and registry:
- Synchronizes cached tools with the Tool Registry
- Registers new tools as they are discovered
- Unregisters tools that are no longer available
- Updates existing tools when schemas change
- Applies consistent grouping and tagging

### 4. MCPAutoSync

A background service that:
- Runs periodic synchronization
- Monitors for tool changes
- Maintains registry consistency
- Provides manual sync triggers

---

## Installation

### Prerequisites

```bash
pip install httpx asyncio
```

### Package Installation

```python
# Copy the abhikartamcp module to your project
# Ensure it's in your PYTHONPATH or tool_management directory
```

---

## Quick Start

### Basic Usage

```python
import asyncio
from abhikartamcp import (
    AbhikartaMCPToolBuilder,
    MCPRegistryIntegration,
    MCPAutoSync
)
from tool_management.registry import ToolRegistry

async def main():
    # 1. Configure the builder
    builder = AbhikartaMCPToolBuilder()
    builder.configure(
        base_url="http://localhost:3002",
        username="admin",
        password="your_password",
        refresh_interval_seconds=600  # 10 minutes
    )
    
    # 2. Start the builder
    await builder.start()
    
    # 3. View discovered tools
    tools = builder.list_cached_tools()
    print(f"Discovered {len(tools)} tools")
    
    # 4. Set up registry integration
    registry = ToolRegistry()
    integration = MCPRegistryIntegration(registry, builder)
    integration.sync_tools()
    
    # 5. Optional: Start auto-sync
    auto_sync = MCPAutoSync(integration, sync_interval_seconds=120)
    await auto_sync.start()
    
    # 6. Execute a tool
    tool = registry.get("some_tool:abhikartamcp")
    if tool:
        result = await tool.execute_async(param1="value1")
        print(result)
    
    # 7. Cleanup
    await auto_sync.stop()
    await builder.stop()

asyncio.run(main())
```

---

## Configuration

### MCP Server Configuration

```python
from abhikartamcp import MCPServerConfig

config = MCPServerConfig(
    base_url="http://localhost:3002",
    mcp_endpoint="/mcp",
    login_endpoint="/api/auth/login",
    tool_list_endpoint="/api/tools/list",
    tool_schema_endpoint_template="/api/tools/{tool_name}/schema",
    username="admin",
    password="password",
    refresh_interval_seconds=600,
    timeout_seconds=30.0,
    tool_name_suffix=":abhikartamcp"
)

builder = AbhikartaMCPToolBuilder()
builder.config = config
```

### Builder Configuration

```python
builder.configure(
    base_url="http://your-server:3002",
    username="your_username",
    password="your_password",
    refresh_interval_seconds=300,  # 5 minutes
    timeout_seconds=60.0
)
```

---

## API Reference

### AbhikartaMCPToolBuilder

#### Methods

**`configure(base_url, username, password, refresh_interval_seconds, timeout_seconds)`**
- Configure connection parameters
- Returns: self (for method chaining)

**`async start()`**
- Start the builder and begin tool discovery
- Authenticates with the server
- Performs initial cache refresh
- Starts periodic refresh task

**`async stop()`**
- Stop the builder and cleanup resources
- Cancels periodic refresh
- Closes HTTP connections

**`get_tool_schema(tool_name)`**
- Get cached schema for a tool
- Args: `tool_name` (str)
- Returns: `MCPToolSchema` or `None`

**`list_cached_tools()`**
- Get list of all cached tool names
- Returns: `List[str]`

**`get_all_schemas()`**
- Get all cached tool schemas
- Returns: `Dict[str, MCPToolSchema]`

**`get_cache_stats()`**
- Get cache statistics
- Returns: `Dict[str, Any]`

**`async force_refresh()`**
- Force immediate cache refresh

---

### AbhikartaBaseTool

#### Constructor

```python
AbhikartaBaseTool(
    name: str,
    description: str,
    mcp_base_url: str,
    mcp_endpoint: str = "/mcp",
    input_schema: Optional[Dict] = None,
    output_schema: Optional[Dict] = None,
    auth_token: Optional[str] = None,
    timeout: float = 30.0,
    version: str = "1.0.0"
)
```

#### Methods

**`execute(**kwargs)`**
- Execute tool synchronously
- Args: Tool-specific parameters
- Returns: `ToolResult`

**`async execute_async(**kwargs)`**
- Execute tool asynchronously
- Args: Tool-specific parameters
- Returns: `ToolResult`

**`async ping()`**
- Check server connectivity
- Returns: `bool`

**`set_auth_token(token)`**
- Update authentication token
- Args: `token` (str)

**`async cleanup()`**
- Cleanup resources

---

### MCPRegistryIntegration

#### Constructor

```python
MCPRegistryIntegration(
    registry: ToolRegistry,
    builder: Optional[AbhikartaMCPToolBuilder] = None,
    group_name: str = "abhikarta_mcp",
    tags: Optional[List[str]] = None
)
```

#### Methods

**`sync_tools()`**
- Synchronize tools between cache and registry
- Registers new tools
- Removes obsolete tools
- Updates existing tools

**`get_registered_tool_names()`**
- Get list of registered MCP tools
- Returns: `List[str]`

**`get_stats()`**
- Get integration statistics
- Returns: `Dict`

---

### MCPAutoSync

#### Constructor

```python
MCPAutoSync(
    integration: MCPRegistryIntegration,
    sync_interval_seconds: int = 60
)
```

#### Methods

**`async start()`**
- Start auto-sync service
- Performs initial sync
- Starts periodic sync loop

**`async stop()`**
- Stop auto-sync service

**`force_sync()`**
- Force immediate synchronization

---

## MCP Protocol

The integration uses JSON-RPC 2.0 protocol for communication:

### Request Format

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "method_name",
    "params": {
        "param1": "value1"
    }
}
```

### Response Format

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "data": "result_data"
    }
}
```

### Supported Methods

- `initialize`: Initialize connection
- `tools/list`: List available tools
- `tool/schema`: Get tool schema
- `tools/call`: Execute a tool
- `ping`: Health check

---

## Error Handling

### Connection Errors

```python
try:
    await builder.start()
except Exception as e:
    print(f"Connection failed: {e}")
    # Handle connection error
```

### Authentication Errors

```python
builder.configure(username="user", password="pass")
await builder.start()

if not builder._auth_token:
    print("Authentication failed")
    # Handle auth error
```

### Tool Execution Errors

```python
result = await tool.execute_async(param="value")

if result.status == "failure":
    print(f"Error: {result.error}")
    print(f"Type: {result.error_type}")
```

---

## Best Practices

### 1. Use Async Context Managers

```python
async with builder:
    # Builder automatically starts and stops
    tools = builder.list_cached_tools()
```

### 2. Monitor Cache Health

```python
stats = builder.get_cache_stats()
if stats['total_tools'] == 0:
    print("Warning: No tools cached")
```

### 3. Handle Periodic Refresh

```python
# Use auto-sync for production
auto_sync = MCPAutoSync(integration, sync_interval_seconds=120)
await auto_sync.start()
```

### 4. Validate Tool Parameters

```python
# Check tool schema before execution
schema = builder.get_tool_schema("tool:abhikartamcp")
if schema:
    print(f"Required params: {schema.input_schema.get('required', [])}")
```

### 5. Graceful Shutdown

```python
try:
    # Your application logic
    pass
finally:
    await auto_sync.stop()
    await builder.stop()
```

---

## Troubleshooting

### Issue: No Tools Discovered

**Solution:**
1. Check server connectivity: `await builder._ping_server()`
2. Verify authentication credentials
3. Check server logs for errors
4. Ensure MCP endpoint is correct

### Issue: Tools Not Executing

**Solution:**
1. Verify tool is registered: `registry.get("tool_name")`
2. Check authentication token is valid
3. Review parameter requirements in schema
4. Test with `ping()` method first

### Issue: Periodic Refresh Not Working

**Solution:**
1. Ensure builder is started: `builder._running`
2. Check refresh interval configuration
3. Review logs for refresh errors
4. Verify server availability

---

## Examples

See the `examples/` directory for complete working examples:

- `basic_usage.py`: Simple integration setup
- `advanced_usage.py`: Advanced features and error handling

---

## Support

For issues, questions, or contributions:

**Email:** ajsinha@gmail.com

---

## License

Copyright © 2025-2030, All Rights Reserved  
Ashutosh Sinha (ajsinha@gmail.com)

This software is proprietary and confidential. Unauthorized use is prohibited.

---

## Changelog

### Version 1.0.0 (2025)
- Initial release
- Dynamic tool discovery
- Automatic registration
- Authentication support
- Health monitoring
- Async execution support
