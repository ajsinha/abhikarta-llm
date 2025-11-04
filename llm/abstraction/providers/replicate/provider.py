"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.0.1

Replicate Provider
"""

import os
from typing import Dict, Any, List
from llm.abstraction.core.provider import LLMProvider
from llm.abstraction.core.facade import LLMFacade, CompletionResponse
from llm.abstraction.core.exceptions import (
    InvalidCredentialsError,
    ProviderInitializationError
)


class ReplicateFacade(LLMFacade):
    """Facade for Replicate"""
    
    def __init__(self, provider: 'ReplicateProvider', model: str):
        super().__init__()
        self.provider = provider
        self.model = model
        self.client = provider.client
    
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        """Generate completion"""
        try:
            output = self.client.run(
                self.model,
                input={"prompt": prompt}
            )
            
            # Output can be string or list
            if isinstance(output, list):
                text = ''.join(output)
            else:
                text = str(output)
            
            return CompletionResponse(
                text=text,
                model=self.model,
                metadata={}
            )
        except Exception as e:
            raise ProviderInitializationError(f"Replicate completion failed: {e}")
    
    def chat(self, messages: List[Dict], **kwargs) -> CompletionResponse:
        """Generate chat completion"""
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        return self.complete(prompt, **kwargs)


class ReplicateProvider(LLMProvider):
    """
    Provider for Replicate
    
    Get API key: https://replicate.com
    """
    
    def __init__(self):
        super().__init__()
        self.provider_name = "replicate"
        self.client = None
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize Replicate provider"""
        self.config = config
        
        api_key = os.environ.get('REPLICATE_API_TOKEN') or config.get('api_key')
        if not api_key:
            raise InvalidCredentialsError("Replicate API key required")
        
        try:
            import replicate
            self.client = replicate
            os.environ['REPLICATE_API_TOKEN'] = api_key
        except ImportError:
            raise ProviderInitializationError(
                "replicate library not installed. Install with: pip install replicate"
            )
    
    def create_facade(self, model_name: str) -> LLMFacade:
        """Create facade"""
        return ReplicateFacade(self, model_name)
    
    def list_available_models(self) -> List[str]:
        """List available models"""
        return [
            'meta/llama-2-70b-chat',
            'meta/llama-2-13b-chat',
            'mistralai/mistral-7b-instruct-v0.2',
        ]
    
    def validate_credentials(self) -> bool:
        """Validate credentials"""
        return self.client is not None
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return self.provider_name
