"""
Abhikarta LLM Facades - Comprehensive Test Suite

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This test suite is part of the proprietary Abhikarta LLM Facades software.
Unauthorized use is prohibited.
"""

import pytest
import sys
import os

# Add facades to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'facades'))

from llm_facade import (
    ModelCapability,
    GenerationConfig,
    ResponseFormat,
    LLMFacadeException,
    CapabilityNotSupportedException,
    RateLimitException,
    AuthenticationException
)

from mock_facade import MockFacade


class TestLLMFacadeBase:
    """Test base facade functionality using Mock provider."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM instance for testing."""
        return MockFacade(model_name="mock-model")
    
    def test_initialization(self, mock_llm):
        """Test facade initialization."""
        assert mock_llm is not None
        assert mock_llm.provider_name == "mock"
        assert mock_llm.model_name == "mock-model"
    
    def test_get_model_info(self, mock_llm):
        """Test model information retrieval."""
        info = mock_llm.get_model_info()
        assert isinstance(info, dict)
        assert "provider" in info
        assert "name" in info
        assert info["provider"] == "mock"
    
    def test_get_capabilities(self, mock_llm):
        """Test capability discovery."""
        capabilities = mock_llm.get_capabilities()
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0
        assert all(isinstance(cap, ModelCapability) for cap in capabilities)
    
    def test_supports_capability(self, mock_llm):
        """Test capability checking."""
        # Mock should support chat
        assert mock_llm.supports_capability(ModelCapability.CHAT_COMPLETION)
        
        # Test with capability that might not be supported
        result = mock_llm.supports_capability(ModelCapability.IMAGE_GENERATION)
        assert isinstance(result, bool)
    
    def test_health_check(self, mock_llm):
        """Test health check functionality."""
        is_healthy = mock_llm.health_check()
        assert isinstance(is_healthy, bool)
    
    def test_context_manager(self):
        """Test context manager protocol."""
        with MockFacade(model_name="mock-model") as llm:
            assert llm is not None
            info = llm.get_model_info()
            assert info["provider"] == "mock"
        # Should close cleanly
    
    def test_string_representation(self, mock_llm):
        """Test __repr__ and __str__ methods."""
        repr_str = repr(mock_llm)
        str_str = str(mock_llm)
        
        assert "mock" in repr_str.lower()
        assert "mock" in str_str.lower()


class TestChatCompletion:
    """Test chat completion functionality."""
    
    @pytest.fixture
    def mock_llm(self):
        return MockFacade(model_name="mock-advanced")
    
    def test_basic_chat_completion(self, mock_llm):
        """Test basic chat completion."""
        messages = [
            {"role": "user", "content": "Hello!"}
        ]
        
        response = mock_llm.chat_completion(messages)
        
        assert isinstance(response, dict)
        assert "content" in response
        assert "role" in response
        assert response["role"] == "assistant"
        assert isinstance(response["content"], str)
    
    def test_chat_with_system_message(self, mock_llm):
        """Test chat with system message."""
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hi!"}
        ]
        
        response = mock_llm.chat_completion(messages)
        assert response is not None
    
    def test_chat_with_config(self, mock_llm):
        """Test chat with generation configuration."""
        messages = [{"role": "user", "content": "Test"}]
        
        config = GenerationConfig(
            max_tokens=100,
            temperature=0.7,
            top_p=0.9
        )
        
        response = mock_llm.chat_completion(messages, config=config)
        assert response is not None
    
    def test_chat_with_tools(self, mock_llm):
        """Test chat with function calling."""
        if not mock_llm.supports_capability(ModelCapability.FUNCTION_CALLING):
            pytest.skip("Function calling not supported")
        
        messages = [{"role": "user", "content": "What's the weather?"}]
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"}
                        }
                    }
                }
            }
        ]
        
        response = mock_llm.chat_completion(messages, tools=tools)
        assert response is not None


class TestTextCompletion:
    """Test text completion functionality."""
    
    @pytest.fixture
    def mock_llm(self):
        return MockFacade(model_name="mock-model")
    
    def test_basic_completion(self, mock_llm):
        """Test basic text completion."""
        if not mock_llm.supports_capability(ModelCapability.TEXT_GENERATION):
            pytest.skip("Text generation not supported")
        
        result = mock_llm.completion("Once upon a time")
        assert isinstance(result, str)
    
    def test_completion_with_config(self, mock_llm):
        """Test completion with configuration."""
        if not mock_llm.supports_capability(ModelCapability.TEXT_GENERATION):
            pytest.skip("Text generation not supported")
        
        config = GenerationConfig(max_tokens=50, temperature=0.5)
        result = mock_llm.completion("Test prompt", config=config)
        assert isinstance(result, str)


class TestStreaming:
    """Test streaming functionality."""
    
    @pytest.fixture
    def mock_llm(self):
        return MockFacade(model_name="mock-model")
    
    def test_stream_chat_completion(self, mock_llm):
        """Test streaming chat completion."""
        if not mock_llm.supports_capability(ModelCapability.STREAMING):
            pytest.skip("Streaming not supported")
        
        messages = [{"role": "user", "content": "Count to 3"}]
        
        chunks = []
        for chunk in mock_llm.stream_chat_completion(messages):
            assert isinstance(chunk, str)
            chunks.append(chunk)
        
        # Should receive at least one chunk
        assert len(chunks) >= 1


