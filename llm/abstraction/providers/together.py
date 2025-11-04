"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.3

Together AI Provider - Open Source Models at Scale
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


class TogetherFacade(LLMFacade):
    """Facade for Together AI interactions"""
    
    def __init__(self, provider: 'TogetherProvider', model: str):
        super().__init__()
        self.provider = provider
        self.model = model
        self.client = provider.client
    
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        """Generate completion"""
        try:
            response = self.client.completions.create(
                model=self.model,
                prompt=prompt,
                max_tokens=kwargs.get('max_tokens', 512),
                temperature=kwargs.get('temperature', 0.7),
                top_p=kwargs.get('top_p', 1.0),
            )
            
            return CompletionResponse(
                text=response.choices[0].text if response.choices else "",
                model=self.model,
                metadata={
                    'usage': {
                        'prompt_tokens': getattr(response.usage, 'prompt_tokens', 0),
                        'completion_tokens': getattr(response.usage, 'completion_tokens', 0),
                        'total_tokens': getattr(response.usage, 'total_tokens', 0)
                    }
                }
            )
        except Exception as e:
            raise ProviderInitializationError(f"Together completion failed: {e}")
    
    def chat(self, messages: List[Dict], **kwargs) -> CompletionResponse:
        """Generate chat completion"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', 512),
                temperature=kwargs.get('temperature', 0.7),
            )
            
            return CompletionResponse(
                text=response.choices[0].message.content if response.choices else "",
                model=self.model,
                metadata={'usage': response.usage.__dict__ if hasattr(response, 'usage') else {}}
            )
        except Exception as e:
            raise ProviderInitializationError(f"Together chat failed: {e}")


class TogetherProvider(LLMProvider):
    """
    Provider for Together AI
    
    Together AI offers inference for 50+ open source models.
    Popular models:
    - meta-llama/Llama-2-70b-chat-hf
    - mistralai/Mixtral-8x7B-Instruct-v0.1
    - togethercomputer/RedPajama-INCITE-7B-Chat
    
    Get API key: https://api.together.xyz
    """
    
    def __init__(self):
        super().__init__()
        self.provider_name = "together"
        self.client = None
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize Together AI provider"""
        self.config = config
        
        # Get API key
        self.api_key = os.environ.get('TOGETHER_API_KEY') or config.get('api_key')
        if not self.api_key:
            raise InvalidCredentialsError("Together API key required")
        
        # Initialize client
        try:
            import together
            together.api_key = self.api_key
            self.client = together
        except ImportError:
            raise ProviderInitializationError(
                "together library not installed. Install with: pip install together"
            )
    
    def create_facade(self, model_name: str) -> LLMFacade:
        """Create facade for specified model"""
        return TogetherFacade(self, model_name)
    
    def list_available_models(self) -> List[str]:
        """List available models"""
        return [
            'meta-llama/Llama-2-70b-chat-hf',
            'mistralai/Mixtral-8x7B-Instruct-v0.1',
            'togethercomputer/RedPajama-INCITE-7B-Chat',
            'NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO',
        ]
    
    def validate_credentials(self) -> bool:
        """Validate API credentials"""
        return self.api_key is not None
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return self.provider_name
