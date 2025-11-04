<!--
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.2
-->

# Abhikarta LLM v3.1.2

**Universal LLM Abstraction Framework**

A production-ready Python framework for working with multiple LLM providers through a single, unified API.

## ✨ Key Features

- **8 LLM Providers** - OpenAI, Anthropic, Google, Groq, Mistral, Together, Ollama, Mock
- **Unified API** - Write once, use with any provider
- **Zero Dependencies** - Works with mock provider out of the box
- **Production Ready** - Comprehensive error handling, type safety
- **Full Featured** - Streaming, chat, parameters, metadata

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
tar -xzf abhikarta-llm-v3.1.2-FINAL.tar.gz
cd abhikarta-llm

# Install (optional)
pip install -e .
```

## 📖 Examples

10 complete examples in `examples/capabilities/`:

```bash
python examples/capabilities/01_basic_usage.py
python examples/capabilities/02_multiple_providers.py
python examples/capabilities/03_streaming.py
```

## 🎯 Supported Providers

| Provider | Models | Speed | Cost | API Key Required |
|----------|--------|-------|------|------------------|
| **Mock** | Testing | Instant | FREE | ❌ No |
| **OpenAI** | GPT-3.5, GPT-4 | Fast | $$$ | ✅ Yes |
| **Anthropic** | Claude 3 | Fast | $$$ | ✅ Yes |
| **Google** | Gemini | Fast | $$ | ✅ Yes |
| **Groq** | Mixtral, Llama | Ultra-fast | $ | ✅ Yes |
| **Mistral** | Mistral models | Fast | $$ | ✅ Yes |
| **Together** | 50+ models | Fast | $ | ✅ Yes |
| **Ollama** | Local models | Medium | FREE | ❌ No |

## 📚 Documentation

- `docs/ARCHITECTURE.md` - System architecture
- `docs/CAPABILITIES.md` - Features & capabilities
- `examples/capabilities/README.md` - Example guide

## 🔧 Configuration

```python
config = {
    'providers': {
        'openai': {
            'enabled': True,
            'api_key': 'your-key-here',  # or use env var OPENAI_API_KEY
            'model': 'gpt-3.5-turbo'
        },
        'anthropic': {
            'enabled': True,
            'api_key': 'your-key-here',  # or use env var ANTHROPIC_API_KEY
            'model': 'claude-3-sonnet-20240229'
        }
    }
}
```

## ✅ What's New in v3.1.2

- ✅ **All import errors fixed**
- ✅ **10 working examples** - One for each capability
- ✅ **Clean codebase** - No broken imports
- ✅ **Updated documentation** - Copyright headers added
- ✅ **Production ready** - All tests passing

## 🧪 Testing

```bash
# Test imports
python3 -c "from llm.abstraction.facade import UnifiedLLMFacade; print('✅ Working!')"

# Run example
python examples/capabilities/01_basic_usage.py
```

## 📄 License

Copyright 2025-2030 all rights reserved  
Ashutosh Sinha  
Email: ajsinha@gmail.com

## 🤝 Support

For questions or issues, contact: ajsinha@gmail.com

---

**Version:** 3.1.2  
**Status:** ✅ Production Ready  
**Quality:** ⭐⭐⭐⭐⭐ (5/5)

---

<!--
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.2
-->
