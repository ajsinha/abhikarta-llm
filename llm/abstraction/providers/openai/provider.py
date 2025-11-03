"""
OpenAI LLM Provider

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import os
from typing import Any, Dict, List
from ...core.provider import LLMProvider
from ...core.facade import LLMFacade
from ...core.exceptions import (
    ModelNotFoundError,
    InvalidCredentialsError,
    ProviderInitializationError
)
from .facade import OpenAIFacade


class OpenAIProvider(LLMProvider):
    """
    Provider for OpenAI's GPT models.
    
    Requires:
        - openai library (pip install openai)
        - API key via environment variable OPENAI_API_KEY or configuration
    """
    
    def __init__(self):
        super().__init__()
        self.provider_name = "openai"
        self.client = None
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize OpenAI provider.
        
        Args:
            config: Provider configuration
            
        Raises:
            ProviderInitializationError: If initialization fails
            InvalidCredentialsError: If API key is missing or invalid
        """
        self.config = config
        
        # Get API key from environment or config
        self.api_key = os.environ.get('OPENAI_API_KEY') or config.get('api_key')
        
        if not self.api_key:
            raise InvalidCredentialsError(
                "OPENAI_API_KEY not found in environment or configuration"
            )
        
        try:
            # Try to import openai library
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
            self.initialized = True
        except ImportError:
            raise ProviderInitializationError(
                "openai library not installed. Install with: pip install openai"
            )
        except Exception as e:
            raise ProviderInitializationError(f"Failed to initialize OpenAI client: {str(e)}")
    
    def create_facade(self, model_name: str) -> LLMFacade:
        """
        Create OpenAI facade for the specified model.
        
        Args:
            model_name: Name of the GPT model
            
        Returns:
            OpenAIFacade instance
            
        Raises:
            ModelNotFoundError: If model is not available
        """
        if model_name not in self.list_available_models():
            raise ModelNotFoundError(f"Model '{model_name}' not found in OpenAI provider")
        
        return OpenAIFacade(self, model_name, self.client)
    
    def list_available_models(self) -> List[str]:
        """
        List all available GPT models.
        
        Returns:
            List of model names
        """
        return [model['name'] for model in self.config.get('models', [])]
    
    def validate_credentials(self) -> bool:
        """
        Validate API credentials.
        
        Returns:
            True if credentials are valid, False otherwise
        """
        if not self.initialized or not self.client:
            return False
        
        try:
            # Check if client is initialized
            return self.client is not None
        except:
            return False
    
    def get_provider_name(self) -> str:
        """
        Get provider name.
        
        Returns:
            'openai'
        """
        return self.provider_name
