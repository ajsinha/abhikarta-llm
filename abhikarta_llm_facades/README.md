# Abhikarta LLM Facades

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

## Legal Notice

This document and the associated software architecture are proprietary and confidential. Unauthorized copying, distribution, modification, or use of this document or the software system it describes is strictly prohibited without explicit written permission from the copyright holder. This document is provided "as is" without warranty of any kind, either expressed or implied. The copyright holder shall not be liable for any damages arising from the use of this document or the software system it describes.

**Patent Pending:** Certain architectural patterns and implementations described in this document may be subject to patent applications.

---

## Overview

Abhikarta LLM Facades provides a unified, provider-agnostic interface for interacting with Large Language Models from various providers. The facade pattern ensures that client code remains decoupled from specific provider implementations, allowing for seamless provider switching and consistent API usage.

## Supported Providers

- **OpenAI** - GPT-4, GPT-3.5, DALL-E, Whisper, Embeddings
- **Anthropic** - Claude 3 Family (Opus, Sonnet, Haiku)
- **Google** - Gemini Pro, PaLM 2
- **Cohere** - Command, Command-R, Embeddings
- **Mistral** - Mistral Large, Medium, Small, Mixtral
- **Groq** - Ultra-fast inference for various models
- **AWS Bedrock** - Access to multiple models via AWS
- **HuggingFace** - Open source models and Inference API
- **Ollama** - Local model execution
- **Together** - Distributed inference
- **Replicate** - Cloud inference for open models
- **Meta** - Llama 2, Llama 3, Code Llama
- **Mock** - Testing and development

## Architecture

### Class Hierarchy

```
LLMFacade (Abstract Base Class)
    ↓
LLMFacadeBase (Common Implementation)
    ↓
Provider-Specific Facades
    ├── OpenAIFacade
    ├── AnthropicFacade
    ├── GoogleFacade
    ├── CohereFacade
    ├── MistralFacade
    ├── GroqFacade
    ├── AWSBedrockFacade
    ├── HuggingFaceLLMFacade
    ├── OllamaFacade
    ├── TogetherFacade
    ├── ReplicateFacade
    ├── MetaFacade
    └── MockFacade
```

### Key Features

1. **Provider Agnostic** - Same API across all providers
2. **Capability Discovery** - Runtime detection of model capabilities
3. **Graceful Degradation** - Fails gracefully for unsupported features
4. **Consistent Error Handling** - Standardized exceptions
5. **Full Async Support** - Native async/await for all operations
6. **Streaming First** - Built-in streaming support
7. **Type Safety** - Comprehensive type hints
8. **Monitoring & Logging** - Built-in request tracking

## Installation

### Requirements

```bash
pip install openai anthropic google-generativeai cohere mistralai groq
pip install boto3 huggingface_hub transformers torch
pip install together replicate ollama
```

### Optional Dependencies

```bash
# For token counting
pip install tiktoken

# For local model execution
pip install accelerate bitsandbytes

# For embeddings
pip install sentence-transformers

# For image processing
pip install pillow
```

## Quick Start

### Basic Usage

```python
from facades.openai_facade import OpenAIFacade

# Initialize facade
llm = OpenAIFacade(
    model_name="gpt-4",
    api_key="sk-..."  # Or set OPENAI_API_KEY env var
)

# Generate response
response = llm.chat_completion([
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain quantum computing in simple terms."}
])

print(response["content"])
```

### Provider Switching

```python
# Switch providers with same interface
from facades.anthropic_facade import AnthropicFacade
from facades.google_facade import GoogleFacade

# OpenAI
openai_llm = OpenAIFacade(model_name="gpt-4")
response1 = openai_llm.chat_completion(messages)

# Anthropic
anthropic_llm = AnthropicFacade(model_name="claude-3-opus-20240229")
response2 = anthropic_llm.chat_completion(messages)

# Google
google_llm = GoogleFacade(model_name="gemini-pro")
response3 = google_llm.chat_completion(messages)

# All responses have the same structure!
```

### Streaming

```python
from facades.openai_facade import OpenAIFacade

llm = OpenAIFacade(model_name="gpt-4")

for chunk in llm.stream_chat_completion(messages):
    print(chunk, end="", flush=True)
```

### Function Calling

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        }
    }
]

response = llm.chat_completion(
    messages=[{"role": "user", "content": "What's the weather in NYC?"}],
    tools=tools
)

