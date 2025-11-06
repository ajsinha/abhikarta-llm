import os
from typing import Dict, Any, List

from llm.abstraction import LLMProvider, LLMFacade
from llm.abstraction.core import InvalidCredentialsError, ProviderInitializationError
from llm.abstraction.providers.mistral import MistralFacade


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
