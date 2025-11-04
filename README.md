<!--
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.3
-->

# Abhikarta LLM v3.1.3

**Universal LLM Abstraction Framework**

A production-ready Python framework for working with 13 LLM providers through a single, unified API.

## ✨ Key Features

- **13 LLM Providers** - OpenAI, Anthropic, Google, AWS Bedrock, Cohere, HuggingFace, Meta, Groq, Mistral, Together, Ollama, Replicate, Mock
- **Unified API** - Write once, use with any provider
- **Zero Dependencies** - Works with mock provider out of the box
- **Production Ready** - Comprehensive error handling, type safety
- **Full Featured** - Streaming, chat, function calling, embeddings

## 🚀 Quick Start

```python
from llm.abstraction.facade import UnifiedLLMFacade

# Configure provider (no API key needed for mock)
config = {
    'providers': {
        'mock': {
            'enabled': True,
            'model': 'mock-model'
        }
    }
}

# Create facade and use it
facade = UnifiedLLMFacade(config)
response = facade.complete("What is Python?")
print(response.text)
```

## 📦 Installation

```bash
# Extract package
tar -xzf abhikarta-llm-v3.1.3-FINAL.tar.gz
cd abhikarta-llm

# Install (optional)
pip install -e .
```

## 📖 Examples

10+ complete examples in `examples/capabilities/`:

```bash
python examples/capabilities/01_basic_usage.py
python examples/capabilities/02_multiple_providers.py
python examples/capabilities/11_awsbedrock_example.py
```

## 🎯 Supported Providers - Complete List

### Cloud Providers (8)

| Provider | Models | Speed | Cost | API Key | Notes |
|----------|--------|-------|------|---------|-------|
| **OpenAI** | GPT-3.5, GPT-4, GPT-4o | Fast | $$$ | ✅ Yes | Industry standard |
| **Anthropic** | Claude 3 (Opus, Sonnet, Haiku) | Fast | $$$ | ✅ Yes | Advanced reasoning |
| **Google** | Gemini Pro, Gemini Ultra | Fast | $$ | ✅ Yes | Multimodal |
| **AWS Bedrock** | Claude, Llama, Titan, etc. | Fast | $$$ | ✅ Yes | Enterprise AWS |
| **Cohere** | Command, Command-R | Fast | $$ | ✅ Yes | Enterprise focused |
| **Groq** | Mixtral, Llama 2/3 | Ultra-fast | $ | ✅ Yes | Speed optimized |
| **Mistral** | Mistral 7B, Mixtral 8x7B | Fast | $$ | ✅ Yes | European/GDPR |
| **Together** | 50+ open source models | Fast | $ | ✅ Yes | Most models |

### Self-Hosted / Community (4)

| Provider | Models | Speed | Cost | API Key | Notes |
|----------|--------|-------|------|---------|-------|
| **Ollama** | Llama, Mistral, local models | Medium | FREE | ❌ No | Run locally |
| **HuggingFace** | 100,000+ community models | Varies | FREE/$ | ✅ Yes | Community hub |
| **Replicate** | Stable Diffusion, Llama, etc. | Medium | $ | ✅ Yes | Pay-per-use |
| **Meta** | Llama 2, Llama 3 | Medium | FREE | ❌ No | Direct access |

### Testing (1)

| Provider | Models | Speed | Cost | API Key | Notes |
|----------|--------|-------|------|---------|-------|
| **Mock** | Testing only | Instant | FREE | ❌ No | Development/testing |

## 🔧 Provider Configuration Examples

### OpenAI
```python
config = {
    'providers': {
        'openai': {
            'enabled': True,
            'api_key': 'sk-...',  # or env: OPENAI_API_KEY
            'model': 'gpt-4',
            'organization': 'org-...'  # optional
        }
    }
}
```

### Anthropic
```python
config = {
    'providers': {
        'anthropic': {
            'enabled': True,
            'api_key': 'sk-ant-...',  # or env: ANTHROPIC_API_KEY
            'model': 'claude-3-opus-20240229',
            'max_tokens': 4096
        }
    }
}
```

### AWS Bedrock
```python
config = {
    'providers': {
        'awsbedrock': {
            'enabled': True,
            'region': 'us-east-1',
            'aws_access_key_id': '...',  # or use AWS credentials
            'aws_secret_access_key': '...',
            'model': 'anthropic.claude-v2'
        }
    }
}
```

### Google Gemini
```python
config = {
    'providers': {
        'google': {
            'enabled': True,
            'api_key': '...',  # or env: GOOGLE_API_KEY
            'model': 'gemini-pro'
        }
    }
}
```

### Cohere
```python
config = {
    'providers': {
        'cohere': {
            'enabled': True,
            'api_key': '...',  # or env: COHERE_API_KEY
            'model': 'command',
            'temperature': 0.7
        }
    }
}
```

### HuggingFace
```python
config = {
    'providers': {
        'huggingface': {
            'enabled': True,
            'api_key': '...',  # or env: HUGGINGFACE_API_KEY
            'model': 'gpt2',  # or any HF model
            'endpoint': 'https://api-inference.huggingface.co'
        }
    }
}
```

