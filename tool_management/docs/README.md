# Abhikarta LLM - Tool Management Framework

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

---

## Overview

A comprehensive, production-ready tool management framework for Large Language Models (LLMs). Provides a modular, extensible architecture supporting all tool types including **Model Context Protocol (MCP)** tools.

## Key Features

✨ **Universal Tool Support**
- API integrations
- Computational tools
- Data processing
- Communication services
- Knowledge retrieval
- **Native MCP support**
- Custom tools

🏗️ **Enterprise-Grade Architecture**
- Modular design with clean separation of concerns
- Standards-based (JSON Schema, MCP Protocol)
- Type-safe with full type hints
- Production-ready with comprehensive error handling

⚡ **Performance & Scalability**
- Async execution support
- Built-in caching middleware
- Rate limiting
- Batch processing capabilities

🔒 **Security First**
- Parameter validation
- Authentication middleware
- Rate limiting
- Sandboxed execution for computational tools

📊 **Observable**
- Execution metrics and statistics
- Comprehensive logging
- Performance tracking
- Middleware pipeline visibility

## Installation

```bash
pip install -e .
```

Or from PyPI (when published):
```bash
pip install abhikarta-tool-management
```

## Quick Start

```python
from tool_management import ToolRegistry, BaseTool, ToolParameter, ToolResult
from tool_management import ToolType, ParameterType
from tool_management.builtin import CalculatorTool

# Create registry
registry = ToolRegistry()

# Register built-in tool
calculator = CalculatorTool()
registry.register(calculator)

# Execute tool
result = await registry.execute("calculator", expression="sqrt(16) + 10")
print(result.data)  # {'expression': 'sqrt(16) + 10', 'result': 14.0}
```

## Creating Custom Tools

```python
class MyTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="My custom tool",
            tool_type=ToolType.CUSTOM
        )
        
        self.add_parameter(ToolParameter(
            name="input",
            param_type=ParameterType.STRING,
            description="Input data",
            required=True
        ))
    
    def execute(self, input: str) -> ToolResult:
        result = input.upper()
        return ToolResult.success_result(data=result)

# Register and use
registry.register(MyTool())
result = await registry.execute("my_tool", input="hello")
```

## MCP Integration

```python
from tool_management.mcp import MCPClient, discover_mcp_tools

# Connect to MCP server with HTTP transport
async with MCPClient(
    server_url="https://mcp.example.com",
    transport="http",  # Also supports "sse" and "stdio"
    headers={"Authorization": "Bearer token"}
) as client:
    # Discover and register MCP tools
    mcp_tools = await discover_mcp_tools(client)
    for tool in mcp_tools:
        registry.register(tool, group="mcp")
    
    # Use MCP tools like any other tool
    result = await registry.execute("mcp_tool_name", param1="value")
```

**Supported Transports**:
- **HTTP/REST** (recommended for production) - Network-based with full auth support
- **SSE** (Server-Sent Events) - Real-time streaming
- **stdio** - Local process communication

## Middleware System

```python
from tool_management.execution import RateLimiter, CachingMiddleware

# Add rate limiting
limiter = RateLimiter(max_calls=100, time_window=60)
registry.add_middleware(limiter)

# Add caching
cache = CachingMiddleware(ttl=300)  # 5 minutes
registry.add_middleware(cache)
```

## LLM Integration

### With Anthropic Claude

```python
import anthropic

# Get tool schemas
schemas = registry.get_all_schemas(format="anthropic")

# Use with Claude
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    tools=schemas,
    messages=[{"role": "user", "content": "Calculate 2+2"}]
)
```

### With OpenAI

```python
import openai

# Get tool schemas
schemas = registry.get_all_schemas(format="openai")

# Use with GPT
response = openai.chat.completions.create(
    model="gpt-4",
    tools=schemas,
    messages=[{"role": "user", "content": "Calculate 2+2"}]
)
```

## Documentation

- **[Architecture Documentation](docs/ARCHITECTURE.md)** - Comprehensive architecture overview
- **[Quick Reference Guide](docs/QUICK_REFERENCE.md)** - Quick reference for common tasks
- **[Examples](examples/)** - Working code examples

## Project Structure

```
abhikarta_llm/
├── tool_management/          # Main module
│   ├── core/                 # Core abstractions
│   ├── registry/             # Tool registry
│   ├── execution/            # Execution engine & middleware
│   ├── mcp/                  # MCP integration
│   ├── builtin/              # Built-in tools
│   └── utils/                # Utilities
├── docs/                     # Documentation
├── examples/                 # Example code
├── tests/                    # Test suite
├── LICENSE                   # License file
├── README.md                 # This file
├── setup.py                  # Setup configuration
└── requirements.txt          # Dependencies
```

## Built-in Tools

### CalculatorTool
Safe mathematical expression evaluator with support for basic arithmetic and math functions.

### JSONValidatorTool
Validates and formats JSON data.

### TextAnalyzerTool
Analyzes text and provides statistics (word count, character count, etc.).

## Requirements

- Python 3.9+
- Type hints support
- asyncio support

## Development

### Running Examples

```bash
cd examples
python basic_usage.py
```

### Running Tests

```bash
pytest tests/
```

## License

Copyright © 2025-2030, All Rights Reserved  
Ashutosh Sinha (ajsinha@gmail.com)

This software and associated documentation are proprietary and confidential. 
Unauthorized copying, distribution, modification, or use is strictly prohibited 
without explicit written permission from the copyright holder.

**Patent Pending**: Certain architectural patterns and implementations may be 
subject to patent applications.

## Support

For questions, issues, or support:
- Email: ajsinha@gmail.com

## Roadmap

- [ ] Additional built-in tools (HTTP client, database tools, file system tools)
- [ ] Streaming execution support
- [ ] Tool versioning system
- [ ] GraphQL tool integration
- [ ] WebSocket tool support
- [ ] Enhanced monitoring and observability
- [ ] Tool marketplace/catalog
- [ ] Plugin system for external tool providers

## Contributing

This is proprietary software. Contributions are accepted only under explicit 
agreement with the copyright holder.

## Acknowledgments

Built with modern Python best practices and inspired by industry-leading 
tool management systems.

---

**Made with ❤️ by Ashutosh Sinha**
