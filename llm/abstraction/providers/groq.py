"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.4

Groq Provider - Ultra-Fast LLM Inference
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


class GroqFacade(LLMFacade):
    """Facade for Groq interactions"""
    
    def __init__(self, provider: 'GroqProvider', model: str):
        super().__init__()
        self.provider = provider
        self.model = model
        self.client = provider.client
    
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        """Generate completion"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get('max_tokens', 1024),
                temperature=kwargs.get('temperature', 0.7),
            )
            
            return CompletionResponse(
                text=response.choices[0].message.content if response.choices else "",
                model=self.model,
                metadata={
                    'usage': response.usage.__dict__ if hasattr(response, 'usage') else {}
                }
            )
        except Exception as e:
            raise ProviderInitializationError(f"Groq completion failed: {e}")
    
    def chat(self, messages: List[Dict], **kwargs) -> CompletionResponse:
        """Generate chat completion"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', 1024),
                temperature=kwargs.get('temperature', 0.7),
            )
            
            return CompletionResponse(
                text=response.choices[0].message.content if response.choices else "",
                model=self.model,
                metadata={'usage': response.usage.__dict__ if hasattr(response, 'usage') else {}}
            )
        except Exception as e:
            raise ProviderInitializationError(f"Groq chat failed: {e}")


class GroqProvider(LLMProvider):
    """
    Provider for Groq
    
    Groq provides ultra-fast LLM inference (500+ tokens/second).
    Supports models: mixtral-8x7b-32768, llama2-70b-4096
    
    Get API key: https://console.groq.com
    """
    
    def __init__(self):
        super().__init__()
        self.provider_name = "groq"
        self.client = None
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize Groq provider"""
        self.config = config
        
        # Get API key
        self.api_key = os.environ.get('GROQ_API_KEY') or config.get('api_key')
        if not self.api_key:
            raise InvalidCredentialsError("Groq API key required")
        
        # Initialize client
        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
        except ImportError:
            raise ProviderInitializationError(
                "groq library not installed. Install with: pip install groq"
            )
    
    def create_facade(self, model_name: str) -> LLMFacade:
        """Create facade for specified model"""
        return GroqFacade(self, model_name)
    
    def list_available_models(self) -> List[str]:
        """List available models"""
        return [
            'mixtral-8x7b-32768',
            'llama2-70b-4096',
            'gemma-7b-it',
        ]
    
    def validate_credentials(self) -> bool:
        """Validate API credentials"""
        return self.api_key is not None
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return self.provider_name