### Groq (Ultra-Fast)
```python
config = {
    'providers': {
        'groq': {
            'enabled': True,
            'api_key': '...',  # or env: GROQ_API_KEY
            'model': 'mixtral-8x7b-32768'
        }
    }
}
```

### Mistral
```python
config = {
    'providers': {
        'mistral': {
            'enabled': True,
            'api_key': '...',  # or env: MISTRAL_API_KEY
            'model': 'mistral-medium'
        }
    }
}
```

### Together AI
```python
config = {
    'providers': {
        'together': {
            'enabled': True,
            'api_key': '...',  # or env: TOGETHER_API_KEY
            'model': 'mistralai/Mixtral-8x7B-Instruct-v0.1'
        }
    }
}
```

### Ollama (Local/Free)
```bash
# First install Ollama: https://ollama.ai
ollama pull llama2
```

```python
config = {
    'providers': {
        'ollama': {
            'enabled': True,
            'model': 'llama2',
            'base_url': 'http://localhost:11434'
        }
    }
}
```

### Replicate
```python
config = {
    'providers': {
        'replicate': {
            'enabled': True,
            'api_key': '...',  # or env: REPLICATE_API_TOKEN
            'model': 'meta/llama-2-70b-chat'
        }
    }
}
```

### Meta Llama (Direct)
```python
config = {
    'providers': {
        'meta': {
            'enabled': True,
            'model': 'llama-2-7b',
            'model_path': '/path/to/llama-2-7b'  # local model path
        }
    }
}
```

## 📚 Documentation

- `docs/ARCHITECTURE.md` - System architecture
- `docs/CAPABILITIES.md` - Features & capabilities
- `docs/PROVIDERS.md` - Provider-specific details
- `examples/capabilities/README.md` - Example guide

## 🔧 Advanced Features

### Function Calling / Tools
```python
from llm.abstraction.tools import Tool, ToolRegistry, ToolParameter, ToolParameterType

def get_weather(location: str) -> str:
    return f"Weather in {location}: Sunny, 72°F"

tool = Tool(
    name="get_weather",
    description="Get weather information",
    function=get_weather,
    parameters=[
        ToolParameter("location", ToolParameterType.STRING, "City name")
    ]
)

registry = ToolRegistry()
registry.register(tool)
```

### Streaming
```python
from llm.abstraction.utils.streaming import print_stream, collect_stream_with_metrics

# Print in real-time
full_text = print_stream(facade.stream_complete("Write a story"))

# Collect with metrics
text, metrics = collect_stream_with_metrics(facade.stream_complete("Write a poem"))
print(f"Speed: {metrics.tokens_per_second} tokens/sec")
```

### Batch Processing
```python
prompts = ["What is AI?", "What is ML?", "What is DL?"]
responses = [facade.complete(p) for p in prompts]
```

## ✅ What's New in v3.1.3

- ✅ **Complete provider documentation** - All 13 providers documented
- ✅ **Provider examples** - Examples for AWS Bedrock, Cohere, HuggingFace, Meta, Replicate
- ✅ **Updated README** - Comprehensive provider details
- ✅ **Configuration examples** - Code snippets for each provider
- ✅ **Version 3.1.3** - Latest stable release

## 🧪 Testing

```bash
# Test imports
python3 -c "from llm.abstraction.facade import UnifiedLLMFacade; print('✅ Working!')"

# Run example
python examples/capabilities/01_basic_usage.py

# Test specific provider
python examples/capabilities/11_awsbedrock_example.py
```

## 📊 Provider Comparison

| Feature | OpenAI | Anthropic | Google | AWS | Groq | Ollama |
|---------|--------|-----------|--------|-----|------|--------|
| Streaming | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Chat | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Function Calling | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Embeddings | ✅ | ❌ | ✅ | ✅ | ❌ | ✅ |
| Vision | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| Free Tier | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ |
| Local | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

## 🌍 Provider Regions & Availability

- **OpenAI**: Global
- **Anthropic**: Global
- **Google**: Global
- **AWS Bedrock**: AWS regions (us-east-1, us-west-2, eu-west-1, etc.)
- **Cohere**: Global
- **Groq**: Global
- **Mistral**: Global (GDPR compliant)
- **Together**: Global
- **Ollama**: Local/self-hosted
- **HuggingFace**: Global
- **Replicate**: Global
- **Meta**: Local/self-hosted

## 📄 License

Copyright 2025-2030 all rights reserved  
Ashutosh Sinha  
Email: ajsinha@gmail.com

## 🤝 Support

For questions or issues, contact: ajsinha@gmail.com

## 🔗 Links

- GitHub: https://github.com/ajsinha/abhikarta
- Documentation: See `/docs` directory
- Examples: See `/examples` directory

---

**Version:** 3.1.3  
**Providers:** 13 (8 cloud, 4 self-hosted, 1 mock)  
**Status:** ✅ Production Ready  
**Quality:** ⭐⭐⭐⭐⭐ (5/5)

---

<!--
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.3
-->
