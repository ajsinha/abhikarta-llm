"""
Mistral LLM Facade Implementation

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
Mistral AI models including Mistral 7B, Mixtral, and specialized variants.
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


class MistralLLMFacade(LLMFacade):
    """
    Mistral AI implementation of the LLMFacade interface.

    Supports Mistral models:
    - Mistral 7B
    - Mistral 7B Instruct
    - Mixtral 8x7B
    - Mixtral 8x22B
    - Mistral Small/Medium/Large

    Features:
    - Function/tool calling
    - JSON mode
    - Streaming responses
    - Async operations
    - Code generation
    """

    MODEL_INFO = {
        "mistral-tiny": {"max_tokens": 8192, "context_window": 32000, "supports_functions": False},
        "mistral-small-latest": {"max_tokens": 8192, "context_window": 32000, "supports_functions": True},
        "mistral-medium-latest": {"max_tokens": 8192, "context_window": 32000, "supports_functions": True},
        "mistral-large-latest": {"max_tokens": 8192, "context_window": 128000, "supports_functions": True},
        "open-mistral-7b": {"max_tokens": 8192, "context_window": 32000, "supports_functions": False},
        "open-mixtral-8x7b": {"max_tokens": 8192, "context_window": 32000, "supports_functions": True},
        "open-mixtral-8x22b": {"max_tokens": 64000, "context_window": 64000, "supports_functions": True}
    }

    def __init__(self, model_name: str, api_key: Optional[str] = None, base_url: Optional[str] = None,
                 timeout: Optional[float] = None, max_retries: int = 3, **kwargs) -> None:
        self.model_name = model_name
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        self.base_url = base_url
        self.timeout = timeout or 300.0
        self.max_retries = max_retries
        self.kwargs = kwargs
        
        if not self.api_key:
            raise AuthenticationException("Mistral API key not provided")
        
        self._initialize_client()
        self._model_info = None

    def _initialize_client(self):
        try:
            from mistralai.client import MistralClient
            from mistralai.async_client import MistralAsyncClient
            
            self.client = MistralClient(api_key=self.api_key)
            self.async_client = MistralAsyncClient(api_key=self.api_key)
        except ImportError:
            raise ImportError("Please install mistralai: pip install mistralai")

    def get_capabilities(self) -> List[ModelCapability]:
        capabilities = [ModelCapability.TEXT_GENERATION, ModelCapability.CHAT_COMPLETION,
                       ModelCapability.STREAMING, ModelCapability.CODE_GENERATION,
                       ModelCapability.JSON_MODE]
        
        config = self.MODEL_INFO.get(self.model_name, {})
        if config.get("supports_functions", False):
            capabilities.extend([ModelCapability.FUNCTION_CALLING, ModelCapability.TOOL_USE])
        
        return capabilities

    def supports_capability(self, capability: ModelCapability) -> bool:
        return capability in self.get_capabilities()

    def get_model_info(self) -> Dict[str, Any]:
        if self._model_info is None:
            config = self.MODEL_INFO.get(self.model_name, {"max_tokens": 8192, "context_window": 32000})
            self._model_info = {
                "provider": "mistral", "name": self.model_name, "version": "latest",
                "max_input_tokens": config["context_window"], "max_output_tokens": config["max_tokens"],
                "context_window": config["context_window"], "supports_streaming": True,
                "supports_functions": config.get("supports_functions", False),
                "supports_vision": False, "modalities": ["text"]
            }
        return self._model_info

    def text_generation(self, prompt: str, *, config: Optional[GenerationConfig] = None, **kwargs) -> str:
        try:
            from mistralai.models.chat_completion import ChatMessage
            messages = [ChatMessage(role="user", content=prompt)]
            
            params = {"model": self.model_name, "messages": messages}
            if config and config.max_tokens:
                params["max_tokens"] = config.max_tokens
            if config and config.temperature is not None:
                params["temperature"] = config.temperature
            if config and config.top_p is not None:
                params["top_p"] = config.top_p
            
            response = self.client.chat(**params)
            return response.choices[0].message.content
        except Exception as e:
            raise self._transform_exception(e)

    async def async_text_generation(self, prompt: str, *, config: Optional[GenerationConfig] = None, **kwargs) -> str:
        try:
            from mistralai.models.chat_completion import ChatMessage
            messages = [ChatMessage(role="user", content=prompt)]
            
            params = {"model": self.model_name, "messages": messages}
            if config and config.max_tokens:
                params["max_tokens"] = config.max_tokens
            if config and config.temperature is not None:
                params["temperature"] = config.temperature
            
            response = await self.async_client.chat(**params)
            return response.choices[0].message.content
        except Exception as e:
            raise self._transform_exception(e)

    def stream_text_generation(self, prompt: str, *, config: Optional[GenerationConfig] = None, **kwargs) -> TextStream:
        try:
            from mistralai.models.chat_completion import ChatMessage
            messages = [ChatMessage(role="user", content=prompt)]
            
            params = {"model": self.model_name, "messages": messages}
            if config and config.max_tokens:
                params["max_tokens"] = config.max_tokens
            
            for chunk in self.client.chat_stream(**params):
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise self._transform_exception(e)

    async def async_stream_text_generation(self, prompt: str, *, config: Optional[GenerationConfig] = None,
                                          **kwargs) -> AsyncIterator[str]:
        try:
            from mistralai.models.chat_completion import ChatMessage
            messages = [ChatMessage(role="user", content=prompt)]
            
            params = {"model": self.model_name, "messages": messages}
            if config and config.max_tokens:
                params["max_tokens"] = config.max_tokens
            
            async for chunk in self.async_client.chat_stream(**params):
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise self._transform_exception(e)

    def chat_completion(self, messages: Messages, *, config: Optional[GenerationConfig] = None, **kwargs) -> Dict[str, Any]:
        start_time = time.time()
        try:
            from mistralai.models.chat_completion import ChatMessage
            mistral_messages = [ChatMessage(role=m["role"], content=m["content"]) for m in messages]
            
            params = {"model": self.model_name, "messages": mistral_messages}
            if config and config.max_tokens:
                params["max_tokens"] = config.max_tokens
            if config and config.temperature is not None:
                params["temperature"] = config.temperature
            
            response = self.client.chat(**params)
            return self._format_chat_response(response, time.time() - start_time)
        except Exception as e:
            raise self._transform_exception(e)

    async def async_chat_completion(self, messages: Messages, *, config: Optional[GenerationConfig] = None,
                                    **kwargs) -> Dict[str, Any]:
        start_time = time.time()
        try:
            from mistralai.models.chat_completion import ChatMessage
            mistral_messages = [ChatMessage(role=m["role"], content=m["content"]) for m in messages]
            
            params = {"model": self.model_name, "messages": mistral_messages}
            if config and config.max_tokens:
                params["max_tokens"] = config.max_tokens
            
            response = await self.async_client.chat(**params)
            return self._format_chat_response(response, time.time() - start_time)
        except Exception as e:
            raise self._transform_exception(e)

    def stream_chat_completion(self, messages: Messages, *, config: Optional[GenerationConfig] = None,
                               **kwargs) -> DeltaStream:
        try:
            from mistralai.models.chat_completion import ChatMessage
            mistral_messages = [ChatMessage(role=m["role"], content=m["content"]) for m in messages]
            
            params = {"model": self.model_name, "messages": mistral_messages}
            if config and config.max_tokens:
                params["max_tokens"] = config.max_tokens
            
            for chunk in self.client.chat_stream(**params):
                yield {"type": "content_delta", "delta": {"content": chunk.choices[0].delta.content}}
        except Exception as e:
            raise self._transform_exception(e)

    async def async_stream_chat_completion(self, messages: Messages, *, config: Optional[GenerationConfig] = None,
                                          **kwargs) -> AsyncIterator[Dict[str, Any]]:
        try:
            from mistralai.models.chat_completion import ChatMessage
            mistral_messages = [ChatMessage(role=m["role"], content=m["content"]) for m in messages]
            
            params = {"model": self.model_name, "messages": mistral_messages}
            if config and config.max_tokens:
                params["max_tokens"] = config.max_tokens
            
            async for chunk in self.async_client.chat_stream(**params):
                yield {"type": "content_delta", "delta": {"content": chunk.choices[0].delta.content}}
        except Exception as e:
            raise self._transform_exception(e)

    def chat_completion_with_tools(self, messages: Messages, tools: List[ToolDefinition], *,
                                   tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
                                   config: Optional[GenerationConfig] = None, **kwargs) -> Dict[str, Any]:
        if not self.supports_capability(ModelCapability.FUNCTION_CALLING):
            raise CapabilityNotSupportedException("function_calling", self.model_name)
        
        start_time = time.time()
        try:
            from mistralai.models.chat_completion import ChatMessage
            mistral_messages = [ChatMessage(role=m["role"], content=m["content"]) for m in messages]
            
            params = {"model": self.model_name, "messages": mistral_messages, "tools": tools}
            if config and config.max_tokens:
                params["max_tokens"] = config.max_tokens
            if tool_choice:
                params["tool_choice"] = tool_choice
            
            response = self.client.chat(**params)
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
            from mistralai.models.chat_completion import ChatMessage
            mistral_messages = [ChatMessage(role=m["role"], content=m["content"]) for m in messages]
            
            params = {"model": self.model_name, "messages": mistral_messages, "tools": tools}
            if config and config.max_tokens:
                params["max_tokens"] = config.max_tokens
            
            response = await self.async_client.chat(**params)
            return self._format_chat_response(response, time.time() - start_time)
        except Exception as e:
            raise self._transform_exception(e)

    def execute_tool_calls(self, tool_calls: List[ToolCall], available_tools: Dict[str, Callable],
                          **kwargs) -> List[ToolResult]:
        results = []
        for tool_call in tool_calls:
            func_call = tool_call.get("function", {})
            func_name = func_call.get("name")
            func_args = json.loads(func_call.get("arguments", "{}"))
            
            if func_name not in available_tools:
                raise ToolNotFoundException(func_name)
            
            try:
                output = available_tools[func_name](**func_args)
                results.append({"tool_call_id": tool_call.get("id"), "content": str(output)})
            except Exception as e:
                raise ToolExecutionException(func_name, str(e))
        return results

    # Unsupported methods
    def chat_completion_with_vision(self, messages: Messages, images: List[ImageInput], *,
                                    config: Optional[GenerationConfig] = None, **kwargs) -> Dict[str, Any]:
        raise CapabilityNotSupportedException("vision", self.model_name)

    async def async_chat_completion_with_vision(self, messages: Messages, images: List[ImageInput], *,
                                               config: Optional[GenerationConfig] = None, **kwargs) -> Dict[str, Any]:
        raise CapabilityNotSupportedException("vision", self.model_name)

    def embed_text(self, text: Union[str, List[str]], **kwargs) -> Union[Embedding, List[Embedding]]:
        try:
            is_single = isinstance(text, str)
            texts = [text] if is_single else text
            
            response = self.client.embeddings(model="mistral-embed", input=texts)
            embeddings = [item.embedding for item in response.data]
            return embeddings[0] if is_single else embeddings
        except Exception as e:
            raise self._transform_exception(e)

    async def async_embed_text(self, text: Union[str, List[str]], **kwargs) -> Union[Embedding, List[Embedding]]:
        try:
            is_single = isinstance(text, str)
            texts = [text] if is_single else text
            
            response = await self.async_client.embeddings(model="mistral-embed", input=texts)
            embeddings = [item.embedding for item in response.data]
            return embeddings[0] if is_single else embeddings
        except Exception as e:
            raise self._transform_exception(e)

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
        return self.embed_text(texts, **kwargs)

    def create_fine_tuning_job(self, training_file: str, **kwargs) -> str:
        raise NotImplementedError("Fine-tuning not available via API")

    def get_fine_tuning_status(self, job_id: str, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError("Fine-tuning status not available")

    # Token management
    def count_tokens(self, text: str, **kwargs) -> int:
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
    def log_request(self, method: str, input_data: Any, response: Any, *, latency_ms: Optional[float] = None,
                   metadata: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        pass

    def get_usage_stats(self, period: str = "day", **kwargs) -> Dict[str, Any]:
        return {}

    def format_messages(self, messages: Messages, **kwargs) -> str:
        return "\n".join(f"{m['role']}: {m['content']}" for m in messages)

    def parse_tool_calls(self, response: Dict[str, Any], **kwargs) -> List[ToolCall]:
        metadata = response.get("metadata", {})
        if hasattr(metadata, "tool_calls"):
            return metadata.tool_calls
        return []

    def validate_config(self, config: Dict[str, Any], **kwargs) -> Tuple[bool, List[str]]:
        errors = []
        if config.get("max_tokens", 0) > self.get_max_output_tokens():
            errors.append(f"max_tokens exceeds limit")
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

    def _format_chat_response(self, response, latency: float) -> Dict[str, Any]:
        choice = response.choices[0]
        usage = TokenUsage(prompt_tokens=response.usage.prompt_tokens,
                          completion_tokens=response.usage.completion_tokens,
                          total_tokens=response.usage.total_tokens)
        
        metadata = CompletionMetadata(model=response.model, finish_reason=choice.finish_reason,
                                     usage=usage, latency_ms=latency * 1000)
        
        tool_calls = None
        if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
            tool_calls = [{"id": tc.id, "type": "function",
                          "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                         for tc in choice.message.tool_calls]
        
        return {"content": choice.message.content or "", "role": "assistant",
                "tool_calls": tool_calls, "metadata": metadata}

    def _transform_exception(self, exception: Exception) -> LLMFacadeException:
        error_msg = str(exception).lower()
        if "rate" in error_msg:
            return RateLimitException(str(exception))
        elif "auth" in error_msg:
            return AuthenticationException(str(exception))
        elif "timeout" in error_msg:
            return NetworkException(str(exception))
        return LLMFacadeException(str(exception))


def create_mistral_llm(model_name: str = "mistral-large-latest", **kwargs) -> MistralLLMFacade:
    """Create a Mistral LLM Facade instance."""
    return MistralLLMFacade(model_name, **kwargs)


__all__ = ['MistralLLMFacade', 'create_mistral_llm']
