"""
Factory Classes for LLM Abstraction System

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import importlib
import json
import os
from typing import Dict, Any, Optional
from .provider import LLMProvider
from .client import LLMClient
from .exceptions import (
    ProviderNotFoundError,
    ProviderInitializationError,
    InvalidConfigurationError,
    MissingConfigurationError
)


class LLMProviderFactory:
    """
    Singleton factory for creating and managing LLM providers.
    
    Loads provider configurations and instantiates providers dynamically.
    """
    
    _instance = None
    _providers: Dict[str, LLMProvider] = {}
    _config: Dict[str, Any] = {}
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMProviderFactory, cls).__new__(cls)
        return cls._instance
    
    def initialize(self, config_path: str = "config/llm_config.json") -> None:
        """
        Initialize factory with configuration.
        
        Args:
            config_path: Path to main configuration file
            
        Raises:
            InvalidConfigurationError: If configuration is invalid
        """
        if self._initialized:
            return
        
        # Load main configuration
        if not os.path.exists(config_path):
            raise MissingConfigurationError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = json.load(f)
        
        self._initialized = True
    
    def get_provider(self, provider_name: str) -> LLMProvider:
        """
        Get or create a provider instance.
        
        Args:
            provider_name: Name of the provider (e.g., 'anthropic', 'openai')
            
        Returns:
            LLMProvider instance
            
        Raises:
            ProviderNotFoundError: If provider not found in configuration
            ProviderInitializationError: If provider initialization fails
        """
        if not self._initialized:
            raise InvalidConfigurationError("Factory not initialized. Call initialize() first.")
        
        # Return cached instance if available
        if provider_name in self._providers:
            return self._providers[provider_name]
        
        # Get provider configuration
        provider_config = self._config.get('providers', {}).get(provider_name)
        if not provider_config:
            raise ProviderNotFoundError(f"Provider '{provider_name}' not found in configuration")
        
        if not provider_config.get('enabled', True):
            raise ProviderNotFoundError(f"Provider '{provider_name}' is disabled")
        
        # Load provider module and class
        try:
            module_path = provider_config['module']
            class_name = provider_config['class']
            
            module = importlib.import_module(module_path + '.provider')
            provider_class = getattr(module, class_name)
            
            # Instantiate provider
            provider = provider_class()
            
            # Load provider-specific configuration
            config_file = provider_config.get('config_file')
            if config_file and os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    specific_config = json.load(f)
            else:
                specific_config = {}
            
            # Initialize provider
            provider.initialize(specific_config)
            
            # Cache the instance
            self._providers[provider_name] = provider
            
            return provider
            
        except Exception as e:
            raise ProviderInitializationError(
                f"Failed to initialize provider '{provider_name}': {str(e)}"
            )
    
    def list_available_providers(self) -> list[str]:
        """
        List all available providers from configuration.
        
        Returns:
            List of provider names
        """
        if not self._initialized:
            return []
        
        providers = self._config.get('providers', {})
        return [
            name for name, config in providers.items()
            if config.get('enabled', True)
        ]
    
    def get_default_provider_name(self) -> str:
        """
        Get the default provider name from configuration.
        
        Returns:
            Default provider name
        """
        return self._config.get('default_provider', 'mock')
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the full configuration.
        
        Returns:
            Configuration dictionary
        """
        return self._config.copy()
    
    def clear_cache(self) -> None:
        """Clear the provider cache"""
        self._providers.clear()


class LLMClientFactory:
    """
    Singleton factory for creating LLM clients.
    
    Creates clients with configured providers and models.
    """
    
    _instance = None
    _provider_factory: Optional[LLMProviderFactory] = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMClientFactory, cls).__new__(cls)
        return cls._instance
    
    def initialize(self, config_path: str = "config/llm_config.json") -> None:
        """
        Initialize factory with configuration.
        
        Args:
            config_path: Path to main configuration file
        """
        # Initialize provider factory
        self._provider_factory = LLMProviderFactory()
        self._provider_factory.initialize(config_path)
        self._config = self._provider_factory.get_config()
    
    def create_client(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        history_size: Optional[int] = None
    ) -> LLMClient:
        """
        Create an LLM client with specified provider and model.
        
        Args:
            provider: Provider name (uses default if None)
            model: Model name (uses default if None)
            history_size: History size (uses default if None)
            
        Returns:
            Configured LLMClient instance
            
        Raises:
            ProviderNotFoundError: If provider not found
            ModelNotFoundError: If model not found
        """
        if self._provider_factory is None:
            raise InvalidConfigurationError("Factory not initialized. Call initialize() first.")
        
        # Use defaults if not specified
        if provider is None:
            provider = self._config.get('default_provider', 'mock')
        
        if model is None:
            model = self._config.get('default_model', 'default-model')
        
        if history_size is None:
            history_size = self._config.get('global_settings', {}).get('history_size', 50)
        
        # Get provider instance
        provider_instance = self._provider_factory.get_provider(provider)
        
        # Create facade for the model
        facade = provider_instance.create_facade(model)
        
        # Create and return client
        return LLMClient(
            facade=facade,
            provider_name=provider,
            model_name=model,
            history_size=history_size
        )
    
    def create_default_client(self) -> LLMClient:
        """
        Create a client with default provider and model.
        
        Returns:
            LLMClient with default configuration
        """
        return self.create_client()
    
    def create_mock_client(self, model: str = "mock-model") -> LLMClient:
        """
        Create a mock client for testing.
        
        Args:
            model: Model name for mock provider
            
        Returns:
            LLMClient with mock provider
        """
        return self.create_client(provider='mock', model=model)
    
    def list_available_models(self, provider: str) -> list[str]:
        """
        List available models for a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            List of model names
        """
        if self._provider_factory is None:
            return []
        
        provider_instance = self._provider_factory.get_provider(provider)
        return provider_instance.list_available_models()
