"""Anthropic Provider."""
import os
from typing import Dict, List, Optional
from .base import BaseProvider, ProviderConfig

class AnthropicProvider(BaseProvider):
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.api_key = config.api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.default_model = config.default_model or "claude-sonnet-4-20250514"
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            from anthropic import Anthropic
            self._client = Anthropic(api_key=self.api_key)
        return self._client
    
    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None,
             temperature: float = 0.7, max_tokens: int = 2048, **kwargs) -> str:
        client = self._get_client()
        system = ""
        chat_msgs = []
        for msg in messages:
            if msg.get("role") == "system":
                system = msg.get("content", "")
            else:
                chat_msgs.append(msg)
        response = client.messages.create(model=model or self.default_model, max_tokens=max_tokens,
            system=system, messages=chat_msgs, **kwargs)
        return response.content[0].text if response.content else ""
    
    def complete(self, prompt: str, model: Optional[str] = None,
                 temperature: float = 0.7, max_tokens: int = 2048, **kwargs) -> str:
        return self.chat([{"role": "user", "content": prompt}], model, temperature, max_tokens, **kwargs)
