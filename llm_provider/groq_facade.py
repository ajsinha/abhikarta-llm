"""
Groq LLM Facade Implementation

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
Groq's ultra-fast LPU inference engine, supporting Llama, Mixtral, and Gemma models.
"""

import os
import json
import time
import asyncio
from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator, Callable, Tuple

from llm_facade import (
    LLMFacade, ModelCapability, GenerationConfig, TokenUsage, CompletionMetadata,
    Messages, TextStream, DeltaStream, ToolDefinition, ToolCall, ToolResult,
    Document, RetrievalResult, Embedding, ImageInput, ImageOutput,
    ModerationResult, SafetyResult, ResponseFormat, LLMFacadeException,
    CapabilityNotSupportedException, RateLimitException, ContentFilterException,
    ContextLengthExceededException, ToolNotFoundException, ToolExecutionException,
    InvalidResponseException, AuthenticationException, NetworkException
)


class GroqLLMFacade(LLMFacade):
    """
    Groq implementation of the LLMFacade interface.

    Supports ultra-fast inference with Groq LPU:
    - Llama 3 (8B, 70B)
    - Llama 3.1 (8B, 70B, 405B)
    - Mixtral 8x7B
    - Gemma 7B, 2B

    Features:
    - Ultra-fast inference (500+ tokens/sec)
    - Chat completion
    - Function calling
    - Streaming responses
    - JSON mode
    - Low latency (<1s for most queries)

    Example:
        >>> llm = GroqLLMFacade(
        ...     model_name="llama-3.1-70b-versatile",
        ...     api_key="gsk_..."
        ... )
        >>> response = llm.chat_completion([
        ...     {"role": "user", "content": "Hello!"}
        ... ])
    """

    MODEL_INFO = {
        "llama-3.1-405b-reasoning": {
            "max_tokens": 8192, "context_window": 131072, "supports_functions": True
        },
        "llama-3.1-70b-versatile": {
            "max_tokens": 8192, "context_window": 131072, "supports_functions": True
        },
        "llama-3.1-8b-instant": {
            "max_tokens": 8192, "context_window": 131072, "supports_functions": True
        },
        "llama3-70b-8192": {
            "max_tokens": 8192, "context_window": 8192, "supports_functions": True
        },
        "llama3-8b-8192": {
            "max_tokens": 8192, "context_window": 8192, "supports_functions": True
        },
        "mixtral-8x7b-32768": {
            "max_tokens": 32768, "context_window": 32768, "supports_functions": True
        },
        "gemma-7b-it": {
            "max_tokens": 8192, "context_window": 8192, "supports_functions": False
        },
        "gemma2-9b-it": {
            "max_tokens": 8192, "context_window": 8192, "supports_functions": True
        }
    }

    def __init__(self, model_name: str, api_key: Optional[str] = None, base_url: Optional[str] = None,
                 timeout: Optional[float] = None, max_retries: int = 3, **kwargs) -> None:
        self.model_name = model_name
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.base_url = base_url or "https://api.groq.com/openai/v1"
        self.timeout = timeout or 60.0  # Groq is fast!
        self.max_retries = max_retries
        self.kwargs = kwargs
        
        if not self.api_key:
            raise AuthenticationException("Groq API key not provided")
        
        self._initialize_client()
        self._model_info = None

    def _initialize_client(self):
        try:
            from groq import Groq, AsyncGroq
            
            self.client = Groq(api_key=self.api_key)
            self.async_client = AsyncGroq(api_key=self.api_key)
            
        except ImportError:
            raise ImportError("Please install groq: pip install groq")

    def get_capabilities(self) -> List[ModelCapability]:
        capabilities = [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CHAT_COMPLETION,
            ModelCapability.STREAMING,
            ModelCapability.CODE_GENERATION,
            ModelCapability.JSON_MODE
        ]
        
        config = self.MODEL_INFO.get(self.model_name, {})
        if config.get("supports_functions", False):
            capabilities.extend([
                ModelCapability.FUNCTION_CALLING,
                ModelCapability.TOOL_USE
            ])
        
        return capabilities

    def supports_capability(self, capability: ModelCapability) -> bool:
        return capability in self.get_capabilities()

    def get_model_info(self) -> Dict[str, Any]:
        if self._model_info is None:
            config = self.MODEL_INFO.get(self.model_name, {
                "max_tokens": 8192, "context_window": 8192, "supports_functions": False
            })
            
            self._model_info = {
                "provider": "groq",
                "name": self.model_name,
                "version": "latest",
                "max_input_tokens": config["context_window"],
                "max_output_tokens": config["max_tokens"],
                "context_window": config["context_window"],
                "supports_streaming": True,
                "supports_functions": config["supports_functions"],
                "supports_vision": False,
                "modalities": ["text"],
                "inference_speed": "ultra_fast"  # Groq's specialty!
            }
        return self._model_info

    def text_generation(self, prompt: str, *, config: Optional[GenerationConfig] = None, **kwargs) -> str:
        try:
            messages = [{"role": "user", "content": prompt}]
            params = self._build_chat_params(messages, config, **kwargs)
            
            response = self.client.chat.completions.create(**params)
            return response.choices[0].message.content
            
        except Exception as e:
            raise self._transform_exception(e)

    async def async_text_generation(self, prompt: str, *, config: Optional[GenerationConfig] = None,
                                    **kwargs) -> str:
        try:
            messages = [{"role": "user", "content": prompt}]
            params = self._build_chat_params(messages, config, **kwargs)
            
            response = await self.async_client.chat.completions.create(**params)
            return response.choices[0].message.content
            
        except Exception as e:
            raise self._transform_exception(e)

    def stream_text_generation(self, prompt: str, *, config: Optional[GenerationConfig] = None,
                               **kwargs) -> TextStream:
        try:
            messages = [{"role": "user", "content": prompt}]
            params = self._build_chat_params(messages, config, **kwargs)
            params["stream"] = True
            
            stream = self.client.chat.completions.create(**params)
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise self._transform_exception(e)

    async def async_stream_text_generation(self, prompt: str, *, config: Optional[GenerationConfig] = None,
                                          **kwargs) -> AsyncIterator[str]:
        try:
            messages = [{"role": "user", "content": prompt}]
            params = self._build_chat_params(messages, config, **kwargs)
            params["stream"] = True
            
            stream = await self.async_client.chat.completions.create(**params)
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise self._transform_exception(e)

    def chat_completion(self, messages: Messages, *, config: Optional[GenerationConfig] = None,
                       **kwargs) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            params = self._build_chat_params(messages, config, **kwargs)
            response = self.client.chat.completions.create(**params)
            
            return self._format_chat_response(response, time.time() - start_time)
            
        except Exception as e:
            raise self._transform_exception(e)

    async def async_chat_completion(self, messages: Messages, *, config: Optional[GenerationConfig] = None,
                                    **kwargs) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            params = self._build_chat_params(messages, config, **kwargs)
            response = await self.async_client.chat.completions.create(**params)
            
            return self._format_chat_response(response, time.time() - start_time)
            
        except Exception as e:
            raise self._transform_exception(e)

    def stream_chat_completion(self, messages: Messages, *, config: Optional[GenerationConfig] = None,
                               **kwargs) -> DeltaStream:
        try:
            params = self._build_chat_params(messages, config, **kwargs)
            params["stream"] = True
            
            stream = self.client.chat.completions.create(**params)
            for chunk in stream:
                delta = chunk.choices[0].delta
                yield {
                    "type": "content_delta",
                    "delta": {"content": delta.content if delta.content else None}
                }
                
        except Exception as e:
            raise self._transform_exception(e)

    async def async_stream_chat_completion(self, messages: Messages, *,
                                          config: Optional[GenerationConfig] = None,
                                          **kwargs) -> AsyncIterator[Dict[str, Any]]:
        try:
            params = self._build_chat_params(messages, config, **kwargs)
            params["stream"] = True
            
            stream = await self.async_client.chat.completions.create(**params)
            async for chunk in stream:
                delta = chunk.choices[0].delta
                yield {
                    "type": "content_delta",
                    "delta": {"content": delta.content if delta.content else None}
                }
                
        except Exception as e:
            raise self._transform_exception(e)

    def chat_completion_with_tools(self, messages: Messages, tools: List[ToolDefinition], *,
                                   tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
                                   config: Optional[GenerationConfig] = None, **kwargs) -> Dict[str, Any]:
        if not self.supports_capability(ModelCapability.FUNCTION_CALLING):
            raise CapabilityNotSupportedException("function_calling", self.model_name)
        
        start_time = time.time()
        
        try:
            params = self._build_chat_params(messages, config, **kwargs)
            params["tools"] = tools
            
            if tool_choice:
                params["tool_choice"] = tool_choice
            
            response = self.client.chat.completions.create(**params)
            return self._format_chat_response(response, time.time() - start_time)
            
        except Exception as e:
            raise self._transform_exception(e)

    async def async_chat_completion_with_tools(self, messages: Messages, tools: List[ToolDefinition], *,
                                              tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
                                              config: Optional[GenerationConfig] = None,
                                              **kwargs) -> Dict[str, Any]:
        if not self.supports_capability(ModelCapability.FUNCTION_CALLING):
            raise CapabilityNotSupportedException("function_calling", self.model_name)
        
        start_time = time.time()
        
        try:
            params = self._build_chat_params(messages, config, **kwargs)
            params["tools"] = tools
            
            if tool_choice:
                params["tool_choice"] = tool_choice
            
            response = await self.async_client.chat.completions.create(**params)
            return self._format_chat_response(response, time.time() - start_time)
            
        except Exception as e:
            raise self._transform_exception(e)

    def execute_tool_calls(self, tool_calls: List[ToolCall], available_tools: Dict[str, Callable],
                          **kwargs) -> List[ToolResult]:
        results = []
        
        for tool_call in tool_calls:
            func_call = tool_call.get("function", {})
            func_name = func_call.get("name")
            func_args_str = func_call.get("arguments", "{}")
            tool_id = tool_call.get("id")
            
            if func_name not in available_tools:
                raise ToolNotFoundException(func_name)
            
            try:
                func = available_tools[func_name]
                func_args = json.loads(func_args_str)
                
                output = func(**func_args)
                
                results.append({
                    "tool_call_id": tool_id,
                    "role": "tool",
                    "name": func_name,
                    "content": str(output)
                })
                
            except Exception as e:
                raise ToolExecutionException(func_name, str(e))
        
        return results

    # Not supported methods
    def chat_completion_with_vision(self, messages: Messages, images: List[ImageInput], *,
                                    config: Optional[GenerationConfig] = None, **kwargs) -> Dict[str, Any]:
        raise CapabilityNotSupportedException("vision", self.model_name)

    async def async_chat_completion_with_vision(self, messages: Messages, images: List[ImageInput], *,
                                               config: Optional[GenerationConfig] = None,
                                               **kwargs) -> Dict[str, Any]:
        raise CapabilityNotSupportedException("vision", self.model_name)

    def embed_text(self, text: Union[str, List[str]], **kwargs) -> Union[Embedding, List[Embedding]]:
        raise CapabilityNotSupportedException("embeddings", self.model_name)

    async def async_embed_text(self, text: Union[str, List[str]], **kwargs) -> Union[Embedding, List[Embedding]]:
        raise CapabilityNotSupportedException("embeddings", self.model_name)

    def generate_image(self, prompt: str, **kwargs) -> ImageOutput:
        raise CapabilityNotSupportedException("image_generation", self.model_name)

    def edit_image(self, image: ImageInput, prompt: str, **kwargs) -> ImageOutput:
        raise CapabilityNotSupportedException("image_editing", self.model_name)

    def transcribe_audio(self, audio: Union[bytes, str], **kwargs) -> str:
        raise CapabilityNotSupportedException("audio_transcription", self.model_name)

    def generate_audio(self, text: str, **kwargs) -> bytes:
        raise CapabilityNotSupportedException("audio_generation", self.model_name)

    def moderate_content(self, content: Union[str, List[str]], **kwargs) -> Union[ModerationResult, List[ModerationResult]]:
        if isinstance(content, str):
            return {"flagged": False, "categories": {}, "scores": {}}
        return [{"flagged": False, "categories": {}, "scores": {}} for _ in content]

    def retrieve_documents(self, query: str, **kwargs) -> RetrievalResult:
        raise CapabilityNotSupportedException("rag", self.model_name)

    def batch_generate(self, prompts: List[str], **kwargs) -> List[str]:
        return [self.text_generation(p, **kwargs) for p in prompts]

    def batch_embed(self, texts: List[str], **kwargs) -> List[Embedding]:
        raise CapabilityNotSupportedException("embeddings", self.model_name)

    def create_fine_tuning_job(self, training_file: str, **kwargs) -> str:
        raise NotImplementedError("Fine-tuning not available")

    def get_fine_tuning_status(self, job_id: str, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError("Fine-tuning status not available")

    # Token management
    def count_tokens(self, text: str, **kwargs) -> int:
        # Groq uses similar tokenization to Llama
        return len(text) // 4

    def count_message_tokens(self, messages: Messages, **kwargs) -> int:
        return sum(len(m.get("content", "")) // 4 for m in messages)

    def truncate_text(self, text: str, max_tokens: int, **kwargs) -> str:
        return text[:max_tokens * 4]

    def get_context_window(self) -> int:
        return self.get_model_info()["context_window"]

    def get_max_output_tokens(self) -> int:
        return self.get_model_info()["max_output_tokens"]

    # Utility methods
    def log_request(self, method: str, input_data: Any, response: Any, *,
                   latency_ms: Optional[float] = None, metadata: Optional[Dict[str, Any]] = None,
                   **kwargs) -> None:
        pass

    def get_usage_stats(self, period: str = "day", **kwargs) -> Dict[str, Any]:
        return {}

    def format_messages(self, messages: Messages, **kwargs) -> str:
        return "\n".join(f"{m['role']}: {m['content']}" for m in messages)

    def parse_tool_calls(self, response: Dict[str, Any], **kwargs) -> List[ToolCall]:
        metadata = response.get("metadata", {})
        return metadata.get("tool_calls", [])

    def validate_config(self, config: Dict[str, Any], **kwargs) -> Tuple[bool, List[str]]:
        errors = []
        if config.get("max_tokens", 0) > self.get_max_output_tokens():
            errors.append("max_tokens exceeds limit")
        return (len(errors) == 0, errors)

    def health_check(self, **kwargs) -> bool:
        try:
            self.text_generation("Hi", config=GenerationConfig(max_tokens=5))
            return True
        except:
            return False

    def close(self) -> None:
        self.client = None
        self.async_client = None

    # Helper methods
    def _build_chat_params(self, messages: Messages, config: Optional[GenerationConfig],
                          **kwargs) -> Dict[str, Any]:
        params = {
            "model": self.model_name,
            "messages": messages
        }
        
        if config:
            if config.max_tokens:
                params["max_tokens"] = config.max_tokens
            if config.temperature is not None:
                params["temperature"] = config.temperature
            if config.top_p is not None:
                params["top_p"] = config.top_p
            if config.stop_sequences:
                params["stop"] = config.stop_sequences
            if config.seed is not None:
                params["seed"] = config.seed
            
            # JSON mode
            if config.response_format and config.response_format == ResponseFormat.JSON:
                params["response_format"] = {"type": "json_object"}
        
        params.update(kwargs)
        return params

    def _format_chat_response(self, response, latency: float) -> Dict[str, Any]:
        choice = response.choices[0]
        message = choice.message
        
        usage = None
        if hasattr(response, 'usage') and response.usage:
            usage = TokenUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            )
        
        metadata = CompletionMetadata(
            model=response.model,
            finish_reason=choice.finish_reason,
            usage=usage,
            latency_ms=latency * 1000
        )
        
        tool_calls = None
        if hasattr(message, 'tool_calls') and message.tool_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]
        
        return {
            "content": message.content or "",
            "role": message.role,
            "tool_calls": tool_calls,
            "metadata": metadata
        }

    def _transform_exception(self, exception: Exception) -> LLMFacadeException:
        error_msg = str(exception).lower()
        
        if "rate" in error_msg or "429" in error_msg:
            return RateLimitException(str(exception))
        elif "auth" in error_msg or "401" in error_msg:
            return AuthenticationException(str(exception))
        elif "context" in error_msg or "token limit" in error_msg:
            return ContextLengthExceededException(0, 0)
        elif "timeout" in error_msg:
            return NetworkException(str(exception))
        else:
            return LLMFacadeException(str(exception))


def create_groq_llm(model_name: str = "llama-3.1-70b-versatile", **kwargs) -> GroqLLMFacade:
    """Create a Groq LLM Facade instance."""
    return GroqLLMFacade(model_name, **kwargs)


__all__ = ['GroqLLMFacade', 'create_groq_llm']
