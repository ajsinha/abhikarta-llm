from typing import List, Dict

from llm.abstraction import LLMFacade, CompletionResponse
from llm.abstraction.core import ProviderInitializationError
from llm.abstraction.providers.together import TogetherProvider


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
