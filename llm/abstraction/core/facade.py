"""
Abstract LLM Facade Interface

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Iterator, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Message:
    """Represents a chat message"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompletionResponse:
    """Response from completion operation"""
    text: str
    model: str
    provider: str
    tokens_used: int = 0
    finish_reason: str = "complete"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ChatResponse:
    """Response from chat operation"""
    message: Message
    model: str
    provider: str
    tokens_used: int = 0
    finish_reason: str = "complete"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ModelInfo:
    """Model information"""
    name: str
    version: str
    description: str
    context_window: int
    max_output: int
    capabilities: Dict[str, bool] = field(default_factory=dict)
    cost: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class LLMFacade(ABC):
    """
    Abstract facade for LLM operations.
    
    Provides a simplified, consistent interface to underlying LLM provider.
    """
    
    def __init__(self, provider: 'LLMProvider', model_name: str):
        self.provider = provider
        self.model_name = model_name
        self.model_info_cache: Optional[ModelInfo] = None
    
    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        """
        Generate completion for a prompt.
        
        Args:
            prompt: Input prompt text
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            CompletionResponse object
            
        Raises:
            APIError: If API call fails
            ValidationError: If input is invalid
        """
        pass
    
    @abstractmethod
    def chat(self, messages: List[Message], **kwargs) -> ChatResponse:
        """
        Generate chat response for message history.
        
        Args:
            messages: List of Message objects
            **kwargs: Additional parameters
            
        Returns:
            ChatResponse object
            
        Raises:
            APIError: If API call fails
            ValidationError: If input is invalid
        """
        pass
    
    @abstractmethod
    def stream_complete(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Stream completion tokens as they are generated.
        
        Args:
            prompt: Input prompt text
            **kwargs: Additional parameters
            
        Yields:
            Token strings
            
        Raises:
            APIError: If API call fails
            ValidationError: If input is invalid
        """
        pass
    
    @abstractmethod
    def stream_chat(self, messages: List[Message], **kwargs) -> Iterator[str]:
        """
        Stream chat response tokens.
        
        Args:
            messages: List of Message objects
            **kwargs: Additional parameters
            
        Yields:
            Token strings
            
        Raises:
            APIError: If API call fails
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> ModelInfo:
        """
        Get information about the current model.
        
        Returns:
            ModelInfo object
        """
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text (approximate for most providers).
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        pass
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for given token usage.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost in USD
        """
        model_info = self.get_model_info()
        cost_config = model_info.cost
        
        input_cost = (input_tokens / 1000) * cost_config.get('input_per_1k', 0)
        output_cost = (output_tokens / 1000) * cost_config.get('output_per_1k', 0)
        
        return input_cost + output_cost
