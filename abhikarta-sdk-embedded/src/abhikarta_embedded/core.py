"""
Abhikarta SDK Embedded Core - Main application class.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .providers import BaseProvider
    from .tools import ToolRegistry

logger = logging.getLogger(__name__)


@dataclass
class AbhikartaConfig:
    """Configuration for Abhikarta SDK Embedded.
    
    Attributes:
        default_provider: Default LLM provider (ollama, openai, anthropic)
        default_model: Default model to use
        log_level: Logging level
        timeout: Default timeout for LLM calls
    """
    default_provider: str = "ollama"
    default_model: str = "llama3.2:3b"
    log_level: str = "INFO"
    timeout: int = 300
    max_retries: int = 3
    
    # Provider-specific settings
    ollama_base_url: str = "http://localhost:11434"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None


class Abhikarta:
    """Main Abhikarta SDK Embedded class.
    
    Use this for standalone applications without a server.
    
    Example:
        >>> from abhikarta_embedded import Abhikarta
        >>> 
        >>> # Initialize
        >>> app = Abhikarta()
        >>> 
        >>> # Configure Ollama
        >>> app.configure_provider("ollama", base_url="http://localhost:11434")
        >>> 
        >>> # Create an agent using fluent API
        >>> agent = (app.agent("Research Assistant")
        ...     .type("react")
        ...     .model("llama3.2:3b")
        ...     .build())
        >>> 
        >>> result = agent.run("Research AI trends")
    """
    
    _instance: Optional[Abhikarta] = None
    
    def __init__(self, config: Optional[AbhikartaConfig] = None):
        """Initialize Abhikarta SDK Embedded.
        
        Args:
            config: Optional configuration
        """
        self.config = config or AbhikartaConfig()
        self._providers: Dict[str, "BaseProvider"] = {}
        self._tool_registry: Optional["ToolRegistry"] = None
        self._agents: Dict[str, Any] = {}
        self._workflows: Dict[str, Any] = {}
        self._swarms: Dict[str, Any] = {}
        self._organizations: Dict[str, Any] = {}
        
        # Setup logging
        logging.basicConfig(level=getattr(logging, self.config.log_level))
        
        # Initialize default providers
        self._init_providers()
        
        logger.info(f"Abhikarta SDK Embedded v{self.version} initialized")
    
    @property
    def version(self) -> str:
        """Get SDK version."""
        from . import __version__
        return __version__
    
    @classmethod
    def get_instance(cls, config: Optional[AbhikartaConfig] = None) -> Abhikarta:
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = cls(config)
        return cls._instance
    
    def _init_providers(self):
        """Initialize default providers."""
        from .providers import (
            OllamaProvider,
            OpenAIProvider,
            AnthropicProvider,
            ProviderConfig,
        )
        
        # Initialize Ollama (always available for local use)
        try:
            ollama_config = ProviderConfig(
                name="ollama",
                base_url=self.config.ollama_base_url,
                default_model=self.config.default_model
            )
            self._providers["ollama"] = OllamaProvider(ollama_config)
        except Exception as e:
            logger.debug(f"Ollama provider not available: {e}")
        
        # Initialize OpenAI if API key provided
        if self.config.openai_api_key:
            try:
                openai_config = ProviderConfig(
                    name="openai",
                    api_key=self.config.openai_api_key,
                    default_model="gpt-4o-mini"
                )
                self._providers["openai"] = OpenAIProvider(openai_config)
            except Exception as e:
                logger.debug(f"OpenAI provider not available: {e}")
        
        # Initialize Anthropic if API key provided
        if self.config.anthropic_api_key:
            try:
                anthropic_config = ProviderConfig(
                    name="anthropic",
                    api_key=self.config.anthropic_api_key,
                    default_model="claude-sonnet-4-20250514"
                )
                self._providers["anthropic"] = AnthropicProvider(anthropic_config)
            except Exception as e:
                logger.debug(f"Anthropic provider not available: {e}")
    
    def configure_provider(
        self,
        name: str,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs
    ) -> "Abhikarta":
        """Configure a provider.
        
        Args:
            name: Provider name (ollama, openai, anthropic)
            base_url: Base URL for the provider
            api_key: API key
            **kwargs: Additional configuration
            
        Returns:
            Self for chaining
        """
        from .providers import (
            OllamaProvider,
            OpenAIProvider,
            AnthropicProvider,
            ProviderConfig,
        )
        
        config = ProviderConfig(name=name, base_url=base_url, api_key=api_key, **kwargs)
        
        provider_classes = {
            "ollama": OllamaProvider,
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
        }
        
        if name in provider_classes:
            self._providers[name] = provider_classes[name](config)
        
        return self
    
    def get_provider(self, name: Optional[str] = None) -> "BaseProvider":
        """Get a provider instance.
        
        Args:
            name: Provider name (uses default if not specified)
            
        Returns:
            Provider instance
        """
        name = name or self.config.default_provider
        if name not in self._providers:
            raise ValueError(f"Provider '{name}' not available. Configure it first.")
        return self._providers[name]
    
    @property
    def tools(self) -> "ToolRegistry":
        """Get the tool registry."""
        if self._tool_registry is None:
            from .tools import ToolRegistry
            self._tool_registry = ToolRegistry()
        return self._tool_registry
    
    def agent(self, name: str) -> "AgentBuilder":
        """Create an agent builder.
        
        Args:
            name: Agent name
            
        Returns:
            AgentBuilder for fluent configuration
        """
        from .agents import AgentBuilder
        return AgentBuilder(self, name)
    
    def workflow(self, name: str) -> "WorkflowBuilder":
        """Create a workflow builder."""
        from .workflows import WorkflowBuilder
        return WorkflowBuilder(self, name)
    
    def swarm(self, name: str) -> "SwarmBuilder":
        """Create a swarm builder."""
        from .swarms import SwarmBuilder
        return SwarmBuilder(self, name)
    
    def organization(self, name: str) -> "OrganizationBuilder":
        """Create an organization builder."""
        from .orgs import OrganizationBuilder
        return OrganizationBuilder(self, name)


# Builders are imported from their respective modules
class AgentBuilder:
    """Placeholder - actual implementation in agents module."""
    pass


class WorkflowBuilder:
    """Placeholder - actual implementation in workflows module."""
    pass


class SwarmBuilder:
    """Placeholder - actual implementation in swarms module."""
    pass


class OrganizationBuilder:
    """Placeholder - actual implementation in orgs module."""
    pass
