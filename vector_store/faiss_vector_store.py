import faiss
import numpy as np
from typing import Any, Dict, List, Optional, Union, Tuple, Iterator, AsyncIterator
from uuid import uuid4
import json
import os
import pickle
from dataclasses import dataclass
from vector_store.vector_store_base import VectorStoreBase

# Type aliases (consistent with VectorStoreBase)
Document = Dict[str, Any]  # { "id": str, "content": str, "metadata": dict, "embedding": List[float] (optional) }
Embedding = List[float]
Filter = Dict[str, Any]
RetrievalResult = List[Tuple[Document, float]]


@dataclass
class FAISSIndex:
    """Internal wrapper for FAISS index and metadata."""
    index: faiss.Index
    documents: Dict[str, Document]  # id -> Document
    embedding_dim: int
    metric: str
    next_id: int = 0


class FAISSVectorStore(VectorStoreBase):
    """
    Fully-featured FAISS-based vector store implementation.
    Supports in-memory and persistent indexing with full CRUD, filtering, MMR, and async ops.
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
        Initialize FAISS vector store.

        Args:
            index_name (str): Logical index name (for multi-index management).
            embedding_dim (int): Vector dimensionality (required for new indexes).
            metric (str): "cosine", "euclidean", "dot".
            persist_path (str, optional): Directory to save/load index.
            **kwargs: Additional FAISS params (e.g., use_gpu=True).
        """
        self.index_name = index_name
        self.persist_path = persist_path
        self._indexes: Dict[str, FAISSIndex] = {}
        self._current_index = None

        if persist_path and os.path.exists(persist_path):
            self._load_from_disk(persist_path)
        elif embedding_dim is not None:
            self.create_index(index_name, embedding_dim, metric, **kwargs)
        else:
            raise ValueError("embedding_dim required for new in-memory index")

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
    ) -> "FAISSVectorStore":
        """
        Create and populate from documents.

        Args:
            documents: List of docs with 'content'.
            embedding_model: Callable that takes text -> embedding.
            **kwargs: Passed to __init__.

        Returns:
            Populated FAISSVectorStore.
        """
        texts = [doc.get("content", "") for doc in documents]
        embeddings = embedding_model.embed_text(texts)
        embedding_dim = len(embeddings[0]) if embeddings else None

        store = cls(index_name=index_name, embedding_dim=embedding_dim, **kwargs)
        store.add_documents(documents, embeddings=embeddings)
        return store

    # =====================================================================
    # Index Management
    # =====================================================================

    def _get_or_create_index(self, index_name: Optional[str] = None) -> FAISSIndex:
        name = index_name or self.index_name
        if name not in self._indexes:
            raise ValueError(f"Index '{name}' not found. Call create_index() first.")
        return self._indexes[name]

    def create_index(
        self,
        index_name: str,
        embedding_dim: int,
        metric: str = "cosine",
        **kwargs,
    ) -> bool:
        """
        Create a new FAISS index.

        Args:
            index_name (str): Name of index.
            embedding_dim (int): Vector size.
            metric (str): Similarity metric.
            **kwargs: FAISS factory string (e.g., "IVF1024,PQ16").

        Returns:
            bool: Success.
        """
        if index_name in self._indexes:
            return False

        factory = kwargs.get("factory")
        if factory:
            index = faiss.index_factory(embedding_dim, factory, faiss.METRIC_INNER_PRODUCT if metric == "cosine" else faiss.METRIC_L2)
        else:
            if metric == "cosine":
                index = faiss.IndexFlatIP(embedding_dim)
            elif metric == "euclidean":
                index = faiss.IndexFlatL2(embedding_dim)
            elif metric == "dot":
                index = faiss.IndexFlatIP(embedding_dim)
            else:
                raise ValueError(f"Unsupported metric: {metric}")

        self._indexes[index_name] = FAISSIndex(
            index=index,
            documents={},
            embedding_dim=embedding_dim,
            metric=metric,
            next_id=0,
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
            "index_type": type(idx.index).__name__,
        }

    # =====================================================================
    # CRUD Operations
    # =====================================================================

    def _normalize_embeddings(self, embeddings: np.ndarray, metric: str) -> np.ndarray:
        if metric == "cosine":
            faiss.normalize_L2(embeddings)
        return embeddings

    def add_documents(
        self,
        documents: List[Document],
        *,
        embeddings: Optional[List[Embedding]] = None,
        ids: Optional[List[str]] = None,
        batch_size: int = 100,
        **kwargs,
    ) -> List[str]:
        idx = self._get_or_create_index()
        if embeddings is None:
            raise ValueError("embeddings required for FAISS")

        embeddings_array = np.array(embeddings).astype('float32')
        embeddings_array = self._normalize_embeddings(embeddings_array, idx.metric)

        inserted_ids = []
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_emb = embeddings_array[i:i + batch_size]
            batch_ids = ids[i:i + batch_size] if ids else None

            for j, (doc, vec) in enumerate(zip(batch_docs, batch_emb)):
                doc_id = batch_ids[j] if batch_ids and batch_ids[j] else str(uuid4())
                idx.documents[doc_id] = {
                    "id": doc_id,
                    "content": doc.get("content", ""),
                    "metadata": doc.get("metadata", {}),
                }
                idx.index.add(np.array([vec]))
                inserted_ids.append(doc_id)

        if self.persist_path:
            self._save_to_disk(self.persist_path)
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
        docs = [
            {"content": "", "metadata": meta or {}} for meta in (metadatas or [])
        ]
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
            if embeddings:
                emb = np.array([embeddings[i]]).astype('float32')
                emb = self._normalize_embeddings(emb, idx.metric)
                faiss_idx = list(idx.documents.keys()).index(doc_id)
                idx.index.remove_ids(np.array([faiss_idx]))
                idx.index.add(emb)
        if self.persist_path:
            self._save_to_disk(self.persist_path)
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

        faiss_ids = [list(idx.documents.keys()).index(did) for did in to_delete if did in idx.documents]
        if faiss_ids:
            idx.index.remove_ids(np.array(faiss_ids))
        for did in to_delete:
            idx.documents.pop(did, None)

        if self.persist_path:
            self._save_to_disk(self.persist_path)
        return len(to_delete) > 0

    def upsert_documents(
        self,
        documents: List[Document],
        embeddings: Optional[List[Embedding]] = None,
        ids: Optional[List[str]] = None,
        **kwargs,
    ) -> List[str]:
        if ids is None:
            raise ValueError("ids required for upsert_documents")
        existing = [i for i in ids if i in self._get_or_create_index().documents]
        new_ids = [i for i in ids if i not in existing]
        new_docs = [documents[ids.index(i)] for i in new_ids]
        new_embs = [embeddings[ids.index(i)] for i in new_ids] if embeddings else None
        self.add_documents(new_docs, embeddings=new_embs, ids=new_ids, **kwargs)
        return ids

    # =====================================================================
    # Retrieval
    # =====================================================================

    def _matches_filter(self, metadata: Dict, filter_dict: Filter) -> bool:
        for key, value in filter_dict.items():
            if key not in metadata:
                return False
            if isinstance(value, dict):
                if not self._matches_filter(metadata[key], value):
                    return False
            elif metadata[key] != value:
                return False
        return True

    def similarity_search(
        self,
        query: Union[str, Embedding],
        *,
        k: int = 5,
        filter: Optional[Filter] = None,
        score_threshold: Optional[float] = None,
        **kwargs,
    ) -> RetrievalResult:
        idx = self._get_or_create_index()
        if isinstance(query, str):
            raise ValueError("FAISS requires pre-computed embeddings. Use embed_query() first.")
        q_vec = np.array([query]).astype('float32')
        q_vec = self._normalize_embeddings(q_vec, idx.metric)

        D, I = idx.index.search(q_vec, k * 2)  # Search more for filtering
        results = []
        doc_ids = list(idx.documents.keys())

        for dist, faiss_id in zip(D[0], I[0]):
            if faiss_id == -1:
                continue
            doc_id = doc_ids[faiss_id]
            doc = idx.documents[doc_id]
            if filter and not self._matches_filter(doc["metadata"], filter):
                continue
            if score_threshold is not None and dist < score_threshold:
                continue
            results.append((doc, float(dist)))
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
        if isinstance(query, str):
            raise ValueError("Embeddings required")
        candidates = self.similarity_search(query, k=fetch_k, filter=filter)
        if not candidates:
            return []

        selected = [candidates[0]]
        query_vec = np.array(query).reshape(1, -1)
        query_vec = self._normalize_embeddings(query_vec, self._get_or_create_index().metric)

        for _ in range(1, k):
            if not candidates:
                break
            mmr_scores = []
            for cand_doc, _ in candidates:
                cand_vec = np.array(cand_doc.get("embedding", [])).reshape(1, -1)
                if cand_vec.size == 0:
                    continue
                sim_to_query = float(np.dot(query_vec, cand_vec.T))
                sim_to_selected = max(
                    np.dot(cand_vec, np.array([c.get("embedding", []) for c, _ in selected]).T).flatten()
                    or [0]
                )
                mmr = lambda_mult * sim_to_query - (1 - lambda_mult) * sim_to_selected
                mmr_scores.append(mmr)
            if not mmr_scores:
                break
            best_idx = np.argmax(mmr_scores)
            selected.append(candidates.pop(best_idx))
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
        raise NotImplementedError("Hybrid search requires external keyword index (e.g., BM25)")

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
    # Async (In-memory sync simulation)
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
        raise NotImplementedError("FAISS does not embed. Use external embedder.")

    def search_with_embedding(self, embedding: Embedding, **kwargs) -> RetrievalResult:
        return self.similarity_search(embedding, **kwargs)

    def count_documents(self, filter: Optional[Filter] = None, **kwargs) -> int:
        idx = self._get_or_create_index()
        if not filter:
            return len(idx.documents)
        return sum(1 for doc in idx.documents.values() if self._matches_filter(doc["metadata"], filter))

    def _save_to_disk(self, path: str):
        os.makedirs(path, exist_ok=True)
        data = {
            "indexes": {
                name: {
                    "documents": idx.documents,
                    "next_id": idx.next_id,
                    "embedding_dim": idx.embedding_dim,
                    "metric": idx.metric,
                } for name, idx in self._indexes.items()
            }
        }
        with open(os.path.join(path, "metadata.json"), "w") as f:
            json.dump(data, f)
        for name, idx in self._indexes.items():
            faiss.write_index(idx.index, os.path.join(path, f"{name}.faiss"))

    def _load_from_disk(self, path: str):
        with open(os.path.join(path, "metadata.json")) as f:
            data = json.load(f)
        for name, info in data["indexes"].items():
            index = faiss.read_index(os.path.join(path, f"{name}.faiss"))
            self._indexes[name] = FAISSIndex(
                index=index,
                documents=info["documents"],
                embedding_dim=info["embedding_dim"],
                metric=info["metric"],
                next_id=info["next_id"],
            )
        if self.index_name in self._indexes:
            self._current_index = self._indexes[self.index_name]

    def backup(self, path: str, **kwargs) -> bool:
        try:
            self._save_to_disk(path)
            return True
        except:
            return False

    def restore(self, path: str, **kwargs) -> bool:
        if not os.path.exists(path):
            return False
        self._load_from_disk(path)
        return True

    def health_check(self) -> bool:
        try:
            for idx in self._indexes.values():
                _ = idx.index.ntotal
            return True
        except:
            return False

if __name__ == '__main__':
    from huggingface_hub import InferenceClient

    # Setup
    embedder = InferenceClient(model="sentence-transformers/all-MiniLM-L6-v2")
    store = FAISSVectorStore(embedding_dim=384, persist_path="./faiss_index")

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