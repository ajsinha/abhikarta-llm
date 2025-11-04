<!--
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.3
-->

# Abhikarta LLM - Architecture & Design

**System Architecture Documentation v3.1.3**

---

## 📐 Overview

Abhikarta LLM is built on a **layered architecture** with clear separation of concerns, enabling modularity, extensibility, and maintainability.

### Design Principles

1. **Single Responsibility**: Each component has one clear purpose
2. **Open/Closed**: Open for extension, closed for modification
3. **Dependency Inversion**: Depend on abstractions, not concretions
4. **Provider Agnostic**: No coupling to specific LLM APIs
5. **Configuration-Driven**: Behavior controlled by configuration
6. **Production-Ready**: Enterprise-grade reliability and security

---

## 🏛️ High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     Application Layer                            │
│  (Your Code - Chat Apps, AI Agents, Knowledge Systems, etc.)    │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Facade Layer                                │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │          UnifiedLLMFacade (Main Entry Point)               │  │
│  │  • Single API for all operations                           │  │
│  │  • Provider selection & routing                            │  │
│  │  • Feature orchestration                                   │  │
│  └────────────────────────────────────────────────────────────┘  │
└───────────────────────────────┬──────────────────────────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Feature Modules │ │ Provider Manager │ │ Security Layer   │
│                  │ │                  │ │                  │
│ • RAG System     │ │ • Provider       │ │ • PII Detection  │
│ • Function Call  │ │   Registration   │ │ • Content Filter │
│ • Templates      │ │ • Load Balancing │ │ • RBAC           │
│ • Validation     │ │ • Fallback       │ │ • Audit Logging  │
│ • Batch Proc     │ │ • Health Checks  │ │ • Key Rotation   │
│ • Conversation   │ │                  │ │                  │
│ • Embeddings     │ │                  │ │                  │
│ • Caching        │ │                  │ │                  │
└──────────────────┘ └───────┬──────────┘ └──────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌──────────────┐  ┌──────────────┐    ┌──────────────┐
│   Provider   │  │   Provider   │ ...│   Provider   │
│   Adapter    │  │   Adapter    │    │   Adapter    │
│   (OpenAI)   │  │   (Groq)     │    │   (Ollama)   │
└──────┬───────┘  └──────┬───────┘    └──────┬───────┘
       │                 │                    │
       ▼                 ▼                    ▼
┌──────────────┐  ┌──────────────┐    ┌──────────────┐
│  External    │  │  External    │    │    Local     │
│  LLM API     │  │  LLM API     │    │  LLM Server  │
│  (Cloud)     │  │  (Cloud)     │    │  (Machine)   │
└──────────────┘  └──────────────┘    └──────────────┘
```

---

## 📦 Component Architecture

### 1. Facade Layer

**Purpose**: Provides unified interface to all functionality

**Key Classes**:
- `UnifiedLLMFacade` - Main entry point
- `ProviderRouter` - Routes requests to providers
- `ConfigManager` - Manages configuration

**Responsibilities**:
- API simplification
- Provider abstraction
- Feature coordination
- Error handling
- Configuration management

**Code Location**: `llm/abstraction/facade.py`

### 2. Provider Layer

**Purpose**: Adapters for different LLM providers

**Base Class**: `BaseLLMProvider`

**Provider Implementations** (11 total):
1. `OpenAIProvider` - GPT-3.5, GPT-4
2. `AnthropicProvider` - Claude 3
3. `CohereProvider` - Command
4. `GoogleProvider` - Gemini
5. `GroqProvider` - Mixtral (ultra-fast) 🆕
6. `MistralProvider` - Mistral models 🆕
7. `TogetherProvider` - 50+ open models 🆕
8. `OllamaProvider` - Local LLMs 🆕
9. `HuggingFaceProvider` - Community models
10. `ReplicateProvider` - Various models
11. `MockProvider` - Testing

**Interface Contract**:
```python
class BaseLLMProvider:
    def initialize(config: Dict) -> None
    def complete(prompt: str, **kwargs) -> LLMResponse
    def stream_complete(prompt: str, **kwargs) -> Iterator[StreamChunk]
    def get_cost(usage: Dict) -> float
    def get_model_info() -> Dict
