"""
Abhikarta Ollama Facade - Local Models

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

import os
from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator

from base_provider_facade import BaseProviderFacade
from llm_facade import *


class OllamaFacade(BaseProviderFacade):
    """Ollama facade for running local models."""
    
    def _initialize_client(self):
        """Initialize Ollama client."""
        try:
            import ollama
        except ImportError:
            raise ImportError("Ollama SDK not installed. Install with: pip install ollama")
        
        # Ollama typically runs locally
        host = self.base_url or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.client = ollama.Client(host=host)
        self.async_client = ollama.AsyncClient(host=host)
    
    def chat_completion(self, messages: Messages, temperature: Optional[float] = None,
                       max_tokens: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        if not self.supports_capability(ModelCapability.CHAT_COMPLETION):
            raise CapabilityNotSupportedException("chat", self.model_name)
        
        options = {}
        if temperature is not None:
            options['temperature'] = temperature
        if max_tokens:
            options['num_predict'] = max_tokens
        
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=messages,
                options=options if options else None,
                **kwargs
            )
            
            return {
                "content": response['message']['content'],
                "tool_calls": None,
                "usage": TokenUsage(
                    prompt_tokens=response.get('prompt_eval_count', 0),
                    completion_tokens=response.get('eval_count', 0),
                    total_tokens=response.get('prompt_eval_count', 0) + response.get('eval_count', 0)
                ),
                "metadata": CompletionMetadata(model=self.model_name),
                "raw_response": response
            }
        except Exception as e:
            raise InvalidResponseException(f"Ollama API error: {str(e)}")
    
    async def achat_completion(self, messages: Messages, **kwargs) -> Dict[str, Any]:
        try:
            response = await self.async_client.chat(
                model=self.model_name,
                messages=messages,
                **kwargs
            )
            
            return {
                "content": response['message']['content'],
                "tool_calls": None,
                "usage": TokenUsage(
                    prompt_tokens=response.get('prompt_eval_count', 0),
                    completion_tokens=response.get('eval_count', 0),
                    total_tokens=response.get('prompt_eval_count', 0) + response.get('eval_count', 0)
                ),
                "metadata": CompletionMetadata(model=self.model_name),
                "raw_response": response
            }
        except Exception as e:
            raise InvalidResponseException(f"Ollama API error: {str(e)}")
    
    def stream_chat_completion(self, messages: Messages, **kwargs) -> Iterator[str]:
        if not self.supports_capability(ModelCapability.STREAMING):
            raise CapabilityNotSupportedException("streaming", self.model_name)
        
        try:
            stream = self.client.chat(
                model=self.model_name,
                messages=messages,
                stream=True,
                **kwargs
            )
            
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
        except Exception as e:
            raise InvalidResponseException(f"Ollama streaming error: {str(e)}")
    
    async def astream_chat_completion(self, messages: Messages, **kwargs) -> AsyncIterator[str]:
        try:
            stream = await self.async_client.chat(
                model=self.model_name,
                messages=messages,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
        except Exception as e:
            raise InvalidResponseException(f"Ollama streaming error: {str(e)}")
    
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
        if not self.supports_capability(ModelCapability.VISION):
            raise CapabilityNotSupportedException("vision", self.model_name)
        # Ollama supports vision for some models
        import base64
        processed_messages = messages.copy()
        
        for i in range(len(processed_messages) - 1, -1, -1):
            if processed_messages[i].get('role') == 'user':
                msg = processed_messages[i]
                image_data = []
                
                for img in images:
                    if isinstance(img, str):
                        if img.startswith('data:'):
                            img_data = img.split(',')[1]
                        else:
                            img_data = img
                    elif isinstance(img, bytes):
                        img_data = base64.b64encode(img).decode('utf-8')
                    else:
                        import io
                        buffer = io.BytesIO()
                        img.save(buffer, format='PNG')
                        img_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    
                    image_data.append(img_data)
                
                msg['images'] = image_data
                break
        
        return self.chat_completion(processed_messages, **kwargs)
    
    def parse_tool_calls(self, response: Dict[str, Any], **kwargs) -> List[ToolCall]:
        return []
    
    def count_tokens(self, text: str, **kwargs) -> int:
        return len(text) // 4
    
    def generate_embeddings(self, texts: Union[str, List[str]], **kwargs) -> Union[Embedding, List[Embedding]]:
        if not self.supports_capability(ModelCapability.EMBEDDINGS):
            raise CapabilityNotSupportedException("embeddings", self.model_name)
        
        is_single = isinstance(texts, str)
        text = texts if is_single else texts[0]
        
        try:
            response = self.client.embeddings(model=self.model_name, prompt=text)
            embedding = response['embedding']
            return embedding if is_single else [embedding]
        except Exception as e:
            raise InvalidResponseException(f"Ollama embeddings error: {str(e)}")
    
    async def agenerate_embeddings(self, texts: Union[str, List[str]], **kwargs) -> Union[Embedding, List[Embedding]]:
        import asyncio
        return await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.generate_embeddings(texts, **kwargs)
        )
    
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


__all__ = ['OllamaFacade']
