# Abhikarta MCP Integration - Examples

**Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)**

---

## Overview

This directory contains comprehensive examples demonstrating how to use the Abhikarta MCP Integration with various tools.

---

## 📁 Available Examples

### 1. **basic_usage.py**
**Getting Started Example**

Demonstrates:
- Basic builder configuration
- Tool discovery
- Registry integration
- Simple tool execution
- Cleanup procedures

**Run:**
```bash
python examples/basic_usage.py
```

---

### 2. **advanced_usage.py**
**Advanced Features Example**

Demonstrates:
- Manual tool creation
- Error handling strategies
- Cache monitoring
- Full lifecycle management
- Mock-based testing

**Run:**
```bash
python examples/advanced_usage.py
```

---

### 3. **duckdb_tools_example.py** ⭐
**Complete DuckDB Analytics Examples**

**5 Comprehensive Examples:**

#### Example 1: List Available DuckDB Files
- Discover CSV, Parquet, JSON files
- Filter by file type
- View file metadata

#### Example 2: Describe Table Schema
- Get detailed column information
- View data types and constraints
- Include sample data

#### Example 3: Get Column Statistics
- Comprehensive statistical summaries
- Mean, std dev, percentiles
- Analyze specific columns

#### Example 4: Aggregate Data
- GROUP BY operations
- Multiple aggregation functions
- HAVING clauses
- Result ordering

#### Example 5: Complete Workflow
- End-to-end data analysis
- File discovery → Schema → Stats → Aggregation

**Run:**
```bash
python examples/duckdb_tools_example.py
```

**Tools Demonstrated:**
- `duckdb_list_files`
- `duckdb_describe_table`
- `duckdb_get_stats`
- `duckdb_aggregate`

---

### 4. **yahoo_finance_example.py** ⭐
**Complete Yahoo Finance Examples**

**5 Comprehensive Examples:**

#### Example 1: Search for Stock Symbols
- Search by company name
- Search by industry/sector
- Filter by exchange

#### Example 2: Get Real-Time Stock Quotes
- Current prices and statistics
- Market cap, P/E ratio, dividends
- Compare multiple stocks
- Track indices

#### Example 3: Get Historical Price Data
- Daily, hourly, minute-level data
- OHLCV (Open, High, Low, Close, Volume)
- Dividend and split events
- Multiple time periods

#### Example 4: Portfolio Monitoring
- Track multiple positions
- Calculate gains/losses
- Portfolio performance metrics
- Real-time valuation

#### Example 5: Market Research Workflow
- Sector analysis
- Company comparison
- Performance tracking
- Complete research cycle

**Run:**
```bash
python examples/yahoo_finance_example.py
```

**Tools Demonstrated:**
- `yahoo_search_symbols`
- `yahoo_get_quote`
- `yahoo_get_history`

---

## 🚀 Quick Start

### Prerequisites

1. **Install the package:**
```bash
cd abhikarta_mcp_integration
pip install -r requirements.txt
pip install -e .
```

2. **Configure MCP server:**
```bash
cp config_example.py config.py
# Edit config.py with your MCP server details
```

3. **Ensure MCP server is running:**
```bash
# Your MCP server should be accessible at http://localhost:3002
curl http://localhost:3002/mcp
```

### Run Examples

**Start with basic example:**
```bash
python examples/basic_usage.py
```

**Try DuckDB tools:**
```bash
python examples/duckdb_tools_example.py
```

**Try Yahoo Finance tools:**
```bash
python examples/yahoo_finance_example.py
```

---

## 📋 Example Structure

Each example follows this pattern:

```python
import asyncio
from abhikartamcp import AbhikartaMCPToolBuilder, MCPRegistryIntegration

async def example_function():
    # 1. Setup
    builder = AbhikartaMCPToolBuilder()
    builder.configure(...)
    
    registry = ToolRegistry()
    integration = MCPRegistryIntegration(registry, builder)
    
    try:
        # 2. Start and sync
        await builder.start()
        integration.sync_tools()
        
        # 3. Get tool
        tool = registry.get("tool_name:abhikartamcp")
        
        # 4. Execute tool
        result = await tool.execute_async(...)
        
        # 5. Process results
        print(result)
        
    finally:
        # 6. Cleanup
        await builder.stop()

asyncio.run(example_function())
```

---

## 🎯 Example Output

### DuckDB Tools Example Output:

