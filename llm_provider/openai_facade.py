"""
OpenAI LLM Facade Implementation

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
OpenAI models including GPT-4, GPT-3.5, DALL-E, Whisper, and embeddings.
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


class OpenAILLMFacade(LLMFacade):
    """
    OpenAI implementation of the LLMFacade interface.

    Supports the full OpenAI model suite:
    - GPT-4 and GPT-4 Turbo (text and vision)
    - GPT-3.5 Turbo
    - DALL-E 2 and 3 (image generation)
    - Whisper (audio transcription)
    - Text embeddings (ada-002, embedding-3)
    - Moderation API

    Features:
    - Function/tool calling
    - Vision capabilities (GPT-4V)
    - JSON mode and structured outputs
    - Streaming responses
    - Async operations
    - Fine-tuning support

    Example:
        >>> llm = OpenAILLMFacade(
        ...     model_name="gpt-4-turbo-preview",
        ...     api_key="sk-..."
        ... )
        >>> response = llm.chat_completion([
        ...     {"role": "user", "content": "Hello!"}
        ... ])
    """

    # Model configurations
    MODEL_INFO = {
        "gpt-4-turbo-preview": {
            "max_tokens": 4096,
            "context_window": 128000,
            "supports_vision": True,
            "supports_functions": True,
            "supports_json": True,
            "cost_per_1k_input": 0.01,
            "cost_per_1k_output": 0.03
        },
        "gpt-4-turbo": {
            "max_tokens": 4096,
            "context_window": 128000,
            "supports_vision": True,
            "supports_functions": True,
            "supports_json": True,
            "cost_per_1k_input": 0.01,
            "cost_per_1k_output": 0.03
        },
        "gpt-4": {
            "max_tokens": 8192,
            "context_window": 8192,
            "supports_vision": False,
            "supports_functions": True,
            "supports_json": True,
            "cost_per_1k_input": 0.03,
            "cost_per_1k_output": 0.06
        },
        "gpt-4-32k": {
            "max_tokens": 32768,
            "context_window": 32768,
            "supports_vision": False,
            "supports_functions": True,
            "supports_json": True,
            "cost_per_1k_input": 0.06,
            "cost_per_1k_output": 0.12
        },
        "gpt-3.5-turbo": {
            "max_tokens": 4096,
            "context_window": 16385,
            "supports_vision": False,
            "supports_functions": True,
            "supports_json": True,
            "cost_per_1k_input": 0.0005,
            "cost_per_1k_output": 0.0015
        },
        "gpt-3.5-turbo-16k": {
            "max_tokens": 16384,
            "context_window": 16384,
            "supports_vision": False,
            "supports_functions": True,
            "supports_json": True,
            "cost_per_1k_input": 0.003,
            "cost_per_1k_output": 0.004
        }
    }

    def __init__(
            self,
            model_name: str,
            api_key: Optional[str] = None,
            base_url: Optional[str] = None,
            timeout: Optional[float] = None,
            max_retries: int = 3,
            organization: Optional[str] = None,
            **kwargs
    ) -> None:
        """
        Initialize OpenAI LLM Facade.

        Args:
            model_name: OpenAI model identifier (e.g., "gpt-4-turbo-preview")
            api_key: OpenAI API key (reads from OPENAI_API_KEY env var if None)
            base_url: Custom API endpoint URL (optional)
            timeout: Request timeout in seconds (default: 600)
            max_retries: Number of retry attempts for failed requests
            organization: OpenAI organization ID (optional)
            **kwargs: Additional configuration
        """
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url
        self.timeout = timeout or 600.0
        self.max_retries = max_retries
        self.organization = organization or os.getenv("OPENAI_ORG_ID")
        self.kwargs = kwargs

        if not self.api_key:
            raise AuthenticationException("OpenAI API key not provided")

        # Initialize client
        self._initialize_client()

        # Model info cache
        self._model_info = None

    def _initialize_client(self):
        """Initialize OpenAI API client."""
        try:
            import openai
            
            client_kwargs = {
                "api_key": self.api_key,
                "max_retries": self.max_retries,
                "timeout": self.timeout
            }
            
            if self.base_url:
                client_kwargs["base_url"] = self.base_url
            
            if self.organization:
                client_kwargs["organization"] = self.organization
            
            self.client = openai.OpenAI(**client_kwargs)
            self.async_client = openai.AsyncOpenAI(**client_kwargs)
            
        except ImportError:
            raise ImportError(
                "Please install openai: pip install openai"
            )
        except Exception as e:
            raise AuthenticationException(f"Failed to initialize OpenAI client: {e}")

    def get_capabilities(self) -> List[ModelCapability]:
        """Get list of capabilities supported by the model."""
        capabilities = [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CHAT_COMPLETION,
            ModelCapability.STREAMING,
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING
        ]
        
        model_config = self.MODEL_INFO.get(self.model_name, {})
        
        if model_config.get("supports_functions", False):
            capabilities.extend([
                ModelCapability.FUNCTION_CALLING,
                ModelCapability.TOOL_USE
            ])
        
        if model_config.get("supports_json", False):
            capabilities.append(ModelCapability.JSON_MODE)
        
        if model_config.get("supports_vision", False):
            capabilities.extend([
                ModelCapability.VISION,
                ModelCapability.IMAGE_UNDERSTANDING,
                ModelCapability.MULTIMODAL
            ])
        
        # Add capabilities for special models
        if "dall-e" in self.model_name.lower():
            capabilities.append(ModelCapability.IMAGE_GENERATION)
        
        if "whisper" in self.model_name.lower():
            capabilities.append(ModelCapability.AUDIO_TRANSCRIPTION)
        
        if "embedding" in self.model_name.lower() or "ada" in self.model_name.lower():
            capabilities.append(ModelCapability.EMBEDDINGS)
        
        return capabilities

    def supports_capability(self, capability: ModelCapability) -> bool:
        """Check if model supports a specific capability."""
        return capability in self.get_capabilities()

    def get_model_info(self) -> Dict[str, Any]:
        """Get detailed model information."""
        if self._model_info is None:
            config = self.MODEL_INFO.get(self.model_name, {
                "max_tokens": 4096,
                "context_window": 8192,
                "supports_vision": False,
                "supports_functions": False,
                "supports_json": False,
                "cost_per_1k_input": 0.0,
                "cost_per_1k_output": 0.0
            })
            
            self._model_info = {
                "provider": "openai",
                "name": self.model_name,
                "version": "latest",
                "max_input_tokens": config["context_window"],
                "max_output_tokens": config["max_tokens"],
                "context_window": config["context_window"],
                "supports_streaming": True,
                "supports_functions": config["supports_functions"],
                "supports_vision": config["supports_vision"],
                "cost_per_1k_input_tokens": config["cost_per_1k_input"],
                "cost_per_1k_output_tokens": config["cost_per_1k_output"],
                "modalities": ["text", "image"] if config["supports_vision"] else ["text"]
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
            messages = [{"role": "user", "content": prompt}]
            params = self._build_chat_params(messages, config, **kwargs)
            
            response = self.client.chat.completions.create(**params)
            return response.choices[0].message.content
            
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
            params = self._build_chat_params(messages, config, **kwargs)
            
            response = await self.async_client.chat.completions.create(**params)
            return response.choices[0].message.content
            
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
            params = self._build_chat_params(messages, config, **kwargs)
            params["stream"] = True
            
            stream = self.client.chat.completions.create(**params)
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
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
            params = self._build_chat_params(messages, config, **kwargs)
            params["stream"] = True
            
            stream = await self.async_client.chat.completions.create(**params)
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
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
            params = self._build_chat_params(messages, config, **kwargs)
            response = self.client.chat.completions.create(**params)
            
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
            params = self._build_chat_params(messages, config, **kwargs)
            response = await self.async_client.chat.completions.create(**params)
            
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
            params = self._build_chat_params(messages, config, **kwargs)
            params["stream"] = True
            
            stream = self.client.chat.completions.create(**params)
            
            for chunk in stream:
                delta = chunk.choices[0].delta
                yield {
                    "type": "content_delta",
                    "delta": {
                        "content": delta.content if delta.content else None,
                        "tool_calls": delta.tool_calls if hasattr(delta, 'tool_calls') else None
                    }
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
            params = self._build_chat_params(messages, config, **kwargs)
            params["stream"] = True
            
            stream = await self.async_client.chat.completions.create(**params)
            
            async for chunk in stream:
                delta = chunk.choices[0].delta
                yield {
                    "type": "content_delta",
                    "delta": {
                        "content": delta.content if delta.content else None,
                        "tool_calls": delta.tool_calls if hasattr(delta, 'tool_calls') else None
                    }
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

    def execute_tool_calls(
            self,
            tool_calls: List[ToolCall],
            available_tools: Dict[str, Callable],
            **kwargs
    ) -> List[ToolResult]:
        """Execute tool calls and return results."""
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
            processed_messages = self._embed_images_in_messages(messages, images)
            params = self._build_chat_params(processed_messages, config, **kwargs)
            
            response = self.client.chat.completions.create(**params)
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
            params = self._build_chat_params(processed_messages, config, **kwargs)
            
            response = await self.async_client.chat.completions.create(**params)
            return self._format_chat_response(response, time.time() - start_time)
            
        except Exception as e:
            raise self._transform_exception(e)

    # =========================================================================
    # Embeddings
    # =========================================================================

    def embed_text(
            self,
            text: Union[str, List[str]],
            **kwargs
    ) -> Union[Embedding, List[Embedding]]:
        """Generate embeddings for text."""
        try:
            is_single = isinstance(text, str)
            texts = [text] if is_single else text
            
            response = self.client.embeddings.create(
                model=kwargs.get("embedding_model", "text-embedding-ada-002"),
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            return embeddings[0] if is_single else embeddings
            
        except Exception as e:
            raise self._transform_exception(e)

    async def async_embed_text(
            self,
            text: Union[str, List[str]],
            **kwargs
    ) -> Union[Embedding, List[Embedding]]:
        """Generate embeddings asynchronously."""
        try:
            is_single = isinstance(text, str)
            texts = [text] if is_single else text
            
            response = await self.async_client.embeddings.create(
                model=kwargs.get("embedding_model", "text-embedding-ada-002"),
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            return embeddings[0] if is_single else embeddings
            
        except Exception as e:
            raise self._transform_exception(e)

    # =========================================================================
    # Image Generation
    # =========================================================================

    def generate_image(
            self,
            prompt: str,
            *,
            size: str = "1024x1024",
            quality: str = "standard",
            n: int = 1,
            **kwargs
    ) -> ImageOutput:
        """Generate image using DALL-E."""
        try:
            response = self.client.images.generate(
                model=kwargs.get("image_model", "dall-e-3"),
                prompt=prompt,
                size=size,
                quality=quality,
                n=n
            )
            
            # Return URL or base64 data
            if n == 1:
                return response.data[0].url
            return [img.url for img in response.data]
            
        except Exception as e:
            raise self._transform_exception(e)

    def edit_image(
            self,
            image: ImageInput,
            prompt: str,
            *,
            mask: Optional[ImageInput] = None,
            **kwargs
    ) -> ImageOutput:
        """Edit image using DALL-E."""
        try:
            # Process image file
            if isinstance(image, str):
                with open(image, 'rb') as f:
                    image_file = f
                    mask_file = open(mask, 'rb') if mask else None
                    
                    response = self.client.images.edit(
                        image=image_file,
                        prompt=prompt,
                        mask=mask_file
                    )
                    
                    if mask_file:
                        mask_file.close()
            else:
                # Handle bytes or PIL Image
                response = self.client.images.edit(
                    image=image,
                    prompt=prompt,
                    mask=mask
                )
            
            return response.data[0].url
            
        except Exception as e:
            raise self._transform_exception(e)

    # =========================================================================
    # Audio
    # =========================================================================

    def transcribe_audio(
            self,
            audio: Union[bytes, str],
            **kwargs
    ) -> str:
        """Transcribe audio using Whisper."""
        try:
            if isinstance(audio, str):
                with open(audio, 'rb') as audio_file:
                    response = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
            else:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio
                )
            
            return response.text
            
        except Exception as e:
            raise self._transform_exception(e)

    def generate_audio(
            self,
            text: str,
            *,
            voice: str = "alloy",
            **kwargs
    ) -> bytes:
        """Generate audio using TTS."""
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            
            return response.content
            
        except Exception as e:
            raise self._transform_exception(e)

    # =========================================================================
    # Moderation
    # =========================================================================

    def moderate_content(
            self,
            content: Union[str, List[str]],
            **kwargs
    ) -> Union[ModerationResult, List[ModerationResult]]:
        """Moderate content using OpenAI moderation API."""
        try:
            is_single = isinstance(content, str)
            contents = [content] if is_single else content
            
            response = self.client.moderations.create(input=contents)
            
            results = []
            for result in response.results:
                results.append({
                    "flagged": result.flagged,
                    "categories": result.categories.model_dump(),
                    "scores": result.category_scores.model_dump()
                })
            
            return results[0] if is_single else results
            
        except Exception as e:
            raise self._transform_exception(e)

    # =========================================================================
    # Token Management
    # =========================================================================

    def count_tokens(self, text: str, **kwargs) -> int:
        """Count tokens in text."""
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model_name)
            return len(encoding.encode(text))
        except:
            # Fallback estimation
            return len(text) // 4

    def count_message_tokens(self, messages: Messages, **kwargs) -> int:
        """Count tokens in messages."""
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model_name)
            
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # Every message has overhead
                for key, value in message.items():
                    if isinstance(value, str):
                        num_tokens += len(encoding.encode(value))
            
            num_tokens += 2  # Assistant reply priming
            return num_tokens
        except:
            return len(json.dumps(messages)) // 4

    def truncate_text(
            self,
            text: str,
            max_tokens: int,
            **kwargs
    ) -> str:
        """Truncate text to fit within token limit."""
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model_name)
            tokens = encoding.encode(text)
            
            if len(tokens) <= max_tokens:
                return text
            
            truncated_tokens = tokens[:max_tokens]
            return encoding.decode(truncated_tokens)
        except:
            # Fallback
            estimated_chars = max_tokens * 4
            return text[:estimated_chars]

    def get_context_window(self) -> int:
        """Get maximum context window size."""
        return self.get_model_info()["context_window"]

    def get_max_output_tokens(self) -> int:
        """Get maximum output tokens."""
        return self.get_model_info()["max_output_tokens"]

    # =========================================================================
    # Batch and Fine-tuning
    # =========================================================================

    def batch_generate(
            self,
            prompts: List[str],
            *,
            config: Optional[GenerationConfig] = None,
            show_progress: bool = False,
            **kwargs
    ) -> List[str]:
        """Process multiple prompts in batch."""
        results = []
        
        iterator = prompts
        if show_progress:
            try:
                from tqdm import tqdm
                iterator = tqdm(prompts)
            except ImportError:
                pass
        
        for prompt in iterator:
            result = self.text_generation(prompt, config=config, **kwargs)
            results.append(result)
        
        return results

    def batch_embed(
            self,
            texts: List[str],
            *,
            batch_size: int = 100,
            **kwargs
    ) -> List[Embedding]:
        """Generate embeddings in batch."""
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.embed_text(batch, **kwargs)
            embeddings.extend(batch_embeddings)
        
        return embeddings

    def create_fine_tuning_job(
            self,
            training_file: str,
            *,
            validation_file: Optional[str] = None,
            hyperparameters: Optional[Dict[str, Any]] = None,
            **kwargs
    ) -> str:
        """Create fine-tuning job."""
        try:
            params = {
                "training_file": training_file,
                "model": self.model_name
            }
            
            if validation_file:
                params["validation_file"] = validation_file
            
            if hyperparameters:
                params["hyperparameters"] = hyperparameters
            
            response = self.client.fine_tuning.jobs.create(**params)
            return response.id
            
        except Exception as e:
            raise self._transform_exception(e)

    def get_fine_tuning_status(self, job_id: str, **kwargs) -> Dict[str, Any]:
        """Get fine-tuning status."""
        try:
            job = self.client.fine_tuning.jobs.retrieve(job_id)
            
            return {
                "id": job.id,
                "status": job.status,
                "model": job.model,
                "fine_tuned_model": job.fine_tuned_model,
                "created_at": job.created_at,
                "finished_at": job.finished_at,
                "error": job.error
            }
            
        except Exception as e:
            raise self._transform_exception(e)

    # =========================================================================
    # Not Implemented
    # =========================================================================

    def retrieve_documents(self, query: str, **kwargs) -> RetrievalResult:
        """Document retrieval not directly supported."""
        raise CapabilityNotSupportedException("rag", self.model_name)

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
                formatted += f"System: {content}\n\n"
            elif role == "user":
                formatted += f"User: {content}\n\n"
            elif role == "assistant":
                formatted += f"Assistant: {content}\n\n"
        
        return formatted

    def parse_tool_calls(self, response: Dict[str, Any], **kwargs) -> List[ToolCall]:
        """Parse tool calls from response."""
        metadata = response.get("metadata", {})
        return metadata.get("tool_calls", [])

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
        if temperature < 0 or temperature > 2:
            errors.append("temperature must be between 0.0 and 2.0")
        
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

    def _build_chat_params(
            self,
            messages: Messages,
            config: Optional[GenerationConfig],
            **kwargs
    ) -> Dict[str, Any]:
        """Build parameters for OpenAI chat completion."""
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
            if config.frequency_penalty is not None:
                params["frequency_penalty"] = config.frequency_penalty
            if config.presence_penalty is not None:
                params["presence_penalty"] = config.presence_penalty
            if config.stop_sequences:
                params["stop"] = config.stop_sequences
            if config.seed is not None:
                params["seed"] = config.seed
            
            # Handle response format
            if config.response_format:
                if config.response_format == ResponseFormat.JSON:
                    params["response_format"] = {"type": "json_object"}
        
        params.update(kwargs)
        return params

    def _format_chat_response(
            self,
            response,
            latency: float
    ) -> Dict[str, Any]:
        """Format OpenAI response to standard format."""
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

    def _embed_images_in_messages(
            self,
            messages: Messages,
            images: List[ImageInput]
    ) -> Messages:
        """Embed images into messages for vision models."""
        processed_messages = []
        image_idx = 0
        
        for msg in messages:
            if msg["role"] == "user" and image_idx < len(images):
                content = []
                
                # Add text
                if isinstance(msg["content"], str):
                    content.append({"type": "text", "text": msg["content"]})
                
                # Add images
                for img in images[image_idx:]:
                    img_data = self._process_image(img)
                    content.append(img_data)
                
                processed_messages.append({
                    "role": "user",
                    "content": content
                })
                image_idx = len(images)
            else:
                processed_messages.append(msg)
        
        return processed_messages

    def _process_image(self, image: ImageInput) -> Dict[str, Any]:
        """Process image into OpenAI format."""
        if isinstance(image, str):
            if image.startswith("http"):
                # URL
                return {
                    "type": "image_url",
                    "image_url": {"url": image}
                }
            else:
                # File path
                with open(image, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode()
                return {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                }
        elif isinstance(image, bytes):
            image_data = base64.b64encode(image).decode()
            return {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
            }
        else:
            # PIL Image
            from io import BytesIO
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            image_data = base64.b64encode(buffer.getvalue()).decode()
            return {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{image_data}"}
            }

    def _transform_exception(self, exception: Exception) -> LLMFacadeException:
        """Transform OpenAI exceptions to facade exceptions."""
        error_msg = str(exception).lower()
        
        if "rate" in error_msg or "429" in error_msg:
            return RateLimitException(str(exception))
        elif "authentication" in error_msg or "401" in error_msg:
            return AuthenticationException(str(exception))
        elif "context" in error_msg or "maximum context" in error_msg:
            return ContextLengthExceededException(0, 0)
        elif "timeout" in error_msg:
            return NetworkException(str(exception))
        elif "content filter" in error_msg or "content_filter" in error_msg:
            return ContentFilterException(str(exception))
        else:
            return LLMFacadeException(str(exception))


def create_openai_llm(
        model_name: str = "gpt-4-turbo-preview",
        **kwargs
) -> OpenAILLMFacade:
    """
    Create an OpenAI LLM Facade instance.

    Args:
        model_name: OpenAI model identifier
        **kwargs: Additional configuration

    Returns:
        Configured OpenAILLMFacade instance

    Example:
        >>> llm = create_openai_llm("gpt-4-turbo-preview")
    """
    return OpenAILLMFacade(model_name, **kwargs)


__all__ = ['OpenAILLMFacade', 'create_openai_llm']
