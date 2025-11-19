"""
Abhikarta HuggingFace Facade

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

import os
from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator

from llm_provider.facade_impl.base_provider_facade import BaseProviderFacade
from llm_facade import *


class HuggingFaceFacade(BaseProviderFacade):
    """HuggingFace Inference API facade."""
    
    def _initialize_client(self):
        """Initialize HuggingFace client."""
        try:
            from huggingface_hub import InferenceClient, AsyncInferenceClient
        except ImportError:
            raise ImportError("HuggingFace Hub not installed. Install with: pip install huggingface_hub")
        
        api_key = self.api_key or os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            raise AuthenticationException("HuggingFace API key required")
        
        self.client = InferenceClient(token=api_key)
        self.async_client = AsyncInferenceClient(token=api_key)
    
    def chat_completion(self, messages: Messages, temperature: Optional[float] = None,
                       max_tokens: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        if not self.supports_capability(ModelCapability.CHAT_COMPLETION):
            raise CapabilityNotSupportedException("chat", self.model_name)
        
        params = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens or 500
        }
        
        if temperature is not None:
            params['temperature'] = temperature
        
        try:
            response = self.client.chat_completion(**params)
            content = response.choices[0].message.content
            
            return {
                "content": content,
                "tool_calls": None,
                "usage": TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                "metadata": CompletionMetadata(model=self.model_name),
                "raw_response": response
            }
        except Exception as e:
            raise InvalidResponseException(f"HuggingFace API error: {str(e)}")
    
    async def achat_completion(self, messages: Messages, **kwargs) -> Dict[str, Any]:
        import asyncio
        return await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.chat_completion(messages, **kwargs)
        )
    
    def stream_chat_completion(self, messages: Messages, **kwargs) -> Iterator[str]:
        if not self.supports_capability(ModelCapability.STREAMING):
            raise CapabilityNotSupportedException("streaming", self.model_name)
        
        try:
            for token in self.client.chat_completion(
                model=self.model_name,
                messages=messages,
                stream=True,
                **kwargs
            ):
                if hasattr(token.choices[0].delta, 'content') and token.choices[0].delta.content:
                    yield token.choices[0].delta.content
        except Exception as e:
            raise InvalidResponseException(f"HuggingFace streaming error: {str(e)}")
    
    async def astream_chat_completion(self, messages: Messages, **kwargs) -> AsyncIterator[str]:
        import asyncio
        for chunk in self.stream_chat_completion(messages, **kwargs):
            yield chunk
            await asyncio.sleep(0)
    
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


__all__ = ['HuggingFaceFacade']
