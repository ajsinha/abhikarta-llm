"""
HuggingFace LLM Facade Test Suite - Refactored Version

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Description:
Test suite for refactored HuggingFace LLM Facade that extends BaseLLMFacadeClass.
"""

import unittest
import os
import sys
import asyncio
from typing import List, Dict, Any
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_provider.huggingface_facade import (
    HuggingFaceLLMFacade,
    create_huggingface_llm,
    GenerationConfig,
    ModelCapability,
    CapabilityNotSupportedException,
    RateLimitException,
    AuthenticationException
)


class TestRefactoredHuggingFacadeInitialization(unittest.TestCase):
    """Test facade initialization with base class."""

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        facade = HuggingFaceLLMFacade(
            model_name="meta-llama/Llama-3.2-1B-Instruct",
            api_key="hf_test_token"
        )
        self.assertEqual(facade.model_name, "meta-llama/Llama-3.2-1B-Instruct")
        self.assertEqual(facade.api_key, "hf_test_token")
        self.assertEqual(facade.provider_name, "huggingface")
        self.assertFalse(facade.use_local)

    def test_base_class_attributes_initialized(self):
        """Test that base class attributes are properly initialized."""
        facade = HuggingFaceLLMFacade(
            model_name="meta-llama/Llama-3.2-1B-Instruct",
            api_key="hf_test"
        )
        # Check base class attributes
        self.assertIsNotNone(facade.provider_config)
        self.assertIsNotNone(facade.logger)
        self.assertEqual(facade.request_count, 0)
        self.assertEqual(facade.total_tokens, 0)

    def test_config_loading_from_base_class(self):
        """Test that provider config is loaded by base class."""
        facade = HuggingFaceLLMFacade(
            model_name="meta-llama/Llama-3.3-70B-Instruct",
            api_key="hf_test"
        )
        # Should have loaded huggingface.json
        self.assertEqual(facade.provider_config.get("provider"), "huggingface")
        self.assertIsInstance(facade.provider_config.get("models"), list)

    def test_model_config_detection(self):
        """Test model-specific config detection from base class."""
        facade = HuggingFaceLLMFacade(
            model_name="meta-llama/Llama-3.3-70B-Instruct",
            api_key="hf_test"
        )
        # Should find model config
        self.assertIsNotNone(facade.model_config)
        self.assertIn("context_window", facade.model_config)


class TestCapabilityDetection(unittest.TestCase):
    """Test capability detection from config."""

    def test_capabilities_from_base_class(self):
        """Test that capabilities are detected by base class."""
        facade = HuggingFaceLLMFacade(
            model_name="meta-llama/Llama-3.3-70B-Instruct",
            api_key="hf_test"
        )
        caps = facade.get_capabilities()

        # Should have basic capabilities
        self.assertIsInstance(caps, list)
        self.assertIn(ModelCapability.CHAT_COMPLETION, caps)
        self.assertIn(ModelCapability.TEXT_GENERATION, caps)
        self.assertIn(ModelCapability.STREAMING, caps)

    def test_vision_model_capabilities(self):
        """Test vision model capability detection."""
        facade = HuggingFaceLLMFacade(
            model_name="meta-llama/Llama-3.2-11B-Vision-Instruct",
            api_key="hf_test"
        )

        self.assertTrue(facade.supports_capability(ModelCapability.VISION))
        self.assertTrue(facade.supports_capability(ModelCapability.MULTIMODAL))

    def test_embedding_model_capabilities(self):
        """Test embedding model capability detection."""
        facade = HuggingFaceLLMFacade(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            api_key="hf_test"
        )

        # Capability detection depends on config file
        caps = facade.get_capabilities()
        self.assertIsInstance(caps, list)


