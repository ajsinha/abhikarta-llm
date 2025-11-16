"""
Abhikarta Base Provider Facade - Dynamic Configuration Loading

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
This module provides a base implementation of LLMFacade that dynamically loads all
configuration from ModelProvider instances (either JSON or Database backed).
No configuration is hardcoded - all data comes from the model registry.
"""

import os
import json
import time
import asyncio
from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator, Callable, Tuple
from abc import abstractmethod

from llm_facade import (
    LLMFacade,
    ModelCapability,
    GenerationConfig,
    TokenUsage,
    CompletionMetadata,
    Messages,
    TextStream,
    DeltaStream,
    ToolDefinition,
    ToolCall,
    ToolResult,
    Document,
    RetrievalResult,
    Embedding,
    ImageInput,
    ImageOutput,
    ModerationResult,
    SafetyResult,
    ResponseFormat,
    LLMFacadeException,
    CapabilityNotSupportedException,
    RateLimitException,
    ContentFilterException,
    ContextLengthExceededException,
    ToolNotFoundException,
    ToolExecutionException,
    InvalidResponseException,
    AuthenticationException,
    NetworkException
)

from model_management.model_provider import ModelProvider, Model


class BaseProviderFacade(LLMFacade):
    """
    Base facade implementation that dynamically loads configuration from ModelProvider.
    
    This class provides a foundation for provider-specific facades, eliminating
    hardcoded configuration and instead reading all model details from the
    ModelProvider instance (which can be backed by JSON or Database).
    
    Key Features:
    - Zero hardcoded configuration
    - Automatic capability detection from model metadata
    - Dynamic cost calculation from model pricing
    - Supports both JSON and Database backends
    - Thread-safe model info caching
    
    Subclasses must implement:
    - _initialize_client(): Setup provider-specific SDK client
    - chat_completion(): Main chat interface
    - Other provider-specific methods as needed
    """
    
    def __init__(
        self,
        provider: ModelProvider,
        model_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        **kwargs
    ) -> None:
        """
        Initialize facade with ModelProvider configuration.
        
        Args:
            provider: ModelProvider instance (JSON or DB backed)
            model_name: Name of the model to use
            api_key: API key for authentication
            base_url: Override base URL (uses provider default if None)
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts
            **kwargs: Provider-specific configuration
        """
        self.provider_config = provider
        self.provider_name = provider.provider
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url or provider.base_url
        self.timeout = timeout or 600.0
        self.max_retries = max_retries
        self.kwargs = kwargs
        
        # Get model from provider
        self.model = self._get_model_from_provider(model_name)
        if not self.model:
            raise ValueError(
                f"Model '{model_name}' not found in provider '{self.provider_name}'"
            )
        
        # Cache frequently accessed model info
        self._capabilities_cache = None
        self._model_info_cache = None
        
    def _get_model_from_provider(self, model_name: str) -> Optional[Model]:
        """Get model instance from provider."""
        models = self.provider_config.get_model_by_name(model_name)
        return models if models else None
    
    def get_capabilities(self) -> List[ModelCapability]:
        """
        Get capabilities from model metadata.
        
        Dynamically builds capability list from model's capabilities dict.
        """
        if self._capabilities_cache is not None:
            return self._capabilities_cache
        
        capabilities = []
        model_caps = self.model.capabilities
        
        # Always include these if model is enabled
        capabilities.append(ModelCapability.TEXT_GENERATION)
        
        # Map model capabilities to ModelCapability enum
        capability_mapping = {
            'chat': ModelCapability.CHAT_COMPLETION,
            'streaming': ModelCapability.STREAMING,
            'function_calling': ModelCapability.FUNCTION_CALLING,
            'tool_use': ModelCapability.TOOL_USE,
            'vision': ModelCapability.VISION,
            'image_understanding': ModelCapability.IMAGE_UNDERSTANDING,
            'multimodal': ModelCapability.MULTIMODAL,
            'code': ModelCapability.CODE_GENERATION,
            'reasoning': ModelCapability.REASONING,
            'embeddings': ModelCapability.EMBEDDINGS,
            'json_mode': ModelCapability.JSON_MODE,
            'structured_output': ModelCapability.STRUCTURED_OUTPUT
        }
        
        for cap_key, cap_enum in capability_mapping.items():
            if model_caps.get(cap_key, False):
                capabilities.append(cap_enum)
        
        self._capabilities_cache = capabilities
        return capabilities
    
    def supports_capability(self, capability: ModelCapability) -> bool:
        """Check if model supports a specific capability."""
        return capability in self.get_capabilities()
    
    def get_model_info(self, **kwargs) -> Dict[str, Any]:
        """
        Get comprehensive model information from provider metadata.
        
        Returns all model details including capabilities, pricing, limits, etc.
        """
        if self._model_info_cache is not None:
            return self._model_info_cache
        
        # Build comprehensive model info from Model instance
        info = {
            'provider': self.provider_name,
            'name': self.model.name,
            'version': self.model.version,
            'description': self.model.description,
            'context_window': self.model.context_window,
            'max_output': self.model.max_output,
            'enabled': self.model.enabled,
            'capabilities': self.model.capabilities,
            'strengths': self.model.strengths,
            'pricing': {
                'input_per_1m_tokens': self.model.input_cost_per_million,
                'output_per_1m_tokens': self.model.output_cost_per_million
            },
            'api_version': self.provider_config.api_version,
            'base_url': self.base_url,
            'provider_notes': self.provider_config.notes
        }
        
        # Add cost calculation if available
        if hasattr(self.model, 'cache_write_cost_per_million'):
            info['pricing']['cache_write_per_1m_tokens'] = self.model.cache_write_cost_per_million
            info['pricing']['cache_read_per_1m_tokens'] = self.model.cache_read_cost_per_million
        
        self._model_info_cache = info
        return info
    
    def get_cost_per_token(self) -> Tuple[float, float]:
        """
        Get cost per token for input and output.
        
        Returns:
            Tuple of (input_cost_per_token, output_cost_per_token)
        """
        input_cost = self.model.input_cost_per_million / 1_000_000
        output_cost = self.model.output_cost_per_million / 1_000_000
        return input_cost, output_cost
    
    def estimate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        cached_tokens: int = 0,
        **kwargs
    ) -> float:
        """
        Estimate cost for a request using model's pricing.
        
        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            cached_tokens: Number of cached tokens (if applicable)
            
        Returns:
            Estimated cost in USD
        """
        return self.model.calculate_cost(prompt_tokens, completion_tokens)
    
    def get_context_window_size(self) -> int:
        """Get maximum context window size."""
        return self.model.context_window
    
    def get_max_output_tokens(self) -> int:
        """Get maximum output tokens."""
        return self.model.max_output
    
    @abstractmethod
    def _initialize_client(self):
        """
        Initialize provider-specific client.
        
        Must be implemented by provider-specific facades.
        """
        pass
    
    def validate_config(
        self,
        config: Dict[str, Any],
        **kwargs
    ) -> Tuple[bool, List[str]]:
        """
        Validate configuration against model limits.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check max_tokens
        if 'max_tokens' in config:
            max_tokens = config['max_tokens']
            if max_tokens > self.model.max_output:
                errors.append(
                    f"max_tokens {max_tokens} exceeds model limit {self.model.max_output}"
                )
        
        # Check temperature
        if 'temperature' in config:
            temp = config['temperature']
            if not 0 <= temp <= 2:
                errors.append(f"temperature {temp} should be between 0 and 2")
        
        # Check top_p
        if 'top_p' in config:
            top_p = config['top_p']
            if not 0 <= top_p <= 1:
                errors.append(f"top_p {top_p} should be between 0 and 1")
        
        return len(errors) == 0, errors
    
    def format_messages(
        self,
        messages: Messages,
        **kwargs
    ) -> str:
        """
        Convert structured messages to prompt string.
        
        Default implementation - can be overridden by provider facades.
        """
        parts = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            parts.append(f"{role.upper()}: {content}")
        return "\n\n".join(parts)
    
    def parse_tool_calls(
        self,
        response: Dict[str, Any],
        **kwargs
    ) -> List[ToolCall]:
        """
        Extract tool calls from response.
        
        Default implementation - should be overridden by provider facades.
        """
        # Base implementation returns empty list
        # Provider-specific facades should implement actual parsing
        return []
    
    def health_check(self, **kwargs) -> bool:
        """
        Check if provider is healthy.
        
        Default implementation - can be enhanced by provider facades.
        """
        return self.provider_config.enabled and self.model.enabled
    
    def close(self) -> None:
        """Cleanup resources."""
        # Base cleanup - subclasses should extend this
        if hasattr(self, 'client'):
            if hasattr(self.client, 'close'):
                self.client.close()
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"{self.__class__.__name__}("
            f"provider='{self.provider_name}', "
            f"model='{self.model_name}')"
        )


__all__ = ['BaseProviderFacade']
