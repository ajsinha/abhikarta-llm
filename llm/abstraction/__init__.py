"""
Abhikarta LLM Abstraction System

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

from .core import (
    LLMProvider,
    LLMFacade,
    LLMClient,
    LLMProviderFactory,
    LLMClientFactory,
    Message,
    CompletionResponse,
    ChatResponse,
    ModelInfo,
    Interaction,
    InteractionHistory,
    LLMException,
    ProviderError,
    ModelError,
    ConfigurationError,
    APIError,
    ValidationError
)

__version__ = "1.0.0"

__all__ = [
    # Factories - Main entry points
    'LLMClientFactory',
    'LLMProviderFactory',
    
    # Core classes
    'LLMClient',
    'LLMProvider',
    'LLMFacade',
    
    # Data classes
    'Message',
    'CompletionResponse',
    'ChatResponse',
    'ModelInfo',
    'Interaction',
    'InteractionHistory',
    
    # Exceptions
    'LLMException',
    'ProviderError',
    'ModelError',
    'ConfigurationError',
    'APIError',
    'ValidationError',
]
