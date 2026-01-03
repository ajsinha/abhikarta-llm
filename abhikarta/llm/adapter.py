"""
LLM Adapter - Unified async interface for LLM operations.

This module provides a simplified async interface for LLM operations,
wrapping the LLMFacade with async support for use in the swarm and
agent modules.

Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.
Email: ajsinha@gmail.com

PATENT PENDING - This software contains patentable inventions.
Unauthorized copying, modification, or distribution is prohibited.

Version: 1.4.8
"""

import asyncio
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Thread pool for running sync LLM calls in async context
_executor = ThreadPoolExecutor(max_workers=10)


@dataclass
class LLMResponse:
    """Response from an LLM call."""
    content: str
    model: str = ""
    provider: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    latency_ms: int = 0
    tool_calls: List[Dict] = field(default_factory=list)
    finish_reason: str = "stop"
    raw_response: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'content': self.content,
            'model': self.model,
            'provider': self.provider,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'total_tokens': self.total_tokens,
            'latency_ms': self.latency_ms,
            'tool_calls': self.tool_calls,
            'finish_reason': self.finish_reason
        }


@dataclass
class LLMConfig:
    """Configuration for LLM adapter."""
    provider: str = "openai"
    model: str = "gpt-4o"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 120
    
    # Provider-specific settings
    base_url: Optional[str] = None
    
    def __post_init__(self):
        """Load API key from environment if not provided."""
        if not self.api_key:
            env_keys = {
                'openai': 'OPENAI_API_KEY',
                'anthropic': 'ANTHROPIC_API_KEY',
                'google': 'GOOGLE_API_KEY',
                'mistral': 'MISTRAL_API_KEY',
                'cohere': 'COHERE_API_KEY',
                'groq': 'GROQ_API_KEY',
                'together': 'TOGETHER_API_KEY',
                'deepseek': 'DEEPSEEK_API_KEY',
                'perplexity': 'PERPLEXITY_API_KEY',
            }
            env_key = env_keys.get(self.provider)
            if env_key:
                self.api_key = os.environ.get(env_key)


