"""
Abstract LLM Provider Interface

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class LLMProvider(ABC):
    """
    Abstract base class for all LLM providers.
    
    Each provider implementation must inherit from this class and
    implement all abstract methods.
    """
    
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.api_key: str = None
        self.initialized: bool = False
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the provider with configuration.
        
        Args:
            config: Provider-specific configuration dictionary
            
        Raises:
            ProviderInitializationError: If initialization fails
            InvalidCredentialsError: If API credentials are invalid
        """
        pass
    
    @abstractmethod
    def create_facade(self, model_name: str) -> 'LLMFacade':
        """
        Create a facade instance for the specified model.
        
        Args:
            model_name: Name of the model to create facade for
            
        Returns:
            LLMFacade instance configured for the model
            
        Raises:
            ModelNotFoundError: If model is not available
        """
        pass
    
    @abstractmethod
    def list_available_models(self) -> List[str]:
        """
        List all available models for this provider.
        
        Returns:
            List of model names
        """
        pass
    
    @abstractmethod
    def validate_credentials(self) -> bool:
        """
        Validate API credentials.
        
        Returns:
            True if credentials are valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the provider name.
        
        Returns:
            Provider name (e.g., 'anthropic', 'openai')
        """
        pass
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary containing model information
        """
        models = self.config.get('models', [])
        for model in models:
            if model.get('name') == model_name:
                return model
        return {}
    
    def is_initialized(self) -> bool:
        """
        Check if provider is initialized.
        
        Returns:
            True if initialized, False otherwise
        """
        return self.initialized
