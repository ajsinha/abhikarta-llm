"""
Abhikarta LLM Facades - Unified Interface for Language Models

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This module and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Patent Pending: Certain architectural patterns and implementations described in this
module may be subject to patent applications.
"""

from .llm_facade import (
    LLMFacade,
    ModelCapability,
    GenerationConfig,
    TokenUsage,
    CompletionMetadata,
    ResponseFormat,
    SafetyLevel,
    LLMFacadeException,
    CapabilityNotSupportedException,
    RateLimitException,
    ContentFilterException,
    ContextLengthExceededException,
    AuthenticationException,
    NetworkException
)

from .llm_facade_base import LLMFacadeBase

# Provider facades
from .openai_facade import OpenAIFacade
from .anthropic_facade import AnthropicFacade
from .google_facade import GoogleFacade
from .cohere_facade import CohereFacade
from .mistral_facade import MistralFacade
from .groq_facade import GroqFacade
from .together_facade import TogetherFacade
from .replicate_facade import ReplicateFacade
from .ollama_facade import OllamaFacade
from .awsbedrock_facade import AWSBedrockFacade
from .huggingface_facade import HuggingfaceFacade
from .meta_facade import MetaFacade
from .mock_facade import MockFacade

__version__ = "1.0.0"
__author__ = "Ashutosh Sinha"
__email__ = "ajsinha@gmail.com"

__all__ = [
    # Base classes
    'LLMFacade',
    'LLMFacadeBase',
    
    # Provider facades
    'OpenAIFacade',
    'AnthropicFacade',
    'GoogleFacade',
    'CohereFacade',
    'MistralFacade',
    'GroqFacade',
    'TogetherFacade',
    'ReplicateFacade',
    'OllamaFacade',
    'AWSBedrockFacade',
    'HuggingfaceFacade',
    'MetaFacade',
    'MockFacade',
    
    # Enums
    'ModelCapability',
    'ResponseFormat',
    'SafetyLevel',
    
    # Data classes
    'GenerationConfig',
    'TokenUsage',
    'CompletionMetadata',
    
    # Exceptions
    'LLMFacadeException',
    'CapabilityNotSupportedException',
    'RateLimitException',
    'ContentFilterException',
    'ContextLengthExceededException',
    'AuthenticationException',
    'NetworkException',
]
