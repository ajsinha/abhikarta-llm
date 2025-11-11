"""
Ollama LLM Facade Implementation

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
This module provides a concrete implementation of the LLMFacade interface for Ollama local models.
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


class OllamaFacade(LLMFacadeBase):
    """
    Ollama implementation of the LLMFacade interface.
    
    Supports local model execution via Ollama. No API key required.
    
    Example:
        >>> from ollama_facade import OllamaFacade
        >>> llm = OllamaFacade(model_name="llama2")
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
        Initialize Ollama facade.
        
        Args:
            model_name: Model identifier (e.g., "llama2", "mistral")
            api_key: Not required for Ollama
            base_url: Ollama server URL (default: http://localhost:11434)
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts
            **kwargs: Additional configuration
        """
        super().__init__(
            provider_name="ollama",
            model_name=model_name,
            api_key=api_key,
            base_url=base_url or "http://localhost:11434",
            timeout=timeout,
            max_retries=max_retries,
            **kwargs
        )
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Ollama client."""
        try:
            import ollama
            
            # Create client pointing to the base URL
            self.client = ollama.Client(host=self.base_url)
            
            self.logger.info(f"Initialized Ollama client for {self.model_name}")
            
        except ImportError:
            raise ImportError("Please install ollama: pip install ollama")
        except Exception as e:
            self.logger.warning(f"Ollama client initialization: {e}")
            # Ollama might still work without client object
            self.client = None
    
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
            # Build options
            options = {}
            if config:
                config_dict = config.to_dict()
                if config_dict.get("temperature") is not None:
                    options["temperature"] = config_dict["temperature"]
                if config_dict.get("top_p") is not None:
                    options["top_p"] = config_dict["top_p"]
                if config_dict.get("top_k") is not None:
                    options["top_k"] = config_dict["top_k"]
                if config_dict.get("stop_sequences"):
                    options["stop"] = config_dict["stop_sequences"]
            
            # Generate response
            if self.client:
                response = self.client.chat(
                    model=self.model_name,
                    messages=messages,
                    options=options if options else None
                )
            else:
                import ollama
                response = ollama.chat(
                    model=self.model_name,
                    messages=messages,
                    options=options if options else None
                )
            
            # Build result
            result = {
                "content": response['message']['content'],
                "role": "assistant",
                "finish_reason": "stop",
                "usage": {
                    "prompt_tokens": response.get('prompt_eval_count', 0),
                    "completion_tokens": response.get('eval_count', 0),
                    "total_tokens": response.get('prompt_eval_count', 0) + response.get('eval_count', 0)
                }
            }
            
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
            options = {}
            if config:
                config_dict = config.to_dict()
                if config_dict.get("temperature") is not None:
                    options["temperature"] = config_dict["temperature"]
            
            # Stream response
            if self.client:
                stream = self.client.chat(
                    model=self.model_name,
                    messages=messages,
                    options=options if options else None,
                    stream=True
                )
            else:
                import ollama
                stream = ollama.chat(
                    model=self.model_name,
                    messages=messages,
                    options=options if options else None,
                    stream=True
                )
            
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
                    
        except Exception as e:
            self._handle_error(e)


__all__ = ['OllamaFacade']
