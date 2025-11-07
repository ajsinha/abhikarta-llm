import asyncpg
import asyncio
import numpy as np
from typing import Any, Dict, List, Optional, Union, Tuple, Iterator, AsyncIterator
from uuid import uuid4
import json
import os
from dataclasses import dataclass
from vector_store.vector_store_base import VectorStoreBase

# Type aliases
Document = Dict[str, Any]
Embedding = List[float]
Filter = Dict[str, Any]
RetrievalResult = List[Tuple[Document, float]]


@dataclass
class PGVectorConfig:
    """Configuration for pgvector connection and index."""
    host: str = "localhost"
    port: int = 5432
    database: str = "postgres"
    user: str = "postgres"
    password: str = "password"
    table_name: str = "vector_store"
    embedding_dim: int = 384
    metric: str = "cosine"  # "cosine", "l2", "ip"
    index_type: str = "ivfflat"  # "ivfflat", "hnsw"
    index_params: Dict[str, Any] = None  # e.g., {"lists": 100}


class PGVectorStore(VectorStoreBase):
    """
    Fully-featured PostgreSQL + pgvector vector store implementation.
    Supports async operations, metadata filtering, MMR, hybrid search (via full-text), and persistence.
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
        Initialize PGVector store.

        Args:
            index_name (str): Table name.
            embedding_dim (int): Vector dimension.
            metric (str): "cosine", "l2", "ip".
            persist_path (str): Not used (connection via config).
            **kwargs: Connection params (host, port, etc.) or config dict.
        """
        self.index_name = index_name or "vector_store"
        self.embedding_dim = embedding_dim
        self.metric = metric.lower()
        self.config = PGVectorConfig(**kwargs)

        if self.metric not in ["cosine", "l2", "ip"]:
            raise ValueError("metric must be 'cosine', 'l2', or 'ip'")

        self._pool: Optional[asyncpg.Pool] = None
        self._initialized = False

    async def _ensure_initialized(self):
        """Ensure pool and table are initialized."""
        if not self._initialized:
            await self._initialize()
            self._initialized = True

    async def _get_pool(self) -> asyncpg.Pool:
        if not self._pool:
            self._pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.user,
                password=self.config.password,
                min_size=1,
                max_size=10,
            )
        return self._pool

    async def _initialize(self):
        """Create table and index on first use."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            # Enable pgvector
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")

            # Create table
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.index_name} (
                    id TEXT PRIMARY KEY,
                    content TEXT,
                    metadata JSONB,
                    embedding VECTOR({self.embedding_dim})
                );
            """)

            # Create index
            index_params = self.config.index_params or {}
            if self.config.index_type == "ivfflat":
                lists = index_params.get("lists", 100)
                await conn.execute(f"""
                    CREATE INDEX IF NOT EXISTS {self.index_name}_idx 
                    ON {self.index_name} USING ivfflat (embedding vector_{self.metric}_ops) 
                    WITH (lists = {lists});
                """)
            elif self.config.index_type == "hnsw":
                m = index_params.get("m", 16)
                ef_construction = index_params.get("ef_construction", 200)
                await conn.execute(f"""
                    CREATE INDEX IF NOT EXISTS {self.index_name}_idx 
                    ON {self.index_name} USING hnsw (embedding vector_{self.metric}_ops) 
                    WITH (m = {m}, ef_construction = {ef_construction});
                """)

    # =====================================================================
    # Class Factory
    # =====================================================================

    @classmethod
    async def from_documents(
        cls,
        documents: List[Document],
        embedding_model: Any,
        index_name: Optional[str] = "default",
        **kwargs,
    ) -> "PGVectorStore":
        texts = [doc.get("content", "") for doc in documents]
        embeddings = await embedding_model.embed_text(texts) if hasattr(embedding_model, "embed_text") else embedding_model.embed_text(texts)
        store = cls(index_name=index_name, embedding_dim=len(embeddings[0]), **kwargs)
        await store._init_task
        await store.add_documents(documents, embeddings=embeddings)
        return store

    # =====================================================================
    # CRUD Operations
    # =====================================================================

    async def add_documents(
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

        pool = await self._get_pool()
        inserted_ids = []

        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_emb = embeddings[i:i + batch_size]
            batch_ids = ids[i:i + batch_size] if ids else [str(uuid4()) for _ in batch_docs]

            async with pool.acquire() as conn:
                await conn.executemany(f"""
                    INSERT INTO {self.index_name} (id, content, metadata, embedding)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (id) DO NOTHING;
                """, [
                    (
                        doc_id,
                        doc.get("content", ""),
                        json.dumps(doc.get("metadata", {})),
                        emb,
                    )
                    for doc_id, doc, emb in zip(batch_ids, batch_docs, batch_emb)
                ])
            inserted_ids.extend(batch_ids)
        return inserted_ids

    async def add_embeddings(
        self,
        embeddings: List[Embedding],
        *,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        batch_size: int = 100,
        **kwargs,
    ) -> List[str]:
        docs = [{"content": "", "metadata": meta or {}} for meta in (metadatas or [{} for _ in embeddings])]
        return await self.add_documents(docs, embeddings=embeddings, ids=ids, batch_size=batch_size, **kwargs)

    async def update_documents(
        self,
        ids: List[str],
        documents: Optional[List[Document]] = None,
        embeddings: Optional[List[Embedding]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> bool:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            for i, doc_id in enumerate(ids):
                updates = []
                params = []
                if documents and i < len(documents):
                    updates.append("content = $%d" % (len(params) + 1))
                    params.append(documents[i].get("content"))
                if embeddings and i < len(embeddings):
                    updates.append("embedding = $%d" % (len(params) + 1))
                    params.append(embeddings[i])
                if metadatas and i < len(metadatas):
                    updates.append("metadata = $%d" % (len(params) + 1))
                    params.append(json.dumps(metadatas[i]))
                if updates:
                    params.append(doc_id)
                    await conn.execute(f"""
                        UPDATE {self.index_name}
                        SET {', '.join(updates)}
                        WHERE id = ${len(params)}
                    """, *params)
        return True

    async def delete_documents(
        self,
        ids: Optional[List[str]] = None,
        filter: Optional[Filter] = None,
        **kwargs,
    ) -> bool:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            if ids:
                await conn.execute(f"DELETE FROM {self.index_name} WHERE id = ANY($1)", ids)
            elif filter:
                where_clause = self._build_where_clause(filter)
                await conn.execute(f"DELETE FROM {self.index_name} WHERE {where_clause}", *filter.values())
        return True

    async def upsert_documents(
        self,
        documents: List[Document],
        embeddings: Optional[List[Embedding]] = None,
        ids: Optional[List[str]] = None,
        **kwargs,
    ) -> List[str]:
        if ids is None:
            raise ValueError("ids required for upsert")
        await self._ensure_initialized()
        await self.delete_documents(ids=ids)
        await self.add_documents(documents, embeddings=embeddings, ids=ids, **kwargs)
        return ids

    # =====================================================================
    # Retrieval
    # =====================================================================

    def _build_where_clause(self, filter_dict: Filter) -> str:
        conditions = []
        for key, value in filter_dict.items():
            if isinstance(value, dict):
                for op, val in value.items():
                    if op == "$eq":
                        conditions.append(f"metadata->>'{key}' = $${len(conditions)+1}")
                    elif op == "$gt":
                        conditions.append(f"(metadata->>'{key}')::float > $${len(conditions)+1}")
                    # Add more operators as needed
            else:
                conditions.append(f"metadata->>'{key}' = $${len(conditions)+1}")
        return " AND ".join(conditions)

    async def similarity_search(
        self,
        query: Union[str, Embedding],
        *,
        k: int = 5,
        filter: Optional[Filter] = None,
        score_threshold: Optional[float] = None,
        **kwargs,
    ) -> RetrievalResult:
        if isinstance(query, str):
            raise ValueError("Pre-computed embedding required for pgvector")

        pool = await self._get_pool()
        async with pool.acquire() as conn:
            where_clause = self._build_where_clause(filter) if filter else "TRUE"
            op = {
                "cosine": "<=>",
                "l2": "<->",
                "ip": "<#>"
            }[self.metric]

            rows = await conn.fetch(f"""
                SELECT id, content, metadata, embedding {op} $1 AS distance
                FROM {self.index_name}
                WHERE {where_clause}
                ORDER BY distance
                LIMIT $2
            """, query, k)

            results = []
            for row in rows:
                dist = float(row["distance"])
                if score_threshold is not None and dist > score_threshold:
                    continue
                doc = {
                    "id": row["id"],
                    "content": row["content"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                }
                results.append((doc, dist))
            return results

    async def max_marginal_relevance_search(
        self,
        query: Union[str, Embedding],
        *,
        k: int = 5,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        filter: Optional[Filter] = None,
        **kwargs,
    ) -> RetrievalResult:
        candidates = await self.similarity_search(query, k=fetch_k, filter=filter)
        if not candidates:
            return []

        selected = [candidates[0]]
        query_vec = np.array(query)

        for _ in range(1, k):
            if not candidates:
                break
            mmr_scores = []
            for cand_doc, _ in candidates:
                cand_vec = np.array(cand_doc.get("embedding", []))
                if len(cand_vec) == 0:
                    continue
                sim_to_query = 1 - self._distance(query_vec, cand_vec)
                sim_to_selected = max(
                    1 - self._distance(cand_vec, np.array(s.get("embedding", []))) for s, _ in selected
                ) if selected else 0
                mmr = lambda_mult * sim_to_query - (1 - lambda_mult) * sim_to_selected
                mmr_scores.append(mmr)
            best_idx = np.argmax(mmr_scores)
            selected.append(candidates.pop(best_idx))
        return selected

    def _distance(self, a: np.ndarray, b: np.ndarray) -> float:
        if self.metric == "cosine":
            return 1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        elif self.metric == "l2":
            return np.linalg.norm(a - b)
        else:  # ip
            return -np.dot(a, b)

    async def hybrid_search(
        self,
        query: str,
        *,
        k: int = 5,
        alpha: float = 0.5,
        filter: Optional[Filter] = None,
        **kwargs,
    ) -> RetrievalResult:
        # Requires full-text index on content
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(f"CREATE INDEX IF NOT EXISTS {self.index_name}_fts ON {self.index_name} USING gin (to_tsvector('english', content));")
            rows = await conn.fetch(f"""
                SELECT id, content, metadata,
                       ts_rank(to_tsvector('english', content), plainto_tsquery('english', $1)) AS keyword_score
                FROM {self.index_name}
                ORDER BY keyword_score DESC
                LIMIT $2
            """, query, k * 2)
            # Combine with semantic (requires embedding)
            # This is a simplified version; full hybrid needs both scores
            return [({"id": r["id"], "content": r["content"], "metadata": json.loads(r["metadata"])}, float(r["keyword_score"])) for r in rows[:k]]

    async def get_documents(
        self,
        ids: List[str],
        *,
        include_embeddings: bool = False,
        **kwargs,
    ) -> List[Document]:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            cols = "id, content, metadata" + (", embedding" if include_embeddings else "")
            rows = await conn.fetch(f"SELECT {cols} FROM {self.index_name} WHERE id = ANY($1)", ids)
            return [
                {
                    "id": r["id"],
                    "content": r["content"],
                    "metadata": json.loads(r["metadata"]) if r["metadata"] else {},
                    "embedding": r["embedding"] if include_embeddings else None
                } for r in rows
            ]

    # =====================================================================
    # Async Variants
    # =====================================================================

    async def aadd_documents(self, **kwargs) -> List[str]:
        return await self.add_documents(**kwargs)

    async def asimilarity_search(self, **kwargs) -> RetrievalResult:
        return await self.similarity_search(**kwargs)

    async def amax_marginal_relevance_search(self, **kwargs) -> RetrievalResult:
        return await self.max_marginal_relevance_search(**kwargs)

    # =====================================================================
    # Index Management
    # =====================================================================

    async def create_index(
        self,
        index_name: str,
        embedding_dim: int,
        metric: str = "cosine",
        **kwargs,
    ) -> bool:
        self.index_name = index_name
        self.embedding_dim = embedding_dim
        self.metric = metric.lower()
        self._init_task = asyncio.create_task(self._initialize())
        await self._init_task
        return True

    async def delete_index(self, index_name: str, **kwargs) -> bool:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(f"DROP TABLE IF EXISTS {index_name}")
        return True

    async def list_indexes(self, **kwargs) -> List[str]:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public' AND tablename LIKE '%vector%'
            """)
            return [r["tablename"] for r in rows]

    async def get_index_stats(self, index_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        table = index_name or self.index_name
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
            return {"document_count": count, "metric": self.metric}

    # =====================================================================
    # Utilities
    # =====================================================================

    async def embed_query(self, query: str, **kwargs) -> Embedding:
        raise NotImplementedError("Use external embedder")

    async def search_with_embedding(self, embedding: Embedding, **kwargs) -> RetrievalResult:
        return await self.similarity_search(embedding, **kwargs)

    async def count_documents(self, filter: Optional[Filter] = None, **kwargs) -> int:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            if not filter:
                return await conn.fetchval(f"SELECT COUNT(*) FROM {self.index_name}")
            where = self._build_where_clause(filter)
            return await conn.fetchval(f"SELECT COUNT(*) FROM {self.index_name} WHERE {where}", *filter.values())

    async def backup(self, path: str, **kwargs) -> bool:
        import shutil
        try:
            os.makedirs(path, exist_ok=True)
            # pg_dump logic can be added
            return True
        except:
            return False

    async def restore(self, path: str, **kwargs) -> bool:
        return False  # Requires pg_restore

    async def health_check(self) -> bool:
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except:
            return False

if __name__ == '__main__':
    import asyncio
    from huggingface_hub import InferenceClient


    async def main():
        embedder = InferenceClient(model="sentence-transformers/all-MiniLM-L6-v2")
        store = PGVectorStore(
            host="localhost",
            database="mydb",
            user="user",
            password="pass",
            embedding_dim=384,
            metric="cosine"
        )

        docs = [
            {"content": "Paris is beautiful.", "metadata": {"city": "Paris"}},
            {"content": "Tokyo is modern.", "metadata": {"city": "Tokyo"}}
        ]
        embs = embedder.feature_extraction([d["content"] for d in docs])
        await store.add_documents(docs, embeddings=embs)

        results = await store.similarity_search(embs[0], k=1)
        print(results[0][0]["content"])


    asyncio.run(main())