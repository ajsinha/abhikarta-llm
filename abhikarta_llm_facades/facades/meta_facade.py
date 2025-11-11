"""
Meta LLM Facade Implementation

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
This module provides a concrete implementation of the LLMFacade interface for Meta models
including Llama 2, Llama 3, Llama 3.1, Llama 3.2, and Code Llama families via Replicate API.
"""

import os
import json
from typing import List, Dict, Any, Optional, Union, Iterator
import time

from .llm_facade_base import LLMFacadeBase
from .llm_facade import (
    ModelCapability,
    GenerationConfig,
    Messages,
    TextStream,
    ToolDefinition,
    AuthenticationException,
)


class MetaFacade(LLMFacadeBase):
    """
    Meta implementation of the LLMFacade interface via Replicate.
    
    Supports Meta's Llama models including:
    - Llama 3.2 (1B, 3B, 11B Vision, 90B Vision)
    - Llama 3.1 (8B, 70B, 405B) with function calling
    - Llama 3 (8B, 70B)
    - Llama 2 (7B, 13B, 70B)
    - Code Llama (7B, 13B, 34B, 70B) including Python variants
    
    Features:
    - Chat completion for instruct models
    - Text completion for base models
    - Vision capabilities (Llama 3.2 Vision models)
    - Function calling (Llama 3.1 models)
    - Code generation (Code Llama models)
    - Streaming support
    - Large context windows (up to 128K tokens)
    
    Example:
        >>> from meta_facade import MetaFacade
        >>> llm = MetaFacade(model_name="llama-3.1-70b-instruct")
        >>> response = llm.chat_completion([
        ...     {"role": "user", "content": "Explain recursion"}
        ... ])
        >>> print(response["content"])
    """
    
    # Model family mappings for capability detection
    LLAMA_32_MODELS = {
        "llama-3.2-1b-instruct", "llama-3.2-3b-instruct",
        "llama-3.2-11b-vision-instruct", "llama-3.2-90b-vision-instruct"
    }
    
    LLAMA_31_MODELS = {
        "llama-3.1-8b-instruct", "llama-3.1-70b-instruct", 
        "llama-3.1-405b-instruct"
    }
    
    LLAMA_3_MODELS = {
        "llama-3-8b-instruct", "llama-3-70b-instruct"
    }
    
    LLAMA_2_MODELS = {
        "llama-2-7b-chat", "llama-2-13b-chat", "llama-2-70b-chat",
        "llama-2-7b", "llama-2-13b", "llama-2-70b"
    }
    
    CODE_LLAMA_MODELS = {
        "codellama-7b-instruct", "codellama-13b-instruct",
        "codellama-34b-instruct", "codellama-70b-instruct",
        "codellama-7b-python", "codellama-13b-python",
        "codellama-34b-python", "codellama-70b-python"
    }
    
    VISION_MODELS = {
        "llama-3.2-11b-vision-instruct", "llama-3.2-90b-vision-instruct"
    }
    
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
        Initialize Meta facade.
        
        Args:
            model_name: Model identifier (e.g., "llama-3.1-70b-instruct")
            api_key: Replicate API token (reads from REPLICATE_API_TOKEN if None)
            base_url: Custom API endpoint
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts
            **kwargs: Additional configuration
        """
        super().__init__(
            provider_name="meta",
            model_name=model_name,
            api_key=api_key or os.getenv("REPLICATE_API_TOKEN"),
            base_url=base_url or "https://api.replicate.com",
            timeout=timeout,
            max_retries=max_retries,
            **kwargs
        )
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Replicate client for Meta models."""
        try:
            import replicate
            
            if self.api_key:
                os.environ["REPLICATE_API_TOKEN"] = self.api_key
            
            self.client = replicate
            self._get_replicate_model_id()
            
        except ImportError:
            raise ImportError(
                "Please install replicate: pip install replicate"
            )
        except Exception as e:
            raise AuthenticationException(
                f"Failed to initialize Meta/Replicate client: {e}"
            )
    
    def _get_replicate_model_id(self) -> str:
        """Get the Replicate model identifier for the Meta model."""
        # Load model config to get replicate_model
        model_config = self._get_model_config()
        
        if model_config and "replicate_model" in model_config:
            self.replicate_model = model_config["replicate_model"]
        else:
            # Default format: meta/{model_name}
            self.replicate_model = f"meta/{self.model_name}"
        
        self.logger.info(f"Using Replicate model: {self.replicate_model}")
        return self.replicate_model
    
    def _is_chat_model(self) -> bool:
        """Check if model supports chat format."""
        return (
            "instruct" in self.model_name.lower() or
            "chat" in self.model_name.lower()
        )
    
    def _supports_function_calling(self) -> bool:
        """Check if model supports function calling."""
        # Only Llama 3.1 models support native function calling
        return any(model in self.model_name for model in self.LLAMA_31_MODELS)
    
    def _supports_vision(self) -> bool:
        """Check if model supports vision."""
        return any(model in self.model_name for model in self.VISION_MODELS)
    
    def _format_prompt(self, messages: Messages) -> str:
        """Format messages for Llama models."""
        if not self._is_chat_model():
            # For base models, just concatenate content
            return "\n\n".join([
                msg.get("content", "") 
                for msg in messages 
                if isinstance(msg.get("content"), str)
            ])
        
        # For chat models, use Llama format
        formatted_parts = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Handle multimodal content
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                content = "\n".join(text_parts)
            
            # Format based on role
            if role == "system":
                formatted_parts.append(f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{content}<|eot_id|>")
            elif role == "user":
                formatted_parts.append(f"<|start_header_id|>user<|end_header_id|>\n\n{content}<|eot_id|>")
            elif role == "assistant":
                formatted_parts.append(f"<|start_header_id|>assistant<|end_header_id|>\n\n{content}<|eot_id|>")
        
        # Add assistant header for response
        formatted_parts.append("<|start_header_id|>assistant<|end_header_id|>\n\n")
        
        return "".join(formatted_parts)
    
    def chat_completion(
        self,
        messages: Messages,
        tools: Optional[List[ToolDefinition]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate chat completion using Meta Llama models.
        
        Args:
            messages: List of message dictionaries
            tools: Optional tool definitions (Llama 3.1 only)
            tool_choice: Tool selection strategy
            config: Generation configuration
            **kwargs: Additional parameters
        
        Returns:
            Dictionary with completion result
        """
        self._check_capability(ModelCapability.CHAT_COMPLETION)
        
        start_time = time.time()
        
        try:
            # Format prompt for Llama
            prompt = self._format_prompt(messages)
            
            # Build input parameters
            input_params = {
                "prompt": prompt
            }
            
            # Add generation config
            if config:
                config_dict = config.to_dict()
                if config_dict.get("max_tokens"):
                    input_params["max_tokens"] = config_dict["max_tokens"]
                if config_dict.get("temperature") is not None:
                    input_params["temperature"] = config_dict["temperature"]
                if config_dict.get("top_p") is not None:
                    input_params["top_p"] = config_dict["top_p"]
                if config_dict.get("stop_sequences"):
                    input_params["stop_sequences"] = ",".join(config_dict["stop_sequences"])
            
            # Handle function calling for Llama 3.1
            if tools and self._supports_function_calling():
                # Format tools as system message for Llama 3.1
                tools_description = json.dumps(tools, indent=2)
                input_params["system_prompt"] = f"You have access to these tools:\n{tools_description}"
            
            # Run prediction
            output = self.client.run(
                self.replicate_model,
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
            
            # Parse tool calls if present (Llama 3.1)
            if tools and self._supports_function_calling():
                tool_calls = self.parse_tool_calls(result)
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
        Generate text completion.
        
        Args:
            prompt: Input prompt
            config: Generation configuration
            **kwargs: Additional parameters
        
        Returns:
            Generated text
        """
        # For chat models, convert to messages
        if self._is_chat_model():
            response = self.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                config=config,
                **kwargs
            )
            return response["content"]
        
        # For base models, use direct completion
        try:
            input_params = {"prompt": prompt}
            
            if config:
                config_dict = config.to_dict()
                if config_dict.get("max_tokens"):
                    input_params["max_tokens"] = config_dict["max_tokens"]
                if config_dict.get("temperature") is not None:
                    input_params["temperature"] = config_dict["temperature"]
            
            output = self.client.run(
                self.replicate_model,
                input=input_params
            )
            
            # Collect output
            if hasattr(output, '__iter__') and not isinstance(output, str):
                return "".join(output)
            return str(output)
            
        except Exception as e:
            self._handle_error(e)
    
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
            prompt = self._format_prompt(messages)
            
            input_params = {"prompt": prompt}
            
            if config:
                config_dict = config.to_dict()
                if config_dict.get("max_tokens"):
                    input_params["max_tokens"] = config_dict["max_tokens"]
                if config_dict.get("temperature") is not None:
                    input_params["temperature"] = config_dict["temperature"]
            
            # Stream from Replicate
            for chunk in self.client.stream(
                self.replicate_model,
                input=input_params
            ):
                if chunk:
                    yield str(chunk)
                    
        except Exception as e:
            self._handle_error(e)
    
    def parse_tool_calls(
        self,
        response: Dict[str, Any],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Extract tool calls from Llama 3.1 response.
        
        Args:
            response: LLM response
            **kwargs: Additional parameters
        
        Returns:
            List of parsed tool calls
        """
        if not self._supports_function_calling():
            return []
        
        content = response.get("content", "")
        tool_calls = []
        
        # Try to parse JSON function calls from content
        try:
            # Look for function call patterns in Llama 3.1 output
            import re
            
            # Pattern: {"name": "function_name", "arguments": {...}}
            pattern = r'\{[^}]*"name"\s*:\s*"([^"]+)"[^}]*"arguments"\s*:\s*(\{[^}]+\})[^}]*\}'
            matches = re.finditer(pattern, content)
            
            for i, match in enumerate(matches):
                function_name = match.group(1)
                arguments_str = match.group(2)
                
                tool_calls.append({
                    "id": f"call_{i}",
                    "type": "function",
                    "function": {
                        "name": function_name,
                        "arguments": arguments_str
                    }
                })
        
        except Exception as e:
            self.logger.warning(f"Could not parse tool calls: {e}")
        
        return tool_calls


__all__ = ['MetaFacade']
