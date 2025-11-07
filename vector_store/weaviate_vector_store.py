import weaviate
from typing import Any, Dict, List, Optional, Union, Tuple
from vector_store.vector_store_base import VectorStoreBase
import uuid

# Type aliases for clarity and consistency
Document = Dict[str, Any]  # {"id": str, "content": str, "metadata": dict, "embedding": List[float] (optional)}
Embedding = List[float]  # Dense vector representation
Filter = Dict[str, Any]  # Metadata filter, e.g., {"category": "news", "date": {"$gt": "2023-01-01"}}
RetrievalResult = List[Tuple[Document, float]]  # List of (doc, similarity_score)

class WeaviateVectorStore(VectorStoreBase):
    """
    Weaviate open-source vector database implementation.
    Supports hybrid search, GraphQL, and schema-based classes.
    """

    def __init__(
        self,
        index_name: Optional[str] = "Document",
        embedding_dim: Optional[int] = None,
        metric: str = "cosine",
        url: str = "http://localhost:8080",
        **kwargs,
    ) -> None:
        self.client = weaviate.Client(url)
        self.class_name = index_name
        if not self.client.schema.exists(self.class_name):
            schema = {
                "class": self.class_name,
                "vectorizer": "none",
                "properties": [
                    {"name": "content", "dataType": ["text"]},
                    {"name": "metadata", "dataType": ["object"]},
                ],
                "vectorIndexConfig": {
                    "distance": metric
                }
            }
            self.client.schema.create_class(schema)

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

        with self.client.batch as batch:
            for doc, emb in zip(documents, embeddings):
                doc_id = ids.pop(0) if ids else str(uuid.uuid4())
                batch.add_data_object(
                    data_object={
                        "content": doc.get("content", ""),
                        "metadata": doc.get("metadata", {})
                    },
                    class_name=self.class_name,
                    uuid=doc_id,
                    vector=emb
                )
        return [str(uuid.uuid4()) for _ in documents]

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

        near_vec = {"vector": query}
        if filter:
            near_vec["where"] = self._build_where(filter)

        results = (
            self.client.query
            .get(self.class_name, ["content", "metadata", "_additional {distance}"])
            .with_near_vector(near_vec)
            .with_limit(k)
            .do()
        )

        formatted = []
        for obj in results["data"]["Get"][self.class_name]:
            dist = obj["_additional"]["distance"]
            doc = {
                "id": obj["_additional"]["id"],
                "content": obj["content"],
                "metadata": obj["metadata"]
            }
            formatted.append((doc, dist))
        return formatted

    def _build_where(self, filter_dict: Filter):
        # Simplified; extend for nested, $or, etc.
        return {"operator": "And", "operands": [
            {"path": [k], "operator": "Equal", "valueText": str(v)} for k, v in filter_dict.items()
        ]}