"""
LLM Facade - Unified interface for LLM providers with automatic logging.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Response from LLM call."""
    content: str
    model: str
    provider: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    latency_ms: int = 0
    tool_calls: List[Dict] = field(default_factory=list)
    finish_reason: str = 'stop'
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


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, api_key: str = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    def complete(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """Generate completion from messages."""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get provider name."""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider."""
    
    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get('base_url', 'https://api.openai.com/v1')
    
    def get_provider_name(self) -> str:
        return 'openai'
    
    def complete(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """Generate completion using OpenAI API."""
        import urllib.request
        import urllib.error
        
        model = kwargs.get('model', 'gpt-4o')
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 2000)
        
        start_time = time.time()
        
        try:
            request_data = {
                'model': model,
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens
            }
            
            # Add tools if provided
            if kwargs.get('tools'):
                request_data['tools'] = kwargs['tools']
            
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=json.dumps(request_data).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                }
            )
            
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            choice = result.get('choices', [{}])[0]
            message = choice.get('message', {})
            usage = result.get('usage', {})
            
            return LLMResponse(
                content=message.get('content', ''),
                model=model,
                provider='openai',
                input_tokens=usage.get('prompt_tokens', 0),
                output_tokens=usage.get('completion_tokens', 0),
                total_tokens=usage.get('total_tokens', 0),
                latency_ms=latency_ms,
                tool_calls=message.get('tool_calls', []),
                finish_reason=choice.get('finish_reason', 'stop'),
                raw_response=result
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise


class AnthropicProvider(BaseLLMProvider):
    """Anthropic LLM provider."""
    
    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get('base_url', 'https://api.anthropic.com/v1')
    
    def get_provider_name(self) -> str:
        return 'anthropic'
    
    def complete(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """Generate completion using Anthropic API."""
        import urllib.request
        
        model = kwargs.get('model', 'claude-3-5-sonnet-20241022')
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 2000)
        system_prompt = kwargs.get('system_prompt', '')
        
        start_time = time.time()
        
        try:
            # Extract system message if present
            filtered_messages = []
            for msg in messages:
                if msg.get('role') == 'system':
                    system_prompt = msg.get('content', system_prompt)
                else:
                    filtered_messages.append(msg)
            
            request_data = {
                'model': model,
                'messages': filtered_messages,
                'max_tokens': max_tokens,
                'temperature': temperature
            }
            
            if system_prompt:
                request_data['system'] = system_prompt
            
            if kwargs.get('tools'):
                request_data['tools'] = kwargs['tools']
            
            req = urllib.request.Request(
                f"{self.base_url}/messages",
                data=json.dumps(request_data).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'x-api-key': self.api_key,
                    'anthropic-version': '2023-06-01'
                }
            )
            
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            content_blocks = result.get('content', [])
            content = ''
            tool_calls = []
            
            for block in content_blocks:
                if block.get('type') == 'text':
                    content += block.get('text', '')
                elif block.get('type') == 'tool_use':
                    tool_calls.append(block)
            
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
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider."""
    
    # Default Ollama host - can be overridden via config
    DEFAULT_BASE_URL = 'http://192.168.2.36:11434'
    DEFAULT_MODEL = 'llama3.2:3b'
    
    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get('base_url', self.DEFAULT_BASE_URL)
    
    def get_provider_name(self) -> str:
        return 'ollama'
    
    def complete(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """Generate completion using Ollama API."""
        import urllib.request
        
        model = kwargs.get('model', self.DEFAULT_MODEL)
        temperature = kwargs.get('temperature', 0.7)
        
        start_time = time.time()
        
        try:
            request_data = {
                'model': model,
                'messages': messages,
                'stream': False,
                'options': {
                    'temperature': temperature
                }
            }
            
            req = urllib.request.Request(
                f"{self.base_url}/api/chat",
                data=json.dumps(request_data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=300) as response:
                result = json.loads(response.read().decode('utf-8'))
            
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
            
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise


class GoogleProvider(BaseLLMProvider):
    """Google Gemini LLM provider."""
    
    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get('base_url', 'https://generativelanguage.googleapis.com/v1beta')
    
    def get_provider_name(self) -> str:
        return 'google'
    
    def complete(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """Generate completion using Google Gemini API."""
        import urllib.request
        
        model = kwargs.get('model', 'gemini-1.5-pro')
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 2000)
        
        start_time = time.time()
        
        try:
            # Convert messages to Gemini format
            contents = []
            system_instruction = None
            
            for msg in messages:
                role = msg.get('role')
                content = msg.get('content', '')
                
                if role == 'system':
                    system_instruction = content
                elif role == 'user':
                    contents.append({'role': 'user', 'parts': [{'text': content}]})
                elif role == 'assistant':
                    contents.append({'role': 'model', 'parts': [{'text': content}]})
            
            request_data = {
                'contents': contents,
                'generationConfig': {
                    'temperature': temperature,
                    'maxOutputTokens': max_tokens
                }
            }
            
            if system_instruction:
                request_data['systemInstruction'] = {'parts': [{'text': system_instruction}]}
            
            url = f"{self.base_url}/models/{model}:generateContent?key={self.api_key}"
            req = urllib.request.Request(
                url,
                data=json.dumps(request_data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            candidates = result.get('candidates', [{}])
            content = ''
            if candidates:
                parts = candidates[0].get('content', {}).get('parts', [])
                content = ''.join([p.get('text', '') for p in parts])
            
            usage = result.get('usageMetadata', {})
            
            return LLMResponse(
                content=content,
                model=model,
                provider='google',
                input_tokens=usage.get('promptTokenCount', 0),
                output_tokens=usage.get('candidatesTokenCount', 0),
                total_tokens=usage.get('totalTokenCount', 0),
                latency_ms=latency_ms,
                finish_reason=candidates[0].get('finishReason', 'STOP') if candidates else 'STOP',
                raw_response=result
            )
            
        except Exception as e:
            logger.error(f"Google Gemini API error: {e}")
            raise


class MistralProvider(BaseLLMProvider):
    """Mistral AI LLM provider."""
    
    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get('base_url', 'https://api.mistral.ai/v1')
    
    def get_provider_name(self) -> str:
        return 'mistral'
    
    def complete(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """Generate completion using Mistral API."""
        import urllib.request
        
        model = kwargs.get('model', 'mistral-large-latest')
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 2000)
        
        start_time = time.time()
        
        try:
            request_data = {
                'model': model,
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens
            }
            
            if kwargs.get('tools'):
                request_data['tools'] = kwargs['tools']
            
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=json.dumps(request_data).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                }
            )
            
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            choice = result.get('choices', [{}])[0]
            message = choice.get('message', {})
            usage = result.get('usage', {})
            
            return LLMResponse(
                content=message.get('content', ''),
                model=model,
                provider='mistral',
                input_tokens=usage.get('prompt_tokens', 0),
                output_tokens=usage.get('completion_tokens', 0),
                total_tokens=usage.get('total_tokens', 0),
                latency_ms=latency_ms,
                tool_calls=message.get('tool_calls', []),
                finish_reason=choice.get('finish_reason', 'stop'),
                raw_response=result
            )
            
        except Exception as e:
            logger.error(f"Mistral API error: {e}")
            raise


class CohereProvider(BaseLLMProvider):
    """Cohere LLM provider."""
    
    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get('base_url', 'https://api.cohere.ai/v1')
    
    def get_provider_name(self) -> str:
        return 'cohere'
    
    def complete(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """Generate completion using Cohere API."""
        import urllib.request
        
        model = kwargs.get('model', 'command-r-plus')
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 2000)
        
        start_time = time.time()
        
        try:
            # Convert to Cohere format
            chat_history = []
            message = ""
            preamble = None
            
            for msg in messages:
                role = msg.get('role')
                content = msg.get('content', '')
                
                if role == 'system':
                    preamble = content
                elif role == 'user':
                    if message:  # Previous user message exists
                        chat_history.append({'role': 'USER', 'message': message})
                    message = content
                elif role == 'assistant':
                    if message:
                        chat_history.append({'role': 'USER', 'message': message})
                        message = ""
                    chat_history.append({'role': 'CHATBOT', 'message': content})
            
            request_data = {
                'model': model,
                'message': message,
                'chat_history': chat_history,
                'temperature': temperature,
                'max_tokens': max_tokens
            }
            
            if preamble:
                request_data['preamble'] = preamble
            
            req = urllib.request.Request(
                f"{self.base_url}/chat",
                data=json.dumps(request_data).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                }
            )
            
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            meta = result.get('meta', {})
            tokens = meta.get('tokens', {})
            
            return LLMResponse(
                content=result.get('text', ''),
                model=model,
                provider='cohere',
                input_tokens=tokens.get('input_tokens', 0),
                output_tokens=tokens.get('output_tokens', 0),
                total_tokens=tokens.get('input_tokens', 0) + tokens.get('output_tokens', 0),
                latency_ms=latency_ms,
                finish_reason=result.get('finish_reason', 'COMPLETE'),
                raw_response=result
            )
            
        except Exception as e:
            logger.error(f"Cohere API error: {e}")
            raise


class GroqProvider(BaseLLMProvider):
    """Groq LLM provider (ultra-fast inference)."""
    
    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get('base_url', 'https://api.groq.com/openai/v1')
    
    def get_provider_name(self) -> str:
        return 'groq'
    
    def complete(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """Generate completion using Groq API (OpenAI-compatible)."""
        import urllib.request
        
        model = kwargs.get('model', 'llama-3.3-70b-versatile')
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 2000)
        
        start_time = time.time()
        
        try:
            request_data = {
                'model': model,
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens
            }
            
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=json.dumps(request_data).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                }
            )
            
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            choice = result.get('choices', [{}])[0]
            message = choice.get('message', {})
            usage = result.get('usage', {})
            
            return LLMResponse(
                content=message.get('content', ''),
                model=model,
                provider='groq',
                input_tokens=usage.get('prompt_tokens', 0),
                output_tokens=usage.get('completion_tokens', 0),
                total_tokens=usage.get('total_tokens', 0),
                latency_ms=latency_ms,
                finish_reason=choice.get('finish_reason', 'stop'),
                raw_response=result
            )
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise


class TogetherProvider(BaseLLMProvider):
    """Together AI LLM provider."""
    
    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get('base_url', 'https://api.together.xyz/v1')
    
    def get_provider_name(self) -> str:
        return 'together'
    
    def complete(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """Generate completion using Together API (OpenAI-compatible)."""
        import urllib.request
        
        model = kwargs.get('model', 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo')
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 2000)
        
        start_time = time.time()
        
        try:
            request_data = {
                'model': model,
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens
            }
            
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=json.dumps(request_data).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                }
            )
            
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            choice = result.get('choices', [{}])[0]
            message = choice.get('message', {})
            usage = result.get('usage', {})
            
            return LLMResponse(
                content=message.get('content', ''),
                model=model,
                provider='together',
                input_tokens=usage.get('prompt_tokens', 0),
                output_tokens=usage.get('completion_tokens', 0),
                total_tokens=usage.get('total_tokens', 0),
                latency_ms=latency_ms,
                finish_reason=choice.get('finish_reason', 'stop'),
                raw_response=result
            )
            
        except Exception as e:
            logger.error(f"Together API error: {e}")
            raise


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek LLM provider."""
    
    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get('base_url', 'https://api.deepseek.com/v1')
    
    def get_provider_name(self) -> str:
        return 'deepseek'
    
    def complete(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """Generate completion using DeepSeek API (OpenAI-compatible)."""
        import urllib.request
        
        model = kwargs.get('model', 'deepseek-chat')
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 2000)
        
        start_time = time.time()
        
        try:
            request_data = {
                'model': model,
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens
            }
            
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=json.dumps(request_data).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                }
            )
            
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            choice = result.get('choices', [{}])[0]
            message = choice.get('message', {})
            usage = result.get('usage', {})
            
            return LLMResponse(
                content=message.get('content', ''),
                model=model,
                provider='deepseek',
                input_tokens=usage.get('prompt_tokens', 0),
                output_tokens=usage.get('completion_tokens', 0),
                total_tokens=usage.get('total_tokens', 0),
                latency_ms=latency_ms,
                finish_reason=choice.get('finish_reason', 'stop'),
                raw_response=result
            )
            
        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
            raise


