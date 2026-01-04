"""Ollama Provider."""
from typing import Dict, List, Optional
import httpx
from .base import BaseProvider, ProviderConfig

class OllamaProvider(BaseProvider):
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.base_url = config.base_url or "http://localhost:11434"
        self.default_model = config.default_model or "llama3.2:3b"
    
    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None,
             temperature: float = 0.7, max_tokens: int = 2048, **kwargs) -> str:
        response = httpx.post(f"{self.base_url}/api/chat",
            json={"model": model or self.default_model, "messages": messages, "stream": False,
                  "options": {"temperature": temperature, "num_predict": max_tokens}},
            timeout=self.config.timeout)
        response.raise_for_status()
        return response.json().get("message", {}).get("content", "")
    
    def complete(self, prompt: str, model: Optional[str] = None,
                 temperature: float = 0.7, max_tokens: int = 2048, **kwargs) -> str:
        response = httpx.post(f"{self.base_url}/api/generate",
            json={"model": model or self.default_model, "prompt": prompt, "stream": False,
                  "options": {"temperature": temperature, "num_predict": max_tokens}},
            timeout=self.config.timeout)
        response.raise_for_status()
        return response.json().get("response", "")
