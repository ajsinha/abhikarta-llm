"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.0.1

Cohere Provider
"""

import os
from typing import Dict, Any, List
from llm.abstraction.core.provider import LLMProvider
from llm.abstraction.core.facade import LLMFacade, CompletionResponse
from llm.abstraction.core.exceptions import (
    InvalidCredentialsError,
    ProviderInitializationError
)


class CohereFacade(LLMFacade):
    """Facade for Cohere"""
    
    def __init__(self, provider: 'CohereProvider', model: str):
        super().__init__()
        self.provider = provider
        self.model = model
        self.client = provider.client
    
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        """Generate completion"""
        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                max_tokens=kwargs.get('max_tokens', 512),
                temperature=kwargs.get('temperature', 0.7),
            )
            
            return CompletionResponse(
                text=response.generations[0].text if response.generations else "",
                model=self.model,
                metadata={}
            )
        except Exception as e:
            raise ProviderInitializationError(f"Cohere completion failed: {e}")
    
    def chat(self, messages: List[Dict], **kwargs) -> CompletionResponse:
        """Generate chat completion"""
        # Convert messages to prompt
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        return self.complete(prompt, **kwargs)


class CohereProvider(LLMProvider):
    """
    Provider for Cohere
    
    Get API key: https://dashboard.cohere.ai
    """
    
    def __init__(self):
        super().__init__()
        self.provider_name = "cohere"
        self.client = None
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize Cohere provider"""
        self.config = config
        
        api_key = os.environ.get('COHERE_API_KEY') or config.get('api_key')
        if not api_key:
            raise InvalidCredentialsError("Cohere API key required")
        
        try:
            import cohere
            self.client = cohere.Client(api_key)
        except ImportError:
            raise ProviderInitializationError(
                "cohere library not installed. Install with: pip install cohere"
            )
    
    def create_facade(self, model_name: str) -> LLMFacade:
        """Create facade"""
        return CohereFacade(self, model_name)
    
    def list_available_models(self) -> List[str]:
        """List available models"""
        return ['command', 'command-light', 'command-nightly']
    
    def validate_credentials(self) -> bool:
        """Validate credentials"""
        return self.client is not None
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return self.provider_name
