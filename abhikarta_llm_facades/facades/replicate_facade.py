"""
Replicate LLM Facade Implementation

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
This module provides a concrete implementation of the LLMFacade interface for Replicate models.
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


class ReplicateFacade(LLMFacadeBase):
    """
    Replicate implementation of the LLMFacade interface.
    
    Example:
        >>> from replicate_facade import ReplicateFacade
        >>> llm = ReplicateFacade(model_name="meta/llama-2-70b-chat")
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
        Initialize Replicate facade.
        
        Args:
            model_name: Model identifier (e.g., "meta/llama-2-70b-chat")
            api_key: API token (reads from REPLICATE_API_TOKEN if None)
            base_url: Custom API endpoint
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts
            **kwargs: Additional configuration
        """
        super().__init__(
            provider_name="replicate",
            model_name=model_name,
            api_key=api_key or os.getenv('REPLICATE_API_TOKEN'),
            base_url=base_url or "https://api.replicate.com",
            timeout=timeout,
            max_retries=max_retries,
            **kwargs
        )
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Replicate client."""
        try:
            import replicate
            
            if self.api_key:
                os.environ["REPLICATE_API_TOKEN"] = self.api_key
            
            self.client = replicate
            
            self.logger.info(f"Initialized Replicate client for {self.model_name}")
            
        except ImportError:
            raise ImportError("Please install replicate: pip install replicate")
        except Exception as e:
            raise AuthenticationException(f"Failed to initialize Replicate client: {e}")
    
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
            # Format prompt
            prompt = self.format_messages(messages)
            
            # Build input parameters
            input_params = {"prompt": prompt}
            
            if config:
                config_dict = config.to_dict()
                if config_dict.get("max_tokens"):
                    input_params["max_new_tokens"] = config_dict["max_tokens"]
                if config_dict.get("temperature") is not None:
                    input_params["temperature"] = config_dict["temperature"]
                if config_dict.get("top_p") is not None:
                    input_params["top_p"] = config_dict["top_p"]
            
            # Run prediction
            output = self.client.run(
                self.model_name,
                input=input_params
            )
            
            # Collect output
            if hasattr(output, '__iter__') and not isinstance(output, str):
                content = "".join(output)
            else:
                content = str(output)
            
            # Build result
            result = {
                "content": content.strip(),
                "role": "assistant",
                "finish_reason": "stop",
                "usage": {
                    "prompt_tokens": self.count_tokens(prompt),
                    "completion_tokens": self.count_tokens(content),
                    "total_tokens": self.count_tokens(prompt) + self.count_tokens(content)
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
            prompt = self.format_messages(messages)
            
            input_params = {"prompt": prompt}
            
            if config:
                config_dict = config.to_dict()
                if config_dict.get("max_tokens"):
                    input_params["max_new_tokens"] = config_dict["max_tokens"]
                if config_dict.get("temperature") is not None:
                    input_params["temperature"] = config_dict["temperature"]
            
            # Stream from Replicate
            for chunk in self.client.stream(
                self.model_name,
                input=input_params
            ):
                if chunk:
                    yield str(chunk)
                    
        except Exception as e:
            self._handle_error(e)


__all__ = ['ReplicateFacade']
