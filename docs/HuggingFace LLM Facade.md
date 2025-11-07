# HuggingFace LLM Facade - Complete Documentation

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

---

## Legal Notice

This document and the associated software implementation are proprietary and confidential. Unauthorized copying, distribution, modification, or use of this document or the software it describes is strictly prohibited without explicit written permission from the copyright holder.

This document is provided "as is" without warranty of any kind, either expressed or implied. The copyright holder shall not be liable for any damages arising from the use of this document or the software system it describes.

**Patent Pending**: Certain architectural patterns and implementations described in this document may be subject to patent applications.

---

## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Architecture](#architecture)
4. [Installation](#installation)
5. [Quick Start](#quick-start)
6. [Detailed Usage](#detailed-usage)
7. [Capability Reference](#capability-reference)
8. [Configuration Options](#configuration-options)
9. [Model Recommendations](#model-recommendations)
10. [API Reference](#api-reference)
11. [Best Practices](#best-practices)
12. [Performance Optimization](#performance-optimization)
13. [Limitations and Known Issues](#limitations-and-known-issues)
14. [Troubleshooting](#troubleshooting)
15. [Examples](#examples)

---

## Overview

The **HuggingFace LLM Facade** is a concrete implementation of the LLMFacade interface designed specifically for HuggingFace models. It provides a unified, provider-agnostic interface for interacting with thousands of models available on the HuggingFace Hub.

### What Makes It Unique

- **Dual Mode Operation**: Supports both API-based inference and local model execution
- **Automatic Capability Detection**: Intelligently detects model capabilities based on architecture
- **Model Flexibility**: Works with chat models, code models, embedding models, and more
- **Cost Effective**: Most HuggingFace models are free to use
- **Open Source Friendly**: Full support for open-source models

### Use Cases

- **Prototyping**: Quickly test different models without changing code
- **Cost Optimization**: Use free open-source models for development
- **Privacy**: Run models locally for sensitive data
- **Model Comparison**: Easily compare different models' performance
- **Research**: Experiment with cutting-edge open-source models

---

## Key Features

### ✅ Supported Capabilities

| Capability | Support Level | Notes |
|------------|--------------|-------|
| **Text Generation** | ✅ Full | All models |
| **Chat Completion** | ✅ Full | Chat-tuned models |
| **Streaming** | ✅ Full | API and local |
| **Embeddings** | ✅ Full | Embedding models |
| **Code Generation** | ✅ Full | Code models |
| **Async Operations** | ✅ Full | Via executor |
| **Batch Processing** | ✅ Full | Efficient batching |
| **Token Management** | ✅ Full | Count, truncate, estimate |
| **RAG Support** | ✅ Full | With vector store |
| **Tool Calling** | ⚠️ Limited | Not natively supported by most models |
| **Structured Output** | ⚠️ Limited | Depends on model |
| **Vision** | ❌ Not Supported | Few models support this |
| **Audio** | ❌ Not Supported | Use specialized facades |
| **Image Generation** | ❌ Not Supported | Use Stable Diffusion facade |

### 🎯 Key Advantages

1. **No API Costs**: Most models are free to use
2. **Local Execution**: Run models on your hardware
3. **Privacy**: Keep data on-premise
4. **Model Variety**: Access to 100,000+ models
5. **Active Community**: Rapid model updates
6. **Quantization Support**: Efficient inference with 4-bit/8-bit models

---

## Architecture

### High-Level Design

```
┌─────────────────────────────────────┐
│   HuggingFaceLLMFacade              │
│   (Implements LLMFacade)            │
└──────────────┬──────────────────────┘
               │
               ├── API Mode
               │   ├── InferenceClient
               │   └── HTTP Requests
               │
               └── Local Mode
                   ├── AutoTokenizer
                   ├── AutoModelForCausalLM
                   └── Local Inference
```

### Component Flow

```
Client Request
     │
     ▼
Capability Check
     │
     ▼
Parameter Building
     │
     ├─────── API Mode ─────┐
     │                      │
     ▼                      ▼
Local Model          InferenceClient
     │                      │
     ▼                      ▼
Tokenize/Generate    HTTP Request
     │                      │
     └──────────┬───────────┘
                ▼
         Normalize Response
                ▼
           Return Result
```

### Capability Detection Logic

```python
def _detect_capabilities():
    capabilities = [TEXT_GENERATION, STREAMING]
    
    if is_chat_model(model_name):
        capabilities.append(CHAT_COMPLETION)
    
    if is_embedding_model(model_name):
        capabilities.append(EMBEDDINGS)
    
    if is_code_model(model_name):
        capabilities.extend([CODE_GENERATION, CHAT_COMPLETION])
    
    return capabilities
```

---

## Installation

### Basic Installation

```bash
# Core installation
pip install huggingface_hub

# For local model execution
pip install transformers torch

# Optional: For quantization
pip install bitsandbytes accelerate

# Optional: For progress bars
pip install tqdm
```

### Full Installation

```bash
# Install all dependencies
pip install huggingface_hub transformers torch bitsandbytes accelerate tqdm

# For GPU support (CUDA)
pip install torch --index-url https://download.pytorch.org/whl/cu118

# For Apple Silicon (MPS)
pip install torch torchvision
```

### System Requirements

**API Mode:**
- Python 3.8+
- Internet connection
- HuggingFace account (free)

**Local Mode:**
- Python 3.8+
- 8GB+ RAM (16GB+ recommended)
- GPU recommended (CUDA or Apple Silicon)
- 10-50GB disk space per model

---

## Quick Start

### 1. Setup

```python
import os
os.environ["HF_TOKEN"] = "your_huggingface_token"

from huggingface_facade import HuggingFaceLLMFacade, create_huggingface_llm
from llm_facade import GenerationConfig
```

### 2. API Mode (Recommended for Testing)

```python
# Initialize with API
llm = HuggingFaceLLMFacade(
    model_name="meta-llama/Llama-2-7b-chat-hf",
    use_local=False  # Use API
)

# Simple generation
response = llm.text_generation(
    "The future of AI is",
    config=GenerationConfig(max_tokens=50, temperature=0.7)
)
print(response)
```

### 3. Local Mode (For Privacy/Cost)

```python
# Initialize with local model
llm = HuggingFaceLLMFacade(
    model_name="gpt2",  # Small model for testing
    use_local=True,
    device="auto"  # Automatic device selection
)

# Generate text
response = llm.text_generation("Once upon a time")
print(response)
```

### 4. Chat Completion

```python
# Use a chat model
llm = create_huggingface_llm("meta-llama/Llama-2-7b-chat-hf")

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is machine learning?"}
]

response = llm.chat_completion(messages)
print(response["content"])
```

---

## Detailed Usage

### Text Generation

```python
llm = HuggingFaceLLMFacade("gpt2")

# Basic generation
text = llm.text_generation("The weather today is")

# With configuration
config = GenerationConfig(
    max_tokens=100,
    temperature=0.8,
    top_p=0.95,
    top_k=50,
    repetition_penalty=1.2
)

text = llm.text_generation("Once upon a time", config=config)

# Streaming
for chunk in llm.stream_text_generation("Tell me a story"):
    print(chunk, end="", flush=True)
```

### Chat Completion

```python
llm = HuggingFaceLLMFacade("meta-llama/Llama-2-7b-chat-hf")

# Simple chat
messages = [
    {"role": "user", "content": "Hello!"}
]

response = llm.chat_completion(messages)
print(response["content"])

# Multi-turn conversation
messages = [
    {"role": "system", "content": "You are a math tutor."},
    {"role": "user", "content": "What is calculus?"},
    {"role": "assistant", "content": "Calculus is..."},
    {"role": "user", "content": "Can you give an example?"}
]

response = llm.chat_completion(messages)

# Streaming chat
for delta in llm.stream_chat_completion(messages):
    if "content" in delta.get("delta", {}):
        print(delta["delta"]["content"], end="")
```

### Embeddings

```python
# Use an embedding model
llm = HuggingFaceLLMFacade(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# Single text
embedding = llm.embed_text("Machine learning is fascinating")
print(f"Embedding dimension: {len(embedding)}")

# Multiple texts
texts = [
    "The cat sat on the mat",
    "Dogs are loyal animals",
    "Python is a programming language"
]

embeddings = llm.embed_text(texts, normalize=True)

# Compute similarity
similarity = llm.compute_similarity(embeddings[0], embeddings[1])
print(f"Similarity: {similarity:.4f}")

# Batch processing
large_texts = ["text " + str(i) for i in range(100)]
embeddings = llm.batch_embed(large_texts, batch_size=32, show_progress=True)
```

### Code Generation

```python
llm = HuggingFaceLLMFacade("codellama/CodeLlama-7b-hf")

# Generate code
result = llm.code_generation(
    "A function to calculate fibonacci numbers",
    language="python",
    include_docs=True
)

print(result["code"])

# Explain code
code = """
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
"""

explanation = llm.code_explanation(code, language="python")
print(explanation)

# Code review
review = llm.code_review(
    code,
    language="python",
    focus_areas=["performance", "style"]
)
print(review["summary"])
```

### RAG (Retrieval Augmented Generation)

```python
# Assuming you have a vector store setup
from vector_store_base import VectorStoreBase

llm = HuggingFaceLLMFacade("meta-llama/Llama-2-7b-chat-hf")
vector_store = MyVectorStore()  # Your vector store implementation

# RAG chat
response = llm.rag_chat(
    messages=[
        {"role": "user", "content": "What are our Q4 sales figures?"}
    ],
    retrieval_top_k=5,
    include_sources=True,
    vector_store=vector_store
)

print(response["content"])
print("Sources:", response["sources"])

# RAG generation
answer = llm.rag_generate(
    "Explain our product roadmap",
    system_prompt="You are a product manager.",
    retrieval_top_k=3,
    vector_store=vector_store
)
```

### Batch Processing

```python
llm = HuggingFaceLLMFacade("gpt2")

# Batch text generation
prompts = [
    "The future of AI",
    "Climate change solutions",
    "Space exploration benefits"
]

config = GenerationConfig(max_tokens=50, temperature=0.7)
results = llm.batch_generate(prompts, config=config, show_progress=True)

for prompt, result in zip(prompts, results):
    print(f"\nPrompt: {prompt}")
    print(f"Result: {result}")

# Batch embeddings
texts = ["text " + str(i) for i in range(100)]
embeddings = llm.batch_embed(texts, batch_size=16)
```

### Async Operations

```python
import asyncio

llm = HuggingFaceLLMFacade("gpt2")

async def async_generation():
    # Single async call
    result = await llm.atext_generation("Hello world")
    print(result)
    
    # Concurrent calls
    tasks = [
        llm.atext_generation("Prompt 1"),
        llm.atext_generation("Prompt 2"),
        llm.atext_generation("Prompt 3")
    ]
    
    results = await asyncio.gather(*tasks)
    return results

# Run async
results = asyncio.run(async_generation())
```

### Token Management

```python
llm = HuggingFaceLLMFacade("meta-llama/Llama-2-7b-chat-hf")

# Count tokens
text = "The quick brown fox jumps over the lazy dog"
token_count = llm.count_tokens(text)
print(f"Tokens: {token_count}")

# Count tokens in messages
messages = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"}
]
message_tokens = llm.count_tokens(messages)

# Truncate text
long_text = "word " * 1000
max_tokens = 100
truncated = llm.truncate_to_max_tokens(long_text, max_tokens)

# Get context window
context_window = llm.get_context_window()
max_output = llm.get_max_output_tokens()

print(f"Context: {context_window}, Max output: {max_output}")

# Estimate cost (free for most HF models)
cost = llm.estimate_cost(1000, 500)
print(f"Cost: ${cost['total_cost']}")  # Usually $0.00
```

---

## Capability Reference

### Capability Detection

The facade automatically detects capabilities based on model name patterns:

```python
llm = HuggingFaceLLMFacade("meta-llama/Llama-2-7b-chat-hf")

# Get all capabilities
capabilities = llm.get_capabilities()
print([cap.value for cap in capabilities])
# Output: ['text_generation', 'chat_completion', 'streaming', 'reasoning']

# Check specific capability
if llm.supports_capability(ModelCapability.CHAT_COMPLETION):
    response = llm.chat_completion(messages)
```

### Model Type Detection

| Model Pattern | Detected Capabilities |
|--------------|----------------------|
| `llama-*-chat` | Chat, Text, Streaming, Reasoning |
| `codellama`, `starcoder` | Code, Chat, Text, Streaming |
| `sentence-transformers` | Embeddings, Text |
| `mistral-*-instruct` | Chat, Text, Streaming, Reasoning |
| `gpt2`, `gpt-neo` | Text, Streaming |

### Capability Matrix

| Capability | Models | Usage |
|-----------|--------|-------|
| **TEXT_GENERATION** | All models | `text_generation()` |
| **CHAT_COMPLETION** | Chat models | `chat_completion()` |
| **EMBEDDINGS** | Embedding models | `embed_text()` |
| **CODE_GENERATION** | Code models | `code_generation()` |
| **STREAMING** | All models | `stream=True` parameter |
| **REASONING** | Advanced models | All methods |

---

## Configuration Options

### Initialization Parameters

```python
llm = HuggingFaceLLMFacade(
    model_name="meta-llama/Llama-2-7b-chat-hf",  # Required
    api_key=None,                    # HF token (from env if None)
    base_url=None,                   # Custom inference endpoint
    timeout=120.0,                   # Request timeout
    max_retries=3,                   # Retry attempts
    use_local=False,                 # Use local model
    device="auto",                   # "cpu", "cuda", "mps", "auto"
    
    # Local mode options
    trust_remote_code=False,         # Allow remote code
    load_in_8bit=False,             # 8-bit quantization
    load_in_4bit=False,             # 4-bit quantization
    torch_dtype=torch.float16       # Model dtype
)
```

### Generation Configuration

```python
from llm_facade import GenerationConfig

config = GenerationConfig(
    max_tokens=100,                  # Max output tokens
    temperature=0.7,                 # Randomness (0.0-2.0)
    top_p=0.9,                      # Nucleus sampling
    top_k=50,                       # Top-K sampling
    repetition_penalty=1.1,         # Penalize repetition
    stop_sequences=["END"]          # Stop generation
)

response = llm.text_generation(prompt, config=config)
```

### Environment Variables

```bash
# API token
export HF_TOKEN="your_token_here"
# or
export HUGGINGFACE_TOKEN="your_token_here"

# Cache directory (for local models)
export HF_HOME="/path/to/cache"
export TRANSFORMERS_CACHE="/path/to/cache"
```

---

## Model Recommendations

### Best Models by Use Case

#### Chat & Conversation

| Model | Size | Speed | Quality | Notes |
|-------|------|-------|---------|-------|
| `meta-llama/Llama-2-7b-chat-hf` | 7B | Fast | Good | Best all-around |
| `meta-llama/Llama-2-13b-chat-hf` | 13B | Medium | Better | Higher quality |
| `mistralai/Mistral-7B-Instruct-v0.2` | 7B | Fast | Excellent | Recommended |
| `mistralai/Mixtral-8x7B-Instruct-v0.1` | 47B | Slow | Best | Production quality |

#### Code Generation

| Model | Specialization | Recommended |
|-------|---------------|-------------|
| `codellama/CodeLlama-7b-hf` | General code | ✓ |
| `codellama/CodeLlama-13b-Python-hf` | Python | ✓✓ |
| `bigcode/starcoder` | Multi-language | ✓ |
| `WizardLM/WizardCoder-15B-V1.0` | Advanced | ✓✓✓ |

#### Embeddings

| Model | Dimension | Speed | Quality |
|-------|-----------|-------|---------|
| `sentence-transformers/all-MiniLM-L6-v2` | 384 | Very Fast | Good |
| `sentence-transformers/all-mpnet-base-v2` | 768 | Fast | Better |
| `BAAI/bge-base-en-v1.5` | 768 | Medium | Best |
| `intfloat/e5-large-v2` | 1024 | Slow | Excellent |

#### Small/Fast Models (Testing)

| Model | Size | Use Case |
|-------|------|----------|
| `gpt2` | 124M | Quick tests |
| `distilgpt2` | 82M | Very fast |
| `microsoft/phi-2` | 2.7B | Efficient |

---

## API Reference

### Core Methods

#### `text_generation()`
```python
def text_generation(
    self,
    prompt: str,
    *,
    config: Optional[GenerationConfig] = None,
    stream: bool = False,
    **kwargs
) -> Union[str, Iterator[str], Dict[str, Any]]
```

**Parameters:**
- `prompt`: Input text to complete
- `config`: Generation configuration
- `stream`: Enable streaming
- `**kwargs`: Additional parameters

**Returns:** Generated text, iterator, or full response dict

---

#### `chat_completion()`
```python
def chat_completion(
    self,
    messages: Messages,
    *,
    config: Optional[GenerationConfig] = None,
    stream: bool = False,
    **kwargs
) -> Union[Dict[str, Any], Iterator[Dict[str, Any]]]
```

**Parameters:**
- `messages`: List of message dictionaries
- `config`: Generation configuration
- `stream`: Enable streaming
- `**kwargs`: Additional parameters

**Returns:** Response dictionary or stream iterator

---

#### `embed_text()`
```python
def embed_text(
    self,
    texts: Union[str, List[str]],
    *,
    normalize: bool = True,
    **kwargs
) -> Union[Embedding, List[Embedding]]
```

**Parameters:**
- `texts`: String or list of strings
- `normalize`: L2-normalize vectors
- `**kwargs`: Additional parameters

**Returns:** Embedding vector(s)

---

### Utility Methods

#### `get_capabilities()`
Returns list of supported capabilities.

#### `supports_capability(capability)`
Check if specific capability is supported.

#### `count_tokens(text)`
Count tokens in text or messages.

#### `get_model_info()`
Get comprehensive model information.

#### `health_check()`
Verify service is accessible.

---

## Best Practices

### 1. Model Selection

```python
# ✓ GOOD: Start with small models for testing
llm = HuggingFaceLLMFacade("gpt2")  # Fast, good for testing

# ✓ GOOD: Use appropriate model size for task
llm = HuggingFaceLLMFacade("meta-llama/Llama-2-7b-chat-hf")  # Production

# ✗ BAD: Using huge models for simple tasks
llm = HuggingFaceLLMFacade("meta-llama/Llama-2-70b-chat-hf")  # Overkill
```

### 2. API vs Local

```python
# For development/testing: Use API
llm = HuggingFaceLLMFacade(model_name, use_local=False)

# For production/privacy: Use local
llm = HuggingFaceLLMFacade(model_name, use_local=True, load_in_4bit=True)
```

### 3. Memory Management

```python
# ✓ GOOD: Use quantization for large models
llm = HuggingFaceLLMFacade(
    "meta-llama/Llama-2-13b-chat-hf",
    use_local=True,
    load_in_4bit=True  # Reduces memory by 4x
)

# ✓ GOOD: Close when done
llm.close()

# ✓ GOOD: Use context manager
with HuggingFaceLLMFacade(model_name) as llm:
    response = llm.chat_completion(messages)
```

### 4. Error Handling

```python
# ✓ GOOD: Check capabilities first
if llm.supports_capability(ModelCapability.EMBEDDINGS):
    embeddings = llm.embed_text(texts)
else:
    print("Model doesn't support embeddings")

# ✓ GOOD: Handle exceptions
try:
    response = llm.chat_completion(messages)
except CapabilityNotSupportedException as e:
    print(f"Feature not supported: {e.capability}")
except Exception as e:
    print(f"Error: {e}")
```

### 5. Batch Processing

```python
# ✓ GOOD: Use batch methods
results = llm.batch_generate(prompts, show_progress=True)

# ✗ BAD: Sequential processing
results = [llm.text_generation(p) for p in prompts]  # Slower
```

### 6. Token Management

```python
# ✓ GOOD: Check token count before generation
tokens = llm.count_tokens(text)
if tokens > llm.get_context_window() * 0.9:
    text = llm.truncate_to_max_tokens(text, llm.get_context_window() * 0.8)
```

---

## Performance Optimization

### 1. Use Quantization

```python
# 4-bit quantization (best memory/performance tradeoff)
llm = HuggingFaceLLMFacade(
    model_name,
    use_local=True,
    load_in_4bit=True
)

# 8-bit quantization (better quality, more memory)
llm = HuggingFaceLLMFacade(
    model_name,
    use_local=True,
    load_in_8bit=True
)
```

### 2. Batch Operations

```python
# Process multiple requests at once
results = llm.batch_generate(
    prompts,
    config=config,
    show_progress=True
)
```

### 3. Streaming

```python
# Stream for better perceived performance
for chunk in llm.stream_text_generation(prompt):
    print(chunk, end="", flush=True)
```

### 4. Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_generation(prompt):
    return llm.text_generation(prompt)
```

### 5. GPU Acceleration

```python
# Use GPU if available
llm = HuggingFaceLLMFacade(
    model_name,
    use_local=True,
    device="cuda"  # or "mps" for Apple Silicon
)
```

---

## Limitations and Known Issues

### Current Limitations

1. **Tool Calling**: Most HuggingFace models don't natively support function calling
2. **Vision**: Very limited vision model support
3. **Audio**: No native audio support
4. **Structured Output**: JSON mode not guaranteed for all models
5. **Context Window**: Smaller than commercial models (typically 2K-8K tokens)

### Known Issues

| Issue | Workaround |
|-------|-----------|
| Slow first inference | Expected - model loading time |
| Out of memory errors | Use smaller model or quantization |
| API rate limits | Use local mode or wait between requests |
| Model not found | Verify model name and access permissions |
| Token mismatch warnings | Normal for some tokenizers |

### Model-Specific Issues

**Llama Models:**
- Require HuggingFace account approval
- Large model sizes (7B+)
- Slower inference

**GPT-2:**
- Limited capabilities
- Short context window (1024 tokens)
- Old model architecture

**Code Models:**
- May generate incomplete code
- Need careful prompting
- Best with specific instructions

---

## Troubleshooting

### Common Problems

#### 1. Model Not Found

**Error:** `404: Model not found`

**Solutions:**
```python
# Check model name spelling
llm = HuggingFaceLLMFacade("meta-llama/Llama-2-7b-chat-hf")  # Correct

# Verify you have access (for gated models)
# Visit: https://huggingface.co/meta-llama/Llama-2-7b-chat-hf

# Check API token is set
import os
print(os.getenv("HF_TOKEN"))
```

#### 2. Out of Memory

**Error:** `CUDA out of memory` or `RuntimeError: Out of memory`

**Solutions:**
```python
# Use quantization
llm = HuggingFaceLLMFacade(
    model_name,
    use_local=True,
    load_in_4bit=True  # 4x less memory
)

# Use smaller model
llm = HuggingFaceLLMFacade("gpt2")

# Use API mode instead
llm = HuggingFaceLLMFacade(model_name, use_local=False)
```

#### 3. Slow Generation

**Problem:** Generation takes too long

**Solutions:**
```python
# Use smaller model
llm = HuggingFaceLLMFacade("distilgpt2")

# Reduce max_tokens
config = GenerationConfig(max_tokens=50)  # Instead of 1000

# Use GPU
llm = HuggingFaceLLMFacade(model_name, use_local=True, device="cuda")

# Use API mode
llm = HuggingFaceLLMFacade(model_name, use_local=False)
```

#### 4. API Rate Limits

**Error:** `429: Too many requests`

**Solutions:**
```python
# Add delays between requests
import time
time.sleep(1)  # 1 second delay

# Use local mode
llm = HuggingFaceLLMFacade(model_name, use_local=True)

# Implement exponential backoff
from time import sleep
from llm_facade import RateLimitException

try:
    response = llm.chat_completion(messages)
except RateLimitException as e:
    sleep(e.retry_after or 60)
    response = llm.chat_completion(messages)
```

#### 5. Token Mismatch Warnings

**Warning:** `Token indices sequence length is longer than the specified maximum`

**Solutions:**
```python
# Truncate input
text = llm.truncate_to_max_tokens(text, max_tokens=1024)

# Or check before generation
if llm.count_tokens(text) > llm.get_context_window():
    text = text[:llm.get_context_window() * 4]  # Rough truncation
```

### Debug Mode

```python
# Enable logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check model info
info = llm.get_model_info()
print(json.dumps(info, indent=2))

# Test health
is_healthy = llm.health_check()
print(f"Healthy: {is_healthy}")

# Check capabilities
caps = llm.get_capabilities()
print(f"Capabilities: {[c.value for c in caps]}")
```

---

## Examples

### Example 1: Simple Chatbot

```python
from huggingface_facade import create_huggingface_llm
from llm_facade import GenerationConfig

# Initialize
llm = create_huggingface_llm("meta-llama/Llama-2-7b-chat-hf")

# Chat loop
messages = []
config = GenerationConfig(max_tokens=200, temperature=0.7)

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break
    
    messages.append({"role": "user", "content": user_input})
    response = llm.chat_completion(messages, config=config)
    
    assistant_reply = response["content"]
    messages.append({"role": "assistant", "content": assistant_reply})
    
    print(f"Bot: {assistant_reply}")
```

### Example 2: Document Q&A with RAG

```python
from huggingface_facade import HuggingFaceLLMFacade
from vector_store import MyVectorStore

# Initialize
llm = HuggingFaceLLMFacade("meta-llama/Llama-2-7b-chat-hf")
vector_store = MyVectorStore()

# Load documents into vector store
documents = [...]  # Your documents
vector_store.add_documents(documents)

# Ask questions
question = "What are the key features of our product?"
response = llm.rag_chat(
    messages=[{"role": "user", "content": question}],
    retrieval_top_k=5,
    include_sources=True,
    vector_store=vector_store
)

print(f"Answer: {response['content']}")
print(f"Sources: {response['sources']}")
```

### Example 3: Code Assistant

```python
from huggingface_facade import HuggingFaceLLMFacade

# Initialize with code model
llm = HuggingFaceLLMFacade("codellama/CodeLlama-7b-Python-hf")

# Generate code
result = llm.code_generation(
    "A function to validate email addresses using regex",
    language="python",
    include_tests=True,
    include_docs=True
)

print("Generated Code:")
print(result["code"])

# Explain existing code
sample_code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""

explanation = llm.code_explanation(sample_code, detail_level="detailed")
print("\nExplanation:")
print(explanation)
```

### Example 4: Semantic Search

```python
from huggingface_facade import HuggingFaceLLMFacade

# Initialize embedding model
llm = HuggingFaceLLMFacade("sentence-transformers/all-MiniLM-L6-v2")

# Your document collection
documents = [
    "Python is a high-level programming language",
    "Machine learning is a subset of artificial intelligence",
    "Dogs are loyal and friendly pets",
    "Cats are independent animals",
    "JavaScript is used for web development"
]

# Generate embeddings
doc_embeddings = llm.embed_text(documents, normalize=True)

# Query
query = "Tell me about programming languages"
query_embedding = llm.embed_text(query, normalize=True)

# Find most similar documents
similarities = [
    (doc, llm.compute_similarity(query_embedding, emb))
    for doc, emb in zip(documents, doc_embeddings)
]

# Sort by similarity
similarities.sort(key=lambda x: x[1], reverse=True)

print("Most relevant documents:")
for doc, score in similarities[:3]:
    print(f"{score:.3f}: {doc}")
```

### Example 5: Batch Translation

```python
from huggingface_facade import HuggingFaceLLMFacade
from llm_facade import GenerationConfig

llm = HuggingFaceLLMFacade("meta-llama/Llama-2-7b-chat-hf")

# Sentences to translate
sentences = [
    "Hello, how are you?",
    "The weather is beautiful today",
    "I love programming",
    "Thank you for your help"
]

# Create prompts
prompts = [f"Translate to Spanish: {s}" for s in sentences]

# Batch generate
config = GenerationConfig(max_tokens=50, temperature=0.3)
translations = llm.batch_generate(prompts, config=config, show_progress=True)

# Display results
for original, translation in zip(sentences, translations):
    print(f"EN: {original}")
    print(f"ES: {translation}\n")
```

---

## Version History

- **v1.0.0** (January 2025)
  - Initial release
  - Full LLMFacade implementation
  - Support for API and local modes
  - Automatic capability detection
  - Comprehensive test suite

---

## Support & Contributing

For questions, bug reports, or feature requests, contact:

**Ashutosh Sinha**  
Email: ajsinha@gmail.com

---

## License

Copyright © 2025-2030, All Rights Reserved  
Ashutosh Sinha

This software and documentation are proprietary and confidential. All rights reserved.

**Patent Pending**: Certain architectural patterns and implementations may be subject to patent applications.

---

**Made with ❤️ by Ashutosh Sinha**