class TestModelInfo(unittest.TestCase):
    """Test model info from base class."""

    def test_get_model_info_from_base(self):
        """Test model info retrieval from base class."""
        facade = HuggingFaceLLMFacade(
            model_name="meta-llama/Llama-3.3-70B-Instruct",
            api_key="hf_test"
        )

        info = facade.get_model_info()

        # Base class should provide these
        self.assertEqual(info["name"], "meta-llama/Llama-3.3-70B-Instruct")
        self.assertEqual(info["provider"], "huggingface")
        self.assertIn("context_length", info)
        self.assertIn("capabilities", info)
        self.assertIsInstance(info["capabilities"], list)

    def test_context_window_from_config(self):
        """Test context window retrieval."""
        facade = HuggingFaceLLMFacade(
            model_name="meta-llama/Llama-3.3-70B-Instruct",
            api_key="hf_test"
        )

        context_window = facade.get_context_window()
        self.assertIsInstance(context_window, int)
        self.assertGreater(context_window, 0)

    def test_max_output_tokens(self):
        """Test max output tokens retrieval."""
        facade = HuggingFaceLLMFacade(
            model_name="meta-llama/Llama-3.3-70B-Instruct",
            api_key="hf_test"
        )

        max_output = facade.get_max_output_tokens()
        self.assertIsInstance(max_output, int)
        self.assertGreater(max_output, 0)


class TestTextGeneration(unittest.TestCase):
    """Test text generation with refactored code."""

    def setUp(self):
        """Set up test fixtures."""
        self.facade = HuggingFaceLLMFacade(
            model_name="meta-llama/Llama-3.2-1B-Instruct",
            api_key="hf_test"
        )

    @patch('huggingface_hub.InferenceClient')
    def test_basic_text_generation(self, mock_client_class):
        """Test basic text generation."""
        mock_client = Mock()
        mock_client.text_generation.return_value = "Generated response"
        mock_client_class.return_value = mock_client

        self.facade.client = mock_client

        response = self.facade.text_generation("Test prompt")

        self.assertEqual(response, "Generated response")
        mock_client.text_generation.assert_called_once()

    @patch('huggingface_hub.InferenceClient')
    def test_streaming_text_generation(self, mock_client_class):
        """Test streaming via convenience method from base class."""
        mock_client = Mock()
        mock_client.text_generation.return_value = iter(["chunk1", "chunk2"])
        mock_client_class.return_value = mock_client

        self.facade.client = mock_client

        # Use base class convenience method
        chunks = list(self.facade.stream_text_generation(prompt="Test"))

        self.assertEqual(len(chunks), 2)


class TestChatCompletion(unittest.TestCase):
    """Test chat completion."""

    def setUp(self):
        """Set up test fixtures."""
        self.facade = HuggingFaceLLMFacade(
            model_name="meta-llama/Llama-3.3-70B-Instruct",
            api_key="hf_test"
        )

    @patch('huggingface_hub.InferenceClient')
    def test_chat_completion(self, mock_client_class):
        """Test chat completion."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 20
        mock_response.usage.total_tokens = 30

        mock_client = Mock()
        mock_client.chat_completion.return_value = mock_response
        mock_client_class.return_value = mock_client

        self.facade.client = mock_client

        messages = [{"role": "user", "content": "Hello"}]
        response = self.facade.chat_completion(messages)

        self.assertEqual(response["content"], "Response")
        self.assertEqual(response["role"], "assistant")

    def test_base_class_message_formatting(self):
        """Test message formatting from base class."""
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello!"}
        ]

        formatted = self.facade.format_messages(messages)

        self.assertIn("System: You are helpful", formatted)
        self.assertIn("User: Hello!", formatted)


class TestConversationManagement(unittest.TestCase):
    """Test conversation management from base class."""

    def setUp(self):
        """Set up test fixtures."""
        self.facade = HuggingFaceLLMFacade(
            model_name="meta-llama/Llama-3.3-70B-Instruct",
            api_key="hf_test"
        )

    def test_start_conversation(self):
        """Test conversation initialization from base class."""
        conv = self.facade.start_conversation()

        self.assertIn("id", conv)
        self.assertIn("messages", conv)
        self.assertEqual(len(conv["messages"]), 0)

    @patch('huggingface_hub.InferenceClient')
    def test_continue_conversation(self, mock_client_class):
        """Test continuing conversation using base class method."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "AI response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 20
        mock_response.usage.total_tokens = 30

        mock_client = Mock()
        mock_client.chat_completion.return_value = mock_response
        mock_client_class.return_value = mock_client

        self.facade.client = mock_client

        # Use base class conversation management
        conv = self.facade.start_conversation()
        response = self.facade.continue_conversation(conv, "Hello")

        self.assertEqual(response, "AI response")
        self.assertEqual(len(conv["messages"]), 2)


