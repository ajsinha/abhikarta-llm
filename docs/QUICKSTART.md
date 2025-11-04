<!--
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.3
-->

# Abhikarta LLM v2.3.0 - Quick Start Guide

**Get up and running in 5 minutes!** 🚀

---

## 📦 Installation (1 minute)

```bash
# Extract the package
tar -xzf abhikarta-llm-v2.3.0-complete.tar.gz
cd abhikarta-llm

# Install dependencies
pip install pydantic numpy urllib3

# Install package
pip install -e .
```

---

## 🔑 Configuration (1 minute)

```bash
# Set your API key
export OPENAI_API_KEY="your-openai-api-key-here"

# Or for other providers
export ANTHROPIC_API_KEY="your-anthropic-key"
export COHERE_API_KEY="your-cohere-key"
```

---

## ✨ Basic Usage (1 minute)

```python
from llm.abstraction.facade import UnifiedLLMFacade

# Initialize
config = {
    'providers': {
        'openai': {
            'enabled': True,
            'api_key': 'your-key',
            'model': 'gpt-3.5-turbo'
        }
    }
}

facade = UnifiedLLMFacade(config)

# Make a request
response = facade.complete("Hello, world!")
print(response.text)
```

---

## 🎯 Try New Features (2 minutes)

### 1. Function Calling
```python
from llm.abstraction.tools import Tool, ToolRegistry

def get_weather(location: str) -> str:
    return f"Weather in {location}: Sunny, 72°F"

registry = ToolRegistry()
registry.register(Tool(
    name="get_weather",
    description="Get weather",
    function=get_weather
))

result = registry.execute("get_weather", location="San Francisco")
print(result)
```

### 2. RAG (Knowledge Base Q&A)
```python
from llm.abstraction.rag import RAGClient, build_knowledge_base
from llm.abstraction.embeddings import EmbeddingClient

# Build knowledge base
docs = ["Python is a language", "AI is machine learning"]
embedding_client = EmbeddingClient(provider='openai')
vector_store = build_knowledge_base(docs, embedding_client)

# Ask questions
rag = RAGClient(facade, vector_store)
response = rag.query("What is Python?")
print(response.answer)
```

### 3. Batch Processing
```python
from llm.abstraction.batch import BatchProcessor

processor = BatchProcessor(facade, batch_size=10)
prompts = ["Summarize AI", "Explain ML", "Define DL"]

result = processor.process_batch_sync(prompts)
print(f"Processed {result.successful}/{result.total}")
```

### 4. Conversation
```python
from llm.abstraction.conversation import ChatClient

chat = ChatClient(facade, max_history=50)

response1 = chat.chat("My name is Alice")
response2 = chat.chat("What's my name?")  # Remembers!
print(response2)
```

---

## 📚 Next Steps

1. **Read the docs**: `FEATURES_v2.3.0.md`
2. **Try examples**: `python examples/new_features_examples.py`
3. **Explore features**: Check out each module in `llm/abstraction/`
4. **Build something**: Start with your use case!

---

## 🆘 Quick Help

**Import Error?**
```bash
pip install -e .
```

**API Key Error?**
```bash
export OPENAI_API_KEY="your-key"
```

**Need Examples?**
```bash
python examples/new_features_examples.py
```

---

## 🎉 You're Ready!

Start building amazing AI applications with Abhikarta LLM v2.3.0!

**Full Documentation**: See `README_v2.3.0.md` and `FEATURES_v2.3.0.md`

---

**© 2025 Ashutosh Sinha | ajsinha@gmail.com**

---

**Copyright 2025-2030 all rights reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**  
**Version: 3.1.3**
