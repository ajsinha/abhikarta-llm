"""
OpenAI LLM Facade Implementation

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
This module provides a concrete implementation of the LLMFacade interface for OpenAI models
including GPT-4, GPT-4 Turbo, GPT-3.5, DALL-E, Whisper, and embeddings models.
"""

import os
from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator
import time

from .llm_facade_base import LLMFacadeBase
from .llm_facade import (
    ModelCapability,
    GenerationConfig,
    TokenUsage,
    CompletionMetadata,
    Messages,
    TextStream,
    ToolDefinition,
    ToolCall,
    ImageInput,
    Embedding,
    AuthenticationException,
    NetworkException
)


class OpenAIFacade(LLMFacadeBase):
    """
    OpenAI implementation of the LLMFacade interface.
    
    Supports:
    - GPT-4 (all variants including Turbo, Vision, and O1)
    - GPT-3.5 Turbo
    - DALL-E 2 & 3 for image generation
    - Whisper for audio transcription
    - Text-to-Speech (TTS)
    - Embeddings (text-embedding-ada-002, text-embedding-3-small/large)
    - Function calling and tool use
    - Vision capabilities (GPT-4 Vision, GPT-4 Turbo with Vision)
    - JSON mode and structured outputs
    - Streaming support for chat and completions
    
    Example:
        >>> from openai_facade import OpenAIFacade
        >>> llm = OpenAIFacade(model_name="gpt-4", api_key="sk-...")
        >>> response = llm.chat_completion([
        ...     {"role": "user", "content": "Explain quantum computing"}
        ... ])
        >>> print(response["content"])
    """
    
    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        organization: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        **kwargs
    ):
        """
        Initialize OpenAI facade.
        
        Args:
            model_name: Model identifier (e.g., "gpt-4", "gpt-3.5-turbo")
            api_key: OpenAI API key (reads from OPENAI_API_KEY env var if None)
            base_url: Custom API endpoint (default: https://api.openai.com/v1)
            organization: OpenAI organization ID
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts
            **kwargs: Additional configuration
        """
        super().__init__(
            provider_name="openai",
            model_name=model_name,
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url=base_url or "https://api.openai.com/v1",
            timeout=timeout,
            max_retries=max_retries,
            **kwargs
        )
        
        self.organization = organization or os.getenv("OPENAI_ORG_ID")
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client."""
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                organization=self.organization,
                timeout=self.timeout,
                max_retries=self.max_retries
            )
        except ImportError:
            raise ImportError("Please install openai: pip install openai")
        except Exception as e:
            raise AuthenticationException(f"Failed to initialize OpenAI client: {e}")
    
    def chat_completion(
        self,
        messages: Messages,
        tools: Optional[List[ToolDefinition]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate chat completion using OpenAI API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            tools: Optional list of tool/function definitions
            tool_choice: Tool selection strategy ("auto", "none", or specific tool)
            config: Generation configuration
            **kwargs: Additional parameters
        
        Returns:
            Dictionary containing:
                - content: Response text
                - role: "assistant"
                - finish_reason: Completion reason
                - usage: Token usage statistics
                - tool_calls: List of tool calls (if any)
        """
        self._check_capability(ModelCapability.CHAT_COMPLETION)
        
        start_time = time.time()
        
        try:
            # Build request parameters
            params = {
                "model": self.model_name,
                "messages": messages
            }
            
            # Add generation config
            if config:
                config_dict = config.to_dict()
                if config_dict.get("max_tokens"):
                    params["max_tokens"] = config_dict["max_tokens"]
                if config_dict.get("temperature") is not None:
                    params["temperature"] = config_dict["temperature"]
                if config_dict.get("top_p") is not None:
                    params["top_p"] = config_dict["top_p"]
                if config_dict.get("frequency_penalty") is not None:
                    params["frequency_penalty"] = config_dict["frequency_penalty"]
                if config_dict.get("presence_penalty") is not None:
                    params["presence_penalty"] = config_dict["presence_penalty"]
                if config_dict.get("stop_sequences"):
                    params["stop"] = config_dict["stop_sequences"]
                if config_dict.get("seed") is not None:
                    params["seed"] = config_dict["seed"]
                if config_dict.get("response_format"):
                    params["response_format"] = {"type": config_dict["response_format"].value}
            
            # Add tools if provided
            if tools:
                params["tools"] = tools
                if tool_choice:
                    params["tool_choice"] = tool_choice
            
            # Add any additional kwargs
            params.update(kwargs)
            
            # Make API call
            response = self.client.chat.completions.create(**params)
            
            # Extract response data
            message = response.choices[0].message
            
            result = {
                "content": message.content or "",
                "role": message.role,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            # Add tool calls if present
            if message.tool_calls:
                result["tool_calls"] = [
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
            
            # Log request
            latency = (time.time() - start_time) * 1000
            self.log_request("chat_completion", messages, result, latency)
            
            return result
            
        except Exception as e:
            self._handle_error(e)
    
    def completion(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> str:
        """
        Generate text completion.
        
        Args:
            prompt: Input prompt text
            config: Generation configuration
            **kwargs: Additional parameters
        
        Returns:
            Generated text completion
        """
        # Use chat completion for GPT-3.5 and GPT-4 models
        if "gpt-" in self.model_name.lower():
            response = self.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                config=config,
                **kwargs
            )
            return response["content"]
        
        # For completion models (legacy)
        try:
            params = {
                "model": self.model_name,
                "prompt": prompt
            }
            
            if config:
                config_dict = config.to_dict()
                if config_dict.get("max_tokens"):
                    params["max_tokens"] = config_dict["max_tokens"]
                if config_dict.get("temperature") is not None:
                    params["temperature"] = config_dict["temperature"]
            
            response = self.client.completions.create(**params)
            return response.choices[0].text
            
        except Exception as e:
            self._handle_error(e)
    
    def stream_chat_completion(
        self,
        messages: Messages,
        tools: Optional[List[ToolDefinition]] = None,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> Iterator[str]:
        """
        Stream chat completion responses.
        
        Args:
            messages: List of message dictionaries
            tools: Optional tool definitions
            config: Generation configuration
            **kwargs: Additional parameters
        
        Yields:
            Text chunks as they are generated
        """
        self._check_capability(ModelCapability.STREAMING)
        
        try:
            params = {
                "model": self.model_name,
                "messages": messages,
                "stream": True
            }
            
            if config:
                config_dict = config.to_dict()
                if config_dict.get("max_tokens"):
                    params["max_tokens"] = config_dict["max_tokens"]
                if config_dict.get("temperature") is not None:
                    params["temperature"] = config_dict["temperature"]
            
            if tools:
                params["tools"] = tools
            
            stream = self.client.chat.completions.create(**params)
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            self._handle_error(e)
    
    def get_embeddings(
        self,
        texts: Union[str, List[str]],
        model: Optional[str] = None,
        **kwargs
    ) -> List[Embedding]:
        """
        Generate embeddings for text(s).
        
        Args:
            texts: Single text or list of texts
            model: Embedding model name (default: text-embedding-3-small)
            **kwargs: Additional parameters
        
        Returns:
            List of embedding vectors
        """
        self._check_capability(ModelCapability.EMBEDDINGS)
        
        if isinstance(texts, str):
            texts = [texts]
        
        embedding_model = model or "text-embedding-3-small"
        
        try:
            response = self.client.embeddings.create(
                model=embedding_model,
                input=texts,
                **kwargs
            )
            
            return [item.embedding for item in response.data]
            
        except Exception as e:
            self._handle_error(e)
    
    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1,
        **kwargs
    ) -> List[str]:
        """
        Generate images using DALL-E.
        
        Args:
            prompt: Text description of desired image
            size: Image size ("1024x1024", "1792x1024", "1024x1792")
            quality: Image quality ("standard" or "hd")
            n: Number of images to generate
            **kwargs: Additional parameters
        
        Returns:
            List of image URLs
        """
        self._check_capability(ModelCapability.IMAGE_GENERATION)
        
        # Determine model based on current facade
        model = self.model_name if "dall-e" in self.model_name else "dall-e-3"
        
        try:
            response = self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=n,
                **kwargs
            )
            
            return [image.url for image in response.data]
            
        except Exception as e:
            self._handle_error(e)
    
    def count_tokens(self, text: str, **kwargs) -> int:
        """
        Count tokens using tiktoken.
        
        Args:
            text: Text to count tokens for
            **kwargs: Additional parameters
        
        Returns:
            Token count
        """
        try:
            import tiktoken
            
            # Get encoding for model
            try:
                encoding = tiktoken.encoding_for_model(self.model_name)
            except KeyError:
                # Use cl100k_base as fallback for newer models
                encoding = tiktoken.get_encoding("cl100k_base")
            
            return len(encoding.encode(text))
            
        except ImportError:
            # Fall back to character-based estimation
            return super().count_tokens(text, **kwargs)
    
    def close(self):
        """Close client connections."""
        if hasattr(self, 'client'):
            self.client.close()
        super().close()


__all__ = ['OpenAIFacade']
