"""
Google (Gemini) LLM Provider

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
from .facade import GoogleFacade


class GoogleProvider(LLMProvider):
    """
    Provider for Google's Gemini models.
    
    Requires:
        - google-generativeai library (pip install google-generativeai)
        - API key via environment variable GOOGLE_API_KEY or configuration
    """
    
    def __init__(self):
        super().__init__()
        self.provider_name = "google"
        self.client = None
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize Google provider.
        
        Args:
            config: Provider configuration
            
        Raises:
            ProviderInitializationError: If initialization fails
            InvalidCredentialsError: If API key is missing or invalid
        """
        self.config = config
        
        # Get API key from environment or config
        self.api_key = os.environ.get('GOOGLE_API_KEY') or config.get('api_key')
        
        if not self.api_key:
            raise InvalidCredentialsError(
                "GOOGLE_API_KEY not found in environment or configuration"
            )
        
        try:
            # Try to import google.generativeai library
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai
            self.initialized = True
        except ImportError:
            raise ProviderInitializationError(
                "google-generativeai library not installed. Install with: pip install google-generativeai"
            )
        except Exception as e:
            raise ProviderInitializationError(f"Failed to initialize Google client: {str(e)}")
    
    def create_facade(self, model_name: str) -> LLMFacade:
        """
        Create Google facade for the specified model.
        
        Args:
            model_name: Name of the Gemini model
            
        Returns:
            GoogleFacade instance
            
        Raises:
            ModelNotFoundError: If model is not available
        """
        if model_name not in self.list_available_models():
            raise ModelNotFoundError(f"Model '{model_name}' not found in Google provider")
        
        return GoogleFacade(self, model_name, self.client)
    
    def list_available_models(self) -> List[str]:
        """
        List all available Gemini models.
        
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
            'google'
        """
        return self.provider_name