```

**Code Location**: `llm/abstraction/providers/`

### 3. Feature Modules

#### RAG System (`llm/abstraction/rag/`)
- `RAGClient` - Main RAG interface
- `DocumentChunker` - Text chunking strategies
- `VectorStore` - Embedding storage
- `Retriever` - Semantic search
- `ContextBuilder` - Context construction

#### Function Calling (`llm/abstraction/tools/`)
- `Tool` - Tool definition
- `ToolRegistry` - Tool management
- `ToolExecutor` - Execution engine
- `ParameterValidator` - Input validation

#### Prompt Templates (`llm/abstraction/prompts/`)
- `PromptTemplate` - Template definition
- `PromptRegistry` - Template management
- `TemplateEngine` - Rendering engine
- `VariableExtractor` - Variable parsing

#### Response Validation (`llm/abstraction/validation/`)
- `ResponseValidator` - Schema validation
- `RetryHandler` - Auto-retry logic
- `SchemaRegistry` - Schema management
- `TypeConverter` - Type conversion

#### Batch Processing (`llm/abstraction/batch/`)
- `BatchProcessor` - Concurrent processing
- `RateLimiter` - Rate limiting
- `ProgressTracker` - Progress monitoring
- `ErrorCollector` - Error aggregation

#### Conversation (`llm/abstraction/conversation/`)
- `ChatClient` - Chat interface
- `Conversation` - History management
- `MessageStore` - Message persistence
- `ContextManager` - Context window management

#### Embeddings (`llm/abstraction/embeddings/`)
- `EmbeddingClient` - Embedding generation
- `VectorStore` - Vector storage
- `SemanticSearch` - Similarity search
- `Clustering` - Vector clustering

#### Advanced Features (`llm/abstraction/advanced/`)
- `SemanticCache` - Similarity-based caching
- `ConnectionPool` - HTTP connection pooling
- `LoadBalancer` - Provider load balancing
- `CircuitBreaker` - Failure protection

### 4. Security Layer

**Components**:
- `PIIDetector` - Detects 12 types of PII
- `ContentFilter` - Filters 12 content categories
- `RBACManager` - Role-based access control
- `AuditLogger` - Comprehensive logging
- `KeyRotator` - API key management

**Code Location**: `llm/abstraction/security/`

### 5. Utilities

**Streaming** (`llm/abstraction/utils/streaming/`):
- `StreamHandler` - Stream processing
- `StreamMetrics` - Performance tracking
- `BufferManager` - Stream buffering

**Caching** (`llm/abstraction/utils/caching/`):
- `CacheManager` - Cache coordination
- `ExactCache` - Exact match caching
- `SemanticCache` - Similarity caching
- `CacheEviction` - LRU eviction

**Metrics** (`llm/abstraction/utils/metrics/`):
- `MetricsCollector` - Metrics gathering
- `PerformanceTracker` - Performance monitoring
- `CostCalculator` - Cost tracking

---

## 🔄 Request Flow

### Basic Completion Flow

```
1. Application makes request
   └─> facade.complete("prompt")

2. Facade validates and prepares
   ├─> Check configuration
   ├─> Select provider
   ├─> Apply security filters
   └─> Check cache

3. Route to provider
   ├─> Provider adapter transforms request
   ├─> Call external API
   ├─> Transform response
   └─> Apply post-processing

4. Return to application
   ├─> Update cache
   ├─> Log to audit
   ├─> Track metrics
   └─> Return LLMResponse
```

### Streaming Flow

```
1. Application requests stream
   └─> facade.stream_complete("prompt")

2. Facade sets up stream
   ├─> Initialize StreamHandler
   ├─> Configure callbacks
   └─> Start metrics tracking

3. Provider streams tokens
   ├─> Each token arrives
   ├─> StreamHandler processes
   ├─> Callbacks triggered
   └─> Metrics updated

4. Stream completes
   ├─> Final metrics calculated
   ├─> Audit log written
   └─> Resources cleaned up
```

### RAG Flow

```
1. User asks question
   └─> rag.query("What is X?")

2. Retrieve relevant documents
   ├─> Generate query embedding
   ├─> Search vector store
   ├─> Rank by similarity
   └─> Get top K documents

3. Build context
   ├─> Combine documents
   ├─> Add citations
   └─> Format prompt

4. Generate answer
   ├─> Call LLM with context
   ├─> Extract answer
   └─> Return with sources
```

---

## 🔌 Extension Points

### Adding a New Provider

1. **Create provider class**:
```python
class NewProvider(BaseLLMProvider):
    def initialize(self, config):
        # Setup
        
    def complete(self, prompt, **kwargs):
        # Implementation
        
    def stream_complete(self, prompt, **kwargs):
        # Streaming
