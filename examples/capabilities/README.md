<!--
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.2
-->

# Abhikarta LLM - Capability Examples

This directory contains 10 complete examples demonstrating core capabilities of Abhikarta LLM.

## Quick Start

```bash
# Run any example
python 01_basic_usage.py
python 02_multiple_providers.py
```

## Examples Overview

| Example | File | Description |
|---------|------|-------------|
| 01 | `01_basic_usage.py` | Basic text completion |
| 02 | `02_multiple_providers.py` | Configure multiple providers |
| 03 | `03_streaming.py` | Streaming responses |
| 04 | `04_chat_messages.py` | Chat with message history |
| 05 | `05_parameters.py` | Temperature & parameters |
| 06 | `06_provider_switching.py` | Switch between providers |
| 07 | `07_error_handling.py` | Error handling patterns |
| 08 | `08_metadata_usage.py` | Access metadata & usage stats |
| 09 | `09_batch_requests.py` | Batch processing |
| 10 | `10_provider_info.py` | Provider information |

## Requirements

- **No API keys required** - All examples work with the mock provider
- To use real providers (OpenAI, Anthropic, etc.), add API keys to config

## Usage Pattern

All examples follow this pattern:

```python
from llm.abstraction.facade import UnifiedLLMFacade

# Configure provider
config = {
    'providers': {
        'mock': {  # or 'openai', 'anthropic', 'groq', etc.
            'enabled': True,
            'model': 'mock-model'
        }
    }
}

# Create facade
facade = UnifiedLLMFacade(config)

# Make requests
response = facade.complete("Your prompt here")
print(response.text)
```

## Supported Providers

- **OpenAI** - GPT-3.5, GPT-4
- **Anthropic** - Claude 3
- **Google** - Gemini
- **Groq** - Ultra-fast inference
- **Mistral** - GDPR-compliant
- **Together** - 50+ open source models
- **Ollama** - Local, FREE
- **Mock** - Testing (no API key)

## Next Steps

1. Run the examples
2. Check out the main documentation in `/docs`
3. Try with real providers by adding API keys
4. Build your own application!

---

<!--
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.2
-->
