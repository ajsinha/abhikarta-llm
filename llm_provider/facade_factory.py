"""
Abhikarta Facade Factory - Universal Provider Facade Creation

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This module and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Patent Pending: Certain architectural patterns and implementations described in this
module may be subject to patent applications.

Description:
This module provides a universal factory for creating LLM facades that work with
either JSON or Database configurations. The factory automatically detects the
configuration source and creates the appropriate facade instance.
"""

from typing import Dict, Optional, Type, Any, List, Tuple
from pathlib import Path

from llm_facade import LLMFacade
from model_management.model_provider import ModelProvider
from model_management.model_provider_json import load_providers as load_json_providers
from model_management.model_provider_db import load_providers as load_db_providers
from core import SingletonMeta
from model_management.model_management_db_handler import ModelManagementDBHandler

class FacadeFactory(metaclass=SingletonMeta):
    """
    Universal factory for creating provider facades with dynamic configuration.
    
    This factory supports both JSON and Database configuration sources and
    automatically creates the appropriate facade for any supported provider.
    
    Features:
    - Automatic provider detection
    - Support for JSON and Database backends
    - Provider-specific facade creation
    - Configuration validation
    - Caching of provider configurations
    
    Usage:
        # Using JSON configuration
        factory = FacadeFactory(config_source="json", config_path="./config")
        facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
        
        # Using Database configuration
        factory = FacadeFactory(config_source="db", db_handler=db_handler)
        facade = factory.create_facade("openai", "gpt-4")
    """
    
    # Registry of provider-specific facade classes
    # Maps provider name to facade class
    _PROVIDER_FACADES: Dict[str, Type[LLMFacade]] = {}
    
    def __init__(
        self,
        config_source: str = "json",
        config_path: Optional[str] = None,
        db_connection_pool_name: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize the facade factory.
        
        Args:
            config_source: Configuration source ("json" or "db")
            config_path: Path to JSON configuration directory (for JSON source)
            db_connection_pool_name: Database connection pool name (for DB source)
            **kwargs: Additional configuration options
        """
        self.config_source = config_source.lower()
        self.config_path = config_path
        self.db_connection_pool_name = db_connection_pool_name
        self.db_handler = None
        self.kwargs = kwargs
        
        # Cache for loaded providers
        self._providers_cache: Dict[str, ModelProvider] = {}
        
        # Validate configuration
        if self.config_source == "json":
            if not self.config_path:
                raise ValueError("config_path is required for JSON configuration")
            if not Path(self.config_path).exists():
                raise ValueError(f"Configuration path does not exist: {self.config_path}")
        elif self.config_source == "db":
            if not self.db_connection_pool_name:
                raise ValueError("db_handler is required for DB configuration")
            self.db_handler = ModelManagementDBHandler.get_instance(self.db_connection_pool_name)
        else:
            raise ValueError(f"Invalid config_source: {self.config_source}")
        
        # Load all providers
        self._load_all_providers()
    
    def _load_all_providers(self) -> None:
        """Load all providers from configured source."""
        if self.config_source == "json":
            self._providers_cache = load_json_providers(self.config_path)
        else:  # db
            self._providers_cache = load_db_providers(self.db_handler)
    
    def reload_providers(self) -> None:
        """Reload all providers from source."""
        self._providers_cache.clear()
        self._load_all_providers()
    
    def get_provider(self, provider_name: str) -> ModelProvider:
        """
        Get ModelProvider instance for a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            ModelProvider instance
            
        Raises:
            ValueError: If provider not found
        """
        if provider_name not in self._providers_cache:
            raise ValueError(f"Provider '{provider_name}' not found")
        return self._providers_cache[provider_name]
    
    def list_providers(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available providers with their details.
        
        Returns:
            Dictionary mapping provider names to provider information
        """
        result = {}
        for name, provider in self._providers_cache.items():
            result[name] = {
                'provider': provider.provider,
                'api_version': provider.api_version,
                'base_url': provider.base_url,
                'enabled': provider.enabled,
                'model_count': len(provider.models)
            }
        return result
    
    def list_models(self, provider_name: Optional[str] = None) -> Dict[str, List[str]]:
        """
        List available models for provider(s).
        
        Args:
            provider_name: Optional provider name (lists all if None)
            
        Returns:
            Dictionary mapping provider names to list of model names
        """
        result = {}
        
        if provider_name:
            provider = self.get_provider(provider_name)
            result[provider_name] = [m.name for m in provider.models if m.enabled]
        else:
            for name, provider in self._providers_cache.items():
                if provider.enabled:
                    result[name] = [m.name for m in provider.models if m.enabled]
        
        return result
    
    def create_facade(
        self,
        provider_name: str,
        model_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        **kwargs
    ) -> LLMFacade:
        """
        Create a facade instance for the specified provider and model.
        
        Args:
            provider_name: Name of the provider (e.g., "anthropic", "openai")
            model_name: Name of the model (e.g., "claude-3-5-sonnet-20241022")
            api_key: API key (reads from environment if None)
            base_url: Override base URL
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts
            **kwargs: Provider-specific configuration
            
        Returns:
            Configured LLMFacade instance
            
        Raises:
            ValueError: If provider or model not found
            AuthenticationException: If API key invalid or missing
            
        Example:
            >>> factory = FacadeFactory(config_source="json", config_path="config")
            >>> facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
            >>> response = facade.chat_completion([{"role": "user", "content": "Hello!"}])
        """
        # Get provider configuration
        provider = self.get_provider(provider_name)
        
        # Check if model exists
        model = provider.get_model_by_name(model_name)
        if not model:
            available = [m.name for m in provider.models]
            raise ValueError(
                f"Model '{model_name}' not found in provider '{provider_name}'. "
                f"Available models: {', '.join(available)}"
            )
        
        if not model.enabled:
            raise ValueError(f"Model '{model_name}' is disabled")
        
        # Check for provider-specific facade
        facade_class = self._PROVIDER_FACADES.get(provider_name)
        
        if facade_class:
            # Use provider-specific facade
            return facade_class(
                provider=provider,
                model_name=model_name,
                api_key=api_key,
                base_url=base_url,
                timeout=timeout,
                max_retries=max_retries,
                **kwargs
            )
        else:
            # Use generic base facade (limited functionality)
            # Provider-specific facades should be registered for full functionality
            raise NotImplementedError(
                f"No facade implementation found for provider '{provider_name}'. "
                f"Please register a provider-specific facade using register_facade()."
            )
    
    @classmethod
    def register_facade(
        cls,
        provider_name: str,
        facade_class: Type[LLMFacade]
    ) -> None:
        """
        Register a provider-specific facade class.
        
        Args:
            provider_name: Name of the provider
            facade_class: Facade class to use for this provider
            
        Example:
            >>> FacadeFactory.register_facade("anthropic", AnthropicFacade)
            >>> FacadeFactory.register_facade("openai", OpenAIFacade)
        """
        cls._PROVIDER_FACADES[provider_name] = facade_class
    
    @classmethod
    def get_registered_providers(cls) -> List[str]:
        """Get list of providers with registered facades."""
        return list(cls._PROVIDER_FACADES.keys())
    
    def create_cheapest_facade(
        self,
        capability: str,
        input_tokens: int = 100000,
        output_tokens: int = 1000,
        **kwargs
    ) -> Tuple[LLMFacade, float]:
        """
        Create facade for the cheapest model supporting a capability.
        
        Args:
            capability: Required capability
            input_tokens: Expected input tokens for cost calculation
            output_tokens: Expected output tokens for cost calculation
            **kwargs: Additional facade configuration
            
        Returns:
            Tuple of (facade instance, estimated cost)
            
        Example:
            >>> factory = FacadeFactory(config_source="json", config_path="config")
            >>> facade, cost = factory.create_cheapest_facade("chat")
            >>> print(f"Using cheapest model at ${cost:.4f}")
        """
        cheapest_provider = None
        cheapest_model = None
        cheapest_cost = float('inf')
        
        for provider_name, provider in self._providers_cache.items():
            if not provider.enabled:
                continue
            
            # Get models with capability
            models = provider.get_models_for_capability(capability)
            
            for model in models:
                if not model.enabled:
                    continue
                
                cost = model.calculate_cost(input_tokens, output_tokens)
                if cost < cheapest_cost:
                    cheapest_cost = cost
                    cheapest_provider = provider_name
                    cheapest_model = model.name
        
        if not cheapest_provider:
            raise ValueError(f"No models found supporting capability '{capability}'")
        
        facade = self.create_facade(cheapest_provider, cheapest_model, **kwargs)
        return facade, cheapest_cost
    
    def get_model_info(self, provider_name: str, model_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a model.
        
        Args:
            provider_name: Name of the provider
            model_name: Name of the model
            
        Returns:
            Dictionary with model details
        """
        provider = self.get_provider(provider_name)
        model = provider.get_model_by_name(model_name)
        
        if not model:
            raise ValueError(f"Model '{model_name}' not found")
        
        return {
            'provider': provider_name,
            'name': model.name,
            'version': model.version,
            'description': model.description,
            'enabled': model.enabled,
            'context_window': model.context_window,
            'max_output': model.max_output,
            'capabilities': model.capabilities,
            'strengths': model.strengths,
            'pricing': {
                'input_per_1m': model.input_cost_per_million,
                'output_per_1m': model.output_cost_per_million
            }
        }


# Convenience functions for quick facade creation

def create_facade_from_json(
    config_dir: str,
    provider_name: str,
    model_name: str,
    **kwargs
) -> LLMFacade:
    """
    Quick facade creation from JSON configuration.
    
    Args:
        config_dir: Directory containing JSON configs
        provider_name: Provider name
        model_name: Model name
        **kwargs: Additional configuration
        
    Returns:
        Configured facade instance
    """
    factory = FacadeFactory(config_source="json", config_path=config_dir)
    return factory.create_facade(provider_name, model_name, **kwargs)


def create_facade_from_db(
    db_handler,
    provider_name: str,
    model_name: str,
    **kwargs
) -> LLMFacade:
    """
    Quick facade creation from database configuration.
    
    Args:
        db_handler: Database handler instance
        provider_name: Provider name
        model_name: Model name
        **kwargs: Additional configuration
        
    Returns:
        Configured facade instance
    """
    factory = FacadeFactory(config_source="db", db_connection_pool_name=db_handler)
    return factory.create_facade(provider_name, model_name, **kwargs)


__all__ = [
    'FacadeFactory',
    'create_facade_from_json',
    'create_facade_from_db'
]
