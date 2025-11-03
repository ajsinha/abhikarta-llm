# Abhikarta LLM Abstraction System

**Version:** 1.0.0  
**Author:** Ashutosh Sinha  
**Email:** ajsinha@gmail.com  
**Repository:** https://github.com/ajsinha/abhikarta

---

## Overview

The Abhikarta LLM Abstraction System provides a unified, configuration-driven interface for interacting with multiple Large Language Model providers. This system abstracts the complexity of different LLM APIs while providing a consistent, extensible, and maintainable architecture.

### Key Features

- **Provider Agnostic**: Seamlessly switch between LLM providers without code changes
- **Configuration-Driven**: All provider and model settings managed through configuration files
- **Extensible**: Plugin architecture allows easy addition of new providers
- **Comprehensive History**: Track all interactions with detailed statistics
- **Mock Provider**: Built-in testing support without requiring API keys
- **Type-Safe**: Full type hints for better IDE support and code quality

### Supported Providers

- ✅ **Mock** - For testing and development (no API key required)
- ✅ **Anthropic** - Claude models
- ✅ **OpenAI** - GPT models
- 🚧 **Google** - Gemini models (placeholder)
- 🚧 **Meta** - Llama models (placeholder)
- 🚧 **HuggingFace** - Open source models (placeholder)
- 🚧 **AWS Bedrock** - Various models (placeholder)

---

## Installation

### From Source

```bash
git clone https://github.com/ajsinha/abhikarta
cd abhikarta-llm
pip install -e .
```

### With Provider Dependencies

```bash
# Install with Anthropic support
pip install -e ".[anthropic]"

# Install with OpenAI support
pip install -e ".[openai]"

# Install with all providers
pip install -e ".[all]"

# Install with development tools
pip install -e ".[dev]"
```

---

## Quick Start

### 1. Basic Usage (Mock Provider)

```python
from llm.abstraction import LLMClientFactory

# Initialize factory
factory = LLMClientFactory()
factory.initialize(config_path="../config/llm_config.json")

# Create a client with mock provider (no API key needed)
client = factory.create_default_client()

# Simple completion
response = client.complete("What is Python?")
print(response)

# Chat interaction
response = client.chat("Hello! How are you?")
print(response)
```

### 2. Using Real Providers

```python
import os

# Set your API key
os.environ['ANTHROPIC_API_KEY'] = 'your-api-key-here'

# Create client with Anthropic
factory = LLMClientFactory()
factory.initialize(config_path="config/llm_config.json")

client = factory.create_client(
    provider='anthropic',
    model='claude-3-haiku-20240307'
)

# Use the client
response = client.chat("Explain quantum computing in simple terms")
print(response)
```

### 3. Streaming Responses

```python
# Stream completion tokens
for token in client.stream_complete("Count from 1 to 10"):
    print(token, end='', flush=True)

# Stream chat responses
for token in client.stream_chat("Tell me a short story"):
    print(token, end='', flush=True)
```

### 4. Working with History

```python
# Get interaction statistics
stats = client.get_history_summary()
print(f"Total interactions: {stats['total_interactions']}")
print(f"Total tokens: {stats['total_tokens']}")
print(f"Total cost: ${stats['total_cost']:.4f}")

# Export history
client.export_history('my_history.json')
```

---

## Configuration

### Environment Variables

Set API keys via environment variables:

```bash
export ANTHROPIC_API_KEY=your_anthropic_key
export OPENAI_API_KEY=your_openai_key
export GOOGLE_API_KEY=your_google_key
```

### Properties File

Edit `config/llm.properties`:

```properties
# Default provider and model
llm.default.provider=anthropic
llm.default.model=claude-3-haiku-20240307

# History settings
llm.history.size=50

# Logging
llm.log.level=INFO
```

### JSON Configuration

The main configuration is in `config/llm_config.json`:

```json
{
  "version": "1.0.0",
  "default_provider": "anthropic",
  "default_model": "claude-3-haiku-20240307",
  "providers": {
    "anthropic": {
      "module": "llm.abstraction.providers.anthropic",
      "class": "AnthropicProvider",
      "enabled": true,
      "config_file": "config/providers/anthropic.json"
    }
  },
  "global_settings": {
    "history_size": 50,
    "max_retries": 3,
    "timeout": 30
  }
}
```

