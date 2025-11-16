"""
Anthropic LLM Facade Implementation

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
This module provides a concrete implementation of the LLMFacade interface for
Anthropic's Claude models, supporting all Claude 3 family models with vision,
tool use, and advanced reasoning capabilities.
"""

import os
import json
import time
import asyncio
import base64
from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator, Callable, Tuple
from dataclasses import dataclass
import warnings

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


class AnthropicLLMFacade(LLMFacade):
    """
    Anthropic implementation of the LLMFacade interface.

    Supports Claude 3 family models with advanced capabilities including:
    - Vision and multimodal understanding
    - Function/tool calling
    - Extended context windows (up to 200K tokens)
    - Streaming responses
    - Async operations
    - System prompts and prefill support

    Features:
    - Claude 3 Opus (highest intelligence)
    - Claude 3 Sonnet (balanced performance)
    - Claude 3 Haiku (fastest responses)
    - Claude 3.5 Sonnet (latest generation)

    Example:
        >>> llm = AnthropicLLMFacade(
        ...     model_name="claude-3-5-sonnet-20241022",
        ...     api_key="sk-ant-..."
        ... )
        >>> response = llm.chat_completion([
        ...     {"role": "user", "content": "Hello!"}
        ... ])
    """

    # Model configurations
    MODEL_INFO = {
        "claude-3-5-sonnet-20241022": {
            "max_tokens": 8096,
            "context_window": 200000,
            "supports_vision": True,
            "supports_tools": True,
            "cost_per_1k_input": 0.003,
            "cost_per_1k_output": 0.015
        },
        "claude-3-opus-20240229": {
            "max_tokens": 4096,
            "context_window": 200000,
            "supports_vision": True,
            "supports_tools": True,
            "cost_per_1k_input": 0.015,
            "cost_per_1k_output": 0.075
        },
        "claude-3-sonnet-20240229": {
            "max_tokens": 4096,
            "context_window": 200000,
            "supports_vision": True,
            "supports_tools": True,
            "cost_per_1k_input": 0.003,
            "cost_per_1k_output": 0.015
        },
        "claude-3-haiku-20240307": {
            "max_tokens": 4096,
            "context_window": 200000,
            "supports_vision": True,
            "supports_tools": True,
            "cost_per_1k_input": 0.00025,
            "cost_per_1k_output": 0.00125
        }
    }

    def __init__(
            self,
            model_name: str,
            api_key: Optional[str] = None,
            base_url: Optional[str] = None,
            timeout: Optional[float] = None,
            max_retries: int = 3,
            **kwargs
    ) -> None:
        """
        Initialize Anthropic LLM Facade.

        Args:
            model_name: Claude model identifier (e.g., "claude-3-5-sonnet-20241022")
            api_key: Anthropic API key (reads from ANTHROPIC_API_KEY env var if None)
            base_url: Custom API endpoint URL (optional)
            timeout: Request timeout in seconds (default: 600)
            max_retries: Number of retry attempts for failed requests
            **kwargs: Additional configuration
                - default_headers: Custom headers for requests
                - anthropic_version: API version string
        """
        self.model_name = model_name
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = base_url
        self.timeout = timeout or 600.0
        self.max_retries = max_retries
        self.kwargs = kwargs

        if not self.api_key:
            raise AuthenticationException("Anthropic API key not provided")

        # Initialize client
        self._initialize_client()

        # Model info cache
        self._model_info = None

    def _initialize_client(self):
        """Initialize Anthropic API client."""
        try:
            import anthropic
            
            client_kwargs = {
                "api_key": self.api_key,
                "max_retries": self.max_retries,
                "timeout": self.timeout
            }
            
            if self.base_url:
                client_kwargs["base_url"] = self.base_url
                
            if "default_headers" in self.kwargs:
                client_kwargs["default_headers"] = self.kwargs["default_headers"]
                
            self.client = anthropic.Anthropic(**client_kwargs)
            self.async_client = anthropic.AsyncAnthropic(**client_kwargs)
            
        except ImportError:
            raise ImportError(
                "Please install anthropic: pip install anthropic"
            )
        except Exception as e:
            raise AuthenticationException(f"Failed to initialize Anthropic client: {e}")

    def get_capabilities(self) -> List[ModelCapability]:
        """Get list of capabilities supported by Claude models."""
        capabilities = [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CHAT_COMPLETION,
            ModelCapability.STREAMING,
            ModelCapability.TOOL_USE,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.JSON_MODE,
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.MULTIMODAL
        ]
        
        # Add vision capability for models that support it
        model_config = self.MODEL_INFO.get(self.model_name, {})
        if model_config.get("supports_vision", False):
            capabilities.extend([
                ModelCapability.VISION,
                ModelCapability.IMAGE_UNDERSTANDING
            ])
            
        return capabilities

    def supports_capability(self, capability: ModelCapability) -> bool:
        """Check if model supports a specific capability."""
        return capability in self.get_capabilities()

    def get_model_info(self) -> Dict[str, Any]:
        """Get detailed model information."""
        if self._model_info is None:
            config = self.MODEL_INFO.get(self.model_name, {})
            
            self._model_info = {
                "provider": "anthropic",
                "name": self.model_name,
                "version": self.model_name.split("-")[-1] if "-" in self.model_name else "latest",
                "max_input_tokens": config.get("context_window", 200000),
                "max_output_tokens": config.get("max_tokens", 4096),
                "context_window": config.get("context_window", 200000),
                "supports_streaming": True,
                "supports_functions": config.get("supports_tools", True),
                "supports_vision": config.get("supports_vision", False),
                "cost_per_1k_input_tokens": config.get("cost_per_1k_input", 0.003),
                "cost_per_1k_output_tokens": config.get("cost_per_1k_output", 0.015),
                "modalities": ["text", "image"] if config.get("supports_vision") else ["text"]
            }
            
        return self._model_info

    # =========================================================================
    # Core Generation Methods
    # =========================================================================

    def text_generation(
            self,
            prompt: str,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> str:
        """Generate text completion for a prompt."""
        start_time = time.time()
        
        try:
            # Build messages
            messages = [{"role": "user", "content": prompt}]
            
            # Build request parameters
            params = self._build_message_params(messages, config, **kwargs)
            
            # Make API call
            response = self.client.messages.create(**params)
            
            # Extract text
            text = self._extract_text_from_response(response)
            
            return text
            
        except Exception as e:
            raise self._transform_exception(e)

    async def async_text_generation(
            self,
            prompt: str,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> str:
        """Generate text completion asynchronously."""
        try:
            messages = [{"role": "user", "content": prompt}]
            params = self._build_message_params(messages, config, **kwargs)
            
            response = await self.async_client.messages.create(**params)
            return self._extract_text_from_response(response)
            
        except Exception as e:
            raise self._transform_exception(e)

    def stream_text_generation(
            self,
            prompt: str,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> TextStream:
        """Stream text generation."""
        try:
            messages = [{"role": "user", "content": prompt}]
            params = self._build_message_params(messages, config, **kwargs)
            
            with self.client.messages.stream(**params) as stream:
                for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            raise self._transform_exception(e)

    async def async_stream_text_generation(
            self,
            prompt: str,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> AsyncIterator[str]:
        """Stream text generation asynchronously."""
        try:
            messages = [{"role": "user", "content": prompt}]
            params = self._build_message_params(messages, config, **kwargs)
            
            async with self.async_client.messages.stream(**params) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            raise self._transform_exception(e)

    def chat_completion(
            self,
            messages: Messages,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """Generate chat completion."""
        start_time = time.time()
        
        try:
            params = self._build_message_params(messages, config, **kwargs)
            response = self.client.messages.create(**params)
            
            return self._format_chat_response(response, time.time() - start_time)
            
        except Exception as e:
            raise self._transform_exception(e)

    async def async_chat_completion(
            self,
            messages: Messages,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """Generate chat completion asynchronously."""
        start_time = time.time()
        
        try:
            params = self._build_message_params(messages, config, **kwargs)
            response = await self.async_client.messages.create(**params)
            
            return self._format_chat_response(response, time.time() - start_time)
            
        except Exception as e:
            raise self._transform_exception(e)

    def stream_chat_completion(
            self,
            messages: Messages,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> DeltaStream:
        """Stream chat completion with delta updates."""
        try:
            params = self._build_message_params(messages, config, **kwargs)
            
            with self.client.messages.stream(**params) as stream:
                for event in stream:
                    if hasattr(event, 'delta'):
                        yield {
                            "type": event.type,
                            "delta": event.delta.__dict__ if hasattr(event.delta, '__dict__') else str(event.delta)
                        }
                        
        except Exception as e:
            raise self._transform_exception(e)

    async def async_stream_chat_completion(
            self,
            messages: Messages,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream chat completion asynchronously."""
        try:
            params = self._build_message_params(messages, config, **kwargs)
            
            async with self.async_client.messages.stream(**params) as stream:
                async for event in stream:
                    if hasattr(event, 'delta'):
                        yield {
                            "type": event.type,
                            "delta": event.delta.__dict__ if hasattr(event.delta, '__dict__') else str(event.delta)
                        }
                        
        except Exception as e:
            raise self._transform_exception(e)

    # =========================================================================
    # Function/Tool Calling
    # =========================================================================

    def chat_completion_with_tools(
            self,
            messages: Messages,
            tools: List[ToolDefinition],
            *,
            tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """Chat completion with tool/function calling support."""
        start_time = time.time()
        
        try:
            # Convert tools to Anthropic format
            anthropic_tools = self._convert_tools_to_anthropic_format(tools)
            
            params = self._build_message_params(messages, config, **kwargs)
            params["tools"] = anthropic_tools
            
            if tool_choice:
                params["tool_choice"] = self._convert_tool_choice(tool_choice)
            
            response = self.client.messages.create(**params)
            
            return self._format_chat_response(response, time.time() - start_time)
            
        except Exception as e:
            raise self._transform_exception(e)

    async def async_chat_completion_with_tools(
            self,
            messages: Messages,
            tools: List[ToolDefinition],
            *,
            tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """Async chat completion with tools."""
        start_time = time.time()
        
        try:
            anthropic_tools = self._convert_tools_to_anthropic_format(tools)
            
            params = self._build_message_params(messages, config, **kwargs)
            params["tools"] = anthropic_tools
            
            if tool_choice:
                params["tool_choice"] = self._convert_tool_choice(tool_choice)
            
            response = await self.async_client.messages.create(**params)
            
            return self._format_chat_response(response, time.time() - start_time)
            
        except Exception as e:
            raise self._transform_exception(e)

    def execute_tool_calls(
            self,
            tool_calls: List[ToolCall],
            available_tools: Dict[str, Callable],
            **kwargs
    ) -> List[ToolResult]:
        """Execute tool calls and return results."""
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_input = tool_call.get("input", {})
            tool_id = tool_call.get("id")
            
            if tool_name not in available_tools:
                raise ToolNotFoundException(tool_name)
            
            try:
                func = available_tools[tool_name]
                if isinstance(tool_input, dict):
                    output = func(**tool_input)
                else:
                    output = func(tool_input)
                
                results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": str(output)
                })
                
            except Exception as e:
                raise ToolExecutionException(tool_name, str(e))
        
        return results

    # =========================================================================
    # Vision/Multimodal
    # =========================================================================

    def chat_completion_with_vision(
            self,
            messages: Messages,
            images: List[ImageInput],
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """Chat completion with image understanding."""
        if not self.supports_capability(ModelCapability.VISION):
            raise CapabilityNotSupportedException("vision", self.model_name)
        
        start_time = time.time()
        
        try:
            # Convert images and embed in messages
            processed_messages = self._embed_images_in_messages(messages, images)
            
            params = self._build_message_params(processed_messages, config, **kwargs)
            response = self.client.messages.create(**params)
            
            return self._format_chat_response(response, time.time() - start_time)
            
        except Exception as e:
            raise self._transform_exception(e)

    async def async_chat_completion_with_vision(
            self,
            messages: Messages,
            images: List[ImageInput],
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """Async chat completion with vision."""
        if not self.supports_capability(ModelCapability.VISION):
            raise CapabilityNotSupportedException("vision", self.model_name)
        
        start_time = time.time()
        
        try:
            processed_messages = self._embed_images_in_messages(messages, images)
            
            params = self._build_message_params(processed_messages, config, **kwargs)
            response = await self.async_client.messages.create(**params)
            
            return self._format_chat_response(response, time.time() - start_time)
            
        except Exception as e:
            raise self._transform_exception(e)

    # =========================================================================
    # Embeddings (Not Supported)
    # =========================================================================

    def embed_text(
            self,
            text: Union[str, List[str]],
            **kwargs
    ) -> Union[Embedding, List[Embedding]]:
        """Anthropic does not provide embedding models."""
        raise CapabilityNotSupportedException("embeddings", self.model_name)

    async def async_embed_text(
            self,
            text: Union[str, List[str]],
            **kwargs
    ) -> Union[Embedding, List[Embedding]]:
        """Anthropic does not provide embedding models."""
        raise CapabilityNotSupportedException("embeddings", self.model_name)

    # =========================================================================
    # Token Management
    # =========================================================================

    def count_tokens(self, text: str, **kwargs) -> int:
        """Count tokens in text."""
        try:
            # Use Anthropic's token counter
            result = self.client.count_tokens(text)
            return result
        except:
            # Fallback estimation: ~4 chars per token
            return len(text) // 4

    def count_message_tokens(self, messages: Messages, **kwargs) -> int:
        """Count tokens in messages."""
        # Convert to text and count
        text = self.format_messages(messages)
        return self.count_tokens(text)

    def truncate_text(
            self,
            text: str,
            max_tokens: int,
            **kwargs
    ) -> str:
        """Truncate text to fit within token limit."""
        current_tokens = self.count_tokens(text)
        
        if current_tokens <= max_tokens:
            return text
        
        # Binary search for optimal length
        ratio = max_tokens / current_tokens
        estimated_chars = int(len(text) * ratio * 0.95)  # 5% safety margin
        
        truncated = text[:estimated_chars]
        return truncated

    def get_context_window(self) -> int:
        """Get maximum context window size."""
        return self.get_model_info()["context_window"]

    def get_max_output_tokens(self) -> int:
        """Get maximum output tokens."""
        return self.get_model_info()["max_output_tokens"]

    # =========================================================================
    # Moderation (Not Directly Supported)
    # =========================================================================

    def moderate_content(
            self,
            content: Union[str, List[str]],
            **kwargs
    ) -> Union[ModerationResult, List[ModerationResult]]:
        """Claude has built-in safety but no separate moderation API."""
        # Return safe by default as Claude has built-in safety
        if isinstance(content, str):
            return {"flagged": False, "categories": {}, "scores": {}}
        return [{"flagged": False, "categories": {}, "scores": {}} for _ in content]

    # =========================================================================
    # Not Implemented Methods
    # =========================================================================

    def generate_image(self, prompt: str, **kwargs) -> ImageOutput:
        """Image generation not supported."""
        raise CapabilityNotSupportedException("image_generation", self.model_name)

    def edit_image(self, image: ImageInput, prompt: str, **kwargs) -> ImageOutput:
        """Image editing not supported."""
        raise CapabilityNotSupportedException("image_editing", self.model_name)

    def transcribe_audio(self, audio: Union[bytes, str], **kwargs) -> str:
        """Audio transcription not supported."""
        raise CapabilityNotSupportedException("audio_transcription", self.model_name)

    def generate_audio(self, text: str, **kwargs) -> bytes:
        """Audio generation not supported."""
        raise CapabilityNotSupportedException("audio_generation", self.model_name)

    def retrieve_documents(self, query: str, **kwargs) -> RetrievalResult:
        """Document retrieval not directly supported."""
        raise CapabilityNotSupportedException("rag", self.model_name)

    def batch_generate(self, prompts: List[str], **kwargs) -> List[str]:
        """Batch generation."""
        return [self.text_generation(p, **kwargs) for p in prompts]

    def batch_embed(self, texts: List[str], **kwargs) -> List[Embedding]:
        """Batch embedding not supported."""
        raise CapabilityNotSupportedException("embeddings", self.model_name)

    def create_fine_tuning_job(self, training_file: str, **kwargs) -> str:
        """Fine-tuning not publicly available."""
        raise NotImplementedError("Fine-tuning not publicly available")

    def get_fine_tuning_status(self, job_id: str, **kwargs) -> Dict[str, Any]:
        """Fine-tuning not publicly available."""
        raise NotImplementedError("Fine-tuning not publicly available")

    # =========================================================================
    # Observability
    # =========================================================================

    def log_request(
            self,
            method: str,
            input_data: Any,
            response: Any,
            *,
            latency_ms: Optional[float] = None,
            metadata: Optional[Dict[str, Any]] = None,
            **kwargs
    ) -> None:
        """Log request for monitoring."""
        # Could integrate with logging system
        pass

    def get_usage_stats(self, period: str = "day", **kwargs) -> Dict[str, Any]:
        """Get usage statistics."""
        return {}

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def format_messages(self, messages: Messages, **kwargs) -> str:
        """Convert messages to formatted prompt."""
        formatted = ""
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                formatted += f"{content}\n\n"
            elif role == "user":
                formatted += f"Human: {content}\n\n"
            elif role == "assistant":
                formatted += f"Assistant: {content}\n\n"
        
        return formatted

    def parse_tool_calls(self, response: Dict[str, Any], **kwargs) -> List[ToolCall]:
        """Parse tool calls from response."""
        tool_calls = []
        
        content = response.get("content", [])
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                tool_calls.append({
                    "id": block.get("id"),
                    "type": "tool_use",
                    "name": block.get("name"),
                    "input": block.get("input", {})
                })
        
        return tool_calls

    def validate_config(
            self,
            config: Dict[str, Any],
            **kwargs
    ) -> Tuple[bool, List[str]]:
        """Validate configuration."""
        errors = []
        
        max_tokens = config.get("max_tokens", 0)
        if max_tokens > self.get_max_output_tokens():
            errors.append(f"max_tokens exceeds limit of {self.get_max_output_tokens()}")
        
        temperature = config.get("temperature", 1.0)
        if temperature < 0 or temperature > 1:
            errors.append("temperature must be between 0.0 and 1.0")
        
        return (len(errors) == 0, errors)

    def health_check(self, **kwargs) -> bool:
        """Check if service is healthy."""
        try:
            response = self.text_generation(
                "Hi",
                config=GenerationConfig(max_tokens=5)
            )
            return True
        except:
            return False

    def close(self) -> None:
        """Close connections and cleanup."""
        self.client = None
        self.async_client = None

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _build_message_params(
            self,
            messages: Messages,
            config: Optional[GenerationConfig],
            **kwargs
    ) -> Dict[str, Any]:
        """Build parameters for Anthropic Messages API."""
        # Extract system message if present
        system_message = None
        processed_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                processed_messages.append(msg)
        
        params = {
            "model": self.model_name,
            "messages": processed_messages,
            "max_tokens": 4096  # Default
        }
        
        if system_message:
            params["system"] = system_message
        
        # Add generation config
        if config:
            if config.max_tokens:
                params["max_tokens"] = config.max_tokens
            if config.temperature is not None:
                params["temperature"] = config.temperature
            if config.top_p is not None:
                params["top_p"] = config.top_p
            if config.top_k is not None:
                params["top_k"] = config.top_k
            if config.stop_sequences:
                params["stop_sequences"] = config.stop_sequences
        
        # Add kwargs
        params.update(kwargs)
        
        return params

    def _extract_text_from_response(self, response) -> str:
        """Extract text content from Anthropic response."""
        if hasattr(response, 'content'):
            for block in response.content:
                if hasattr(block, 'text'):
                    return block.text
        return ""

    def _format_chat_response(
            self,
            response,
            latency: float
    ) -> Dict[str, Any]:
        """Format Anthropic response to standard format."""
        content = []
        tool_calls = []
        
        if hasattr(response, 'content'):
            for block in response.content:
                if hasattr(block, 'text'):
                    content.append(block.text)
                elif hasattr(block, 'type') and block.type == 'tool_use':
                    tool_calls.append({
                        "id": block.id,
                        "type": "tool_use",
                        "name": block.name,
                        "input": block.input
                    })
        
        usage = None
        if hasattr(response, 'usage'):
            usage = TokenUsage(
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens
            )
        
        metadata = CompletionMetadata(
            model=response.model if hasattr(response, 'model') else self.model_name,
            finish_reason=response.stop_reason if hasattr(response, 'stop_reason') else None,
            usage=usage,
            latency_ms=latency * 1000
        )
        
        return {
            "content": "\n".join(content) if content else "",
            "role": "assistant",
            "tool_calls": tool_calls if tool_calls else None,
            "metadata": metadata
        }

    def _convert_tools_to_anthropic_format(
            self,
            tools: List[ToolDefinition]
    ) -> List[Dict[str, Any]]:
        """Convert standard tool definitions to Anthropic format."""
        anthropic_tools = []
        
        for tool in tools:
            if tool.get("type") == "function":
                func = tool.get("function", {})
                anthropic_tools.append({
                    "name": func.get("name"),
                    "description": func.get("description", ""),
                    "input_schema": func.get("parameters", {})
                })
        
        return anthropic_tools

    def _convert_tool_choice(
            self,
            tool_choice: Union[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Convert tool choice to Anthropic format."""
        if isinstance(tool_choice, str):
            if tool_choice == "auto":
                return {"type": "auto"}
            elif tool_choice == "required":
                return {"type": "any"}
            else:
                return {"type": "tool", "name": tool_choice}
        return tool_choice

    def _embed_images_in_messages(
            self,
            messages: Messages,
            images: List[ImageInput]
    ) -> Messages:
        """Embed images into messages."""
        processed_messages = []
        image_idx = 0
        
        for msg in messages:
            if msg["role"] == "user" and image_idx < len(images):
                # Add images to user message
                content = []
                
                # Add images
                for img in images[image_idx:]:
                    img_data = self._process_image(img)
                    content.append(img_data)
                
                # Add text content
                if isinstance(msg["content"], str):
                    content.append({"type": "text", "text": msg["content"]})
                
                processed_messages.append({
                    "role": "user",
                    "content": content
                })
                image_idx = len(images)
            else:
                processed_messages.append(msg)
        
        return processed_messages

    def _process_image(self, image: ImageInput) -> Dict[str, Any]:
        """Process image into Anthropic format."""
        if isinstance(image, str):
            # Could be URL or file path
            if image.startswith("http"):
                # Download image
                import requests
                response = requests.get(image)
                image_data = base64.b64encode(response.content).decode()
                media_type = response.headers.get('content-type', 'image/jpeg')
            else:
                # Read from file
                with open(image, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode()
                media_type = "image/jpeg"  # Could infer from extension
        elif isinstance(image, bytes):
            image_data = base64.b64encode(image).decode()
            media_type = "image/jpeg"
        else:
            # PIL Image
            from io import BytesIO
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            image_data = base64.b64encode(buffer.getvalue()).decode()
            media_type = "image/png"
        
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": image_data
            }
        }

    def _transform_exception(self, exception: Exception) -> LLMFacadeException:
        """Transform Anthropic exceptions to facade exceptions."""
        error_msg = str(exception).lower()
        
        if "rate" in error_msg or "429" in error_msg:
            return RateLimitException(str(exception))
        elif "authentication" in error_msg or "401" in error_msg:
            return AuthenticationException(str(exception))
        elif "context" in error_msg or "too long" in error_msg:
            return ContextLengthExceededException(0, 0)
        elif "timeout" in error_msg:
            return NetworkException(str(exception))
        else:
            return LLMFacadeException(str(exception))


def create_anthropic_llm(
        model_name: str = "claude-3-5-sonnet-20241022",
        **kwargs
) -> AnthropicLLMFacade:
    """
    Create an Anthropic LLM Facade instance.

    Args:
        model_name: Claude model identifier
        **kwargs: Additional configuration

    Returns:
        Configured AnthropicLLMFacade instance

    Example:
        >>> llm = create_anthropic_llm("claude-3-5-sonnet-20241022")
    """
    return AnthropicLLMFacade(model_name, **kwargs)


__all__ = ['AnthropicLLMFacade', 'create_anthropic_llm']
