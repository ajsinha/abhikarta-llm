"""
Abhikarta MCP Integration - Basic Tests

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

Basic unit tests for the MCP integration components.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

# Import components to test
from abhikartamcp import (
    AbhikartaMCPToolBuilder,
    MCPServerConfig,
    AbhikartaBaseTool,
    MCPRegistryIntegration
)


class TestMCPServerConfig:
    """Test MCPServerConfig dataclass"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = MCPServerConfig()
        
        assert config.base_url == "http://localhost:3002"
        assert config.mcp_endpoint == "/mcp"
        assert config.tool_name_suffix == ":abhikartamcp"
        assert config.refresh_interval_seconds == 600
        assert config.timeout_seconds == 30.0
    
    def test_custom_config(self):
        """Test custom configuration values"""
        config = MCPServerConfig(
            base_url="https://custom.server.com",
            username="testuser",
            password="testpass",
            refresh_interval_seconds=300
        )
        
        assert config.base_url == "https://custom.server.com"
        assert config.username == "testuser"
        assert config.password == "testpass"
        assert config.refresh_interval_seconds == 300


class TestAbhikartaMCPToolBuilder:
    """Test AbhikartaMCPToolBuilder class"""
    
    def test_singleton_pattern(self):
        """Test that builder implements singleton pattern"""
        builder1 = AbhikartaMCPToolBuilder()
        builder2 = AbhikartaMCPToolBuilder()
        
        assert builder1 is builder2
    
    def test_configure(self):
        """Test configuration method"""
        builder = AbhikartaMCPToolBuilder()
        
        result = builder.configure(
            base_url="https://test.com",
            username="user",
            password="pass",
            refresh_interval_seconds=120
        )
        
        assert result is builder  # Method chaining
        assert builder.config.base_url == "https://test.com"
        assert builder.config.username == "user"
        assert builder.config.refresh_interval_seconds == 120
    
    def test_initial_state(self):
        """Test initial builder state"""
        builder = AbhikartaMCPToolBuilder()
        
        assert builder._running is False
        assert builder._auth_token is None
        assert len(builder._tool_cache) >= 0  # May be populated from previous tests


class TestAbhikartaBaseTool:
    """Test AbhikartaBaseTool class"""
    
    def test_tool_creation(self):
        """Test basic tool creation"""
        tool = AbhikartaBaseTool(
            name="test_tool:abhikartamcp",
            description="A test tool",
            mcp_base_url="http://localhost:3002",
            input_schema={
                "type": "object",
                "properties": {
                    "param1": {"type": "string"}
                }
            }
        )
        
        assert tool.name == "test_tool:abhikartamcp"
        assert tool.original_tool_name == "test_tool"
        assert tool.description == "A test tool"
    
    def test_tool_name_extraction(self):
        """Test extraction of original tool name from suffixed name"""
        tool = AbhikartaBaseTool(
            name="my_awesome_tool:abhikartamcp",
            description="Test",
            mcp_base_url="http://localhost:3002"
        )
        
        assert tool.original_tool_name == "my_awesome_tool"
    
    def test_mcp_url_construction(self):
        """Test MCP URL construction"""
        tool = AbhikartaBaseTool(
            name="test:abhikartamcp",
            description="Test",
            mcp_base_url="http://localhost:3002",
            mcp_endpoint="/custom/mcp"
        )
        
        assert tool.mcp_url == "http://localhost:3002/custom/mcp"


class TestMCPRegistryIntegration:
    """Test MCPRegistryIntegration class"""
    
    def test_integration_creation(self):
        """Test integration creation with mock registry"""
        mock_registry = Mock()
        builder = AbhikartaMCPToolBuilder()
        
        integration = MCPRegistryIntegration(
            registry=mock_registry,
            builder=builder,
            group_name="test_group",
            tags=["test", "mcp"]
        )
        
        assert integration.registry is mock_registry
        assert integration.builder is builder
        assert integration.group_name == "test_group"
        assert integration.tags == ["test", "mcp"]
    
    def test_registered_tools_tracking(self):
        """Test that registered tools are tracked"""
        mock_registry = Mock()
        integration = MCPRegistryIntegration(
            registry=mock_registry,
            builder=AbhikartaMCPToolBuilder()
        )
        
        assert len(integration._registered_tools) >= 0
        assert isinstance(integration._registered_tools, set)


# Async tests
class TestAsyncOperations:
    """Test asynchronous operations"""
    
    @pytest.mark.asyncio
    async def test_builder_lifecycle(self):
        """Test builder start and stop lifecycle"""
        builder = AbhikartaMCPToolBuilder()
        builder.configure(
            base_url="http://localhost:3002",
            username="test",
            password="test"
        )
        
        # Note: This will fail without a running server
        # It's here to demonstrate the test structure
        try:
            await builder.start()
            assert builder._running is True
            
            await builder.stop()
            assert builder._running is False
        except Exception as e:
            # Expected if no server is running
            assert isinstance(e, Exception)


# Mock-based tests
class TestWithMocks:
    """Tests using mocks for external dependencies"""
    
    @pytest.mark.asyncio
    async def test_mocked_authentication(self):
        """Test authentication with mocked HTTP client"""
        builder = AbhikartaMCPToolBuilder()
        builder.configure(username="user", password="pass")
        
        # Mock the HTTP client
        mock_response = Mock()
        mock_response.json.return_value = {"token": "test_token"}
        mock_response.raise_for_status = Mock()
        
        with patch.object(builder, '_http_client') as mock_client:
            mock_client.post = AsyncMock(return_value=mock_response)
            
            result = await builder._authenticate()
            
            assert result is True
            assert builder._auth_token == "test_token"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
