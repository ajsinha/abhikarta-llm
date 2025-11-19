"""
Abhikarta OpenAI Facade - Dynamic Configuration Implementation

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
from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator

from llm_provider.base_provider_facade import BaseProviderFacade
from llm_provider.llm_facade import (
    ModelCapability,
    TokenUsage,
    CompletionMetadata,
    Messages,
    TextStream,
    ToolDefinition,
    ToolCall,
    Embedding,
    ImageInput,
    ImageOutput,
    AuthenticationException,
    CapabilityNotSupportedException,
    InvalidResponseException, ModerationResult
)


class OpenAIFacade(BaseProviderFacade):
    """
    OpenAI-specific facade with dynamic configuration loading.
    
    Features:
    - Loads all configuration from ModelProvider
    - Supports GPT-4, GPT-3.5, and other OpenAI models
    - Function calling and tool use
    - Streaming responses
    - Vision capabilities (GPT-4 Vision)
    - Embeddings (text-embedding models)
    """
    
    def _initialize_client(self):
        """Initialize OpenAI SDK client."""
        try:
            from openai import OpenAI, AsyncOpenAI
        except ImportError:
            raise ImportError(
                "OpenAI SDK not installed. Install with: pip install openai"
            )
        
        # Get API key
        api_key = self.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise AuthenticationException(
                "OpenAI API key required. Provide via api_key parameter or "
                "OPENAI_API_KEY environment variable."
            )
        
        client_kwargs = {
            "api_key": api_key,
            "timeout": self.timeout,
            "max_retries": self.max_retries
        }
        
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        
        if "organization" in self.kwargs:
            client_kwargs["organization"] = self.kwargs["organization"]
        
        self.client = OpenAI(**client_kwargs)
        self.async_client = AsyncOpenAI(**client_kwargs)
    
    def chat_completion(
        self,
        messages: Messages,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[ToolDefinition]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate chat completion using OpenAI API."""
        if not self.supports_capability(ModelCapability.CHAT_COMPLETION):
            raise CapabilityNotSupportedException("chat", self.model_name)
        
        request_params = {
            "model": self.model_name,
            "messages": messages
        }
        
        if temperature is not None:
            request_params["temperature"] = temperature
        if max_tokens:
            request_params["max_tokens"] = max_tokens
        if tools:
            request_params["tools"] = tools
            if tool_choice:
                request_params["tool_choice"] = tool_choice
        if response_format:
            request_params["response_format"] = response_format
        
        request_params.update(kwargs)
        
        try:
            response = self.client.chat.completions.create(**request_params)
            return self._convert_response(response)
        except Exception as e:
            raise InvalidResponseException(f"OpenAI API error: {str(e)}")
    
    async def achat_completion(
        self,
        messages: Messages,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[ToolDefinition]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Async chat completion."""
        request_params = {
            "model": self.model_name,
            "messages": messages
        }
        
        if temperature is not None:
            request_params["temperature"] = temperature
        if max_tokens:
            request_params["max_tokens"] = max_tokens
        if tools:
            request_params["tools"] = tools
        
        request_params.update(kwargs)
        
        try:
            response = await self.async_client.chat.completions.create(**request_params)
            return self._convert_response(response)
        except Exception as e:
            raise InvalidResponseException(f"OpenAI API error: {str(e)}")
    
    def stream_chat_completion(
        self,
        messages: Messages,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Iterator[str]:
        """Stream chat completion responses."""
        if not self.supports_capability(ModelCapability.STREAMING):
            raise CapabilityNotSupportedException("streaming", self.model_name)
        
        request_params = {
            "model": self.model_name,
            "messages": messages,
            "stream": True
        }
        
        if temperature is not None:
            request_params["temperature"] = temperature
        if max_tokens:
            request_params["max_tokens"] = max_tokens
        
        request_params.update(kwargs)
        
        try:
            stream = self.client.chat.completions.create(**request_params)
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise InvalidResponseException(f"OpenAI streaming error: {str(e)}")
    
    async def astream_chat_completion(
        self,
        messages: Messages,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Async stream chat completion."""
        request_params = {
            "model": self.model_name,
            "messages": messages,
            "stream": True
        }
        
        if temperature is not None:
            request_params["temperature"] = temperature
        if max_tokens:
            request_params["max_tokens"] = max_tokens
        
        request_params.update(kwargs)
        
        try:
            stream = await self.async_client.chat.completions.create(**request_params)
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise InvalidResponseException(f"OpenAI streaming error: {str(e)}")
    
    def chat_completion_with_vision(
        self,
        messages: Messages,
        images: List[ImageInput],
        **kwargs
    ) -> Dict[str, Any]:
        """Chat completion with vision (GPT-4 Vision)."""
        if not self.supports_capability(ModelCapability.VISION):
            raise CapabilityNotSupportedException("vision", self.model_name)
        
        # Process images and add to messages
        processed_messages = self._add_images_to_messages(messages, images)
        return self.chat_completion(processed_messages, **kwargs)
    
    def _add_images_to_messages(
        self,
        messages: Messages,
        images: List[ImageInput]
    ) -> Messages:
        """Add images to messages in OpenAI format."""
        processed_messages = messages.copy()
        
        # Find last user message
        for i in range(len(processed_messages) - 1, -1, -1):
            if processed_messages[i].get('role') == 'user':
                msg = processed_messages[i]
                if isinstance(msg['content'], str):
                    msg['content'] = [
                        {"type": "text", "text": msg['content']}
                    ]
                
                for img in images:
                    if isinstance(img, str):
                        # URL or base64
                        if img.startswith('http'):
                            image_content = {"type": "image_url", "image_url": {"url": img}}
                        else:
                            image_content = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}}
                    else:
                        # Convert to base64
                        import base64
                        if isinstance(img, bytes):
                            img_b64 = base64.b64encode(img).decode('utf-8')
                        else:
                            # PIL Image
                            import io
                            buffer = io.BytesIO()
                            img.save(buffer, format='PNG')
                            img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                        image_content = {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                    
                    msg['content'].append(image_content)
                break
        
        return processed_messages
    
    def generate_embeddings(
        self,
        texts: Union[str, List[str]],
        **kwargs
    ) -> Union[Embedding, List[Embedding]]:
        """Generate embeddings using OpenAI API."""
        if not self.supports_capability(ModelCapability.EMBEDDINGS):
            raise CapabilityNotSupportedException("embeddings", self.model_name)
        
        is_single = isinstance(texts, str)
        if is_single:
            texts = [texts]
        
        try:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=texts,
                **kwargs
            )
            
            embeddings = [item.embedding for item in response.data]
            return embeddings[0] if is_single else embeddings
        
        except Exception as e:
            raise InvalidResponseException(f"OpenAI embeddings error: {str(e)}")
    
    async def agenerate_embeddings(
        self,
        texts: Union[str, List[str]],
        **kwargs
    ) -> Union[Embedding, List[Embedding]]:
        """Async generate embeddings."""
        is_single = isinstance(texts, str)
        if is_single:
            texts = [texts]
        
        try:
            response = await self.async_client.embeddings.create(
                model=self.model_name,
                input=texts,
                **kwargs
            )
            
            embeddings = [item.embedding for item in response.data]
            return embeddings[0] if is_single else embeddings
        
        except Exception as e:
            raise InvalidResponseException(f"OpenAI embeddings error: {str(e)}")
    
    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        **kwargs
    ) -> ImageOutput:
        """Generate image using DALL-E."""
        if not self.supports_capability(ModelCapability.IMAGE_GENERATION):
            raise CapabilityNotSupportedException("image_generation", self.model_name)
        
        try:
            response = self.client.images.generate(
                model=self.model_name,
                prompt=prompt,
                size=size,
                quality=quality,
                **kwargs
            )
            
            return response.data[0].url
        
        except Exception as e:
            raise InvalidResponseException(f"OpenAI image generation error: {str(e)}")
    
    async def agenerate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        **kwargs
    ) -> ImageOutput:
        """Async image generation."""
        try:
            response = await self.async_client.images.generate(
                model=self.model_name,
                prompt=prompt,
                size=size,
                **kwargs
            )
            
            return response.data[0].url
        
        except Exception as e:
            raise InvalidResponseException(f"OpenAI image generation error: {str(e)}")
    
    def _convert_response(self, response) -> Dict[str, Any]:
        """Convert OpenAI response to standard format."""
        choice = response.choices[0]
        
        tool_calls = None
        if choice.message.tool_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in choice.message.tool_calls
            ]
        
        return {
            "content": choice.message.content or "",
            "tool_calls": tool_calls,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            "metadata": {
                "model": response.model,
                "finish_reason": choice.finish_reason
            },
            "raw_response": response
        }
    
    def parse_tool_calls(
        self,
        response: Dict[str, Any],
        **kwargs
    ) -> List[ToolCall]:
        """Extract tool calls from response."""
        if "tool_calls" in response and response["tool_calls"]:
            return response["tool_calls"]
        return []
    
    def count_tokens(self, text: str, **kwargs) -> int:
        """Count tokens (rough approximation)."""
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model_name)
            return len(encoding.encode(text))
        except:
            # Fallback approximation
            return len(text) // 4
    
    # Placeholder implementations
    def text_completion(self, prompt: str, **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        response = self.chat_completion(messages, **kwargs)
        return response["content"]
    
    async def atext_completion(self, prompt: str, **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        response = await self.achat_completion(messages, **kwargs)
        return response["content"]
    
    def stream_text_completion(self, prompt: str, **kwargs) -> TextStream:
        messages = [{"role": "user", "content": prompt}]
        return self.stream_chat_completion(messages, **kwargs)
    
    async def astream_text_completion(self, prompt: str, **kwargs) -> TextStream:
        messages = [{"role": "user", "content": prompt}]
        async for chunk in self.astream_chat_completion(messages, **kwargs):
            yield chunk
    
    def moderate_content(self, content: str, **kwargs) -> ModerationResult:
        """Content moderation using OpenAI API."""
        try:
            response = self.client.moderations.create(input=content)
            result = response.results[0]
            return {
                "flagged": result.flagged,
                "categories": result.categories.dict(),
                "category_scores": result.category_scores.dict()
            }
        except Exception as e:
            raise InvalidResponseException(f"OpenAI moderation error: {str(e)}")
    
    async def amoderate_content(self, content: str, **kwargs) -> ModerationResult:
        """Async content moderation."""
        try:
            response = await self.async_client.moderations.create(input=content)
            result = response.results[0]
            return {
                "flagged": result.flagged,
                "categories": result.categories.dict(),
                "category_scores": result.category_scores.dict()
            }
        except Exception as e:
            raise InvalidResponseException(f"OpenAI moderation error: {str(e)}")
    
    def log_request(self, method: str, input_data: Any, response: Any, latency_ms: float, metadata: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        pass
    
    def get_usage_stats(self, period: str = "day", **kwargs) -> Dict[str, Any]:
        return {"message": "Usage stats not implemented"}


__all__ = ['OpenAIFacade']
