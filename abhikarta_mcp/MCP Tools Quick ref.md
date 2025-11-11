# MCP Tools - Quick Reference Guide

**Copyright © 2025-2030 Ashutosh Sinha (ajsinha@gmail.com)**

---

## 🚀 30-Second Start

```python
from mcp_tools import create_tool_from_mcp

# Your MCP schema
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

# Your executor
def executor(args):
    return {"temp": 22, "location": args["location"]}

# Create & use
tool = create_tool_from_mcp(schema, executor)
llm_tool = tool.to_llm_tool_definition()  # Use with LLM
result = tool.execute({"location": "Paris"})  # Execute
```

---

## 📋 Three Usage Patterns

### Pattern 1: Just Convert (No Execution)

```python
from mcp_tools import mcp_schemas_to_llm_tools

# Convert MCP schemas → LLM tools instantly
llm_tools = mcp_schemas_to_llm_tools(mcp_schemas)

# Use with any LLM
response = llm.chat_completion(messages, tools=llm_tools)
```

**Use when**: You only need LLM tool definitions, handle execution separately.

---

### Pattern 2: Full Control (With Execution)

```python
from mcp_tools import MCPToolFactory, MCPToolRegistry

# Setup
factory = MCPToolFactory({"tool1": executor1, "tool2": executor2})
registry = MCPToolRegistry()

# Create tools
tools = factory.create_tools_from_mcp_schemas(schemas)
registry.register_multiple(tools)

# Get LLM tools
llm_tools = registry.get_all_tool_definitions()

# Use with LLM
response = llm.chat_completion(messages, tools=llm_tools)

# Execute when LLM calls tools
if "tool_calls" in response:
    for call in response["tool_calls"]:
        result = registry.execute(
            call["function"]["name"],
            json.loads(call["function"]["arguments"])
        )
```

**Use when**: You want full control over the execution flow.

---

### Pattern 3: Automatic (Zero Boilerplate)

```python
from mcp_tools_integration import MCPToolEnabledLLM

# Wrap your LLM
enhanced = MCPToolEnabledLLM(openai_facade)

# Register MCP endpoints
enhanced.register_mcp_endpoints(schemas, executor_map)

# Just chat - tools handled automatically!
response = enhanced.chat("What's the weather in Paris?")
```

**Use when**: You want the system to handle everything automatically.

---

## 🔧 Core Classes

### MCPTool
```python
tool = MCPTool(name, description, input_schema, executor)
tool.execute(args)  # Returns MCPToolResult
tool.to_llm_tool_definition()  # Get LLM format
tool.validate_arguments(args)  # Validate args
```

### MCPToolFactory
```python
factory = MCPToolFactory(executor_registry)
factory.register_executor(name, executor)
factory.create_tool_from_mcp_schema(schema, executor)
factory.create_tools_from_mcp_schemas(schemas)
factory.create_llm_tool_definitions(schemas)  # Direct conversion
```

### MCPToolRegistry
```python
registry = MCPToolRegistry()
registry.register(tool)
registry.register_multiple(tools)
registry.execute(name, args)
registry.get_all_tool_definitions()
registry.list_tools()
```

### MCPToolResult
```python
result = tool.execute(args)
result.is_success()  # bool
result.status  # MCPToolStatus enum
result.data  # Result data
result.error  # Error message if failed
result.execution_time  # Execution time in seconds
```

---

## 📝 Schema Format

### MCP Schema (Input)
```python
{
    "name": "tool_name",
    "description": "What it does",
    "inputSchema": {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "..."},
            "param2": {"type": "number"}
        },
        "required": ["param1"]
    }
}
```

### LLM Tool (Output)
```python
{
    "type": "function",
    "function": {
        "name": "tool_name",
        "description": "What it does",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "..."},
                "param2": {"type": "number"}
            },
            "required": ["param1"]
        }
    }
}
```

---

## 💡 Common Recipes

### Recipe 1: Single Tool
```python
from mcp_tools import create_tool_from_mcp

tool = create_tool_from_mcp(schema, executor)
llm_tool = tool.to_llm_tool_definition()
result = tool.execute(args)
```

### Recipe 2: Multiple Tools
```python
from mcp_tools import MCPToolFactory, MCPToolRegistry

factory = MCPToolFactory(executors)
registry = MCPToolRegistry()
tools = factory.create_tools_from_mcp_schemas(schemas)
registry.register_multiple(tools)
llm_tools = registry.get_all_tool_definitions()
```

### Recipe 3: Schema Conversion Only
```python
from mcp_tools import mcp_schemas_to_llm_tools

llm_tools = mcp_schemas_to_llm_tools(schemas)
# Use immediately with LLM
```

### Recipe 4: Handle LLM Tool Calls
```python
# After LLM returns tool_calls
for call in response["tool_calls"]:
    name = call["function"]["name"]
    args = json.loads(call["function"]["arguments"])
    result = registry.execute(name, args)
    
    # Send result back to LLM
    tool_message = {
        "role": "tool",
        "tool_call_id": call["id"],
        "content": json.dumps(result.data)
    }
```

---

## ⚡ Quick Tips

### ✅ DO
- Validate schemas before conversion
- Handle errors in executors
- Use registry for multiple tools
- Add retries for flaky endpoints
- Log tool executions

### ❌ DON'T
- Mix different schema formats
- Ignore validation errors
- Skip error handling in executors
- Hardcode timeouts
- Forget to test tools

---

## 🔍 Debugging

### Check Tool Definition
```python
tool = factory.create_tool_from_mcp_schema(schema)
print(json.dumps(tool.to_llm_tool_definition(), indent=2))
```

### Test Execution
```python
result = tool.execute(test_args)
print(f"Status: {result.status.value}")
print(f"Data: {result.data}")
print(f"Error: {result.error}")
print(f"Time: {result.execution_time}s")
```

### Validate Arguments
```python
is_valid, error = tool.validate_arguments(args)
if not is_valid:
    print(f"Validation error: {error}")
```

---

## 📚 Full Documentation

- **[MCP_TOOLS_DOCUMENTATION.md](computer:///mnt/user-data/outputs/MCP_TOOLS_DOCUMENTATION.md)** - Complete docs
- **[mcp_tools.py](computer:///mnt/user-data/outputs/mcp_tools.py)** - Core implementation
- **[mcp_tools_examples.py](computer:///mnt/user-data/outputs/mcp_tools_examples.py)** - 6 examples
- **[mcp_tools_integration.py](computer:///mnt/user-data/outputs/mcp_tools_integration.py)** - Integration patterns

---

## 🎯 Decision Tree

```
Do you need to execute tools?
├─ NO → Use Pattern 1 (mcp_schemas_to_llm_tools)
└─ YES
   ├─ Want full control? → Use Pattern 2 (Factory + Registry)
   └─ Want automatic? → Use Pattern 3 (MCPToolEnabledLLM)
```

---

## 📞 Support

**Author**: Ashutosh Sinha  
**Email**: ajsinha@gmail.com

---

**Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.**