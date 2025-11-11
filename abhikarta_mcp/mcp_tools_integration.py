"""
MCP Tools Integration Guide

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Practical guide for integrating MCP tools with LLM facades.
"""

import json
from typing import List, Dict, Any
from mcp_tools import MCPToolFactory, MCPToolRegistry


# =============================================================================
# Pattern 1: Simple MCP Endpoint Wrapper
# =============================================================================

class MCPEndpointWrapper:
    """
    Wrapper for MCP endpoints that converts them into LLM-compatible tools.
    
    Use this when you have a set of MCP endpoint schemas and want to use
    them directly with LLMs.
    """
    
    def __init__(self):
        self.registry = MCPToolRegistry()
        self.factory = MCPToolFactory()
    
    def load_mcp_endpoints(
        self,
        endpoints: List[Dict[str, Any]],
        executor_map: Dict[str, callable]
    ):
        """
        Load MCP endpoints and their executors.
        
        Args:
            endpoints: List of MCP endpoint schemas
            executor_map: Mapping of endpoint names to executor functions
        """
        # Register all executors
        for name, executor in executor_map.items():
            self.factory.register_executor(name, executor)
        
        # Create tools from schemas
        tools = self.factory.create_tools_from_mcp_schemas(endpoints)
        
        # Register tools
        self.registry.register_multiple(tools)
        
        return len(tools)
    
    def get_llm_tools(self) -> List[Dict[str, Any]]:
        """Get all tools in LLM-compatible format."""
        return self.registry.get_all_tool_definitions()
    
    def execute_tool(self, name: str, arguments: Dict[str, Any]):
        """Execute a tool by name."""
        return self.registry.execute(name, arguments)
    
    def handle_llm_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process tool calls from LLM response.
        
        Args:
            tool_calls: Tool calls from LLM response
        
        Returns:
            List of tool results ready to send back to LLM
        """
        results = []
        
        for tool_call in tool_calls:
            tool_id = tool_call.get("id", "")
            function_name = tool_call["function"]["name"]
            function_args = json.loads(tool_call["function"]["arguments"])
            
            # Execute the tool
            result = self.execute_tool(function_name, function_args)
            
            # Format for LLM
            tool_result = {
                "role": "tool",
                "tool_call_id": tool_id,
                "name": function_name,
                "content": json.dumps(result.data) if result.is_success() else json.dumps({"error": result.error})
            }
            
            results.append(tool_result)
        
        return results


# =============================================================================
# Pattern 2: Complete LLM Integration
# =============================================================================

class MCPToolEnabledLLM:
    """
    Wrapper that adds MCP tool support to any LLM facade.
    
    This allows you to use MCP endpoints as tools with any LLM provider.
    """
    
    def __init__(self, llm_facade):
        """
        Initialize with an LLM facade.
        
        Args:
            llm_facade: Any LLM facade (OpenAI, Anthropic, etc.)
        """
        self.llm = llm_facade
        self.mcp_wrapper = MCPEndpointWrapper()
        self.conversation_history = []
    
    def register_mcp_endpoints(
        self,
        endpoints: List[Dict[str, Any]],
        executor_map: Dict[str, callable]
    ):
        """Register MCP endpoints as tools."""
        count = self.mcp_wrapper.load_mcp_endpoints(endpoints, executor_map)
        print(f"Registered {count} MCP tools")
    
    def chat(
        self,
        message: str,
        max_tool_iterations: int = 5
    ) -> str:
        """
        Chat with the LLM, automatically handling tool calls.
        
        Args:
            message: User message
            max_tool_iterations: Maximum number of tool call iterations
        
        Returns:
            Final response from LLM
        """
        # Add user message
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
        
        # Get LLM tools
        tools = self.mcp_wrapper.get_llm_tools()
        
        # Tool call loop
        for iteration in range(max_tool_iterations):
            # Call LLM
            response = self.llm.chat_completion(
                messages=self.conversation_history,
                tools=tools if tools else None
            )
            
            # Add assistant message
            assistant_message = {
                "role": "assistant",
                "content": response.get("content", "")
            }
            
            # Check for tool calls
            if "tool_calls" in response:
                assistant_message["tool_calls"] = response["tool_calls"]
                self.conversation_history.append(assistant_message)
                
                # Execute tool calls
                tool_results = self.mcp_wrapper.handle_llm_tool_calls(response["tool_calls"])
                
                # Add tool results to conversation
                self.conversation_history.extend(tool_results)
                
                # Continue to next iteration
                continue
            else:
                # No tool calls, we're done
                self.conversation_history.append(assistant_message)
                return response.get("content", "")
        
        # Max iterations reached
        return "Maximum tool iterations reached. Please simplify your request."
    
    def reset_conversation(self):
        """Reset conversation history."""
        self.conversation_history = []


# =============================================================================
# Pattern 3: Practical Usage Example
# =============================================================================

def practical_example():
    """
    Complete practical example showing how to integrate MCP endpoints
    with LLM facades.
    """
    print("=" * 60)
    print("Practical MCP Tools Integration Example")
    print("=" * 60)
    
    # Step 1: Define your MCP endpoints (from your server/service)
    mcp_endpoints = [
        {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "description": "Temperature unit"}
                },
                "required": ["location"]
            }
        },
        {
            "name": "search_documents",
            "description": "Search through documentation",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "category": {"type": "string", "description": "Document category"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "create_task",
            "description": "Create a new task",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                    "due_date": {"type": "string", "description": "Due date (YYYY-MM-DD)"}
                },
                "required": ["title"]
            }
        }
    ]
    
    # Step 2: Define executor functions for each endpoint
    def get_weather(args):
        """Call your actual weather MCP endpoint."""
        # In reality, this would call your MCP server:
        # return mcp_client.call_tool("get_weather", args)
        
        # Mock response
        location = args["location"]
        unit = args.get("unit", "celsius")
        return {
            "location": location,
            "temperature": 22 if unit == "celsius" else 72,
            "unit": unit,
            "conditions": "Partly cloudy",
            "humidity": 65
        }
    
    def search_documents(args):
        """Call your document search MCP endpoint."""
        query = args["query"]
        category = args.get("category", "all")
        
        # Mock response
        return {
            "query": query,
            "category": category,
            "results": [
                {"title": "Introduction to Python", "url": "/docs/python-intro"},
                {"title": "Python Best Practices", "url": "/docs/python-best-practices"}
            ],
            "total_count": 2
        }
    
    def create_task(args):
        """Call your task creation MCP endpoint."""
        # Mock response
        return {
            "task_id": "task-12345",
            "title": args["title"],
            "priority": args.get("priority", "medium"),
            "status": "created",
            "created_at": "2025-11-11T10:00:00Z"
        }
    
    # Step 3: Create executor map
    executor_map = {
        "get_weather": get_weather,
        "search_documents": search_documents,
        "create_task": create_task
    }
    
    # Step 4: Initialize the system
    print("\nInitializing MCP Tool System...")
    wrapper = MCPEndpointWrapper()
    wrapper.load_mcp_endpoints(mcp_endpoints, executor_map)
    
    # Step 5: Get LLM-compatible tool definitions
    llm_tools = wrapper.get_llm_tools()
    print(f"\nGenerated {len(llm_tools)} LLM tool definitions")
    
    # Step 6: Use with your LLM (example with mock LLM)
    print("\n" + "=" * 60)
    print("Using with LLM:")
    print("=" * 60)
    
    # Simulate LLM asking about weather
    print("\nUser: What's the weather in London?")
    
    # Mock LLM response with tool call
    llm_response = {
        "content": "",
        "tool_calls": [{
            "id": "call_123",
            "type": "function",
            "function": {
                "name": "get_weather",
                "arguments": '{"location": "London", "unit": "celsius"}'
            }
        }]
    }
    
    print("LLM decides to call: get_weather")
    
    # Execute tool via wrapper
    tool_results = wrapper.handle_llm_tool_calls(llm_response["tool_calls"])
    print(f"\nTool execution result:")
    print(json.dumps(tool_results[0], indent=2))
    
    # Step 7: Multiple tool calls
    print("\n" + "=" * 60)
    print("User: Search for Python docs and create a task to review them")
    print("=" * 60)
    
    # LLM might call multiple tools
    multi_tool_response = {
        "tool_calls": [
            {
                "id": "call_456",
                "type": "function",
                "function": {
                    "name": "search_documents",
                    "arguments": '{"query": "Python", "category": "tutorials"}'
                }
            },
            {
                "id": "call_789",
                "type": "function",
                "function": {
                    "name": "create_task",
                    "arguments": '{"title": "Review Python documentation", "priority": "high"}'
                }
            }
        ]
    }
    
    print("\nLLM calls 2 tools:")
    tool_results = wrapper.handle_llm_tool_calls(multi_tool_response["tool_calls"])
    
    for i, result in enumerate(tool_results, 1):
        print(f"\nTool {i} result:")
        print(json.dumps(result, indent=2))


# =============================================================================
# Pattern 4: Direct Schema Conversion (No Executors)
# =============================================================================

def direct_conversion_example():
    """
    When you just need to convert schemas to LLM format without execution.
    
    Useful when you want to:
    1. Let LLM know what tools are available
    2. Handle execution separately (e.g., in a different service)
    """
    print("\n" + "=" * 60)
    print("Direct Schema Conversion (No Executors)")
    print("=" * 60)
    
    from mcp_tools import mcp_schemas_to_llm_tools
    
    # You have MCP schemas from your server
    mcp_schemas = [
        {
            "name": "read_file",
            "description": "Read contents of a file",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        },
        {
            "name": "write_file",
            "description": "Write contents to a file",
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
    
    # Convert to LLM tools instantly
    llm_tools = mcp_schemas_to_llm_tools(mcp_schemas)
    
    print("\nConverted MCP schemas to LLM tools:")
    print(json.dumps(llm_tools, indent=2))
    
    print("\nReady to use:")
    print("""
    # Use with any LLM
    response = llm.chat_completion(
        messages=[{"role": "user", "content": "Read config.json"}],
        tools=llm_tools
    )
    
    # When LLM makes a tool call, handle it externally
    if "tool_calls" in response:
        for call in response["tool_calls"]:
            # Send to your MCP server for execution
            result = mcp_server.execute(call['function']['name'], ...)
    """)


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    practical_example()
    direct_conversion_example()
    
    print("\n" + "=" * 60)
    print("Integration guide completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Replace mock executors with real MCP endpoint calls")
    print("2. Integrate with your preferred LLM facade")
    print("3. Add error handling and retries as needed")
    print("4. Deploy!")
