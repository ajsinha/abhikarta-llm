"""
AWS Bedrock LLM Facade Implementation

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
This module provides a concrete implementation of the LLMFacade interface for AWS Bedrock models.
"""

import os
import json
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


class AWSBedrockFacade(LLMFacadeBase):
    """
    AWS Bedrock implementation of the LLMFacade interface.
    
    Supports multiple models through AWS Bedrock including Claude, Llama, and others.
    
    Example:
        >>> from awsbedrock_facade import AWSBedrockFacade
        >>> llm = AWSBedrockFacade(model_name="anthropic.claude-3-sonnet-20240229-v1:0")
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
        region: str = "us-east-1",
        timeout: Optional[float] = None,
        max_retries: int = 3,
        **kwargs
    ):
        """
        Initialize AWS Bedrock facade.
        
        Args:
            model_name: Model identifier (e.g., "anthropic.claude-3-sonnet-20240229-v1:0")
            api_key: Not used (uses AWS credentials)
            base_url: Not used for Bedrock
            region: AWS region (default: us-east-1)
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts
            **kwargs: Additional configuration (aws_access_key_id, aws_secret_access_key)
        """
        super().__init__(
            provider_name="awsbedrock",
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            **kwargs
        )
        self.region = region
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize AWS Bedrock client."""
        try:
            import boto3
            
            # Create Bedrock runtime client
            session_kwargs = {
                "region_name": self.region
            }
            
            # Add AWS credentials if provided
            if self.kwargs.get("aws_access_key_id"):
                session_kwargs["aws_access_key_id"] = self.kwargs["aws_access_key_id"]
            if self.kwargs.get("aws_secret_access_key"):
                session_kwargs["aws_secret_access_key"] = self.kwargs["aws_secret_access_key"]
            
            self.client = boto3.client('bedrock-runtime', **session_kwargs)
            
            self.logger.info(f"Initialized AWS Bedrock client for {self.model_name}")
            
        except ImportError:
            raise ImportError("Please install boto3: pip install boto3")
        except Exception as e:
            raise AuthenticationException(f"Failed to initialize AWS Bedrock client: {e}")
    
    def _format_for_bedrock(self, messages: Messages) -> Dict[str, Any]:
        """Format messages for Bedrock API based on model provider."""
        # Determine model provider from model_name
        if "anthropic" in self.model_name:
            return self._format_for_anthropic(messages)
        elif "meta" in self.model_name:
            return self._format_for_meta(messages)
        else:
            # Generic format
            return {"prompt": self.format_messages(messages)}
    
    def _format_for_anthropic(self, messages: Messages) -> Dict[str, Any]:
        """Format for Anthropic Claude models on Bedrock."""
        system_message = ""
        formatted_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": formatted_messages,
            "max_tokens": 4096
        }
        
        if system_message:
            body["system"] = system_message
        
        return body
    
    def _format_for_meta(self, messages: Messages) -> Dict[str, Any]:
        """Format for Meta Llama models on Bedrock."""
        prompt = self.format_messages(messages)
        return {
            "prompt": prompt,
            "max_gen_len": 2048,
            "temperature": 0.7,
            "top_p": 0.9
        }
    
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
            # Format body based on model
            body = self._format_for_bedrock(messages)
            
            # Add config
            if config:
                config_dict = config.to_dict()
                if config_dict.get("max_tokens"):
                    body["max_tokens"] = config_dict["max_tokens"]
                if config_dict.get("temperature") is not None:
                    body["temperature"] = config_dict["temperature"]
                if config_dict.get("top_p") is not None:
                    body["top_p"] = config_dict["top_p"]
            
            # Invoke model
            response = self.client.invoke_model(
                modelId=self.model_name,
                body=json.dumps(body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract content based on model type
            if "anthropic" in self.model_name:
                content = response_body.get("content", [{}])[0].get("text", "")
                usage = response_body.get("usage", {})
            elif "meta" in self.model_name:
                content = response_body.get("generation", "")
                usage = {"input_tokens": 0, "output_tokens": 0}
            else:
                content = str(response_body)
                usage = {}
            
            # Build result
            result = {
                "content": content,
                "role": "assistant",
                "finish_reason": "stop",
                "usage": {
                    "prompt_tokens": usage.get("input_tokens", 0),
                    "completion_tokens": usage.get("output_tokens", 0),
                    "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
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
            # Format body
            body = self._format_for_bedrock(messages)
            
            if config:
                config_dict = config.to_dict()
                if config_dict.get("max_tokens"):
                    body["max_tokens"] = config_dict["max_tokens"]
                if config_dict.get("temperature") is not None:
                    body["temperature"] = config_dict["temperature"]
            
            # Invoke with streaming
            response = self.client.invoke_model_with_response_stream(
                modelId=self.model_name,
                body=json.dumps(body)
            )
            
            # Process stream
            for event in response['body']:
                chunk = json.loads(event['chunk']['bytes'])
                
                if "anthropic" in self.model_name:
                    if chunk.get("type") == "content_block_delta":
                        if "delta" in chunk and "text" in chunk["delta"]:
                            yield chunk["delta"]["text"]
                else:
                    # Generic handling
                    if "generation" in chunk:
                        yield chunk["generation"]
                    
        except Exception as e:
            self._handle_error(e)


__all__ = ['AWSBedrockFacade']
