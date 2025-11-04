<!--
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.4
-->

# Abhikarta LLM Architecture and Design

**Version: 3.1.4**  
**Technical Specification and Design Document**

---

**Copyright © 2025-2030 Ashutosh Sinha. All rights reserved.**  
**Email**: ajsinha@gmail.com  
**GitHub**: https://github.com/ajsinha/abhikarta

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Architecture](#2-system-architecture)
3. [Component Architecture](#3-component-architecture)
4. [Design Patterns](#4-design-patterns)
5. [Provider Abstraction Layer](#5-provider-abstraction-layer)
6. [Feature Modules](#6-feature-modules)
7. [Data Flow](#7-data-flow)
8. [Security Architecture](#8-security-architecture)
9. [Scalability Design](#9-scalability-design)
10. [Extension Points](#10-extension-points)
11. [Code Organization](#11-code-organization)
12. [Implementation Details](#12-implementation-details)

---

## 1. Introduction

### 1.1 Purpose

This document describes the architecture and design of Abhikarta LLM, a universal LLM abstraction framework that provides a unified interface to multiple Large Language Model providers.

### 1.2 Scope

This document covers:
- Overall system architecture
- Component design and interactions
- Design patterns and principles
- Implementation strategies
- Extensibility mechanisms
- Performance considerations
- Security architecture

### 1.3 Audience

- Software architects
- Senior developers
- Technical leads
- System integrators
- Security engineers

### 1.4 Document Conventions

- **Bold**: Important terms
- `Code`: Code elements
- → : Data flow direction
- ↔ : Bidirectional communication

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Application Layer                        │
│                     (User Applications/Services)                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Facade Layer                             │
│                     UnifiedLLMFacade                            │
│  • Single unified API                                           │
│  • Request routing                                              │
│  • Response normalization                                       │
│  • Configuration management                                     │
└───────────────────────────────┬─────────────────────────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            │                   │                   │
            ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Feature Layer   │  │ Feature Layer   │  │ Feature Layer   │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ • RAG           │  │ • Validation    │  │ • Security      │
│ • Tools         │  │ • Batch         │  │ • Caching       │
│ • Templates     │  │ • Conversation  │  │ • Monitoring    │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Provider Abstraction Layer                   │
│  • Provider factory                                             │
│  • Provider registry                                            │
│  • Protocol adapters                                            │
│  • Response normalizers                                         │
└───────────────────────────────┬─────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────┐
        │                       │                   │
        ▼                       ▼                   ▼
┌──────────────┐      ┌──────────────┐    ┌──────────────┐
│ Provider Mgr │      │ Provider Mgr │    │ Provider Mgr │
├──────────────┤      ├──────────────┤    ├──────────────┤
│ OpenAI       │      │ Groq         │    │ Ollama       │
│ Anthropic    │      │ Mistral      │    │ Mock         │
│ Cohere       │      │ Together     │    │ ...          │
│ Google       │      │ HuggingFace  │    │              │
└──────┬───────┘      └──────┬───────┘    └──────┬───────┘
       │                     │                    │
       ▼                     ▼                    ▼
┌──────────────┐      ┌──────────────┐    ┌──────────────┐
│ OpenAI API   │      │ Groq API     │    │ Ollama API   │
└──────────────┘      └──────────────┘    └──────────────┘
```

### 2.2 Architectural Layers

#### 2.2.1 Application Layer
- **Purpose**: User-facing applications and services
- **Responsibilities**: Business logic, UI, API endpoints
- **Technology**: Any (Python, web frameworks, etc.)

#### 2.2.2 Facade Layer
- **Purpose**: Unified interface to all LLM capabilities
- **Responsibilities**:
  - Request routing to appropriate providers
  - Response normalization
  - Configuration management
  - Error handling and recovery
- **Technology**: Python, Pydantic for validation

#### 2.2.3 Feature Layer
- **Purpose**: Advanced LLM capabilities
- **Modules**:
  - RAG (Retrieval Augmented Generation)
  - Function calling / Tool use
  - Prompt templates
  - Response validation
  - Batch processing
  - Conversation management
  - Embeddings
  - Semantic caching
  - Security features
- **Technology**: Python, specialized libraries

#### 2.2.4 Provider Abstraction Layer
- **Purpose**: Abstract away provider-specific details
- **Responsibilities**:
  - Provider instantiation
  - Protocol adaptation
  - Response normalization
  - Error translation
- **Technology**: Python, adapter pattern

#### 2.2.5 Provider Layer
- **Purpose**: Direct integration with LLM providers
- **Providers**: 11 total (OpenAI, Anthropic, Groq, Mistral, Together, Ollama, Cohere, Google, Hugging Face, Replicate, Mock)
- **Technology**: Provider SDKs, REST APIs

---

## 3. Component Architecture

### 3.1 Core Components

#### 3.1.4 UnifiedLLMFacade

```python
class UnifiedLLMFacade:
    """
    Main entry point - provides unified interface to all providers
    
    Responsibilities:
    - Configuration loading and validation
    - Provider initialization and management
    - Request routing
    - Response handling
    - Error management
    """
    
    def __init__(self, config: Dict[str, Any])
    def complete(self, prompt: str, **kwargs) -> LLMResponse
    def stream_complete(self, prompt: str, **kwargs) -> Iterator[StreamChunk]
    def list_providers(self) -> List[str]
    def get_provider(self, name: str) -> BaseLLMProvider
```

**Key Design Decisions:**
- Single instance manages all providers
- Configuration-driven initialization
- Lazy provider loading
- Thread-safe operations

#### 3.1.4 BaseLLMProvider

```python
class BaseLLMProvider(ABC):
    """
    Abstract base class for all LLM providers
    
    Defines contract that all providers must implement
    """
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None
    
    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> LLMResponse
    
    @abstractmethod
    def stream_complete(self, prompt: str, **kwargs) -> Iterator[StreamChunk]
```

**Design Principles:**
- Template Method pattern
- Contract-based design
- Minimal required interface
- Extension through subclassing

### 3.2 Feature Modules

#### 3.2.1 RAG Module

```
rag/
├── __init__.py
├── client.py          # RAGClient - main interface
├── retriever.py       # Document retrieval
├── chunker.py         # Document chunking
├── reranker.py        # Result reranking
└── citation.py        # Citation management
```

**Architecture:**
```
Query → Retriever → Reranker → LLM (with context) → Response with citations
```

#### 3.2.2 Tools Module

```
tools/
├── __init__.py
├── registry.py        # ToolRegistry
├── tool.py            # Tool definition
├── executor.py        # Tool execution
└── validator.py       # Parameter validation
```

**Architecture:**
```
LLM → Tool Call → Validator → Executor → Tool → Result → LLM
```

#### 3.2.3 Security Module

```
security/
├── __init__.py
├── pii_detector.py    # PII detection
├── content_filter.py  # Content filtering
├── rbac.py            # Role-based access control
├── audit_logger.py    # Audit logging
└── key_manager.py     # API key management
```

---

## 4. Design Patterns

### 4.1 Facade Pattern

**Purpose**: Provide simplified interface to complex subsystem

**Implementation**: UnifiedLLMFacade

```python
# Instead of:
openai_client = OpenAI(api_key=key)
anthropic_client = Anthropic(api_key=key)
# ... manage multiple clients

# Use:
facade = UnifiedLLMFacade(config)
# Single interface for all
```

**Benefits:**
- Simplified API
- Reduced coupling
- Easy provider switching

### 4.2 Strategy Pattern

**Purpose**: Define family of algorithms, make them interchangeable

**Implementation**: Provider selection

```python
class ProviderStrategy:
    def select_provider(self, criteria: Dict) -> BaseLLMProvider:
        # Select based on cost, speed, availability, etc.
        pass
```

**Benefits:**
- Flexible provider selection
- Runtime algorithm switching
- Easy to add new strategies

### 4.3 Factory Pattern

**Purpose**: Create objects without specifying exact class

**Implementation**: Provider instantiation

```python
class ProviderFactory:
    @staticmethod
    def create(provider_name: str, config: Dict) -> BaseLLMProvider:
        if provider_name == 'openai':
            return OpenAIProvider()
        elif provider_name == 'groq':
            return GroqProvider()
        # ... etc
```

**Benefits:**
- Centralized object creation
- Easy to add new providers
- Encapsulates construction logic

### 4.4 Observer Pattern

**Purpose**: Define one-to-many dependency for event notification

**Implementation**: Streaming callbacks

```python
class StreamHandler:
    def __init__(self):
        self.observers = []
    
    def attach(self, observer: Observer):
        self.observers.append(observer)
    
    def notify(self, event: Event):
        for observer in self.observers:
            observer.update(event)
```

**Benefits:**
- Loose coupling
- Dynamic subscriptions
- Event-driven architecture

### 4.5 Decorator Pattern

**Purpose**: Add functionality to objects dynamically

**Implementation**: Feature composition

```python
@with_caching
@with_validation
@with_monitoring
def complete(prompt: str) -> LLMResponse:
    # Core completion logic
    pass
```

**Benefits:**
- Dynamic feature addition
- Separation of concerns
- Composable functionality

### 4.6 Singleton Pattern

**Purpose**: Ensure single instance of class

**Implementation**: Configuration manager

```python
class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**Benefits:**
- Single source of truth
- Global access point
- Resource conservation

---

## 5. Provider Abstraction Layer

### 5.1 Provider Interface

All providers implement consistent interface:

```python
class BaseLLMProvider:
    # Required methods
    def initialize(self, config: Dict[str, Any]) -> None
    def complete(self, prompt: str, **kwargs) -> LLMResponse
    def stream_complete(self, prompt: str, **kwargs) -> Iterator[StreamChunk]
    
    # Optional methods
    def list_models(self) -> List[str]
    def get_model_info(self, model: str) -> Dict
    def count_tokens(self, text: str) -> int
```

### 5.2 Response Normalization

Different providers return different formats. We normalize to:

```python
@dataclass
class LLMResponse:
    text: str                    # Generated text
    metadata: Dict[str, Any]     # Provider-specific metadata
    raw_response: Any            # Original response object
    
    # Normalized metadata
    @property
    def model(self) -> str
    
    @property
    def tokens_used(self) -> Dict[str, int]
    
    @property
    def cost(self) -> float
```

### 5.3 Error Handling

Providers throw different errors. We normalize to:

```python
class LLMError(Exception):
    """Base exception"""
    pass

class APIError(LLMError):
    """API communication error"""
    pass

class RateLimitError(LLMError):
    """Rate limit exceeded"""
    pass

class AuthenticationError(LLMError):
    """Authentication failed"""
    pass

class ValidationError(LLMError):
    """Invalid input"""
    pass
```

### 5.4 Provider Registry

```python
class ProviderRegistry:
    """
    Central registry of all providers
    """
    
    def __init__(self):
        self._providers: Dict[str, Type[BaseLLMProvider]] = {}
    
    def register(self, name: str, provider_class: Type[BaseLLMProvider]):
        self._providers[name] = provider_class
    
    def get(self, name: str) -> Type[BaseLLMProvider]:
        return self._providers.get(name)
    
    def list_available(self) -> List[str]:
        return list(self._providers.keys())
```

---

## 6. Feature Modules

### 6.1 RAG (Retrieval Augmented Generation)

**Architecture:**

```
┌──────────────┐
│  User Query  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────┐
│  Embedding Generation            │
│  (Convert query to vector)       │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│  Vector Store Search             │
│  (Find similar documents)        │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│  Reranking                       │
│  (Score and sort results)        │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│  Context Assembly                │
│  (Build prompt with context)     │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│  LLM Generation                  │
│  (Generate answer)               │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│  Citation Extraction             │
│  (Link answer to sources)        │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────┐
│   Response   │
└──────────────┘
```

**Components:**

1. **DocumentChunker**: Split documents into chunks
2. **EmbeddingClient**: Generate embeddings
3. **VectorStore**: Store and search vectors
4. **Retriever**: Find relevant documents
5. **Reranker**: Score and sort results
6. **RAGClient**: Orchestrate RAG pipeline

### 6.2 Function Calling

**Architecture:**

```
LLM Request → Function Detection → Parameter Extraction →
Validation → Execution → Result Formatting → LLM Response
```

**Components:**

1. **Tool**: Function definition
2. **ToolRegistry**: Manage available tools
3. **ToolExecutor**: Execute tool functions
4. **ParameterValidator**: Validate inputs
5. **ResultFormatter**: Format outputs

**Example Flow:**

```
User: "What's the weather in NYC?"
  ↓
LLM: Identifies need for weather tool
  ↓
System: Extracts parameters {location: "NYC"}
  ↓
System: Validates parameters
  ↓
System: Executes get_weather("NYC")
  ↓
Tool: Returns "Sunny, 72°F"
  ↓
LLM: Formats final response
  ↓
Response: "The weather in NYC is sunny and 72°F"
```

### 6.3 Batch Processing

**Architecture:**

```
Input Queue → Batch Builder → Rate Limiter →
Parallel Executor → Result Collector → Output
```

**Components:**

1. **BatchProcessor**: Main coordinator
2. **RateLimiter**: Control request rate
3. **WorkerPool**: Parallel execution
4. **ResultAggregator**: Collect results
5. **ErrorHandler**: Manage failures

**Concurrency Model:**

```python
async def process_batch(prompts: List[str]):
    # Create worker pool
    pool = WorkerPool(max_workers=10)
    
    # Process in parallel
    tasks = [pool.submit(process_one, p) for p in prompts]
    
    # Gather results
    results = await asyncio.gather(*tasks)
    
    return results
```

### 6.4 Semantic Caching

**Architecture:**

```
Query → Generate Embedding → Search Cache →
If Hit: Return Cached | If Miss: Generate & Cache → Response
```

**Components:**

1. **SemanticCache**: Main cache manager
2. **EmbeddingClient**: Generate query embeddings
3. **SimilaritySearch**: Find similar queries
4. **CacheStore**: Store cached responses
5. **EvictionPolicy**: Manage cache size

**Similarity Calculation:**

```python
def is_similar(query_embedding, cached_embedding, threshold=0.95):
    similarity = cosine_similarity(query_embedding, cached_embedding)
    return similarity >= threshold
```

---

## 7. Data Flow

### 7.1 Synchronous Completion Flow

```
1. User → facade.complete("prompt")
2. Facade → Validate input
3. Facade → Select provider (based on config/strategy)
4. Facade → Apply pre-processors (caching, validation)
5. Provider → Transform to provider format
6. Provider → Call provider API
7. Provider → Receive response
8. Provider → Normalize response
9. Facade → Apply post-processors (logging, caching)
10. Facade → Return LLMResponse to user
```

### 7.2 Streaming Flow

```
1. User → facade.stream_complete("prompt")
2. Facade → Setup stream
3. Provider → Initiate streaming request
4. Loop:
   a. Provider → Receive chunk
   b. Provider → Normalize chunk
   c. Facade → Apply callbacks
   d. Facade → Yield StreamChunk to user
5. Provider → Stream complete
6. Facade → Cleanup & finalize metrics
```

### 7.3 RAG Flow

```
1. User → rag.query("question")
2. RAG → Generate query embedding
3. RAG → Search vector store
4. RAG → Retrieve top-k documents
5. RAG → Rerank results
6. RAG → Build context prompt
7. RAG → Call LLM with context
8. RAG → Extract citations
9. RAG → Return response with sources
```

### 7.4 Batch Processing Flow

```
1. User → processor.process_batch(prompts)
2. Processor → Split into batches
3. For each batch:
   a. Rate Limiter → Check quota
   b. Worker Pool → Process in parallel
   c. Collector → Gather results
4. Processor → Aggregate all results
5. Processor → Return BatchResult
```

---

## 8. Security Architecture

### 8.1 Security Layers

```
┌─────────────────────────────────────┐
│     Application Security            │
│  • Authentication                   │
│  • Authorization                    │
│  • Input validation                 │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│     Content Security                │
│  • PII detection                    │
│  • Content filtering                │
│  • Prompt injection protection      │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│     Access Control                  │
│  • RBAC                            │
│  • Permission checking              │
│  • Resource-level access            │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│     Audit & Compliance              │
│  • Activity logging                 │
│  • Audit trails                     │
│  • Compliance reporting             │
└─────────────────────────────────────┘
```

### 8.2 PII Detection Architecture

```python
class PIIDetector:
    """
    Detect and redact personally identifiable information
    """
    
    # Patterns for different PII types
    patterns = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        # ... 12 types total
    }
    
    def detect(self, text: str) -> List[PIIMatch]:
        """Detect PII in text"""
        
    def redact(self, text: str) -> str:
        """Replace PII with placeholders"""
```

### 8.3 RBAC Architecture

```python
class RBACManager:
    """
    Role-Based Access Control
    """
    
    # Permission hierarchy
    permissions = {
        'llm.read': 'View LLM responses',
        'llm.complete': 'Generate completions',
        'llm.stream': 'Use streaming',
        'llm.admin': 'Admin operations',
        # ... 27 permissions total
    }
    
    # Role definitions
    roles = {
        'user': ['llm.read', 'llm.complete'],
        'developer': ['llm.read', 'llm.complete', 'llm.stream'],
        'admin': ['llm.*'],  # All permissions
    }
```

### 8.4 Audit Logging

```python
class AuditLogger:
    """
    Comprehensive audit logging
    """
    
    def log_event(self, event: AuditEvent):
        """
        Log security event
        
        Captures:
        - Who (user)
        - What (action)
        - When (timestamp)
        - Where (IP, location)
        - Result (success/failure)
        - Details (metadata)
        """
```

---

## 9. Scalability Design

### 9.1 Horizontal Scaling

**Strategy**: Multiple facade instances

```
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Facade 1 │   │ Facade 2 │   │ Facade 3 │
└────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │
     └──────────────┼──────────────┘
                    │
            ┌───────▼────────┐
            │  Load Balancer │
            └───────┬────────┘
                    │
            ┌───────▼────────┐
            │   Providers    │
            └────────────────┘
```

**Benefits:**
- Distribute load
- No single point of failure
- Independent scaling

### 9.2 Vertical Scaling

**Strategy**: Increase resources per instance

- More CPU: Faster processing
- More memory: Larger caches
- Better network: Higher throughput

### 9.3 Caching Strategy

**Multi-Level Caching:**

```
L1: In-Memory Cache (fastest)
  ↓ (miss)
L2: Semantic Cache (fast)
  ↓ (miss)
L3: Distributed Cache (medium)
  ↓ (miss)
LLM Provider (slowest)
```

### 9.4 Connection Pooling

```python
class ConnectionPool:
    """
    Reuse HTTP connections
    """
    
    def __init__(self, pool_size=10):
        self.pool = urllib3.PoolManager(
            num_pools=pool_size,
            maxsize=pool_size,
            block=True
        )
```

**Benefits:**
- 30-50% faster requests
- Reduced latency
- Better resource usage

### 9.5 Async Processing

```python
async def process_requests(requests):
    """
    Process multiple requests concurrently
    """
    tasks = [process_one(req) for req in requests]
    results = await asyncio.gather(*tasks)
    return results
```

**Benefits:**
- Non-blocking I/O
- Higher concurrency
- Better throughput

---

## 10. Extension Points

### 10.1 Custom Providers

```python
from llm.abstraction.providers.base import BaseLLMProvider

class CustomProvider(BaseLLMProvider):
    """
    Add your own provider
    """
    
    def initialize(self, config):
        # Setup your provider
        pass
    
    def complete(self, prompt, **kwargs):
        # Implement completion
        pass
    
    def stream_complete(self, prompt, **kwargs):
        # Implement streaming
        pass

# Register
registry.register('custom', CustomProvider)
```

### 10.2 Custom Tools

```python
from llm.abstraction.tools import Tool

def my_function(param1: str, param2: int) -> str:
    """My custom tool"""
    return f"Result: {param1} {param2}"

# Create tool
tool = Tool(
    name="my_tool",
    description="My custom tool",
    function=my_function
)

# Register
registry.register(tool)
```

### 10.3 Custom Validators

```python
from llm.abstraction.validation import Validator

class CustomValidator(Validator):
    """
    Custom response validation
    """
    
    def validate(self, response: str) -> bool:
        # Your validation logic
        return True
```

### 10.4 Custom Caching

```python
from llm.abstraction.advanced import CacheBackend

class CustomCache(CacheBackend):
    """
    Custom cache implementation
    """
    
    def get(self, key: str) -> Optional[str]:
        # Retrieve from cache
        pass
    
    def set(self, key: str, value: str, ttl: int):
        # Store in cache
        pass
```

---

## 11. Code Organization

### 11.1 Directory Structure

```
abhikarta-llm/
│
├── llm/
│   └── abstraction/
│       ├── __init__.py
│       ├── facade.py              # Main facade
│       ├── base.py                # Base classes
│       │
│       ├── providers/             # Provider implementations
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── openai.py
│       │   ├── anthropic.py
│       │   ├── groq.py           # New
│       │   ├── mistral.py        # New
│       │   ├── together.py       # New
│       │   ├── ollama.py         # New
│       │   └── ...
│       │
│       ├── tools/                 # Function calling
│       │   ├── __init__.py
│       │   ├── registry.py
│       │   ├── tool.py
│       │   └── executor.py
│       │
│       ├── rag/                   # RAG system
│       │   ├── __init__.py
│       │   ├── client.py
│       │   ├── retriever.py
│       │   ├── chunker.py
│       │   └── reranker.py
│       │
│       ├── prompts/               # Templates
│       │   ├── __init__.py
│       │   ├── template.py
│       │   └── registry.py
│       │
│       ├── validation/            # Response validation
│       │   ├── __init__.py
│       │   └── validator.py
│       │
│       ├── batch/                 # Batch processing
│       │   ├── __init__.py
│       │   └── processor.py
│       │
│       ├── conversation/          # Chat management
│       │   ├── __init__.py
│       │   └── manager.py
│       │
│       ├── embeddings/            # Embeddings
│       │   ├── __init__.py
│       │   ├── client.py
│       │   └── vector_store.py
│       │
│       ├── advanced/              # Advanced features
│       │   ├── __init__.py
│       │   ├── caching.py
│       │   └── pooling.py
│       │
│       ├── security/              # Security
│       │   ├── __init__.py
│       │   ├── pii_detector.py
│       │   ├── content_filter.py
│       │   ├── rbac.py
│       │   └── audit_logger.py
│       │
│       └── utils/                 # Utilities
│           ├── __init__.py
│           ├── streaming.py
│           └── monitoring.py
│
├── examples/                      # Examples
│   └── capabilities/
│       ├── 01_basic_usage.py
│       ├── 02_multiple_providers.py
│       └── ...
│
├── tests/                         # Tests
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── docs/                          # Documentation
│   ├── README.md
│   ├── Architecture and Design.md
│   └── User Guide.md
│
└── setup.py                       # Package setup
```

### 11.2 Module Dependencies

```
facade.py
  → providers/
  → tools/
  → rag/
  → validation/
  → batch/
  → conversation/
  → embeddings/
  → advanced/
  → security/
  → utils/

Each feature module is independent and can be used separately
```

---

## 12. Implementation Details

### 12.1 Configuration Management

```python
@dataclass
class ProviderConfig:
    enabled: bool
    api_key: Optional[str]
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None

@dataclass
class SystemConfig:
    providers: Dict[str, ProviderConfig]
    features: Dict[str, Any]
    security: Dict[str, Any]
```

### 12.2 Error Handling Strategy

```python
def with_retry(max_retries=3, backoff=2):
    """
    Decorator for automatic retry with exponential backoff
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RetryableError as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(backoff ** attempt)
        return wrapper
    return decorator
```

### 12.3 Performance Monitoring

```python
class PerformanceMonitor:
    """
    Track performance metrics
    """
    
    def track_request(self, metadata: Dict):
        # Track metrics
        self.metrics['total_requests'] += 1
        self.metrics['total_tokens'] += metadata['tokens']
        self.metrics['total_cost'] += metadata['cost']
        self.metrics['latency'].append(metadata['duration'])
```

### 12.4 Thread Safety

```python
from threading import Lock

class ThreadSafeProvider:
    """
    Thread-safe provider wrapper
    """
    
    def __init__(self):
        self._lock = Lock()
    
    def complete(self, prompt):
        with self._lock:
            # Thread-safe completion
            pass
```

---

## Appendix A: Design Decisions

### A.1 Why Facade Pattern?

**Decision**: Use Facade pattern for main interface

**Rationale**:
- Simplify complex subsystem
- Reduce coupling
- Easy provider switching
- Consistent API

**Alternatives Considered**:
- Direct provider access: Too complex
- Adapter pattern only: Not enough abstraction

### A.2 Why Configuration-Driven?

**Decision**: Use configuration files/dicts for setup

**Rationale**:
- Separation of config and code
- Easy environment management
- Runtime flexibility
- No code changes for new providers

**Alternatives Considered**:
- Hardcoded: Too rigid
- Builder pattern: Too verbose

### A.3 Why Async Support?

**Decision**: Provide both sync and async interfaces

**Rationale**:
- Non-blocking I/O
- Better concurrency
- Scalability
- Modern Python best practice

**Alternatives Considered**:
- Sync only: Limited scalability
- Async only: Harder to use

---

## Appendix B: Performance Considerations

### B.1 Caching

- In-memory cache for speed
- Semantic cache for better hit rate
- Distributed cache for scale
- TTL-based eviction

### B.2 Connection Pooling

- Reuse HTTP connections
- Configurable pool size
- Automatic cleanup
- 30-50% performance improvement

### B.3 Batch Processing

- Parallel execution
- Rate limiting
- Error handling
- 10-15x throughput improvement

---

## Appendix C: Security Considerations

### C.1 API Key Management

- Environment variables
- Encrypted storage
- Rotation support
- Never log keys

### C.2 PII Protection

- Detect 12 PII types
- Automatic redaction
- Configurable sensitivity
- Audit logging

### C.3 Access Control

- Role-based (RBAC)
- 27 permissions
- Resource-level
- Audit trails

---

**End of Document**

**Copyright © 2025-2030 Ashutosh Sinha. All rights reserved.**  
**Email**: ajsinha@gmail.com  
**GitHub**: https://github.com/ajsinha/abhikarta

---

**Copyright 2025-2030 all rights reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**  
**Version: 3.1.4**
