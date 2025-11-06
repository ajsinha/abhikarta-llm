from typing import List, Dict

import requests

from llm.abstraction import LLMFacade, CompletionResponse
from llm.abstraction.core import ProviderInitializationError
from llm.abstraction.providers.ollama import OllamaProvider


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
