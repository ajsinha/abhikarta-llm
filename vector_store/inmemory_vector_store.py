import numpy as np
from typing import Any, Dict, List, Optional, Union, Tuple, Iterator, AsyncIterator
from uuid import uuid4
from dataclasses import dataclass
import asyncio
import os
from vector_store.vector_store_base import VectorStoreBase

# Type aliases
Document = Dict[str, Any]  # { "id": str, "content": str, "metadata": dict, "embedding": List[float] }
Embedding = List[float]
Filter = Dict[str, Any]
RetrievalResult = List[Tuple[Document, float]]


@dataclass
class InMemoryIndex:
    """Internal structure for in-memory vector storage."""
    documents: Dict[str, Document]
    embeddings: np.ndarray  # shape: (n_docs, embedding_dim)
    ids: List[str]
    embedding_dim: int
    metric: str


class InMemoryVectorStore(VectorStoreBase):
    """
    Fully in-memory vector store implementation.
    Fast, lightweight, ideal for prototyping, testing, or small-scale RAG.
    Supports filtering, MMR, async (via sync simulation), and full CRUD.
    """

    def __init__(
        self,
        index_name: Optional[str] = "default",
        embedding_dim: Optional[int] = None,
        metric: str = "cosine",
        persist_path: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Initialize in-memory store.

        Args:
            index_name (str): Logical name (for multi-index support).
            embedding_dim (int): Vector size (required for new index).
            metric (str): "cosine", "euclidean", "dot".
            persist_path (str): Not used.
            **kwargs: Optional initial data.
        """
        self.index_name = index_name
        self.embedding_dim = embedding_dim
        self.metric = metric.lower()
        self._indexes: Dict[str, InMemoryIndex] = {}
        self._current_index = None

        if embedding_dim is not None:
            self.create_index(index_name, embedding_dim, metric)

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
    ) -> "InMemoryVectorStore":
        """
        Create and populate from documents.

        Args:
            documents: List of docs with 'content'.
            embedding_model: Callable: list[str] -> list[Embedding].
            **kwargs: Passed to __init__.

        Returns:
            Populated store.
        """
        texts = [doc.get("content", "") for doc in documents]
        embeddings = embedding_model.embed_text(texts)
        store = cls(index_name=index_name, embedding_dim=len(embeddings[0]), **kwargs)
        store.add_documents(documents, embeddings=embeddings)
        return store

    # =====================================================================
    # Index Management
    # =====================================================================

    def _get_or_create_index(self, index_name: Optional[str] = None) -> InMemoryIndex:
        name = index_name or self.index_name
        if name not in self._indexes:
            raise ValueError(f"Index '{name}' not found.")
        return self._indexes[name]

    def create_index(
        self,
        index_name: str,
        embedding_dim: int,
        metric: str = "cosine",
        **kwargs,
    ) -> bool:
        if index_name in self._indexes:
            return False
        self._indexes[index_name] = InMemoryIndex(
            documents={},
            embeddings=np.zeros((0, embedding_dim), dtype=np.float32),
            ids=[],
            embedding_dim=embedding_dim,
            metric=metric.lower(),
        )
        if index_name == self.index_name:
            self._current_index = self._indexes[index_name]
        return True

    def delete_index(self, index_name: str, **kwargs) -> bool:
        if index_name not in self._indexes:
            return False
        del self._indexes[index_name]
        if self._current_index and self._current_index == self._indexes.get(index_name):
            self._current_index = None
        return True

    def list_indexes(self, **kwargs) -> List[str]:
        return list(self._indexes.keys())

    def get_index_stats(self, index_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        idx = self._get_or_create_index(index_name)
        return {
            "document_count": len(idx.documents),
            "embedding_dim": idx.embedding_dim,
            "metric": idx.metric,
            "index_type": "InMemory",
        }

    # =====================================================================
    # CRUD Operations
    # =====================================================================

    def _normalize(self, vec: np.ndarray) -> np.ndarray:
        if self.metric == "cosine":
            norm = np.linalg.norm(vec, axis=1, keepdims=True)
            norm[norm == 0] = 1.0
            return vec / norm
        return vec

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
            raise ValueError("embeddings required")

        idx = self._get_or_create_index()
        new_embs = np.array(embeddings, dtype=np.float32)
        new_embs = self._normalize(new_embs)

        inserted_ids = []
        for doc, emb in zip(documents, new_embs):
            doc_id = (ids.pop(0) if ids else str(uuid4()))
            idx.documents[doc_id] = {
                "id": doc_id,
                "content": doc.get("content", ""),
                "metadata": doc.get("metadata", {}),
                "embedding": emb.tolist(),
            }
            idx.ids.append(doc_id)
            inserted_ids.append(doc_id)

        idx.embeddings = np.vstack([idx.embeddings, new_embs]) if idx.embeddings.size else new_embs
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
        docs = [{"content": "", "metadata": m or {}} for m in (metadatas or [{} for _ in embeddings])]
        return self.add_documents(docs, embeddings=embeddings, ids=ids, batch_size=batch_size, **kwargs)

    def update_documents(
        self,
        ids: List[str],
        documents: Optional[List[Document]] = None,
        embeddings: Optional[List[Embedding]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> bool:
        idx = self._get_or_create_index()
        for i, doc_id in enumerate(ids):
            if doc_id not in idx.documents:
                continue
            if documents and i < len(documents):
                idx.documents[doc_id]["content"] = documents[i].get("content", idx.documents[doc_id]["content"])
            if metadatas and i < len(metadatas):
                idx.documents[doc_id]["metadata"] = metadatas[i]
            if embeddings and i < len(embeddings):
                new_emb = self._normalize(np.array([embeddings[i]], dtype=np.float32))
                pos = idx.ids.index(doc_id)
                idx.embeddings[pos] = new_emb
                idx.documents[doc_id]["embedding"] = new_emb[0].tolist()
        return True

    def delete_documents(
        self,
        ids: Optional[List[str]] = None,
        filter: Optional[Filter] = None,
        **kwargs,
    ) -> bool:
        idx = self._get_or_create_index()
        to_delete = []

        if ids:
            to_delete = [i for i in ids if i in idx.documents]
        elif filter:
            to_delete = [
                doc_id for doc_id, doc in idx.documents.items()
                if self._matches_filter(doc["metadata"], filter)
            ]

        for doc_id in to_delete:
            pos = idx.ids.index(doc_id)
            idx.embeddings = np.delete(idx.embeddings, pos, axis=0)
            idx.ids.pop(pos)
            idx.documents.pop(doc_id)

        return len(to_delete) > 0

    def upsert_documents(
        self,
        documents: List[Document],
        embeddings: Optional[List[Embedding]] = None,
        ids: List[str] = None,
        **kwargs,
    ) -> List[str]:
        existing = [i for i in ids if i in self._get_or_create_index().documents]
        self.delete_documents(ids=existing)
        new_ids = [i for i in ids if i not in existing]
        new_docs = [documents[ids.index(i)] for i in new_ids]
        new_embs = [embeddings[ids.index(i)] for i in new_ids] if embeddings else None
        return self.add_documents(new_docs, embeddings=new_embs, ids=new_ids, **kwargs) + existing

    # =====================================================================
    # Retrieval
    # =====================================================================

    def _matches_filter(self, metadata: Dict, filter_dict: Filter) -> bool:
        for key, value in filter_dict.items():
            if key not in metadata:
                return False
            if isinstance(value, dict):
                for op, val in value.items():
                    if op == "$eq" and metadata[key] != val:
                        return False
                    elif op == "$gt" and not (metadata[key] > val):
                        return False
                    # Add more operators as needed
            elif metadata[key] != value:
                return False
        return True

    def _compute_distances(self, query_vec: np.ndarray, candidates: np.ndarray) -> np.ndarray:
        if self.metric == "cosine":
            return 1 - np.dot(candidates, query_vec.T).flatten()
        elif self.metric == "euclidean":
            return np.linalg.norm(candidates - query_vec, axis=1)
        else:  # dot
            return -np.dot(candidates, query_vec.T).flatten()

    def similarity_search(
        self,
        query: Union[str, Embedding],
        *,
        k: int = 5,
        filter: Optional[Filter] = None,
        score_threshold: Optional[float] = None,
        **kwargs,
    ) -> RetrievalResult:
        if isinstance(query, str):
            raise ValueError("Pre-computed embedding required")

        idx = self._get_or_create_index()
        query_vec = self._normalize(np.array([query], dtype=np.float32))

        # Filter candidates
        candidate_ids = idx.ids
        if filter:
            candidate_ids = [i for i in idx.ids if self._matches_filter(idx.documents[i]["metadata"], filter)]

        if not candidate_ids:
            return []

        candidate_embs = np.array([idx.documents[i]["embedding"] for i in candidate_ids], dtype=np.float32)
        distances = self._compute_distances(query_vec, candidate_embs)

        # Sort and apply threshold
        sorted_idx = np.argsort(distances)
        results = []
        for idx_pos in sorted_idx:
            dist = float(distances[idx_pos])
            if score_threshold is not None and dist > score_threshold:
                continue
            doc_id = candidate_ids[idx_pos]
            results.append((idx.documents[doc_id], dist))
            if len(results) >= k:
                break
        return results

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
        candidates = self.similarity_search(query, k=fetch_k, filter=filter)
        if len(candidates) <= 1:
            return candidates[:k]

        query_vec = np.array(query)
        selected = [candidates[0]]
        candidate_embs = np.array([c[0]["embedding"] for c in candidates[1:]])

        for _ in range(1, k):
            if not candidate_embs.size:
                break
            sim_to_query = 1 - self._compute_distances(np.array([query_vec]), candidate_embs)
            sim_to_selected = np.max(
                [1 - self._compute_distances(np.array([s[0]["embedding"]]), candidate_embs) for s in selected],
                axis=0
            ) if selected else np.zeros(len(candidate_embs))
            mmr = lambda_mult * sim_to_query.flatten() - (1 - lambda_mult) * sim_to_selected
            best_idx = np.argmax(mmr)
            selected.append(candidates[1:][best_idx])
            candidate_embs = np.delete(candidate_embs, best_idx, axis=0)
        return selected

    def hybrid_search(
        self,
        query: str,
        *,
        k: int = 5,
        alpha: float = 0.5,
        filter: Optional[Filter] = None,
        **kwargs,
    ) -> RetrievalResult:
        # Simple keyword fallback
        idx = self._get_or_create_index()
        matches = [
            (doc, 0.0) for doc_id, doc in idx.documents.items()
            if query.lower() in doc["content"].lower() and (not filter or self._matches_filter(doc["metadata"], filter))
        ]
        return matches[:k]

    def get_documents(
        self,
        ids: List[str],
        *,
        include_embeddings: bool = False,
        **kwargs,
    ) -> List[Document]:
        idx = self._get_or_create_index()
        results = []
        for doc_id in ids:
            if doc_id in idx.documents:
                doc = idx.documents[doc_id].copy()
                if not include_embeddings:
                    doc.pop("embedding", None)
                results.append(doc)
        return results

    # =====================================================================
    # Async Variants
    # =====================================================================

    async def aadd_documents(self, **kwargs) -> List[str]:
        return self.add_documents(**kwargs)

    async def asimilarity_search(self, **kwargs) -> RetrievalResult:
        return self.similarity_search(**kwargs)

    async def amax_marginal_relevance_search(self, **kwargs) -> RetrievalResult:
        return self.max_marginal_relevance_search(**kwargs)

    # =====================================================================
    # Utilities
    # =====================================================================

    def embed_query(self, query: str, **kwargs) -> Embedding:
        raise NotImplementedError("Use external embedder")

    def search_with_embedding(self, embedding: Embedding, **kwargs) -> RetrievalResult:
        return self.similarity_search(embedding, **kwargs)

    def count_documents(self, filter: Optional[Filter] = None, **kwargs) -> int:
        idx = self._get_or_create_index()
        if not filter:
            return len(idx.documents)
        return sum(1 for doc in idx.documents.values() if self._matches_filter(doc["metadata"], filter))

    def backup(self, path: str, **kwargs) -> bool:
        import pickle
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
            with open(path, "wb") as f:
                pickle.dump({k: {"documents": v.documents, "ids": v.ids} for k, v in self._indexes.items()}, f)
            return True
        except:
            return False

    def restore(self, path: str, **kwargs) -> bool:
        import pickle
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
            for name, info in data.items():
                if name not in self._indexes:
                    self.create_index(name, self.embedding_dim, self.metric)
                idx = self._indexes[name]
                idx.documents = info["documents"]
                idx.ids = info["ids"]
                idx.embeddings = np.array([doc["embedding"] for doc in idx.documents.values()], dtype=np.float32)
            return True
        except:
            return False

    def health_check(self) -> bool:
        return True

if __name__ == '__main__':
    from huggingface_hub import InferenceClient

    # Setup
    embedder = InferenceClient(model="sentence-transformers/all-MiniLM-L6-v2")
    store = InMemoryVectorStore(embedding_dim=384)

    # Index
    docs = [
        {"content": "Paris is the capital of France.", "metadata": {"source": "wiki"}},
        {"content": "Berlin is the capital of Germany.", "metadata": {"source": "wiki"}},
    ]
    embs = embedder.feature_extraction([d["content"] for d in docs])
    store.add_documents(docs, embeddings=embs)

    # Search
    results = store.similarity_search(embs[0], k=1)
    print(results[0][0]["content"])  # Output: Paris is the capital of France.