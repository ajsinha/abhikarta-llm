"""
Abhikarta Groq Facade - Dynamic Configuration Implementation

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

import os
import json
from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator, Tuple

from base_provider_facade import BaseProviderFacade
from llm_facade import *


class GroqFacade(BaseProviderFacade):
    """Groq facade for ultra-fast inference with Llama, Mixtral, and Gemma models."""
    
    def _initialize_client(self):
        """Initialize Groq client."""
        try:
            from groq import Groq, AsyncGroq
        except ImportError:
            raise ImportError("Groq SDK not installed. Install with: pip install groq")
        
        api_key = self.api_key or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise AuthenticationException("Groq API key required")
        
        self.client = Groq(api_key=api_key)
        self.async_client = AsyncGroq(api_key=api_key)
    
    def chat_completion(self, messages: Messages, temperature: Optional[float] = None,
                       max_tokens: Optional[int] = None, tools: Optional[List[ToolDefinition]] = None,
                       **kwargs) -> Dict[str, Any]:
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
        if tools:
            params['tools'] = tools
        
        params.update(kwargs)
        
        try:
            response = self.client.chat.completions.create(**params)
            return self._convert_response(response)
        except Exception as e:
            raise InvalidResponseException(f"Groq API error: {str(e)}")
    
    async def achat_completion(self, messages: Messages, **kwargs) -> Dict[str, Any]:
        try:
            response = await self.async_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                **kwargs
            )
            return self._convert_response(response)
        except Exception as e:
            raise InvalidResponseException(f"Groq API error: {str(e)}")
    
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
            raise InvalidResponseException(f"Groq streaming error: {str(e)}")
    
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
            raise InvalidResponseException(f"Groq streaming error: {str(e)}")
    
    def _convert_response(self, response) -> Dict[str, Any]:
        choice = response.choices[0]
        content = choice.message.content or ""
        
        tool_calls = []
        if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                tool_calls.append({
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                })
        
        usage = TokenUsage(
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens
        )
        
        return {
            "content": content,
            "tool_calls": tool_calls if tool_calls else None,
            "usage": usage,
            "metadata": CompletionMetadata(model=response.model, finish_reason=choice.finish_reason, usage=usage),
            "raw_response": response
        }
    
    def chat_completion_with_vision(self, messages: Messages, images: List[ImageInput], **kwargs) -> Dict[str, Any]:
        if not self.supports_capability(ModelCapability.VISION):
            raise CapabilityNotSupportedException("vision", self.model_name)
        # Groq supports vision for some models - process images and add to messages
        processed_messages = self._add_images_to_messages(messages, images)
        return self.chat_completion(processed_messages, **kwargs)
    
    def _add_images_to_messages(self, messages: Messages, images: List[ImageInput]) -> Messages:
        """Add images to messages in OpenAI-compatible format."""
        import base64
        processed_messages = messages.copy()
        
        for i in range(len(processed_messages) - 1, -1, -1):
            if processed_messages[i].get('role') == 'user':
                msg = processed_messages[i]
                if isinstance(msg['content'], str):
                    msg['content'] = [{"type": "text", "text": msg['content']}]
                
                for img in images:
                    if isinstance(img, str):
                        if img.startswith('http'):
                            image_content = {"type": "image_url", "image_url": {"url": img}}
                        else:
                            image_content = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}}
                    else:
                        if isinstance(img, bytes):
                            img_b64 = base64.b64encode(img).decode('utf-8')
                        else:
                            import io
                            buffer = io.BytesIO()
                            img.save(buffer, format='PNG')
                            img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                        image_content = {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                    
                    msg['content'].append(image_content)
                break
        
        return processed_messages
    
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
    
    def parse_tool_calls(self, response: Dict[str, Any], **kwargs) -> List[ToolCall]:
        return response.get("tool_calls", [])
    
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


__all__ = ['GroqFacade']
