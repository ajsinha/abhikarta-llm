"""
Mock LLM Provider for Testing

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

from typing import Any, Dict, List
from ...core.provider import LLMProvider
from ...core.facade import LLMFacade
from ...core.exceptions import ModelNotFoundError
from .facade import MockFacade


class MockProvider(LLMProvider):
    """
    Mock provider for testing and development.
    
    Does not require API keys and returns predefined responses.
    """
    
    def __init__(self):
        super().__init__()
        self.provider_name = "mock"
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize mock provider.
        
        Args:
            config: Configuration dictionary (ignored for mock)
        """
        self.config = config
        
        # Default mock models
        if 'models' not in self.config:
            self.config['models'] = [
                {
                    'name': 'mock-model',
                    'version': '1.0',
                    'description': 'Mock model for testing',
                    'context_window': 4096,
                    'max_output': 1024,
                    'cost': {
                        'input_per_1k': 0.0,
                        'output_per_1k': 0.0
                    },
                    'capabilities': {
                        'chat': True,
                        'completion': True,
                        'streaming': True,
                        'function_calling': False,
                        'vision': False
                    }
                },
                {
                    'name': 'mock-advanced',
                    'version': '2.0',
                    'description': 'Advanced mock model',
                    'context_window': 8192,
                    'max_output': 2048,
                    'cost': {
                        'input_per_1k': 0.0,
                        'output_per_1k': 0.0
                    },
                    'capabilities': {
                        'chat': True,
                        'completion': True,
                        'streaming': True,
                        'function_calling': True,
                        'vision': True
                    }
                }
            ]
        
        self.initialized = True
    
    def create_facade(self, model_name: str) -> LLMFacade:
        """
        Create mock facade for the specified model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            MockFacade instance
            
        Raises:
            ModelNotFoundError: If model is not available
        """
        if model_name not in self.list_available_models():
            raise ModelNotFoundError(f"Model '{model_name}' not found in mock provider")
        
        return MockFacade(self, model_name)
    
    def list_available_models(self) -> List[str]:
        """
        List all available mock models.
        
        Returns:
            List of model names
        """
        return [model['name'] for model in self.config.get('models', [])]
    
    def validate_credentials(self) -> bool:
        """
        Validate credentials (always returns True for mock).
        
        Returns:
            True
        """
        return True
    
    def get_provider_name(self) -> str:
        """
        Get provider name.
        
        Returns:
            'mock'
        """
        return self.provider_name
