# Project Structure

**Abhikarta MCP Integration**  
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)

---

## Directory Structure

```
abhikarta_mcp_integration/
│
├── abhikartamcp/                          # Main package directory
│   ├── __init__.py                        # Package initialization
│   ├── abhikarta_mcp_tool_builder.py      # Tool discovery and caching
│   ├── abhikarta_base_tool.py             # Tool wrapper implementation
│   └── registry_integration.py            # Registry synchronization
│
├── examples/                              # Usage examples
│   ├── basic_usage.py                     # Basic integration example
│   └── advanced_usage.py                  # Advanced features example
│
├── tests/                                 # Test suite
│   ├── __init__.py                        # Test package initialization
│   └── test_basic.py                      # Basic unit tests
│
├── README.md                              # Main documentation
├── TECHNICAL.md                           # Technical documentation
├── INSTALL.md                             # Installation guide
├── CHANGELOG.md                           # Version history
├── LICENSE                                # License information
├── PROJECT_STRUCTURE.md                   # This file
│
├── setup.py                               # Package installation script
├── requirements.txt                       # Python dependencies
└── config_example.py                      # Configuration template
```

---

## File Descriptions

### Core Package (`abhikartamcp/`)

#### `__init__.py`
- Package initialization and exports
- Defines public API
- Version information

#### `abhikarta_mcp_tool_builder.py` (500+ lines)
- **Class:** `AbhikartaMCPToolBuilder`
- **Pattern:** Singleton
- **Purpose:** Tool discovery and caching
- **Key Features:**
  - JSON-RPC communication
  - Authentication management
  - Periodic cache refresh
  - Health monitoring
- **Dependencies:** httpx, asyncio

#### `abhikarta_base_tool.py` (400+ lines)
- **Class:** `AbhikartaBaseTool`
- **Pattern:** Adapter
- **Purpose:** Tool execution wrapper
- **Key Features:**
  - BaseTool extension
  - Parameter validation
  - Sync/async execution
  - MCP protocol communication
- **Type:** ToolType.ABHIKARTAMCP

#### `registry_integration.py` (350+ lines)
- **Classes:** 
  - `MCPRegistryIntegration`
  - `MCPAutoSync`
- **Purpose:** Registry synchronization
- **Key Features:**
  - Automatic tool registration
  - Periodic synchronization
  - Tool lifecycle management
  - Group and tag management

---

## Documentation Files

### `README.md`
- Quick start guide
- Feature overview
- API reference
- Usage examples
- Best practices

### `TECHNICAL.md`
- System architecture
- Component design
- Protocol specification
- Performance considerations
- Security details

### `INSTALL.md`
- Installation methods
- Configuration guide
- Verification steps
- Troubleshooting

### `CHANGELOG.md`
- Version history
- Feature additions
- Bug fixes
- Breaking changes

---

## Examples

### `examples/basic_usage.py`
Demonstrates:
- Builder configuration
- Tool discovery
- Registry integration
- Basic tool execution

### `examples/advanced_usage.py`
Demonstrates:
- Manual tool creation
- Error handling
- Cache monitoring
- Full lifecycle management
- Mock testing

---

## Tests

### `tests/test_basic.py`
Contains:
- Unit tests for all components
- Mock-based tests
- Async operation tests
- Integration tests

Test coverage includes:
- Configuration management
- Singleton pattern
- Tool creation
- Registry integration
- Async operations

---

## Configuration

### `config_example.py`
Provides templates for:
- MCP server configuration
- Registry settings
- Logging configuration
- Environment-specific configs
- Production examples

---

## Package Files

### `setup.py`
- Package metadata
- Dependencies
- Installation configuration
- PyPI information

### `requirements.txt`
- Core dependencies
- Version specifications
- Optional dependencies

---

## File Statistics

```
Total Files: 16
Total Lines: ~3,500
Languages: Python 100%

Code Distribution:
- Core Implementation: 45%
- Documentation: 35%
- Examples: 10%
- Tests: 7%
- Configuration: 3%
```

---

## Import Hierarchy

```
Application Code
    ↓
abhikartamcp
    ↓
    ├── AbhikartaMCPToolBuilder
    │       ↓
    │   (httpx, asyncio)
    │
    ├── AbhikartaBaseTool
    │       ↓
    │   tool_management.core.base
    │
    └── MCPRegistryIntegration
            ↓
        tool_management.registry
```

---

## Key Design Patterns

1. **Singleton Pattern**
   - `AbhikartaMCPToolBuilder`
   - Ensures single instance for caching

2. **Adapter Pattern**
   - `AbhikartaBaseTool`
   - Adapts MCP tools to framework interface

3. **Observer Pattern**
   - `MCPAutoSync`
   - Monitors and responds to cache changes

4. **Factory Pattern**
   - `_create_tool_from_schema()`
   - Creates tool instances from schemas

---

## Module Dependencies

### External Dependencies
```
httpx (HTTP client)
asyncio (Async operations)
```

### Framework Dependencies
```
tool_management.core.base
tool_management.core.types
tool_management.core.parameters
tool_management.core.results
tool_management.registry.registry
```

### Standard Library
```
logging
threading
time
datetime
dataclasses
typing
json
```

---

## Extension Points

The package is designed for extension:

1. **Custom Transport**
   - Extend `_send_mcp_request()` for new protocols

2. **Custom Caching**
   - Replace `_tool_cache` with Redis/database

3. **Custom Authentication**
   - Override `_authenticate()` method

4. **Custom Tool Types**
   - Extend `AbhikartaBaseTool` for specific needs

5. **Middleware**
   - Add pre/post execution hooks

---

## Performance Characteristics

### Memory Usage
- **Idle:** ~10MB
- **With 100 tools cached:** ~20MB
- **During execution:** +5MB per concurrent tool

### Timing
- **Initial discovery:** 1-2s for 10 tools
- **Cache refresh:** <2s for 50 tools
- **Tool execution:** 50-500ms (network dependent)

---

## Version Information

**Version:** 1.0.0  
**Python:** 3.8+  
**Release Date:** 2025-01-01  
**Status:** Stable

---

## License

Proprietary - See LICENSE file for details

Copyright © 2025-2030, All Rights Reserved  
Ashutosh Sinha (ajsinha@gmail.com)
