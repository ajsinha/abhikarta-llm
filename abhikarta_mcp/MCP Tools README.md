# MCP Tools - Generic MCP Endpoint Integration for LLMs

**Copyright © 2025-2030 Ashutosh Sinha (ajsinha@gmail.com)**

---

## 🎯 What is This?

**MCP Tools** is a generic system for converting **Model Context Protocol (MCP)** endpoint schemas into LLM-compatible tool definitions. It bridges the gap between your MCP endpoints and LLM providers (OpenAI, Anthropic, Google, etc.).

### The Problem

You have MCP endpoints with schemas like this:

```json
{
  "name": "get_weather",
  "description": "Get current weather",
  "inputSchema": {
    "type": "object",
    "properties": {
      "location": {"type": "string"}
    },
    "required": ["location"]
  }
}
```

You need LLM tool definitions like this:

```json
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "Get current weather",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {"type": "string"}
      },
      "required": ["location"]
    }
  }
}
```

### The Solution

**MCP Tools handles the conversion and execution automatically!**

---

## ✨ Features

- ✅ **Generic** - Works with any MCP endpoint schema
- ✅ **LLM Agnostic** - Compatible with OpenAI, Anthropic, Google, etc.
- ✅ **Automatic Validation** - Validates arguments against schema
- ✅ **Error Handling** - Comprehensive error handling and retries
- ✅ **Flexible** - Three usage patterns to fit your architecture
- ✅ **Production Ready** - Type hints, logging, metadata tracking

---

## 🚀 Quick Start

### Installation

```bash
# Copy these files to your project:
# - mcp_tools.py
# - mcp_tools_integration.py (optional, for advanced patterns)
```

### Basic Usage (3 Lines)

```python
from mcp_tools import create_tool_from_mcp

# Your MCP schema + executor
tool = create_tool_from_mcp(mcp_schema, executor_function)

# Use with any LLM
llm_tool = tool.to_llm_tool_definition()
```

### Complete Example

```python
from mcp_tools import create_tool_from_mcp

# 1. Define your MCP endpoint schema
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

# 2. Define executor that calls your MCP endpoint
def get_weather_executor(args):
    # Call your actual MCP endpoint here
    location = args["location"]
    unit = args.get("unit", "celsius")
    
    # Return result from your MCP endpoint
    return {
        "location": location,
        "temperature": 22,
        "unit": unit,
        "conditions": "Sunny"
    }

# 3. Create the tool
tool = create_tool_from_mcp(mcp_schema, get_weather_executor)

# 4. Get LLM tool definition
llm_tool_def = tool.to_llm_tool_definition()

# 5. Use with your LLM
response = llm.chat_completion(
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=[llm_tool_def]
)

# 6. Execute tool when LLM calls it
if "tool_calls" in response:
    for tool_call in response["tool_calls"]:
        args = json.loads(tool_call["function"]["arguments"])
        result = tool.execute(args)
        
        if result.is_success():
            print(f"Weather: {result.data}")
```

---

## 📚 Three Usage Patterns

### Pattern 1: Just Convert (Simplest)

**Use when**: You only need schema conversion, handle execution separately.

```python
from mcp_tools import mcp_schemas_to_llm_tools

# Convert all schemas at once
llm_tools = mcp_schemas_to_llm_tools(mcp_schemas)

# Use immediately
response = llm.chat_completion(messages, tools=llm_tools)
```

### Pattern 2: Full Control (Most Flexible)

**Use when**: You want complete control over tool management and execution.

```python
from mcp_tools import MCPToolFactory, MCPToolRegistry

# Create factory with executors
factory = MCPToolFactory({
    "get_weather": weather_executor,
    "search_docs": search_executor
})

# Create registry
registry = MCPToolRegistry()

# Create and register tools
tools = factory.create_tools_from_mcp_schemas(mcp_schemas)
registry.register_multiple(tools)

# Use with LLM
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

### Pattern 3: Automatic (Most Convenient)

**Use when**: You want zero-boilerplate tool handling.

```python
from mcp_tools_integration import MCPToolEnabledLLM

# Wrap your LLM facade
enhanced_llm = MCPToolEnabledLLM(openai_facade)

# Register MCP endpoints
enhanced_llm.register_mcp_endpoints(mcp_schemas, executor_map)

# Just chat - tools handled automatically!
response = enhanced_llm.chat(
    "What's the weather in Paris and create a reminder?"
)
# System automatically handles tool calls and returns final response
```

---

## 🏗️ Architecture

```
┌─────────────────────┐
│   MCP Endpoint      │
│   Schema            │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  MCPToolFactory     │
│  create_tool_from   │
│  _mcp_schema()      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    MCPTool          │
│  (with executor)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  to_llm_tool_       │
│  definition()       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  LLM Tool           │
│  Definition         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  OpenAI/Anthropic/  │
│  Google/Cohere/etc  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Tool Call          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  tool.execute()     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  MCPToolResult      │
└─────────────────────┘
```

---

## 📦 Package Contents

| File | Description |
|------|-------------|
| `mcp_tools.py` | Core implementation (600+ lines) |
| `mcp_tools_examples.py` | 6 comprehensive examples |
| `mcp_tools_integration.py` | Advanced integration patterns |
| `MCP_TOOLS_DOCUMENTATION.md` | Complete documentation |
| `MCP_TOOLS_QUICKREF.md` | Quick reference guide |
| `README.md` | This file |

---

## 🎓 Examples

### Example 1: Weather Tool

```python
schema = {
    "name": "get_weather",
    "description": "Get weather",
    "inputSchema": {
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        },
        "required": ["location"]
    }
}

