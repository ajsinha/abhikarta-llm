import pinecone
from typing import Any, Dict, List, Optional, Union, Tuple
import numpy as np
from uuid import uuid4
import json
from vector_store.vector_store_base import VectorStoreBase
import os

# Type aliases
Document = Dict[str, Any]
Embedding = List[float]
Filter = Dict[str, Any]
RetrievalResult = List[Tuple[Document, float]]


class PineconeVectorStore(VectorStoreBase):
    """
    Pinecone cloud vector database implementation.
    Fully managed, scalable, supports real-time updates and metadata filtering.
    """

    def __init__(
        self,
        index_name: Optional[str] = "default",
        embedding_dim: Optional[int] = None,
        metric: str = "cosine",
        persist_path: Optional[str] = None,
        api_key: Optional[str] = None,
        environment: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Initialize Pinecone vector store.

        Args:
            index_name (str): Name of the Pinecone index.
            embedding_dim (int): Vector dimension.
            metric (str): "cosine", "euclidean", "dotproduct".
            api_key (str): Pinecone API key.
            environment (str): Pinecone environment (e.g., "us-east1-gcp").
            **kwargs: Additional Pinecone index config.
        """
        pinecone.init(api_key=api_key or os.getenv("PINECONE_API_KEY"), environment=environment or os.getenv("PINECONE_ENV"))
        self.index_name = index_name
        self.metric = metric.lower()

        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=index_name,
                dimension=embedding_dim,
                metric=self.metric,
                **kwargs,
            )
        self.index = pinecone.Index(index_name)

    @classmethod
    def from_documents(
        cls,
        documents: List[Document],
        embedding_model: Any,
        index_name: Optional[str] = "default",
        **kwargs,
    ) -> "PineconeVectorStore":
        texts = [doc.get("content", "") for doc in documents]
        embeddings = embedding_model.embed_text(texts)
        store = cls(index_name=index_name, embedding_dim=len(embeddings[0]), **kwargs)
        store.add_documents(documents, embeddings=embeddings)
        return store

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

        vectors = []
        inserted_ids = []
        for i, (doc, emb) in enumerate(zip(documents, embeddings)):
            doc_id = ids[i] if ids and i < len(ids) else str(uuid4())
            vectors.append((
                doc_id,
                emb,
                doc.get("metadata", {})
            ))
            inserted_ids.append(doc_id)

            if len(vectors) >= batch_size:
                self.index.upsert(vectors=vectors)
                vectors = []

        if vectors:
            self.index.upsert(vectors=vectors)
        return inserted_ids

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

        results = self.index.query(
            vector=query,
            top_k=k,
            filter=filter,
            include_metadata=True,
        )
        formatted = []
        for match in results.matches:
            if score_threshold is not None and match.score < score_threshold:
                continue
            doc = {
                "id": match.id,
                "content": match.metadata.get("_content", ""),
                "metadata": {k: v for k, v in match.metadata.items() if k != "_content"}
            }
            formatted.append((doc, match.score))
        return formatted

    def delete_documents(self, ids: Optional[List[str]] = None, filter: Optional[Filter] = None, **kwargs) -> bool:
        if ids:
            self.index.delete(ids=ids)
        elif filter:
            self.index.delete(filter=filter)
        return True

    def get_documents(self, ids: List[str], **kwargs) -> List[Document]:
        results = self.index.fetch(ids=ids)
        return [
            {
                "id": vid,
                "content": vec.metadata.get("_content", ""),
                "metadata": {k: v for k, v in vec.metadata.items() if k != "_content"}
            }
            for vid, vec in results.vectors.items()
        ]

    def health_check(self) -> bool:
        try:
            self.index.describe_index_stats()
            return True
        except:
            return False