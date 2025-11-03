"""
OpenAI LLM Facade

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


class OpenAIFacade(LLMFacade):
    """
    Facade for OpenAI's GPT models.
    
    Wraps the OpenAI API client and provides a consistent interface.
    """
    
    def __init__(self, provider: LLMProvider, model_name: str, client: Any):
        super().__init__(provider, model_name)
        self.client = client
    
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        """
        Generate completion using GPT.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Returns:
            CompletionResponse object
        """
        try:
            # OpenAI uses chat format even for completions
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7)
            )
            
            text = response.choices[0].message.content
            
            return CompletionResponse(
                text=text,
                model=self.model_name,
                provider='openai',
                tokens_used=response.usage.total_tokens,
                finish_reason=response.choices[0].finish_reason,
                metadata={
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens
                }
            )
        except Exception as e:
            raise APIError(f"OpenAI API error: {str(e)}", provider='openai')
    
    def chat(self, messages: List[Message], **kwargs) -> ChatResponse:
        """
        Generate chat response using GPT.
        
        Args:
            messages: List of Message objects
            **kwargs: Additional parameters
            
        Returns:
            ChatResponse object
        """
        try:
            # Convert Message objects to OpenAI format
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7)
            )
            
            text = response.choices[0].message.content
            
            response_message = Message(
                role='assistant',
                content=text
            )
            
            return ChatResponse(
                message=response_message,
                model=self.model_name,
                provider='openai',
                tokens_used=response.usage.total_tokens,
                finish_reason=response.choices[0].finish_reason,
                metadata={
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens
                }
            )
        except Exception as e:
            raise APIError(f"OpenAI API error: {str(e)}", provider='openai')
    
    def stream_complete(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Stream completion tokens using GPT.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Yields:
            Token strings
        """
        try:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7),
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise APIError(f"OpenAI streaming error: {str(e)}", provider='openai')
    
    def stream_chat(self, messages: List[Message], **kwargs) -> Iterator[str]:
        """
        Stream chat response tokens using GPT.
        
        Args:
            messages: List of Message objects
            **kwargs: Additional parameters
            
        Yields:
            Token strings
        """
        try:
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7),
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise APIError(f"OpenAI streaming error: {str(e)}", provider='openai')
    
    def get_model_info(self) -> ModelInfo:
        """
        Get GPT model information.
        
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
            context_window=model_config.get('context_window', 8192),
            max_output=model_config.get('max_output', 4096),
            capabilities=model_config.get('capabilities', {}),
            cost=model_config.get('cost', {}),
            metadata={'provider': 'openai'}
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