```
==================================================
Example 1: List Available DuckDB Files
==================================================
✓ Found tool: duckdb_list_files:abhikartamcp
  Description: List available data files...

--- List All Data Files ---
Data directory: /data/duckdb
Total files: 15

  File: sales_data.csv
    Type: csv
    Size: 2.5 MB
    Modified: 2025-01-01T12:00:00Z
...
```

### Yahoo Finance Example Output:

```
==================================================
Example 2: Get Real-Time Stock Quotes
==================================================

--- Apple Inc. (AAPL) Quote ---
Apple Inc. (AAPL)
==================================================
Price:           $175.50
Change:          ▲ $2.30 (+1.33%)
Volume:          52,345,678
Market Cap:      $2,750,000,000,000

Day Range:       $173.20 - $176.80
52-Week Range:   $124.17 - $199.62

P/E Ratio:       28.45
Dividend Yield:  0.52%
...
```

---

## 🔧 Customization

### Modify Server Configuration

Edit examples to use your server:

```python
builder.configure(
    base_url="http://your-server:3002",  # Your MCP server
    username="your_username",             # Your credentials
    password="your_password",
    refresh_interval_seconds=300          # 5 minutes
)
```

### Add Custom Logic

Extend examples with your own logic:

```python
# After getting results
if result:
    data = result.get('data', result)
    
    # Your custom processing
    process_data(data)
    save_to_database(data)
    send_notification(data)
```

---

## 📊 Tool Schema Reference

### DuckDB Tools

**duckdb_list_files:**
```python
{
    "file_type": "csv|parquet|json|tsv|all",
    "include_metadata": True/False
}
```

**duckdb_describe_table:**
```python
{
    "table_name": "table_name",
    "include_sample_data": True/False,
    "sample_size": 5
}
```

**duckdb_get_stats:**
```python
{
    "table_name": "table_name",
    "columns": ["col1", "col2"],  # Optional
    "include_percentiles": True/False
}
```

**duckdb_aggregate:**
```python
{
    "table_name": "table_name",
    "aggregations": {"column": "sum|avg|count|min|max"},
    "group_by": ["col1", "col2"],
    "having": "condition",
    "order_by": [{"column": "col", "direction": "asc|desc"}],
    "limit": 100
}
```

### Yahoo Finance Tools

**yahoo_search_symbols:**
```python
{
    "query": "search term",
    "limit": 10,
    "exchange": "NYSE|NASDAQ|AMEX|all"
}
```

**yahoo_get_quote:**
```python
{
    "symbol": "AAPL"
}
```

**yahoo_get_history:**
```python
{
    "symbol": "AAPL",
    "period": "1d|5d|1mo|3mo|6mo|1y|2y|5y|10y|ytd|max",
    "interval": "1m|5m|15m|30m|1h|1d|1wk|1mo",
    "include_events": True/False
}
```

---

## 🐛 Troubleshooting

### Connection Errors

```python
# Add error handling
try:
    await builder.start()
except Exception as e:
    print(f"Connection failed: {e}")
    # Check server is running
    # Verify credentials
```

### Tool Not Found

```python
tool = registry.get("tool_name:abhikartamcp")
if not tool:
    print("Tool not found. Available tools:")
    print(builder.list_cached_tools())
```

### Rate Limiting

```python
# Add delays between requests
import asyncio
for symbol in symbols:
    result = await tool.execute_async(symbol=symbol)
    await asyncio.sleep(0.5)  # 500ms delay
```

---

## 📚 Related Documentation

- [Main README](../README.md)
- [Installation Guide](../docs/INSTALL.md)
- [Technical Documentation](../docs/TECHNICAL.md)
- [API Reference](../docs/README.md#api-reference)

---

## 💡 Tips

1. **Start Simple:** Begin with `basic_usage.py` to understand the flow
2. **Read Comments:** Each example has detailed comments explaining the code
3. **Experiment:** Modify parameters to see different results
4. **Error Handling:** Always wrap async code in try-finally blocks
5. **Rate Limiting:** Add delays when calling external APIs repeatedly

---

## 🎓 Learning Path

1. **Beginner:** Run `basic_usage.py`
2. **Intermediate:** Try specific tool examples
3. **Advanced:** Study `advanced_usage.py`
4. **Expert:** Create your own custom examples

---

## 📝 Adding Your Own Examples

To add a new example:

1. Create a new file: `examples/my_example.py`
2. Follow the pattern from existing examples
3. Add documentation comments
4. Test thoroughly
5. Update this README

---

## 🙏 Support

For issues with examples:

**Email:** ajsinha@gmail.com

Include:
- Which example
- Error message
- Python version
- MCP server status

---

**Happy Coding! 🚀**

Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
