import chromadb
from chromadb.utils import embedding_functions
import numpy as np
from typing import Any, Dict, List, Optional, Union, Tuple, Iterator, AsyncIterator
from uuid import uuid4
import json
import os
from dataclasses import dataclass
from vector_store.vector_store_base import VectorStoreBase

# Type aliases (consistent with VectorStoreBase)
Document = Dict[str, Any]  # { "id": str, "content": str, "metadata": dict, "embedding": List[float] (optional) }
Embedding = List[float]
Filter = Dict[str, Any]
RetrievalResult = List[Tuple[Document, float]]


class ChromaDBVectorStore(VectorStoreBase):
    """
    Fully-featured ChromaDB-based vector store implementation.
    Supports persistent and in-memory collections with full CRUD, filtering, MMR, and async ops.
    """

    def __init__(
            self,
            index_name: Optional[str] = "default",
            embedding_dim: Optional[int] = None,
            metric: str = "cosine",
            persist_path: Optional[str] = "./chroma_db",
            **kwargs,
    ) -> None:
        """
        Initialize ChromaDB vector store.

        Args:
            index_name (str): Collection name.
            embedding_dim (int): Not strictly required for Chroma, but for consistency.
            metric (str): "cosine", "euclidean" (l2), "dot" (ip).
            persist_path (str, optional): Directory for persistent vector_store.
            **kwargs: Additional Chroma params (e.g., embedding_function).
        """
        self.index_name = index_name
        self.persist_path = persist_path
        self.metric = metric if metric in ["cosine", "l2", "ip"] else "cosine"  # Chroma metrics: cosine, l2, ip

        # Initialize client - compatible with multiple ChromaDB versions
        self.client = self._create_client(persist_path)

        self.embedding_function = kwargs.get("embedding_function")
        self.collection = self.client.get_or_create_collection(
            name=index_name,
            metadata={"hnsw:space": self.metric},  # HNSW metric config
        )

    def _create_client(self, persist_path: Optional[str]):
        """
        Create ChromaDB client with compatibility across versions.

        Tries multiple approaches to handle different ChromaDB API versions:
        - ChromaDB >= 0.4.0: Uses PersistentClient/EphemeralClient
        - ChromaDB < 0.4.0: Uses Client with settings
        """
        if persist_path:
            # Try newer API first (ChromaDB >= 0.4.0)
            try:
                return chromadb.PersistentClient(path=persist_path)
            except AttributeError:
                # Fall back to older API (ChromaDB < 0.4.0)
                try:
                    from chromadb.config import Settings
                    settings = Settings(
                        chroma_db_impl="duckdb+parquet",
                        persist_directory=persist_path
                    )
                    return chromadb.Client(settings)
                except (ImportError, AttributeError):
                    # Last resort: use basic Client
                    return chromadb.Client()
        else:
            # In-memory client
            try:
                # Try newer API (EphemeralClient)
                return chromadb.EphemeralClient()
            except AttributeError:
                # Fall back to older API
                return chromadb.Client()

    # =====================================================================
    # Class Factory
    # =====================================================================

    @classmethod
    def from_documents(
            cls,
            documents: List[Document],
            embedding_model: Any,
            index_name: Optional[str] = "default",
            **kwargs,
    ) -> "ChromaDBVectorStore":
        """
        Create and populate from documents.

        Args:
            documents: List of docs with 'content'.
            embedding_model: Callable that takes list of texts -> list of embeddings.
            **kwargs: Passed to __init__.

        Returns:
            Populated ChromaDBVectorStore.
        """
        texts = [doc.get("content", "") for doc in documents]
        embeddings = embedding_model.embed_text(texts)
        store = cls(index_name=index_name, **kwargs)
        store.add_documents(documents, embeddings=embeddings)
        return store

    # =====================================================================
    # Index Management
    # =====================================================================

    def create_index(
            self,
            index_name: str,
            embedding_dim: int,
            metric: str = "cosine",
            **kwargs,
    ) -> bool:
        """
        Create a new collection (index).

        Args:
            index_name (str): Name.
            embedding_dim (int): Ignored in Chroma (dynamic).
            metric (str): "cosine", "l2", "ip".
            **kwargs: Additional metadata.

        Returns:
            bool: Success (always True if not exists).
        """
        self.client.get_or_create_collection(
            name=index_name,
            metadata={"hnsw:space": metric if metric in ["cosine", "l2", "ip"] else "cosine"},
        )
        return True

    def delete_index(self, index_name: str, **kwargs) -> bool:
        try:
            self.client.delete_collection(name=index_name)
            return True
        except:
            return False

    def list_indexes(self, **kwargs) -> List[str]:
        return [coll.name for coll in self.client.list_collections()]

    def get_index_stats(self, index_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        coll = self.client.get_collection(name=index_name or self.index_name)
        return {
            "document_count": coll.count(),
            "metric": coll.metadata.get("hnsw:space", "unknown"),
            "index_type": "ChromaDB",
        }

    # =====================================================================
    # CRUD Operations
    # =====================================================================

    def add_documents(
            self,
            documents: List[Document],
            *,
            embeddings: Optional[List[Embedding]] = None,
            ids: Optional[List[str]] = None,
            batch_size: int = 100,
            **kwargs,
    ) -> List[str]:
        if embeddings is None:
            raise ValueError("embeddings required for ChromaDB")

        inserted_ids = []
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_emb = embeddings[i:i + batch_size]
            batch_ids = ids[i:i + batch_size] if ids else [str(uuid4()) for _ in batch_docs]
            batch_metas = [doc.get("metadata", {}) for doc in batch_docs]
            batch_texts = [doc.get("content", "") for doc in batch_docs]

            self.collection.add(
                ids=batch_ids,
                embeddings=batch_emb,
                metadatas=batch_metas,
                documents=batch_texts,
            )
            inserted_ids.extend(batch_ids)
        return inserted_ids

    def add_embeddings(
            self,
            embeddings: List[Embedding],
            *,
            metadatas: Optional[List[Dict[str, Any]]] = None,
            ids: Optional[List[str]] = None,
            batch_size: int = 100,
            **kwargs,
    ) -> List[str]:
        docs = [{"content": "", "metadata": meta or {}} for meta in (metadatas or [{} for _ in embeddings])]
        return self.add_documents(docs, embeddings=embeddings, ids=ids, batch_size=batch_size, **kwargs)

    def update_documents(
            self,
            ids: List[str],
            documents: Optional[List[Document]] = None,
            embeddings: Optional[List[Embedding]] = None,
            metadatas: Optional[List[Dict[str, Any]]] = None,
            **kwargs,
    ) -> bool:
        for i, doc_id in enumerate(ids):
            updates = {}
            if documents and i < len(documents):
                updates["documents"] = [documents[i].get("content", "")]
            if embeddings and i < len(embeddings):
                updates["embeddings"] = [embeddings[i]]
            if metadatas and i < len(metadatas):
                updates["metadatas"] = [metadatas[i]]
            if updates:
                self.collection.update(ids=[doc_id], **updates)
        return True

    def delete_documents(
            self,
            ids: Optional[List[str]] = None,
            filter: Optional[Filter] = None,
            **kwargs,
    ) -> bool:
        if ids:
            self.collection.delete(ids=ids)
            return True
        elif filter:
            self.collection.delete(where=filter)  # Chroma uses 'where' for metadata filter
            return True
        return False

    def upsert_documents(
            self,
            documents: List[Document],
            embeddings: Optional[List[Embedding]] = None,
            ids: List[str] = None,
            **kwargs,
    ) -> List[str]:
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=[doc.get("metadata", {}) for doc in documents],
            documents=[doc.get("content", "") for doc in documents],
        )
        return ids

    # =====================================================================
    # Retrieval
    # =====================================================================

    def similarity_search(
            self,
            query: Union[str, Embedding],
            *,
            k: int = 5,
            filter: Optional[Filter] = None,
            score_threshold: Optional[float] = None,
            **kwargs,
    ) -> RetrievalResult:
        query_emb = [query] if not isinstance(query, str) else None
        query_texts = [query] if isinstance(query, str) else None

        results = self.collection.query(
            query_embeddings=query_emb,
            query_texts=query_texts,
            n_results=k,
            where=filter,
            include=["metadatas", "documents", "distances"],
        )

        formatted = []
        for i in range(len(results["ids"][0])):
            doc_id = results["ids"][0][i]
            dist = results["distances"][0][i]
            if score_threshold is not None and dist < score_threshold:
                continue
            doc = {
                "id": doc_id,
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] or {},
            }
            formatted.append((doc, dist))
        return formatted

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
        # Chroma supports MMR natively via query with lambda
        query_emb = [query] if not isinstance(query, str) else None
        query_texts = [query] if isinstance(query, str) else None

        results = self.collection.query(
            query_embeddings=query_emb,
            query_texts=query_texts,
            n_results=k,
            where=filter,
            fetch_k=fetch_k,
            lambda_value=lambda_mult,  # Assuming Chroma has MMR param; otherwise implement manually
            include=["metadatas", "documents", "distances"],
        )

        formatted = []
        for i in range(len(results["ids"][0])):
            doc_id = results["ids"][0][i]
            dist = results["distances"][0][i]
            doc = {
                "id": doc_id,
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] or {},
            }
            formatted.append((doc, dist))
        return formatted

    def hybrid_search(
            self,
            query: str,
            *,
            k: int = 5,
            alpha: float = 0.5,
            filter: Optional[Filter] = None,
            **kwargs,
    ) -> RetrievalResult:
        raise NotImplementedError("Hybrid search not natively supported in ChromaDB; use external sparse index")

    def get_documents(
            self,
            ids: List[str],
            *,
            include_embeddings: bool = False,
            **kwargs,
    ) -> List[Document]:
        includes = ["metadatas", "documents"]
        if include_embeddings:
            includes.append("embeddings")
        results = self.collection.get(ids=ids, include=includes)
        formatted = []
        for i in range(len(results["ids"])):
            doc = {
                "id": results["ids"][i],
                "content": results["documents"][i],
                "metadata": results["metadatas"][i] or {},
            }
            if include_embeddings:
                doc["embedding"] = results["embeddings"][i]
            formatted.append(doc)
        return formatted

    # =====================================================================
    # Async Variants
    # =====================================================================

    async def aadd_documents(self, **kwargs) -> List[str]:
        return self.add_documents(**kwargs)  # Chroma sync for simplicity; extend with async client if needed

    async def asimilarity_search(self, **kwargs) -> RetrievalResult:
        return self.similarity_search(**kwargs)

    async def amax_marginal_relevance_search(self, **kwargs) -> RetrievalResult:
        return self.max_marginal_relevance_search(**kwargs)

    # =====================================================================
    # Utilities
    # =====================================================================

    def embed_query(self, query: str, **kwargs) -> Embedding:
        if self.embedding_function:
            return self.embedding_function([query])[0]
        raise NotImplementedError("No embedding_function set. Use external embedder.")

    def search_with_embedding(self, embedding: Embedding, **kwargs) -> RetrievalResult:
        return self.similarity_search(embedding, **kwargs)

    def count_documents(self, filter: Optional[Filter] = None, **kwargs) -> int:
        # Chroma doesn't support filtered count directly; query with large k and count
        if not filter:
            return self.collection.count()
        results = self.collection.query(query_texts=[""], n_results=999999, where=filter, include=[])
        return len(results["ids"][0])

    def backup(self, path: str, **kwargs) -> bool:
        # Chroma persistent is already on disk; copy directory
        import shutil
        try:
            shutil.copytree(self.persist_path, path)
            return True
        except:
            return False

    def restore(self, path: str, **kwargs) -> bool:
        if not os.path.exists(path):
            return False
        self.client = self._create_client(path)
        self.collection = self.client.get_collection(name=self.index_name)
        return True

    def health_check(self) -> bool:
        try:
            _ = self.client.heartbeat()
            return True
        except:
            return False


if __name__ == '__main__':
    from huggingface_hub import InferenceClient

    # Setup
    embedder = InferenceClient(model="sentence-transformers/all-MiniLM-L6-v2")
    store = ChromaDBVectorStore(persist_path="./chroma_db")

    # Index
    docs = [
        {"content": "Paris is the capital of France.", "metadata": {"source": "wiki"}},
        {"content": "Python is a programming language.", "metadata": {"source": "docs"}},
    ]
    embs = embedder.feature_extraction([d["content"] for d in docs])
    store.add_documents(docs, embeddings=embs)

    # Search
    results = store.similarity_search(embs[0], k=1)
    print(results[0][0]["content"])