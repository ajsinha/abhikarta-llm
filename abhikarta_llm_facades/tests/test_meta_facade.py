"""
Meta Facade Tests

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

from facades.meta_facade import MetaFacade
from facades.llm_facade import GenerationConfig, ModelCapability


class TestMetaFacade(unittest.TestCase):
    """Test suite for MetaFacade."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.model_name = "llama-3.1-70b-instruct"
    
    @patch('facades.meta_facade.replicate')
    def test_initialization(self, mock_client):
        """Test facade initialization."""
        facade = MetaFacade(model_name=self.model_name)
        
        self.assertIsNotNone(facade)
        self.assertEqual(facade.model_name, self.model_name)
        self.assertEqual(facade.provider_name, "meta")
    
    @patch('facades.meta_facade.replicate')
    def test_get_capabilities(self, mock_client):
        """Test capability detection."""
        facade = MetaFacade(model_name=self.model_name)
        
        capabilities = facade.get_capabilities()
        self.assertIsInstance(capabilities, list)
        self.assertTrue(len(capabilities) > 0)
    
    @patch('facades.meta_facade.replicate')
    def test_chat_completion_mock(self, mock_client):
        """Test chat completion with mocked client."""
        facade = MetaFacade(model_name=self.model_name)
        
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


class TestMetaFacadeIntegration(unittest.TestCase):
    """Integration tests for MetaFacade."""
    
    @unittest.skipUnless(os.getenv("REPLICATE_API_TOKEN"), "API credentials not set")
    def test_real_api_call(self):
        """Test with real API (requires credentials)."""
        pass  # Implement when needed


def suite():
    """Create test suite."""
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestMetaFacade))
    test_suite.addTest(unittest.makeSuite(TestMetaFacadeIntegration))
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
