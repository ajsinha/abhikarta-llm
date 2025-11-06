from typing import List, Dict

from llm.abstraction import LLMFacade, CompletionResponse
from llm.abstraction.core import ProviderInitializationError


class MistralFacade(LLMFacade):
    """Facade for Mistral AI interactions"""

    def __init__(self, provider: 'MistralProvider', model: str):
        super().__init__()
        self.provider = provider
        self.model = model
        self.client = provider.client

    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        """Generate completion"""
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get('max_tokens', 512),
                temperature=kwargs.get('temperature', 0.7),
            )

            return CompletionResponse(
                text=response.choices[0].message.content if response.choices else "",
                model=self.model,
                metadata={
                    'usage': getattr(response, 'usage', {})
                }
            )
        except Exception as e:
            raise ProviderInitializationError(f"Mistral completion failed: {e}")

    def chat(self, messages: List[Dict], **kwargs) -> CompletionResponse:
        """Generate chat completion"""
        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', 512),
                temperature=kwargs.get('temperature', 0.7),
            )

            return CompletionResponse(
                text=response.choices[0].message.content if response.choices else "",
                model=self.model,
                metadata={'usage': getattr(response, 'usage', {})}
            )
        except Exception as e:
            raise ProviderInitializationError(f"Mistral chat failed: {e}")
