"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.2
"""

"""HuggingFace LLM Provider"""
import os
from typing import Any, Dict, List
from ...core.provider import LLMProvider
from ...core.facade import LLMFacade
from ...core.exceptions import ModelNotFoundError, InvalidCredentialsError, ProviderInitializationError
from .facade import HuggingFaceFacade

class HuggingFaceProvider(LLMProvider):
    def __init__(self):
        super().__init__()
        self.provider_name = "huggingface"
        self.client = None
    
    def initialize(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.api_key = os.environ.get('HUGGINGFACE_API_KEY') or config.get('api_key')
        
        try:
            from huggingface_hub import InferenceClient
            if self.api_key:
                self.client = InferenceClient(token=self.api_key)
            else:
                self.client = InferenceClient()
            self.initialized = True
        except ImportError:
            raise ProviderInitializationError(
                "huggingface_hub not installed. Install with: pip install huggingface_hub"
            )
    
    def create_facade(self, model_name: str) -> LLMFacade:
        if model_name not in self.list_available_models():
            raise ModelNotFoundError(f"Model '{model_name}' not found")
        return HuggingFaceFacade(self, model_name, self.client)
    
    def list_available_models(self) -> List[str]:
        return [model['name'] for model in self.config.get('models', [])]
    
    def validate_credentials(self) -> bool:
        return self.initialized
    
    def get_provider_name(self) -> str:
        return self.provider_name
