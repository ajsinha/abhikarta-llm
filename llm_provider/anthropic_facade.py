"""
Abhikarta Anthropic Facade - Dynamic Configuration Implementation

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

import os
import json
import base64
from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator, Tuple
from PIL import Image
import io

from base_provider_facade import BaseProviderFacade
from llm_facade import (
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
    ImageInput,
    AuthenticationException,
    CapabilityNotSupportedException,
    InvalidResponseException
)


class AnthropicFacade(BaseProviderFacade):
    """
    Anthropic-specific facade with dynamic configuration loading.
    
    Features:
    - Loads all configuration from ModelProvider
    - Supports Claude 3.x family with vision and tool use
    - Streaming responses
    - Async operations
    - Prompt caching (when supported by model)
    - Extended thinking (when supported by model)
    """
    
    def _initialize_client(self):
        """Initialize Anthropic SDK client."""
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "Anthropic SDK not installed. Install with: pip install anthropic"
            )
        
        # Get API key from parameter or environment
        api_key = self.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise AuthenticationException(
                "Anthropic API key required. Provide via api_key parameter or "
                "ANTHROPIC_API_KEY environment variable."
            )
        
        client_kwargs = {
            "api_key": api_key,
            "max_retries": self.max_retries,
            "timeout": self.timeout
        }
        
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        
        if "anthropic_version" in self.kwargs:
            client_kwargs["default_headers"] = {
                "anthropic-version": self.kwargs["anthropic_version"]
            }
        
        self.client = anthropic.Anthropic(**client_kwargs)
        self.async_client = anthropic.AsyncAnthropic(**client_kwargs)
    
    def chat_completion(
        self,
        messages: Messages,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[ToolDefinition]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate chat completion using Anthropic API.
        
        Args:
            messages: List of message dictionaries
            system: Optional system prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            tools: Tool definitions for function calling
            tool_choice: Tool selection strategy
            **kwargs: Additional Anthropic-specific parameters
            
        Returns:
            Response dictionary with content, usage, and metadata
        """
        if not self.supports_capability(ModelCapability.CHAT_COMPLETION):
            raise CapabilityNotSupportedException("chat", self.model_name)
        
        # Use model's default max_tokens if not specified
        if not max_tokens:
            max_tokens = min(4096, self.model.max_output)
        
        request_params = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens
        }
        
        if system:
            request_params["system"] = system
        
        if temperature is not None:
            request_params["temperature"] = temperature
        
        if tools:
            request_params["tools"] = tools
            if tool_choice:
                request_params["tool_choice"] = tool_choice
        
        # Add any additional parameters
        request_params.update(kwargs)
        
        try:
            response = self.client.messages.create(**request_params)
            
            # Convert to standard format
            return self._convert_response(response)
        
        except Exception as e:
            raise InvalidResponseException(f"Anthropic API error: {str(e)}")
    
    async def achat_completion(
        self,
        messages: Messages,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[ToolDefinition]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Async version of chat_completion."""
        if not max_tokens:
            max_tokens = min(4096, self.model.max_output)
        
        request_params = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens
        }
        
        if system:
            request_params["system"] = system
        if temperature is not None:
            request_params["temperature"] = temperature
        if tools:
            request_params["tools"] = tools
            if tool_choice:
                request_params["tool_choice"] = tool_choice
        
        request_params.update(kwargs)
        
        try:
            response = await self.async_client.messages.create(**request_params)
            return self._convert_response(response)
        except Exception as e:
            raise InvalidResponseException(f"Anthropic API error: {str(e)}")
    
    def stream_chat_completion(
        self,
        messages: Messages,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[ToolDefinition]] = None,
        **kwargs
    ) -> Iterator[str]:
        """
        Stream chat completion responses.
        
        Yields text chunks as they arrive from the API.
        """
        if not self.supports_capability(ModelCapability.STREAMING):
            raise CapabilityNotSupportedException("streaming", self.model_name)
        
        if not max_tokens:
            max_tokens = min(4096, self.model.max_output)
        
        request_params = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        if system:
            request_params["system"] = system
        if temperature is not None:
            request_params["temperature"] = temperature
        if tools:
            request_params["tools"] = tools
        
        request_params.update(kwargs)
        
        try:
            with self.client.messages.stream(**request_params) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            raise InvalidResponseException(f"Anthropic streaming error: {str(e)}")
    
    async def astream_chat_completion(
        self,
        messages: Messages,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Async version of stream_chat_completion."""
        if not max_tokens:
            max_tokens = min(4096, self.model.max_output)
        
        request_params = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        if system:
            request_params["system"] = system
        if temperature is not None:
            request_params["temperature"] = temperature
        
        request_params.update(kwargs)
        
        try:
            async with self.async_client.messages.stream(**request_params) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            raise InvalidResponseException(f"Anthropic streaming error: {str(e)}")
    
    def chat_completion_with_vision(
        self,
        messages: Messages,
        images: List[ImageInput],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Chat completion with image inputs.
        
        Args:
            messages: Chat messages
            images: List of images (PIL Image, bytes, or base64 strings)
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary
        """
        if not self.supports_capability(ModelCapability.VISION):
            raise CapabilityNotSupportedException("vision", self.model_name)
        
        # Convert images and add to last user message
        processed_messages = self._add_images_to_messages(messages, images)
        
        return self.chat_completion(processed_messages, **kwargs)
    
    def _add_images_to_messages(
        self,
        messages: Messages,
        images: List[ImageInput]
    ) -> Messages:
        """Add images to messages in Anthropic format."""
        processed_messages = messages.copy()
        
        # Find last user message
        last_user_idx = None
        for i in range(len(processed_messages) - 1, -1, -1):
            if processed_messages[i].get('role') == 'user':
                last_user_idx = i
                break
        
        if last_user_idx is None:
            raise ValueError("No user message found to attach images")
        
        # Convert content to list format if string
        msg = processed_messages[last_user_idx]
        if isinstance(msg['content'], str):
            msg['content'] = [{"type": "text", "text": msg['content']}]
        
        # Add images
        for img in images:
            image_data = self._process_image(img)
            msg['content'].append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": image_data['media_type'],
                    "data": image_data['data']
                }
            })
        
        return processed_messages
    
    def _process_image(self, image: ImageInput) -> Dict[str, str]:
        """Convert image to Anthropic format."""
        if isinstance(image, bytes):
            # Detect image type
            media_type = "image/jpeg"
            if image.startswith(b'\x89PNG'):
                media_type = "image/png"
            elif image.startswith(b'GIF'):
                media_type = "image/gif"
            elif image.startswith(b'RIFF') and b'WEBP' in image[:20]:
                media_type = "image/webp"
            
            return {
                "media_type": media_type,
                "data": base64.b64encode(image).decode('utf-8')
            }
        
        elif isinstance(image, str):
            # Assume base64 string or file path
            if os.path.isfile(image):
                with open(image, 'rb') as f:
                    return self._process_image(f.read())
            else:
                # Assume base64
                return {
                    "media_type": "image/jpeg",
                    "data": image
                }
        
        elif isinstance(image, Image.Image):
            # PIL Image
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            return {
                "media_type": "image/png",
                "data": base64.b64encode(buffer.getvalue()).decode('utf-8')
            }
        
        else:
            raise ValueError(f"Unsupported image type: {type(image)}")
    
    def _convert_response(self, response) -> Dict[str, Any]:
        """Convert Anthropic response to standard format."""
        content = ""
        tool_calls = []
        
        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "type": "function",
                    "function": {
                        "name": block.name,
                        "arguments": json.dumps(block.input)
                    }
                })
        
        return {
            "content": content,
            "tool_calls": tool_calls if tool_calls else None,
            "usage": TokenUsage(
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens
            ),
            "metadata": CompletionMetadata(
                model=response.model,
                finish_reason=response.stop_reason,
                usage=TokenUsage(
                    prompt_tokens=response.usage.input_tokens,
                    completion_tokens=response.usage.output_tokens,
                    total_tokens=response.usage.input_tokens + response.usage.output_tokens
                )
            ),
            "raw_response": response
        }
    
    def parse_tool_calls(
        self,
        response: Dict[str, Any],
        **kwargs
    ) -> List[ToolCall]:
        """Extract tool calls from Anthropic response."""
        if "tool_calls" in response and response["tool_calls"]:
            return response["tool_calls"]
        return []
    
    def count_tokens(self, text: str, **kwargs) -> int:
        """
        Count tokens in text using Anthropic's token counting.
        
        Note: This is an approximation. Use Anthropic's official
        token counting API for exact counts.
        """
        # Rough approximation: 1 token ≈ 4 characters
        return len(text) // 4
    
    # Placeholder implementations for required abstract methods
    def text_completion(self, prompt: str, **kwargs) -> str:
        """Text completion (maps to chat completion)."""
        messages = [{"role": "user", "content": prompt}]
        response = self.chat_completion(messages, **kwargs)
        return response["content"]
    
    async def atext_completion(self, prompt: str, **kwargs) -> str:
        """Async text completion."""
        messages = [{"role": "user", "content": prompt}]
        response = await self.achat_completion(messages, **kwargs)
        return response["content"]
    
    def stream_text_completion(self, prompt: str, **kwargs) -> TextStream:
        """Stream text completion."""
        messages = [{"role": "user", "content": prompt}]
        return self.stream_chat_completion(messages, **kwargs)
    
    async def astream_text_completion(self, prompt: str, **kwargs) -> TextStream:
        """Async stream text completion."""
        messages = [{"role": "user", "content": prompt}]
        async for chunk in self.astream_chat_completion(messages, **kwargs):
            yield chunk
    
    # Stub implementations for unsupported features
    def generate_embeddings(self, texts: Union[str, List[str]], **kwargs) -> Union[Embedding, List[Embedding]]:
        raise CapabilityNotSupportedException("embeddings", self.model_name)
    
    async def agenerate_embeddings(self, texts: Union[str, List[str]], **kwargs) -> Union[Embedding, List[Embedding]]:
        raise CapabilityNotSupportedException("embeddings", self.model_name)
    
    def generate_image(self, prompt: str, **kwargs) -> ImageOutput:
        raise CapabilityNotSupportedException("image_generation", self.model_name)
    
    async def agenerate_image(self, prompt: str, **kwargs) -> ImageOutput:
        raise CapabilityNotSupportedException("image_generation", self.model_name)
    
    def moderate_content(self, content: str, **kwargs) -> ModerationResult:
        raise CapabilityNotSupportedException("moderation", self.model_name)
    
    async def amoderate_content(self, content: str, **kwargs) -> ModerationResult:
        raise CapabilityNotSupportedException("moderation", self.model_name)
    
    def log_request(self, method: str, input_data: Any, response: Any, latency_ms: float, metadata: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        # Basic logging - can be extended
        pass
    
    def get_usage_stats(self, period: str = "day", **kwargs) -> Dict[str, Any]:
        # Placeholder - would need to implement usage tracking
        return {"message": "Usage stats not implemented"}


__all__ = ['AnthropicFacade']
