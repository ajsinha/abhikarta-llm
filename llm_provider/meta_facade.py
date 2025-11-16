"""
Meta LLM Facade Implementation

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
Meta's Llama models including Llama 2, Llama 3, and Code Llama through various APIs.
"""

import os
import json
import time
import asyncio
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


class MetaLLMFacade(LLMFacade):
    """
    Meta implementation of the LLMFacade interface for Llama models.

    Supports Meta's Llama model family:
    - Llama 2 (7B, 13B, 70B)
    - Llama 3 (8B, 70B)
    - Llama 3.1 (8B, 70B, 405B)
    - Code Llama (7B, 13B, 34B, 70B)

    Can be used with:
    - Meta AI API (when available)
    - Together AI
    - Replicate
    - Local deployment (via transformers)

    Features:
    - Chat completion
    - Code generation (Code Llama)
    - Streaming responses
    - Async operations

    Example:
        >>> llm = MetaLLMFacade(
        ...     model_name="meta-llama/Llama-3-70b-chat-hf",
        ...     api_key="...",
        ...     provider="together"
        ... )
        >>> response = llm.chat_completion([
        ...     {"role": "user", "content": "Hello!"}
        ... ])
    """

    MODEL_INFO = {
        "llama-2-7b-chat": {
            "max_tokens": 4096,
            "context_window": 4096,
            "supports_functions": False
        },
        "llama-2-13b-chat": {
            "max_tokens": 4096,
            "context_window": 4096,
            "supports_functions": False
        },
        "llama-2-70b-chat": {
            "max_tokens": 4096,
            "context_window": 4096,
            "supports_functions": False
        },
        "llama-3-8b-instruct": {
            "max_tokens": 8192,
            "context_window": 8192,
            "supports_functions": True
        },
        "llama-3-70b-instruct": {
            "max_tokens": 8192,
            "context_window": 8192,
            "supports_functions": True
        },
        "llama-3.1-8b-instruct": {
            "max_tokens": 16384,
            "context_window": 128000,
            "supports_functions": True
        },
        "llama-3.1-70b-instruct": {
            "max_tokens": 16384,
            "context_window": 128000,
            "supports_functions": True
        },
        "llama-3.1-405b-instruct": {
            "max_tokens": 16384,
            "context_window": 128000,
            "supports_functions": True
        },
        "code-llama-7b-instruct": {
            "max_tokens": 16384,
            "context_window": 16384,
            "supports_functions": False
        },
        "code-llama-34b-instruct": {
            "max_tokens": 16384,
            "context_window": 16384,
            "supports_functions": False
        }
    }

    def __init__(
            self,
            model_name: str,
            api_key: Optional[str] = None,
            base_url: Optional[str] = None,
            timeout: Optional[float] = None,
            max_retries: int = 3,
            provider: str = "together",
            **kwargs
    ) -> None:
        """
        Initialize Meta LLM Facade.

        Args:
            model_name: Llama model identifier
            api_key: API key for the provider
            base_url: Custom API endpoint URL (optional)
            timeout: Request timeout in seconds (default: 300)
            max_retries: Number of retry attempts
            provider: API provider ("together", "replicate", "local")
            **kwargs: Additional configuration
        """
        self.model_name = model_name
        self.api_key = api_key or os.getenv("TOGETHER_API_KEY") or os.getenv("REPLICATE_API_TOKEN")
        self.base_url = base_url
        self.timeout = timeout or 300.0
        self.max_retries = max_retries
        self.provider = provider.lower()
        self.kwargs = kwargs

        # Initialize client
        self._initialize_client()
        self._model_info = None

    def _initialize_client(self):
        """Initialize API client based on provider."""
        if self.provider == "together":
            self._initialize_together_client()
        elif self.provider == "replicate":
            self._initialize_replicate_client()
        elif self.provider == "local":
            self._initialize_local_client()
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _initialize_together_client(self):
        """Initialize Together AI client."""
        try:
            import together
            together.api_key = self.api_key
            self.client = together
        except ImportError:
            raise ImportError("Please install together: pip install together")

    def _initialize_replicate_client(self):
        """Initialize Replicate client."""
        try:
            import replicate
            self.client = replicate.Client(api_token=self.api_key)
        except ImportError:
            raise ImportError("Please install replicate: pip install replicate")

    def _initialize_local_client(self):
        """Initialize local transformers client."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            self.client = None
        except ImportError:
            raise ImportError("Please install transformers: pip install transformers torch")

    def get_capabilities(self) -> List[ModelCapability]:
        """Get list of capabilities."""
        capabilities = [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CHAT_COMPLETION,
            ModelCapability.STREAMING
        ]
        
        # Check if code model
        if "code" in self.model_name.lower():
            capabilities.append(ModelCapability.CODE_GENERATION)
        
        # Llama 3+ supports function calling
        model_key = self._get_model_key()
        config = self.MODEL_INFO.get(model_key, {})
        if config.get("supports_functions", False):
            capabilities.extend([
                ModelCapability.FUNCTION_CALLING,
                ModelCapability.TOOL_USE
            ])
        
        return capabilities

    def supports_capability(self, capability: ModelCapability) -> bool:
        """Check if model supports a specific capability."""
        return capability in self.get_capabilities()

    def get_model_info(self) -> Dict[str, Any]:
        """Get detailed model information."""
        if self._model_info is None:
            model_key = self._get_model_key()
            config = self.MODEL_INFO.get(model_key, {
                "max_tokens": 4096,
                "context_window": 4096,
                "supports_functions": False
            })
            
            self._model_info = {
                "provider": f"meta_{self.provider}",
                "name": self.model_name,
                "version": "latest",
                "max_input_tokens": config["context_window"],
                "max_output_tokens": config["max_tokens"],
                "context_window": config["context_window"],
                "supports_streaming": True,
                "supports_functions": config["supports_functions"],
                "supports_vision": False,
                "modalities": ["text"]
            }
        
        return self._model_info

    def _get_model_key(self) -> str:
        """Extract model key from model name."""
        name_lower = self.model_name.lower()
        for key in self.MODEL_INFO.keys():
            if key in name_lower:
                return key
        return "llama-2-7b-chat"

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
        """Generate text completion."""
        if self.provider == "together":
            return self._together_text_generation(prompt, config, **kwargs)
        elif self.provider == "replicate":
            return self._replicate_text_generation(prompt, config, **kwargs)
        elif self.provider == "local":
            return self._local_text_generation(prompt, config, **kwargs)

    def _together_text_generation(
            self,
            prompt: str,
            config: Optional[GenerationConfig],
            **kwargs
    ) -> str:
        """Generate text using Together AI."""
        try:
            params = {
                "model": self.model_name,
                "prompt": prompt,
                "max_tokens": config.max_tokens if config and config.max_tokens else 512
            }
            
            if config:
                if config.temperature is not None:
                    params["temperature"] = config.temperature
                if config.top_p is not None:
                    params["top_p"] = config.top_p
                if config.stop_sequences:
                    params["stop"] = config.stop_sequences
            
            response = self.client.Complete.create(**params)
            return response["output"]["choices"][0]["text"]
            
        except Exception as e:
            raise self._transform_exception(e)

    def _replicate_text_generation(
            self,
            prompt: str,
            config: Optional[GenerationConfig],
            **kwargs
    ) -> str:
        """Generate text using Replicate."""
        try:
            input_params = {"prompt": prompt}
            
            if config:
                if config.max_tokens:
                    input_params["max_length"] = config.max_tokens
                if config.temperature is not None:
                    input_params["temperature"] = config.temperature
                if config.top_p is not None:
                    input_params["top_p"] = config.top_p
            
            output = self.client.run(self.model_name, input=input_params)
            
            if isinstance(output, list):
                return "".join(output)
            return str(output)
            
        except Exception as e:
            raise self._transform_exception(e)

    def _local_text_generation(
            self,
            prompt: str,
            config: Optional[GenerationConfig],
            **kwargs
    ) -> str:
        """Generate text locally."""
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            
            gen_kwargs = {
                "max_new_tokens": config.max_tokens if config and config.max_tokens else 512,
                "temperature": config.temperature if config and config.temperature else 0.7,
                "top_p": config.top_p if config and config.top_p else 0.9,
                "do_sample": True
            }
            
            outputs = self.model.generate(**inputs, **gen_kwargs)
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove prompt from response
            response = response[len(prompt):]
            return response.strip()
            
        except Exception as e:
            raise self._transform_exception(e)

    async def async_text_generation(
            self,
            prompt: str,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> str:
        """Generate text asynchronously."""
        import concurrent.futures
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                lambda: self.text_generation(prompt, config=config, **kwargs)
            )
        return result

    def stream_text_generation(
            self,
            prompt: str,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> TextStream:
        """Stream text generation."""
        if self.provider == "together":
            try:
                params = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "max_tokens": config.max_tokens if config and config.max_tokens else 512,
                    "stream_tokens": True
                }
                
                if config:
                    if config.temperature is not None:
                        params["temperature"] = config.temperature
                    if config.top_p is not None:
                        params["top_p"] = config.top_p
                
                for chunk in self.client.Complete.create_streaming(**params):
                    if "choices" in chunk and chunk["choices"]:
                        text = chunk["choices"][0].get("text", "")
                        if text:
                            yield text
                            
            except Exception as e:
                raise self._transform_exception(e)
        else:
            # Fallback to non-streaming
            result = self.text_generation(prompt, config=config, **kwargs)
            yield result

    async def async_stream_text_generation(
            self,
            prompt: str,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> AsyncIterator[str]:
        """Stream text asynchronously."""
        for chunk in self.stream_text_generation(prompt, config=config, **kwargs):
            yield chunk

    def chat_completion(
            self,
            messages: Messages,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """Generate chat completion."""
        start_time = time.time()
        
        # Convert messages to prompt
        prompt = self._format_chat_prompt(messages)
        text = self.text_generation(prompt, config=config, **kwargs)
        
        return {
            "content": text,
            "role": "assistant",
            "tool_calls": None,
            "metadata": CompletionMetadata(
                model=self.model_name,
                finish_reason="stop",
                latency_ms=(time.time() - start_time) * 1000
            )
        }

    async def async_chat_completion(
            self,
            messages: Messages,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """Generate chat completion asynchronously."""
        import concurrent.futures
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                lambda: self.chat_completion(messages, config=config, **kwargs)
            )
        return result

    def stream_chat_completion(
            self,
            messages: Messages,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> DeltaStream:
        """Stream chat completion."""
        prompt = self._format_chat_prompt(messages)
        
        for chunk in self.stream_text_generation(prompt, config=config, **kwargs):
            yield {
                "type": "content_delta",
                "delta": {"content": chunk}
            }

    async def async_stream_chat_completion(
            self,
            messages: Messages,
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream chat completion asynchronously."""
        prompt = self._format_chat_prompt(messages)
        
        async for chunk in self.async_stream_text_generation(prompt, config=config, **kwargs):
            yield {
                "type": "content_delta",
                "delta": {"content": chunk}
            }

    def _format_chat_prompt(self, messages: Messages) -> str:
        """Format messages into Llama chat prompt."""
        prompt = "<|begin_of_text|>"
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                prompt += f"<|start_header_id|>system<|end_header_id|>\n\n{content}<|eot_id|>"
            elif role == "user":
                prompt += f"<|start_header_id|>user<|end_header_id|>\n\n{content}<|eot_id|>"
            elif role == "assistant":
                prompt += f"<|start_header_id|>assistant<|end_header_id|>\n\n{content}<|eot_id|>"
        
        prompt += "<|start_header_id|>assistant<|end_header_id|>\n\n"
        return prompt

    # =========================================================================
    # Function/Tool Calling (Limited Support)
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
        """Chat completion with tools (basic support for Llama 3+)."""
        if not self.supports_capability(ModelCapability.FUNCTION_CALLING):
            raise CapabilityNotSupportedException("function_calling", self.model_name)
        
        # Add tools to system message
        system_msg = self._build_tool_system_message(tools)
        enhanced_messages = [{"role": "system", "content": system_msg}] + messages
        
        return self.chat_completion(enhanced_messages, config=config, **kwargs)

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
        if not self.supports_capability(ModelCapability.FUNCTION_CALLING):
            raise CapabilityNotSupportedException("function_calling", self.model_name)
        
        system_msg = self._build_tool_system_message(tools)
        enhanced_messages = [{"role": "system", "content": system_msg}] + messages
        
        return await self.async_chat_completion(enhanced_messages, config=config, **kwargs)

    def _build_tool_system_message(self, tools: List[ToolDefinition]) -> str:
        """Build system message with tool definitions."""
        tools_desc = "You have access to the following tools:\n\n"
        
        for tool in tools:
            if tool.get("type") == "function":
                func = tool.get("function", {})
                tools_desc += f"- {func.get('name')}: {func.get('description', '')}\n"
        
        tools_desc += "\nTo use a tool, respond with: TOOL_CALL: {tool_name}({arguments})"
        return tools_desc

    def execute_tool_calls(
            self,
            tool_calls: List[ToolCall],
            available_tools: Dict[str, Callable],
            **kwargs
    ) -> List[ToolResult]:
        """Execute tool calls."""
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("arguments", {})
            
            if tool_name not in available_tools:
                raise ToolNotFoundException(tool_name)
            
            try:
                func = available_tools[tool_name]
                output = func(**tool_args)
                
                results.append({
                    "tool_call_id": tool_call.get("id", ""),
                    "content": str(output)
                })
                
            except Exception as e:
                raise ToolExecutionException(tool_name, str(e))
        
        return results

    # =========================================================================
    # Not Supported Methods
    # =========================================================================

    def chat_completion_with_vision(
            self,
            messages: Messages,
            images: List[ImageInput],
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """Vision not supported."""
        raise CapabilityNotSupportedException("vision", self.model_name)

    async def async_chat_completion_with_vision(
            self,
            messages: Messages,
            images: List[ImageInput],
            *,
            config: Optional[GenerationConfig] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """Vision not supported."""
        raise CapabilityNotSupportedException("vision", self.model_name)

    def embed_text(
            self,
            text: Union[str, List[str]],
            **kwargs
    ) -> Union[Embedding, List[Embedding]]:
        """Embeddings not supported."""
        raise CapabilityNotSupportedException("embeddings", self.model_name)

    async def async_embed_text(
            self,
            text: Union[str, List[str]],
            **kwargs
    ) -> Union[Embedding, List[Embedding]]:
        """Embeddings not supported."""
        raise CapabilityNotSupportedException("embeddings", self.model_name)

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

    def moderate_content(
            self,
            content: Union[str, List[str]],
            **kwargs
    ) -> Union[ModerationResult, List[ModerationResult]]:
        """Moderation not available."""
        if isinstance(content, str):
            return {"flagged": False, "categories": {}, "scores": {}}
        return [{"flagged": False, "categories": {}, "scores": {}} for _ in content]

    def retrieve_documents(self, query: str, **kwargs) -> RetrievalResult:
        """RAG not directly supported."""
        raise CapabilityNotSupportedException("rag", self.model_name)

    def batch_generate(self, prompts: List[str], **kwargs) -> List[str]:
        """Batch generation."""
        return [self.text_generation(p, **kwargs) for p in prompts]

    def batch_embed(self, texts: List[str], **kwargs) -> List[Embedding]:
        """Batch embedding not supported."""
        raise CapabilityNotSupportedException("embeddings", self.model_name)

    def create_fine_tuning_job(self, training_file: str, **kwargs) -> str:
        """Fine-tuning not available via API."""
        raise NotImplementedError("Fine-tuning not available via API")

    def get_fine_tuning_status(self, job_id: str, **kwargs) -> Dict[str, Any]:
        """Fine-tuning status not available."""
        raise NotImplementedError("Fine-tuning status not available")

    # =========================================================================
    # Token Management
    # =========================================================================

    def count_tokens(self, text: str, **kwargs) -> int:
        """Count tokens."""
        if self.provider == "local" and self.tokenizer:
            return len(self.tokenizer.encode(text))
        return len(text) // 4

    def count_message_tokens(self, messages: Messages, **kwargs) -> int:
        """Count tokens in messages."""
        prompt = self._format_chat_prompt(messages)
        return self.count_tokens(prompt)

    def truncate_text(self, text: str, max_tokens: int, **kwargs) -> str:
        """Truncate text."""
        if self.provider == "local" and self.tokenizer:
            tokens = self.tokenizer.encode(text)
            if len(tokens) > max_tokens:
                tokens = tokens[:max_tokens]
                return self.tokenizer.decode(tokens)
        
        estimated_chars = max_tokens * 4
        return text[:estimated_chars]

    def get_context_window(self) -> int:
        """Get context window size."""
        return self.get_model_info()["context_window"]

    def get_max_output_tokens(self) -> int:
        """Get max output tokens."""
        return self.get_model_info()["max_output_tokens"]

    # =========================================================================
    # Observability & Utility
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
        """Log request."""
        pass

    def get_usage_stats(self, period: str = "day", **kwargs) -> Dict[str, Any]:
        """Get usage stats."""
        return {}

    def format_messages(self, messages: Messages, **kwargs) -> str:
        """Format messages."""
        return self._format_chat_prompt(messages)

    def parse_tool_calls(self, response: Dict[str, Any], **kwargs) -> List[ToolCall]:
        """Parse tool calls from response."""
        content = response.get("content", "")
        
        # Simple parsing for TOOL_CALL format
        tool_calls = []
        if "TOOL_CALL:" in content:
            # Parse tool call format: TOOL_CALL: tool_name({args})
            import re
            pattern = r'TOOL_CALL:\s*(\w+)\((.*?)\)'
            matches = re.finditer(pattern, content)
            
            for match in matches:
                tool_name = match.group(1)
                args_str = match.group(2)
                
                try:
                    args = json.loads(f"{{{args_str}}}")
                except:
                    args = {}
                
                tool_calls.append({
                    "id": f"call_{len(tool_calls)}",
                    "name": tool_name,
                    "arguments": args
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
        
        return (len(errors) == 0, errors)

    def health_check(self, **kwargs) -> bool:
        """Health check."""
        try:
            self.text_generation("Hi", config=GenerationConfig(max_tokens=5))
            return True
        except:
            return False

    def close(self) -> None:
        """Close connections."""
        self.client = None
        self.model = None
        self.tokenizer = None

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _transform_exception(self, exception: Exception) -> LLMFacadeException:
        """Transform exceptions."""
        error_msg = str(exception).lower()
        
        if "rate" in error_msg or "429" in error_msg:
            return RateLimitException(str(exception))
        elif "auth" in error_msg or "401" in error_msg:
            return AuthenticationException(str(exception))
        elif "timeout" in error_msg:
            return NetworkException(str(exception))
        else:
            return LLMFacadeException(str(exception))


def create_meta_llm(
        model_name: str = "meta-llama/Llama-3-70b-chat-hf",
        provider: str = "together",
        **kwargs
) -> MetaLLMFacade:
    """
    Create a Meta LLM Facade instance.

    Args:
        model_name: Llama model identifier
        provider: API provider ("together", "replicate", "local")
        **kwargs: Additional configuration

    Returns:
        Configured MetaLLMFacade instance

    Example:
        >>> llm = create_meta_llm(
        ...     "meta-llama/Llama-3-70b-chat-hf",
        ...     provider="together"
        ... )
    """
    return MetaLLMFacade(model_name, provider=provider, **kwargs)


__all__ = ['MetaLLMFacade', 'create_meta_llm']
