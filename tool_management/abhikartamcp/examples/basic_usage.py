"""
Abhikarta MCP Integration - Basic Usage Example

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

This example demonstrates basic usage of the Abhikarta MCP integration.
"""

import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import the MCP integration components
from tool_management.abhikartamcp import (
    AbhikartaMCPServerProxy,
    MCPRegistryIntegration,
    MCPAutoSync
)

from tool_management.registry import ToolRegistry



async def main():
    """Main example function"""
    
    print("=" * 70)
    print("Abhikarta MCP Integration - Basic Usage Example")
    print("=" * 70)
    print()
    
    # Step 1: Create and configure the MCP tool builder
    print("Step 1: Configuring MCP Tool Builder...")
    builder = AbhikartaMCPServerProxy()
    builder.configure(
        base_url="http://localhost:3002",
        username="admin",
        password="admin123",
        refresh_interval_seconds=600  # 10 minutes
    )
    print(f"Builder configured: {builder}")
    print()
    
    # Step 2: Start the builder (connects and performs initial discovery)
    print("Step 2: Starting MCP Tool Builder...")
    await builder.start()
    print("Builder started successfully")
    print()
    
    # Step 3: View discovered tools
    print("Step 3: Viewing discovered tools...")
    cached_tools = builder.list_cached_tools()
    print(f"Found {len(cached_tools)} tools:")
    for tool_name in cached_tools:
        schema = builder.get_tool_schema(tool_name)
        print(f"  - {tool_name}")
        print(f"    Description: {schema.description}")
    print()
    
    # Step 4: Create a tool registry
    print("Step 4: Creating Tool Registry...")
    registry = ToolRegistry()
    print("Registry created")
    print()
    
    # Step 5: Set up registry integration
    print("Step 5: Setting up Registry Integration...")
    integration = MCPRegistryIntegration(
        registry=registry,
        mcp_server_proxy=builder,
        group_name="mcp_tools",
        tags=["mcp", "abhikarta", "dynamic"]
    )
    print(f"Integration created: {integration}")
    print()
    
    # Step 6: Perform initial sync
    print("Step 6: Syncing tools to registry...")
    integration.sync_tools()
    stats = integration.get_stats()
    print(f"Sync complete. Stats: {stats}")
    print()
    
    # Step 7: Set up auto-sync (optional)
    print("Step 7: Setting up Auto-Sync...")
    auto_sync = MCPAutoSync(
        integration=integration,
        sync_interval_seconds=120  # 2 minutes
    )
    await auto_sync.start()
    print("Auto-sync started")
    print()
    
    # Step 8: Test a tool execution (if tools are available)
    if cached_tools:
        print("Step 8: Testing tool execution...")
        tool_name = cached_tools[0]
        tool = registry.get(tool_name)
        
        if tool:
            print(f"Testing tool: {tool.name}")
            print(f"Description: {tool.description}")
            
            # Check if tool can be pinged
            can_ping = await tool.ping()
            print(f"Server connectivity check: {'OK' if can_ping else 'FAILED'}")
            
            # Note: Actual execution would require proper parameters
            # based on the tool's schema
            print()
    
    # Step 9: Monitor for a short period
    print("Step 9: Monitoring for 10 seconds...")
    print("(In production, this would run continuously)")
    await asyncio.sleep(10)
    print()
    
    # Step 10: Cleanup
    print("Step 10: Cleaning up...")
    await auto_sync.stop()
    await builder.stop()
    print("Cleanup complete")
    print()
    
    print("=" * 70)
    print("Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
