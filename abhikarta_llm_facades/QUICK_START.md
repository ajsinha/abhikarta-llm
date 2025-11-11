# Quick Start Guide - Abhikarta LLM Facades

**Copyright © 2025-2030 Ashutosh Sinha (ajsinha@gmail.com). All Rights Reserved.**

## Installation

```bash
# Clone or download the project
cd abhikarta_llm_facades

# Install with all dependencies
pip install -e .[all]

# Or install specific providers only
pip install -e .[openai,anthropic]
```

## First Example (5 minutes)

```python
# example.py
from facades.openai_facade import OpenAIFacade

# Set your API key
import os
os.environ["OPENAI_API_KEY"] = "your-key-here"

# Create facade
llm = OpenAIFacade(model_name="gpt-4")

# Chat
response = llm.chat_completion([
    {"role": "user", "content": "What is AI?"}
])

print(response["content"])
```

## Switch Providers (Same API!)

```python
from facades.anthropic_facade import AnthropicFacade
from facades.google_facade import GoogleFacade

# Same messages work with any provider
messages = [{"role": "user", "content": "Hello!"}]

# Try OpenAI
openai_llm = OpenAIFacade(model_name="gpt-4")
response1 = openai_llm.chat_completion(messages)

# Try Anthropic
anthropic_llm = AnthropicFacade(model_name="claude-3-opus-20240229")
response2 = anthropic_llm.chat_completion(messages)

# Try Google
google_llm = GoogleFacade(model_name="gemini-pro")
response3 = google_llm.chat_completion(messages)

# All have the same response format!
```

## Streaming

```python
from facades.openai_facade import OpenAIFacade

llm = OpenAIFacade(model_name="gpt-4")

for chunk in llm.stream_chat_completion(messages):
    print(chunk, end="", flush=True)
```

## With Configuration

```python
from facades.llm_facade import GenerationConfig

config = GenerationConfig(
    max_tokens=500,
    temperature=0.7,
    top_p=0.9
)

response = llm.chat_completion(messages, config=config)
```

## Check Capabilities

```python
from facades.llm_facade import ModelCapability

if llm.supports_capability(ModelCapability.FUNCTION_CALLING):
    print("This model supports function calling!")

capabilities = llm.get_capabilities()
for cap in capabilities:
    print(f"- {cap.value}")
```

## Function Calling

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
                }
            }
        }
    }
]

response = llm.chat_completion(
    messages=[{"role": "user", "content": "Weather in NYC?"}],
    tools=tools
)
```

## Error Handling

```python
from facades.llm_facade import (
    RateLimitException,
    AuthenticationException
)

try:
    response = llm.chat_completion(messages)
except RateLimitException as e:
    print(f"Rate limited: {e}")
except AuthenticationException as e:
    print(f"Auth failed: {e}")
```

## Next Steps

1. Browse `examples/` directory for complete examples
2. Read `docs/` for detailed provider documentation
3. Check `tests/` for usage patterns
4. See main `README.md` for comprehensive guide

## Environment Variables

Set API keys via environment variables:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="AIza..."
export COHERE_API_KEY="..."
export MISTRAL_API_KEY="..."
export GROQ_API_KEY="..."
export HF_TOKEN="hf_..."
export TOGETHER_API_KEY="..."
export REPLICATE_API_TOKEN="r8_..."
```

## Run Examples

```bash
# OpenAI
python examples/openai_example.py

# Anthropic
python examples/anthropic_example.py

# Any provider
python examples/{provider}_example.py
```

## Help & Support

Email: ajsinha@gmail.com

---

**Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.**
