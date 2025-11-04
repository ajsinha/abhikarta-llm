<!--
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.3
-->

# Abhikarta LLM - Capability Examples

This directory contains 15 complete examples demonstrating core capabilities of Abhikarta LLM.

## Quick Start

```bash
# Run any example
python 01_basic_usage.py
python 02_multiple_providers.py
python 11_awsbedrock_example.py
```

## Examples Overview

### Core Features (1-10)

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

### Provider-Specific Examples (11-15)

| Example | File | Provider | Description |
|---------|------|----------|-------------|
| 11 | `11_awsbedrock_example.py` | AWS Bedrock | Enterprise AWS integration |
| 12 | `12_cohere_example.py` | Cohere | Command models |
| 13 | `13_huggingface_example.py` | HuggingFace | 100,000+ models |
| 14 | `14_meta_llama_example.py` | Meta | Direct Llama access |
| 15 | `15_replicate_example.py` | Replicate | Pay-per-use models |

## Requirements

- **No API keys required** - Examples 01-10 work with the mock provider
- To use real providers (examples 11-15), add API keys to config or environment

## Usage Pattern

All examples follow this pattern:

```python
from llm.abstraction.facade import UnifiedLLMFacade

# Configure provider
config = {
    'providers': {
        'mock': {  # or 'openai', 'anthropic', 'awsbedrock', etc.
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

## Supported Providers (13 Total)

### Cloud Providers (8)
- **OpenAI** - GPT-3.5, GPT-4, GPT-4o
- **Anthropic** - Claude 3 (Opus, Sonnet, Haiku)
- **Google** - Gemini Pro, Gemini Ultra
- **AWS Bedrock** - Claude, Llama, Titan, etc.
- **Cohere** - Command, Command-R
- **Groq** - Mixtral, Llama 2/3 (ultra-fast)
- **Mistral** - Mistral 7B, Mixtral 8x7B (GDPR)
- **Together** - 50+ open source models

### Self-Hosted / Community (4)
- **Ollama** - Local models (FREE)
- **HuggingFace** - 100,000+ models
- **Replicate** - Pay-per-use
- **Meta** - Direct Llama access

### Testing (1)
- **Mock** - Testing (no API key)

## Provider Setup Instructions

### AWS Bedrock (Example 11)
```bash
# 1. Set up AWS credentials
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_REGION=us-east-1

# 2. Enable Bedrock in AWS Console
# 3. Run example
python 11_awsbedrock_example.py
```

### Cohere (Example 12)
```bash
# 1. Sign up at https://cohere.ai
# 2. Get API key
export COHERE_API_KEY=your-cohere-key

# 3. Run example
python 12_cohere_example.py
```

### HuggingFace (Example 13)
```bash
# 1. Sign up at https://huggingface.co
# 2. Get API token
export HUGGINGFACE_API_KEY=your-hf-token

# 3. Run example
python 13_huggingface_example.py
```

### Meta Llama (Example 14)
```bash
# 1. Download Llama models from Meta
# 2. Accept license agreement
# 3. Update model_path in config
python 14_meta_llama_example.py

# Or use Ollama instead:
ollama pull llama2
# Then use ollama provider
```

### Replicate (Example 15)
```bash
# 1. Sign up at https://replicate.com
# 2. Get API token
export REPLICATE_API_TOKEN=your-replicate-token

# 3. Run example
python 15_replicate_example.py
```

## Advanced Usage

### Multiple Providers
```python
config = {
    'providers': {
        'openai': {'enabled': True, 'api_key': 'key1', 'model': 'gpt-4'},
        'anthropic': {'enabled': True, 'api_key': 'key2', 'model': 'claude-3-opus'},
        'awsbedrock': {'enabled': True, 'region': 'us-east-1', 'model': 'anthropic.claude-v2'}
    }
}
```

### Streaming
```python
for chunk in facade.stream_complete("Write a story"):
    print(chunk.text, end='', flush=True)
```

### Error Handling
```python
try:
    response = facade.complete("Prompt")
except Exception as e:
    print(f"Error: {e}")
```

## Next Steps

1. Run the examples (start with 01-10)
2. Check out the main documentation in `/docs`
3. Try with real providers by adding API keys (examples 11-15)
4. Build your own application!

## Comparison: When to Use Which Provider

| Use Case | Recommended Provider | Why |
|----------|---------------------|-----|
| General purpose | OpenAI GPT-4 | Best overall quality |
| Long conversations | Anthropic Claude | 100K context |
| Multimodal | Google Gemini | Native vision |
| Enterprise/AWS | AWS Bedrock | AWS integration |
| Speed critical | Groq | Ultra-fast inference |
| GDPR compliance | Mistral | European/privacy |
| Cost-effective | Together | Cheap open source |
| Local/offline | Ollama | FREE, private |
| Experimentation | HuggingFace | 100K+ models |
| Pay-per-use | Replicate | No subscription |
| Testing | Mock | No API key needed |

## Performance Comparison

| Provider | Avg Latency | Cost/1M tokens | Context Window |
|----------|-------------|----------------|----------------|
| Groq | 0.1s | $0.27 | 32K |
| OpenAI | 1-2s | $10-60 | 128K |
| Anthropic | 1-2s | $15-75 | 200K |
| Google | 1-2s | $1.25-10 | 32K |
| AWS Bedrock | 1-2s | Varies | Varies |
| Cohere | 1-2s | $1-15 | 4K-128K |
| Together | 1-3s | $0.20-1 | 32K |
| Ollama | 2-5s | FREE | Varies |

---

<!--
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.3
-->
