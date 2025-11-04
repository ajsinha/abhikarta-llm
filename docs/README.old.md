<!--
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.4
-->

# Abhikarta LLM - Universal LLM Abstraction Framework

**The most comprehensive, production-ready LLM abstraction layer for Python**

[![Version](https://img.shields.io/badge/version-3.1.4-blue.svg)](https://github.com/ajsinha/abhikarta)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Providers](https://img.shields.io/badge/providers-11-orange.svg)](#providers)
[![Features](https://img.shields.io/badge/features-36%2B-red.svg)](#features)

> **Abhikarta** (अभिकर्ता) - Sanskrit for "agent" or "actor"

**One API to rule them all. Switch between 11 LLM providers without changing code.**

---

## 🌟 Why Abhikarta LLM?

### The Problem
- 😫 Every provider has different APIs
- 💸 Vendor lock-in costs thousands/year
- 🐌 Can't optimize for speed or cost
- 🔒 Privacy and compliance concerns

### The Solution
```python
facade = UnifiedLLMFacade(config)
response = facade.complete("Hello!")

# Switch providers: Change ONE line in config
# OpenAI → Groq (25x faster!)
# GPT-4 → Ollama (100% free!)
```

**Zero code changes. Maximum flexibility.**

---

## ⚡ Quick Start

```bash
# Install
pip install -e .

# Use it
from llm.abstraction.facade import UnifiedLLMFacade

config = {'providers': {'ollama': {'enabled': True}}}
facade = UnifiedLLMFacade(config)
response = facade.complete("What is AI?")
```

---

## 🎯 11 Providers

| Provider | Speed | Cost | Feature |
|----------|-------|------|---------|
| Ollama 🆕 | Medium | FREE | Local/Private |
| Groq 🆕 | ⚡ 500+/s | $$ | Ultra-fast |
| Mistral 🆕 | Fast | $$ | GDPR |
| Together 🆕 | Fast | $$ | 50+ models |
| OpenAI | Medium | $$$$ | Standard |
| Anthropic | Medium | $$$ | Safety |
| Cohere | Fast | $$ | Multilingual |
| Google | Medium | $$$ | Multimodal |
| + 3 more |

---

## 💎 36+ Features

- ⚡ Function Calling
- 📚 RAG System  
- 🎨 Prompt Templates
- ✅ Response Validation
- 🔄 Batch Processing
- 💬 Conversation Management
- 🔍 Embeddings
- 💾 Semantic Caching
- 🌊 Real-time Streaming
- 🔒 Security Suite

[See all →](CAPABILITIES.md)

---

## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design
- **[CAPABILITIES.md](CAPABILITIES.md)** - All features
- **[USER_GUIDE.md](USER_GUIDE.md)** - How-to guides
- **[USE_CASES.md](USE_CASES.md)** - Real examples
- **[WHY_ABHIKARTA.md](WHY_ABHIKARTA.md)** - Why choose us

---

## 🚀 Examples

13 comprehensive examples in `examples/capabilities/`

```bash
python examples/capabilities/01_basic_usage.py
python examples/capabilities/13_new_providers.py
```

---

## 💰 Cost Savings

```
GPT-4:     $900/mo → Ollama: $0/mo     (100% savings!)
Anthropic: $540/mo → Groq:   $16/mo    (97% savings!)
```

---

## 📞 Support

- **Email**: ajsinha@gmail.com
- **GitHub**: github.com/ajsinha/abhikarta
- **Version**: 2.4.0

---

**Made with ❤️  by Ashutosh Sinha**

**One API, Infinite Possibilities**

---

**Copyright 2025-2030 all rights reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**  
**Version: 3.1.4**
