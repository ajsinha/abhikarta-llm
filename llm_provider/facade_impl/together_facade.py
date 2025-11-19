"""
Abhikarta Together AI Facade

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

import os
from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator

from llm_provider.base_provider_facade import BaseProviderFacade
from llm_provider.llm_facade import *


class TogetherFacade(BaseProviderFacade):
    """Together AI facade for open-source models."""
    
    def _initialize_client(self):
        """Initialize Together client."""
        try:
            from together import Together, AsyncTogether
        except ImportError:
            raise ImportError("Together SDK not installed. Install with: pip install together")
        
        api_key = self.api_key or os.getenv("TOGETHER_API_KEY")
        if not api_key:
            raise AuthenticationException("Together API key required")
        
        self.client = Together(api_key=api_key)
        self.async_client = AsyncTogether(api_key=api_key)
    
    def chat_completion(self, messages: Messages, temperature: Optional[float] = None,
                       max_tokens: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        if not self.supports_capability(ModelCapability.CHAT_COMPLETION):
            raise CapabilityNotSupportedException("chat", self.model_name)
        
        params = {
            "model": self.model_name,
            "messages": messages
        }
        
        if temperature is not None:
            params['temperature'] = temperature
        if max_tokens:
            params['max_tokens'] = max_tokens
        
        params.update(kwargs)
        
        try:
            response = self.client.chat.completions.create(**params)
            return self._convert_response(response)
        except Exception as e:
            raise InvalidResponseException(f"Together API error: {str(e)}")
    
    async def achat_completion(self, messages: Messages, **kwargs) -> Dict[str, Any]:
        try:
            response = await self.async_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                **kwargs
            )
            return self._convert_response(response)
        except Exception as e:
            raise InvalidResponseException(f"Together API error: {str(e)}")
    
    def stream_chat_completion(self, messages: Messages, **kwargs) -> Iterator[str]:
        if not self.supports_capability(ModelCapability.STREAMING):
            raise CapabilityNotSupportedException("streaming", self.model_name)
        
        try:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=True,
                **kwargs
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise InvalidResponseException(f"Together streaming error: {str(e)}")
    
    async def astream_chat_completion(self, messages: Messages, **kwargs) -> AsyncIterator[str]:
        try:
            stream = await self.async_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise InvalidResponseException(f"Together streaming error: {str(e)}")
    
    def _convert_response(self, response) -> Dict[str, Any]:
        choice = response.choices[0]
        content = choice.message.content or ""
        
        usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
        
            }
        
        return {
            "content": content,
            "tool_calls": None,
            "usage": usage,
            "metadata": {
                "model": response.model
            },
            "raw_response": response
        }
    
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
    
    def chat_completion_with_vision(self, messages: Messages, images: List[ImageInput], **kwargs) -> Dict[str, Any]:
        raise CapabilityNotSupportedException("vision", self.model_name)
    
    def parse_tool_calls(self, response: Dict[str, Any], **kwargs) -> List[ToolCall]:
        return []
    
    def count_tokens(self, text: str, **kwargs) -> int:
        return len(text) // 4
    
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
        pass
    
    def get_usage_stats(self, period: str = "day", **kwargs) -> Dict[str, Any]:
        return {"message": "Usage stats not implemented"}


__all__ = ['TogetherFacade']
