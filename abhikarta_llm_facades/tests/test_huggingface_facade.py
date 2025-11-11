"""
HuggingFace Facade Tests

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

import unittest
import os
import sys
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from facades.huggingface_facade import HuggingfaceFacade
from facades.llm_facade import GenerationConfig, ModelCapability


class TestHuggingfaceFacade(unittest.TestCase):
    """Test suite for HuggingfaceFacade."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.model_name = "gpt2"
    
    @patch('facades.huggingface_facade.InferenceClient')
    def test_initialization(self, mock_client):
        """Test facade initialization."""
        facade = HuggingfaceFacade(model_name=self.model_name)
        
        self.assertIsNotNone(facade)
        self.assertEqual(facade.model_name, self.model_name)
        self.assertEqual(facade.provider_name, "huggingface")
    
    @patch('facades.huggingface_facade.InferenceClient')
    def test_get_capabilities(self, mock_client):
        """Test capability detection."""
        facade = HuggingfaceFacade(model_name=self.model_name)
        
        capabilities = facade.get_capabilities()
        self.assertIsInstance(capabilities, list)
        self.assertTrue(len(capabilities) > 0)
    
    @patch('facades.huggingface_facade.InferenceClient')
    def test_chat_completion_mock(self, mock_client):
        """Test chat completion with mocked client."""
        facade = HuggingfaceFacade(model_name=self.model_name)
        
        # Mock response
        with patch.object(facade, '_generate_api', return_value="Test response"):
            with patch.object(facade, '_generate_local', return_value="Test response"):
                with patch.object(facade, 'chat_completion', return_value={
                    "content": "Test response",
                    "role": "assistant",
                    "finish_reason": "stop",
                    "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
                }):
                    messages = [{"role": "user", "content": "Hello!"}]
                    result = facade.chat_completion(messages)
                    
                    self.assertIsInstance(result, dict)
                    self.assertIn("content", result)


class TestHuggingfaceFacadeIntegration(unittest.TestCase):
    """Integration tests for HuggingfaceFacade."""
    
    @unittest.skipUnless(os.getenv("HF_TOKEN"), "API credentials not set")
    def test_real_api_call(self):
        """Test with real API (requires credentials)."""
        pass  # Implement when needed


def suite():
    """Create test suite."""
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestHuggingfaceFacade))
    test_suite.addTest(unittest.makeSuite(TestHuggingfaceFacadeIntegration))
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
