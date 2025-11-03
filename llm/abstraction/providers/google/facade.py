"""
Google (Gemini) LLM Facade

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


class GoogleFacade(LLMFacade):
    """
    Facade for Google's Gemini models.
    
    Wraps the Google Generative AI API and provides a consistent interface.
    """
    
    def __init__(self, provider: LLMProvider, model_name: str, client: Any):
        super().__init__(provider, model_name)
        self.client = client
        self.model = client.GenerativeModel(model_name)
    
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        """
        Generate completion using Gemini.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Returns:
            CompletionResponse object
        """
        try:
            generation_config = {
                "temperature": kwargs.get('temperature', 0.7),
                "max_output_tokens": kwargs.get('max_tokens', 1000),
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            text = response.text if hasattr(response, 'text') else str(response)
            
            # Estimate token count (Gemini doesn't always provide exact counts)
            tokens_used = len(prompt.split()) + len(text.split())
            
            return CompletionResponse(
                text=text,
                model=self.model_name,
                provider='google',
                tokens_used=tokens_used,
                finish_reason='complete',
                metadata={
                    'prompt_feedback': getattr(response, 'prompt_feedback', None)
                }
            )
        except Exception as e:
            raise APIError(f"Google API error: {str(e)}", provider='google')
    
    def chat(self, messages: List[Message], **kwargs) -> ChatResponse:
        """
        Generate chat response using Gemini.
        
        Args:
            messages: List of Message objects
            **kwargs: Additional parameters
            
        Returns:
            ChatResponse object
        """
        try:
            generation_config = {
                "temperature": kwargs.get('temperature', 0.7),
                "max_output_tokens": kwargs.get('max_tokens', 1000),
            }
            
            # Start a chat session
            chat = self.model.start_chat(history=[])
            
            # Add previous messages to history
            for msg in messages[:-1]:
                if msg.role == 'user':
                    chat.send_message(msg.content)
            
            # Send the last message and get response
            last_message = messages[-1].content
            response = chat.send_message(
                last_message,
                generation_config=generation_config
            )
            
            text = response.text if hasattr(response, 'text') else str(response)
            
            response_message = Message(
                role='assistant',
                content=text
            )
            
            # Estimate token count
            total_content = ' '.join(m.content for m in messages) + text
            tokens_used = len(total_content.split())
            
            return ChatResponse(
                message=response_message,
                model=self.model_name,
                provider='google',
                tokens_used=tokens_used,
                finish_reason='complete',
                metadata={}
            )
        except Exception as e:
            raise APIError(f"Google API error: {str(e)}", provider='google')
    
    def stream_complete(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Stream completion tokens using Gemini.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Yields:
            Token strings
        """
        try:
            generation_config = {
                "temperature": kwargs.get('temperature', 0.7),
                "max_output_tokens": kwargs.get('max_tokens', 1000),
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                stream=True
            )
            
            for chunk in response:
                if hasattr(chunk, 'text'):
                    yield chunk.text
        except Exception as e:
            raise APIError(f"Google streaming error: {str(e)}", provider='google')
    
    def stream_chat(self, messages: List[Message], **kwargs) -> Iterator[str]:
        """
        Stream chat response tokens using Gemini.
        
        Args:
            messages: List of Message objects
            **kwargs: Additional parameters
            
        Yields:
            Token strings
        """
        try:
            generation_config = {
                "temperature": kwargs.get('temperature', 0.7),
                "max_output_tokens": kwargs.get('max_tokens', 1000),
            }
            
            chat = self.model.start_chat(history=[])
            
            # Add previous messages
            for msg in messages[:-1]:
                if msg.role == 'user':
                    chat.send_message(msg.content)
            
            # Stream the last message
            last_message = messages[-1].content
            response = chat.send_message(
                last_message,
                generation_config=generation_config,
                stream=True
            )
            
            for chunk in response:
                if hasattr(chunk, 'text'):
                    yield chunk.text
        except Exception as e:
            raise APIError(f"Google streaming error: {str(e)}", provider='google')
    
    def get_model_info(self) -> ModelInfo:
        """
        Get Gemini model information.
        
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
            context_window=model_config.get('context_window', 32000),
            max_output=model_config.get('max_output', 8192),
            capabilities=model_config.get('capabilities', {}),
            cost=model_config.get('cost', {}),
            metadata={'provider': 'google'}
        )
        
        return self.model_info_cache
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        try:
            # Try to use Gemini's token counting if available
            result = self.model.count_tokens(text)
            return result.total_tokens
        except:
            # Fallback to rough estimate
            return len(text) // 4
