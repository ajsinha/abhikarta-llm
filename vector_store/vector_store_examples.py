"""
Example Usage of Vector Store Factory
Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.
Email: ajsinha@gmail.com

This file demonstrates how to use the VectorStoreFactory to create
and work with different vector store implementations.
"""

import os
import sys

# Add parent directory to path if running as script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vector_store.vector_store_factory import VectorStoreFactory, create_vector_store


def example_1_list_available_stores():
    """Example 1: List all available vector stores"""
    print("=" * 60)
    print("Example 1: Listing Available Vector Stores")
    print("=" * 60)

    stores = VectorStoreFactory.list_available_stores()
    print(f"\nFound {len(stores)} available store types:")
    for i, store in enumerate(stores, 1):
        print(f"  {i}. {store}")
    print()


def example_2_create_inmemory_store():
    """Example 2: Create an in-memory vector store"""
    print("=" * 60)
    print("Example 2: Creating In-Memory Vector Store")
    print("=" * 60)

    # Method 1: Using factory directly
    store = VectorStoreFactory.create(
        'inmemory',
        index_name='test_index',
        embedding_dim=384,
        metric='cosine'
    )

    print(f"\n✓ Created store: {type(store).__name__}")
    print(f"  Index name: test_index")
    print(f"  Embedding dim: 384")
    print(f"  Metric: cosine")
    print(f"  Health check: {store.health_check()}")

    # Get stats
    stats = store.get_index_stats()
    print(f"\nIndex Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()

    return store


def example_3_create_with_config_dict():
    """Example 3: Create store using configuration dictionary"""
    print("=" * 60)
    print("Example 3: Creating Store with Config Dictionary")
    print("=" * 60)

    # Configuration dictionary
    config = {
        'index_name': 'my_documents',
        'embedding_dim': 768,
        'metric': 'cosine'
    }

    print("\nConfiguration:")
    for key, value in config.items():
        print(f"  {key}: {value}")

    # Create store using convenience function
    store = create_vector_store('inmemory', config=config)

    print(f"\n✓ Store created successfully")
    print(f"  Type: {type(store).__name__}")
    print()

    return store


def example_4_add_and_search_documents(store):
    """Example 4: Add documents and perform similarity search"""
    print("=" * 60)
    print("Example 4: Adding Documents and Searching")
    print("=" * 60)

    # Sample documents
    documents = [
        {
            "content": "Paris is the capital of France",
            "metadata": {"category": "geography", "country": "France"}
        },
        {
            "content": "Berlin is the capital of Germany",
            "metadata": {"category": "geography", "country": "Germany"}
        },
        {
            "content": "Python is a programming language",
            "metadata": {"category": "technology", "type": "language"}
        },
        {
            "content": "Machine learning is a subset of AI",
            "metadata": {"category": "technology", "type": "ai"}
        }
    ]

    # Simulated embeddings (in real use, you'd use an actual embedding model)
    import numpy as np
    np.random.seed(42)  # For reproducibility

    embeddings = []
    for _ in documents:
        # Create random embeddings (768-dim to match config)
        emb = np.random.randn(768).tolist()
        embeddings.append(emb)

    # Add documents
    print(f"\nAdding {len(documents)} documents...")
    ids = store.add_documents(documents, embeddings=embeddings)
    print(f"✓ Added documents with IDs: {ids[:2]}... ({len(ids)} total)")

    # Get document count
    count = store.count_documents()
    print(f"✓ Total documents in store: {count}")

    # Perform similarity search
    print("\nPerforming similarity search...")
    query_embedding = embeddings[0]  # Use first document's embedding as query

    results = store.similarity_search(
        query=query_embedding,
        k=2,
        filter={"category": "geography"}
    )

    print(f"✓ Found {len(results)} results:")
    for i, (doc, score) in enumerate(results, 1):
        print(f"\n  Result {i}:")
        print(f"    Content: {doc['content']}")
        print(f"    Score: {score:.4f}")
        print(f"    Metadata: {doc['metadata']}")
    print()


def example_5_multiple_store_types():
    """Example 5: Create different types of stores"""
    print("=" * 60)
    print("Example 5: Creating Multiple Store Types")
    print("=" * 60)

    store_configs = {
        'inmemory': {
            'index_name': 'test1',
            'embedding_dim': 384,
            'metric': 'cosine'
        },
        'faiss': {
            'index_name': 'test2',
            'embedding_dim': 384,
            'metric': 'cosine',
            'persist_path': './test_faiss'
        }
    }

    created_stores = []

    for store_type, config in store_configs.items():
        try:
            print(f"\nCreating {store_type} store...")
            store = create_vector_store(store_type, config=config)
            created_stores.append((store_type, store))
            print(f"  ✓ Success: {type(store).__name__}")
            print(f"    Health: {store.health_check()}")
        except Exception as e:
            print(f"  ✗ Failed: {e}")

    print(f"\nSuccessfully created {len(created_stores)} store(s)")
    print()

    return created_stores


def example_6_error_handling():
    """Example 6: Demonstrate error handling"""
    print("=" * 60)
    print("Example 6: Error Handling")
    print("=" * 60)

    # Try to create unsupported store
    print("\nTrying to create unsupported store type...")
    try:
        store = create_vector_store('invalid_store')
        print("  ✗ Should have raised ValueError")
    except ValueError as e:
        print(f"  ✓ Caught expected error: {e}")

    # Try to create store with missing parameters
    print("\nTrying to create store without required parameters...")
    try:
        store = create_vector_store('inmemory')  # Missing embedding_dim
        print("  ✗ Should have raised error")
    except Exception as e:
        print(f"  ✓ Caught expected error: {type(e).__name__}")

    print()


def example_7_from_documents():
    """Example 7: Create store using from_documents class method"""
    print("=" * 60)
    print("Example 7: Creating Store from Documents")
    print("=" * 60)

    # Mock embedding model
    class MockEmbedder:
        def embed_text(self, texts):
            import numpy as np
            # Return random embeddings for demo
            return [np.random.randn(384).tolist() for _ in texts]

    documents = [
        {"content": "Document 1", "metadata": {"id": 1}},
        {"content": "Document 2", "metadata": {"id": 2}}
    ]

    embedder = MockEmbedder()

    # Get the store class
    InMemoryStore = VectorStoreFactory.get_store_class('inmemory')

    print("\nCreating store from documents...")
    store = InMemoryStore.from_documents(
        documents=documents,
        embedding_model=embedder,
        index_name='from_docs'
    )

    print(f"✓ Store created and populated")
    print(f"  Document count: {store.count_documents()}")
    print()


def example_8_custom_store_registration():
    """Example 8: Register a custom store implementation"""
    print("=" * 60)
    print("Example 8: Custom Store Registration")
    print("=" * 60)

    from vector_store.vector_store_base import VectorStoreBase

    # Define a minimal custom store
    class MyCustomStore(VectorStoreBase):
        def __init__(self, **kwargs):
            self.name = kwargs.get('name', 'custom')
            print(f"  Initialized custom store: {self.name}")

        # Implement required abstract methods (minimal for demo)
        def add_documents(self, documents, **kwargs):
            return []

        def similarity_search(self, query, **kwargs):
            return []

        def health_check(self):
            return True

        # ... (other abstract methods would need implementation)

    print("\nRegistering custom store...")
    VectorStoreFactory.register('mystore', MyCustomStore)

    print("✓ Custom store registered")
    print(f"  Available stores now include: {VectorStoreFactory.list_available_stores()[-1]}")

    print("\nCreating custom store instance...")
    custom = create_vector_store('mystore', name='test_custom')
    print(f"✓ Custom store created: {type(custom).__name__}")
    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("VECTOR STORE FACTORY - COMPREHENSIVE EXAMPLES")
    print("Copyright © 2025-2030 Ashutosh Sinha")
    print("=" * 60)
    print()

    # Run examples
    try:
        example_1_list_available_stores()

        store = example_2_create_inmemory_store()

        example_3_create_with_config_dict()

        example_4_add_and_search_documents(store)

        example_5_multiple_store_types()

        example_6_error_handling()

        example_7_from_documents()

        example_8_custom_store_registration()

        print("=" * 60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print()

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()