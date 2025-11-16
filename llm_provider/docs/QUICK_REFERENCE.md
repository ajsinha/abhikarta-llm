# Abhikarta Facade System - Quick Reference Card

## Installation & Setup

### Install Dependencies
```bash
pip install anthropic openai pillow tiktoken
```

### Import and Register
```python
import register_facades  # Auto-registers all facades
from facade_factory import FacadeFactory
```

## Factory Creation

### JSON Configuration
```python
factory = FacadeFactory(
    config_source="json",
    config_path="./config"
)
```

### Database Configuration
```python
from model_management.model_management_db_handler import ModelManagementDBHandler

db_handler = ModelManagementDBHandler.get_instance("./db_management.sqlite")
factory = FacadeFactory(config_source="db", db_handler=db_handler)
```

## Facade Creation

### Basic Creation
```python
facade = factory.create_facade(
    provider_name="anthropic",
    model_name="claude-3-5-sonnet-20241022"
)
```

### Cost-Optimized Creation
```python
facade, cost = factory.create_cheapest_facade(
    capability="chat",
    input_tokens=10000,
    output_tokens=500
)
```

## Common Operations

### Chat Completion
```python
response = facade.chat_completion(
    messages=[
        {"role": "user", "content": "Your question"}
    ],
    temperature=0.7,
    max_tokens=1000
)
print(response["content"])
```

### Streaming
```python
for chunk in facade.stream_chat_completion(messages):
    print(chunk, end="", flush=True)
```

### Async
```python
response = await facade.achat_completion(messages)
```

### Vision
```python
from PIL import Image
image = Image.open("image.png")

response = facade.chat_completion_with_vision(
    messages=[{"role": "user", "content": "What's in this?"}],
    images=[image]
)
```

### Tool Use / Function Calling
```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            }
        }
    }
}]

response = facade.chat_completion(messages, tools=tools)

if response["tool_calls"]:
    for tc in response["tool_calls"]:
        print(f"Tool: {tc['function']['name']}")
```

## Information & Capabilities

### List Providers
```python
providers = factory.list_providers()
for name, info in providers.items():
    print(f"{name}: {info['model_count']} models")
```

### List Models
```python
models = factory.list_models("anthropic")
print(models["anthropic"])
```

### Check Capabilities
```python
caps = facade.get_capabilities()
if ModelCapability.VISION in caps:
    # Use vision features
    pass
```

### Get Model Info
```python
info = facade.get_model_info()
print(f"Context: {info['context_window']:,}")
print(f"Max Output: {info['max_output']:,}")
print(f"Input Cost: ${info['pricing']['input_per_1m_tokens']}/1M")
```

### Estimate Cost
```python
cost = facade.estimate_cost(
    prompt_tokens=1000,
    completion_tokens=500
)
print(f"Estimated: ${cost:.6f}")
```

## Error Handling

```python
from llm_facade import (
    AuthenticationException,
    RateLimitException,
    CapabilityNotSupportedException,
    ContextLengthExceededException
)

try:
    response = facade.chat_completion(messages)
except AuthenticationException:
    print("Invalid API key")
except RateLimitException as e:
    print(f"Rate limited. Retry in {e.retry_after}s")
except CapabilityNotSupportedException as e:
    print(f"Not supported: {e.capability}")
except ContextLengthExceededException as e:
    print(f"Too long: {e.provided} > {e.maximum}")
```

## Environment Variables

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="..."
```

## Provider-Specific Features

### Anthropic
```python
# System prompts
response = facade.chat_completion(
    messages=[{"role": "user", "content": "Hello"}],
    system="You are a Python expert"
)
```

### OpenAI
```python
# JSON mode
response = facade.chat_completion(
    messages=[{"role": "user", "content": "List 3 colors"}],
    response_format={"type": "json_object"}
)

# Embeddings
embedding = facade.generate_embeddings("text")

# Image generation (DALL-E)
image_url = facade.generate_image("A sunset")

# Moderation
result = facade.moderate_content("text to check")
```

## Context Manager

```python
with factory.create_facade("anthropic", "model") as facade:
    response = facade.chat_completion(messages)
# Automatically closed
```

## Best Practices

### 1. Always Check Capabilities
```python
if facade.supports_capability(ModelCapability.VISION):
    # Use vision
else:
    # Fallback
```

### 2. Stay Within Context Limits
```python
context_limit = facade.get_context_window_size()
tokens = facade.count_tokens(text)
if tokens > context_limit * 0.8:
    # Truncate or split
```

### 3. Handle Errors Gracefully
```python
try:
    response = facade.chat_completion(messages)
except Exception as e:
    # Log and handle
    pass
```

### 4. Monitor Costs
```python
cost = facade.estimate_cost(1000, 500)
if cost > budget:
    # Use cheaper model
    facade, _ = factory.create_cheapest_facade("chat")
```

## Key Files

- `facade_factory.py` - Universal factory
- `base_provider_facade.py` - Base implementation
- `anthropic_facade.py` - Anthropic/Claude
- `openai_facade.py` - OpenAI/GPT
- `register_facades.py` - Registration
- `provider_facade_template.py` - Template for new providers
- `Abhikarta_Model_Facade_README_and_Quickguide.md` - Full docs

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Provider not found | Check `factory.list_providers()` |
| Model not found | Check `factory.list_models(provider)` |
| No facade found | Import `register_facades` |
| Auth failed | Set environment variable |
| Context too long | Check `get_context_window_size()` |

## Complete Example

```python
import register_facades
from facade_factory import FacadeFactory
from llm_facade import ModelCapability

def main():
    # Setup
    factory = FacadeFactory(
        config_source="json",
        config_path="./config"
    )
    
    # Create facade
    facade = factory.create_facade(
        "anthropic",
        "claude-3-5-sonnet-20241022"
    )
    
    # Check capabilities
    print(f"Capabilities: {facade.get_capabilities()}")
    
    # Get info
    info = facade.get_model_info()
    print(f"Context: {info['context_window']:,} tokens")
    
    # Chat
    response = facade.chat_completion(
        messages=[{"role": "user", "content": "Hello!"}],
        max_tokens=100
    )
    
    print(f"Response: {response['content']}")
    print(f"Tokens: {response['usage'].total_tokens}")
    
    # Cost
    cost = facade.estimate_cost(
        response['usage'].prompt_tokens,
        response['usage'].completion_tokens
    )
    print(f"Cost: ${cost:.6f}")

if __name__ == "__main__":
    main()
```

---

For full documentation, see `Abhikarta_Model_Facade_README_and_Quickguide.md`

**Copyright © 2025-2030 | Ashutosh Sinha | ajsinha@gmail.com**
