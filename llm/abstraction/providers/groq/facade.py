from typing import List, Dict

from llm.abstraction import LLMFacade, CompletionResponse
from llm.abstraction.core import ProviderInitializationError
from llm.abstraction.providers.groq import GroqProvider


class GroqFacade(LLMFacade):
    """Facade for Groq interactions"""

    def __init__(self, provider: 'GroqProvider', model: str):
        super().__init__()
        self.provider = provider
        self.model = model
        self.client = provider.client

    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        """Generate completion"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get('max_tokens', 1024),
                temperature=kwargs.get('temperature', 0.7),
            )

            return CompletionResponse(
                text=response.choices[0].message.content if response.choices else "",
                model=self.model,
                metadata={
                    'usage': response.usage.__dict__ if hasattr(response, 'usage') else {}
                }
            )
        except Exception as e:
            raise ProviderInitializationError(f"Groq completion failed: {e}")

    def chat(self, messages: List[Dict], **kwargs) -> CompletionResponse:
        """Generate chat completion"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', 1024),
                temperature=kwargs.get('temperature', 0.7),
            )

            return CompletionResponse(
                text=response.choices[0].message.content if response.choices else "",
                model=self.model,
                metadata={'usage': response.usage.__dict__ if hasattr(response, 'usage') else {}}
            )
        except Exception as e:
            raise ProviderInitializationError(f"Groq chat failed: {e}")