class TestAsyncOperations(unittest.TestCase):
    """Test async operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.facade = HuggingFaceLLMFacade(
            model_name="meta-llama/Llama-3.2-1B-Instruct",
            api_key="hf_test"
        )

    def test_async_text_generation(self):
        """Test async text generation."""
        with patch.object(self.facade, 'text_generation', return_value="Response"):
            async def run_test():
                response = await self.facade.atext_generation(prompt="Test")
                self.assertEqual(response, "Response")

            asyncio.run(run_test())


class TestBatchProcessing(unittest.TestCase):
    """Test batch processing."""

    def setUp(self):
        """Set up test fixtures."""
        self.facade = HuggingFaceLLMFacade(
            model_name="meta-llama/Llama-3.2-1B-Instruct",
            api_key="hf_test"
        )

    def test_batch_generate(self):
        """Test batch generation."""
        with patch.object(self.facade, 'text_generation', side_effect=lambda p, **k: f"Response to: {p}"):
            prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
            results = self.facade.batch_generate(prompts, show_progress=False)

            self.assertEqual(len(results), 3)
            self.assertEqual(results[0], "Response to: Prompt 1")


class TestTokenCounting(unittest.TestCase):
    """Test token counting from base class."""

    def setUp(self):
        """Set up test fixtures."""
        self.facade = HuggingFaceLLMFacade(
            model_name="meta-llama/Llama-3.2-1B-Instruct",
            api_key="hf_test"
        )

    def test_count_tokens_uses_base_class(self):
        """Test token counting from base class."""
        count = self.facade.count_tokens("Hello world")

        # Base class provides default implementation
        self.assertIsInstance(count, int)
        self.assertGreater(count, 0)

    def test_truncate_to_max_tokens(self):
        """Test text truncation from base class."""
        long_text = "word " * 1000
        truncated = self.facade.truncate_to_max_tokens(long_text, max_tokens=50)

        # Should be truncated
        self.assertLess(len(truncated), len(long_text))


class TestErrorHandling(unittest.TestCase):
    """Test error handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.facade = HuggingFaceLLMFacade(
            model_name="meta-llama/Llama-3.2-1B-Instruct",
            api_key="hf_test"
        )

    def test_rate_limit_exception_transformation(self):
        """Test rate limit error transformation."""
        error = Exception("Rate limit exceeded (429)")
        transformed = self.facade._transform_exception(error)

        self.assertIsInstance(transformed, RateLimitException)

    def test_auth_exception_transformation(self):
        """Test authentication error transformation."""
        error = Exception("Unauthorized (401)")
        transformed = self.facade._transform_exception(error)

        self.assertIsInstance(transformed, AuthenticationException)


class TestLogging(unittest.TestCase):
    """Test logging from base class."""

    def setUp(self):
        """Set up test fixtures."""
        self.facade = HuggingFaceLLMFacade(
            model_name="meta-llama/Llama-3.2-1B-Instruct",
            api_key="hf_test"
        )

    def test_logger_initialized(self):
        """Test that logger is initialized by base class."""
        self.assertIsNotNone(self.facade.logger)
        self.assertEqual(
            self.facade.logger.name,
            "llm_facade.huggingface.meta-llama/Llama-3.2-1B-Instruct"
        )

    def test_log_request_from_base_class(self):
        """Test request logging from base class."""
        # Should not raise exception
        self.facade.log_request(
            method="text_generation",
            input_data={"prompt": "test"},
            response={"content": "response"},
            latency_ms=100.0
        )


