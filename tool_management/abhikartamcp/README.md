# Abhikarta MCP Integration v1.0.0

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install package
pip install -e .

# 3. Run examples
python examples/basic_usage.py
python examples/duckdb_tools_example.py
python examples/yahoo_finance_example.py
```

---

## 📦 What's Included

### **Core Module** (`abhikartamcp/`)
- `abhikarta_mcp_tool_builder.py` - Tool discovery and caching
- `abhikarta_base_tool.py` - Tool wrapper implementation
- `registry_integration.py` - Registry synchronization

### **Examples** (`examples/`)
- `basic_usage.py` - Getting started guide
- `advanced_usage.py` - Advanced features
- **`duckdb_tools_example.py`** - Complete DuckDB tools examples ⭐
- **`yahoo_finance_example.py`** - Complete Yahoo Finance tools examples ⭐

### **Documentation** (`docs/`)
- `README.md` - Complete user guide
- `TECHNICAL.md` - Architecture details
- `INSTALL.md` - Installation guide
- `PROJECT_STRUCTURE.md` - File organization
- `CHANGELOG.md` - Version history

### **Configuration**
- `setup.py` - Package installation
- `requirements.txt` - Dependencies
- `config_example.py` - Configuration templates

---

## 🎯 Features

✅ **Dynamic Tool Discovery** from MCP server  
✅ **Automatic Registry Integration**  
✅ **Periodic Cache Refresh** (configurable)  
✅ **Token-Based Authentication** with auto-renewal  
✅ **JSON-RPC 2.0 Protocol** support  
✅ **Sync & Async Execution** modes  
✅ **Schema-Based Validation**  
✅ **Health Monitoring**  

---

## 📚 Documentation

### Quick Links
- **[Complete User Guide](docs/README.md)** - Full documentation with API reference
- **[Installation Guide](docs/INSTALL.md)** - Step-by-step installation
- **[Technical Documentation](docs/TECHNICAL.md)** - Architecture and design
- **[Project Structure](docs/PROJECT_STRUCTURE.md)** - File organization

### Tool Examples
- **[DuckDB Tools](examples/duckdb_tools_example.py)** - Data analytics examples
- **[Yahoo Finance Tools](examples/yahoo_finance_example.py)** - Financial data examples

---

## 🛠️ Available Tool Examples

### DuckDB Analytics Tools
- `duckdb_list_files` - List available data files
- `duckdb_describe_table` - Get table schema
- `duckdb_get_stats` - Statistical summaries
- `duckdb_aggregate` - GROUP BY aggregations

### Yahoo Finance Tools
- `yahoo_search_symbols` - Search stock symbols
- `yahoo_get_quote` - Real-time quotes
- `yahoo_get_history` - Historical OHLCV data

---

## 💡 Usage Example

```python
import asyncio
from abhikartamcp import AbhikartaMCPToolBuilder, MCPRegistryIntegration
from tool_management.registry import ToolRegistry

async def main():
    # Setup
    builder = AbhikartaMCPToolBuilder()
    builder.configure(
        base_url="http://localhost:3002",
        username="admin",
        password="your_password"
    )
    
    # Start and sync
    await builder.start()
    
    registry = ToolRegistry()
    integration = MCPRegistryIntegration(registry, builder)
    integration.sync_tools()
    
    # Use a tool
    tool = registry.get("duckdb_list_files:abhikartamcp")
    result = await tool.execute_async(file_type="csv")
    print(result)
    
    # Cleanup
    await builder.stop()

asyncio.run(main())
```

---

## 📋 Requirements

- Python 3.8+
- httpx library
- Abhikarta Tool Management Framework

---

## 🔒 License

**Proprietary License** - See [LICENSE](LICENSE) file

Copyright © 2025-2030, All Rights Reserved  
Ashutosh Sinha (ajsinha@gmail.com)

---

## 📞 Support

**Email:** ajsinha@gmail.com

Include:
- Python version
- Operating system
- Error messages (if any)
- Configuration (sanitized)

---

## 🌟 Key Components

### 1. AbhikartaMCPToolBuilder
Singleton class for tool discovery and caching
- Connects to MCP server via JSON-RPC
- Periodic refresh (default: 10 minutes)
- Authentication token management

### 2. AbhikartaBaseTool
Tool wrapper extending BaseTool
- Type: `ToolType.ABHIKARTAMCP`
- Executes via `tools/call` method
- Supports sync and async execution

### 3. MCPRegistryIntegration
Registry synchronization manager
- Automatic tool registration/removal
- Group and tag management
- Update detection

### 4. MCPAutoSync
Background synchronization service
- Periodic registry updates
- Manual sync trigger
- Error recovery

---

## 📈 Version

**Current Version:** 1.0.0  
**Release Date:** 2025-01-01  
**Status:** Stable

For version history, see [CHANGELOG.md](docs/CHANGELOG.md)

---

**Built with ❤️ by Ashutosh Sinha**

Enterprise-grade integration for the Abhikarta Tool Management Framework