```

2. **Register in factory**:
```python
# providers/__init__.py
from .new_provider import NewProvider
```

3. **Add configuration**:
```python
config = {
    'providers': {
        'new_provider': {
            'enabled': True,
            'api_key': '...'
        }
    }
}
```

### Adding a Feature Module

1. **Create module directory**: `llm/abstraction/new_feature/`
2. **Implement core classes**
3. **Add to facade**: Integrate with `UnifiedLLMFacade`
4. **Write tests**: Add comprehensive tests
5. **Document**: Add to CAPABILITIES.md

---

## 📊 Data Flow

### Configuration Flow

```
config.yaml
    ↓
ConfigManager.load()
    ↓
Validate configuration
    ↓
Initialize providers
    ↓
Setup feature modules
    ↓
Ready for requests
```

### Response Flow

```
LLM API Response
    ↓
Provider transforms
    ↓
LLMResponse object
    ↓
Post-processing
    ↓
Cache update
    ↓
Metrics logging
    ↓
Return to user
```

---

## 🔐 Security Architecture

### Defense in Depth

```
Layer 1: Input Validation
    ├─> Parameter validation
    ├─> Type checking
    └─> Size limits

Layer 2: PII Detection
    ├─> Scan for sensitive data
    ├─> Redact if found
    └─> Log detection

Layer 3: Content Filtering
    ├─> Check categories
    ├─> Apply strictness level
    └─> Block or warn

Layer 4: RBAC
    ├─> Check permissions
    ├─> Verify role
    └─> Allow/deny

Layer 5: Audit Logging
    ├─> Log all actions
    ├─> Encrypt logs
    └─> Retain per policy
```

---

## ⚡ Performance Optimizations

### 1. Connection Pooling
- Reuse HTTP connections
- 30-50% faster requests
- Reduced latency

### 2. Caching
- **Exact Cache**: Fast lookups (hash-based)
- **Semantic Cache**: Similarity-based (embeddings)
- **Multi-level**: L1 (memory) + L2 (disk)

### 3. Batch Processing
- Concurrent requests
- Rate-limited execution
- 10-15x throughput improvement

### 4. Streaming
- Token-by-token delivery
- Reduced perceived latency
- Better UX

---

## 📈 Scalability

### Horizontal Scaling

```
Load Balancer
    ├─> Instance 1 (Abhikarta)
    ├─> Instance 2 (Abhikarta)
    └─> Instance N (Abhikarta)
         └─> Shared Cache (Redis)
         └─> Shared DB (PostgreSQL)
```

### Provider Load Balancing

```
Request
    ↓
Load Balancer
    ├─> Provider 1 (if available)
    ├─> Provider 2 (if available)
    └─> Provider N (if available)
```

---

## 🎯 Design Patterns Used

1. **Facade**: UnifiedLLMFacade simplifies complexity
2. **Adapter**: Provider adapters normalize APIs
3. **Strategy**: Different caching/validation strategies
4. **Factory**: Provider factory for instantiation
5. **Observer**: Event callbacks for streaming
6. **Singleton**: Configuration manager
7. **Template Method**: Base provider template
8. **Chain of Responsibility**: Security filters

---

## 📝 Code Organization

```
abhikarta-llm/
├── llm/
│   └── abstraction/
│       ├── facade.py           # Main facade
│       ├── providers/          # Provider adapters
│       │   ├── base.py
│       │   ├── openai.py
│       │   ├── groq.py
│       │   └── ...
│       ├── tools/              # Function calling
│       ├── rag/                # RAG system
│       ├── prompts/            # Templates
│       ├── validation/         # Validation
│       ├── batch/              # Batch processing
│       ├── conversation/       # Chat management
│       ├── embeddings/         # Embeddings
│       ├── advanced/           # Advanced features
│       ├── security/           # Security
│       └── utils/              # Utilities
├── examples/                   # Examples
├── tests/                      # Tests
└── docs/                       # Documentation
```

---

## 🔍 Testing Strategy

### Unit Tests
- Test each component in isolation
- Mock external dependencies
- High code coverage (>80%)

### Integration Tests
- Test component interactions
- Use test doubles for providers
- Verify end-to-end flows

### Provider Tests
- Test each provider adapter
- Mock external APIs
- Verify contract compliance

### Performance Tests
- Benchmark critical paths
- Load testing
- Stress testing

---

## 📚 Further Reading

- [CAPABILITIES.md](CAPABILITIES.md) - Feature documentation
- [USE_CASES.md](USE_CASES.md) - Use cases
- [USER_GUIDE.md](USER_GUIDE.md) - User guide
- [WHY_ABHIKARTA.md](WHY_ABHIKARTA.md) - Comparisons

---

© 2025-2030 Ashutosh Sinha | ajsinha@gmail.com

---

**Copyright 2025-2030 all rights reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**  
**Version: 3.1.3**
