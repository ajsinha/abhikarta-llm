"""
Mock LLM Facade for Testing

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

from typing import List, Iterator
import time
from ...core.facade import (
    LLMFacade,
    Message,
    CompletionResponse,
    ChatResponse,
    ModelInfo
)
from ...core.provider import LLMProvider


class MockFacade(LLMFacade):
    """
    Mock facade for testing LLM operations.
    
    Returns predefined responses without calling any actual API.
    """
    
    def __init__(self, provider: LLMProvider, model_name: str):
        super().__init__(provider, model_name)
        self.call_count = 0
    
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        """
        Generate mock completion.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters (ignored)
            
        Returns:
            CompletionResponse with mock data
        """
        self.call_count += 1
        
        # Generate mock response based on prompt
        if "hello" in prompt.lower():
            text = "Hello! I'm a mock LLM. How can I help you today?"
        elif "?" in prompt:
            text = f"That's a great question about '{prompt[:50]}'. Here's a mock answer for testing purposes."
        else:
            text = f"Mock response to: {prompt[:50]}..."
        
        tokens_used = len(prompt.split()) + len(text.split())
        
        return CompletionResponse(
            text=text,
            model=self.model_name,
            provider='mock',
            tokens_used=tokens_used,
            finish_reason='complete',
            metadata={'call_count': self.call_count}
        )
    
    def chat(self, messages: List[Message], **kwargs) -> ChatResponse:
        """
        Generate mock chat response.
        
        Args:
            messages: List of messages
            **kwargs: Additional parameters (ignored)
            
        Returns:
            ChatResponse with mock data
        """
        self.call_count += 1
        
        # Get last user message
        user_messages = [m for m in messages if m.role == 'user']
        last_message = user_messages[-1].content if user_messages else "Hello"
        
        # Generate mock response
        if "hello" in last_message.lower() or "hi" in last_message.lower():
            content = "Hello! I'm a mock assistant. How can I help you?"
        elif "?" in last_message:
            content = f"That's an interesting question. Here's a mock answer for testing."
        else:
            content = f"I understand you said: '{last_message[:50]}...'. Here's my mock response."
        
        response_message = Message(
            role='assistant',
            content=content
        )
        
        # Calculate mock token usage
        total_content = ' '.join(m.content for m in messages) + content
        tokens_used = len(total_content.split())
        
        return ChatResponse(
            message=response_message,
            model=self.model_name,
            provider='mock',
            tokens_used=tokens_used,
            finish_reason='complete',
            metadata={'call_count': self.call_count}
        )
    
    def stream_complete(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Stream mock completion tokens.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters (ignored)
            
        Yields:
            Token strings
        """
        self.call_count += 1
        
        response = f"Mock streaming response to: {prompt[:30]}..."
        words = response.split()
        
        for word in words:
            time.sleep(0.01)  # Simulate streaming delay
            yield word + " "
    
    def stream_chat(self, messages: List[Message], **kwargs) -> Iterator[str]:
        """
        Stream mock chat response tokens.
        
        Args:
            messages: List of messages
            **kwargs: Additional parameters (ignored)
            
        Yields:
            Token strings
        """
        self.call_count += 1
        
        user_messages = [m for m in messages if m.role == 'user']
        last_message = user_messages[-1].content if user_messages else "Hello"
        
        response = f"Mock streaming chat response about: {last_message[:30]}..."
        words = response.split()
        
        for word in words:
            time.sleep(0.01)  # Simulate streaming delay
            yield word + " "
    
    def get_model_info(self) -> ModelInfo:
        """
        Get mock model information.
        
        Returns:
            ModelInfo object with mock data
        """
        if self.model_info_cache:
            return self.model_info_cache
        
        # Get model config from provider
        model_config = self.provider.get_model_info(self.model_name)
        
        self.model_info_cache = ModelInfo(
            name=model_config.get('name', self.model_name),
            version=model_config.get('version', '1.0'),
            description=model_config.get('description', 'Mock model for testing'),
            context_window=model_config.get('context_window', 4096),
            max_output=model_config.get('max_output', 1024),
            capabilities=model_config.get('capabilities', {}),
            cost=model_config.get('cost', {}),
            metadata={'provider': 'mock'}
        )
        
        return self.model_info_cache
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text (simple word-based count for mock).
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        return len(text.split())
