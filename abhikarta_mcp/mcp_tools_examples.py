"""
MCP Tools Usage Examples

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Comprehensive examples showing how to use the MCP Tool system.
"""

import json
from mcp_tools import (
    MCPToolFactory,
    MCPToolRegistry,
    create_tool_from_mcp,
    mcp_schemas_to_llm_tools
)


# =============================================================================
# Example 1: Simple Tool Creation from MCP Schema
# =============================================================================

def example_1_simple_tool():
    """Create a simple tool from an MCP schema."""
    print("=" * 60)
    print("Example 1: Simple Tool Creation")
    print("=" * 60)
    
    # Your MCP endpoint schema
    mcp_schema = {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit"
                }
            },
            "required": ["location"]
        }
    }
    
    # Define the executor function
    def get_weather_executor(args):
        """Actual implementation that calls your MCP endpoint."""
        location = args["location"]
        unit = args.get("unit", "celsius")
        
        # Here you would call your actual MCP endpoint
        # For demo, return mock data
        return {
            "location": location,
            "temperature": 22 if unit == "celsius" else 72,
            "unit": unit,
            "conditions": "Sunny"
        }
    
    # Create the tool
    tool = create_tool_from_mcp(mcp_schema, get_weather_executor)
    
    # Get LLM tool definition
    llm_tool_def = tool.to_llm_tool_definition()
    print("\nLLM Tool Definition:")
    print(json.dumps(llm_tool_def, indent=2))
    
    # Execute the tool
    result = tool.execute({"location": "Paris", "unit": "celsius"})
    print(f"\nExecution Result:")
    print(f"Status: {result.status.value}")
    print(f"Data: {result.data}")
    print(f"Execution Time: {result.execution_time:.3f}s")


# =============================================================================
# Example 2: Multiple Tools with Factory
# =============================================================================

def example_2_multiple_tools():
    """Create multiple tools using the factory."""
    print("\n" + "=" * 60)
    print("Example 2: Multiple Tools with Factory")
    print("=" * 60)
    
    # Multiple MCP schemas
    mcp_schemas = [
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
        },
        {
            "name": "search_database",
            "description": "Search the database",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Max results"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "send_email",
            "description": "Send an email",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body"}
                },
                "required": ["to", "subject", "body"]
            }
        }
    ]
    
    # Create executor functions
    def weather_executor(args):
        return {"temp": 22, "location": args["location"]}
    
    def search_executor(args):
        return {"results": [f"Result for: {args['query']}"]}
    
    def email_executor(args):
        return {"sent": True, "to": args["to"]}
    
    # Create factory with executors
    factory = MCPToolFactory()
    factory.register_executor("get_weather", weather_executor)
    factory.register_executor("search_database", search_executor)
    factory.register_executor("send_email", email_executor)
    
    # Create all tools
    tools = factory.create_tools_from_mcp_schemas(mcp_schemas)
    
    print(f"\nCreated {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # Get LLM tool definitions for all tools
    llm_tools = [tool.to_llm_tool_definition() for tool in tools]
    print(f"\nLLM Tool Definitions:")
    print(json.dumps(llm_tools, indent=2))


# =============================================================================
# Example 3: Using Tool Registry
# =============================================================================

def example_3_tool_registry():
    """Use the tool registry for managing tools."""
    print("\n" + "=" * 60)
    print("Example 3: Tool Registry")
    print("=" * 60)
    
    # Create registry
    registry = MCPToolRegistry()
    
    # Define MCP schemas
    mcp_schemas = [
        {
            "name": "calculate",
            "description": "Perform mathematical calculations",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"]
                    },
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["operation", "a", "b"]
            }
        },
        {
            "name": "get_user_info",
            "description": "Get user information",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"}
                },
                "required": ["user_id"]
            }
        }
    ]
    
    # Create executors
    def calculate_executor(args):
        ops = {
            "add": lambda a, b: a + b,
            "subtract": lambda a, b: a - b,
            "multiply": lambda a, b: a * b,
            "divide": lambda a, b: a / b if b != 0 else "Error: Division by zero"
        }
        op = args["operation"]
        return {"result": ops[op](args["a"], args["b"])}
    
    def user_info_executor(args):
        return {"user_id": args["user_id"], "name": "John Doe", "email": "john@example.com"}
    
    # Create factory and tools
    factory = MCPToolFactory({
        "calculate": calculate_executor,
        "get_user_info": user_info_executor
    })
    
    tools = factory.create_tools_from_mcp_schemas(mcp_schemas)
    
    # Register all tools
    registry.register_multiple(tools)
    
    print(f"\nRegistered tools: {registry.list_tools()}")
    print(f"Total tools: {len(registry)}")
    
    # Execute tools via registry
    print("\nExecuting 'calculate' tool:")
    result = registry.execute("calculate", {
        "operation": "multiply",
        "a": 6,
        "b": 7
    })
    print(f"Result: {result.data}")
    
    print("\nExecuting 'get_user_info' tool:")
    result = registry.execute("get_user_info", {"user_id": "123"})
    print(f"Result: {result.data}")
    
    # Get all tool definitions for LLM
    all_tools = registry.get_all_tool_definitions()
    print(f"\nAll tool definitions for LLM:")
    print(json.dumps(all_tools, indent=2))


# =============================================================================
# Example 4: Direct Schema to LLM Tools Conversion
# =============================================================================

