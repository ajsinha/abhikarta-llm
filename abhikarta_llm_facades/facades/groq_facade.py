"""
Groq LLM Facade Implementation

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
This module provides a concrete implementation of the LLMFacade interface for Groq models.
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


class GroqFacade(LLMFacadeBase):
    """
    Groq implementation of the LLMFacade interface.
    
    Example:
        >>> from groq_facade import GroqFacade
        >>> llm = GroqFacade(model_name="llama2-70b-4096")
        >>> response = llm.chat_completion([
        ...     {"role": "user", "content": "Hello!"}
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
        Initialize Groq facade.
        
        Args:
            model_name: Model identifier
            api_key: API key (reads from GROQ_API_KEY if None)
            base_url: Custom API endpoint
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts
            **kwargs: Additional configuration
        """
        super().__init__(
            provider_name="groq",
            model_name=model_name,
            api_key=api_key or os.getenv('GROQ_API_KEY'),
            base_url=base_url or "https://api.groq.com",
            timeout=timeout,
            max_retries=max_retries,
            **kwargs
        )
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Groq client."""
        try:
            from groq import Groq
            
            self.client = Groq(
                api_key=self.api_key,
                timeout=self.timeout,
                max_retries=self.max_retries
            )
            
            self.logger.info(f"Initialized Groq client for {self.model_name}")
            
        except ImportError:
            raise ImportError("Please install groq: pip install groq")
        except Exception as e:
            raise AuthenticationException(f"Failed to initialize Groq client: {e}")
    
    def chat_completion(
        self,
        messages: Messages,
        tools: Optional[List[ToolDefinition]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate chat completion.
        
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
            # Build request parameters
            params = {
                "model": self.model_name,
                "messages": messages
            }
            
            if config:
                config_dict = config.to_dict()
                if config_dict.get("max_tokens"):
                    params["max_tokens"] = config_dict["max_tokens"]
                if config_dict.get("temperature") is not None:
                    params["temperature"] = config_dict["temperature"]
                if config_dict.get("top_p") is not None:
                    params["top_p"] = config_dict["top_p"]
                if config_dict.get("stop_sequences"):
                    params["stop"] = config_dict["stop_sequences"]
            
            if tools:
                params["tools"] = tools
                if tool_choice:
                    params["tool_choice"] = tool_choice
            
            # Generate response
            response = self.client.chat.completions.create(**params)
            
            # Extract message
            message = response.choices[0].message
            
            # Build result
            result = {
                "content": message.content or "",
                "role": message.role,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            if message.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            
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
        Generate text completion.
        
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
            # Streaming implementation varies by provider
            # Fallback to non-streaming for now
            result = self.chat_completion(messages, tools, None, config, **kwargs)
            yield result["content"]
            
        except Exception as e:
            self._handle_error(e)


__all__ = ['GroqFacade']
