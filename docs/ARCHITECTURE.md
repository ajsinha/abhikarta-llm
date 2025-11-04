<!--
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.2
-->

# Abhikarta LLM - Architecture & Design

**Technical Architecture Documentation**

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Design Principles](#design-principles)
3. [Core Architecture](#core-architecture)
4. [Component Details](#component-details)
5. [Design Patterns](#design-patterns)
6. [Data Flow](#data-flow)
7. [Extension Points](#extension-points)
8. [Performance Considerations](#performance-considerations)

---

## System Overview

Abhikarta LLM is built using a **layered architecture** with the Facade pattern at its core, providing a unified interface to 11 different LLM providers.

### High-Level Architecture

\`\`\`
┌─────────────────────────────────────────────────────────┐
│                  Application Layer                       │
│            (Your code using Abhikarta)                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Facade Layer                            │
│         UnifiedLLMFacade (Single Entry Point)            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ Complete │ │  Stream  │ │  Tools   │ │   RAG    │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Provider Abstraction Layer                  │
│           Base LLM Provider Interface                    │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬──────────┐
        ▼            ▼            ▼          ▼
   ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
   │ OpenAI │  │  Groq  │  │Mistral │  │ Ollama │
   │Provider│  │Provider│  │Provider│  │Provider│
   └───┬────┘  └───┬────┘  └───┬────┘  └───┬────┘
       │           │            │            │
       ▼           ▼            ▼            ▼
   [OpenAI]    [Groq]      [Mistral]    [Ollama]
     API         API          API        Local
\`\`\`

### Key Components

1. **Facade Layer** - Single entry point
2. **Provider Layer** - Abstractions for each LLM
3. **Feature Modules** - RAG, Tools, Validation, etc.
4. **Utility Layer** - Caching, metrics, security
5. **Configuration Layer** - Provider setup

---

## Design Principles

### 1. **Single Responsibility Principle**
Each component has one clear purpose:
- Facade: Unified interface
- Providers: LLM-specific logic
- Modules: Feature implementation

### 2. **Open/Closed Principle**
- Open for extension (new providers)
- Closed for modification (stable core)

### 3. **Liskov Substitution**
All providers implement `BaseLLMProvider` interface:
\`\`\`python
class BaseLLMProvider(ABC):
    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> LLMResponse:
        pass
    
    @abstractmethod
    def stream_complete(self, prompt: str, **kwargs) -> Iterator[StreamChunk]:
        pass
\`\`\`

### 4. **Dependency Inversion**
High-level modules depend on abstractions, not concrete implementations:
\`\`\`python
# Good: Depends on abstraction
facade = UnifiedLLMFacade(config)

# Not: facade = OpenAIProvider()  # Direct dependency
\`\`\`

### 5. **Interface Segregation**
Providers only implement what they need:
- All: `complete()`, `stream_complete()`
- Optional: `embed()`, `list_models()`

---

## Core Architecture

### Facade Pattern

The UnifiedLLMFacade is the single entry point:

\`\`\`python
class UnifiedLLMFacade:
    def __init__(self, config: Dict):
        self.providers = self._initialize_providers(config)
        self.default_provider = self._get_default()
    
    def complete(self, prompt: str, provider: str = None, **kwargs):
        """Route request to appropriate provider"""
        provider_instance = self.providers[provider or self.default_provider]
        return provider_instance.complete(prompt, **kwargs)
\`\`\`

### Provider Architecture

Each provider implements the base interface:

\`\`\`python
class OpenAIProvider(BaseLLMProvider):
    def initialize(self, config: Dict):
        self.client = OpenAI(api_key=config['api_key'])
        self.model = config.get('model', 'gpt-3.5-turbo')
    
    def complete(self, prompt: str, **kwargs) -> LLMResponse:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return LLMResponse(
            text=response.choices[0].message.content,
            metadata={'model': self.model, 'usage': response.usage}
        )
\`\`\`

---

## Component Details

### 1. Facade Layer

**File**: `llm/abstraction/facade.py`

**Responsibilities**:
- Provider initialization
- Request routing
- Error handling
- Response formatting

**Key Methods**:
\`\`\`python
def complete(prompt, provider=None, **kwargs) -> LLMResponse
def stream_complete(prompt, provider=None, **kwargs) -> Iterator[StreamChunk]
def embed(text, provider=None) -> Embedding
\`\`\`

### 2. Provider Layer

**Directory**: `llm/abstraction/providers/`

**Base Interface**: `BaseLLMProvider`

**Providers** (11 total):
1. `openai.py` - OpenAI (GPT)
2. `anthropic.py` - Anthropic (Claude)
3. `cohere.py` - Cohere
4. `google.py` - Google (Gemini)
5. `groq.py` - Groq (ultra-fast)
6. `mistral.py` - Mistral AI
7. `together.py` - Together AI
8. `ollama.py` - Ollama (local)
9. `huggingface.py` - Hugging Face
10. `replicate.py` - Replicate
11. `mock.py` - Mock (testing)

### 3. Feature Modules

**Function Calling**:
\`\`\`
llm/abstraction/tools/
├── __init__.py
├── tool.py          # Tool definition
├── registry.py      # Tool management
└── executor.py      # Tool execution
\`\`\`

**RAG System**:
\`\`\`
llm/abstraction/rag/
├── __init__.py
├── client.py        # RAG client
├── retriever.py     # Document retrieval
└── chunker.py       # Document chunking
\`\`\`

**Prompt Templates**:
\`\`\`
llm/abstraction/prompts/
├── __init__.py
├── template.py      # Template class
├── registry.py      # Template storage
└── defaults.py      # Default templates
\`\`\`

**Validation**:
\`\`\`
llm/abstraction/validation/
├── __init__.py
├── validator.py     # Schema validation
└── retry.py         # Auto-retry logic
\`\`\`

### 4. Utility Layer

**Caching**:
- `advanced/cache.py` - Semantic caching
- `advanced/pool.py` - Connection pooling

**Metrics**:
- `utils/metrics.py` - Performance tracking
- `utils/streaming.py` - Stream metrics

**Security**:
- `security/pii.py` - PII detection
- `security/filter.py` - Content filtering
- `security/rbac.py` - Access control
- `security/audit.py` - Audit logging

---

## Design Patterns

### 1. Facade Pattern
**Used**: Core architecture
**Purpose**: Simplify complex subsystems

### 2. Factory Pattern
**Used**: Provider creation
**Purpose**: Decouple object creation

\`\`\`python
def get_provider(name: str) -> BaseLLMProvider:
    providers = {
        'openai': OpenAIProvider,
        'groq': GroqProvider,
        'mistral': MistralProvider
    }
    return providers[name]()
\`\`\`

### 3. Strategy Pattern
**Used**: Provider selection
**Purpose**: Interchangeable algorithms

### 4. Observer Pattern
**Used**: Streaming callbacks
**Purpose**: Event notification

\`\`\`python
handler = StreamHandler(
    on_token=lambda t: print(t),
    on_complete=lambda: print("Done!")
)
\`\`\`

### 5. Decorator Pattern
**Used**: Caching, metrics
**Purpose**: Add functionality

\`\`\`python
@cache_response
@track_metrics
def complete(prompt):
    return provider.complete(prompt)
\`\`\`

### 6. Template Method Pattern
**Used**: Base provider
**Purpose**: Define skeleton

### 7. Registry Pattern
**Used**: Tools, prompts
**Purpose**: Central registration

---

## Data Flow

### Request Flow

\`\`\`
User Request
    │
    ▼
Facade.complete(prompt)
    │
    ├─► Validate input
    ├─► Select provider
    ├─► Apply middleware (cache check)
    │
    ▼
Provider.complete(prompt)
    │
    ├─► Prepare request
    ├─► Call LLM API
    ├─► Parse response
    │
    ▼
Return LLMResponse
    │
    ├─► Apply middleware (cache store)
    ├─► Track metrics
    ├─► Log audit
    │
    ▼
User receives response
\`\`\`

### Streaming Flow

\`\`\`
User Request Stream
    │
    ▼
Facade.stream_complete(prompt)
    │
    ▼
Provider.stream_complete(prompt)
    │
    ├─► Prepare request
    ├─► Open stream
    │
    ▼
For each chunk:
    │
    ├─► Parse chunk
    ├─► Track metrics (TTFT, TPS)
    ├─► Fire callbacks
    ├─► Yield StreamChunk
    │
    ▼
Stream complete
\`\`\`

### RAG Flow

\`\`\`
User Query
    │
    ▼
RAGClient.query(question)
    │
    ├─► Generate query embedding
    │
    ▼
VectorStore.search(embedding)
    │
    ├─► Find similar documents
    ├─► Return top-k results
    │
    ▼
Build context prompt
    │
    ├─► Format: "Context: ... Question: ..."
    │
    ▼
Facade.complete(prompt)
    │
    ▼
Return answer with citations
\`\`\`

---

## Extension Points

### Adding New Provider

1. **Create provider class**:
\`\`\`python
# llm/abstraction/providers/newprovider.py
class NewProvider(BaseLLMProvider):
    def initialize(self, config):
        # Setup
        pass
    
    def complete(self, prompt, **kwargs):
        # Implementation
        pass
    
    def stream_complete(self, prompt, **kwargs):
        # Implementation
        pass
\`\`\`

2. **Register in `__init__.py`**:
\`\`\`python
from .newprovider import NewProvider
__all__.append('NewProvider')
\`\`\`

3. **Add to facade**:
Provider auto-discovered by facade

### Adding New Feature

1. **Create module directory**:
\`\`\`
llm/abstraction/newfeature/
├── __init__.py
├── client.py
└── utils.py
\`\`\`

2. **Implement feature**:
\`\`\`python
class NewFeatureClient:
    def __init__(self, facade):
        self.facade = facade
    
    def do_something(self):
        # Implementation
        pass
\`\`\`

3. **Export from `__init__.py`**:
\`\`\`python
from .client import NewFeatureClient
__all__ = ['NewFeatureClient']
\`\`\`

---

## Performance Considerations

### 1. Connection Pooling
Reuse HTTP connections:
\`\`\`python
from llm.abstraction.advanced import ConnectionPool

pool = ConnectionPool(pool_size=10)
# Connections reused across requests
\`\`\`

### 2. Caching
Semantic caching reduces API calls:
\`\`\`python
from llm.abstraction.advanced import SemanticCache

cache = SemanticCache(embedding_client)
# Similar queries hit cache
\`\`\`

### 3. Batch Processing
Process multiple requests concurrently:
\`\`\`python
from llm.abstraction.batch import BatchProcessor

processor = BatchProcessor(facade, max_concurrent=10)
# 10-15x faster than sequential
\`\`\`

### 4. Streaming
Reduce latency with streaming:
\`\`\`python
# Non-streaming: Wait for full response
response = facade.complete(prompt)  # 2-5 seconds

# Streaming: Show tokens as generated
for chunk in facade.stream_complete(prompt):
    print(chunk.text)  # Immediate feedback
\`\`\`

### 5. Provider Selection
Choose provider based on needs:
- **Speed**: Groq (500+ tok/s)
- **Cost**: Ollama (free) or Mistral ($15/mo)
- **Quality**: OpenAI GPT-4

---

## Security Architecture

### Defense in Depth

\`\`\`
Application Code
    │
    ▼
┌─────────────────────┐
│   Input Validation   │ ◄─ Validate prompts
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   PII Detection      │ ◄─ Redact sensitive data
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Content Filtering   │ ◄─ Block harmful content
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   RBAC Check         │ ◄─ Verify permissions
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Audit Logging      │ ◄─ Log all actions
└──────────┬──────────┘
           │
           ▼
Provider API Call
\`\`\`

---

## Scalability

### Horizontal Scaling

\`\`\`
Load Balancer
    │
    ├─► Abhikarta Instance 1
    ├─► Abhikarta Instance 2
    └─► Abhikarta Instance 3
         │
         ├─► Provider Pool 1 (OpenAI)
         ├─► Provider Pool 2 (Groq)
         └─► Provider Pool 3 (Mistral)
\`\`\`

### Vertical Scaling

- **Batch Processing**: Handle more concurrent requests
- **Connection Pooling**: Reuse connections
- **Caching**: Reduce API calls

---

## Error Handling

### Retry Strategy

\`\`\`python
@retry(
    max_attempts=3,
    backoff=exponential,
    exceptions=[RateLimitError, APIError]
)
def complete_with_retry(prompt):
    return provider.complete(prompt)
\`\`\`

### Fallback Chain

\`\`\`python
providers = ['groq', 'mistral', 'ollama']

for provider in providers:
    try:
        return facade.complete(prompt, provider=provider)
    except Exception:
        continue  # Try next provider
\`\`\`

---

## Monitoring & Observability

### Metrics Tracked

1. **Request Metrics**
   - Request count
   - Response time
   - Token usage
   - Cost per request

2. **Provider Metrics**
   - Provider usage
   - Success rate
   - Error rate
   - Latency

3. **Feature Metrics**
   - Cache hit rate
   - Tool execution time
   - RAG retrieval time

### Logging Levels

\`\`\`
DEBUG   - Detailed information
INFO    - General information
WARNING - Warning messages
ERROR   - Error messages
CRITICAL - Critical issues
\`\`\`

---

## Testing Architecture

### Test Pyramid

\`\`\`
         ┌────┐
         │ E2E│     End-to-end tests
         └────┘
       ┌────────┐
       │Integration│  Integration tests
       └────────┘
     ┌──────────────┐
     │   Unit Tests  │  Unit tests
     └──────────────┘
\`\`\`

### Mock Provider

For testing without API calls:
\`\`\`python
config = {'providers': {'mock': {'enabled': True}}}
facade = UnifiedLLMFacade(config)

# Returns simulated responses
response = facade.complete("test")
\`\`\`

---

## Deployment Architecture

### Standalone Deployment

\`\`\`
Application
    │
    └─► Abhikarta LLM
            │
            ├─► OpenAI API
            ├─► Groq API
            └─► Local Ollama
\`\`\`

### Microservices Deployment

\`\`\`
API Gateway
    │
    ├─► Service A (Abhikarta)
    ├─► Service B (Abhikarta)
    └─► Service C (Abhikarta)
\`\`\`

---

## Best Practices

### 1. Configuration Management
- Use environment variables
- Separate dev/prod configs
- Never commit API keys

### 2. Error Handling
- Always use try/except
- Implement retry logic
- Have fallback providers

### 3. Performance
- Use caching when possible
- Batch requests for efficiency
- Choose appropriate provider

### 4. Security
- Enable PII detection
- Use RBAC
- Enable audit logging
- Rotate API keys regularly

### 5. Monitoring
- Track metrics
- Set up alerts
- Monitor costs
- Review audit logs

---

## Conclusion

Abhikarta LLM's architecture provides:
- **Flexibility**: 11 providers, easy to add more
- **Reliability**: Fallbacks, retry, error handling
- **Performance**: Caching, pooling, batch processing
- **Security**: PII, filtering, RBAC, audit
- **Scalability**: Horizontal and vertical scaling
- **Maintainability**: Clean architecture, SOLID principles

The facade pattern with provider abstraction enables **zero vendor lock-in** while maintaining a **simple, unified API**.

---

**© 2025-2030 Ashutosh Sinha | ajsinha@gmail.com**

---

**Copyright 2025-2030 all rights reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**  
**Version: 3.1.2**
