"""
Mock LLM Facade Implementation

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
This module provides a mock implementation of the LLMFacade interface for testing purposes.
"""

import time
from typing import List, Dict, Any, Optional, Union, Iterator

from .llm_facade_base import LLMFacadeBase
from .llm_facade import (
    ModelCapability,
    GenerationConfig,
    Messages,
    ToolDefinition,
)


class MockFacade(LLMFacadeBase):
    """
    Mock implementation of the LLMFacade interface for testing.
    
    Returns predefined responses without making any API calls.
    Useful for testing and development.
    
    Example:
        >>> from mock_facade import MockFacade
        >>> llm = MockFacade(model_name="mock-model")
        >>> response = llm.chat_completion([
        ...     {"role": "user", "content": "Hello!"}
        ... ])
        >>> print(response["content"])
        Mock response to: Hello!
    """
    
    def __init__(
        self,
        model_name: str = "mock-model",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        response_template: str = "Mock response to: {prompt}",
        **kwargs
    ):
        """
        Initialize Mock facade.
        
        Args:
            model_name: Model identifier
            api_key: Not required for mock
            base_url: Not used
            timeout: Simulated delay
            max_retries: Not used
            response_template: Template for generating responses
            **kwargs: Additional configuration
        """
        super().__init__(
            provider_name="mock",
            model_name=model_name,
            api_key=api_key or "mock-key",
            base_url=base_url or "http://localhost",
            timeout=timeout or 0.1,
            max_retries=max_retries,
            **kwargs
        )
        self.response_template = response_template
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize mock client."""
        self.client = "mock-client"
        self.logger.info(f"Initialized Mock facade for {self.model_name}")
    
    def get_capabilities(self) -> List[ModelCapability]:
        """Get list of mock capabilities."""
        return [
            ModelCapability.CHAT_COMPLETION,
            ModelCapability.TEXT_GENERATION,
            ModelCapability.STREAMING,
            ModelCapability.EMBEDDINGS
        ]
    
    def chat_completion(
        self,
        messages: Messages,
        tools: Optional[List[ToolDefinition]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate mock chat completion.
        
        Args:
            messages: List of message dictionaries
            tools: Optional tool definitions
            tool_choice: Tool selection strategy
            config: Generation configuration
            **kwargs: Additional parameters
        
        Returns:
            Dictionary with mock completion result
        """
        self._check_capability(ModelCapability.CHAT_COMPLETION)
        
        start_time = time.time()
        
        # Simulate processing delay
        time.sleep(self.timeout)
        
        # Get last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # Generate mock response
        content = self.response_template.format(prompt=user_message)
        
        # Build result
        result = {
            "content": content,
            "role": "assistant",
            "finish_reason": "stop",
            "usage": {
                "prompt_tokens": self.count_tokens(str(messages)),
                "completion_tokens": self.count_tokens(content),
                "total_tokens": self.count_tokens(str(messages)) + self.count_tokens(content)
            }
        }
        
        # Mock tool calls if tools provided
        if tools and len(tools) > 0:
            result["tool_calls"] = [{
                "id": "mock_call_1",
                "type": "function",
                "function": {
                    "name": tools[0].get("name", "mock_function"),
                    "arguments": '{"param": "mock_value"}'
                }
            }]
        
        # Log request
        latency = (time.time() - start_time) * 1000
        self.log_request("chat_completion", messages, result, latency)
        
        return result
    
    def completion(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> str:
        """
        Generate mock text completion.
        
        Args:
            prompt: Input prompt
            config: Generation configuration
            **kwargs: Additional parameters
        
        Returns:
            Mock generated text
        """
        response = self.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            config=config,
            **kwargs
        )
        return response["content"]
    
    def stream_chat_completion(
        self,
        messages: Messages,
        tools: Optional[List[ToolDefinition]] = None,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> Iterator[str]:
        """
        Stream mock chat completion responses.
        
        Args:
            messages: List of message dictionaries
            tools: Optional tool definitions
            config: Generation configuration
            **kwargs: Additional parameters
        
        Yields:
            Mock text chunks
        """
        self._check_capability(ModelCapability.STREAMING)
        
        # Get full response
        result = self.chat_completion(messages, tools, None, config, **kwargs)
        content = result["content"]
        
        # Stream word by word
        words = content.split()
        for word in words:
            time.sleep(0.01)  # Simulate streaming delay
            yield word + " "
    
    def get_embeddings(
        self,
        texts: Union[str, List[str]],
        model: Optional[str] = None,
        **kwargs
    ) -> List[List[float]]:
        """
        Generate mock embeddings.
        
        Args:
            texts: Single text or list of texts
            model: Embedding model name
            **kwargs: Additional parameters
        
        Returns:
            List of mock embedding vectors
        """
        if isinstance(texts, str):
            texts = [texts]
        
        # Return mock embeddings (random-ish but deterministic)
        embeddings = []
        for text in texts:
            # Simple hash-based mock embedding
            embedding = [float((ord(c) % 100) / 100.0) for c in (text[:1536] if len(text) > 1536 else text.ljust(1536, ' '))]
            embeddings.append(embedding)
        
        return embeddings


__all__ = ['MockFacade']