def example_4_direct_conversion():
    """Convert MCP schemas directly to LLM tool definitions without executors."""
    print("\n" + "=" * 60)
    print("Example 4: Direct Schema Conversion")
    print("=" * 60)
    
    # You have a bunch of MCP endpoint schemas
    mcp_schemas = [
        {
            "name": "list_files",
            "description": "List files in a directory",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path"},
                    "recursive": {"type": "boolean", "description": "List recursively"}
                },
                "required": ["path"]
            }
        },
        {
            "name": "read_file",
            "description": "Read file contents",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path"}
                },
                "required": ["path"]
            }
        },
        {
            "name": "write_file",
            "description": "Write to a file",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"]
            }
        }
    ]
    
    # Convert directly to LLM tools
    llm_tools = mcp_schemas_to_llm_tools(mcp_schemas)
    
    print(f"\nConverted {len(llm_tools)} MCP schemas to LLM tools:")
    print(json.dumps(llm_tools, indent=2))
    
    # Now you can use these with your LLM
    print("\n" + "=" * 40)
    print("Ready to use with LLM:")
    print("=" * 40)
    print("""
    response = llm.chat_completion(
        messages=[{"role": "user", "content": "List files in /home"}],
        tools=llm_tools
    )
    """)


# =============================================================================
# Example 5: Complete Integration with LLM
# =============================================================================

def example_5_llm_integration():
    """Complete example integrating with LLM facade."""
    print("\n" + "=" * 60)
    print("Example 5: Complete LLM Integration")
    print("=" * 60)
    
    # Step 1: Define your MCP endpoints
    mcp_endpoints = [
        {
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
        },
        {
            "name": "search_docs",
            "description": "Search documentation",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {"type": "integer", "description": "Maximum results"}
                },
                "required": ["query"]
            }
        }
    ]
    
    # Step 2: Create executors
    def weather_executor(args):
        # Call your actual MCP endpoint here
        return {
            "location": args["location"],
            "temperature": 22,
            "unit": args.get("unit", "celsius"),
            "conditions": "Sunny"
        }
    
    def search_executor(args):
        # Call your actual MCP endpoint here
        return {
            "query": args["query"],
            "results": [
                {"title": "Doc 1", "url": "http://example.com/doc1"},
                {"title": "Doc 2", "url": "http://example.com/doc2"}
            ]
        }
    
    # Step 3: Set up factory and registry
    factory = MCPToolFactory({
        "get_weather": weather_executor,
        "search_docs": search_executor
    })
    
    registry = MCPToolRegistry()
    tools = factory.create_tools_from_mcp_schemas(mcp_endpoints)
    registry.register_multiple(tools)
    
    # Step 4: Get LLM tool definitions
    llm_tools = registry.get_all_tool_definitions()
    
    print("\nLLM Tools prepared:")
    for tool in llm_tools:
        print(f"  - {tool['function']['name']}")
    
    # Step 5: Simulate LLM interaction
    print("\n" + "=" * 40)
    print("Simulating LLM Interaction:")
    print("=" * 40)
    
    # This is what you would do with your actual LLM
    print("""
    # Send to LLM
    response = llm.chat_completion(
        messages=[
            {"role": "user", "content": "What's the weather in Paris?"}
        ],
        tools=llm_tools
    )
    
    # LLM decides to call get_weather
    if "tool_calls" in response:
        for tool_call in response["tool_calls"]:
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"])
            
            # Execute via registry
            result = registry.execute(tool_name, tool_args)
            
            if result.is_success():
                # Send result back to LLM
                tool_result_message = {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result.data)
                }
                
                # Continue conversation with tool result
                final_response = llm.chat_completion(
                    messages=[...previous_messages, tool_result_message]
                )
    """)
    
    # Demonstrate execution
    print("\nDemonstrating tool execution:")
    result = registry.execute("get_weather", {"location": "Paris"})
    print(f"\nTool: get_weather")
    print(f"Result: {result.data}")
    print(f"Status: {result.status.value}")


# =============================================================================
# Example 6: Error Handling and Validation
# =============================================================================

def example_6_error_handling():
    """Demonstrate error handling and validation."""
    print("\n" + "=" * 60)
    print("Example 6: Error Handling and Validation")
    print("=" * 60)
    
    mcp_schema = {
        "name": "divide_numbers",
        "description": "Divide two numbers",
        "inputSchema": {
            "type": "object",
            "properties": {
                "numerator": {"type": "number"},
                "denominator": {"type": "number"}
            },
            "required": ["numerator", "denominator"]
        }
    }
    
    def divide_executor(args):
        if args["denominator"] == 0:
            raise ValueError("Cannot divide by zero")
        return {"result": args["numerator"] / args["denominator"]}
    
    tool = create_tool_from_mcp(mcp_schema, divide_executor)
    
    # Test 1: Valid execution
    print("\nTest 1: Valid execution")
    result = tool.execute({"numerator": 10, "denominator": 2})
    print(f"Result: {result.data}, Status: {result.status.value}")
    
    # Test 2: Division by zero
    print("\nTest 2: Division by zero")
    result = tool.execute({"numerator": 10, "denominator": 0})
    print(f"Error: {result.error}, Status: {result.status.value}")
    
    # Test 3: Missing required field
    print("\nTest 3: Missing required field")
    result = tool.execute({"numerator": 10})
    print(f"Error: {result.error}, Status: {result.status.value}")
    
    # Test 4: Invalid type
    print("\nTest 4: Invalid type")
    result = tool.execute({"numerator": "ten", "denominator": 2})
    print(f"Error: {result.error}, Status: {result.status.value}")


# =============================================================================
# Run All Examples
# =============================================================================

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    example_1_simple_tool()
    example_2_multiple_tools()
    example_3_tool_registry()
    example_4_direct_conversion()
    example_5_llm_integration()
    example_6_error_handling()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