class PerplexityProvider(BaseLLMProvider):
    """Perplexity AI LLM provider (with search)."""
    
    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get('base_url', 'https://api.perplexity.ai')
    
    def get_provider_name(self) -> str:
        return 'perplexity'
    
    def complete(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """Generate completion using Perplexity API."""
        import urllib.request
        
        model = kwargs.get('model', 'llama-3.1-sonar-large-128k-online')
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 2000)
        
        start_time = time.time()
        
        try:
            request_data = {
                'model': model,
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens
            }
            
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=json.dumps(request_data).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                }
            )
            
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            choice = result.get('choices', [{}])[0]
            message = choice.get('message', {})
            usage = result.get('usage', {})
            
            return LLMResponse(
                content=message.get('content', ''),
                model=model,
                provider='perplexity',
                input_tokens=usage.get('prompt_tokens', 0),
                output_tokens=usage.get('completion_tokens', 0),
                total_tokens=usage.get('total_tokens', 0),
                latency_ms=latency_ms,
                finish_reason=choice.get('finish_reason', 'stop'),
                raw_response=result
            )
            
        except Exception as e:
            logger.error(f"Perplexity API error: {e}")
            raise


class LLMFacade:
    """
    Unified facade for LLM operations with automatic database logging.
    
    Every LLM call is automatically logged to the llm_calls table.
    
    Supported Providers:
        - openai: OpenAI (GPT-4, GPT-4o, GPT-3.5, o1)
        - anthropic: Anthropic (Claude 3.5, Claude 3)
        - google: Google Gemini (Gemini 1.5 Pro, Flash)
        - mistral: Mistral AI (Large, Medium, Small)
        - cohere: Cohere (Command R+, Command R)
        - groq: Groq (Ultra-fast inference)
        - together: Together AI (Open source models)
        - deepseek: DeepSeek (DeepSeek Chat, Coder)
        - perplexity: Perplexity (Sonar models with search)
        - ollama: Ollama (Local models)
    
    Usage:
        facade = LLMFacade(db_facade, user_id='user123')
        facade.configure_provider('openai', api_key='sk-...')
        
        response = facade.complete(
            provider='openai',
            model='gpt-4o',
            messages=[{'role': 'user', 'content': 'Hello'}]
        )
    """
    
    PROVIDERS = {
        'openai': OpenAIProvider,
        'anthropic': AnthropicProvider,
        'google': GoogleProvider,
        'mistral': MistralProvider,
        'cohere': CohereProvider,
        'groq': GroqProvider,
        'together': TogetherProvider,
        'deepseek': DeepSeekProvider,
        'perplexity': PerplexityProvider,
        'ollama': OllamaProvider
    }
    
    def __init__(self, db_facade=None, user_id: str = 'system'):
        self.db_facade = db_facade
        self.user_id = user_id
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.default_provider = 'ollama'
        self.default_model = 'llama3.2:3b'
    
    def configure_provider(self, provider_name: str, api_key: str = None, **kwargs):
        """Configure an LLM provider."""
        if provider_name not in self.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        provider_class = self.PROVIDERS[provider_name]
        self.providers[provider_name] = provider_class(api_key=api_key, **kwargs)
        logger.info(f"Configured LLM provider: {provider_name}")
    
    def set_default_provider(self, provider_name: str):
        """Set the default provider."""
        self.default_provider = provider_name
    
    def complete(
        self,
        messages: List[Dict],
        provider: str = None,
        model: str = None,
        execution_id: str = None,
        agent_id: str = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion with automatic logging.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            provider: Provider name (openai, anthropic, ollama)
            model: Model name
            execution_id: Associated execution ID for logging
            agent_id: Associated agent ID for logging
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLMResponse object
        """
        provider_name = provider or self.default_provider
        
        if provider_name not in self.providers:
            raise ValueError(f"Provider not configured: {provider_name}")
        
        llm_provider = self.providers[provider_name]
        
        # Extract prompts for logging
        system_prompt = None
        user_prompt = None
        for msg in messages:
            if msg.get('role') == 'system':
                system_prompt = msg.get('content')
            elif msg.get('role') == 'user':
                user_prompt = msg.get('content')
        
        call_id = str(uuid.uuid4())
        start_time = time.time()
        error_message = None
        status = 'success'
        response = None
        
        try:
            response = llm_provider.complete(messages, model=model, **kwargs)
            
        except Exception as e:
            status = 'failed'
            error_message = str(e)
            logger.error(f"LLM call failed: {e}")
            raise
        
        finally:
            # Log to database
            latency_ms = int((time.time() - start_time) * 1000)
            self._log_call(
                call_id=call_id,
                execution_id=execution_id,
                agent_id=agent_id,
                provider=provider_name,
                model=model or 'unknown',
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                messages=messages,
                response=response,
                latency_ms=latency_ms,
                status=status,
                error_message=error_message,
                kwargs=kwargs
            )
        
        return response
    
    def _log_call(
        self,
        call_id: str,
        execution_id: str,
        agent_id: str,
        provider: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        messages: List[Dict],
        response: Optional[LLMResponse],
        latency_ms: int,
        status: str,
        error_message: str,
        kwargs: Dict
    ):
        """Log LLM call to database."""
        if not self.db_facade:
            return
        
        try:
            # Calculate cost
            input_tokens = response.input_tokens if response else 0
            output_tokens = response.output_tokens if response else 0
            total_tokens = response.total_tokens if response else 0
            cost = self._calculate_cost(provider, model, input_tokens, output_tokens)
            
            self.db_facade.execute("""
                INSERT INTO llm_calls (
                    call_id, execution_id, agent_id, user_id,
                    provider, model, request_type,
                    system_prompt, user_prompt, messages,
                    response_content, tool_calls,
                    input_tokens, output_tokens, total_tokens,
                    cost_estimate, temperature, max_tokens,
                    latency_ms, status, error_message, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                call_id,
                execution_id,
                agent_id,
                self.user_id,
                provider,
                model,
                'chat',
                system_prompt,
                user_prompt,
                json.dumps(messages),
                response.content if response else None,
                json.dumps(response.tool_calls) if response and response.tool_calls else None,
                input_tokens,
                output_tokens,
                total_tokens,
                cost,
                kwargs.get('temperature'),
                kwargs.get('max_tokens'),
                latency_ms,
                status,
                error_message,
                json.dumps({'finish_reason': response.finish_reason if response else None})
            ))
            
            logger.debug(f"Logged LLM call: {call_id}")
            
        except Exception as e:
            logger.error(f"Failed to log LLM call: {e}")
    
    def _calculate_cost(self, provider: str, model: str, 
                       input_tokens: int, output_tokens: int) -> float:
        """Calculate estimated cost."""
        COSTS = {
            'openai': {
                'gpt-4o': {'input': 2.50, 'output': 10.00},
                'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
                'gpt-4-turbo': {'input': 10.00, 'output': 30.00},
            },
            'anthropic': {
                'claude-3-5-sonnet-20241022': {'input': 3.00, 'output': 15.00},
                'claude-3-opus-20240229': {'input': 15.00, 'output': 75.00},
            },
            'ollama': {}  # Free
        }
        
        provider_costs = COSTS.get(provider, {})
        model_costs = provider_costs.get(model, {'input': 0, 'output': 0})
        
        input_cost = (input_tokens / 1_000_000) * model_costs.get('input', 0)
        output_cost = (output_tokens / 1_000_000) * model_costs.get('output', 0)
        
        return round(input_cost + output_cost, 6)
    
    def get_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics."""
        if not self.db_facade:
            return {}
        
        result = self.db_facade.fetch_one("""
            SELECT 
                COUNT(*) as total_calls,
                SUM(input_tokens) as total_input_tokens,
                SUM(output_tokens) as total_output_tokens,
                SUM(total_tokens) as total_tokens,
                SUM(cost_estimate) as total_cost,
                AVG(latency_ms) as avg_latency
            FROM llm_calls 
            WHERE user_id = ? 
            AND created_at > datetime('now', ?)
        """, (self.user_id, f'-{days} days'))
        
        return result or {}
