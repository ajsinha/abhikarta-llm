"""
Vector Store Factory
Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.
Email: ajsinha@gmail.com

Factory module for creating vector store instances by name.
"""

from typing import Dict, Any, Optional, Type
from vector_store.vector_store_base import VectorStoreBase


class VectorStoreFactory:
    """
    Factory class for creating vector store instances.

    Provides a unified interface to instantiate different vector store
    implementations based on string identifiers.
    """

    _registry: Dict[str, Type[VectorStoreBase]] = {}
    _initialized = False

    @classmethod
    def _initialize_registry(cls):
        """Lazy initialization of vector store registry."""
        if cls._initialized:
            return

        # Import vector store implementations
        try:
            from vector_store.chromadb_vector_store import ChromaDBVectorStore
            cls._registry['chroma'] = ChromaDBVectorStore
            cls._registry['chromadb'] = ChromaDBVectorStore
        except ImportError as e:
            print(f"Warning: ChromaDB not available: {e}")

        try:
            from vector_store.pinecone_vector_store import PineconeVectorStore
            cls._registry['pinecone'] = PineconeVectorStore
        except ImportError as e:
            print(f"Warning: Pinecone not available: {e}")

        try:
            from vector_store.weaviate_vector_store import WeaviateVectorStore
            cls._registry['weaviate'] = WeaviateVectorStore
        except ImportError as e:
            print(f"Warning: Weaviate not available: {e}")

        try:
            from vector_store.qdrant_vector_store import QdrantVectorStore
            cls._registry['qdrant'] = QdrantVectorStore
        except ImportError as e:
            print(f"Warning: Qdrant not available: {e}")

        try:
            from vector_store.faiss_vector_store import FAISSVectorStore
            cls._registry['faiss'] = FAISSVectorStore
        except ImportError as e:
            print(f"Warning: FAISS not available: {e}")

        try:
            from vector_store.pgvector_vector_store import PGVectorStore
            cls._registry['pgvector'] = PGVectorStore
            cls._registry['postgres'] = PGVectorStore
            cls._registry['postgresql'] = PGVectorStore
        except ImportError as e:
            print(f"Warning: PGVector not available: {e}")

        try:
            from vector_store.inmemory_vector_store import InMemoryVectorStore
            cls._registry['inmemory'] = InMemoryVectorStore
            cls._registry['memory'] = InMemoryVectorStore
        except ImportError as e:
            print(f"Warning: InMemory store not available: {e}")

        cls._initialized = True

    @classmethod
    def create(
            cls,
            store_type: str,
            config: Optional[Dict[str, Any]] = None,
            **kwargs
    ) -> VectorStoreBase:
        """
        Create a vector store instance by type name.

        Args:
            store_type (str): Type of vector store. Supported values:
                - 'chroma', 'chromadb': ChromaDB vector store
                - 'pinecone': Pinecone cloud vector store
                - 'weaviate': Weaviate vector store
                - 'qdrant': Qdrant vector store
                - 'faiss': FAISS vector store
                - 'pgvector', 'postgres', 'postgresql': PostgreSQL with pgvector
                - 'inmemory', 'memory': In-memory vector store
            config (dict, optional): Configuration dictionary with store-specific parameters
            **kwargs: Additional keyword arguments (merged with config)

        Returns:
            VectorStoreBase: Initialized vector store instance

        Raises:
            ValueError: If store_type is not supported
            ImportError: If required dependencies for the store are not installed

        Examples:
            >>> # Create ChromaDB store
            >>> store = VectorStoreFactory.create(
            ...     'chroma',
            ...     config={'index_name': 'my_collection', 'persist_path': './data'}
            ... )

            >>> # Create Pinecone store
            >>> store = VectorStoreFactory.create(
            ...     'pinecone',
            ...     config={
            ...         'index_name': 'my-index',
            ...         'api_key': 'your-key',
            ...         'environment': 'us-east1-gcp'
            ...     }
            ... )

            >>> # Create with kwargs
            >>> store = VectorStoreFactory.create(
            ...     'faiss',
            ...     embedding_dim=768,
            ...     metric='cosine'
            ... )
        """
        # Initialize registry on first use
        cls._initialize_registry()

        # Normalize store type
        store_type = store_type.lower().strip()

        # Check if store type is registered
        if store_type not in cls._registry:
            available = ', '.join(sorted(set(cls._registry.keys())))
            raise ValueError(
                f"Unsupported vector store type: '{store_type}'. "
                f"Available types: {available}"
            )

        # Merge config and kwargs
        params = config.copy() if config else {}
        params.update(kwargs)

        # Get store class and instantiate
        store_class = cls._registry[store_type]

        try:
            return store_class(**params)
        except Exception as e:
            raise RuntimeError(
                f"Failed to create {store_type} vector store: {e}"
            ) from e

    @classmethod
    def register(cls, name: str, store_class: Type[VectorStoreBase]):
        """
        Register a custom vector store implementation.

        Args:
            name (str): Identifier for the store type
            store_class (Type[VectorStoreBase]): Vector store class

        Example:
            >>> class MyCustomStore(VectorStoreBase):
            ...     # Implementation
            ...     pass
            >>>
            >>> VectorStoreFactory.register('custom', MyCustomStore)
            >>> store = VectorStoreFactory.create('custom', index_name='test')
        """
        cls._initialize_registry()
        cls._registry[name.lower()] = store_class

    @classmethod
    def list_available_stores(cls) -> list:
        """
        List all available vector store types.

        Returns:
            list: List of supported store type names

        Example:
            >>> available = VectorStoreFactory.list_available_stores()
            >>> print(available)
            ['chroma', 'chromadb', 'pinecone', 'weaviate', ...]
        """
        cls._initialize_registry()
        return sorted(set(cls._registry.keys()))

    @classmethod
    def get_store_class(cls, store_type: str) -> Type[VectorStoreBase]:
        """
        Get the class for a specific store type without instantiation.

        Args:
            store_type (str): Type of vector store

        Returns:
            Type[VectorStoreBase]: Vector store class

        Raises:
            ValueError: If store_type is not supported
        """
        cls._initialize_registry()
        store_type = store_type.lower().strip()

        if store_type not in cls._registry:
            available = ', '.join(sorted(set(cls._registry.keys())))
            raise ValueError(
                f"Unsupported vector store type: '{store_type}'. "
                f"Available types: {available}"
            )

        return cls._registry[store_type]


