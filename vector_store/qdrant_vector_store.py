from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import Any, Dict, List, Optional, Union, Tuple
from uuid import uuid4

from vector_store.vector_store_base import VectorStoreBase

class QdrantVectorStore(VectorStoreBase):
    """
    Qdrant vector database implementation (local or cloud).
    Supports payload filtering, MMR, and payload indexing.
    """

    def __init__(
        self,
        index_name: Optional[str] = "collection",
        embedding_dim: Optional[int] = None,
        metric: str = "cosine",
        host: str = "localhost",
        port: int = 6333,
        **kwargs,
    ) -> None:
        self.client = QdrantClient(host=host, port=port, **kwargs)
        self.collection_name = index_name

        if not self.client.collection_exists(index_name):
            self.client.create_collection(
                collection_name=index_name,
                vectors_config=models.VectorParams(
                    size=embedding_dim,
                    distance=models.Distance.COSINE if metric == "cosine" else models.Distance.EUCLID
                )
            )

    def add_documents(
        self,
        documents: List[Document],
        *,
        embeddings: Optional[List[Embedding]] = None,
        ids: Optional[List[str]] = None,
        **kwargs,
    ) -> List[str]:
        if embeddings is None:
            raise ValueError("embeddings required")

        points = []
        for i, (doc, emb) in enumerate(zip(documents, embeddings)):
            point_id = ids[i] if ids and i < len(ids) else str(uuid4())
            points.append(models.PointStruct(
                id=point_id,
                vector=emb,
                payload={
                    "content": doc.get("content", ""),
                    "metadata": doc.get("metadata", {})
                }
            ))
        self.client.upsert(collection_name=self.collection_name, points=points)
        return [p.id for p in points]

    def similarity_search(
        self,
        query: Union[str, Embedding],
        *,
        k: int = 5,
        filter: Optional[Filter] = None,
        **kwargs,
    ) -> RetrievalResult:
        if isinstance(query, str):
            raise ValueError("Embedding required")

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query,
            query_filter=self._build_filter(filter) if filter else None,
            limit=k
        )
        return [
            ({
                "id": r.id,
                "content": r.payload.get("content", ""),
                "metadata": r.payload.get("metadata", {})
            }, r.score)
            for r in results
        ]

    def _build_filter(self, filter_dict: Filter):
        conditions = []
        for k, v in filter_dict.items():
            conditions.append(models.FieldCondition(
                key=f"metadata.{k}",
                match=models.MatchValue(value=v)
            ))
        return models.Filter(must=conditions)