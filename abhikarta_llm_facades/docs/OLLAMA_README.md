# Ollama Provider - Abhikarta LLM Facades

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This document and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use of this document or the software
system it describes is strictly prohibited without explicit written permission from the
copyright holder.

Patent Pending: Certain architectural patterns and implementations described in this
document may be subject to patent applications.


---

## Overview

This document provides comprehensive documentation for using the Ollama provider with Abhikarta LLM Facades.

## Installation

```bash
curl https://ollama.ai/install.sh | sh
```

## Configuration

### Base URL

Default: `http://localhost:11434`

You can override with custom endpoint:

```python
llm = OllamaFacade(
    model_name="llama2",
    base_url="https://your-custom-endpoint.com"
)
```

## Supported Features

- Local Models
- Chat
- Completions
- Embeddings
- No API Key Required

## Basic Usage

### Initialization

```python
from facades.ollama_facade import OllamaFacade

# Initialize with environment variable
llm = OllamaFacade(
    model_name="llama2"
)

# Or pass API key directly
llm = OllamaFacade(
    model_name="llama2",
)
```

### Chat Completion

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is quantum computing?"}
]

response = llm.chat_completion(messages)
print(response["content"])
```

### Streaming

```python
for chunk in llm.stream_chat_completion(messages):
    print(chunk, end="", flush=True)
```

### With Configuration

```python
from facades.llm_facade import GenerationConfig

config = GenerationConfig(
    max_tokens=1000,
    temperature=0.7,
    top_p=0.9
)

response = llm.chat_completion(messages, config=config)
```

## Advanced Features

### Function Calling

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["location"]
            }
        }
    }
]

response = llm.chat_completion(
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=tools
)

if "tool_calls" in response:
    for tool_call in response["tool_calls"]:
        print(f"Function: {tool_call['function']['name']}")
        print(f"Arguments: {tool_call['function']['arguments']}")
```

### Vision (if supported)

```python
from PIL import Image

messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "What's in this image?"},
            {"type": "image_url", "image_url": {"url": "path/to/image.jpg"}}
        ]
    }
]

response = llm.chat_completion(messages)
```

### Embeddings (if supported)

```python
embeddings = llm.get_embeddings([
    "Hello world",
    "How are you?"
])

for i, emb in enumerate(embeddings):
    print(f"Embedding {i}: {len(emb)} dimensions")
```

## Model Information

### Available Models

Load the provider configuration to see all available models:

```python
import json

# View all models for this provider
info = llm.get_model_info()
print(json.dumps(info, indent=2))
```

### Check Capabilities

```python
from facades.llm_facade import ModelCapability

capabilities = llm.get_capabilities()
print("Supported capabilities:")
for cap in capabilities:
    print(f"  - {cap.value}")

# Check specific capability
if llm.supports_capability(ModelCapability.FUNCTION_CALLING):
    print("This model supports function calling!")
```

## Error Handling

```python
from facades.llm_facade import (
    RateLimitException,
    ContentFilterException,
    AuthenticationException,
    ContextLengthExceededException
)

try:
    response = llm.chat_completion(messages)
except RateLimitException as e:
    print(f"Rate limit exceeded: {e}")
except ContentFilterException as e:
    print(f"Content filtered: {e}")
except AuthenticationException as e:
    print(f"Authentication failed: {e}")
except ContextLengthExceededException as e:
    print(f"Context too long: {e.provided} > {e.maximum}")
```

## Monitoring & Usage

```python
# Get usage statistics
stats = llm.get_usage_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"Total tokens: {stats['total_tokens']}")

# Health check
if llm.health_check():
    print("Service is healthy")
else:
    print("Service unavailable")
```

## Context Manager

```python
with {info['title'].replace(' ', '')}Facade(model_name="{info['example_model']}") as llm:
    response = llm.chat_completion(messages)
    print(response["content"])
# Automatically cleaned up
```

## Best Practices

1. **Reuse Instances** - Create facade once and reuse for multiple requests
2. **Set Timeouts** - Always configure appropriate timeouts
3. **Handle Errors** - Implement comprehensive error handling
4. **Monitor Usage** - Track token usage and costs
5. **Use Streaming** - For long responses, use streaming
6. **Check Capabilities** - Verify features before using them

## Examples

See `examples/{provider_name}_example.py` for complete, runnable examples.

## Troubleshooting

### Common Issues

2. **Rate Limiting**
   - Implement exponential backoff
   - Use built-in retry logic with `max_retries` parameter

3. **Context Length Errors**
   - Check model's context window limit
   - Reduce message length or use summarization

4. **Timeout Errors**
   - Increase timeout parameter
   - Check network connectivity

## Support

For issues specific to this provider, consult their official documentation.
For facade-related issues, contact: ajsinha@gmail.com

---

**Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.**