def executor(args):
    # Call your MCP endpoint
    return {"temp": 22, "location": args["location"]}

tool = create_tool_from_mcp(schema, executor)
result = tool.execute({"location": "Paris"})
print(result.data)  # {"temp": 22, "location": "Paris"}
```

### Example 2: Multiple Tools

```python
factory = MCPToolFactory()
registry = MCPToolRegistry()

# Register multiple executors
factory.register_executor("get_weather", weather_func)
factory.register_executor("search_docs", search_func)
factory.register_executor("create_task", task_func)

# Create all tools
tools = factory.create_tools_from_mcp_schemas([
    weather_schema,
    search_schema,
    task_schema
])

# Register and use
registry.register_multiple(tools)
llm_tools = registry.get_all_tool_definitions()
```

### Example 3: With LLM Integration

See `mcp_tools_integration.py` for complete working examples with actual LLM facades.

---

## 🔧 API Quick Reference

### Core Functions

```python
# Simple conversion
create_tool_from_mcp(schema, executor) → MCPTool

# Batch conversion (no executors)
mcp_schemas_to_llm_tools(schemas) → List[Dict]
```

### Core Classes

```python
# Tool creation
factory = MCPToolFactory(executor_registry)
tool = factory.create_tool_from_mcp_schema(schema, executor)

# Tool management
registry = MCPToolRegistry()
registry.register(tool)
registry.execute(name, args)

# Tool execution
tool = MCPTool(name, description, schema, executor)
result = tool.execute(args)
llm_def = tool.to_llm_tool_definition()
```

---

## ✅ Validation & Error Handling

### Automatic Validation

```python
# Arguments are validated against schema
result = tool.execute({"invalid": "args"})

if not result.is_success():
    print(f"Error: {result.error}")
    # Output: "Validation failed: Missing required field: location"
```

### Execution Errors

```python
# Execution errors are caught and wrapped
result = tool.execute({"location": "Paris"})

if result.is_success():
    print(result.data)
else:
    print(f"Error: {result.error}")
    print(f"Status: {result.status.value}")
```

---

## 🎯 Use Cases

1. **Microservices** - Convert service endpoints to LLM tools
2. **API Integration** - Expose APIs to LLMs
3. **Automation** - Let LLMs control external systems
4. **Data Access** - Give LLMs access to databases/services
5. **Multi-Agent Systems** - Tools for agent communication

---

## 📖 Documentation

- **Quick Reference**: [MCP_TOOLS_QUICKREF.md](computer:///mnt/user-data/outputs/MCP_TOOLS_QUICKREF.md)
- **Complete Docs**: [MCP_TOOLS_DOCUMENTATION.md](computer:///mnt/user-data/outputs/MCP_TOOLS_DOCUMENTATION.md)
- **Examples**: Run `python mcp_tools_examples.py`
- **Integration**: See `mcp_tools_integration.py`

---

## 🚦 Quick Decision Guide

**Need to convert schemas?**
- Just schemas → Use `mcp_schemas_to_llm_tools()`
- With execution → Use `MCPToolFactory` + `MCPToolRegistry`
- Automatic flow → Use `MCPToolEnabledLLM`

**Starting from scratch?**
1. Start with Pattern 1 (schema conversion)
2. Add Pattern 2 when you need execution
3. Use Pattern 3 for production

---

## 🔬 Testing

```python
# Test schema conversion
llm_tools = mcp_schemas_to_llm_tools(schemas)
assert len(llm_tools) == len(schemas)

# Test tool creation
tool = create_tool_from_mcp(schema, executor)
assert tool.name == schema["name"]

# Test execution
result = tool.execute(valid_args)
assert result.is_success()
assert result.data is not None
```

---

## 💡 Best Practices

### ✅ DO
- Validate schemas before conversion
- Add logging to executors
- Handle errors in executors gracefully
- Use registry for multiple tools
- Test tools independently

### ❌ DON'T
- Skip schema validation
- Ignore execution errors
- Hardcode API keys in executors
- Mix schema formats
- Skip error handling

---

## 🤝 Integration with LLM Facades

Works seamlessly with all LLM providers:

```python
# OpenAI
from facades.openai_facade import OpenAIFacade
llm = OpenAIFacade("gpt-4")

# Anthropic
from facades.anthropic_facade import AnthropicFacade
llm = AnthropicFacade("claude-3-opus-20240229")

# Google
from facades.google_facade import GoogleFacade
llm = GoogleFacade("gemini-pro")

# Use with any of them
response = llm.chat_completion(messages, tools=llm_tools)
```

---

## 🎉 Summary

**MCP Tools gives you three simple ways to use MCP endpoints with LLMs:**

1. **Convert** schemas to LLM format
2. **Execute** tools with validation and error handling  
3. **Automate** the entire tool calling flow

**Pick the pattern that fits your needs and start building!**

---

## 📞 Support

**Author**: Ashutosh Sinha  
**Email**: ajsinha@gmail.com

---

## 📜 License

Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.

---

**Get started in 3 lines of code. Scale to hundreds of tools.**