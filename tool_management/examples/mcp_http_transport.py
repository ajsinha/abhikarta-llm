"""
Abhikarta LLM - Tool Management Framework
MCP HTTP Transport Example

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

This example demonstrates using MCP with HTTP/REST transport.
"""

import asyncio
from tool_management import ToolRegistry
from tool_management.mcp import MCPClient, discover_mcp_tools


async def example_http_transport():
    """
    Example: Using MCP with HTTP/REST transport.
    
    HTTP transport is ideal for production deployments where:
    - MCP server is running as a web service
    - Network-based communication is required
    - Multiple clients need to connect
    - Load balancing is needed
    """
    
    print("=" * 60)
    print("MCP HTTP Transport Example")
    print("=" * 60)
    print()
    
    registry = ToolRegistry()
    
    try:
        # Example 1: Basic HTTP connection
        print("1. Connecting via HTTP transport...")
        async with MCPClient(
            server_url="http://localhost:3000/mcp",
            transport="http",
            timeout=30.0,
            headers={"Authorization": "Bearer your-token-here"}
        ) as client:
            
            server_info = await client.connect()
            print(f"   ✓ Connected to: {server_info.name}")
            print(f"   ✓ Version: {server_info.version}")
            print(f"   ✓ Transport: HTTP\n")
            
            # Example 2: Discover tools
            print("2. Discovering tools via HTTP...")
            tools = await discover_mcp_tools(client, prefix="http_")
            print(f"   ✓ Discovered {len(tools)} tools\n")
            
            # Example 3: Register and use tools
            print("3. Registering and using tools...")
            for tool in tools:
                registry.register(tool, group="mcp_http")
            
            if tools:
                result = await registry.execute(tools[0].name)
                if result.success:
                    print(f"   ✓ Tool executed successfully\n")
        
        print("   ✓ Connection closed automatically (context manager)\n")
        
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        print("\n   Note: This example requires a running MCP server.")
        print("   The server should expose an HTTP endpoint at the specified URL.\n")


async def example_multiple_transports():
    """
    Example: Comparing different transport options.
    """
    
    print("=" * 60)
    print("Transport Comparison")
    print("=" * 60)
    print()
    
    # HTTP Transport (Recommended for production)
    print("1. HTTP Transport")
    print("   Pros:")
    print("   - Network-based, works across machines")
    print("   - Supports load balancing")
    print("   - Firewall-friendly (uses standard HTTP)")
    print("   - Easy to secure with HTTPS/TLS")
    print("   - Standard authentication (headers, OAuth, etc.)")
    print()
    print("   Usage:")
    print("   client = MCPClient('http://mcp-server:3000', transport='http')")
    print()
    
    # SSE Transport
    print("2. SSE Transport (Server-Sent Events)")
    print("   Pros:")
    print("   - Real-time updates from server")
    print("   - Efficient for streaming data")
    print("   - Uses standard HTTP")
    print()
    print("   Usage:")
    print("   client = MCPClient('http://mcp-server:3000/sse', transport='sse')")
    print()
    
    # stdio Transport
    print("3. stdio Transport")
    print("   Pros:")
    print("   - Direct process communication")
    print("   - Low latency")
    print("   - No network overhead")
    print()
    print("   Usage:")
    print("   client = MCPClient('/path/to/mcp-server', transport='stdio')")
    print()
    
    print("Recommendation: Use HTTP transport for most production scenarios.")
    print()


async def example_http_with_auth():
    """
    Example: HTTP transport with authentication.
    """
    
    print("=" * 60)
    print("HTTP Transport with Authentication")
    print("=" * 60)
    print()
    
    # Example configurations
    configs = [
        {
            "name": "Bearer Token",
            "headers": {"Authorization": "Bearer eyJhbGc..."},
            "description": "OAuth 2.0 or JWT tokens"
        },
        {
            "name": "API Key",
            "headers": {"X-API-Key": "your-api-key"},
            "description": "Simple API key authentication"
        },
        {
            "name": "Basic Auth",
            "headers": {"Authorization": "Basic dXNlcjpwYXNz"},
            "description": "HTTP Basic Authentication"
        },
        {
            "name": "Custom Header",
            "headers": {"X-Custom-Auth": "secret-value"},
            "description": "Custom authentication scheme"
        }
    ]
    
    print("Common authentication patterns:\n")
    
    for i, config in enumerate(configs, 1):
        print(f"{i}. {config['name']}")
        print(f"   Description: {config['description']}")
        print(f"   Headers: {config['headers']}")
        print()
        print("   Usage:")
        print("   client = MCPClient(")
        print(f"       server_url='http://mcp-server:3000',")
        print(f"       transport='http',")
        print(f"       headers={config['headers']}")
        print("   )")
        print()


async def example_production_setup():
    """
    Example: Production-ready MCP HTTP setup.
    """
    
    print("=" * 60)
    print("Production HTTP Transport Setup")
    print("=" * 60)
    print()
    
    print("Recommended production configuration:\n")
    
    print("```python")
    print("from tool_management.mcp import MCPClient")
    print("from tool_management import ToolRegistry")
    print()
    print("# Production MCP client configuration")
    print("async def setup_mcp_client():")
    print("    client = MCPClient(")
    print("        server_url='https://mcp.yourcompany.com/api',  # HTTPS!")
    print("        transport='http',")
    print("        timeout=30.0,")
    print("        headers={")
    print("            'Authorization': f'Bearer {get_auth_token()}',")
    print("            'X-Client-Version': '1.0.0',")
    print("            'X-Environment': 'production'")
    print("        }")
    print("    )")
    print("    ")
    print("    # Connect and verify")
    print("    await client.connect()")
    print("    ")
    print("    # Discover tools")
    print("    tools = await discover_mcp_tools(client)")
    print("    ")
    print("    # Register with registry")
    print("    registry = ToolRegistry()")
    print("    for tool in tools:")
    print("        registry.register(tool, group='mcp', tags=['production'])")
    print("    ")
    print("    return client, registry")
    print("```")
    print()
    
    print("Production checklist:")
    print("  ✓ Use HTTPS (not HTTP)")
    print("  ✓ Implement proper authentication")
    print("  ✓ Set appropriate timeouts")
    print("  ✓ Add retry logic for failed requests")
    print("  ✓ Monitor connection health")
    print("  ✓ Log all MCP interactions")
    print("  ✓ Handle connection failures gracefully")
    print()


async def main():
    """Run all HTTP transport examples"""
    
    # Example 1: Basic HTTP usage
    await example_http_transport()
    
    # Example 2: Transport comparison
    await example_multiple_transports()
    
    # Example 3: Authentication
    await example_http_with_auth()
    
    # Example 4: Production setup
    await example_production_setup()
    
    print("=" * 60)
    print("HTTP Transport Examples Completed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
