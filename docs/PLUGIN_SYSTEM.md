<!--
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.3
-->

# Plugin System Documentation

## Overview

The Abhikarta LLM Abstraction System uses a plugin architecture that allows easy addition of new LLM providers without modifying core code. This document explains how to create custom providers.

## Architecture

The plugin system consists of three main components:

1. **Provider** - Handles authentication and provider-level operations
2. **Facade** - Implements model-specific operations
3. **Configuration** - JSON file defining available models

## Creating a Custom Provider

### Step 1: Create Provider Directory

```bash
mkdir -p llm/abstraction/providers/myprovider
```

### Step 2: Implement Provider Class

Create `provider.py`:

```python
"""My Custom LLM Provider"""
import os
from typing import Any, Dict, List
from ...core.provider import LLMProvider
from ...core.facade import LLMFacade
from ...core.exceptions import *
from .facade import MyProviderFacade

class MyProvider(LLMProvider):
    def __init__(self):
        super().__init__()
        self.provider_name = "myprovider"
        self.client = None
    
    def initialize(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.api_key = os.environ.get('MYPROVIDER_API_KEY') or config.get('api_key')
        
        if not self.api_key:
            raise InvalidCredentialsError("API key not found")
        
        # Initialize your client here
        # self.client = YourSDK(api_key=self.api_key)
        self.initialized = True
    
    def create_facade(self, model_name: str) -> LLMFacade:
        if model_name not in self.list_available_models():
            raise ModelNotFoundError(f"Model '{model_name}' not found")
        return MyProviderFacade(self, model_name, self.client)
    
    def list_available_models(self) -> List[str]:
        return [model['name'] for model in self.config.get('models', [])]
    
    def validate_credentials(self) -> bool:
        return self.initialized
    
    def get_provider_name(self) -> str:
        return self.provider_name
```

### Step 3: Implement Facade Class

Create `facade.py`:

```python
"""My Provider Facade"""
from typing import List, Iterator, Any
from ...core.facade import *
from ...core.provider import LLMProvider
from ...core.exceptions import APIError

class MyProviderFacade(LLMFacade):
    def __init__(self, provider: LLMProvider, model_name: str, client: Any):
        super().__init__(provider, model_name)
        self.client = client
    
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        try:
            # Call your provider's API
            result = self.client.complete(
                prompt=prompt,
                model=self.model_name,
                max_tokens=kwargs.get('max_tokens', 1000)
            )
            
            return CompletionResponse(
                text=result.text,
                model=self.model_name,
                provider='myprovider',
                tokens_used=result.tokens,
                finish_reason='complete'
            )
        except Exception as e:
            raise APIError(f"Provider error: {str(e)}", provider='myprovider')
    
    def chat(self, messages: List[Message], **kwargs) -> ChatResponse:
        # Implement chat
        pass
    
    def stream_complete(self, prompt: str, **kwargs) -> Iterator[str]:
        # Implement streaming
        pass
    
    def stream_chat(self, messages: List[Message], **kwargs) -> Iterator[str]:
        # Implement streaming chat
        pass
    
    def get_model_info(self) -> ModelInfo:
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
            metadata={'provider': 'myprovider'}
        )
        return self.model_info_cache
    
    def count_tokens(self, text: str) -> int:
        # Implement token counting
        return len(text) // 4
```

### Step 4: Create Package Init

Create `__init__.py`:

```python
from .provider import MyProvider
from .facade import MyProviderFacade

__all__ = ['MyProvider', 'MyProviderFacade']
```

### Step 5: Create Configuration

Create `config/providers/myprovider.json`:

```json
{
  "provider": "myprovider",
  "api_version": "v1",
  "base_url": "https://api.myprovider.com",
  "models": [
    {
      "name": "my-model-v1",
      "version": "1.0",
      "description": "My custom model",
      "strengths": ["reasoning", "creativity"],
      "context_window": 8192,
      "max_output": 4096,
      "cost": {
        "input_per_1k": 0.001,
        "output_per_1k": 0.002
      },
      "capabilities": {
        "chat": true,
        "completion": true,
        "streaming": true,
        "function_calling": false,
        "vision": false
      }
    }
  ]
}
```

### Step 6: Register Provider

Add to `config/llm_config.json`:

```json
{
  "providers": {
    "myprovider": {
      "module": "llm.abstraction.providers.myprovider",
      "class": "MyProvider",
      "facade_class": "MyProviderFacade",
      "enabled": true,
      "config_file": "config/providers/myprovider.json"
    }
  }
}
```

### Step 7: Use Your Provider

```python
from llm.abstraction import LLMClientFactory

factory = LLMClientFactory()
factory.initialize()

client = factory.create_client(
    provider='myprovider',
    model='my-model-v1'
)

response = client.complete("Hello, world!")
print(response)
```

## Advanced Features

### Adding Retry Logic

```python
from ...utils.retry import retry_with_backoff, RetryConfig
from ...core.exceptions import APIError

class MyProviderFacade(LLMFacade):
    @retry_with_backoff(
        max_attempts=3,
        retryable_exceptions=(APIError,)
    )
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        # Your implementation
        pass
```

### Adding Rate Limiting

```python
from ...utils.rate_limiter import rate_limit

class MyProviderFacade(LLMFacade):
    @rate_limit(tokens_per_second=10)
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        # Your implementation
        pass
```

### Adding Caching

```python
from ...utils.cache import ResponseCache

class MyProvider(LLMProvider):
    def __init__(self):
        super().__init__()
        self.cache = ResponseCache(max_size=1000, ttl=3600)
    
    def create_facade(self, model_name: str) -> LLMFacade:
        facade = MyProviderFacade(self, model_name, self.client)
        facade.cache = self.cache
        return facade
```

## Best Practices

1. **Error Handling**: Always wrap API calls in try-except and raise appropriate exceptions
2. **Token Counting**: Implement accurate token counting when possible
3. **Streaming**: Support streaming for better UX when available
4. **Cost Tracking**: Include accurate cost information in model configs
5. **Documentation**: Document any provider-specific parameters
6. **Testing**: Create unit tests for your provider

## Example Providers

See existing implementations for reference:
- `llm/abstraction/providers/anthropic/` - Full-featured example
- `llm/abstraction/providers/openai/` - Streaming implementation
- `llm/abstraction/providers/google/` - Alternative API style
- `llm/abstraction/providers/mock/` - Simple testing example

## Troubleshooting

### Provider Not Loading

1. Check module path in config
2. Verify __init__.py exists
3. Ensure all imports are correct

### Authentication Errors

1. Set environment variable: `export MYPROVIDER_API_KEY=...`
2. Or add to `config/llm.properties`
3. Verify credentials with `provider.validate_credentials()`

### Model Not Found

1. Check model name matches config
2. Verify config file path is correct
3. Ensure provider is enabled in main config

## Contributing

To contribute a provider to the main repository:

1. Follow this guide
2. Add comprehensive tests
3. Update README.md
4. Submit pull request

---

© 2025-2030 Ashutosh Sinha | ajsinha@gmail.com

---

**Copyright 2025-2030 all rights reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**  
**Version: 3.1.3**
