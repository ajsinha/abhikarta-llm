# Abhikarta LLM Vector Store Architecture and Design

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

---

## Legal Notice

This document and the associated software architecture are proprietary and confidential. Unauthorized copying, distribution, modification, or use of this document or the software system it describes is strictly prohibited without explicit written permission from the copyright holder. This document is provided "as is" without warranty of any kind, either expressed or implied. The copyright holder shall not be liable for any damages arising from the use of this document or the software system it describes.

**Patent Pending**: Certain architectural patterns and implementations described in this document may be subject to patent applications.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Architecture Principles](#architecture-principles)
4. [High-Level Architecture](#high-level-architecture)
5. [Component Architecture](#component-architecture)
6. [Design Patterns](#design-patterns)
7. [Interface Specifications](#interface-specifications)
8. [Implementation Details](#implementation-details)
9. [Data Flow Diagrams](#data-flow-diagrams)
10. [Deployment Architecture](#deployment-architecture)
11. [Usage Examples](#usage-examples)
12. [Performance Considerations](#performance-considerations)
13. [Security Architecture](#security-architecture)
14. [Future Enhancements](#future-enhancements)

---

## 1. Executive Summary

The **Abhikarta LLM Vector Store** is a comprehensive, provider-agnostic abstraction layer for vector database operations in Large Language Model (LLM) applications. It provides a unified interface across multiple vector store backends including ChromaDB, Pinecone, Weaviate, Qdrant, FAISS, PgVector, and in-memory implementations.

### Key Features

- **Unified Interface**: Single API for all vector database operations
- **Provider Agnostic**: Switch between vector stores without code changes
- **Production Ready**: Comprehensive CRUD operations, batch processing, and error handling
- **Scalable**: Support for both local and cloud-based vector stores
- **Extensible**: Easy to add new vector store implementations
- **Async Support**: Asynchronous operations for high-performance applications
- **Rich Feature Set**: MMR search, hybrid search, metadata filtering, and more

### Supported Vector Stores

| Store | Type | Use Case | Scalability |
|-------|------|----------|-------------|
| ChromaDB | Local/Cloud | Development, Small-Medium Scale | Medium |
| Pinecone | Cloud | Production, Large Scale | High |
| Weaviate | Self-hosted/Cloud | Enterprise, GraphQL | High |
| Qdrant | Self-hosted/Cloud | Production, High Performance | High |
| FAISS | Local | Research, Prototyping | Low-Medium |
| PgVector | PostgreSQL Extension | Existing PG Infrastructure | Medium |
| InMemory | In-Process | Testing, Caching | Low |

---

## 2. System Overview

### 2.1 Purpose

The Abhikarta Vector Store provides a standardized interface for vector similarity search operations, enabling LLM applications to:

- Store and retrieve document embeddings efficiently
- Perform semantic similarity searches
- Filter results based on metadata
- Support diverse deployment scenarios (local, cloud, hybrid)
- Maintain consistency across different vector database backends

### 2.2 Architecture Style

The system employs a **Facade Pattern** combined with **Strategy Pattern** to provide:

- A simplified interface to complex vector database subsystems
- Interchangeable implementations based on deployment requirements
- Consistent behavior across different backends

### 2.3 Core Abstractions

```
Document: Dict[str, Any]
├── id: str (unique identifier)
├── content: str (textual content)
├── metadata: Dict[str, Any] (arbitrary key-value pairs)
└── embedding: List[float] (optional, pre-computed vector)

Embedding: List[float]
└── Dense vector representation (typically 384-4096 dimensions)

Filter: Dict[str, Any]
└── Metadata-based query predicates

RetrievalResult: List[Tuple[Document, float]]
└── Ordered list of (document, similarity_score) pairs
```

---

## 3. Architecture Principles

### 3.1 Design Principles

1. **Separation of Concerns**: Vector storage logic separated from embedding generation
2. **Interface Segregation**: Clean, minimal interface with optional extensions
3. **Dependency Inversion**: Depend on abstractions, not concrete implementations
4. **Open/Closed Principle**: Open for extension (new stores), closed for modification
5. **Single Responsibility**: Each component has one reason to change

### 3.2 SOLID Principles Application

| Principle | Implementation |
|-----------|----------------|
| **S** - Single Responsibility | Each store implementation handles only its specific backend |
| **O** - Open/Closed | New stores can be added without modifying base class |
| **L** - Liskov Substitution | All implementations are interchangeable |
| **I** - Interface Segregation | Base class provides comprehensive but optional methods |
| **D** - Dependency Inversion | Clients depend on VectorStoreBase abstraction |

### 3.3 Key Design Goals

- **Consistency**: Identical behavior across different backends
- **Performance**: Efficient batch operations and async support
- **Reliability**: Comprehensive error handling and validation
- **Maintainability**: Clear code structure and documentation
- **Testability**: Mockable interfaces and dependency injection

---

## 4. High-Level Architecture

### 4.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                         │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │LLM App      │  │RAG Pipeline  │  │Search Service│  │
│  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘  │
└─────────┼─────────────────┼──────────────────┼──────────┘
          │                 │                  │
          └─────────────────┼──────────────────┘
                            │
┌───────────────────────────┼──────────────────────────────┐
│              Abstraction Layer                           │
│                  ┌────────▼────────┐                     │
│                  │VectorStoreBase  │                     │
│                  │(Abstract)       │                     │
│                  └────────┬────────┘                     │
└───────────────────────────┼──────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
┌─────────▼──────────────────▼─────────────────▼──────────┐
│              Implementation Layer                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ChromaDB  │  │Pinecone  │  │Weaviate  │  │Qdrant  │ │
│  │Store     │  │Store     │  │Store     │  │Store   │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬────┘ │
└───────┼─────────────┼──────────────┼─────────────┼──────┘
        │             │              │             │
┌───────▼─────────────▼──────────────▼─────────────▼──────┐
│              Backend Layer                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ChromaDB  │  │Pinecone  │  │Weaviate  │  │Qdrant  │ │
│  │Database  │  │Cloud     │  │Server    │  │Server  │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
└──────────────────────────────────────────────────────────┘
```

### 4.2 Component Interaction

```
Client                VectorStoreBase       ConcreteStore         Backend
  │                         │                     │                  │
  │  add_documents()        │                     │                  │
  ├────────────────────────>│                     │                  │
  │                         │  add_documents()    │                  │
  │                         ├────────────────────>│                  │
  │                         │                     │  validate input  │
  │                         │                     ├─────────┐        │
  │                         │                     │         │        │
  │                         │                     │<────────┘        │
  │                         │                     │  batch process   │
  │                         │                     ├─────────┐        │
  │                         │                     │         │        │
  │                         │                     │<────────┘        │
  │                         │                     │  insert vectors  │
  │                         │                     ├─────────────────>│
  │                         │                     │    return IDs    │
  │                         │                     │<─────────────────┤
  │                         │    return IDs       │                  │
  │                         │<────────────────────┤                  │
  │    return IDs           │                     │                  │
  │<────────────────────────┤                     │                  │
  │                         │                     │                  │
```

---

## 5. Component Architecture

### 5.1 VectorStoreBase - Abstract Interface

The core abstraction that defines the contract for all vector store implementations.

```python
class VectorStoreBase(ABC):
    """
    Unified interface for vector database operations.
    Defines all required and optional methods.
    """
```

#### Responsibility Matrix

| Category | Methods | Purpose |
|----------|---------|---------|
| **Initialization** | `__init__`, `from_documents` | Setup and factory methods |
| **CRUD Operations** | `add_documents`, `update_documents`, `delete_documents`, `upsert_documents` | Data manipulation |
| **Retrieval** | `similarity_search`, `max_marginal_relevance_search`, `hybrid_search`, `get_documents` | Query operations |
| **Index Management** | `create_index`, `delete_index`, `list_indexes`, `get_index_stats` | Administrative operations |
| **Utilities** | `embed_query`, `count_documents`, `backup`, `restore`, `health_check` | Helper functions |
| **Async Support** | `aadd_documents`, `asimilarity_search`, `amax_marginal_relevance_search` | Asynchronous operations |

### 5.2 Implementation Hierarchy

```
                    VectorStoreBase (Abstract)
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
ChromaDBVectorStore  PineconeVectorStore  WeaviateVectorStore
        │                   │                   │
    - client            - index             - client
    - collection        - metric            - class_name
    - persist_path
        │
        └─── Methods:
             - add_documents()
             - similarity_search()
             - max_marginal_relevance_search()
             - get_documents()
             - etc.
```

### 5.3 Type System

```python
# Core Type Definitions
Document = Dict[str, Any]
# Structure: {
#     "id": str,           # Unique identifier
#     "content": str,      # Text content
#     "metadata": dict,    # Arbitrary metadata
#     "embedding": List[float]  # Optional pre-computed vector
# }

Embedding = List[float]
# Dense vector: [0.123, -0.456, 0.789, ...]
# Typical dimensions: 384 (MiniLM), 768 (BERT), 1536 (OpenAI), 4096 (Cohere)

Filter = Dict[str, Any]
# Metadata predicates: {
#     "category": "news",
#     "date": {"$gt": "2023-01-01"},
#     "author": {"$in": ["Alice", "Bob"]}
# }

RetrievalResult = List[Tuple[Document, float]]
# Results: [(doc1, 0.95), (doc2, 0.87), ...]
# Sorted by similarity score (descending)
```

---

## 6. Design Patterns

### 6.1 Facade Pattern

**Intent**: Provide a simplified, unified interface to a set of interfaces in a subsystem.

**Application**: VectorStoreBase acts as a facade over various vector database APIs.

```
Client Code ──> VectorStoreBase Facade ──┬──> ChromaDB API
                                          ├──> Pinecone API
                                          ├──> Weaviate API
                                          └──> Qdrant API
```

**Benefits**:
- Reduces complexity for clients
- Decouples client code from backend implementations
- Single point of API evolution

### 6.2 Strategy Pattern

**Intent**: Define a family of algorithms, encapsulate each one, and make them interchangeable.

**Application**: Each vector store implementation is a strategy for storing/retrieving vectors.

```python
# Strategy Selection Example
def create_vector_store(config: dict) -> VectorStoreBase:
    """Factory function demonstrating Strategy Pattern"""
    store_type = config.get("type", "chromadb")
    
    strategies = {
        "chromadb": ChromaDBVectorStore,
        "pinecone": PineconeVectorStore,
        "weaviate": WeaviateVectorStore,
        "qdrant": QdrantVectorStore,
    }
    
    store_class = strategies.get(store_type)
    return store_class(**config.get("params", {}))
```

### 6.3 Template Method Pattern

**Intent**: Define the skeleton of an algorithm in a base class, letting subclasses override specific steps.

**Application**: Common workflows (e.g., batch processing) are defined in base class or as utility methods.

```python
# Conceptual Template Method
def batch_add_documents(self, documents, batch_size=100):
    """Template method for batch processing"""
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        self._validate_batch(batch)        # Hook method
        self._process_batch(batch)         # Hook method
        self._commit_batch(batch)          # Hook method
```

### 6.4 Factory Method Pattern

**Intent**: Define an interface for creating objects, but let subclasses decide which class to instantiate.

**Application**: `from_documents()` class method creates instances from documents.

```python
@classmethod
def from_documents(cls, documents, embedding_model, **kwargs):
    """Factory method for creating initialized stores"""
    # Generate embeddings
    embeddings = embedding_model.embed_text([d["content"] for d in documents])
    
    # Create instance
    store = cls(**kwargs)
    
    # Populate
    store.add_documents(documents, embeddings=embeddings)
    
    return store
```

### 6.5 Adapter Pattern

**Intent**: Convert the interface of a class into another interface clients expect.

**Application**: Each implementation adapts backend-specific APIs to the unified interface.

```
VectorStoreBase Interface ──> ChromaDBVectorStore Adapter ──> ChromaDB Native API
```

---

## 7. Interface Specifications

### 7.1 Initialization Methods

#### `__init__(index_name, embedding_dim, metric, **kwargs)`

**Purpose**: Initialize vector store connection and configuration.

**Parameters**:
- `index_name` (str, optional): Index/collection name (default varies by implementation)
- `embedding_dim` (int, optional): Vector dimensionality (required for some stores)
- `metric` (str): Similarity metric - `"cosine"`, `"euclidean"`, `"dot"`, `"manhattan"`
- `**kwargs`: Provider-specific configuration

**Provider-Specific Parameters**:

| Provider | Special Parameters |
|----------|-------------------|
| ChromaDB | `persist_path` (str): Persistence directory |
| Pinecone | `api_key` (str), `environment` (str): Cloud credentials |
| Weaviate | `url` (str): Server endpoint |
| Qdrant | `host` (str), `port` (int): Server location |

**Example**:
```python
# ChromaDB with persistence
store = ChromaDBVectorStore(
    index_name="my_collection",
    embedding_dim=384,
    metric="cosine",
    persist_path="./data/chroma"
)

# Pinecone cloud
store = PineconeVectorStore(
    index_name="production-index",
    embedding_dim=1536,
    metric="cosine",
    api_key="your-api-key",
    environment="us-east1-gcp"
)
```

#### `from_documents(documents, embedding_model, index_name, **kwargs)`

**Purpose**: Factory method to create and populate store in one step.

**Parameters**:
- `documents` (List[Document]): Documents to insert
- `embedding_model`: Model/function to generate embeddings
- `index_name` (str, optional): Index name
- `**kwargs`: Passed to `__init__()` and `add_documents()`

**Returns**: Initialized and populated VectorStoreBase instance

**Example**:
```python
from sentence_transformers import SentenceTransformer

# Documents
docs = [
    {"content": "Machine learning is a subset of AI", "metadata": {"topic": "ml"}},
    {"content": "Neural networks are inspired by the brain", "metadata": {"topic": "nn"}}
]

# Embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Create and populate
store = ChromaDBVectorStore.from_documents(
    documents=docs,
    embedding_model=embedder,
    index_name="knowledge_base"
)
```

### 7.2 CRUD Operations

#### `add_documents(documents, embeddings, ids, batch_size, **kwargs)`

**Purpose**: Insert new documents with embeddings.

**Parameters**:
- `documents` (List[Document]): Documents to add
- `embeddings` (List[Embedding], optional): Pre-computed vectors
- `ids` (List[str], optional): Custom document IDs (auto-generated if None)
- `batch_size` (int): Batch size for insertion (default: 100)

**Returns**: List[str] - Inserted document IDs

**Behavior**:
- If `embeddings` is None and store has integrated embedder, generates embeddings
- If `embeddings` is None and no embedder available, raises ValueError
- Auto-generates UUIDs for missing IDs
- Processes in batches for efficiency

**Example**:
```python
# With pre-computed embeddings
ids = store.add_documents(
    documents=[
        {"content": "Document 1", "metadata": {"category": "tech"}},
        {"content": "Document 2", "metadata": {"category": "science"}}
    ],
    embeddings=[
        [0.1, 0.2, 0.3, ...],  # 384-dim vector
        [0.4, 0.5, 0.6, ...]   # 384-dim vector
    ]
)
print(f"Added documents: {ids}")
# Output: ['uuid-1', 'uuid-2']
```

#### `update_documents(ids, documents, embeddings, metadatas, **kwargs)`

**Purpose**: Update existing documents by ID.

**Parameters**:
- `ids` (List[str]): Document IDs to update
- `documents` (List[Document], optional): New content/metadata
- `embeddings` (List[Embedding], optional): New vectors
- `metadatas` (List[Dict], optional): Updated metadata only

**Returns**: bool - Success status

**Example**:
```python
# Update content and embedding
success = store.update_documents(
    ids=['doc-1'],
    documents=[{"content": "Updated content", "metadata": {"version": 2}}],
    embeddings=[[0.7, 0.8, 0.9, ...]]
)

# Update metadata only
success = store.update_documents(
    ids=['doc-1'],
    metadatas=[{"status": "reviewed"}]
)
```

#### `delete_documents(ids, filter, **kwargs)`

**Purpose**: Delete documents by IDs or metadata filter.

**Parameters**:
- `ids` (List[str], optional): Specific IDs to delete
- `filter` (Filter, optional): Metadata-based deletion

**Returns**: bool - Success status

**Example**:
```python
# Delete by IDs
store.delete_documents(ids=['doc-1', 'doc-2'])

# Delete by filter (all documents in category)
store.delete_documents(filter={"category": "outdated"})
```

#### `upsert_documents(documents, embeddings, ids, **kwargs)`

**Purpose**: Insert or update (upsert) documents.

**Parameters**:
- `documents` (List[Document]): Documents to upsert
- `embeddings` (List[Embedding], optional): Vectors
- `ids` (List[str]): Document IDs

**Returns**: List[str] - Affected IDs

**Example**:
```python
# Upsert documents (insert if new, update if exists)
ids = store.upsert_documents(
    documents=[{"content": "New or updated content"}],
    embeddings=[[0.1, 0.2, ...]],
    ids=['doc-1']
)
```

### 7.3 Retrieval Operations

#### `similarity_search(query, k, filter, score_threshold, **kwargs)`

**Purpose**: Perform similarity search using query text or embedding.

**Parameters**:
- `query` (str | Embedding): Query text (auto-embedded) or pre-computed vector
- `k` (int): Number of results (default: 5)
- `filter` (Filter, optional): Metadata filter
- `score_threshold` (float, optional): Minimum similarity score

**Returns**: RetrievalResult - List of (Document, score) tuples

**Scoring**:
- Cosine similarity: [0, 1] or [-1, 1] depending on implementation
- Higher scores = more similar
- Results sorted by score (descending)

**Example**:
```python
# Search with text query (requires integrated embedder)
results = store.similarity_search(
    query="machine learning algorithms",
    k=5,
    filter={"category": "tech"},
    score_threshold=0.7
)

for doc, score in results:
    print(f"Score: {score:.3f} - {doc['content'][:100]}")

# Search with pre-computed embedding
query_embedding = embedder.encode("machine learning")
results = store.similarity_search(
    query=query_embedding,
    k=10
)
```

#### `max_marginal_relevance_search(query, k, fetch_k, lambda_mult, filter, **kwargs)`

**Purpose**: MMR search for diverse results (reduces redundancy).

**Parameters**:
- `query` (str | Embedding): Query
- `k` (int): Final number of results (default: 5)
- `fetch_k` (int): Initial candidates to fetch (default: 20)
- `lambda_mult` (float): Diversity parameter [0, 1]
  - 0.0 = maximum diversity
  - 1.0 = maximum relevance (equivalent to similarity_search)
  - 0.5 = balanced
- `filter` (Filter, optional): Metadata filter

**Returns**: RetrievalResult

**Algorithm**:
1. Fetch `fetch_k` most similar documents
2. Iteratively select documents maximizing: `λ * similarity - (1-λ) * max_similarity_to_selected`
3. Return top `k` diverse documents

**Example**:
```python
# Diverse results for broad question
results = store.max_marginal_relevance_search(
    query="artificial intelligence",
    k=5,
    fetch_k=20,
    lambda_mult=0.5  # Balance relevance and diversity
)
```

#### `hybrid_search(query, k, alpha, filter, **kwargs)`

**Purpose**: Hybrid dense (semantic) + sparse (keyword) search.

**Parameters**:
- `query` (str): Query text
- `k` (int): Results
- `alpha` (float): Weight [0, 1]
  - 0.0 = pure keyword search
  - 1.0 = pure semantic search
  - 0.5 = equal weighting
- `filter` (Filter, optional): Metadata filter

**Returns**: RetrievalResult

**Note**: Not all backends support hybrid search natively. May require external sparse index (e.g., BM25).

**Example**:
```python
# Hybrid search (works with Weaviate, Qdrant with sparse vectors)
results = store.hybrid_search(
    query="python programming language",
    k=10,
    alpha=0.7  # Favor semantic over keyword
)
```

#### `get_documents(ids, include_embeddings, **kwargs)`

**Purpose**: Retrieve documents by IDs (direct lookup).

**Parameters**:
- `ids` (List[str]): Document IDs
- `include_embeddings` (bool): Include vectors in response (default: False)

**Returns**: List[Document]

**Example**:
```python
# Fetch specific documents
docs = store.get_documents(
    ids=['doc-1', 'doc-2', 'doc-3'],
    include_embeddings=True
)

for doc in docs:
    print(f"ID: {doc['id']}, Content: {doc['content'][:50]}")
    print(f"Embedding dim: {len(doc['embedding'])}")
```

### 7.4 Index Management

#### `create_index(index_name, embedding_dim, metric, **kwargs)`

**Purpose**: Create a new index/collection.

**Parameters**:
- `index_name` (str): Index name
- `embedding_dim` (int): Vector dimensionality
- `metric` (str): Similarity metric

**Returns**: bool - Success status

**Example**:
```python
store.create_index(
    index_name="new_collection",
    embedding_dim=768,
    metric="cosine"
)
```

#### `delete_index(index_name, **kwargs)`

**Purpose**: Delete an index/collection.

**Returns**: bool - Success status

#### `list_indexes(**kwargs)`

**Purpose**: List all available indexes.

**Returns**: List[str] - Index names

#### `get_index_stats(index_name, **kwargs)`

**Purpose**: Get index statistics.

**Returns**: Dict with keys like `document_count`, `storage_size`, etc.

**Example**:
```python
stats = store.get_index_stats()
print(f"Documents: {stats['document_count']}")
print(f"Metric: {stats.get('metric', 'unknown')}")
```

### 7.5 Utility Methods

#### `embed_query(query, **kwargs)`

**Purpose**: Generate embedding for a query using integrated embedder.

**Parameters**:
- `query` (str): Text to embed

**Returns**: Embedding (List[float])

**Note**: Requires store to be initialized with an embedding function.

#### `count_documents(filter, **kwargs)`

**Purpose**: Count documents matching filter.

**Returns**: int - Document count

#### `backup(path, **kwargs)`

**Purpose**: Backup the store to a file/directory.

**Returns**: bool - Success status

#### `restore(path, **kwargs)`

**Purpose**: Restore from a backup.

**Returns**: bool - Success status

#### `health_check()`

**Purpose**: Check if the vector store is reachable and healthy.

**Returns**: bool - Health status

**Example**:
```python
if store.health_check():
    print("Store is healthy")
else:
    print("Store unavailable - check connection")
```

### 7.6 Async Operations

#### `aadd_documents(**kwargs)`, `asimilarity_search(**kwargs)`, `amax_marginal_relevance_search(**kwargs)`

**Purpose**: Asynchronous versions of core operations.

**Example**:
```python
import asyncio

async def async_add():
    ids = await store.aadd_documents(
        documents=docs,
        embeddings=embeddings
    )
    return ids

# Run async
ids = asyncio.run(async_add())
```

---

## 8. Implementation Details

### 8.1 ChromaDB Implementation

**ChromaDBVectorStore** - Local or persistent vector store with simple API.

#### Architecture

```
ChromaDBVectorStore
│
├── PersistentClient (if persist_path provided)
│   └── Local SQLite + HDF5 storage
│
├── EphemeralClient (if no persist_path)
│   └── In-memory storage
│
└── Collection
    ├── Documents (text content)
    ├── Embeddings (vectors)
    ├── Metadatas (JSON objects)
    └── IDs (string identifiers)
```

#### Key Features

- **Persistence**: Automatic disk persistence with `persist_path`
- **Metrics**: Supports cosine, l2 (Euclidean), and ip (inner product)
- **Metadata Filtering**: Native support via `where` clause
- **HNSW Indexing**: Fast approximate nearest neighbor search

#### Configuration

```python
store = ChromaDBVectorStore(
    index_name="my_collection",
    embedding_dim=384,  # Informational only
    metric="cosine",    # or "l2", "ip"
    persist_path="./chroma_db"  # Persistence directory
)
```

#### Example Usage

```python
# Initialize
store = ChromaDBVectorStore(persist_path="./data")

# Add documents
docs = [
    {"content": "Paris is the capital of France", "metadata": {"source": "wiki"}},
    {"content": "Python is a programming language", "metadata": {"source": "docs"}}
]
embeddings = embedder.encode([d["content"] for d in docs])
ids = store.add_documents(docs, embeddings=embeddings)

# Search
results = store.similarity_search(
    query=embedder.encode("French capital")[0],
    k=1,
    filter={"source": "wiki"}
)
print(results[0][0]["content"])  # "Paris is the capital of France"
```

### 8.2 Pinecone Implementation

**PineconeVectorStore** - Cloud-native, fully managed vector database.

#### Architecture

```
PineconeVectorStore
│
├── Pinecone API Client
│   ├── Authentication (API key)
│   └── Region/Environment
│
└── Index
    ├── Vectors (dense embeddings)
    ├── Metadata (JSON payloads)
    ├── Namespaces (logical partitions)
    └── Pods (compute resources)
```

#### Key Features

- **Fully Managed**: No infrastructure management
- **Scalability**: Auto-scaling pods
- **Low Latency**: Global CDN and edge caching
- **Metadata Filtering**: Advanced filter expressions
- **Sparse-Dense Hybrid**: Support for hybrid vectors

#### Configuration

```python
store = PineconeVectorStore(
    index_name="production-index",
    embedding_dim=1536,
    metric="cosine",  # or "euclidean", "dotproduct"
    api_key="your-api-key",
    environment="us-east1-gcp"  # or other regions
)
```

#### Metadata Storage Pattern

Pinecone stores document content in metadata with special key:

```python
metadata = {
    "_content": doc["content"],  # Document text
    **doc["metadata"]            # User metadata
}
```

#### Example Usage

```python
# Initialize (creates index if not exists)
store = PineconeVectorStore(
    index_name="kb-index",
    embedding_dim=1536,
    api_key=os.getenv("PINECONE_API_KEY")
)

# Add with auto-batching
ids = store.add_documents(
    documents=[...],  # 10,000 documents
    embeddings=[...],
    batch_size=100  # Batches of 100
)

# Search with metadata filter
results = store.similarity_search(
    query=query_embedding,
    k=10,
    filter={"category": "technology", "year": {"$gte": 2023}}
)
```

### 8.3 Weaviate Implementation

**WeaviateVectorStore** - Open-source, GraphQL-based vector search engine.

#### Architecture

```
WeaviateVectorStore
│
├── Weaviate Client
│   ├── REST API
│   └── GraphQL API
│
└── Schema
    ├── Class (analogous to collection)
    │   ├── Properties (fields)
    │   ├── Vectorizer (embedding module)
    │   └── Vector Index Config
    └── Cross-references (graph relationships)
```

#### Key Features

- **GraphQL**: Powerful query language
- **Modular System**: Pluggable vectorizers and modules
- **Graph Capabilities**: Link documents via cross-references
- **Hybrid Search**: Built-in BM25 + vector search
- **Generative Search**: LLM integration for summarization

#### Schema Definition

```python
schema = {
    "class": "Document",
    "vectorizer": "none",  # External embeddings
    "properties": [
        {"name": "content", "dataType": ["text"]},
        {"name": "metadata", "dataType": ["object"]}
    ],
    "vectorIndexConfig": {
        "distance": "cosine"  # or "euclidean", "dot", "manhattan"
    }
}
```

#### Example Usage

```python
# Initialize
store = WeaviateVectorStore(
    index_name="Document",
    url="http://localhost:8080"
)

# Batch add with context manager
with store.client.batch as batch:
    for doc, emb in zip(documents, embeddings):
        batch.add_data_object(
            data_object={"content": doc["content"], "metadata": doc["metadata"]},
            class_name="Document",
            vector=emb
        )

# Hybrid search (semantic + keyword)
results = store.hybrid_search(
    query="machine learning",
    k=5,
    alpha=0.7  # Weight toward semantic
)
```

### 8.4 Qdrant Implementation

**QdrantVectorStore** - High-performance vector search engine with rich filtering.

#### Architecture

```
QdrantVectorStore
│
├── Qdrant Client
│   ├── gRPC API (high performance)
│   └── REST API
│
└── Collection
    ├── Vectors (dense embeddings)
    ├── Payload (JSON documents)
    ├── Payload Index (for fast filtering)
    └── HNSW Index (for vector search)
```

#### Key Features

- **Performance**: Written in Rust, highly optimized
- **Rich Filtering**: Complex payload queries
- **Payload Indexing**: Indexed metadata for fast filtering
- **Quantization**: Scalar and product quantization for compression
- **Distributed**: Sharding and replication support

#### Example Usage

```python
# Initialize (local or cloud)
store = QdrantVectorStore(
    index_name="my_collection",
    embedding_dim=768,
    metric="cosine",
    host="localhost",
    port=6333
)

# Add with structured payload
store.add_documents(
    documents=[
        {"content": "AI research paper", "metadata": {"type": "research", "year": 2024}}
    ],
    embeddings=[embedding_vector]
)

# Search with complex filter
results = store.similarity_search(
    query=query_vector,
    k=10,
    filter={
        "type": "research",
        "year": 2024
    }
)
```

### 8.5 Implementation Comparison

| Feature | ChromaDB | Pinecone | Weaviate | Qdrant |
|---------|----------|----------|----------|--------|
| **Deployment** | Local/Cloud | Cloud Only | Self-hosted/Cloud | Self-hosted/Cloud |
| **Persistence** | SQLite + Files | Managed | RocksDB | RocksDB |
| **Filtering** | Basic | Advanced | GraphQL | Rich |
| **Hybrid Search** | No | Via Sparse | Native | Via Sparse Vectors |
| **MMR** | External | External | External | External |
| **Indexing** | HNSW | Proprietary | HNSW | HNSW + Quantization |
| **Scalability** | Medium | High | High | High |
| **Cost** | Free | Usage-based | Free/Paid | Free/Paid |

---

## 9. Data Flow Diagrams

### 9.1 Document Addition Flow

```
┌─────────────┐
│   Client    │
│add_documents│
└──────┬──────┘
       │
       ▼
┌──────────────┐      YES    ┌─────────────────┐
│ Embeddings   ├────────────>│ Use Provided    │
│ Provided?    │              │ Embeddings      │
└──────┬───────┘              └────────┬────────┘
       │ NO                            │
       ▼                               │
┌──────────────┐      YES    ┌─────────┼────────┐
│ Integrated   ├────────────>│ Generate│        │
│ Embedder?    │              │ Embeddings      │
└──────┬───────┘              └────────┬────────┘
       │ NO                            │
       ▼                               │
┌──────────────┐                       │
│ Raise        │                       │
│ ValueError   │                       │
└──────────────┘                       │
                                       ▼
                                ┌──────────────┐
                                │ Validate     │
                                │ Input        │
                                └──────┬───────┘
                                       │
                                       ▼
                                ┌──────────────┐    YES    ┌──────────────┐
                                │ IDs          ├─────────>│ Use Provided │
                                │ Provided?    │           │ IDs          │
                                └──────┬───────┘           └──────┬───────┘
                                       │ NO                       │
                                       ▼                          │
                                ┌──────────────┐                 │
                                │ Generate     │                 │
                                │ UUIDs        │                 │
                                └──────┬───────┘                 │
                                       └──────────┬──────────────┘
                                                  │
                                                  ▼
                                           ┌──────────────┐
                                           │ Batch        │
                                           │ Documents    │
                                           └──────┬───────┘
                                                  │
                                                  ▼
                                           ┌──────────────┐
                                           │ Process      │
                                           │ Each Batch   │
                                           └──────┬───────┘
                                                  │
                                                  ▼
                                           ┌──────────────┐
                                           │ Backend      │
                                           │ Insert       │
                                           └──────┬───────┘
                                                  │
                                                  ▼
                                           ┌──────────────┐
                                           │ Return IDs   │
                                           └──────────────┘
```

### 9.2 Similarity Search Flow

```
┌─────────────┐
│   Client    │
│   search    │
└──────┬──────┘
       │
       ▼
┌──────────────┐      Text String    ┌─────────────────┐
│ Query Type?  ├──────────────────>│ Need to         │
└──────┬───────┘                     │ Generate        │
       │ Embedding Vector            │ Embedding       │
       │                             └────────┬────────┘
       │                                      │
       │                                      ▼
       │                             ┌─────────────────┐     YES
       │                             │ Integrated      ├────────┐
       │                             │ Embedder?       │        │
       │                             └────────┬────────┘        │
       │                                      │ NO              │
       │                                      ▼                 │
       │                             ┌─────────────────┐        │
       │                             │ Raise ValueError│        │
       │                             └─────────────────┘        │
       │                                                        │
       │                                      ┌─────────────────┘
       │                                      │
       └──────────────────────────────────────┘
                                              │
                                              ▼
                                       ┌──────────────┐
                                       │ Prepare      │
                                       │ Query        │
                                       └──────┬───────┘
                                              │
                                              ▼
                                       ┌──────────────┐    YES    ┌──────────────┐
                                       │ Filter       ├─────────>│ Build Filter │
                                       │ Provided?    │           │ Expression   │
                                       └──────┬───────┘           └──────┬───────┘
                                              │ NO                       │
                                              └──────────┬───────────────┘
                                                         │
                                                         ▼
                                                  ┌──────────────┐
                                                  │ Execute      │
                                                  │ Vector Search│
                                                  └──────┬───────┘
                                                         │
                                                         ▼
                                                  ┌──────────────┐
                                                  │ Backend      │
                                                  │ Returns      │
                                                  │ Results      │
                                                  └──────┬───────┘
                                                         │
                                                         ▼
                                                  ┌──────────────┐
                                                  │ Format       │
                                                  │ Results      │
                                                  └──────┬───────┘
                                                         │
                                                         ▼
                                                  ┌──────────────┐    YES
                                                  │ Score        ├────────┐
                                                  │ Threshold?   │        │
                                                  └──────┬───────┘        │
                                                         │ NO             │
                                                         │                ▼
                                                         │         ┌──────────────┐
                                                         │         │ Filter by    │
                                                         │         │ Score        │
                                                         │         └──────┬───────┘
                                                         │                │
                                                         └────────────────┘
                                                                  │
                                                                  ▼
                                                           ┌──────────────┐
                                                           │ Return       │
                                                           │ Results      │
                                                           └──────────────┘
```

### 9.3 MMR Search Algorithm

```
Step 1: Initial Similarity Search
┌────────────────────────────────────┐
│ Fetch fetch_k candidates          │
│ (e.g., top 20 similar docs)       │
└────────────┬───────────────────────┘
             │
             ▼
Step 2: Initialize
┌────────────────────────────────────┐
│ selected = []                      │
│ candidates = fetch_k results       │
└────────────┬───────────────────────┘
             │
             ▼
Step 3: Iterative Selection Loop
┌────────────────────────────────────┐
│ While len(selected) < k:           │
│                                    │
│   For each candidate:              │
│     MMR_score = λ * sim(query,doc) │
│       - (1-λ) * max(sim(doc,sel))  │
│                                    │
│   Select doc with highest MMR      │
│   Move to selected set             │
│   Remove from candidates           │
└────────────┬───────────────────────┘
             │
             ▼
Step 4: Return
┌────────────────────────────────────┐
│ Return top k diverse documents     │
└────────────────────────────────────┘

Where:
  λ (lambda_mult) = diversity parameter
  λ = 1.0: pure relevance
  λ = 0.0: pure diversity
  λ = 0.5: balanced
```

---

## 10. Deployment Architecture

### 10.1 Local Development Deployment

```
┌────────────────────────────────────────────┐
│       Developer Machine                    │
│                                            │
│  ┌──────────────────┐                     │
│  │ Python           │                     │
│  │ Application      │                     │
│  └────────┬─────────┘                     │
│           │                                │
│           ▼                                │
│  ┌──────────────────┐                     │
│  │ VectorStoreBase  │                     │
│  └────────┬─────────┘                     │
│           │                                │
│           ▼                                │
│  ┌──────────────────┐                     │
│  │ ChromaDBVector   │                     │
│  │ Store            │                     │
│  └────────┬─────────┘                     │
│           │                                │
│           ▼                                │
│  ┌──────────────────┐                     │
│  │ Local ChromaDB   │                     │
│  │ ./chroma_db      │                     │
│  └──────────────────┘                     │
│                                            │
│  ┌──────────────────┐                     │
│  │ Embedding Model  │                     │
│  │ (Local)          │                     │
│  └──────────────────┘                     │
└────────────────────────────────────────────┘

Use Case: Local development, testing, prototyping
```

### 10.2 Production Cloud Deployment

```
┌──────────────────────────────────────────────────────────┐
│                Production Environment                     │
│                                                           │
│  ┌────────────────┐                                      │
│  │ Load Balancer  │                                      │
│  └────────┬───────┘                                      │
│           │                                               │
│      ┌────┼────┬────────────────────┐                   │
│      │    │    │                    │                   │
│      ▼    ▼    ▼                    │                   │
│  ┌───┐ ┌───┐ ┌───┐                 │                   │
│  │App│ │App│ │App│                 │                   │
│  │ 1 │ │ 2 │ │ N │  Application    │                   │
│  └─┬─┘ └─┬─┘ └─┬─┘  Tier           │                   │
│    │     │     │                    │                   │
│    └─────┼─────┘                    │                   │
│          │                          │                   │
│          ▼                          │                   │
│  ┌────────────────┐                 │                   │
│  │ Pinecone Cloud │  Vector Store   │                   │
│  │ or             │  Tier           │                   │
│  │ Managed Qdrant │                 │                   │
│  └────────────────┘                 │                   │
│                                     │                   │
│  ┌────────────────┐                 │                   │
│  │ Embedding API  │  Embedding      │                   │
│  │ (OpenAI/Cohere)│  Service        │                   │
│  └────────────────┘                 │                   │
│                                     │                   │
│  ┌────────────────┐                 │                   │
│  │ PostgreSQL     │  Document       │                   │
│  │ (Metadata)     │  Store          │                   │
│  └────────────────┘                 │                   │
└──────────────────────────────────────────────────────────┘

Use Case: Production workloads with high availability
```

### 10.3 Hybrid Deployment (Self-Hosted)

```
┌──────────────────────────────────────────────────────────┐
│            On-Premise Kubernetes Cluster                 │
│                                                           │
│  ┌────────────────────────────────────────────┐         │
│  │         Application Pods                   │         │
│  │  ┌──────────┐      ┌──────────┐           │         │
│  │  │ App Pod 1│      │ App Pod 2│           │         │
│  │  └────┬─────┘      └────┬─────┘           │         │
│  └───────┼─────────────────┼──────────────────┘         │
│          │                 │                             │
│          └────────┬────────┘                             │
│                   │                                      │
│  ┌────────────────┼────────────────────────┐            │
│  │    Weaviate StatefulSet                 │            │
│  │  ┌────────┐  ┌────────┐  ┌────────┐    │            │
│  │  │Weaviate│  │Weaviate│  │Weaviate│    │            │
│  │  │ Node 1 │  │ Node 2 │  │ Node 3 │    │            │
│  │  └───┬────┘  └───┬────┘  └───┬────┘    │            │
│  └──────┼───────────┼───────────┼──────────┘            │
│         │           │           │                        │
│         └───────────┼───────────┘                        │
│                     │                                    │
│  ┌──────────────────▼───────────────────┐               │
│  │      Persistent Volumes              │               │
│  └──────────────────────────────────────┘               │
└──────────────────────────────────────────────────────────┘

Use Case: Enterprise with data sovereignty requirements
```

### 10.4 Multi-Region Deployment

```
┌──────────────────────────────────────────────────────────┐
│              Global Deployment                           │
│                                                           │
│  ┌────────────────────────────────────────────┐         │
│  │    Global Load Balancer (GeoDNS)          │         │
│  └──────┬─────────────┬─────────────┬─────────┘         │
│         │             │             │                    │
│    ┌────▼───┐    ┌────▼───┐    ┌───▼────┐              │
│    │        │    │        │    │        │              │
│  ┌─┴────────▼┐ ┌─▼────────▼┐ ┌─▼────────▼┐            │
│  │  US East  │ │ EU Region │ │Asia Region│            │
│  │           │ │           │ │           │            │
│  │┌─────────┐│ │┌─────────┐│ │┌─────────┐│            │
│  ││App      ││ ││App      ││ ││App      ││            │
│  ││Cluster  ││ ││Cluster  ││ ││Cluster  ││            │
│  │└────┬────┘│ │└────┬────┘│ │└────┬────┘│            │
│  │     │     │ │     │     │ │     │     │            │
│  │┌────▼────┐│ │┌────▼────┐│ │┌────▼────┐│            │
│  ││Pinecone ││ ││Pinecone ││ ││Pinecone ││            │
│  ││US-East  ││ ││EU-West  ││ ││AP-SE    ││            │
│  │└─────────┘│ │└─────────┘│ │└─────────┘│            │
│  └───────────┘ └───────────┘ └───────────┘            │
│                                                         │
│  ┌────────────────────────────────────────────┐        │
│  │   Central Document Store (Replicated)      │        │
│  └────────────────────────────────────────────┘        │
└──────────────────────────────────────────────────────────┘

Use Case: Global applications with regional data compliance
```

---

## 11. Usage Examples

### 11.1 Basic RAG Pipeline

```python
"""
Complete RAG (Retrieval Augmented Generation) pipeline
using Abhikarta Vector Store
"""

from sentence_transformers import SentenceTransformer
from vector_store.chromadb_vector_store import ChromaDBVectorStore
import openai

class RAGPipeline:
    def __init__(self, vector_store: VectorStoreBase, llm_model="gpt-4"):
        self.store = vector_store
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.llm_model = llm_model
    
    def index_documents(self, documents: List[str], metadatas: List[dict] = None):
        """Index documents into vector store"""
        # Generate embeddings
        embeddings = self.embedder.encode(documents, convert_to_numpy=True).tolist()
        
        # Prepare documents
        docs = [
            {
                "content": text,
                "metadata": metadatas[i] if metadatas else {}
            }
            for i, text in enumerate(documents)
        ]
        
        # Add to store
        ids = self.store.add_documents(docs, embeddings=embeddings)
        return ids
    
    def query(self, question: str, k: int = 3, filter: dict = None):
        """Query with RAG"""
        # 1. Generate query embedding
        query_emb = self.embedder.encode([question])[0].tolist()
        
        # 2. Retrieve relevant context
        results = self.store.similarity_search(
            query=query_emb,
            k=k,
            filter=filter
        )
        
        # 3. Build context from retrieved documents
        context = "\n\n".join([
            f"[Source {i+1}]: {doc['content']}"
            for i, (doc, score) in enumerate(results)
        ])
        
        # 4. Generate answer with LLM
        prompt = f"""Answer the question based on the context below.

Context:
{context}

Question: {question}

Answer:"""
        
        response = openai.ChatCompletion.create(
            model=self.llm_model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "answer": response.choices[0].message.content,
            "sources": [doc for doc, _ in results]
        }

# Usage
if __name__ == "__main__":
    # Initialize
    store = ChromaDBVectorStore(persist_path="./rag_data")
    rag = RAGPipeline(store)
    
    # Index knowledge base
    documents = [
        "The Eiffel Tower is located in Paris, France.",
        "Python was created by Guido van Rossum in 1991.",
        "Machine learning is a subset of artificial intelligence.",
    ]
    rag.index_documents(documents)
    
    # Query
    result = rag.query("Where is the Eiffel Tower?")
    print(f"Answer: {result['answer']}")
    print(f"Sources: {result['sources']}")
```

### 11.2 Batch Processing Large Dataset

```python
"""
Efficient batch processing for large-scale indexing
"""

from typing import Iterator
from vector_store.qdrant_vector_store import QdrantVectorStore
from sentence_transformers import SentenceTransformer
import time

class BatchIndexer:
    def __init__(
        self,
        vector_store: VectorStoreBase,
        embedder,
        batch_size: int = 100,
        embedding_batch_size: int = 32
    ):
        self.store = vector_store
        self.embedder = embedder
        self.batch_size = batch_size
        self.embedding_batch_size = embedding_batch_size
    
    def index_from_iterator(
        self,
        documents: Iterator[dict],
        total: int = None
    ):
        """Index documents from an iterator (e.g., database cursor)"""
        batch = []
        processed = 0
        
        for doc in documents:
            batch.append(doc)
            
            if len(batch) >= self.batch_size:
                self._process_batch(batch)
                processed += len(batch)
                
                if total:
                    print(f"Progress: {processed}/{total} ({100*processed/total:.1f}%)")
                
                batch = []
        
        # Process remaining
        if batch:
            self._process_batch(batch)
            processed += len(batch)
        
        return processed
    
    def _process_batch(self, batch: List[dict]):
        """Process a single batch"""
        texts = [doc["content"] for doc in batch]
        
        # Generate embeddings in sub-batches
        all_embeddings = []
        for i in range(0, len(texts), self.embedding_batch_size):
            sub_texts = texts[i:i + self.embedding_batch_size]
            sub_embeddings = self.embedder.encode(sub_texts, convert_to_numpy=True)
            all_embeddings.extend(sub_embeddings.tolist())
        
        # Add to store
        self.store.add_documents(batch, embeddings=all_embeddings)

# Usage
if __name__ == "__main__":
    # Initialize
    store = QdrantVectorStore(
        index_name="large_corpus",
        embedding_dim=768,
        host="localhost"
    )
    embedder = SentenceTransformer('all-mpnet-base-v2')
    indexer = BatchIndexer(store, embedder, batch_size=500)
    
    # Simulate document stream (e.g., from database)
    def document_generator():
        # In practice: SELECT * FROM documents
        for i in range(100000):
            yield {
                "content": f"Document {i} content...",
                "metadata": {"index": i}
            }
    
    # Index
    start = time.time()
    count = indexer.index_from_iterator(document_generator(), total=100000)
    elapsed = time.time() - start
    
    print(f"Indexed {count} documents in {elapsed:.2f}s ({count/elapsed:.0f} docs/s)")
```

### 11.3 Multi-Store Fallback Strategy

```python
"""
Resilient vector store with automatic fallback
"""

from typing import List
from vector_store.vector_store_base import VectorStoreBase, RetrievalResult
import logging

logger = logging.getLogger(__name__)

class ResilientVectorStore:
    """Vector store with primary/fallback strategy"""
    
    def __init__(
        self,
        primary: VectorStoreBase,
        fallback: VectorStoreBase,
        sync_enabled: bool = True
    ):
        self.primary = primary
        self.fallback = fallback
        self.sync_enabled = sync_enabled
    
    def add_documents(self, documents, embeddings, **kwargs):
        """Add to primary, optionally sync to fallback"""
        try:
            # Add to primary
            ids = self.primary.add_documents(documents, embeddings=embeddings, **kwargs)
            
            # Sync to fallback
            if self.sync_enabled:
                try:
                    self.fallback.add_documents(documents, embeddings=embeddings, ids=ids, **kwargs)
                except Exception as e:
                    logger.warning(f"Failed to sync to fallback: {e}")
            
            return ids
        
        except Exception as e:
            logger.error(f"Primary add failed: {e}, attempting fallback")
            return self.fallback.add_documents(documents, embeddings=embeddings, **kwargs)
    
    def similarity_search(self, query, **kwargs) -> RetrievalResult:
        """Search primary, fallback on failure"""
        try:
            return self.primary.similarity_search(query, **kwargs)
        except Exception as e:
            logger.warning(f"Primary search failed: {e}, using fallback")
            return self.fallback.similarity_search(query, **kwargs)
    
    def health_check(self) -> dict:
        """Check health of both stores"""
        return {
            "primary": self.primary.health_check(),
            "fallback": self.fallback.health_check()
        }

# Usage
if __name__ == "__main__":
    from vector_store.pinecone_vector_store import PineconeVectorStore
    from vector_store.chromadb_vector_store import ChromaDBVectorStore
    
    # Setup resilient store
    primary = PineconeVectorStore(index_name="prod", api_key="...")
    fallback = ChromaDBVectorStore(persist_path="./backup")
    
    store = ResilientVectorStore(primary, fallback, sync_enabled=True)
    
    # Use normally
    ids = store.add_documents(documents, embeddings=embeddings)
    results = store.similarity_search(query_emb, k=5)
```

### 11.4 Semantic Search API

```python
"""
RESTful API for semantic search using FastAPI
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from vector_store.pinecone_vector_store import PineconeVectorStore
from sentence_transformers import SentenceTransformer

app = FastAPI(title="Semantic Search API")

# Initialize
embedder = SentenceTransformer('all-MiniLM-L6-v2')
store = PineconeVectorStore(
    index_name="semantic-search",
    embedding_dim=384,
    api_key="your-api-key"
)

class Document(BaseModel):
    content: str
    metadata: Optional[dict] = {}

class SearchQuery(BaseModel):
    query: str
    k: int = 5
    filter: Optional[dict] = None

@app.post("/documents")
async def add_documents(documents: List[Document]):
    """Add documents to the index"""
    # Generate embeddings
    texts = [doc.content for doc in documents]
    embeddings = embedder.encode(texts).tolist()
    
    # Prepare docs
    docs = [
        {"content": doc.content, "metadata": doc.metadata}
        for doc in documents
    ]
    
    # Add to store
    ids = store.add_documents(docs, embeddings=embeddings)
    return {"ids": ids, "count": len(ids)}

@app.post("/search")
async def search(query: SearchQuery):
    """Semantic search"""
    # Generate query embedding
    query_emb = embedder.encode([query.query])[0].tolist()
    
    # Search
    results = store.similarity_search(
        query=query_emb,
        k=query.k,
        filter=query.filter
    )
    
    # Format response
    return {
        "results": [
            {
                "id": doc["id"],
                "content": doc["content"],
                "metadata": doc["metadata"],
                "score": score
            }
            for doc, score in results
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    healthy = store.health_check()
    if not healthy:
        raise HTTPException(status_code=503, detail="Vector store unavailable")
    return {"status": "healthy"}

# Run: uvicorn semantic_search_api:app --reload
```

### 11.5 Hybrid Search with BM25

```python
"""
Hybrid search combining semantic and keyword search
"""

from typing import List, Tuple
from vector_store.vector_store_base import VectorStoreBase, RetrievalResult
import numpy as np
from rank_bm25 import BM25Okapi

class HybridSearchEngine:
    """Semantic + BM25 hybrid search"""
    
    def __init__(
        self,
        vector_store: VectorStoreBase,
        embedder,
        documents: List[dict] = None
    ):
        self.store = vector_store
        self.embedder = embedder
        
        # Build BM25 index
        if documents:
            self._build_bm25(documents)
    
    def _build_bm25(self, documents: List[dict]):
        """Build BM25 index from documents"""
        self.documents = documents
        self.doc_ids = [doc["id"] for doc in documents]
        
        # Tokenize
        tokenized = [doc["content"].lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized)
    
    def hybrid_search(
        self,
        query: str,
        k: int = 10,
        alpha: float = 0.5,
        filter: dict = None
    ) -> RetrievalResult:
        """
        Hybrid search with configurable weighting
        
        Args:
            query: Search query
            k: Number of results
            alpha: Weight [0, 1] - 1.0 = pure semantic, 0.0 = pure BM25
            filter: Metadata filter
        
        Returns:
            Hybrid-ranked results
        """
        # 1. Semantic search
        query_emb = self.embedder.encode([query])[0].tolist()
        semantic_results = self.store.similarity_search(
            query=query_emb,
            k=k*2,  # Fetch more for fusion
            filter=filter
        )
        
        # 2. BM25 search
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Get top BM25 docs
        bm25_top_indices = np.argsort(bm25_scores)[::-1][:k*2]
        bm25_results = [
            (self.documents[idx], bm25_scores[idx])
            for idx in bm25_top_indices
        ]
        
        # 3. Normalize scores
        semantic_scores = {doc["id"]: score for doc, score in semantic_results}
        bm25_scores_dict = {doc["id"]: score for doc, score in bm25_results}
        
        # Min-max normalization
        def normalize(scores):
            min_s, max_s = min(scores.values()), max(scores.values())
            return {k: (v - min_s) / (max_s - min_s) if max_s > min_s else 0 
                    for k, v in scores.items()}
        
        semantic_norm = normalize(semantic_scores)
        bm25_norm = normalize(bm25_scores_dict)
        
        # 4. Fuse scores
        all_doc_ids = set(semantic_norm.keys()) | set(bm25_norm.keys())
        hybrid_scores = {}
        
        for doc_id in all_doc_ids:
            sem_score = semantic_norm.get(doc_id, 0.0)
            bm25_score = bm25_norm.get(doc_id, 0.0)
            hybrid_scores[doc_id] = alpha * sem_score + (1 - alpha) * bm25_score
        
        # 5. Rank and return top k
        sorted_ids = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)[:k]
        
        # Retrieve full documents
        doc_lookup = {doc["id"]: doc for doc, _ in semantic_results + bm25_results}
        results = [
            (doc_lookup[doc_id], score)
            for doc_id, score in sorted_ids
            if doc_id in doc_lookup
        ]
        
        return results

# Usage
if __name__ == "__main__":
    from vector_store.weaviate_vector_store import WeaviateVectorStore
    from sentence_transformers import SentenceTransformer
    
    # Initialize
    store = WeaviateVectorStore(index_name="hybrid_corpus")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Fetch all documents (for BM25 indexing)
    documents = [...]  # List of indexed documents
    
    # Create hybrid search engine
    hybrid = HybridSearchEngine(store, embedder, documents)
    
    # Search
    results = hybrid.hybrid_search(
        query="machine learning algorithms",
        k=10,
        alpha=0.7  # Favor semantic (70%) over keyword (30%)
    )
    
    for doc, score in results:
        print(f"Score: {score:.3f} - {doc['content'][:100]}")
```

---

## 12. Performance Considerations

### 12.1 Embedding Generation Optimization

**Bottleneck**: Embedding generation is often the slowest part of the pipeline.

**Optimization Strategies**:

1. **Batch Embedding**:
```python
# Bad: One at a time
embeddings = [embedder.encode(text) for text in texts]

# Good: Batch processing
embeddings = embedder.encode(texts, batch_size=32)
```

2. **GPU Acceleration**:
```python
from sentence_transformers import SentenceTransformer

# Use GPU if available
embedder = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')
```

3. **Caching**:
```python
from functools import lru_cache

@lru_cache(maxsize=10000)
def cached_embed(text: str):
    return tuple(embedder.encode([text])[0])
```

### 12.2 Vector Search Performance

**Factors Affecting Search Speed**:

| Factor | Impact | Optimization |
|--------|--------|--------------|
| **Index Size** | Linear to logarithmic | Use HNSW, quantization |
| **Vector Dimension** | Quadratic | Dimensionality reduction (PCA) |
| **Metadata Filtering** | Linear | Indexed metadata fields |
| **Result Count (k)** | Linear | Request only needed results |

**Approximate Benchmarks** (1M vectors, 768-dim):

| Operation | ChromaDB | Pinecone | Qdrant | FAISS |
|-----------|----------|----------|--------|-------|
| Insert (1000 docs) | 500ms | 200ms | 150ms | 50ms |
| Search (k=10) | 50ms | 20ms | 15ms | 5ms |
| Filtered Search | 100ms | 30ms | 20ms | N/A |

### 12.3 Batch Size Tuning

**Recommended Batch Sizes**:

```python
# Embedding generation
embedding_batch_size = 32  # Balance GPU memory and throughput

# Database insertion
insertion_batch_size = {
    "chromadb": 100,
    "pinecone": 100,
    "weaviate": 100,
    "qdrant": 100,
    "faiss": 1000  # FAISS is very fast locally
}
```

### 12.4 Scalability Guidelines

| Scale | Documents | Strategy | Store |
|-------|-----------|----------|-------|
| **Small** | < 10K | In-memory or local | ChromaDB, FAISS |
| **Medium** | 10K - 1M | Single server | Qdrant, Weaviate |
| **Large** | 1M - 100M | Distributed | Pinecone, Weaviate Cluster |
| **Massive** | > 100M | Multi-region | Pinecone (sharded) |

### 12.5 Memory Considerations

**Estimated Memory Usage**:

```
Memory = num_vectors × dimension × 4 bytes (float32) × overhead_factor

Example:
1M vectors × 768 dimensions × 4 bytes × 1.5 overhead
= 1,000,000 × 768 × 4 × 1.5
≈ 4.6 GB
```

**Optimization**:
- Use quantization (8-bit, 4-bit)
- Implement pagination for large result sets
- Stream large batches instead of loading all at once

---

## 13. Security Architecture

### 13.1 Authentication & Authorization

**API Key Management**:

```python
import os
from typing import Optional

class SecureVectorStore:
    """Wrapper with credential management"""
    
    @staticmethod
    def get_credentials(provider: str) -> dict:
        """Fetch credentials from secure source"""
        credentials = {
            "pinecone": {
                "api_key": os.getenv("PINECONE_API_KEY"),
                "environment": os.getenv("PINECONE_ENV")
            },
            "weaviate": {
                "api_key": os.getenv("WEAVIATE_API_KEY"),
                "url": os.getenv("WEAVIATE_URL")
            }
        }
        
        creds = credentials.get(provider, {})
        
        # Validate
        if not all(creds.values()):
            raise ValueError(f"Missing credentials for {provider}")
        
        return creds
    
    @classmethod
    def create_store(cls, provider: str, **kwargs):
        """Factory with automatic credential injection"""
        creds = cls.get_credentials(provider)
        
        store_classes = {
            "pinecone": PineconeVectorStore,
            "weaviate": WeaviateVectorStore,
        }
        
        store_class = store_classes[provider]
        return store_class(**{**creds, **kwargs})
```

### 13.2 Data Encryption

**At Rest**:
- ChromaDB: Use encrypted volumes
- Pinecone: Encrypted by default (AES-256)
- Weaviate/Qdrant: Encrypt persistent volumes

**In Transit**:
```python
# Enforce TLS for cloud stores
store = PineconeVectorStore(
    index_name="secure-index",
    api_key="...",
    environment="us-east1-gcp",
    # TLS enabled by default
)

# Weaviate with TLS
store = WeaviateVectorStore(
    url="https://my-cluster.weaviate.network",  # HTTPS
    api_key="..."
)
```

### 13.3 Metadata Sanitization

```python
import re
from typing import Any, Dict

class SecureMetadata:
    """Sanitize metadata to prevent injection attacks"""
    
    @staticmethod
    def sanitize(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Remove potentially dangerous content"""
        sanitized = {}
        
        for key, value in metadata.items():
            # Sanitize key
            safe_key = re.sub(r'[^a-zA-Z0-9_-]', '', key)
            
            # Sanitize value
            if isinstance(value, str):
                # Remove SQL/NoSQL injection patterns
                safe_value = re.sub(r'[;\'"\\]', '', value)
                safe_value = safe_value[:1000]  # Limit length
            elif isinstance(value, (int, float, bool)):
                safe_value = value
            else:
                safe_value = str(value)[:1000]
            
            sanitized[safe_key] = safe_value
        
        return sanitized

# Usage
doc = {
    "content": "Some text",
    "metadata": SecureMetadata.sanitize({
        "user_input": potentially_malicious_string
    })
}
```

### 13.4 Access Control (RBAC)

```python
from enum import Enum
from typing import List

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

class AccessControlledStore:
    """Vector store with RBAC"""
    
    def __init__(self, store: VectorStoreBase, user_permissions: List[Permission]):
        self.store = store
        self.permissions = user_permissions
    
    def _check_permission(self, required: Permission):
        if Permission.ADMIN in self.permissions:
            return True
        if required not in self.permissions:
            raise PermissionError(f"Permission denied: {required.value}")
    
    def add_documents(self, *args, **kwargs):
        self._check_permission(Permission.WRITE)
        return self.store.add_documents(*args, **kwargs)
    
    def similarity_search(self, *args, **kwargs):
        self._check_permission(Permission.READ)
        return self.store.similarity_search(*args, **kwargs)
    
    def delete_documents(self, *args, **kwargs):
        self._check_permission(Permission.DELETE)
        return self.store.delete_documents(*args, **kwargs)
```

### 13.5 Audit Logging

```python
import logging
from datetime import datetime
from functools import wraps

logger = logging.getLogger(__name__)

def audit_log(operation: str):
    """Decorator for audit logging"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            start = datetime.now()
            try:
                result = func(self, *args, **kwargs)
                logger.info(f"AUDIT: {operation} succeeded at {start} by user_id={getattr(self, 'user_id', 'unknown')}")
                return result
            except Exception as e:
                logger.error(f"AUDIT: {operation} failed at {start} - {str(e)}")
                raise
        return wrapper
    return decorator

class AuditedVectorStore:
    def __init__(self, store, user_id):
        self.store = store
        self.user_id = user_id
    
    @audit_log("add_documents")
    def add_documents(self, *args, **kwargs):
        return self.store.add_documents(*args, **kwargs)
    
    @audit_log("similarity_search")
    def similarity_search(self, *args, **kwargs):
        return self.store.similarity_search(*args, **kwargs)
```

---

## 14. Future Enhancements

### 14.1 Planned Features

1. **Multi-Vector Support**
   - Store multiple embeddings per document (e.g., title + content vectors)
   - Late interaction models (ColBERT-style)
   - Status: In Research

2. **Automatic Index Optimization**
   - Dynamic HNSW parameter tuning
   - Automatic quantization based on dataset size
   - Status: Q2 2025

3. **Advanced Filtering**
   - Geo-spatial filtering (lat/long ranges)
   - Temporal range queries
   - Complex boolean expressions (AND, OR, NOT)
   - Status: Q3 2025

4. **Reranking Integration**
   - Cross-encoder reranking pipeline
   - LLM-based reranking
   - Status: Q3 2025

5. **Observability**
   - Built-in metrics (latency, throughput, error rates)
   - OpenTelemetry integration
   - Cost tracking for cloud stores
   - Status: Q4 2025

### 14.2 Roadmap

| Quarter | Feature | Status |
|---------|---------|--------|
| Q1 2025 | Multi-vector support | In Progress |
| Q2 2025 | Geo-spatial filtering | Planned |
| Q2 2025 | Auto-optimization | Planned |
| Q3 2025 | Reranking integration | Planned |
| Q3 2025 | Advanced filtering | Planned |
| Q4 2025 | Observability suite | Research |
| Q4 2025 | Cost optimization tools | Research |

### 14.3 Extension Points

**Custom Similarity Functions**:
```python
from typing import Callable

class CustomMetricStore(VectorStoreBase):
    """Store with custom distance metric"""
    
    def __init__(self, similarity_fn: Callable = None, **kwargs):
        super().__init__(**kwargs)
        self.similarity_fn = similarity_fn or cosine_similarity
    
    def _compute_similarity(self, vec1, vec2):
        return self.similarity_fn(vec1, vec2)
```

**Middleware Pattern**:
```python
class VectorStoreMiddleware:
    """Extensible middleware for vector stores"""
    
    def __init__(self, store: VectorStoreBase):
        self.store = store
        self.middleware_stack = []
    
    def use(self, middleware: Callable):
        """Add middleware"""
        self.middleware_stack.append(middleware)
        return self
    
    def similarity_search(self, query, **kwargs):
        # Pre-processing middleware
        for mw in self.middleware_stack:
            query, kwargs = mw.before_search(query, kwargs)
        
        # Execute search
        results = self.store.similarity_search(query, **kwargs)
        
        # Post-processing middleware
        for mw in reversed(self.middleware_stack):
            results = mw.after_search(results)
        
        return results
```

**Plugin System**:
```python
class VectorStorePlugin(ABC):
    """Base class for plugins"""
    
    @abstractmethod
    def on_add(self, documents, embeddings):
        pass
    
    @abstractmethod
    def on_search(self, query, results):
        pass

class CachePlugin(VectorStorePlugin):
    """Example: Result caching plugin"""
    
    def __init__(self):
        self.cache = {}
    
    def on_search(self, query, results):
        # Cache results by query hash
        query_hash = hash(str(query))
        if query_hash in self.cache:
            return self.cache[query_hash]
        self.cache[query_hash] = results
        return results
```

---

## Appendix A: Error Handling

### Common Error Patterns

```python
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class VectorStoreError(Exception):
    """Base exception for vector store errors"""
    pass

class ConnectionError(VectorStoreError):
    """Store unreachable"""
    pass

class ValidationError(VectorStoreError):
    """Invalid input"""
    pass

def safe_add_documents(store, documents, embeddings):
    """Robust document addition with error handling"""
    try:
        # Validate
        if len(documents) != len(embeddings):
            raise ValidationError("Document and embedding counts must match")
        
        # Execute
        ids = store.add_documents(documents, embeddings=embeddings)
        logger.info(f"Successfully added {len(ids)} documents")
        return ids
    
    except ConnectionError as e:
        logger.error(f"Connection failed: {e}")
        # Attempt retry or fallback
        return None
    
    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        raise
    
    except Exception as e:
        logger.exception("Unexpected error during add_documents")
        raise VectorStoreError(f"Failed to add documents: {e}")
```

---

## Appendix B: Configuration Examples

### ChromaDB Configuration

```yaml
# config/chromadb.yaml
vector_store:
  type: chromadb
  params:
    index_name: production_kb
    embedding_dim: 384
    metric: cosine
    persist_path: /data/chroma_prod
    
embedding:
  model: sentence-transformers/all-MiniLM-L6-v2
  device: cuda
  batch_size: 32
```

### Pinecone Configuration

```yaml
# config/pinecone.yaml
vector_store:
  type: pinecone
  params:
    index_name: prod-search-index
    embedding_dim: 1536
    metric: cosine
    api_key: ${PINECONE_API_KEY}
    environment: us-east1-gcp
    
embedding:
  provider: openai
  model: text-embedding-3-large
  dimensions: 1536
```

### Qdrant Configuration

```yaml
# config/qdrant.yaml
vector_store:
  type: qdrant
  params:
    index_name: knowledge_base
    embedding_dim: 768
    metric: cosine
    host: qdrant-server.company.com
    port: 6333
    
embedding:
  model: sentence-transformers/all-mpnet-base-v2
  device: cuda
  batch_size: 64
```

---

## Appendix C: Testing Strategy

```python
import pytest
from vector_store.vector_store_base import VectorStoreBase

class VectorStoreTestSuite:
    """Standardized test suite for all implementations"""
    
    @pytest.fixture
    def store(self):
        """Override in concrete test class"""
        raise NotImplementedError
    
    def test_add_and_retrieve(self, store):
        """Test basic CRUD"""
        docs = [{"content": "test", "metadata": {}}]
        embeddings = [[0.1, 0.2, 0.3]]
        
        ids = store.add_documents(docs, embeddings=embeddings)
        assert len(ids) == 1
        
        retrieved = store.get_documents(ids)
        assert len(retrieved) == 1
        assert retrieved[0]["content"] == "test"
    
    def test_similarity_search(self, store):
        """Test search functionality"""
        # Add test data
        docs = [
            {"content": "machine learning", "metadata": {}},
            {"content": "deep learning", "metadata": {}},
        ]
        embeddings = [[0.9, 0.1], [0.1, 0.9]]
        store.add_documents(docs, embeddings=embeddings)
        
        # Search
        results = store.similarity_search([0.9, 0.1], k=1)
        assert len(results) == 1
        assert "machine" in results[0][0]["content"]
    
    def test_metadata_filtering(self, store):
        """Test filtered search"""
        docs = [
            {"content": "doc1", "metadata": {"type": "A"}},
            {"content": "doc2", "metadata": {"type": "B"}},
        ]
        embeddings = [[0.5, 0.5], [0.6, 0.4]]
        store.add_documents(docs, embeddings=embeddings)
        
        results = store.similarity_search(
            [0.5, 0.5],
            k=10,
            filter={"type": "A"}
        )
        assert len(results) == 1
        assert results[0][0]["metadata"]["type"] == "A"

class TestChromaDB(VectorStoreTestSuite):
    @pytest.fixture
    def store(self):
        return ChromaDBVectorStore(persist_path=":memory:")

class TestPinecone(VectorStoreTestSuite):
    @pytest.fixture
    def store(self):
        # Use test environment
        return PineconeVectorStore(
            index_name="test-index",
            api_key=os.getenv("PINECONE_API_KEY_TEST")
        )
```

---

## Glossary

**Embedding**: Dense vector representation of text, typically 384-4096 dimensions.

**HNSW**: Hierarchical Navigable Small World - graph-based algorithm for approximate nearest neighbor search.

**MMR**: Maximal Marginal Relevance - algorithm for diverse result selection.

**Quantization**: Compression technique reducing vector precision (e.g., float32 to int8).

**RAG**: Retrieval Augmented Generation - LLM pattern using retrieved context.

**Semantic Search**: Search based on meaning rather than keywords.

**Vector Store**: Database optimized for storing and searching high-dimensional vectors.

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-01-01 | Ashutosh Sinha | Initial release |
| 1.1 | 2025-01-06 | Ashutosh Sinha | Simplified diagrams for better rendering |

---

**End of Document**

*This document is proprietary and confidential. Unauthorized distribution is prohibited.*

**© 2025-2030 Ashutosh Sinha. All Rights Reserved.**
**Email: ajsinha@gmail.com**