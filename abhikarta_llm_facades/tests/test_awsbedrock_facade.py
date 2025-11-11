"""
AWS Bedrock Facade Tests

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

from facades.awsbedrock_facade import AWSBedrockFacade
from facades.llm_facade import GenerationConfig, ModelCapability


class TestAWSBedrockFacade(unittest.TestCase):
    """Test suite for AWSBedrockFacade."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.model_name = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    @patch('facades.awsbedrock_facade.boto3')
    def test_initialization(self, mock_client):
        """Test facade initialization."""
        facade = AWSBedrockFacade(model_name=self.model_name)
        
        self.assertIsNotNone(facade)
        self.assertEqual(facade.model_name, self.model_name)
        self.assertEqual(facade.provider_name, "awsbedrock")
    
    @patch('facades.awsbedrock_facade.boto3')
    def test_get_capabilities(self, mock_client):
        """Test capability detection."""
        facade = AWSBedrockFacade(model_name=self.model_name)
        
        capabilities = facade.get_capabilities()
        self.assertIsInstance(capabilities, list)
        self.assertTrue(len(capabilities) > 0)
    
    @patch('facades.awsbedrock_facade.boto3')
    def test_chat_completion_mock(self, mock_client):
        """Test chat completion with mocked client."""
        facade = AWSBedrockFacade(model_name=self.model_name)
        
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


class TestAWSBedrockFacadeIntegration(unittest.TestCase):
    """Integration tests for AWSBedrockFacade."""
    
    @unittest.skipUnless(os.getenv("AWS_ACCESS_KEY_ID"), "API credentials not set")
    def test_real_api_call(self):
        """Test with real API (requires credentials)."""
        pass  # Implement when needed


def suite():
    """Create test suite."""
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestAWSBedrockFacade))
    test_suite.addTest(unittest.makeSuite(TestAWSBedrockFacadeIntegration))
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
