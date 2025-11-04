<!--
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.3
-->

# Abhikarta LLM - Complete Capabilities Documentation

**Comprehensive guide to all 32+ features**

---

## 📚 Table of Contents

1. [Core Features](#core-features)
2. [Advanced Features (v2.3.0)](#advanced-features-v230)
3. [Streaming Features (v2.2.0)](#streaming-features-v220)
4. [Security Features (v2.1.0)](#security-features-v210)
5. [Quick Reference](#quick-reference)
6. [Code Examples](#code-examples)

---

## Core Features

### 1. Unified Interface (Facade Pattern)
**What it does**: Single API for multiple LLM providers

**Example**:
```python
from llm.abstraction.facade import UnifiedLLMFacade

config = {'providers': {'openai': {'enabled': True}}}
facade = UnifiedLLMFacade(config)
response = facade.complete("Hello, world!")
```

**Benefits**:
- Switch providers without code changes
- Consistent API across all LLMs
- Easy provider comparison

**Example**: `01_basic_usage.py`

---

### 2. Multiple Provider Support
**Supported providers**: 7 total
1. OpenAI (GPT-3.5, GPT-4)
2. Anthropic (Claude 3)
3. Cohere (Command)
4. Google (Gemini)
5. Hugging Face
6. Replicate
7. Mock (testing)

**Configuration**:
```python
config = {
    'providers': {
        'openai': {'enabled': True, 'api_key': 'key1'},
        'anthropic': {'enabled': True, 'api_key': 'key2'},
        'mock': {'enabled': True}
    }
}
```

**Example**: `02_multiple_providers.py`

---

### 3. Configuration-Driven
**Features**:
- JSON/YAML/Python dict configuration
- Environment variable support
- Override defaults per request
- Provider-specific settings

**Example**:
```python
# Basic config
config = {
    'providers': {'openai': {'enabled': True}},
    'features': {
        'caching': True,
        'streaming': True
    }
}
```

---

### 4. Async Support
**What it does**: Non-blocking async operations

**Example**:
```python
async def generate():
    response = await facade.acomplete("prompt")
    return response.text

# Or with streaming
async for chunk in facade.astream_complete("prompt"):
    print(chunk.text)
```

**Benefits**:
- Better concurrency
- Higher throughput
- Scalable applications

---

### 5. Response Caching
**What it does**: Cache responses to avoid duplicate API calls

**Features**:
- Exact match caching
- Semantic caching (similarity-based)
- TTL (time-to-live)
- Size limits

**Benefits**:
- 50-200x faster for cached queries
- Significant cost savings
- Better user experience

---

### 6. History Tracking
**What it does**: Track all LLM interactions

**Information tracked**:
- Prompts and responses
- Timestamps
- Token usage
- Costs
- Model used
- Success/failure

**Use cases**:
- Debugging
- Cost analysis
- Quality monitoring
- Compliance

---

### 7. Error Handling
**Features**:
- Automatic retry with exponential backoff
- Provider fallback
- Graceful degradation
- Detailed error messages

**Example**:
```python
try:
    response = facade.complete(prompt)
except RateLimitError:
    # Handle rate limit
except APIError as e:
    # Handle API errors
```

---

### 8. Rate Limiting
**What it does**: Control request rate to avoid quota exhaustion

**Features**:
- Requests per minute/hour limits
- Token bucket algorithm
- Per-provider limits
- Automatic throttling

**Example**:
```python
from llm.abstraction.batch import RateLimitedBatchProcessor

processor = RateLimitedBatchProcessor(
    facade,
    requests_per_minute=60
)
```

---

### 9. Mock Provider
**What it does**: Test without real API calls

**Use cases**:
- Unit testing
- Development without API keys
- CI/CD pipelines
- Cost-free experimentation

**Example**:
```python
config = {
    'providers': {
        'mock': {
            'enabled': True,
            'model': 'mock-model'
        }
    }
}
```

---

### 10. Performance Metrics
**Tracked metrics**:
- Response time
- Token usage
- Tokens per second (TPS)
- Time to first token (TTFT)
- Cost per request
- Success rate

**Example**:
```python
response = facade.complete(prompt)
print(f"Tokens: {response.metadata['usage']}")
print(f"Time: {response.metadata['duration']}s")
```

---

## Advanced Features (v2.3.0)

### 11. Function Calling / Tool Use ⭐
**What it does**: Give LLMs access to external functions

**Example**:
```python
from llm.abstraction.tools import Tool, ToolRegistry

def get_weather(location: str) -> str:
    return f"Weather in {location}: Sunny"

registry = ToolRegistry()
registry.register(Tool("weather", "Get weather", get_weather))
result = registry.execute("weather", location="NYC")
```

**Use cases**:
- AI agents
- API integrations
- Workflow automation
- Multi-step reasoning

**Example**: `04_function_calling.py`

---

### 12. RAG Support ⭐
**What it does**: Answer questions using knowledge bases

**Features**:
- Document chunking
- Semantic retrieval
- Citation support
- Conversational RAG

**Example**:
```python
from llm.abstraction.rag import RAGClient, build_knowledge_base

documents = ["doc1", "doc2", "doc3"]
vector_store = build_knowledge_base(documents, embedding_client)

rag = RAGClient(facade, vector_store)
response = rag.query("What is...?")
```

**Use cases**:
- Customer support bots
- Document Q&A
- Knowledge management
- Research assistants

**Example**: `05_rag.py`

---

### 13. Prompt Templates ⭐
**What it does**: Manage reusable prompt templates

**Features**:
- Variable substitution
- Version management
- Usage tracking
- 8 default templates

**Example**:
```python
from llm.abstraction.prompts import PromptTemplate, PromptRegistry

template = PromptTemplate(
    name="summarize",
    template="Summarize in {num} sentences: {text}"
)

registry = PromptRegistry()
registry.register(template)

prompt = registry.render('summarize', num=3, text="...")
```

**Use cases**:
- Consistent prompting
- A/B testing
- Team collaboration
- Prompt engineering

**Example**: `06_prompt_templates.py`

---

### 14. Response Validation ⭐
**What it does**: Ensure outputs match expected schema

**Features**:
- Pydantic validation
- Automatic retry on failure
- JSON extraction
- Type safety

**Example**:
```python
from llm.abstraction.validation import ResponseValidator
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: float

validator = ResponseValidator()
product = validator.validate_with_retry(
    facade, prompt, Product
)
```

**Use cases**:
- Data extraction
- API integrations
- Type-safe responses
- Quality assurance

**Example**: `07_response_validation.py`

---

### 15. Batch Processing ⭐
**What it does**: Process multiple prompts efficiently

**Features**:
- Concurrent processing
- Rate limiting
- Error tracking
- Progress monitoring

**Example**:
```python
from llm.abstraction.batch import BatchProcessor

processor = BatchProcessor(facade, batch_size=10)
result = processor.process_batch_sync(prompts)

print(f"{result.successful}/{result.total} successful")
```

**Performance**:
- 10-15x faster than sequential
- Configurable concurrency
- Automatic retry on failures

**Example**: `08_batch_processing.py`

---

### 16. Conversation Management ⭐
**What it does**: Manage multi-turn conversations

**Features**:
- Automatic history tracking
- Token limit handling
- Conversation persistence
- Context truncation

**Example**:
```python
from llm.abstraction.conversation import ChatClient

chat = ChatClient(facade, max_history=50)

response1 = chat.chat("My name is Alice")
response2 = chat.chat("What's my name?")  # Remembers!
```

**Use cases**:
- Chat applications
- Customer support
- Interactive assistants
- Conversational AI

**Example**: `09_conversation.py`

---

### 17. Embeddings Support ⭐
**What it does**: Generate and use text embeddings

**Features**:
- Multiple providers (OpenAI, mock)
- Vector stores
- Semantic search
- Batch operations

**Example**:
```python
from llm.abstraction.embeddings import EmbeddingClient, VectorStore

client = EmbeddingClient(provider='openai')
store = VectorStore(client)

store.add("Document text")
results = store.search("query", top_k=5)
```

**Use cases**:
- Semantic search
- Document similarity
- Recommendation systems
- RAG foundation

**Example**: `10_embeddings.py`

---

### 18. Connection Pooling ⭐
**What it does**: Reuse HTTP connections for performance

**Features**:
- urllib3 pooling
- Configurable pool size
- Automatic retry
- Timeout handling

**Benefits**:
- 30-50% faster requests
- Reduced latency
- Better resource usage

**Example**:
```python
from llm.abstraction.advanced import ConnectionPool

pool = ConnectionPool(pool_size=10)
response = pool.request('POST', url, json=data)
```

---

### 19. Semantic Caching ⭐
**What it does**: Cache based on semantic similarity

**Features**:
- Similarity matching (not just exact)
- Configurable threshold
- TTL and size limits
- LRU eviction

**Example**:
```python
from llm.abstraction.advanced import SemanticCache

cache = SemanticCache(embedding_client, similarity_threshold=0.95)

cache.set("What is AI?", "AI is...")
response = cache.get("Tell me about AI")  # Hits cache!
```

**Benefits**:
- Better cache hit rate
- Understands meaning
- Cost optimization

**Example**: `11_semantic_caching.py`

---

## Streaming Features (v2.2.0)

### 20. Real-time Streaming
**What it does**: Stream responses token-by-token

**Example**:
```python
for chunk in facade.stream_complete(prompt):
    print(chunk.text, end='', flush=True)
```

**Benefits**:
- Immediate feedback
- Better UX
- Can stop early

**Example**: `03_streaming.py`

---

### 21. Performance Metrics
**Tracked during streaming**:
- TTFT (Time to First Token)
- TPS (Tokens Per Second)
- Total duration
- Token count

**Example**:
```python
from llm.abstraction.utils.streaming import StreamMetrics

metrics = StreamMetrics()
for chunk in stream:
    metrics.add_token(chunk.text)

print(f"TTFT: {metrics.ttft}s")
print(f"TPS: {metrics.tps}")
```

---

### 22. Event Callbacks
**Available events**:
- on_start
- on_token
- on_complete
- on_error

**Example**:
```python
from llm.abstraction.utils.streaming import StreamHandler

handler = StreamHandler(
    on_start=lambda m: print("Started!"),
    on_token=lambda t, i: print(f"Token: {t}"),
    on_complete=lambda txt, m: print("Done!")
)
```

---

### 23. Stream Utilities
**Features**:
- Buffering
- Throttling
- Timeout handling
- Error recovery

---

## Security Features (v2.1.0)

### 24. PII Detection & Redaction
**Detected PII types** (12):
1. Email addresses
2. Phone numbers
3. SSN
4. Credit cards
5. IP addresses
6. Physical addresses
7. Names
8. Passport numbers
9. Driver's licenses
10. Bank accounts
11. Medical records
12. Date of birth

**Example**:
```python
from llm.abstraction.security import PIIDetector

detector = PIIDetector()
text = "Email me at john@example.com"
safe_text = detector.redact(text)  # "Email me at [EMAIL]"
```

**Example**: `12_security_features.py`

---

### 25. Content Filtering
**Filtered categories** (12):
- Violence
- Hate speech
- Sexual content
- Profanity
- Self-harm
- Illegal activities
- Personal attacks
- Spam
- Misinformation
- Political (optional)
- Religious (optional)
- Financial fraud

**Example**:
```python
from llm.abstraction.security import ContentFilter

filter = ContentFilter(strictness='medium')
is_safe, categories = filter.check(text)
```

---

### 26. RBAC (Role-Based Access Control)
**Features**:
- User and role management
- 27 granular permissions
- Resource-based access
- Audit trails

**Roles**:
- Admin
- Developer
- Analyst
- User

**Example**:
```python
from llm.abstraction.security import RBACManager

rbac = RBACManager()
rbac.add_user("alice", role="developer")
if rbac.has_permission("alice", "llm.complete"):
    # Allow access
```

---

### 27. Audit Logging
**Logged information**:
- Who (user)
- What (action)
- When (timestamp)
- Where (IP address)
- Result (success/failure)
- Details (metadata)

**Features**:
- Encryption
- Retention policies
- Compliance support

---

### 28. API Key Rotation
**Features**:
- Automated rotation
- Grace periods
- Notifications
- Zero-downtime

---

## Quick Reference

### Feature Matrix

| Feature | Status | Version | Example |
|---------|--------|---------|---------|
| Unified Interface | ✅ | v2.0 | 01 |
| Multiple Providers | ✅ | v2.0 | 02 |
| Streaming | ✅ | v2.2 | 03 |
| Function Calling | ✅ | v2.3 | 04 |
| RAG | ✅ | v2.3 | 05 |
| Prompt Templates | ✅ | v2.3 | 06 |
| Validation | ✅ | v2.3 | 07 |
| Batch Processing | ✅ | v2.3 | 08 |
| Conversation | ✅ | v2.3 | 09 |
| Embeddings | ✅ | v2.3 | 10 |
| Semantic Caching | ✅ | v2.3 | 11 |
| Security | ✅ | v2.1 | 12 |

---

### Import Reference

```python
# Core
from llm.abstraction.facade import UnifiedLLMFacade

# Tools
from llm.abstraction.tools import Tool, ToolRegistry

# RAG
from llm.abstraction.rag import RAGClient, build_knowledge_base

# Templates
from llm.abstraction.prompts import PromptTemplate, PromptRegistry

# Validation
from llm.abstraction.validation import ResponseValidator

# Batch
from llm.abstraction.batch import BatchProcessor

# Conversation
from llm.abstraction.conversation import ChatClient

# Embeddings
from llm.abstraction.embeddings import EmbeddingClient, VectorStore

# Caching
from llm.abstraction.advanced import SemanticCache

# Security
from llm.abstraction.security import PIIDetector, ContentFilter
```

---

## Code Examples

See `examples/capabilities/` for complete code examples of every feature!

---

**© 2025-2030 Ashutosh Sinha | ajsinha@gmail.com**

---

**Copyright 2025-2030 all rights reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**  
**Version: 3.1.3**
