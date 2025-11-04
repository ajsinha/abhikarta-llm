<!--
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.2
-->

# Abhikarta LLM - Complete User Guide

**Comprehensive tutorials and how-to guides for all features**

Version: 3.1.2

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Provider Configuration](#provider-configuration)
3. [Basic Operations](#basic-operations)
4. [Advanced Features](#advanced-features)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Installation

#### Prerequisites
```bash
# Python 3.8+ required
python --version

# Core dependencies
pip install pydantic numpy urllib3
```

#### Install Abhikarta LLM
```bash
# Extract package
tar -xzf abhikarta-llm-v3.1.2-COMPLETE.tar.gz
cd abhikarta-llm

# Install in editable mode
pip install -e .

# Verify installation
python verify_installation.py
```

### Your First Program

```python
from llm.abstraction.facade import UnifiedLLMFacade

# Configure with mock provider (no API key needed)
config = {
    'providers': {
        'mock': {
            'enabled': True,
            'model': 'mock-model'
        }
    }
}

# Create facade
facade = UnifiedLLMFacade(config)

# Make your first request
response = facade.complete("What is artificial intelligence?")

# Print response
print(response.text)
print(f"Model used: {response.metadata['model']}")
```

---

## Provider Configuration

### 1. Ollama (Local & Free)

```python
# Install Ollama first
# curl https://ollama.ai/install.sh | sh
# ollama pull llama2

config = {
    'providers': {
        'ollama': {
            'enabled': True,
            'base_url': 'http://localhost:11434',  # Default
            'model': 'llama2'  # or mistral, codellama, phi
        }
    }
}

facade = UnifiedLLMFacade(config)
response = facade.complete("Explain Python")
# Cost: $0, Privacy: 100%
```

**When to use**: Development, testing, privacy-critical apps

### 2. Groq (Ultra-Fast)

```python
# pip install groq
# export GROQ_API_KEY="your-key"

config = {
    'providers': {
        'groq': {
            'enabled': True,
            'api_key': os.getenv('GROQ_API_KEY'),
            'model': 'mixtral-8x7b-32768'
        }
    }
}

# Real-time streaming at 500+ tokens/second!
for chunk in facade.stream_complete("Write a story"):
    print(chunk.text, end='', flush=True)
```

**When to use**: Real-time chat, streaming, interactive apps

### 3. Mistral (GDPR Compliant)

```python
# pip install mistralai
# export MISTRAL_API_KEY="your-key"

config = {
    'providers': {
        'mistral': {
            'enabled': True,
            'api_key': os.getenv('MISTRAL_API_KEY'),
            'model': 'mistral-small'  # or tiny, medium, large
        }
    }
}

# GDPR-compliant processing
response = facade.complete("Analyze customer data", provider='mistral')
```

**When to use**: European apps, GDPR requirements

### 4. Together AI (50+ Models)

```python
# pip install together
# export TOGETHER_API_KEY="your-key"

config = {
    'providers': {
        'together': {
            'enabled': True,
            'api_key': os.getenv('TOGETHER_API_KEY'),
            'model': 'meta-llama/Llama-2-70b-chat-hf'
        }
    }
}

# Try different models
models = [
    'meta-llama/Llama-2-70b-chat-hf',
    'mistralai/Mixtral-8x7B-Instruct-v0.1'
]

for model in models:
    response = facade.complete("Hello", model=model)
    print(f"{model}: {response.text}")
```

**When to use**: Model experimentation, open source projects

### 5. Multi-Provider Setup

```python
# Configure all providers at once
config = {
    'providers': {
        # Local/Free
        'ollama': {
            'enabled': True,
            'model': 'llama2'
        },
        # Ultra-fast
        'groq': {
            'enabled': True,
            'api_key': os.getenv('GROQ_API_KEY'),
            'model': 'mixtral-8x7b-32768'
        },
        # GDPR
        'mistral': {
            'enabled': True,
            'api_key': os.getenv('MISTRAL_API_KEY'),
            'model': 'mistral-small'
        },
        # Standard
        'openai': {
            'enabled': True,
            'api_key': os.getenv('OPENAI_API_KEY'),
            'model': 'gpt-3.5-turbo'
        }
    }
}

# Use different providers for different tasks
facade = UnifiedLLMFacade(config)

# Development with free local
dev_response = facade.complete("test", provider='ollama')

# Real-time with ultra-fast
fast_response = facade.complete("urgent query", provider='groq')

# EU data with GDPR
eu_response = facade.complete("customer data", provider='mistral')

# Production with reliable
prod_response = facade.complete("important task", provider='openai')
```

---

## Basic Operations

### 1. Simple Completion

```python
response = facade.complete(
    prompt="Explain quantum computing",
    temperature=0.7,      # Creativity (0.0-1.0)
    max_tokens=500,       # Response length
    top_p=0.9            # Nucleus sampling
)

print(response.text)
print(response.metadata)  # Model, usage, etc.
```

### 2. Streaming Responses

```python
# Token-by-token streaming
for chunk in facade.stream_complete("Write a long article"):
    print(chunk.text, end='', flush=True)
    
    # Check if final
    if chunk.is_final:
        print("\n\nStreaming complete!")
```

### 3. With History

```python
from llm.abstraction.conversation import ChatClient

chat = ChatClient(facade, max_history=50)

# Turn 1
response1 = chat.chat("My name is Alice")

# Turn 2 - remembers name!
response2 = chat.chat("What's my name?")
print(response2)  # "Your name is Alice"
```

### 4. Error Handling

```python
try:
    response = facade.complete("prompt")
    print(response.text)
    
except ValueError as e:
    print(f"Configuration error: {e}")
    
except ConnectionError as e:
    print(f"Network error: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Advanced Features

### 1. Function Calling (AI Agents)

```python
from llm.abstraction.tools import Tool, ToolRegistry

# Define tools
def get_weather(location: str) -> str:
    """Get weather for a location"""
    return f"Weather in {location}: Sunny, 72°F"

def search_web(query: str) -> str:
    """Search the web"""
    return f"Search results for: {query}"

# Register tools
registry = ToolRegistry()
registry.register(Tool(
    name="get_weather",
    description="Get current weather",
    function=get_weather
))
registry.register(Tool(
    name="search_web",
    description="Search the internet",
    function=search_web
))

# Execute tools
result = registry.execute("get_weather", location="New York")
print(result)  # "Weather in New York: Sunny, 72°F"
```

### 2. RAG (Knowledge Base Q&A)

```python
from llm.abstraction.rag import RAGClient, build_knowledge_base
from llm.abstraction.embeddings import EmbeddingClient

# Prepare knowledge base
documents = [
    "Python is a high-level programming language.",
    "Machine learning is a subset of AI.",
    "Neural networks are inspired by the brain."
]

# Build vector store
embedding_client = EmbeddingClient(provider='openai')
vector_store = build_knowledge_base(documents, embedding_client)

# Create RAG client
rag = RAGClient(facade, vector_store, top_k=2)

# Query with context
response = rag.query("What is Python?")
print(response.answer)
print(f"Sources: {response.sources}")
```

### 3. Prompt Templates

```python
from llm.abstraction.prompts import PromptTemplate, PromptRegistry

# Create template
template = PromptTemplate(
    name="summarize",
    template="Summarize the following in {num} sentences:\n\n{text}",
    description="Text summarization"
)

# Register template
registry = PromptRegistry()
registry.register(template)

# Use template
prompt = registry.render(
    'summarize',
    num=3,
    text="Long article text here..."
)

response = facade.complete(prompt)
```

### 4. Response Validation

```python
from llm.abstraction.validation import ResponseValidator
from pydantic import BaseModel
from typing import List

# Define schema
class Product(BaseModel):
    name: str
    price: float
    categories: List[str]

# Create validator
validator = ResponseValidator()

# Generate and validate
prompt = "Extract product info: Apple iPhone 15, $999, in Electronics and Phones"
response = facade.complete(prompt)

try:
    product = validator.validate(response.text, Product)
    print(f"Valid! {product.name} - ${product.price}")
except Exception as e:
    print(f"Validation failed: {e}")
```

### 5. Batch Processing

```python
from llm.abstraction.batch import BatchProcessor

# Create processor
processor = BatchProcessor(
    facade,
    batch_size=10,        # Process 10 at a time
    max_concurrent=5      # 5 concurrent requests
)

# Prepare prompts
prompts = [f"Explain {topic}" for topic in [
    "AI", "ML", "DL", "NLP", "CV",
    # ... 1000s more
]]

# Process in parallel
result = processor.process_batch_sync(prompts)

print(f"Processed: {result.successful}/{result.total}")
print(f"Time: {result.duration_seconds:.1f}s")
print(f"Throughput: {result.successful/result.duration_seconds:.1f} req/s")
# Typically 10-15x faster than sequential!
```

### 6. Semantic Caching

```python
from llm.abstraction.advanced import SemanticCache
from llm.abstraction.embeddings import EmbeddingClient

# Create cache
embedding_client = EmbeddingClient(provider='openai')
cache = SemanticCache(
    embedding_client,
    similarity_threshold=0.90,  # 90% similar = cache hit
    max_size=1000               # Store 1000 entries
)

# Cache response
prompt1 = "What is AI?"
response1 = facade.complete(prompt1)
cache.set(prompt1, response1.text)

# Similar query hits cache!
prompt2 = "Tell me about AI"  # Similar to prompt1
cached = cache.get(prompt2)

if cached:
    print("Cache HIT! Instant response")
    print(cached)
    # 50-200x faster!
else:
    # Cache miss, make API call
    response = facade.complete(prompt2)
```

### 7. Security Features

```python
from llm.abstraction.security import PIIDetector, ContentFilter

# PII Detection
detector = PIIDetector()
text = "Contact John Doe at john@example.com or 555-1234"
safe_text = detector.redact(text)
print(safe_text)  # "Contact [NAME] at [EMAIL] or [PHONE]"

# Content Filtering
filter = ContentFilter(strictness='medium')
text = "Some user input..."
is_safe, categories = filter.check(text)

if is_safe:
    response = facade.complete(text)
else:
    print(f"Content blocked: {categories}")
```

---

## Best Practices

### 1. Provider Selection

```python
# Use the right provider for each task

config = {
    'providers': {
        'ollama': {'enabled': True},     # Development
        'groq': {'enabled': True},       # Real-time
        'mistral': {'enabled': True},    # GDPR/EU
        'openai': {'enabled': True}      # Production
    }
}

# Development/Testing
if environment == 'development':
    provider = 'ollama'  # Free, private
    
# Real-time/Streaming
elif use_case == 'chat':
    provider = 'groq'  # Ultra-fast
    
# GDPR/European
elif region == 'EU':
    provider = 'mistral'  # Compliant
    
# Production
else:
    provider = 'openai'  # Reliable
```

### 2. Error Handling & Retry

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def robust_complete(prompt):
    """Complete with automatic retry"""
    try:
        return facade.complete(prompt)
    except Exception as e:
        print(f"Attempt failed: {e}")
        raise

# Usage
response = robust_complete("important prompt")
```

### 3. Cost Optimization

```python
# Strategy 1: Use cheaper providers
cheap_providers = ['ollama', 'mistral-tiny', 'groq']

# Strategy 2: Cache aggressively
cache = SemanticCache(embedding_client, similarity_threshold=0.85)

# Strategy 3: Batch processing
processor = BatchProcessor(facade, batch_size=20)

# Strategy 4: Use appropriate models
config = {
    'providers': {
        # Simple tasks
        'mistral': {'model': 'mistral-tiny'},  # $0.14/1M
        # Complex tasks
        'openai': {'model': 'gpt-4'}           # $30/1M
    }
}

# Route by complexity
if is_simple(prompt):
    response = facade.complete(prompt, provider='mistral')
else:
    response = facade.complete(prompt, provider='openai')
```

### 4. Performance Monitoring

```python
import time

start_time = time.time()
response = facade.complete(prompt)
duration = time.time() - start_time

# Log metrics
print(f"Duration: {duration:.2f}s")
print(f"Tokens: {response.metadata['usage']}")
print(f"Model: {response.metadata['model']}")

# Track costs
tokens_used = response.metadata['usage']['total_tokens']
cost_per_token = 0.000001  # Example rate
cost = tokens_used * cost_per_token
print(f"Cost: ${cost:.4f}")
```

### 5. Async Operations

```python
import asyncio

async def async_complete(prompt):
    """Async completion for better concurrency"""
    return await facade.acomplete(prompt)

async def process_many():
    """Process multiple prompts concurrently"""
    prompts = ["prompt1", "prompt2", "prompt3"]
    
    tasks = [async_complete(p) for p in prompts]
    responses = await asyncio.gather(*tasks)
    
    return responses

# Run
responses = asyncio.run(process_many())
```

---

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Problem: ModuleNotFoundError
# Solution: Install package
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/abhikarta-llm"
```

#### 2. API Key Errors
```bash
# Problem: Invalid API key
# Solution: Set environment variable
export OPENAI_API_KEY="your-key-here"
export GROQ_API_KEY="your-key-here"
export MISTRAL_API_KEY="your-key-here"

# Or use .env file
pip install python-dotenv
```

#### 3. Ollama Connection
```bash
# Problem: Cannot connect to Ollama
# Solution: Start Ollama service
ollama serve

# Check if running
curl http://localhost:11434/api/tags
```

#### 4. Rate Limit Errors
```python
# Problem: Rate limit exceeded
# Solution: Use rate limiter
from llm.abstraction.batch import RateLimitedBatchProcessor

processor = RateLimitedBatchProcessor(
    facade,
    requests_per_minute=60  # Limit to 60/min
)
```

#### 5. Out of Memory
```python
# Problem: Large batch processing fails
# Solution: Reduce batch size
processor = BatchProcessor(
    facade,
    batch_size=5,          # Smaller batches
    max_concurrent=2       # Fewer concurrent
)
```

### Getting Help

1. **Check Documentation**
   - README.md - Overview
   - ARCHITECTURE.md - Design
   - CAPABILITIES.md - Features
   - USE_CASES.md - Examples

2. **Run Examples**
   ```bash
   cd examples/capabilities
   python 01_basic_usage.py
   ```

3. **Verify Installation**
   ```bash
   python verify_installation.py
   ```

4. **Contact Support**
   - Email: ajsinha@gmail.com
   - GitHub: github.com/ajsinha/abhikarta

---

**© 2025-2030 Ashutosh Sinha | ajsinha@gmail.com**

---

**Copyright 2025-2030 all rights reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**  
**Version: 3.1.2**