---

## Architecture

### Core Components

1. **LLMProvider** - Abstract base for all provider implementations
2. **LLMFacade** - Simplified interface to provider operations
3. **LLMClient** - High-level user-facing client
4. **LLMProviderFactory** - Singleton for creating providers
5. **LLMClientFactory** - Singleton for creating clients
6. **InteractionHistory** - Manages interaction tracking

### Design Patterns

- **Factory Pattern** - For creating providers and clients
- **Singleton Pattern** - For factory instances
- **Facade Pattern** - For simplified provider interfaces
- **Plugin Architecture** - For extensible provider support

---

## Examples

The `llm/abstraction/examples/` directory contains several examples:

- `basic_usage.py` - Basic operations and features
- `multi_provider.py` - Comparing multiple providers

Run examples:

```bash
cd abhikarta-llm
python -m llm.abstraction.examples.basic_usage
python -m llm.abstraction.examples.multi_provider
```

---

## Project Structure

```
abhikarta-llm/
├── llm/
│   └── abstraction/
│       ├── core/              # Core abstractions
│       │   ├── provider.py
│       │   ├── facade.py
│       │   ├── client.py
│       │   ├── factories.py
│       │   ├── history.py
│       │   └── exceptions.py
│       ├── providers/         # Provider implementations
│       │   ├── mock/
│       │   ├── anthropic/
│       │   ├── openai/
│       │   └── ...
│       ├── config/            # Configuration utilities
│       ├── utils/             # Utility functions
│       └── examples/          # Usage examples
├── config/                    # Configuration files
│   ├── llm_config.json
│   ├── llm.properties
│   └── providers/
├── tests/                     # Test suite
├── setup.py                   # Installation script
└── README.md                  # This file
```

---

## API Reference

### LLMClient Methods

#### `complete(prompt, temperature=0.7, max_tokens=1000, **kwargs) -> str`
Generate a completion for a prompt.

#### `chat(message, temperature=0.7, max_tokens=1000, use_history=True, **kwargs) -> str`
Send a chat message and get a response.

#### `stream_complete(prompt, temperature=0.7, max_tokens=1000, **kwargs) -> Iterator[str]`
Stream completion tokens as they are generated.

#### `stream_chat(message, temperature=0.7, max_tokens=1000, use_history=True, **kwargs) -> Iterator[str]`
Stream chat response tokens.

#### `batch_complete(prompts, temperature=0.7, max_tokens=1000, **kwargs) -> List[str]`
Process multiple prompts in batch.

#### `get_history_summary() -> Dict[str, Any]`
Get statistics about interaction history.

#### `export_history(filepath: str) -> None`
Export interaction history to JSON file.

---

## Testing

Run the basic example with the mock provider (no API keys needed):

```bash
python -m llm.abstraction.examples.basic_usage
```

---

## Adding New Providers

To add a new provider:

1. Create a new directory: `llm/abstraction/providers/myprovider/`
2. Implement `provider.py` inheriting from `LLMProvider`
3. Implement `facade.py` inheriting from `LLMFacade`
4. Create configuration: `config/providers/myprovider.json`
5. Add to main config: `config/llm_config.json`

See existing providers for reference.

---

## Requirements

- Python >= 3.8
- pydantic >= 2.0

### Optional Provider Dependencies

- anthropic >= 0.18 (for Anthropic)
- openai >= 1.0 (for OpenAI)
- google-generativeai >= 0.3 (for Google)
- transformers >= 4.30 (for HuggingFace)
- boto3 >= 1.28 (for AWS Bedrock)

---

## License

© 2025-2030 All rights reserved  
Ashutosh Sinha

---

## Support

For issues, questions, or contributions:
- **Email:** ajsinha@gmail.com
- **GitHub:** https://github.com/ajsinha/abhikarta

---

## Changelog

### Version 1.0.0 (2025-11)
- Initial release
- Mock, Anthropic, and OpenAI providers
- Configuration-driven architecture
- Interaction history management
- Comprehensive examples and documentation
