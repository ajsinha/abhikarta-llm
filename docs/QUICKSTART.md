# LLM Abstraction System - Quick Start Guide

**© 2025-2030 All Rights Reserved**  
**Ashutosh Sinha** | ajsinha@gmail.com

## Installation

1. **Extract the archive:**
   ```bash
   tar -xzf llm_abstraction.tar.gz
   cd llm_abstraction
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys:**
   Edit `config/application.properties` and add your API keys.

## 5-Minute Tutorial

### 1. Basic Usage (Mock Provider - No API Keys Needed)

```python
from clients.client_facade import LLMClientFacade

# Initialize
facade = LLMClientFacade('config/application.properties')

# Generate text with mock provider
response = facade.generate(
    "What is Python?",
    provider="mock",
    model_name="mock-model-1"
)
print(response)
```

### 2. Using Real Providers

After setting up API keys, use any provider:

```python
# OpenAI GPT-4
response = facade.generate(
    "Explain quantum computing",
    provider="openai",
    model_name="gpt-4"
)

# AWS Bedrock Claude
response = facade.generate(
    "Explain quantum computing",
    provider="bedrock",
    model_name="claude-3-sonnet"
)

# Together AI Llama
response = facade.generate(
    "Explain quantum computing",
    provider="together",
    model_name="llama-3-8b-instruct"
)
```

### 3. Chat Completion

```python
messages = [
    {"role": "user", "content": "What is AI?"},
    {"role": "assistant", "content": "AI is..."},
    {"role": "user", "content": "Tell me more"}
]

response = facade.chat(messages, provider="mock", model_name="mock-model-1")
```

## Running Examples

```bash
# Test with mock provider (no API keys needed)
python examples/mock_testing.py

# Basic usage example
python examples/basic_usage.py

# Provider override example
python examples/provider_override.py

# Showcase all models
python examples/all_models_showcase.py
```

## Supported Providers & Models (25+ models)

### AWS Bedrock
- Claude 3 (Opus, Sonnet, Haiku)
- Llama 2 70B, Llama 3 8B
- Mistral 7B

### Together AI
- Llama 2 70B Chat
- Llama 3 8B/70B Instruct
- Mistral 7B Instruct

### Hugging Face
- Meta-Llama models
- Falcon 40B
- Various open-source models

### OpenAI
- GPT-4, GPT-4 Turbo
- GPT-3.5 Turbo

### Anthropic
- Claude 3 (Opus, Sonnet, Haiku)

### Cohere
- Command, Command Light, Command R

### Google
- Gemini Pro/Ultra
- PaLM 2

### Mock (Testing)
- Mock Model 1, Mock Model 2

## Key Features

✅ **Factory Pattern** - Automatic provider registration  
✅ **Facade Pattern** - Simple, unified interface  
✅ **Configuration-Driven** - Change providers without code changes  
✅ **Multiple Providers** - 8 providers, 25+ models  
✅ **Llama Models** - Full support for Llama 2 and Llama 3  
✅ **Mock Testing** - Test without API calls  
✅ **Provider Override** - Specify provider at runtime  
✅ **Streaming Support** - For compatible models  
✅ **Caching** - Automatic client/model caching  

## Architecture Highlights

The system implements three design patterns:

1. **Factory Pattern**: `LLMModelFactory` and `LLMClientFactory` create instances
2. **Facade Pattern**: `LLMClientFacade` provides simplified interface
3. **Abstract Classes**: `BaseLLMModel` and `BaseLLMClient` ensure consistency

## Project Structure

```
llm_abstraction/
├── config/
│   └── application.properties    # Configuration
├── models/
│   ├── base_model.py             # Abstract model
│   ├── model_factory.py          # Factory pattern
│   ├── model_facade.py           # Facade pattern
│   └── implementations/          # Provider models
├── clients/
│   ├── base_client.py            # Abstract client
│   ├── client_factory.py         # Factory pattern
│   ├── client_facade.py          # Main entry point
│   └── implementations/          # Provider clients
├── utils/
│   └── properties_configurator.py
├── examples/
│   ├── basic_usage.py
│   ├── provider_override.py
│   ├── mock_testing.py
│   └── all_models_showcase.py
└── README.md
```

## Configuration Example

```properties
# Default provider and model
llm.default.provider=mock
llm.default.model=mock-model-1

# AWS Bedrock
provider.bedrock.enabled=true
provider.bedrock.access_key=YOUR_KEY
provider.bedrock.secret_key=YOUR_SECRET

# OpenAI
provider.openai.enabled=true
provider.openai.api_key=YOUR_KEY

# Together AI
provider.together.enabled=true
provider.together.api_key=YOUR_KEY
```

## Next Steps

1. **Run mock examples** to understand the system
2. **Add your API keys** to configuration
3. **Test with real providers**
4. **Integrate into your application**
5. **Extend with custom providers** if needed

## Common Use Cases

### 1. Multi-Model Comparison
```python
providers = [("openai", "gpt-4"), ("anthropic", "claude-3-sonnet")]
for provider, model in providers:
    response = facade.generate(prompt, provider=provider, model_name=model)
    print(f"{provider}: {response}")
```

### 2. Fallback Strategy
```python
try:
    response = facade.generate(prompt, provider="openai", model_name="gpt-4")
except:
    response = facade.generate(prompt, provider="mock", model_name="mock-model-1")
```

### 3. A/B Testing
```python
import random
provider = random.choice(["bedrock", "openai", "anthropic"])
response = facade.generate(prompt, provider=provider)
```

## Support

For questions or issues, contact: ajsinha@gmail.com

## License

© 2025-2030 All Rights Reserved  
Ashutosh Sinha  
See LICENSE file for details.
