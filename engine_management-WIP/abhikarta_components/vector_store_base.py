from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Tuple, Iterator, AsyncIterator

# Type aliases for clarity and consistency
Document = Dict[str, Any]  # {"id": str, "content": str, "metadata": dict, "embedding": List[float] (optional)}
Embedding = List[float]  # Dense vector representation
Filter = Dict[str, Any]  # Metadata filter, e.g., {"category": "news", "date": {"$gt": "2023-01-01"}}
RetrievalResult = List[Tuple[Document, float]]  # List of (doc, similarity_score)


class VectorStoreBase(ABC):
    """
    Abstract base class defining a unified, provider-agnostic interface for vector stores.
    Acts as a facade over different vector databases (e.g., FAISS, Pinecone, Chroma, Weaviate, Qdrant, Milvus).
    Concrete subclasses implement these methods for specific backends while maintaining identical call signatures.
    Assumes embeddings are handled externally (e.g., via an embedder model) unless otherwise specified.
    """

    # =====================================================================
    # Initialization and Configuration
    # =====================================================================

    @abstractmethod
    def __init__(
        self,
        index_name: Optional[str] = None,
        embedding_dim: Optional[int] = None,
        metric: str = "cosine",
        **kwargs,
    ) -> None:
        """
        Initialize the vector store instance.

        Args:
            index_name (str, optional): Name of the index or collection to use/create.
            embedding_dim (int, optional): Dimensionality of vectors (required for some stores).
            metric (str): Similarity metric ("cosine", "euclidean", "dot", "manhattan").
            **kwargs: Provider-specific config (e.g., api_key, host, persistence_path).
        """
        pass

    @abstractmethod
    def from_documents(
        cls,
        documents: List[Document],
        embedding_model: Any,
        index_name: Optional[str] = None,
        **kwargs,
    ) -> "VectorStoreBase":
        """
        Class method to create and populate a vector store from documents.

        Args:
            documents (List[Document]): List of docs with 'content' and optional 'metadata'.
            embedding_model (Any): Model or function to generate embeddings from text.
            index_name (str, optional): Index to create.
            **kwargs: Init kwargs + add_documents options (e.g., batch_size).

        Returns:
            VectorStoreBase: Initialized and populated instance.
        """
        pass

    # =====================================================================
    # Indexing Operations
    # =====================================================================

    @abstractmethod
    def add_documents(
        self,
        documents: List[Document],
        *,
        embeddings: Optional[List[Embedding]] = None,
        ids: Optional[List[str]] = None,
        batch_size: int = 100,
        **kwargs,
    ) -> List[str]:
        """
        Add documents to the store, generating or using provided embeddings.

        Args:
            documents (List[Document]): Docs with 'content' and 'metadata'.
            embeddings (List[Embedding], optional): Pre-computed vectors; if None, generate via integrated embedder.
            ids (List[str], optional): Custom IDs; auto-generated if None.
            batch_size (int): Batch size for insertion.
            **kwargs: Namespace, ttl, overwrite_existing.

        Returns:
            List[str]: Inserted document IDs.
        """
        pass

    @abstractmethod
    def add_embeddings(
        self,
        embeddings: List[Embedding],
        *,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        batch_size: int = 100,
        **kwargs,
    ) -> List[str]:
        """
        Add raw embeddings with optional metadata.

        Args:
            embeddings (List[Embedding]): Vectors to insert.
            metadatas (List[dict], optional): Per-vector metadata.
            ids (List[str], optional): Custom IDs.
            batch_size (int): Insertion batch size.
            **kwargs: Additional provider options.

        Returns:
            List[str]: Inserted IDs.
        """
        pass

    @abstractmethod
    def update_documents(
        self,
        ids: List[str],
        documents: Optional[List[Document]] = None,
        embeddings: Optional[List[Embedding]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> bool:
        """
        Update existing documents by ID.

        Args:
            ids (List[str]): IDs to update.
            documents (List[Document], optional): New content/metadata.
            embeddings (List[Embedding], optional): New vectors.
            metadatas (List[dict], optional): Updated metadata.
            **kwargs: Partial update flags.

        Returns:
            bool: Success.
        """
        pass

    @abstractmethod
    def delete_documents(
        self,
        ids: Optional[List[str]] = None,
        filter: Optional[Filter] = None,
        **kwargs,
    ) -> bool:
        """
        Delete documents by IDs or filter.

        Args:
            ids (List[str], optional): Specific IDs to delete.
            filter (Filter, optional): Metadata filter for deletion.
            **kwargs: Namespace, soft_delete.

        Returns:
            bool: Success.
        """
        pass

    @abstractmethod
    def upsert_documents(
        self,
        documents: List[Document],
        embeddings: Optional[List[Embedding]] = None,
        ids: List[str] = None,
        **kwargs,
    ) -> List[str]:
        """
        Insert or update documents (upsert).

        Args:
            documents (List[Document]): Docs to upsert.
            embeddings (List[Embedding], optional): Vectors.
            ids (List[str]): Corresponding IDs.
            **kwargs: Batch size, conflict resolution.

        Returns:
            List[str]: Affected IDs.
        """
        pass

    # =====================================================================
    # Retrieval Operations
    # =====================================================================

    @abstractmethod
    def similarity_search(
        self,
        query: Union[str, Embedding],
        *,
        k: int = 5,
        filter: Optional[Filter] = None,
        score_threshold: Optional[float] = None,
        **kwargs,
    ) -> RetrievalResult:
        """
        Perform similarity search using query text or embedding.

        Args:
            query (str | Embedding): Query text (auto-embedded) or vector.
            k (int): Number of results.
            filter (Filter, optional): Metadata filter.
            score_threshold (float, optional): Min similarity score.
            **kwargs: Fetch_vector, include_metadata.

        Returns:
            List[Tuple[Document, float]]: Results with scores.
        """
        pass

    @abstractmethod
    def max_marginal_relevance_search(
        self,
        query: Union[str, Embedding],
        *,
        k: int = 5,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        filter: Optional[Filter] = None,
        **kwargs,
    ) -> RetrievalResult:
        """
        MMR search for diversity in results.

        Args:
            query (str | Embedding): Query.
            k (int): Final results.
            fetch_k (int): Initial candidates.
            lambda_mult (float): Diversity balance (0=diversity, 1=relevance).
            filter (Filter, optional): Metadata filter.
            **kwargs: Score threshold.

        Returns:
            List[Tuple[Document, float]]: Diverse results.
        """
        pass

    @abstractmethod
    def hybrid_search(
        self,
        query: str,
        *,
        k: int = 5,
        alpha: float = 0.5,  # Weight between dense (1.0) and sparse (0.0)
        filter: Optional[Filter] = None,
        **kwargs,
    ) -> RetrievalResult:
        """
        Hybrid dense + sparse (keyword) search.

        Args:
            query (str): Query text.
            k (int): Results.
            alpha (float): Dense vs sparse weight.
            filter (Filter, optional): Filter.
            **kwargs: Sparse method (BM25), reranker.

        Returns:
            List[Tuple[Document, float]]: Fused results.
        """
        pass

    @abstractmethod
    def get_documents(
        self,
        ids: List[str],
        *,
        include_embeddings: bool = False,
        **kwargs,
    ) -> List[Document]:
        """
        Retrieve documents by IDs.

        Args:
            ids (List[str]): Document IDs.
            include_embeddings (bool): Return vectors.
            **kwargs: Batch size.

        Returns:
            List[Document]: Matching documents.
        """
        pass

    # =====================================================================
    # Async Variants
    # =====================================================================

    @abstractmethod
    async def aadd_documents(self, **kwargs) -> List[str]:
        """
        Async version of add_documents.

        Args:
            **kwargs: Same as add_documents.

        Returns:
            List[str]: Inserted IDs.
        """
        pass

    @abstractmethod
    async def asimilarity_search(self, **kwargs) -> RetrievalResult:
        """
        Async version of similarity_search.

        Args:
            **kwargs: Same as similarity_search.

        Returns:
            RetrievalResult: Results.
        """
        pass

    @abstractmethod
    async def amax_marginal_relevance_search(self, **kwargs) -> RetrievalResult:
        """
        Async version of max_marginal_relevance_search.

        Args:
            **kwargs: Same as max_marginal_relevance_search.

        Returns:
            RetrievalResult: Results.
        """
        pass

    # =====================================================================
    # Index Management
    # =====================================================================

    @abstractmethod
    def create_index(
        self,
        index_name: str,
        embedding_dim: int,
        metric: str = "cosine",
        **kwargs,
    ) -> bool:
        """
        Create a new index/collection.

        Args:
            index_name (str): Name.
            embedding_dim (int): Vector size.
            metric (str): Similarity metric.
            **kwargs: Shards, replicas, pod_type.

        Returns:
            bool: Success.
        """
        pass

    @abstractmethod
    def delete_index(self, index_name: str, **kwargs) -> bool:
        """
        Delete an index/collection.

        Args:
            index_name (str): Name.
            **kwargs: Cascade delete.

        Returns:
            bool: Success.
        """
        pass

    @abstractmethod
    def list_indexes(self, **kwargs) -> List[str]:
        """
        List available indexes/collections.

        Args:
            **kwargs: Namespace.

        Returns:
            List[str]: Index names.
        """
        pass

    @abstractmethod
    def get_index_stats(self, index_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Get statistics for an index.

        Args:
            index_name (str, optional): Specific index; current if None.
            **kwargs: Detailed flags.

        Returns:
            dict: {'document_count': int, 'storage_size': int, ...}
        """
        pass

    # =====================================================================
    # Utility Methods
    # =====================================================================

    @abstractmethod
    def embed_query(self, query: str, **kwargs) -> Embedding:
        """
        Generate embedding for a query using integrated embedder.

        Args:
            query (str): Text to embed.
            **kwargs: Model-specific params.

        Returns:
            Embedding: Vector.
        """
        pass

    @abstractmethod
    def search_with_embedding(
        self,
        embedding: Embedding,
        *,
        k: int = 5,
        filter: Optional[Filter] = None,
        **kwargs,
    ) -> RetrievalResult:
        """
        Search using a pre-computed embedding.

        Args:
            embedding (Embedding): Query vector.
            k (int): Results.
            filter (Filter, optional): Filter.
            **kwargs: Score threshold.

        Returns:
            RetrievalResult: Results.
        """
        pass

    @abstractmethod
    def count_documents(
        self,
        filter: Optional[Filter] = None,
        **kwargs,
    ) -> int:
        """
        Count documents matching filter.

        Args:
            filter (Filter, optional): Criteria.
            **kwargs: Namespace.

        Returns:
            int: Count.
        """
        pass

    @abstractmethod
    def backup(self, path: str, **kwargs) -> bool:
        """
        Backup the store to a file/path.

        Args:
            path (str): Backup location.
            **kwargs: Compression, incremental.

        Returns:
            bool: Success.
        """
        pass

    @abstractmethod
    def restore(self, path: str, **kwargs) -> bool:
        """
        Restore from a backup.

        Args:
            path (str): Backup source.
            **kwargs: Overwrite, selective.

        Returns:
            bool: Success.
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        Check if the vector store is reachable and healthy.

        Returns:
            bool: True if healthy.
        """
        pass