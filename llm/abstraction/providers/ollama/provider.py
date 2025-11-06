from typing import Dict, Any, List

import requests

from llm.abstraction import LLMProvider, LLMFacade
from llm.abstraction.core import ProviderInitializationError
from llm.abstraction.providers.ollama.facade import OllamaFacade


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
