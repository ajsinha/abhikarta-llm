"""Base Provider class."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class ProviderConfig:
    name: str
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    default_model: str = ""
    timeout: int = 300

class BaseProvider(ABC):
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.name = config.name
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None,
             temperature: float = 0.7, max_tokens: int = 2048, **kwargs) -> str:
        pass
    
    @abstractmethod
    def complete(self, prompt: str, model: Optional[str] = None,
                 temperature: float = 0.7, max_tokens: int = 2048, **kwargs) -> str:
        pass

class Provider:
    @classmethod
    def create(cls, name: str, **kwargs) -> BaseProvider:
        from .ollama import OllamaProvider
        from .openai import OpenAIProvider
        from .anthropic import AnthropicProvider
        providers = {"ollama": OllamaProvider, "openai": OpenAIProvider, "anthropic": AnthropicProvider}
        if name not in providers:
            raise ValueError(f"Unknown provider: {name}")
        return providers[name](ProviderConfig(name=name, **kwargs))
