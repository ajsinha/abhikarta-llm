import os
from typing import Dict, Any, List

from llm.abstraction import LLMProvider, LLMFacade
from llm.abstraction.core import InvalidCredentialsError, ProviderInitializationError
from llm.abstraction.providers.groq.facade import GroqFacade


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
