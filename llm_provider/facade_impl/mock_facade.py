"""
Abhikarta Mock Facade - For Testing

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

import time
from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator

from llm_provider.facade_impl.base_provider_facade import BaseProviderFacade
from llm_facade import *


class MockFacade(BaseProviderFacade):
    """Mock facade for testing and development."""
    
    def _initialize_client(self):
        """No real client needed for mock."""
        self.call_count = 0
        self.latency_ms = self.kwargs.get('mock_latency_ms', 100)
    
    def chat_completion(self, messages: Messages, temperature: Optional[float] = None,
                       max_tokens: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        self.call_count += 1
        time.sleep(self.latency_ms / 1000.0)
        
        # Generate mock response
        last_message = messages[-1]['content'] if messages else "Hello"
        response_text = f"Mock response to: {last_message[:50]}... (call #{self.call_count})"
        
        token_count = len(response_text) // 4
        
        return {
            "content": response_text,
            "tool_calls": None,
            "usage": TokenUsage(
                prompt_tokens=token_count,
                completion_tokens=token_count,
                total_tokens=token_count * 2
            ),
            "metadata": CompletionMetadata(
                model=self.model_name,
                finish_reason="stop",
                usage=TokenUsage(
                    prompt_tokens=token_count,
                    completion_tokens=token_count,
                    total_tokens=token_count * 2
                )
            ),
            "raw_response": {"mock": True}
        }
    
    async def achat_completion(self, messages: Messages, **kwargs) -> Dict[str, Any]:
        import asyncio
        await asyncio.sleep(self.latency_ms / 1000.0)
        return self.chat_completion(messages, **kwargs)
    
    def stream_chat_completion(self, messages: Messages, **kwargs) -> Iterator[str]:
        self.call_count += 1
        words = ["This", "is", "a", "mock", "streaming", "response", f"(call #{self.call_count})"]
        
        for word in words:
            time.sleep(0.05)
            yield word + " "
    
    async def astream_chat_completion(self, messages: Messages, **kwargs) -> AsyncIterator[str]:
        import asyncio
        self.call_count += 1
        words = ["This", "is", "a", "mock", "streaming", "response", f"(call #{self.call_count})"]
        
        for word in words:
            await asyncio.sleep(0.05)
            yield word + " "
    
    def chat_completion_with_vision(self, messages: Messages, images: List[ImageInput], **kwargs) -> Dict[str, Any]:
        self.call_count += 1
        
        return {
            "content": f"Mock vision response: I see {len(images)} image(s) (call #{self.call_count})",
            "tool_calls": None,
            "usage": TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
            "metadata": CompletionMetadata(model=self.model_name),
            "raw_response": {"mock": True}
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
    
    def parse_tool_calls(self, response: Dict[str, Any], **kwargs) -> List[ToolCall]:
        return []
    
    def count_tokens(self, text: str, **kwargs) -> int:
        return len(text) // 4
    
    def generate_embeddings(self, texts: Union[str, List[str]], **kwargs) -> Union[Embedding, List[Embedding]]:
        is_single = isinstance(texts, str)
        # Return mock embeddings (128-dimensional)
        embedding = [0.1] * 128
        return embedding if is_single else [embedding]
    
    async def agenerate_embeddings(self, texts: Union[str, List[str]], **kwargs) -> Union[Embedding, List[Embedding]]:
        return self.generate_embeddings(texts, **kwargs)
    
    def generate_image(self, prompt: str, **kwargs) -> ImageOutput:
        return f"mock_image_url_for_{prompt[:20]}.png"
    
    async def agenerate_image(self, prompt: str, **kwargs) -> ImageOutput:
        return self.generate_image(prompt, **kwargs)
    
    def moderate_content(self, content: str, **kwargs) -> ModerationResult:
        return {
            "flagged": False,
            "categories": {"hate": False, "violence": False},
            "scores": {"hate": 0.01, "violence": 0.02}
        }
    
    async def amoderate_content(self, content: str, **kwargs) -> ModerationResult:
        return self.moderate_content(content, **kwargs)
    
    def log_request(self, method: str, input_data: Any, response: Any, latency_ms: float, metadata: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        print(f"Mock: Logged {method} call")
    
    def get_usage_stats(self, period: str = "day", **kwargs) -> Dict[str, Any]:
        return {
            "total_calls": self.call_count,
            "mock": True
        }


__all__ = ['MockFacade']