if "tool_calls" in response:
    for tool_call in response["tool_calls"]:
        print(f"Call {tool_call['function']['name']}")
        print(f"Args: {tool_call['function']['arguments']}")
```

### Capability Discovery

```python
from facades.llm_facade import ModelCapability

# Check capabilities before using
if llm.supports_capability(ModelCapability.VISION):
    response = llm.chat_completion_with_vision(messages, images)

if llm.supports_capability(ModelCapability.FUNCTION_CALLING):
    response = llm.chat_completion(messages, tools=tools)

# Get all capabilities
capabilities = llm.get_capabilities()
print(f"Model supports: {[cap.value for cap in capabilities]}")
```

### Context Manager

```python
with OpenAIFacade(model_name="gpt-4") as llm:
    response = llm.chat_completion(messages)
    print(response["content"])
# Automatically closes connections
```

## Configuration

### Generation Configuration

```python
from facades.llm_facade import GenerationConfig, ResponseFormat

config = GenerationConfig(
    max_tokens=1000,
    temperature=0.7,
    top_p=0.9,
    frequency_penalty=0.5,
    presence_penalty=0.5,
    stop_sequences=["END"],
    seed=42,
    response_format=ResponseFormat.JSON
)

response = llm.chat_completion(messages, config=config)
```

### Environment Variables

Each provider can be configured via environment variables:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Google
export GOOGLE_API_KEY="AIza..."

# Cohere
export COHERE_API_KEY="..."

# And so on...
```

## Monitoring & Logging

```python
# Get usage statistics
stats = llm.get_usage_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"Total tokens: {stats['total_tokens']}")
print(f"Total cost: ${stats['total_cost']}")

# Health check
if llm.health_check():
    print("Service is healthy")
```

## Error Handling

```python
from facades.llm_facade import (
    CapabilityNotSupportedException,
    RateLimitException,
    ContentFilterException,
    ContextLengthExceededException,
    AuthenticationException
)

try:
    response = llm.chat_completion(messages)
except CapabilityNotSupportedException as e:
    print(f"Feature not supported: {e}")
except RateLimitException as e:
    print(f"Rate limit hit. Retry after: {e.retry_after}")
except ContentFilterException as e:
    print(f"Content filtered: {e.category}")
except ContextLengthExceededException as e:
    print(f"Context too long: {e.provided} > {e.maximum}")
except AuthenticationException as e:
    print(f"Auth failed: {e}")
```

## Provider-Specific Documentation

Detailed documentation for each provider is available in the `docs/` directory:

- [OpenAI Documentation](docs/OPENAI_README.md)
- [Anthropic Documentation](docs/ANTHROPIC_README.md)
- [Google Documentation](docs/GOOGLE_README.md)
- [Cohere Documentation](docs/COHERE_README.md)
- [Mistral Documentation](docs/MISTRAL_README.md)
- [Groq Documentation](docs/GROQ_README.md)
- [AWS Bedrock Documentation](docs/AWSBEDROCK_README.md)
- [HuggingFace Documentation](docs/HUGGINGFACE_README.md)
- [Ollama Documentation](docs/OLLAMA_README.md)
- [Together Documentation](docs/TOGETHER_README.md)
- [Replicate Documentation](docs/REPLICATE_README.md)
- [Meta Documentation](docs/META_README.md)
- [Mock Documentation](docs/MOCK_README.md)

## Examples

Complete, executable examples for each provider are available in the `examples/` directory.

## Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific provider tests
python -m pytest tests/test_openai.py

# Run with coverage
python -m pytest --cov=facades tests/
```

## Performance Considerations

1. **Token Counting** - Use provider-specific tokenizers when available
2. **Streaming** - Prefer streaming for long responses
3. **Batching** - Use batch APIs when available
4. **Caching** - Enable prompt caching for repeated queries
5. **Connection Pooling** - Reuse facade instances when possible

## Best Practices

1. **Use Context Managers** - Ensures proper cleanup
2. **Check Capabilities** - Verify features before use
3. **Handle Errors** - Implement proper error handling
4. **Monitor Usage** - Track tokens and costs
5. **Log Requests** - Enable logging for debugging
6. **Set Timeouts** - Always configure request timeouts
7. **Retry Logic** - Use built-in retry mechanisms

## Contributing

This is proprietary software. Please contact ajsinha@gmail.com for licensing inquiries.

## License

Proprietary and Confidential. All Rights Reserved.

## Support

For support, please contact: ajsinha@gmail.com

---

**Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.**
