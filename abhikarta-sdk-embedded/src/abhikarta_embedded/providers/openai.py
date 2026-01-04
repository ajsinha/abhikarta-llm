"""OpenAI Provider."""
import os
from typing import Dict, List, Optional
from .base import BaseProvider, ProviderConfig

class OpenAIProvider(BaseProvider):
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.api_key = config.api_key or os.environ.get("OPENAI_API_KEY")
        self.default_model = config.default_model or "gpt-4o-mini"
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key)
        return self._client
    
    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None,
             temperature: float = 0.7, max_tokens: int = 2048, **kwargs) -> str:
        client = self._get_client()
        response = client.chat.completions.create(model=model or self.default_model,
            messages=messages, temperature=temperature, max_tokens=max_tokens, **kwargs)
        return response.choices[0].message.content or ""
    
    def complete(self, prompt: str, model: Optional[str] = None,
                 temperature: float = 0.7, max_tokens: int = 2048, **kwargs) -> str:
        return self.chat([{"role": "user", "content": prompt}], model, temperature, max_tokens, **kwargs)
