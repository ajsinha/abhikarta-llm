"""
Abhikarta MCP Integration - Advanced Usage Example

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

This example demonstrates advanced usage including tool execution,
error handling, and monitoring.
"""

import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from tool_management.abhikartamcp import (
    AbhikartaMCPToolBuilder,
    AbhikartaBaseTool,
    MCPRegistryIntegration
)

# Mock registry for demonstration
class ToolRegistry:
    def __init__(self):
        self._tools = {}
    
    def register(self, tool, group=None, tags=None):
        self._tools[tool.name] = tool
        return self
    
    def unregister(self, tool_name):
        if tool_name in self._tools:
            del self._tools[tool_name]
        return self
    
    def get(self, tool_name):
        return self._tools.get(tool_name)
    
    def list_all(self):
        return list(self._tools.values())


async def execute_tool_example(tool: AbhikartaBaseTool):
    """
    Example of executing a tool with proper error handling.
    
    Args:
        tool: AbhikartaBaseTool instance to execute
    """
    print(f"\nExecuting tool: {tool.name}")
    print(f"Description: {tool.description}")
    
    # First, check connectivity
    print("Checking server connectivity...")
    is_alive = await tool.ping()
    if not is_alive:
        print("❌ Server is not responding")
        return
    print("✓ Server is responsive")
    
    # Get tool schema to understand parameters
    print(f"\nTool Parameters:")
    if tool._parameters:
        for param in tool._parameters.list_all():
            print(f"  - {param.name} ({param.param_type}): {param.description}")
            if param.required:
                print(f"    Required: Yes")
            if param.default is not None:
                print(f"    Default: {param.default}")
    else:
        print("  (No parameters required)")
    
    # Example execution with mock parameters
    # In real usage, you would provide actual parameter values
    print("\nExecuting tool with test parameters...")
    
    try:
        # Adjust these parameters based on your actual tool
        result = await tool.execute_async(
            # Add your tool-specific parameters here
            # For example:
            # query="test query",
            # limit=10
        )
        
        print(f"\n✓ Execution successful!")
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"\n❌ Execution failed: {e}")


async def monitor_cache_changes(builder: AbhikartaMCPToolBuilder, duration: int = 60):
    """
    Monitor the tool cache for changes over time.
    
    Args:
        builder: AbhikartaMCPToolBuilder instance
        duration: How long to monitor (seconds)
    """
    print(f"\nMonitoring tool cache for {duration} seconds...")
    
    previous_tools = set(builder.list_cached_tools())
    print(f"Initial tool count: {len(previous_tools)}")
    
    start_time = asyncio.get_event_loop().time()
    
    while (asyncio.get_event_loop().time() - start_time) < duration:
        await asyncio.sleep(10)  # Check every 10 seconds
        
        current_tools = set(builder.list_cached_tools())
        
        # Check for added tools
        added = current_tools - previous_tools
        if added:
            print(f"\n✓ New tools discovered: {added}")
        
        # Check for removed tools
        removed = previous_tools - current_tools
        if removed:
            print(f"\n⚠ Tools removed: {removed}")
        
        # Check for updates (cache refresh)
        stats = builder.get_cache_stats()
        last_refresh = stats.get('last_refresh')
        if last_refresh:
            print(f"Last cache refresh: {last_refresh}")
        
        previous_tools = current_tools
    
    print("\nMonitoring complete")


async def manual_tool_creation_example():
    """
    Example of manually creating and using an AbhikartaBaseTool.
    
    This is useful when you want to create a tool directly without
    using the builder.
    """
    print("\n" + "=" * 70)
    print("Manual Tool Creation Example")
    print("=" * 70)
    
    # Create a tool manually
    tool = AbhikartaBaseTool(
        name="test_tool:abhikartamcp",
        description="A test tool for demonstration",
        mcp_base_url="http://localhost:3002",
        mcp_endpoint="/mcp",
        input_schema={
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "A test message"
                }
            },
            "required": ["message"]
        },
        auth_token="your-auth-token-here"
    )
    
    print(f"Created tool: {tool}")
    print(f"Original tool name: {tool.original_tool_name}")
    
    # Test connectivity
    is_alive = await tool.ping()
    print(f"Server connectivity: {'OK' if is_alive else 'FAILED'}")
    
    # Cleanup
    await tool.cleanup()


async def full_lifecycle_example():
    """
    Complete lifecycle example: setup, discovery, sync, execute, cleanup.
    """
    print("\n" + "=" * 70)
    print("Full Lifecycle Example")
    print("=" * 70)
    
    # Setup
    print("\n1. Setup Phase")
    builder = AbhikartaMCPToolBuilder()
    builder.configure(
        base_url="http://localhost:3002",
        username="admin",
        password="admin123",
        refresh_interval_seconds=300
    )
    
    registry = ToolRegistry()
    integration = MCPRegistryIntegration(registry, builder)
    
    # Start
    print("\n2. Start Phase")
    await builder.start()
    print(f"Builder stats: {builder.get_cache_stats()}")
    
    # Sync
    print("\n3. Sync Phase")
    integration.sync_tools()
    print(f"Integration stats: {integration.get_stats()}")
    
    # Execute
    print("\n4. Execution Phase")
    tools = registry.list_all()
    if tools:
        # Execute first available tool
        await execute_tool_example(tools[0])
    else:
        print("No tools available for execution")
    
    # Monitor
    print("\n5. Monitoring Phase")
    await monitor_cache_changes(builder, duration=30)
    
    # Cleanup
    print("\n6. Cleanup Phase")
    await builder.stop()
    
    print("\nLifecycle complete!")


async def error_handling_example():
    """
    Example demonstrating proper error handling.
    """
    print("\n" + "=" * 70)
    print("Error Handling Example")
    print("=" * 70)
    
    builder = AbhikartaMCPToolBuilder()
    
    # Test with invalid credentials
    print("\nTesting with invalid credentials...")
    builder.configure(
        base_url="http://localhost:3002",
        username="invalid",
        password="invalid"
    )
    
    try:
        await builder.start()
    except Exception as e:
        print(f"Expected error: {e}")
    
    # Test with unreachable server
    print("\nTesting with unreachable server...")
    builder.configure(base_url="http://invalid-server:9999")
    
    try:
        await builder.start()
    except Exception as e:
        print(f"Expected error: {e}")
    
    print("\nError handling demonstration complete")


async def main():
    """Main function running all examples"""
    
    print("=" * 70)
    print("Abhikarta MCP Integration - Advanced Examples")
    print("=" * 70)
    
    # Run examples
    try:
        # Manual tool creation
        await manual_tool_creation_example()
        
        # Error handling
        await error_handling_example()
        
        # Full lifecycle (requires actual MCP server)
        # Uncomment if you have a running MCP server:
        # await full_lifecycle_example()
        
    except Exception as e:
        print(f"\n❌ Error in examples: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
