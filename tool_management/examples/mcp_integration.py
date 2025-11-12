"""
Abhikarta LLM - Tool Management Framework
MCP Integration Example

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

This example demonstrates Model Context Protocol (MCP) integration.
"""

import asyncio
from tool_management import ToolRegistry
from tool_management.mcp import MCPClient, MCPTool, discover_mcp_tools

server_url = "http://localhost:3002"

async def example_mcp_connection():
    """
    Example: Connecting to an MCP server and discovering tools.
    
    Note: This example assumes an MCP server is running on localhost:3000
    """
    
    print("=" * 60)
    print("MCP Integration Example")
    print("=" * 60)
    print()
    
    # Create registry
    registry = ToolRegistry()
    
    try:
        # Example 1: Connect to MCP server
        print("1. Connecting to MCP server...")
        client = MCPClient(
            server_url=server_url,
            transport="http"  # or "sse"
        )
        
        server_info = await client.connect()
        print(f"   ✓ Connected to: {server_info.name}")
        print(f"   ✓ Version: {server_info.version}")
        print(f"   ✓ Capabilities: {', '.join(server_info.capabilities)}\n")
        
        # Example 2: Discover tools from MCP server
        print("2. Discovering MCP tools...")
        mcp_tools = await discover_mcp_tools(client, prefix="mcp_")
        
        print(f"   ✓ Discovered {len(mcp_tools)} tools:")
        for tool in mcp_tools:
            print(f"     - {tool.name}: {tool.description}")
        print()
        
        # Example 3: Register MCP tools
        print("3. Registering MCP tools in registry...")
        for tool in mcp_tools:
            registry.register(tool, group="mcp", tags=["mcp", "external"])
        print(f"   ✓ Registered {len(mcp_tools)} MCP tools\n")
        
        # Example 4: Use an MCP tool
        if mcp_tools:
            print("4. Using MCP tool...")
            tool_name = mcp_tools[0].name
            
            # Example parameters - adjust based on actual MCP tool
            result = await registry.execute(
                tool_name,
                # Add appropriate parameters here
            )
            
            if result.success:
                print(f"   ✓ Tool executed successfully")
                print(f"   Result: {result.data}\n")
            else:
                print(f"   ✗ Tool execution failed: {result.error}\n")
        
        # Example 5: List all tools (including MCP)
        print("5. Listing all tools:")
        all_tools = registry.list_all()
        
        by_group = {}
        for tool in all_tools:
            group = "ungrouped"
            for g, tools in registry._groups.items():
                if tool.name in tools:
                    group = g
                    break
            by_group.setdefault(group, []).append(tool)
        
        for group, tools in by_group.items():
            print(f"   {group}:")
            for tool in tools:
                print(f"     - {tool.name}")
        print()
        
        # Example 6: Get schemas for LLM integration
        print("6. Generating schemas for LLM...")
        schemas = registry.get_all_schemas(format="anthropic")
        
        print(f"   ✓ Generated {len(schemas)} tool schemas")
        if schemas:
            print(f"   Example MCP tool schema:")
            mcp_schema = next((s for s in schemas if s['name'].startswith('mcp_')), None)
            if mcp_schema:
                print(f"     Name: {mcp_schema['name']}")
                print(f"     Description: {mcp_schema['description']}")
        print()
        
        # Cleanup
        await client.disconnect()
        
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        print("\n   Note: This example requires a running MCP server.")
        print("   To test MCP integration:")
        print("   1. Start an MCP server on localhost:3000")
        print("   2. Run this example again\n")


async def example_manual_mcp_tool():
    """
    Example: Manually creating an MCP tool without auto-discovery.
    """
    
    print("=" * 60)
    print("Manual MCP Tool Creation")
    print("=" * 60)
    print()
    
    registry = ToolRegistry()
    
    # Create MCP client
    client = MCPClient("http://localhost:3000")
    
    # Manually create MCP tool with known schema
    mcp_tool = MCPTool(
        name="database_query",
        description="Query the database using SQL",
        mcp_client=client,
        mcp_tool_name="db_query",  # Original name in MCP server
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SQL query to execute"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of rows",
                    "default": 100
                }
            },
            "required": ["query"]
        }
    )
    
    registry.register(mcp_tool, group="mcp", tags=["database", "mcp"])
    
    print("✓ Created and registered manual MCP tool")
    print(f"  Name: {mcp_tool.name}")
    print(f"  Description: {mcp_tool.description}")
    print(f"  Parameters: {list(mcp_tool._parameters._parameters.keys())}")
    print()


async def example_mcp_with_llm():
    """
    Example: Using MCP tools with LLM integration.
    """
    
    print("=" * 60)
    print("MCP Tools with LLM Integration")
    print("=" * 60)
    print()
    
    registry = ToolRegistry()
    
    # Simulate MCP tool discovery
    print("Note: This is a demonstration of the integration pattern.")
    print("In production, you would:")
    print()
    print("1. Connect to real MCP server:")
    print("   client = MCPClient('http://mcp-server:3000')")
    print("   await client.connect()")
    print()
    print("2. Discover tools:")
    print("   tools = await discover_mcp_tools(client)")
    print()
    print("3. Register with registry:")
    print("   for tool in tools:")
    print("       registry.register(tool)")
    print()
    print("4. Get schemas for LLM:")
    print("   schemas = registry.get_all_schemas(format='anthropic')")
    print()
    print("5. Use with Claude:")
    print("   import anthropic")
    print("   client = anthropic.Anthropic()")
    print("   response = client.messages.create(")
    print("       model='claude-sonnet-4-20250514',")
    print("       tools=schemas,")
    print("       messages=[...]")
    print("   )")
    print()


async def main():
    """Run all MCP examples"""
    
    # Example 1: Basic MCP connection
    await example_mcp_connection()
    
    # Example 2: Manual MCP tool creation
    await example_manual_mcp_tool()
    
    # Example 3: MCP with LLM
    await example_mcp_with_llm()
    
    print("=" * 60)
    print("MCP Integration Examples Completed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
