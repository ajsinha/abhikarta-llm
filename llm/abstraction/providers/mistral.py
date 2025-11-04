"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.3

Mistral AI Provider - European GDPR-Compliant LLM
"""

import os
from typing import Optional, Dict, Any, List, Iterator
from llm.abstraction.core.provider import LLMProvider
from llm.abstraction.core.facade import LLMFacade, CompletionResponse
from llm.abstraction.core.exceptions import (
    ModelNotFoundError,
    InvalidCredentialsError,
    ProviderInitializationError
)


class MistralFacade(LLMFacade):
    """Facade for Mistral AI interactions"""
    
    def __init__(self, provider: 'MistralProvider', model: str):
        super().__init__()
        self.provider = provider
        self.model = model
        self.client = provider.client
    
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        """Generate completion"""
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get('max_tokens', 512),
                temperature=kwargs.get('temperature', 0.7),
            )
            
            return CompletionResponse(
                text=response.choices[0].message.content if response.choices else "",
                model=self.model,
                metadata={
                    'usage': getattr(response, 'usage', {})
                }
            )
        except Exception as e:
            raise ProviderInitializationError(f"Mistral completion failed: {e}")
    
    def chat(self, messages: List[Dict], **kwargs) -> CompletionResponse:
        """Generate chat completion"""
        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', 512),
                temperature=kwargs.get('temperature', 0.7),
            )
            
            return CompletionResponse(
                text=response.choices[0].message.content if response.choices else "",
                model=self.model,
                metadata={'usage': getattr(response, 'usage', {})}
            )
        except Exception as e:
            raise ProviderInitializationError(f"Mistral chat failed: {e}")


class MistralProvider(LLMProvider):
    """
    Provider for Mistral AI
    
    Mistral AI provides GDPR-compliant European models.
    Models: mistral-tiny, mistral-small, mistral-medium, mistral-large
    
    Get API key: https://console.mistral.ai
    """
    
    def __init__(self):
        super().__init__()
        self.provider_name = "mistral"
        self.client = None
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize Mistral AI provider"""
        self.config = config
        
        # Get API key
        self.api_key = os.environ.get('MISTRAL_API_KEY') or config.get('api_key')
        if not self.api_key:
            raise InvalidCredentialsError("Mistral API key required")
        
        # Initialize client
        try:
            from mistralai.client import MistralClient
            self.client = MistralClient(api_key=self.api_key)
        except ImportError:
            raise ProviderInitializationError(
                "mistralai library not installed. Install with: pip install mistralai"
            )
    
    def create_facade(self, model_name: str) -> LLMFacade:
        """Create facade for specified model"""
        return MistralFacade(self, model_name)
    
    def list_available_models(self) -> List[str]:
        """List available models"""
        return [
            'mistral-tiny',
            'mistral-small',
            'mistral-medium',
            'mistral-large-latest',
        ]
    
    def validate_credentials(self) -> bool:
        """Validate API credentials"""
        return self.api_key is not None
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return self.provider_name