class TestTokenCounting:
    """Test token counting functionality."""
    
    @pytest.fixture
    def mock_llm(self):
        return MockFacade(model_name="mock-model")
    
    def test_count_tokens(self, mock_llm):
        """Test token counting for text."""
        text = "This is a test message."
        count = mock_llm.count_tokens(text)
        
        assert isinstance(count, int)
        assert count > 0
    
    def test_count_message_tokens(self, mock_llm):
        """Test token counting for messages."""
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello!"}
        ]
        
        count = mock_llm.count_message_tokens(messages)
        assert isinstance(count, int)
        assert count > 0


class TestMessageFormatting:
    """Test message formatting utilities."""
    
    @pytest.fixture
    def mock_llm(self):
        return MockFacade(model_name="mock-model")
    
    def test_format_messages(self, mock_llm):
        """Test message formatting."""
        messages = [
            {"role": "system", "content": "System message"},
            {"role": "user", "content": "User message"},
            {"role": "assistant", "content": "Assistant message"}
        ]
        
        formatted = mock_llm.format_messages(messages)
        
        assert isinstance(formatted, str)
        assert "System" in formatted or "system" in formatted
        assert "User" in formatted or "user" in formatted or "Human" in formatted
    
    def test_format_multimodal_messages(self, mock_llm):
        """Test formatting of multimodal messages."""
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's this?"},
                    {"type": "image_url", "image_url": {"url": "test.jpg"}}
                ]
            }
        ]
        
        formatted = mock_llm.format_messages(messages)
        assert isinstance(formatted, str)
        assert "What's this?" in formatted


class TestConfiguration:
    """Test configuration and validation."""
    
    @pytest.fixture
    def mock_llm(self):
        return MockFacade(model_name="mock-model")
    
    def test_generation_config(self):
        """Test GenerationConfig dataclass."""
        config = GenerationConfig(
            max_tokens=100,
            temperature=0.7,
            top_p=0.9,
            frequency_penalty=0.5
        )
        
        config_dict = config.to_dict()
        assert config_dict["max_tokens"] == 100
        assert config_dict["temperature"] == 0.7
        assert "stop_sequences" not in config_dict  # Should exclude None values
    
    def test_validate_config(self, mock_llm):
        """Test configuration validation."""
        valid_config = {
            "model_name": "test-model",
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        is_valid, errors = mock_llm.validate_config(valid_config)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_invalid_config(self, mock_llm):
        """Test validation of invalid configuration."""
        invalid_config = {
            "model_name": "",  # Empty model name
            "temperature": 5.0,  # Out of range
            "max_tokens": -10  # Negative
        }
        
        is_valid, errors = mock_llm.validate_config(invalid_config)
        assert is_valid is False
        assert len(errors) > 0


class TestUsageTracking:
    """Test usage tracking and statistics."""
    
    @pytest.fixture
    def mock_llm(self):
        return MockFacade(model_name="mock-model")
    
    def test_get_usage_stats(self, mock_llm):
        """Test usage statistics retrieval."""
        # Make a few requests
        messages = [{"role": "user", "content": "Test"}]
        
        for _ in range(3):
            mock_llm.chat_completion(messages)
        
        stats = mock_llm.get_usage_stats()
        
        assert isinstance(stats, dict)
        assert "total_requests" in stats
        assert "total_tokens" in stats
        assert stats["total_requests"] >= 3
    
    def test_log_request(self, mock_llm):
        """Test request logging."""
        # This should not raise an exception
        mock_llm.log_request(
            method="chat_completion",
            input_data={"test": "data"},
            response={"content": "response"},
            latency_ms=100.0
        )


class TestErrorHandling:
    """Test error handling and exceptions."""
    
    @pytest.fixture
    def mock_llm(self):
        return MockFacade(model_name="mock-model")
    
    def test_capability_not_supported(self, mock_llm):
        """Test CapabilityNotSupportedException."""
        # Create a facade that doesn't support certain features
        with pytest.raises(Exception):  # May raise different exceptions
            mock_llm._check_capability(ModelCapability.IMAGE_GENERATION)
    
    def test_invalid_messages(self, mock_llm):
        """Test handling of invalid messages."""
        # Empty messages
        with pytest.raises(Exception):
            mock_llm.chat_completion([])
    
    def test_error_handling_method(self, mock_llm):
        """Test error handling utility method."""
        # Test that _handle_error properly converts exceptions
        test_error = Exception("Rate limit exceeded")
        
        with pytest.raises(LLMFacadeException):
            mock_llm._handle_error(test_error)


class TestProviderSpecific:
    """Test provider-specific functionality."""
    
    def test_mock_provider_basic(self):
        """Test basic mock provider functionality."""
        llm = MockFacade(model_name="mock-model")
        
        assert llm.provider_name == "mock"
        assert llm.supports_capability(ModelCapability.CHAT_COMPLETION)
    
    def test_mock_provider_advanced(self):
        """Test advanced mock provider features."""
        llm = MockFacade(model_name="mock-advanced")
        
        # Advanced mock should support more features
        capabilities = llm.get_capabilities()
        assert len(capabilities) > 0


class TestAsync:
    """Test async functionality."""
    
    @pytest.mark.asyncio
    async def test_async_placeholder(self):
        """Placeholder for async tests."""
        # Async functionality to be implemented
        pass


# Test utilities
def test_imports():
    """Test that all required modules can be imported."""
    from llm_facade_base import LLMFacadeBase
    from openai_facade import OpenAIFacade
    from anthropic_facade import AnthropicFacade
    from mock_facade import MockFacade
    
    assert LLMFacadeBase is not None
    assert OpenAIFacade is not None
    assert AnthropicFacade is not None
    assert MockFacade is not None


def test_version():
    """Test version information."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'facades'))
    
    # Check Python version
    assert sys.version_info >= (3, 8), "Python 3.8+ required"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
