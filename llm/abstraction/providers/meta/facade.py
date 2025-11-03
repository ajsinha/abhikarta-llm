"""
Meta (Llama) LLM Facade via Replicate

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


class MetaFacade(LLMFacade):
    """
    Facade for Meta's Llama models via Replicate.
    
    Wraps the Replicate API and provides a consistent interface.
    """
    
    def __init__(self, provider: LLMProvider, model_name: str, client: Any):
        super().__init__(provider, model_name)
        self.client = client
        # Get the replicate model version from config
        model_config = provider.get_model_info(model_name)
        self.replicate_model = model_config.get('replicate_model', 'meta/llama-2-70b-chat')
    
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        """
        Generate completion using Llama.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Returns:
            CompletionResponse object
        """
        try:
            input_params = {
                "prompt": prompt,
                "temperature": kwargs.get('temperature', 0.7),
                "max_new_tokens": kwargs.get('max_tokens', 1000),
                "top_p": kwargs.get('top_p', 1.0),
            }
            
            output = self.client.run(self.replicate_model, input=input_params)
            
            # Replicate returns iterator, join it
            if hasattr(output, '__iter__') and not isinstance(output, str):
                text = ''.join(output)
            else:
                text = str(output)
            
            tokens_used = len(prompt.split()) + len(text.split())
            
            return CompletionResponse(
                text=text,
                model=self.model_name,
                provider='meta',
                tokens_used=tokens_used,
                finish_reason='complete',
                metadata={'replicate_model': self.replicate_model}
            )
        except Exception as e:
            raise APIError(f"Meta/Replicate API error: {str(e)}", provider='meta')
    
    def chat(self, messages: List[Message], **kwargs) -> ChatResponse:
        """
        Generate chat response using Llama.
        
        Args:
            messages: List of Message objects
            **kwargs: Additional parameters
            
        Returns:
            ChatResponse object
        """
        try:
            # Format messages for Llama chat format
            prompt = self._format_chat_prompt(messages)
            
            input_params = {
                "prompt": prompt,
                "temperature": kwargs.get('temperature', 0.7),
                "max_new_tokens": kwargs.get('max_tokens', 1000),
                "top_p": kwargs.get('top_p', 1.0),
            }
            
            output = self.client.run(self.replicate_model, input=input_params)
            
            # Replicate returns iterator, join it
            if hasattr(output, '__iter__') and not isinstance(output, str):
                text = ''.join(output)
            else:
                text = str(output)
            
            response_message = Message(
                role='assistant',
                content=text.strip()
            )
            
            total_content = ' '.join(m.content for m in messages) + text
            tokens_used = len(total_content.split())
            
            return ChatResponse(
                message=response_message,
                model=self.model_name,
                provider='meta',
                tokens_used=tokens_used,
                finish_reason='complete',
                metadata={'replicate_model': self.replicate_model}
            )
        except Exception as e:
            raise APIError(f"Meta/Replicate API error: {str(e)}", provider='meta')
    
    def stream_complete(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Stream completion tokens using Llama.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Yields:
            Token strings
        """
        try:
            input_params = {
                "prompt": prompt,
                "temperature": kwargs.get('temperature', 0.7),
                "max_new_tokens": kwargs.get('max_tokens', 1000),
            }
            
            for output in self.client.stream(self.replicate_model, input=input_params):
                yield str(output)
        except Exception as e:
            raise APIError(f"Meta/Replicate streaming error: {str(e)}", provider='meta')
    
    def stream_chat(self, messages: List[Message], **kwargs) -> Iterator[str]:
        """
        Stream chat response tokens using Llama.
        
        Args:
            messages: List of Message objects
            **kwargs: Additional parameters
            
        Yields:
            Token strings
        """
        try:
            prompt = self._format_chat_prompt(messages)
            
            input_params = {
                "prompt": prompt,
                "temperature": kwargs.get('temperature', 0.7),
                "max_new_tokens": kwargs.get('max_tokens', 1000),
            }
            
            for output in self.client.stream(self.replicate_model, input=input_params):
                yield str(output)
        except Exception as e:
            raise APIError(f"Meta/Replicate streaming error: {str(e)}", provider='meta')
    
    def get_model_info(self) -> ModelInfo:
        """
        Get Llama model information.
        
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
            context_window=model_config.get('context_window', 4096),
            max_output=model_config.get('max_output', 2048),
            capabilities=model_config.get('capabilities', {}),
            cost=model_config.get('cost', {}),
            metadata={'provider': 'meta', 'replicate_model': self.replicate_model}
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
        # Rough estimate: ~4 characters per token
        return len(text) // 4
    
    def _format_chat_prompt(self, messages: List[Message]) -> str:
        """
        Format messages into Llama chat prompt format.
        
        Args:
            messages: List of Message objects
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        for msg in messages:
            if msg.role == 'system':
                prompt_parts.append(f"<<SYS>>\n{msg.content}\n<</SYS>>\n\n")
            elif msg.role == 'user':
                prompt_parts.append(f"[INST] {msg.content} [/INST]")
            elif msg.role == 'assistant':
                prompt_parts.append(f" {msg.content} ")
        
        return ''.join(prompt_parts)
