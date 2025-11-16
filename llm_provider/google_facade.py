"""
Google LLM Facade Implementation

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
Google's Gemini models and PaLM API.
"""

import os
import json
import time
import asyncio
import base64
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


class GoogleLLMFacade(LLMFacade):
    """
    Google implementation of the LLMFacade interface for Gemini models.

    Supports Google models:
    - Gemini Pro
    - Gemini Pro Vision
    - Gemini Ultra
    - Gemini 1.5 Pro
    - Gemini 1.5 Flash

    Features:
    - Multimodal understanding (text, images, video)
    - Function/tool calling
    - JSON mode
    - Streaming responses
    - Large context windows (up to 1M tokens)
    - Async operations
    """

    MODEL_INFO = {
        "gemini-pro": {"max_tokens": 8192, "context_window": 32768, "supports_vision": False, "supports_functions": True},
        "gemini-pro-vision": {"max_tokens": 4096, "context_window": 16384, "supports_vision": True, "supports_functions": False},
        "gemini-ultra": {"max_tokens": 8192, "context_window": 32768, "supports_vision": True, "supports_functions": True},
        "gemini-1.5-pro": {"max_tokens": 8192, "context_window": 1000000, "supports_vision": True, "supports_functions": True},
        "gemini-1.5-flash": {"max_tokens": 8192, "context_window": 1000000, "supports_vision": True, "supports_functions": True}
    }

    def __init__(self, model_name: str, api_key: Optional[str] = None, base_url: Optional[str] = None,
                 timeout: Optional[float] = None, max_retries: int = 3, **kwargs) -> None:
        self.model_name = model_name
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.base_url = base_url
        self.timeout = timeout or 300.0
        self.max_retries = max_retries
        self.kwargs = kwargs
        
        if not self.api_key:
            raise AuthenticationException("Google API key not provided")
        
        self._initialize_client()
        self._model_info = None

    def _initialize_client(self):
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.genai = genai
            self.model = genai.GenerativeModel(self.model_name)
        except ImportError:
            raise ImportError("Please install google-generativeai: pip install google-generativeai")

    def get_capabilities(self) -> List[ModelCapability]:
        capabilities = [ModelCapability.TEXT_GENERATION, ModelCapability.CHAT_COMPLETION,
                       ModelCapability.STREAMING, ModelCapability.CODE_GENERATION,
                       ModelCapability.REASONING, ModelCapability.JSON_MODE]
        
        config = self.MODEL_INFO.get(self.model_name, {})
        if config.get("supports_vision", False):
            capabilities.extend([ModelCapability.VISION, ModelCapability.IMAGE_UNDERSTANDING,
                               ModelCapability.MULTIMODAL, ModelCapability.VIDEO_UNDERSTANDING])
        
        if config.get("supports_functions", False):
            capabilities.extend([ModelCapability.FUNCTION_CALLING, ModelCapability.TOOL_USE])
        
        return capabilities

    def supports_capability(self, capability: ModelCapability) -> bool:
        return capability in self.get_capabilities()

    def get_model_info(self) -> Dict[str, Any]:
        if self._model_info is None:
            config = self.MODEL_INFO.get(self.model_name, {"max_tokens": 8192, "context_window": 32768})
            self._model_info = {
                "provider": "google", "name": self.model_name, "version": "latest",
                "max_input_tokens": config["context_window"], "max_output_tokens": config["max_tokens"],
                "context_window": config["context_window"], "supports_streaming": True,
                "supports_functions": config.get("supports_functions", False),
                "supports_vision": config.get("supports_vision", False),
                "modalities": ["text", "image", "video"] if config.get("supports_vision") else ["text"]
            }
        return self._model_info

    def text_generation(self, prompt: str, *, config: Optional[GenerationConfig] = None, **kwargs) -> str:
        try:
            gen_config = self._build_generation_config(config)
            response = self.model.generate_content(prompt, generation_config=gen_config)
            return response.text
        except Exception as e:
            raise self._transform_exception(e)

    async def async_text_generation(self, prompt: str, *, config: Optional[GenerationConfig] = None, **kwargs) -> str:
        try:
            gen_config = self._build_generation_config(config)
            response = await self.model.generate_content_async(prompt, generation_config=gen_config)
            return response.text
        except Exception as e:
            raise self._transform_exception(e)

    def stream_text_generation(self, prompt: str, *, config: Optional[GenerationConfig] = None, **kwargs) -> TextStream:
        try:
            gen_config = self._build_generation_config(config)
            response = self.model.generate_content(prompt, generation_config=gen_config, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            raise self._transform_exception(e)

    async def async_stream_text_generation(self, prompt: str, *, config: Optional[GenerationConfig] = None,
                                          **kwargs) -> AsyncIterator[str]:
        try:
            gen_config = self._build_generation_config(config)
            response = await self.model.generate_content_async(prompt, generation_config=gen_config, stream=True)
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            raise self._transform_exception(e)

    def chat_completion(self, messages: Messages, *, config: Optional[GenerationConfig] = None, **kwargs) -> Dict[str, Any]:
        start_time = time.time()
        try:
            # Convert messages to Gemini format
            chat = self.model.start_chat(history=self._convert_messages_to_history(messages))
            
            # Get last user message
            last_message = messages[-1]["content"] if messages else ""
            
            gen_config = self._build_generation_config(config)
            response = chat.send_message(last_message, generation_config=gen_config)
            
            return self._format_chat_response(response, time.time() - start_time)
        except Exception as e:
            raise self._transform_exception(e)

    async def async_chat_completion(self, messages: Messages, *, config: Optional[GenerationConfig] = None,
                                    **kwargs) -> Dict[str, Any]:
        start_time = time.time()
        try:
            chat = self.model.start_chat(history=self._convert_messages_to_history(messages))
            last_message = messages[-1]["content"] if messages else ""
            
            gen_config = self._build_generation_config(config)
            response = await chat.send_message_async(last_message, generation_config=gen_config)
            
            return self._format_chat_response(response, time.time() - start_time)
        except Exception as e:
            raise self._transform_exception(e)

    def stream_chat_completion(self, messages: Messages, *, config: Optional[GenerationConfig] = None,
                               **kwargs) -> DeltaStream:
        try:
            chat = self.model.start_chat(history=self._convert_messages_to_history(messages))
            last_message = messages[-1]["content"] if messages else ""
            
            gen_config = self._build_generation_config(config)
            response = chat.send_message(last_message, generation_config=gen_config, stream=True)
            
            for chunk in response:
                if chunk.text:
                    yield {"type": "content_delta", "delta": {"content": chunk.text}}
        except Exception as e:
            raise self._transform_exception(e)

    async def async_stream_chat_completion(self, messages: Messages, *, config: Optional[GenerationConfig] = None,
                                          **kwargs) -> AsyncIterator[Dict[str, Any]]:
        try:
            chat = self.model.start_chat(history=self._convert_messages_to_history(messages))
            last_message = messages[-1]["content"] if messages else ""
            
            gen_config = self._build_generation_config(config)
            response = await chat.send_message_async(last_message, generation_config=gen_config, stream=True)
            
            async for chunk in response:
                if chunk.text:
                    yield {"type": "content_delta", "delta": {"content": chunk.text}}
        except Exception as e:
            raise self._transform_exception(e)

    def chat_completion_with_tools(self, messages: Messages, tools: List[ToolDefinition], *,
                                   tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
                                   config: Optional[GenerationConfig] = None, **kwargs) -> Dict[str, Any]:
        if not self.supports_capability(ModelCapability.FUNCTION_CALLING):
            raise CapabilityNotSupportedException("function_calling", self.model_name)
        
        start_time = time.time()
        try:
            # Convert tools to Gemini format
            gemini_tools = self._convert_tools_to_gemini_format(tools)
            
            # Create model with tools
            model_with_tools = self.genai.GenerativeModel(self.model_name, tools=gemini_tools)
            chat = model_with_tools.start_chat(history=self._convert_messages_to_history(messages))
            
            last_message = messages[-1]["content"] if messages else ""
            gen_config = self._build_generation_config(config)
            response = chat.send_message(last_message, generation_config=gen_config)
            
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
            gemini_tools = self._convert_tools_to_gemini_format(tools)
            model_with_tools = self.genai.GenerativeModel(self.model_name, tools=gemini_tools)
            chat = model_with_tools.start_chat(history=self._convert_messages_to_history(messages))
            
            last_message = messages[-1]["content"] if messages else ""
            gen_config = self._build_generation_config(config)
            response = await chat.send_message_async(last_message, generation_config=gen_config)
            
            return self._format_chat_response(response, time.time() - start_time)
        except Exception as e:
            raise self._transform_exception(e)

    def execute_tool_calls(self, tool_calls: List[ToolCall], available_tools: Dict[str, Callable],
                          **kwargs) -> List[ToolResult]:
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})
            
            if tool_name not in available_tools:
                raise ToolNotFoundException(tool_name)
            
            try:
                output = available_tools[tool_name](**tool_args)
                results.append({"tool_call_id": tool_call.get("id", ""), "content": str(output)})
            except Exception as e:
                raise ToolExecutionException(tool_name, str(e))
        return results

    def chat_completion_with_vision(self, messages: Messages, images: List[ImageInput], *,
                                    config: Optional[GenerationConfig] = None, **kwargs) -> Dict[str, Any]:
        if not self.supports_capability(ModelCapability.VISION):
            raise CapabilityNotSupportedException("vision", self.model_name)
        
        start_time = time.time()
        try:
            # Process images
            processed_images = [self._process_image(img) for img in images]
            
            # Combine text and images
            last_message = messages[-1]["content"] if messages else ""
            content_parts = processed_images + [last_message]
            
            gen_config = self._build_generation_config(config)
            response = self.model.generate_content(content_parts, generation_config=gen_config)
            
            return self._format_chat_response(response, time.time() - start_time)
        except Exception as e:
            raise self._transform_exception(e)

    async def async_chat_completion_with_vision(self, messages: Messages, images: List[ImageInput], *,
                                               config: Optional[GenerationConfig] = None, **kwargs) -> Dict[str, Any]:
        if not self.supports_capability(ModelCapability.VISION):
            raise CapabilityNotSupportedException("vision", self.model_name)
        
        start_time = time.time()
        try:
            processed_images = [self._process_image(img) for img in images]
            last_message = messages[-1]["content"] if messages else ""
            content_parts = processed_images + [last_message]
            
            gen_config = self._build_generation_config(config)
            response = await self.model.generate_content_async(content_parts, generation_config=gen_config)
            
            return self._format_chat_response(response, time.time() - start_time)
        except Exception as e:
            raise self._transform_exception(e)

    def embed_text(self, text: Union[str, List[str]], **kwargs) -> Union[Embedding, List[Embedding]]:
        try:
            is_single = isinstance(text, str)
            texts = [text] if is_single else text
            
            embeddings = []
            for t in texts:
                result = self.genai.embed_content(model="models/embedding-001", content=t)
                embeddings.append(result['embedding'])
            
            return embeddings[0] if is_single else embeddings
        except Exception as e:
            raise self._transform_exception(e)

    async def async_embed_text(self, text: Union[str, List[str]], **kwargs) -> Union[Embedding, List[Embedding]]:
        import concurrent.futures
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(executor, lambda: self.embed_text(text, **kwargs))
        return result

    # Unsupported methods
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
        try:
            result = self.model.count_tokens(text)
            return result.total_tokens
        except:
            return len(text) // 4

    def count_message_tokens(self, messages: Messages, **kwargs) -> int:
        text = self.format_messages(messages)
        return self.count_tokens(text)

    def truncate_text(self, text: str, max_tokens: int, **kwargs) -> str:
        current_tokens = self.count_tokens(text)
        if current_tokens <= max_tokens:
            return text
        ratio = max_tokens / current_tokens
        return text[:int(len(text) * ratio * 0.95)]

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
        return response.get("tool_calls", [])

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
        self.model = None

    # Helper methods
    def _build_generation_config(self, config: Optional[GenerationConfig]):
        if not config:
            return None
        
        gen_config = {}
        if config.max_tokens:
            gen_config["max_output_tokens"] = config.max_tokens
        if config.temperature is not None:
            gen_config["temperature"] = config.temperature
        if config.top_p is not None:
            gen_config["top_p"] = config.top_p
        if config.top_k is not None:
            gen_config["top_k"] = config.top_k
        if config.stop_sequences:
            gen_config["stop_sequences"] = config.stop_sequences
        
        return self.genai.GenerationConfig(**gen_config) if gen_config else None

    def _convert_messages_to_history(self, messages: Messages) -> List:
        history = []
        for msg in messages[:-1]:  # Exclude last message
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [msg["content"]]})
        return history

    def _convert_tools_to_gemini_format(self, tools: List[ToolDefinition]) -> List:
        gemini_tools = []
        for tool in tools:
            if tool.get("type") == "function":
                func = tool.get("function", {})
                gemini_tools.append({
                    "name": func.get("name"),
                    "description": func.get("description", ""),
                    "parameters": func.get("parameters", {})
                })
        return gemini_tools

    def _process_image(self, image: ImageInput):
        from PIL import Image as PILImage
        
        if isinstance(image, str):
            if image.startswith("http"):
                import requests
                from io import BytesIO
                response = requests.get(image)
                img = PILImage.open(BytesIO(response.content))
            else:
                img = PILImage.open(image)
        elif isinstance(image, bytes):
            from io import BytesIO
            img = PILImage.open(BytesIO(image))
        else:
            img = image
        
        return img

    def _format_chat_response(self, response, latency: float) -> Dict[str, Any]:
        usage = None
        if hasattr(response, 'usage_metadata'):
            usage = TokenUsage(
                prompt_tokens=response.usage_metadata.prompt_token_count,
                completion_tokens=response.usage_metadata.candidates_token_count,
                total_tokens=response.usage_metadata.total_token_count
            )
        
        metadata = CompletionMetadata(
            model=self.model_name,
            finish_reason="stop",
            usage=usage,
            latency_ms=latency * 1000
        )
        
        # Extract function calls if present
        tool_calls = None
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call'):
                        if not tool_calls:
                            tool_calls = []
                        tool_calls.append({
                            "id": f"call_{len(tool_calls)}",
                            "name": part.function_call.name,
                            "args": dict(part.function_call.args)
                        })
        
        return {
            "content": response.text if hasattr(response, 'text') else "",
            "role": "assistant",
            "tool_calls": tool_calls,
            "metadata": metadata
        }

    def _transform_exception(self, exception: Exception) -> LLMFacadeException:
        error_msg = str(exception).lower()
        if "rate" in error_msg or "quota" in error_msg:
            return RateLimitException(str(exception))
        elif "api key" in error_msg or "authentication" in error_msg:
            return AuthenticationException(str(exception))
        elif "timeout" in error_msg:
            return NetworkException(str(exception))
        elif "safety" in error_msg or "blocked" in error_msg:
            return ContentFilterException(str(exception))
        return LLMFacadeException(str(exception))


def create_google_llm(model_name: str = "gemini-pro", **kwargs) -> GoogleLLMFacade:
    """Create a Google LLM Facade instance."""
    return GoogleLLMFacade(model_name, **kwargs)


__all__ = ['GoogleLLMFacade', 'create_google_llm']
