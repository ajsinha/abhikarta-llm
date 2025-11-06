"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.0.1

Unified LLM Facade - Main entry point for Abhikarta LLM
"""

from typing import Dict, Any, Optional, Iterator, List
from .core.facade import LLMFacade, CompletionResponse, Message
from .providers import get_provider


class UnifiedLLMFacade:
    """
    Unified facade for interacting with multiple LLM providers.
    
    This class provides a simple, consistent interface for working with
    different LLM providers (OpenAI, Anthropic, Cohere, Google, Groq,
    Mistral, Together, Ollama, etc.) without changing your code.
    
    Example:
        ```python
        config = {
            'providers': {
                'openai': {
                    'enabled': True,
                    'api_key': 'your-key',
                    'model': 'gpt-3.5-turbo'
                }
            }
        }
        
        facade = UnifiedLLMFacade(config)
        response = facade.complete("Hello, world!")
        print(response.text)
        ```
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the UnifiedLLMFacade.
        
        Args:
            config: Configuration dictionary with provider settings
                   Format: {
                       'providers': {
                           'provider_name': {
                               'enabled': True,
                               'api_key': 'key',
                               'model': 'model-name',
                               ...
                           }
                       }
                   }
        """
        self.config = config
        self.providers = {}
        self.default_provider = None
        
        # Initialize all enabled providers
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all enabled providers from config."""
        providers_config = self.config.get('providers', {})
        
        for provider_name, provider_config in providers_config.items():
            if provider_config.get('enabled', False):
                try:
                    provider = get_provider(provider_name, provider_config)
                    
                    # Get model name from config, with provider-specific defaults
                    model = provider_config.get('model')
                    if not model:
                        # Set sensible defaults for each provider
                        defaults = {
                            'mock': 'mock-model',
                            'openai': 'gpt-3.5-turbo',
                            'anthropic': 'claude-3-sonnet-20240229',
                            'groq': 'mixtral-8x7b-32768',
                            'mistral': 'mistral-small',
                            'together': 'meta-llama/Llama-2-70b-chat-hf',
                            'ollama': 'llama2',
                            'google': 'gemini-pro',
                        }
                        model = defaults.get(provider_name, 'default')
                    
                    # Create facade for this provider
                    if type(model) == dict:
                        facade = provider.create_facade(model['name'])
                    else: # must be string
                        facade = provider.create_facade(model)
                    self.providers[provider_name] = facade
                    
                    # Set first enabled provider as default
                    if self.default_provider is None:
                        self.default_provider = provider_name
                        
                except Exception as e:
                    print(f"Warning: Failed to initialize provider '{provider_name}': {e}")
        
        if not self.providers:
            raise ValueError("No providers were successfully initialized. Check your configuration.")
    
    def complete(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> CompletionResponse:
        """
        Generate a completion for the given prompt.
        
        Args:
            prompt: The input prompt text
            provider: Which provider to use (defaults to first enabled provider)
            model: Which model to use (overrides config)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
        
        Returns:
            CompletionResponse with generated text and metadata
        
        Example:
            ```python
            response = facade.complete(
                "Explain quantum computing",
                temperature=0.7,
                max_tokens=500
            )
            print(response.text)
            ```
        """
        provider_name = provider or self.default_provider
        
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not found or not enabled")
        
        provider_instance = self.providers[provider_name]
        
        # Call the provider's complete method
        return provider_instance.complete(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def stream_complete(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Iterator[CompletionResponse]:
        """
        Generate a streaming completion for the given prompt.
        
        Args:
            prompt: The input prompt text
            provider: Which provider to use (defaults to first enabled provider)
            model: Which model to use (overrides config)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
        
        Yields:
            CompletionResponse objects with incremental text
        
        Example:
            ```python
            for chunk in facade.stream_complete("Write a story"):
                print(chunk.text, end='', flush=True)
            ```
        """
        provider_name = provider or self.default_provider
        
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not found or not enabled")
        
        provider_instance = self.providers[provider_name]
        
        # Call the provider's stream_complete method
        yield from provider_instance.stream_complete(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> CompletionResponse:
        """
        Generate a chat completion for the given messages.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            provider: Which provider to use (defaults to first enabled provider)
            model: Which model to use (overrides config)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
        
        Returns:
            CompletionResponse with generated text and metadata
        
        Example:
            ```python
            messages = [
                {"role": "user", "content": "Hello!"},
                {"role": "assistant", "content": "Hi! How can I help?"},
                {"role": "user", "content": "Tell me a joke"}
            ]
            response = facade.chat(messages)
            print(response.text)
            ```
        """
        provider_name = provider or self.default_provider
        
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not found or not enabled")
        
        provider_instance = self.providers[provider_name]
        
        # Convert dict messages to Message objects if needed
        from llm.abstraction.core.facade import Message
        processed_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                processed_messages.append(Message(role=msg['role'], content=msg['content']))
            else:
                processed_messages.append(msg)
        
        # Call the provider's chat method
        chat_response = provider_instance.chat(
            messages=processed_messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Convert ChatResponse to CompletionResponse for consistency
        if hasattr(chat_response, 'message'):
            # It's a ChatResponse, convert to CompletionResponse
            return CompletionResponse(
                text=chat_response.message.content,
                model=chat_response.model,
                provider=chat_response.provider,
                tokens_used=chat_response.tokens_used,
                finish_reason=chat_response.finish_reason,
                metadata=chat_response.metadata
            )
        else:
            # Already a CompletionResponse
            return chat_response
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available (enabled) providers.
        
        Returns:
            List of provider names
        """
        return list(self.providers.keys())
    
    def get_default_provider(self) -> str:
        """
        Get the default provider name.
        
        Returns:
            Name of the default provider
        """
        return self.default_provider
    
    def set_default_provider(self, provider_name: str):
        """
        Set the default provider.
        
        Args:
            provider_name: Name of the provider to set as default
        
        Raises:
            ValueError: If provider is not enabled
        """
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not found or not enabled")
        
        self.default_provider = provider_name


# For backwards compatibility
UnifiedFacade = UnifiedLLMFacade
