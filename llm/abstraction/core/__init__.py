"""
Core LLM Abstraction Components

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

from .provider import LLMProvider
from .facade import LLMFacade, Message, CompletionResponse, ChatResponse, ModelInfo
from .client import LLMClient
from .factories import LLMProviderFactory, LLMClientFactory
from .history import InteractionHistory, Interaction
from .exceptions import *

__all__ = [
    # Core classes
    'LLMProvider',
    'LLMFacade',
    'LLMClient',
    'LLMProviderFactory',
    'LLMClientFactory',
    
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
    'ProviderNotFoundError',
    'ProviderInitializationError',
    'InvalidCredentialsError',
    'ModelError',
    'ModelNotFoundError',
    'ConfigurationError',
    'InvalidConfigurationError',
    'MissingConfigurationError',
    'APIError',
    'RateLimitError',
    'TimeoutError',
    'ValidationError',
    'HistoryError',
]