def create_vector_store(
        store_type: str,
        config: Optional[Dict[str, Any]] = None,
        **kwargs
) -> VectorStoreBase:
    """
    Convenience function to create a vector store.

    This is a shorthand for VectorStoreFactory.create().

    Args:
        store_type (str): Type of vector store
        config (dict, optional): Configuration dictionary
        **kwargs: Additional keyword arguments

    Returns:
        VectorStoreBase: Initialized vector store instance

    Examples:
        >>> # Create ChromaDB store
        >>> store = create_vector_store('chroma', persist_path='./data')

        >>> # Create Pinecone with config dict
        >>> config = {
        ...     'index_name': 'prod-index',
        ...     'api_key': 'your-key',
        ...     'embedding_dim': 1536
        ... }
        >>> store = create_vector_store('pinecone', config)

        >>> # Create in-memory store for testing
        >>> store = create_vector_store('inmemory', embedding_dim=384)
    """
    return VectorStoreFactory.create(store_type, config, **kwargs)


# Example configurations for different stores
EXAMPLE_CONFIGS = {
    'chroma': {
        'index_name': 'my_collection',
        'embedding_dim': 384,
        'metric': 'cosine',
        'persist_path': './chroma_db'
    },
    'pinecone': {
        'index_name': 'my-index',
        'embedding_dim': 1536,
        'metric': 'cosine',
        'api_key': 'your-pinecone-api-key',
        'environment': 'us-east1-gcp'
    },
    'weaviate': {
        'index_name': 'Document',
        'embedding_dim': 768,
        'metric': 'cosine',
        'url': 'http://localhost:8080'
    },
    'qdrant': {
        'index_name': 'my_collection',
        'embedding_dim': 768,
        'metric': 'cosine',
        'host': 'localhost',
        'port': 6333
    },
    'faiss': {
        'index_name': 'default',
        'embedding_dim': 768,
        'metric': 'cosine',
        'persist_path': './faiss_index'
    },
    'pgvector': {
        'index_name': 'vector_store',
        'embedding_dim': 384,
        'metric': 'cosine',
        'host': 'localhost',
        'port': 5432,
        'database': 'vectordb',
        'user': 'postgres',
        'password': 'password'
    },
    'inmemory': {
        'index_name': 'default',
        'embedding_dim': 384,
        'metric': 'cosine'
    }
}

if __name__ == '__main__':
    """
    Example usage and testing
    """
    import os

    print("Abhikarta Vector Store Factory")
    print("=" * 50)
    print()

    # List available stores
    print("Available vector stores:")
    for store in VectorStoreFactory.list_available_stores():
        print(f"  - {store}")
    print()

    # Example 1: Create in-memory store (no dependencies)
    print("Example 1: Creating in-memory store")
    try:
        store = create_vector_store('inmemory', embedding_dim=384)
        print(f"✓ Created: {type(store).__name__}")
        print(f"  Health: {store.health_check()}")
    except Exception as e:
        print(f"✗ Error: {e}")
    print()

    # Example 2: Create with config dictionary
    print("Example 2: Creating store with config dict")
    config = {
        'index_name': 'test_collection',
        'embedding_dim': 768,
        'metric': 'cosine'
    }
    try:
        store = create_vector_store('inmemory', config=config)
        print(f"✓ Created: {type(store).__name__}")
        stats = store.get_index_stats()
        print(f"  Stats: {stats}")
    except Exception as e:
        print(f"✗ Error: {e}")
    print()

    # Example 3: Get store class
    print("Example 3: Getting store class")
    try:
        store_class = VectorStoreFactory.get_store_class('inmemory')
        print(f"✓ Class: {store_class.__name__}")
        print(f"  Module: {store_class.__module__}")
    except Exception as e:
        print(f"✗ Error: {e}")
    print()

    # Example 4: Show example configs
    print("Example 4: Sample configurations")
    for store_type, config in EXAMPLE_CONFIGS.items():
        print(f"\n{store_type}:")
        for key, value in config.items():
            print(f"  {key}: {value}")