class LLMAdapter:
    """
    Unified async adapter for LLM operations.
    
    Provides a simple async interface for making LLM calls across
    multiple providers. Wraps the LLMFacade with async support.
    
    Usage:
        # Simple usage
        adapter = LLMAdapter(provider='openai', model='gpt-4o')
        response = await adapter.generate(
            prompt="Hello, world!",
            system_prompt="You are a helpful assistant."
        )
        print(response.content)
        
        # With configuration
        config = LLMConfig(
            provider='anthropic',
            model='claude-3-5-sonnet-20241022',
            temperature=0.5
        )
        adapter = LLMAdapter(config=config)
        response = await adapter.generate("Tell me a joke")
    
    Supported Providers:
        - openai: GPT-4o, GPT-4o-mini, GPT-4-turbo, o1
        - anthropic: Claude 3.5 Sonnet, Claude 3 Opus
        - google: Gemini 1.5 Pro, Gemini 1.5 Flash
        - mistral: Mistral Large, Medium, Small
        - cohere: Command R+, Command R
        - groq: Ultra-fast inference
        - together: Open source models
        - deepseek: DeepSeek Chat, Coder
        - perplexity: Sonar models with search
        - ollama: Local models
    """
    
    def __init__(
        self,
        provider: str = None,
        model: str = None,
        config: LLMConfig = None,
        api_key: str = None,
        **kwargs
    ):
        """
        Initialize the LLM adapter.
        
        Args:
            provider: LLM provider name (openai, anthropic, etc.)
            model: Model name
            config: LLMConfig object (overrides provider/model)
            api_key: API key (overrides config)
            **kwargs: Additional config parameters
        """
        if config:
            self.config = config
        else:
            self.config = LLMConfig(
                provider=provider or 'openai',
                model=model or 'gpt-4o',
                api_key=api_key,
                **kwargs
            )
        
        if api_key:
            self.config.api_key = api_key
        
        self._facade = None
        self._initialized = False
        
        logger.info(f"LLMAdapter initialized: provider={self.config.provider}, model={self.config.model}")
    
    def _ensure_initialized(self):
        """Lazy initialization of the LLM facade."""
        if self._initialized:
            return
        
        try:
            from abhikarta.llm_provider.llm_facade import LLMFacade
            
            self._facade = LLMFacade()
            self._facade.configure_provider(
                self.config.provider,
                api_key=self.config.api_key,
                base_url=self.config.base_url
            )
            self._facade.set_default_provider(self.config.provider)
            self._initialized = True
            
        except ImportError as e:
            logger.warning(f"LLMFacade not available: {e}")
            self._facade = None
            self._initialized = True
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None,
        tools: List[Dict] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: User prompt/message
            system_prompt: Optional system prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
            tools: Optional list of tool definitions for function calling
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLMResponse object containing the generated content
        """
        self._ensure_initialized()
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})
        
        # Use configured defaults if not overridden
        temperature = temperature if temperature is not None else self.config.temperature
        max_tokens = max_tokens or self.config.max_tokens
        
        # Use facade if available
        if self._facade:
            try:
                # Run sync call in thread pool
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    _executor,
                    lambda: self._facade.complete(
                        messages=messages,
                        model=self.config.model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        tools=tools,
                        **kwargs
                    )
                )
                
                return LLMResponse(
                    content=response.content,
                    model=response.model,
                    provider=response.provider,
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                    total_tokens=response.total_tokens,
                    latency_ms=response.latency_ms,
                    tool_calls=response.tool_calls,
                    finish_reason=response.finish_reason,
                    raw_response=response.raw_response
                )
                
            except Exception as e:
                logger.error(f"LLM generation error: {e}")
                # Fall back to direct API call
                return await self._direct_call(
                    messages, temperature, max_tokens, tools, **kwargs
                )
        
        # Direct API call fallback
        return await self._direct_call(
            messages, temperature, max_tokens, tools, **kwargs
        )
    
    async def chat(
        self,
        messages: List[Dict],
        temperature: float = None,
        max_tokens: int = None,
        tools: List[Dict] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Send a multi-turn chat conversation.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            max_tokens: Override default max tokens
            tools: Optional tool definitions
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse object
        """
        self._ensure_initialized()
        
        temperature = temperature if temperature is not None else self.config.temperature
        max_tokens = max_tokens or self.config.max_tokens
        
        if self._facade:
            try:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    _executor,
                    lambda: self._facade.complete(
                        messages=messages,
                        model=self.config.model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        tools=tools,
                        **kwargs
                    )
                )
                
                return LLMResponse(
                    content=response.content,
                    model=response.model,
                    provider=response.provider,
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                    total_tokens=response.total_tokens,
                    latency_ms=response.latency_ms,
                    tool_calls=response.tool_calls,
                    finish_reason=response.finish_reason,
                    raw_response=response.raw_response
                )
                
            except Exception as e:
                logger.error(f"Chat error: {e}")
                return await self._direct_call(
                    messages, temperature, max_tokens, tools, **kwargs
                )
        
        return await self._direct_call(
            messages, temperature, max_tokens, tools, **kwargs
        )
    
    async def _direct_call(
        self,
        messages: List[Dict],
        temperature: float,
        max_tokens: int,
        tools: List[Dict] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Make a direct API call without the facade.
        
        This is a fallback for when the facade is not available.
        """
        import json
        import time
        import urllib.request
        import urllib.error
        
        provider = self.config.provider
        api_key = self.config.api_key
        model = self.config.model
        
        start_time = time.time()
        
        try:
            if provider == 'openai':
                base_url = self.config.base_url or 'https://api.openai.com/v1'
                return await self._openai_call(
                    base_url, api_key, model, messages, 
                    temperature, max_tokens, tools
                )
            
            elif provider == 'anthropic':
                return await self._anthropic_call(
                    api_key, model, messages,
                    temperature, max_tokens, tools
                )
            
            elif provider == 'ollama':
                base_url = self.config.base_url or 'http://localhost:11434'
                return await self._ollama_call(
                    base_url, model, messages,
                    temperature, max_tokens
                )
            
            else:
                # Generic OpenAI-compatible fallback
                base_url = self.config.base_url or f'https://api.{provider}.com/v1'
                return await self._openai_call(
                    base_url, api_key, model, messages,
                    temperature, max_tokens, tools
                )
                
        except Exception as e:
            logger.error(f"Direct API call failed: {e}")
            return LLMResponse(
                content=f"Error: {str(e)}",
                model=model,
                provider=provider,
                finish_reason='error'
            )
    
    async def _openai_call(
        self, base_url: str, api_key: str, model: str,
        messages: List[Dict], temperature: float, max_tokens: int,
        tools: List[Dict] = None
    ) -> LLMResponse:
        """Make OpenAI API call."""
        import json
        import time
        import urllib.request
        
        start_time = time.time()
        
        request_data = {
            'model': model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens
        }
        
        if tools:
            request_data['tools'] = tools
        
        loop = asyncio.get_event_loop()
        
        def make_request():
            req = urllib.request.Request(
                f"{base_url}/chat/completions",
                data=json.dumps(request_data).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}'
                }
            )
            
            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        
        result = await loop.run_in_executor(_executor, make_request)
        
        latency_ms = int((time.time() - start_time) * 1000)
        choice = result.get('choices', [{}])[0]
        message = choice.get('message', {})
        usage = result.get('usage', {})
        
        tool_calls = []
        if message.get('tool_calls'):
            tool_calls = [
                {
                    'id': tc.get('id'),
                    'type': tc.get('type'),
                    'function': tc.get('function', {})
                }
                for tc in message.get('tool_calls', [])
            ]
        
        return LLMResponse(
            content=message.get('content', ''),
            model=model,
            provider='openai',
            input_tokens=usage.get('prompt_tokens', 0),
            output_tokens=usage.get('completion_tokens', 0),
            total_tokens=usage.get('total_tokens', 0),
            latency_ms=latency_ms,
            tool_calls=tool_calls,
            finish_reason=choice.get('finish_reason', 'stop'),
            raw_response=result
        )
    
    async def _anthropic_call(
        self, api_key: str, model: str, messages: List[Dict],
        temperature: float, max_tokens: int, tools: List[Dict] = None
    ) -> LLMResponse:
        """Make Anthropic API call."""
        import json
        import time
        import urllib.request
        
        start_time = time.time()
        
        # Extract system message
        system_content = ""
        user_messages = []
        for msg in messages:
            if msg.get('role') == 'system':
                system_content = msg.get('content', '')
            else:
                user_messages.append(msg)
        
        request_data = {
            'model': model,
            'messages': user_messages,
            'max_tokens': max_tokens,
            'temperature': temperature
        }
        
        if system_content:
            request_data['system'] = system_content
        
        if tools:
            # Convert to Anthropic tool format
            request_data['tools'] = [
                {
                    'name': t.get('function', {}).get('name'),
                    'description': t.get('function', {}).get('description', ''),
                    'input_schema': t.get('function', {}).get('parameters', {})
                }
                for t in tools
            ]
        
        loop = asyncio.get_event_loop()
        
        def make_request():
            req = urllib.request.Request(
                'https://api.anthropic.com/v1/messages',
                data=json.dumps(request_data).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01'
                }
            )
            
            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        
        result = await loop.run_in_executor(_executor, make_request)
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Extract text content
        content_blocks = result.get('content', [])
        content = ''
        tool_calls = []
        
        for block in content_blocks:
            if block.get('type') == 'text':
                content += block.get('text', '')
            elif block.get('type') == 'tool_use':
                tool_calls.append({
                    'id': block.get('id'),
                    'type': 'function',
                    'function': {
                        'name': block.get('name'),
                        'arguments': json.dumps(block.get('input', {}))
                    }
                })
        
        usage = result.get('usage', {})
        
        return LLMResponse(
            content=content,
            model=model,
            provider='anthropic',
            input_tokens=usage.get('input_tokens', 0),
            output_tokens=usage.get('output_tokens', 0),
            total_tokens=usage.get('input_tokens', 0) + usage.get('output_tokens', 0),
            latency_ms=latency_ms,
            tool_calls=tool_calls,
            finish_reason=result.get('stop_reason', 'end_turn'),
            raw_response=result
        )
    
    async def _ollama_call(
        self, base_url: str, model: str, messages: List[Dict],
        temperature: float, max_tokens: int
    ) -> LLMResponse:
        """Make Ollama API call."""
        import json
        import time
        import urllib.request
        
        start_time = time.time()
        
        request_data = {
            'model': model,
            'messages': messages,
            'stream': False,
            'options': {
                'temperature': temperature,
                'num_predict': max_tokens
            }
        }
        
        loop = asyncio.get_event_loop()
        
        def make_request():
            req = urllib.request.Request(
                f"{base_url}/api/chat",
                data=json.dumps(request_data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        
        result = await loop.run_in_executor(_executor, make_request)
        
        latency_ms = int((time.time() - start_time) * 1000)
        message = result.get('message', {})
        
        return LLMResponse(
            content=message.get('content', ''),
            model=model,
            provider='ollama',
            input_tokens=result.get('prompt_eval_count', 0),
            output_tokens=result.get('eval_count', 0),
            total_tokens=result.get('prompt_eval_count', 0) + result.get('eval_count', 0),
            latency_ms=latency_ms,
            finish_reason='stop',
            raw_response=result
        )
    
    def set_api_key(self, api_key: str):
        """Update the API key."""
        self.config.api_key = api_key
        self._initialized = False
    
    def set_model(self, model: str):
        """Update the model."""
        self.config.model = model
    
    def set_provider(self, provider: str):
        """Update the provider."""
        self.config.provider = provider
        self._initialized = False


# Convenience function for quick usage
async def generate(
    prompt: str,
    system_prompt: str = None,
    provider: str = 'openai',
    model: str = 'gpt-4o',
    **kwargs
) -> LLMResponse:
    """
    Quick helper function for one-off LLM calls.
    
    Usage:
        from abhikarta.llm import generate
        response = await generate("Hello!", provider='openai')
        print(response.content)
    """
    adapter = LLMAdapter(provider=provider, model=model)
    return await adapter.generate(prompt, system_prompt=system_prompt, **kwargs)
