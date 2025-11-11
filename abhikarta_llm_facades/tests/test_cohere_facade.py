"""
Cohere Facade Tests

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

import unittest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from facades.cohere_facade import CohereFacade
from facades.llm_facade import GenerationConfig, ModelCapability


class TestCohereFacade(unittest.TestCase):
    """Test suite for CohereFacade."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test-api-key-cohere"
        self.model_name = "command-r-plus"
    
    def test_initialization(self):
        """Test facade initialization."""
        facade = CohereFacade(
            model_name=self.model_name,
            api_key=self.api_key
        )
        
        self.assertIsNotNone(facade)
        self.assertEqual(facade.model_name, self.model_name)
        self.assertEqual(facade.api_key, self.api_key)
        self.assertEqual(facade.provider_name, "cohere")
    
    def test_get_capabilities(self):
        """Test capability detection."""
        facade = CohereFacade(
            model_name=self.model_name,
            api_key=self.api_key
        )
        
        capabilities = facade.get_capabilities()
        self.assertIsInstance(capabilities, list)
        self.assertTrue(len(capabilities) > 0)
        self.assertIn(ModelCapability.CHAT_COMPLETION, capabilities)
    
    def test_supports_capability(self):
        """Test capability checking."""
        facade = CohereFacade(
            model_name=self.model_name,
            api_key=self.api_key
        )
        
        self.assertTrue(facade.supports_capability(ModelCapability.CHAT_COMPLETION))
    
    @patch('facades.cohere_facade.cohere.Client')
    def test_chat_completion(self, mock_client):
        """Test chat completion."""
        # Mock the response
        mock_response = Mock()
        mock_response.text = "Test response"
        mock_response.meta = Mock(tokens=Mock(input_tokens=10, output_tokens=5))
        mock_client.return_value.chat.return_value = mock_response
        
        facade = CohereFacade(
            model_name=self.model_name,
            api_key=self.api_key
        )
        
        messages = [
            {"role": "user", "content": "Hello!"}
        ]
        
        result = facade.chat_completion(messages)
        
        self.assertIsInstance(result, dict)
        self.assertIn("content", result)
        self.assertIn("role", result)
        self.assertEqual(result["role"], "assistant")
    
    def test_completion(self):
        """Test text completion."""
        facade = CohereFacade(
            model_name=self.model_name,
            api_key=self.api_key
        )
        
        # Mock to avoid actual API call
        with patch.object(facade, 'chat_completion', return_value={"content": "Test response"}):
            result = facade.completion("Test prompt")
            self.assertEqual(result, "Test response")
    
    def test_generation_config(self):
        """Test generation configuration."""
        config = GenerationConfig(
            max_tokens=100,
            temperature=0.7,
            top_p=0.9
        )
        
        self.assertEqual(config.max_tokens, 100)
        self.assertEqual(config.temperature, 0.7)
        self.assertEqual(config.top_p, 0.9)
    
    def test_count_tokens(self):
        """Test token counting."""
        facade = CohereFacade(
            model_name=self.model_name,
            api_key=self.api_key
        )
        
        text = "This is a test message."
        count = facade.count_tokens(text)
        
        self.assertIsInstance(count, int)
        self.assertGreater(count, 0)
    
    def test_format_messages(self):
        """Test message formatting."""
        facade = CohereFacade(
            model_name=self.model_name,
            api_key=self.api_key
        )
        
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        
        formatted = facade.format_messages(messages)
        
        self.assertIsInstance(formatted, str)
        self.assertIn("helpful", formatted)
        self.assertIn("Hello", formatted)


class TestCohereFacadeIntegration(unittest.TestCase):
    """Integration tests for CohereFacade (requires API key)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = os.getenv("COHERE_API_KEY")
        self.model_name = "command-r-plus"
    
    @unittest.skipUnless(os.getenv("COHERE_API_KEY"), "API key not set")
    def test_real_chat_completion(self):
        """Test actual chat completion with real API."""
        facade = CohereFacade(
            model_name=self.model_name,
            api_key=self.api_key
        )
        
        messages = [
            {"role": "user", "content": "Say 'test successful' if you can read this."}
        ]
        
        result = facade.chat_completion(messages)
        
        self.assertIsInstance(result, dict)
        self.assertIn("content", result)
        self.assertIsInstance(result["content"], str)
        self.assertGreater(len(result["content"]), 0)


def suite():
    """Create test suite."""
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestCohereFacade))
    test_suite.addTest(unittest.makeSuite(TestCohereFacadeIntegration))
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
