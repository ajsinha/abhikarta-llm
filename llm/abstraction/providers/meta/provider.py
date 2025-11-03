"""
Meta (Llama) LLM Provider via Replicate

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
from .facade import MetaFacade


class MetaProvider(LLMProvider):
    """
    Provider for Meta's Llama models via Replicate API.
    
    Requires:
        - replicate library (pip install replicate)
        - API key via environment variable REPLICATE_API_TOKEN or configuration
    """
    
    def __init__(self):
        super().__init__()
        self.provider_name = "meta"
        self.client = None
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize Meta provider.
        
        Args:
            config: Provider configuration
            
        Raises:
            ProviderInitializationError: If initialization fails
            InvalidCredentialsError: If API key is missing or invalid
        """
        self.config = config
        
        # Get API key from environment or config
        self.api_key = os.environ.get('REPLICATE_API_TOKEN') or config.get('api_key')
        
        if not self.api_key:
            raise InvalidCredentialsError(
                "REPLICATE_API_TOKEN not found in environment or configuration"
            )
        
        try:
            # Try to import replicate library
            import replicate
            os.environ['REPLICATE_API_TOKEN'] = self.api_key
            self.client = replicate
            self.initialized = True
        except ImportError:
            raise ProviderInitializationError(
                "replicate library not installed. Install with: pip install replicate"
            )
        except Exception as e:
            raise ProviderInitializationError(f"Failed to initialize Meta client: {str(e)}")
    
    def create_facade(self, model_name: str) -> LLMFacade:
        """
        Create Meta facade for the specified model.
        
        Args:
            model_name: Name of the Llama model
            
        Returns:
            MetaFacade instance
            
        Raises:
            ModelNotFoundError: If model is not available
        """
        if model_name not in self.list_available_models():
            raise ModelNotFoundError(f"Model '{model_name}' not found in Meta provider")
        
        return MetaFacade(self, model_name, self.client)
    
    def list_available_models(self) -> List[str]:
        """
        List all available Llama models.
        
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
            return self.client is not None
        except:
            return False
    
    def get_provider_name(self) -> str:
        """
        Get provider name.
        
        Returns:
            'meta'
        """
        return self.provider_name
