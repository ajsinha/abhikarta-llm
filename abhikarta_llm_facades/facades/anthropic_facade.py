"""
Anthropic LLM Facade Implementation

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
This module provides a concrete implementation of the LLMFacade interface for
Anthropic's Claude models.
"""

import os
import time
from typing import List, Dict, Any, Optional, Union, Iterator

from .llm_facade_base import LLMFacadeBase
from .llm_facade import (
    ModelCapability,
    GenerationConfig,
    Messages,
    ToolDefinition,
    AuthenticationException,
)


class AnthropicFacade(LLMFacadeBase):
    """
    Anthropic implementation of the LLMFacade interface.
    
    Supports Claude 3 family models (Opus, Sonnet, Haiku) with features including:
    - Chat completion with 200K context
    - Vision capabilities
    - Function calling
    - Streaming responses
    
    Example:
        >>> from anthropic_facade import AnthropicFacade
        >>> llm = AnthropicFacade(model_name="claude-3-opus-20240229")
        >>> response = llm.chat_completion([
        ...     {"role": "user", "content": "Explain quantum computing"}
        ... ])
        >>> print(response["content"])
    """
    
    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        **kwargs
    ):
        """
        Initialize Anthropic facade.
        
        Args:
            model_name: Model identifier (e.g., "claude-3-opus-20240229")
            api_key: Anthropic API key (reads from ANTHROPIC_API_KEY if None)
            base_url: Custom API endpoint
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts
            **kwargs: Additional configuration
        """
        super().__init__(
            provider_name="anthropic",
            model_name=model_name,
            api_key=api_key or os.getenv('ANTHROPIC_API_KEY'),
            base_url=base_url or "https://api.anthropic.com",
            timeout=timeout,
            max_retries=max_retries,
            **kwargs
        )
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Anthropic client."""
        try:
            import anthropic
            
            self.client = anthropic.Anthropic(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
                max_retries=self.max_retries
            )
            
            self.logger.info(f"Initialized Anthropic client for {self.model_name}")
            
        except ImportError:
            raise ImportError("Please install anthropic: pip install anthropic")
        except Exception as e:
            raise AuthenticationException(f"Failed to initialize Anthropic client: {e}")
    
    def chat_completion(
        self,
        messages: Messages,
        tools: Optional[List[ToolDefinition]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate chat completion using Claude.
        
        Args:
            messages: List of message dictionaries
            tools: Optional tool definitions
            tool_choice: Tool selection strategy
            config: Generation configuration
            **kwargs: Additional parameters
        
        Returns:
            Dictionary with completion result
        """
        self._check_capability(ModelCapability.CHAT_COMPLETION)
        
        start_time = time.time()
        
        try:
            # Extract system message if present
            system_message = None
            filtered_messages = []
            
            for msg in messages:
                if msg.get("role") == "system":
                    system_message = msg.get("content", "")
                else:
                    filtered_messages.append(msg)
            
            # Build request parameters
            params = {
                "model": self.model_name,
                "messages": filtered_messages,
                "max_tokens": 4096  # Default
            }
            
            if system_message:
                params["system"] = system_message
            
            # Add generation config
            if config:
                config_dict = config.to_dict()
                if config_dict.get("max_tokens"):
                    params["max_tokens"] = config_dict["max_tokens"]
                if config_dict.get("temperature") is not None:
                    params["temperature"] = config_dict["temperature"]
                if config_dict.get("top_p") is not None:
                    params["top_p"] = config_dict["top_p"]
                if config_dict.get("top_k") is not None:
                    params["top_k"] = config_dict["top_k"]
                if config_dict.get("stop_sequences"):
                    params["stop_sequences"] = config_dict["stop_sequences"]
            
            # Add tools if provided
            if tools:
                params["tools"] = tools
                if tool_choice:
                    params["tool_choice"] = tool_choice
            
            # Make API call
            response = self.client.messages.create(**params)
            
            # Extract content
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
                            "arguments": str(block.input)
                        }
                    })
            
            # Build result
            result = {
                "content": content,
                "role": "assistant",
                "finish_reason": response.stop_reason,
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                }
            }
            
            if tool_calls:
                result["tool_calls"] = tool_calls
            
            # Log request
            latency = (time.time() - start_time) * 1000
            self.log_request("chat_completion", messages, result, latency)
            
            return result
            
        except Exception as e:
            self._handle_error(e)
    
    def completion(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> str:
        """
        Generate text completion (uses chat format for Claude).
        
        Args:
            prompt: Input prompt
            config: Generation configuration
            **kwargs: Additional parameters
        
        Returns:
            Generated text
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
        Stream chat completion responses.
        
        Args:
            messages: List of message dictionaries
            tools: Optional tool definitions
            config: Generation configuration
            **kwargs: Additional parameters
        
        Yields:
            Text chunks as they are generated
        """
        self._check_capability(ModelCapability.STREAMING)
        
        try:
            # Extract system message
            system_message = None
            filtered_messages = []
            
            for msg in messages:
                if msg.get("role") == "system":
                    system_message = msg.get("content", "")
                else:
                    filtered_messages.append(msg)
            
            # Build parameters
            params = {
                "model": self.model_name,
                "messages": filtered_messages,
                "max_tokens": 4096,
                "stream": True
            }
            
            if system_message:
                params["system"] = system_message
            
            if config:
                config_dict = config.to_dict()
                if config_dict.get("max_tokens"):
                    params["max_tokens"] = config_dict["max_tokens"]
                if config_dict.get("temperature") is not None:
                    params["temperature"] = config_dict["temperature"]
            
            if tools:
                params["tools"] = tools
            
            # Stream response
            with self.client.messages.stream(**params) as stream:
                for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            self._handle_error(e)


__all__ = ['AnthropicFacade']
