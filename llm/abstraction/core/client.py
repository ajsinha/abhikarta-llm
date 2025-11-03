"""
LLM Client - Main User Interface

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

from typing import List, Dict, Any, Iterator, Optional
from .facade import LLMFacade, Message, CompletionResponse, ChatResponse
from .history import InteractionHistory, Interaction
from .exceptions import ValidationError


class LLMClient:
    """
    High-level client for LLM operations.
    
    Provides convenience methods and maintains interaction history.
    Delegates actual LLM operations to the facade.
    """
    
    def __init__(
        self,
        facade: LLMFacade,
        provider_name: str,
        model_name: str,
        history_size: int = 50
    ):
        """
        Initialize LLM client.
        
        Args:
            facade: LLMFacade instance
            provider_name: Provider name
            model_name: Model name
            history_size: Maximum history size
        """
        self.facade = facade
        self.provider_name = provider_name
        self.model_name = model_name
        self.history = InteractionHistory(max_size=history_size)
        self._conversation_messages: List[Message] = []
    
    def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """
        Generate completion for a prompt.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text
            
        Raises:
            ValidationError: If input is invalid
            APIError: If API call fails
        """
        if not prompt or not prompt.strip():
            raise ValidationError("Prompt cannot be empty")
        
        # Call facade
        response = self.facade.complete(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Record in history
        interaction = Interaction(
            prompt=prompt,
            response=response.text,
            model=self.model_name,
            provider=self.provider_name,
            tokens_used=response.tokens_used,
            cost=self._calculate_cost(response),
            metadata=response.metadata
        )
        self.history.add(interaction)
        
        return response.text
    
    def chat(
        self,
        message: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        use_history: bool = True,
        **kwargs
    ) -> str:
        """
        Send a chat message and get response.
        
        Args:
            message: User message
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            use_history: Whether to include conversation history
            **kwargs: Additional parameters
            
        Returns:
            Assistant's response text
            
        Raises:
            ValidationError: If input is invalid
            APIError: If API call fails
        """
        if not message or not message.strip():
            raise ValidationError("Message cannot be empty")
        
        # Add user message to conversation
        user_msg = Message(role="user", content=message)
        
        # Build message list
        if use_history:
            messages = self._conversation_messages + [user_msg]
        else:
            messages = [user_msg]
        
        # Call facade
        response = self.facade.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Update conversation history
        if use_history:
            self._conversation_messages.append(user_msg)
            self._conversation_messages.append(response.message)
        
        # Record in interaction history
        interaction = Interaction(
            prompt=message,
            response=response.message.content,
            model=self.model_name,
            provider=self.provider_name,
            tokens_used=response.tokens_used,
            cost=self._calculate_cost_from_chat(response),
            metadata=response.metadata
        )
        self.history.add(interaction)
        
        return response.message.content
    
    def stream_complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Iterator[str]:
        """
        Stream completion tokens.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Yields:
            Token strings
            
        Raises:
            ValidationError: If input is invalid
            APIError: If API call fails
        """
        if not prompt or not prompt.strip():
            raise ValidationError("Prompt cannot be empty")
        
        full_response = []
        
        for token in self.facade.stream_complete(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        ):
            full_response.append(token)
            yield token
        
        # Record in history after streaming completes
        response_text = ''.join(full_response)
        tokens_used = self.facade.count_tokens(prompt) + self.facade.count_tokens(response_text)
        
        interaction = Interaction(
            prompt=prompt,
            response=response_text,
            model=self.model_name,
            provider=self.provider_name,
            tokens_used=tokens_used,
            cost=self.facade.estimate_cost(
                self.facade.count_tokens(prompt),
                self.facade.count_tokens(response_text)
            ),
            metadata={'streaming': True}
        )
        self.history.add(interaction)
    
    def stream_chat(
        self,
        message: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        use_history: bool = True,
        **kwargs
    ) -> Iterator[str]:
        """
        Stream chat response tokens.
        
        Args:
            message: User message
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            use_history: Whether to include conversation history
            **kwargs: Additional parameters
            
        Yields:
            Token strings
        """
        if not message or not message.strip():
            raise ValidationError("Message cannot be empty")
        
        user_msg = Message(role="user", content=message)
        
        if use_history:
            messages = self._conversation_messages + [user_msg]
        else:
            messages = [user_msg]
        
        full_response = []
        
        for token in self.facade.stream_chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        ):
            full_response.append(token)
            yield token
        
        # Update conversation and history
        response_text = ''.join(full_response)
        assistant_msg = Message(role="assistant", content=response_text)
        
        if use_history:
            self._conversation_messages.append(user_msg)
            self._conversation_messages.append(assistant_msg)
        
        tokens_used = sum(self.facade.count_tokens(m.content) for m in messages) + \
                      self.facade.count_tokens(response_text)
        
        interaction = Interaction(
            prompt=message,
            response=response_text,
            model=self.model_name,
            provider=self.provider_name,
            tokens_used=tokens_used,
            metadata={'streaming': True}
        )
        self.history.add(interaction)
    
    def batch_complete(
        self,
        prompts: List[str],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> List[str]:
        """
        Process multiple prompts in batch.
        
        Args:
            prompts: List of prompts
            temperature: Sampling temperature
            max_tokens: Maximum tokens per response
            **kwargs: Additional parameters
            
        Returns:
            List of responses
        """
        results = []
        for prompt in prompts:
            try:
                response = self.complete(
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                results.append(response)
            except Exception as e:
                results.append(f"Error: {str(e)}")
        
        return results
    
    def clear_conversation(self) -> None:
        """Clear the conversation message history"""
        self._conversation_messages.clear()
    
    def get_conversation(self) -> List[Message]:
        """Get current conversation messages"""
        return self._conversation_messages.copy()
    
    def set_system_message(self, content: str) -> None:
        """
        Set system message for conversation.
        
        Args:
            content: System message content
        """
        # Remove existing system messages
        self._conversation_messages = [
            m for m in self._conversation_messages if m.role != 'system'
        ]
        
        # Add new system message at the beginning
        system_msg = Message(role="system", content=content)
        self._conversation_messages.insert(0, system_msg)
    
    def get_history_summary(self) -> Dict[str, Any]:
        """
        Get summary of interaction history.
        
        Returns:
            Dictionary containing history statistics
        """
        return self.history.get_statistics()
    
    def export_history(self, filepath: str) -> None:
        """
        Export interaction history to file.
        
        Args:
            filepath: Output file path
        """
        self.history.export_to_json(filepath)
    
    def _calculate_cost(self, response: CompletionResponse) -> float:
        """Calculate cost from completion response"""
        try:
            model_info = self.facade.get_model_info()
            # Rough estimate: assume 50% input, 50% output
            total_tokens = response.tokens_used
            input_tokens = total_tokens // 2
            output_tokens = total_tokens - input_tokens
            return self.facade.estimate_cost(input_tokens, output_tokens)
        except:
            return 0.0
    
    def _calculate_cost_from_chat(self, response: ChatResponse) -> float:
        """Calculate cost from chat response"""
        try:
            model_info = self.facade.get_model_info()
            total_tokens = response.tokens_used
            input_tokens = total_tokens // 2
            output_tokens = total_tokens - input_tokens
            return self.facade.estimate_cost(input_tokens, output_tokens)
        except:
            return 0.0
    
    def __repr__(self) -> str:
        return f"LLMClient(provider={self.provider_name}, model={self.model_name})"
