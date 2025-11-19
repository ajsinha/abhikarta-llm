"""
Abhikarta Cohere Facade - Dynamic Configuration Implementation

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

import os
import json
from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator

from llm_provider.base_provider_facade import BaseProviderFacade
from llm_provider.llm_facade import *


class CohereFacade(BaseProviderFacade):
    """Cohere facade with Command, Command-R, and embedding models."""
    
    def _initialize_client(self):
        """Initialize Cohere client."""
        try:
            import cohere
        except ImportError:
            raise ImportError("Cohere SDK not installed. Install with: pip install cohere")
        
        api_key = self.api_key or os.getenv("COHERE_API_KEY")
        if not api_key:
            raise AuthenticationException("Cohere API key required")
        
        self.client = cohere.Client(api_key=api_key, timeout=self.timeout)
        self.async_client = cohere.AsyncClient(api_key=api_key, timeout=self.timeout)
    
    def chat_completion(self, messages: Messages, temperature: Optional[float] = None,
                       max_tokens: Optional[int] = None, tools: Optional[List[ToolDefinition]] = None,
                       **kwargs) -> Dict[str, Any]:
        if not self.supports_capability(ModelCapability.CHAT_COMPLETION):
            raise CapabilityNotSupportedException("chat", self.model_name)
        
        # Convert messages
        chat_history = []
        message_text = ""
        for msg in messages:
            role = msg.get('role')
            content = msg.get('content', '')
            if role == 'system':
                kwargs['preamble'] = content
            elif role == 'user':
                message_text = content
            elif role == 'assistant':
                chat_history.append({"role": "CHATBOT", "message": content})
        
        params = {
            "model": self.model_name,
            "message": message_text,
            "chat_history": chat_history if chat_history else None
        }
        
        if temperature is not None:
            params['temperature'] = temperature
        if max_tokens:
            params['max_tokens'] = max_tokens
        if tools:
            params['tools'] = self._convert_tools(tools)
        
        params.update(kwargs)
        
        try:
            response = self.client.chat(**params)
            return self._convert_response(response)
        except Exception as e:
            raise InvalidResponseException(f"Cohere API error: {str(e)}")
    
    async def achat_completion(self, messages: Messages, **kwargs) -> Dict[str, Any]:
        chat_history = []
        message_text = ""
        for msg in messages:
            role = msg.get('role')
            content = msg.get('content', '')
            if role == 'system':
                kwargs['preamble'] = content
            elif role == 'user':
                message_text = content
            elif role == 'assistant':
                chat_history.append({"role": "CHATBOT", "message": content})
        
        try:
            response = await self.async_client.chat(
                model=self.model_name,
                message=message_text,
                chat_history=chat_history if chat_history else None,
                **kwargs
            )
            return self._convert_response(response)
        except Exception as e:
            raise InvalidResponseException(f"Cohere API error: {str(e)}")
    
    def stream_chat_completion(self, messages: Messages, **kwargs) -> Iterator[str]:
        if not self.supports_capability(ModelCapability.STREAMING):
            raise CapabilityNotSupportedException("streaming", self.model_name)
        
        chat_history = []
        message_text = ""
        for msg in messages:
            role = msg.get('role')
            content = msg.get('content', '')
            if role == 'user':
                message_text = content
            elif role == 'assistant':
                chat_history.append({"role": "CHATBOT", "message": content})
        
        try:
            stream = self.client.chat_stream(
                model=self.model_name,
                message=message_text,
                chat_history=chat_history if chat_history else None,
                **kwargs
            )
            
            for event in stream:
                if event.event_type == "text-generation":
                    yield event.text
        except Exception as e:
            raise InvalidResponseException(f"Cohere streaming error: {str(e)}")
    
    async def astream_chat_completion(self, messages: Messages, **kwargs) -> AsyncIterator[str]:
        import asyncio
        for chunk in self.stream_chat_completion(messages, **kwargs):
            yield chunk
            await asyncio.sleep(0)
    
    def generate_embeddings(self, texts: Union[str, List[str]], **kwargs) -> Union[Embedding, List[Embedding]]:
        if not self.supports_capability(ModelCapability.EMBEDDINGS):
            raise CapabilityNotSupportedException("embeddings", self.model_name)
        
        is_single = isinstance(texts, str)
        if is_single:
            texts = [texts]
        
        try:
            response = self.client.embed(
                model=self.model_name,
                texts=texts,
                **kwargs
            )
            embeddings = response.embeddings
            return embeddings[0] if is_single else embeddings
        except Exception as e:
            raise InvalidResponseException(f"Cohere embeddings error: {str(e)}")
    
    async def agenerate_embeddings(self, texts: Union[str, List[str]], **kwargs) -> Union[Embedding, List[Embedding]]:
        is_single = isinstance(texts, str)
        if is_single:
            texts = [texts]
        
        try:
            response = await self.async_client.embed(
                model=self.model_name,
                texts=texts,
                **kwargs
            )
            embeddings = response.embeddings
            return embeddings[0] if is_single else embeddings
        except Exception as e:
            raise InvalidResponseException(f"Cohere embeddings error: {str(e)}")
    
    def _convert_tools(self, tools: List[ToolDefinition]) -> List[Dict]:
        cohere_tools = []
        for tool in tools:
            if tool.get('type') == 'function':
                func = tool['function']
                cohere_tools.append({
                    "name": func['name'],
                    "description": func.get('description', ''),
                    "parameter_definitions": func.get('parameters', {}).get('properties', {})
                })
        return cohere_tools
    
    def _convert_response(self, response) -> Dict[str, Any]:
        content = response.text if hasattr(response, 'text') else ""
        
        tool_calls = []
        if hasattr(response, 'tool_calls'):
            for tc in response.tool_calls:
                tool_calls.append({
                    "id": tc.name,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": json.dumps(tc.parameters)
                    }
                })
        
        usage = None
        if hasattr(response, 'meta') and hasattr(response.meta, 'tokens'):
            usage = {
                "prompt_tokens": response.meta.tokens.input_tokens,
                "completion_tokens": response.meta.tokens.output_tokens,
                "total_tokens": response.meta.tokens.input_tokens + response.meta.tokens.output_tokens
            
            }
        
        return {
            "content": content,
            "tool_calls": tool_calls if tool_calls else None,
            "usage": usage,
            "metadata": {
                "model": self.model_name
            },
            "raw_response": response
        }
    
    def chat_completion_with_vision(self, messages: Messages, images: List[ImageInput], **kwargs) -> Dict[str, Any]:
        raise CapabilityNotSupportedException("vision", self.model_name)
    
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


__all__ = ['CohereFacade']
