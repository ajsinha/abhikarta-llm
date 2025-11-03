"""
Anthropic LLM Facade

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

from typing import List, Iterator, Any
from ...core.facade import (
    LLMFacade,
    Message,
    CompletionResponse,
    ChatResponse,
    ModelInfo
)
from ...core.provider import LLMProvider
from ...core.exceptions import APIError


class AnthropicFacade(LLMFacade):
    """
    Facade for Anthropic's Claude models.
    
    Wraps the Anthropic API client and provides a consistent interface.
    """
    
    def __init__(self, provider: LLMProvider, model_name: str, client: Any):
        super().__init__(provider, model_name)
        self.client = client
    
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        """
        Generate completion using Claude.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Returns:
            CompletionResponse object
        """
        try:
            # Anthropic uses messages format, so wrap prompt in a user message
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract text from response
            text = response.content[0].text if response.content else ""
            
            return CompletionResponse(
                text=text,
                model=self.model_name,
                provider='anthropic',
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                finish_reason=response.stop_reason or 'complete',
                metadata={
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens
                }
            )
        except Exception as e:
            raise APIError(f"Anthropic API error: {str(e)}", provider='anthropic')
    
    def chat(self, messages: List[Message], **kwargs) -> ChatResponse:
        """
        Generate chat response using Claude.
        
        Args:
            messages: List of Message objects
            **kwargs: Additional parameters
            
        Returns:
            ChatResponse object
        """
        try:
            # Convert Message objects to Anthropic format
            anthropic_messages = []
            system_message = None
            
            for msg in messages:
                if msg.role == 'system':
                    system_message = msg.content
                else:
                    anthropic_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            # Build request parameters
            request_params = {
                "model": self.model_name,
                "max_tokens": kwargs.get('max_tokens', 1000),
                "temperature": kwargs.get('temperature', 0.7),
                "messages": anthropic_messages
            }
            
            if system_message:
                request_params["system"] = system_message
            
            response = self.client.messages.create(**request_params)
            
            # Extract response text
            text = response.content[0].text if response.content else ""
            
            response_message = Message(
                role='assistant',
                content=text
            )
            
            return ChatResponse(
                message=response_message,
                model=self.model_name,
                provider='anthropic',
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                finish_reason=response.stop_reason or 'complete',
                metadata={
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens
                }
            )
        except Exception as e:
            raise APIError(f"Anthropic API error: {str(e)}", provider='anthropic')
    
    def stream_complete(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Stream completion tokens using Claude.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Yields:
            Token strings
        """
        try:
            with self.client.messages.stream(
                model=self.model_name,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7),
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            raise APIError(f"Anthropic streaming error: {str(e)}", provider='anthropic')
    
    def stream_chat(self, messages: List[Message], **kwargs) -> Iterator[str]:
        """
        Stream chat response tokens using Claude.
        
        Args:
            messages: List of Message objects
            **kwargs: Additional parameters
            
        Yields:
            Token strings
        """
        try:
            # Convert Message objects to Anthropic format
            anthropic_messages = []
            system_message = None
            
            for msg in messages:
                if msg.role == 'system':
                    system_message = msg.content
                else:
                    anthropic_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            request_params = {
                "model": self.model_name,
                "max_tokens": kwargs.get('max_tokens', 1000),
                "temperature": kwargs.get('temperature', 0.7),
                "messages": anthropic_messages
            }
            
            if system_message:
                request_params["system"] = system_message
            
            with self.client.messages.stream(**request_params) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            raise APIError(f"Anthropic streaming error: {str(e)}", provider='anthropic')
    
    def get_model_info(self) -> ModelInfo:
        """
        Get Claude model information.
        
        Returns:
            ModelInfo object
        """
        if self.model_info_cache:
            return self.model_info_cache
        
        model_config = self.provider.get_model_info(self.model_name)
        
        self.model_info_cache = ModelInfo(
            name=model_config.get('name', self.model_name),
            version=model_config.get('version', ''),
            description=model_config.get('description', ''),
            context_window=model_config.get('context_window', 200000),
            max_output=model_config.get('max_output', 4096),
            capabilities=model_config.get('capabilities', {}),
            cost=model_config.get('cost', {}),
            metadata={'provider': 'anthropic'}
        )
        
        return self.model_info_cache
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count (rough approximation)
        """
        # Rough estimate: ~4 characters per token for English text
        return len(text) // 4
