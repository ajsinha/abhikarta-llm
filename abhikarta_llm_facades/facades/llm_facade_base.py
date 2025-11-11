"""
Abhikarta LLM Facade Base - Common Implementation Base Class

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This module and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

This document is provided "as is" without warranty of any kind, either expressed or implied.
The copyright holder shall not be liable for any damages arising from the use of this
document or the software system it describes.

Patent Pending: Certain architectural patterns and implementations described in this
module may be subject to patent applications.

Description:
This module provides LLMFacadeBase, an abstract base class that extends LLMFacade with
common functionality implementations to reduce boilerplate code in provider-specific facades.
Provider facades should extend this class rather than implementing LLMFacade directly.
"""

import os
import json
import time
import logging
from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator, Callable, Tuple
from abc import abstractmethod
from datetime import datetime
import asyncio

from .llm_facade import (
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
    SafetyLevel,
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


class LLMFacadeBase(LLMFacade):
    """
    Base implementation class providing common functionality for all LLM provider facades.
    
    This class implements common patterns and utility methods that are shared across
    different LLM providers, reducing code duplication and ensuring consistent behavior.
    
    Provider-specific facades should:
    1. Extend this class
    2. Implement abstract methods marked with @abstractmethod
    3. Override other methods as needed for provider-specific behavior
    
    Common functionality provided:
    - Message formatting and validation
    - Configuration management
    - Token counting estimates
    - Error handling and retry logic
    - Logging and monitoring
    - Health checks
    - Resource cleanup
    
    Example:
        >>> class OpenAIFacade(LLMFacadeBase):
        ...     def __init__(self, model_name, api_key=None, **kwargs):
        ...         super().__init__("openai", model_name, api_key, **kwargs)
        ...         # OpenAI-specific initialization
        ...     
        ...     def chat_completion(self, messages, **kwargs):
        ...         # OpenAI-specific implementation
        ...         pass
    """
    
    def __init__(
        self,
        provider_name: str,
        model_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        **kwargs
    ):
        """
        Initialize the base facade.
        
        Args:
            provider_name: Name of the provider (e.g., "openai", "anthropic")
            model_name: Model identifier
            api_key: API authentication key
            base_url: Custom API endpoint
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            **kwargs: Additional configuration options
        """
        self.provider_name = provider_name
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout or 60.0
        self.max_retries = max_retries
        self.kwargs = kwargs
        
        # Initialize logging
        self.logger = logging.getLogger(f"{provider_name}.{model_name}")
        
        # Request tracking
        self._request_count = 0
        self._total_tokens = 0
        self._total_cost = 0.0
        self._start_time = time.time()
        
        # Model metadata cache
        self._model_info_cache = None
        self._capabilities_cache = None
        
        # Load provider configuration if available
        self._provider_config = self._load_provider_config()
    
    def _load_provider_config(self) -> Optional[Dict[str, Any]]:
        """Load provider configuration from JSON file."""
        try:
            config_path = os.path.join(
                os.path.dirname(__file__),
                f"{self.provider_name}.json"
            )
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load provider config: {e}")
        return None
    
    def _get_model_config(self) -> Optional[Dict[str, Any]]:
        """Get configuration for the current model from provider config."""
        if not self._provider_config:
            return None
        
        models = self._provider_config.get("models", [])
        for model in models:
            if model.get("name") == self.model_name:
                return model
        return None
    
    # ========================================================================
    # Default Implementations
    # ========================================================================
    
    def get_capabilities(self) -> List[ModelCapability]:
        """Get list of capabilities. Override if provider has specific detection."""
        if self._capabilities_cache:
            return self._capabilities_cache
        
        capabilities = []
        model_config = self._get_model_config()
        
        if model_config:
            caps = model_config.get("capabilities", {})
            
            if caps.get("chat"):
                capabilities.append(ModelCapability.CHAT_COMPLETION)
            if caps.get("completion"):
                capabilities.append(ModelCapability.TEXT_GENERATION)
            if caps.get("streaming"):
                capabilities.append(ModelCapability.STREAMING)
            if caps.get("function_calling"):
                capabilities.extend([
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.TOOL_USE
                ])
            if caps.get("vision"):
                capabilities.extend([
                    ModelCapability.VISION,
                    ModelCapability.IMAGE_UNDERSTANDING,
                    ModelCapability.MULTIMODAL
                ])
            if caps.get("embeddings"):
                capabilities.append(ModelCapability.EMBEDDINGS)
            if caps.get("code"):
                capabilities.append(ModelCapability.CODE_GENERATION)
        
        self._capabilities_cache = capabilities
        return capabilities
    
    def supports_capability(self, capability: ModelCapability) -> bool:
        """Check if model supports a specific capability."""
        return capability in self.get_capabilities()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get detailed model information."""
        if self._model_info_cache:
            return self._model_info_cache
        
        model_config = self._get_model_config()
        
        info = {
            "provider": self.provider_name,
            "name": self.model_name,
            "capabilities": [cap.value for cap in self.get_capabilities()],
        }
        
        if model_config:
            info.update({
                "version": model_config.get("version"),
                "description": model_config.get("description"),
                "context_window": model_config.get("context_window"),
                "max_output": model_config.get("max_output"),
                "strengths": model_config.get("strengths", []),
                "cost": model_config.get("cost", {})
            })
        
        self._model_info_cache = info
        return info
    
    def count_tokens(self, text: str, **kwargs) -> int:
        """
        Estimate token count. Override for provider-specific tokenization.
        Default uses rough approximation: ~4 characters per token.
        """
        # Basic approximation
        return len(text) // 4
    
    def count_message_tokens(self, messages: Messages, **kwargs) -> int:
        """Count tokens in message list."""
        total = 0
        for message in messages:
            content = message.get("content", "")
            if isinstance(content, str):
                total += self.count_tokens(content)
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        text = item.get("text", "")
                        total += self.count_tokens(text)
            # Add overhead for role and formatting
            total += 4
        return total
    
    def format_messages(self, messages: Messages, **kwargs) -> str:
        """Convert messages to single prompt string."""
        formatted = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if isinstance(content, list):
                # Extract text from multimodal content
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                content = "\n".join(text_parts)
            
            if role == "system":
                formatted.append(f"System: {content}")
            elif role == "user":
                formatted.append(f"Human: {content}")
            elif role == "assistant":
                formatted.append(f"Assistant: {content}")
        
        return "\n\n".join(formatted)
    
    def parse_tool_calls(self, response: Dict[str, Any], **kwargs) -> List[ToolCall]:
        """Extract tool calls from response. Override for provider-specific format."""
        return []
    
    def validate_config(
        self,
        config: Dict[str, Any],
        **kwargs
    ) -> Tuple[bool, List[str]]:
        """Validate configuration parameters."""
        errors = []
        
        # Check required fields
        if not config.get("model_name"):
            errors.append("model_name is required")
        
        # Validate temperature
        temp = config.get("temperature")
        if temp is not None:
            if not isinstance(temp, (int, float)):
                errors.append("temperature must be a number")
            elif temp < 0 or temp > 2:
                errors.append("temperature must be between 0 and 2")
        
        # Validate max_tokens
        max_tokens = config.get("max_tokens")
        if max_tokens is not None:
            if not isinstance(max_tokens, int):
                errors.append("max_tokens must be an integer")
            elif max_tokens < 1:
                errors.append("max_tokens must be positive")
        
        # Validate top_p
        top_p = config.get("top_p")
        if top_p is not None:
            if not isinstance(top_p, (int, float)):
                errors.append("top_p must be a number")
            elif top_p < 0 or top_p > 1:
                errors.append("top_p must be between 0 and 1")
        
        return (len(errors) == 0, errors)
    
    def log_request(
        self,
        method: str,
        input_data: Any,
        response: Optional[Any] = None,
        latency_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        """Log request for monitoring."""
        self._request_count += 1
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "provider": self.provider_name,
            "model": self.model_name,
            "method": method,
            "request_id": self._request_count,
            "latency_ms": latency_ms,
            "metadata": metadata or {}
        }
        
        # Extract token usage if available
        if response and isinstance(response, dict):
            usage = response.get("usage")
            if usage:
                self._total_tokens += usage.get("total_tokens", 0)
                log_entry["tokens"] = usage
        
        self.logger.info(f"Request logged: {json.dumps(log_entry)}")
    
    def get_usage_stats(
        self,
        period: str = "day",
        **kwargs
    ) -> Dict[str, Any]:
        """Get usage statistics."""
        uptime = time.time() - self._start_time
        
        return {
            "provider": self.provider_name,
            "model": self.model_name,
            "period": period,
            "total_requests": self._request_count,
            "total_tokens": self._total_tokens,
            "total_cost": self._total_cost,
            "uptime_seconds": uptime,
            "average_tokens_per_request": (
                self._total_tokens / self._request_count
                if self._request_count > 0 else 0
            )
        }
    
    def health_check(self, **kwargs) -> bool:
        """Basic health check. Override for provider-specific checks."""
        try:
            # Check if we have required credentials
            if not self.api_key and self.provider_name != "mock":
                return False
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    def close(self) -> None:
        """Cleanup resources."""
        self.logger.info(f"Closing {self.provider_name} facade for {self.model_name}")
        # Provider-specific cleanup should override this
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _check_capability(self, capability: ModelCapability) -> None:
        """Raise exception if capability not supported."""
        if not self.supports_capability(capability):
            raise CapabilityNotSupportedException(
                capability.value,
                self.model_name
            )
    
    def _handle_error(self, error: Exception) -> None:
        """Convert provider-specific errors to facade exceptions."""
        error_msg = str(error).lower()
        
        if "rate limit" in error_msg or "429" in error_msg:
            raise RateLimitException(str(error))
        elif "content filter" in error_msg or "safety" in error_msg:
            raise ContentFilterException(str(error))
        elif "context length" in error_msg or "too long" in error_msg:
            raise ContextLengthExceededException(0, 0)
        elif "auth" in error_msg or "401" in error_msg or "403" in error_msg:
            raise AuthenticationException(str(error))
        elif "network" in error_msg or "timeout" in error_msg:
            raise NetworkException(str(error))
        else:
            raise LLMFacadeException(str(error))
    
    def _merge_configs(
        self,
        default: Dict[str, Any],
        override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge configuration dictionaries."""
        merged = default.copy()
        merged.update({k: v for k, v in override.items() if v is not None})
        return merged
    
    # ========================================================================
    # Abstract Methods (Must be implemented by provider facades)
    # ========================================================================
    
    @abstractmethod
    def chat_completion(
        self,
        messages: Messages,
        tools: Optional[List[ToolDefinition]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Must be implemented by provider facade."""
        pass
    
    @abstractmethod
    def completion(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> str:
        """Must be implemented by provider facade."""
        pass
    
    # =========================================================================
    # Default stub implementations for optional methods
    # =========================================================================
    
    def text_generation(self, prompt: str, **kwargs) -> str:
        """Default text generation (uses completion)."""
        return self.completion(prompt, **kwargs)
    
    def stream_text_generation(self, prompt: str, **kwargs) -> Iterator[str]:
        """Default streaming text generation."""
        yield self.text_generation(prompt, **kwargs)
    
    def chat_completion_with_vision(self, messages: Messages, images: List[Any], **kwargs) -> Dict[str, Any]:
        """Vision chat not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support vision capabilities"
        )
    
    def achat_completion(self, messages: Messages, **kwargs):
        """Async chat not implemented by default."""
        raise NotImplementedError("Async operations not implemented for this provider")
    
    def achat_completion_with_vision(self, messages: Messages, images: List[Any], **kwargs):
        """Async vision chat not implemented by default."""
        raise NotImplementedError("Async vision operations not implemented")
    
    def atext_generation(self, prompt: str, **kwargs):
        """Async text generation not implemented by default."""
        raise NotImplementedError("Async operations not implemented for this provider")
    
    def image_generation(self, prompt: str, **kwargs) -> Any:
        """Image generation not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support image generation"
        )
    
    def image_editing(self, image: Any, prompt: str, **kwargs) -> Any:
        """Image editing not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support image editing"
        )
    
    def image_variation(self, image: Any, **kwargs) -> Any:
        """Image variation not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support image variations"
        )
    
    def image_captioning(self, image: Any, **kwargs) -> str:
        """Image captioning not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support image captioning"
        )
    
    def audio_transcription(self, audio: Any, **kwargs) -> str:
        """Audio transcription not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support audio transcription"
        )
    
    def audio_translation(self, audio: Any, **kwargs) -> str:
        """Audio translation not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support audio translation"
        )
    
    def embed_text(self, text: str, **kwargs) -> List[float]:
        """Text embedding not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support embeddings"
        )
    
    def embed_image(self, image: Any, **kwargs) -> List[float]:
        """Image embedding not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support image embeddings"
        )
    
    def batch_embed(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Batch embedding not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support batch embeddings"
        )
    
    def compute_similarity(self, text1: str, text2: str, **kwargs) -> float:
        """Similarity computation not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support similarity computation"
        )
    
    def classify_text(self, text: str, labels: List[str], **kwargs) -> Dict[str, float]:
        """Text classification not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support classification"
        )
    
    def extract_structured_data(self, text: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Structured extraction not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support structured extraction"
        )
    
    def generate_with_schema(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Schema-based generation not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support schema-based generation"
        )
    
    def moderate_content(self, text: str, **kwargs) -> Dict[str, Any]:
        """Content moderation not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support content moderation"
        )
    
    def code_generation(self, description: str, **kwargs) -> str:
        """Code generation (uses chat_completion)."""
        messages = [{"role": "user", "content": f"Generate code for: {description}"}]
        response = self.chat_completion(messages, **kwargs)
        return response["content"]
    
    def code_completion(self, code: str, **kwargs) -> str:
        """Code completion not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support code completion"
        )
    
    def code_explanation(self, code: str, **kwargs) -> str:
        """Code explanation (uses chat_completion)."""
        messages = [{"role": "user", "content": f"Explain this code:\n\n{code}"}]
        response = self.chat_completion(messages, **kwargs)
        return response["content"]
    
    def code_review(self, code: str, **kwargs) -> str:
        """Code review (uses chat_completion)."""
        messages = [{"role": "user", "content": f"Review this code:\n\n{code}"}]
        response = self.chat_completion(messages, **kwargs)
        return response["content"]
    
    def create_tool_definition(self, name: str, description: str, parameters: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Create tool definition."""
        return {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        }
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any], **kwargs) -> Any:
        """Tool calling not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support tool calling"
        )
    
    def execute_tool_loop(self, messages: Messages, tools: List[Any], **kwargs) -> Dict[str, Any]:
        """Tool loop not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support tool loops"
        )
    
    def retrieve_documents(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Document retrieval not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support document retrieval"
        )
    
    def rag_generate(self, query: str, documents: List[Dict[str, Any]], **kwargs) -> str:
        """RAG generation not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support RAG"
        )
    
    def rag_chat(self, messages: Messages, documents: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """RAG chat not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support RAG chat"
        )
    
    def batch_generate(self, prompts: List[str], **kwargs) -> List[str]:
        """Batch generation not supported by default."""
        return [self.completion(prompt, **kwargs) for prompt in prompts]
    
    def create_conversation(self, **kwargs) -> str:
        """Conversation management not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support conversation management"
        )
    
    def continue_conversation(self, conversation_id: str, message: str, **kwargs) -> Dict[str, Any]:
        """Continue conversation not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support conversation management"
        )
    
    def get_conversation_history(self, conversation_id: str, **kwargs) -> List[Dict[str, Any]]:
        """Get conversation history not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support conversation management"
        )
    
    def clear_conversation(self, conversation_id: str, **kwargs) -> None:
        """Clear conversation not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support conversation management"
        )
    
    def create_fine_tuning_job(self, training_data: List[Dict[str, Any]], **kwargs) -> str:
        """Fine-tuning not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support fine-tuning"
        )
    
    def get_fine_tuning_status(self, job_id: str, **kwargs) -> Dict[str, Any]:
        """Fine-tuning status not supported by default."""
        raise CapabilityNotSupportedException(
            f"{self.provider_name} does not support fine-tuning"
        )
    
    def truncate_to_max_tokens(self, text: str, max_tokens: int, **kwargs) -> str:
        """Truncate text to max tokens."""
        tokens = text.split()
        if len(tokens) <= max_tokens:
            return text
        return " ".join(tokens[:max_tokens])
    
    def get_context_window(self, **kwargs) -> int:
        """Get context window size."""
        return 4096  # Default
    
    def get_max_output_tokens(self, **kwargs) -> int:
        """Get max output tokens."""
        return 2048  # Default
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, **kwargs) -> float:
        """Estimate cost (not implemented by default)."""
        return 0.0


__all__ = ['LLMFacadeBase']
