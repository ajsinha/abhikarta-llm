"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.2

Ollama Provider - Local LLM Inference
"""

import os
import requests
from typing import Optional, Dict, Any, List, Iterator
from llm.abstraction.core.provider import LLMProvider
from llm.abstraction.core.facade import LLMFacade, CompletionResponse
from llm.abstraction.core.exceptions import (
    ModelNotFoundError,
    InvalidCredentialsError,
    ProviderInitializationError
)


class OllamaFacade(LLMFacade):
    """Facade for Ollama interactions"""
    
    def __init__(self, provider: 'OllamaProvider', model: str):
        super().__init__()
        self.provider = provider
        self.model = model
        self.base_url = provider.base_url
    
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        """Generate completion"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get('temperature', 0.7),
                        "num_predict": kwargs.get('max_tokens', 512),
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return CompletionResponse(
                text=data.get('response', ''),
                model=self.model,
                metadata={
                    'total_duration': data.get('total_duration'),
                    'load_duration': data.get('load_duration'),
                    'prompt_eval_count': data.get('prompt_eval_count'),
                    'eval_count': data.get('eval_count'),
                }
            )
        except Exception as e:
            raise ProviderInitializationError(f"Ollama completion failed: {e}")
    
    def chat(self, messages: List[Dict], **kwargs) -> CompletionResponse:
        """Generate chat completion"""
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get('temperature', 0.7),
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return CompletionResponse(
                text=data.get('message', {}).get('content', ''),
                model=self.model,
                metadata={'usage': data.get('usage', {})}
            )
        except Exception as e:
            raise ProviderInitializationError(f"Ollama chat failed: {e}")


class OllamaProvider(LLMProvider):
    """
    Provider for Ollama
    
    Ollama runs LLMs locally - no API key required!
    100% free and private.
    
    Install: curl https://ollama.ai/install.sh | sh
    Models: llama2, mistral, codellama, phi, and more
    """
    
    def __init__(self):
        super().__init__()
        self.provider_name = "ollama"
        self.base_url = "http://localhost:11434"
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize Ollama provider"""
        self.config = config
        
        # Get base URL (default to localhost)
        self.base_url = config.get('base_url', 'http://localhost:11434')
        
        # Check if Ollama is running
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            response.raise_for_status()
        except Exception as e:
            raise ProviderInitializationError(
                f"Ollama not running at {self.base_url}. "
                f"Install: curl https://ollama.ai/install.sh | sh"
            )
    
    def create_facade(self, model_name: str) -> LLMFacade:
        """Create facade for specified model"""
        return OllamaFacade(self, model_name)
    
    def list_available_models(self) -> List[str]:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        except:
            return ['llama2', 'mistral', 'codellama', 'phi']
    
    def validate_credentials(self) -> bool:
        """Validate connection (no credentials needed)"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return self.provider_name