class TestConfigValidation(unittest.TestCase):
    """Test config validation from base class."""

    def setUp(self):
        """Set up test fixtures."""
        self.facade = HuggingFaceLLMFacade(
            model_name="meta-llama/Llama-3.2-1B-Instruct",
            api_key="hf_test"
        )

    def test_validate_config_from_base(self):
        """Test config validation from base class."""
        config = {
            "max_tokens": 100,
            "temperature": 0.7
        }

        is_valid, errors = self.facade.validate_config(config)

        # Base class provides validation
        self.assertIsInstance(is_valid, bool)
        self.assertIsInstance(errors, list)


class TestHealthCheck(unittest.TestCase):
    """Test health check."""

    def setUp(self):
        """Set up test fixtures."""
        self.facade = HuggingFaceLLMFacade(
            model_name="meta-llama/Llama-3.2-1B-Instruct",
            api_key="hf_test"
        )

    def test_health_check_success(self):
        """Test successful health check."""
        with patch.object(self.facade, 'text_generation', return_value="OK"):
            result = self.facade.health_check()
            self.assertTrue(result)

    def test_health_check_failure(self):
        """Test failed health check."""
        with patch.object(self.facade, 'text_generation', side_effect=Exception("Error")):
            result = self.facade.health_check()
            self.assertFalse(result)


class TestContextManager(unittest.TestCase):
    """Test context manager support from base class."""

    def test_context_manager_protocol(self):
        """Test using facade as context manager."""
        with HuggingFaceLLMFacade(
            model_name="meta-llama/Llama-3.2-1B-Instruct",
            api_key="hf_test"
        ) as facade:
            self.assertIsNotNone(facade)
            self.assertIsNotNone(facade.logger)

        # After exiting, should be closed
        self.assertIsNone(facade.client)


class TestFactoryFunction(unittest.TestCase):
    """Test factory function."""

    def test_factory_creates_instance(self):
        """Test factory function creates correct instance."""
        facade = create_huggingface_llm(
            model_name="meta-llama/Llama-3.2-1B-Instruct",
            api_key="hf_test"
        )

        self.assertIsInstance(facade, HuggingFaceLLMFacade)
        self.assertEqual(facade.provider_name, "huggingface")


class TestCodeReduction(unittest.TestCase):
    """Test that refactoring properly uses base class."""

    def test_no_duplicate_methods(self):
        """Verify common methods are inherited from base class."""
        facade = HuggingFaceLLMFacade(
            model_name="meta-llama/Llama-3.2-1B-Instruct",
            api_key="hf_test"
        )

        # These should come from base class
        self.assertTrue(hasattr(facade, 'get_capabilities'))
        self.assertTrue(hasattr(facade, 'supports_capability'))
        self.assertTrue(hasattr(facade, 'format_messages'))
        self.assertTrue(hasattr(facade, 'count_tokens'))
        self.assertTrue(hasattr(facade, 'validate_config'))
        self.assertTrue(hasattr(facade, 'health_check'))
        self.assertTrue(hasattr(facade, 'start_conversation'))
        self.assertTrue(hasattr(facade, 'continue_conversation'))

        # Verify they're from base class, not redefined
        from base_llm_facade_class import BaseLLMFacadeClass
        self.assertIs(
            type(facade).get_capabilities.__func__,
            BaseLLMFacadeClass.get_capabilities.__func__
        )


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()

    print("\n" + "="*70)
    if success:
        print("✓ All refactored tests passed!")
        print("✓ Base class integration verified!")
    else:
        print("✗ Some tests failed")
    print("="*70)

    sys.exit(0 if success else 1)