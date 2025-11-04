"""
Embeddings Support

Generate and use embeddings for semantic search and similarity.

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
import json


@dataclass
class Embedding:
    """Represents a text embedding"""
    text: str
    vector: List[float]
    model: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_numpy(self) -> np.ndarray:
        """Convert to numpy array"""
        return np.array(self.vector)
    
    def dimension(self) -> int:
        """Get embedding dimension"""
        return len(self.vector)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'text': self.text,
            'vector': self.vector,
            'model': self.model,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }


class EmbeddingClient:
    """Client for generating embeddings"""
    
    def __init__(
        self,
        provider: str = 'openai',
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        self.provider = provider
        self.model = model or self._get_default_model()
        self.api_key = api_key
        self._client = None
    
    def _get_default_model(self) -> str:
        """Get default model for provider"""
        defaults = {
            'openai': 'text-embedding-3-small',
            'anthropic': 'claude-3-embedding',
            'mock': 'mock-embedding'
        }
        return defaults.get(self.provider, 'text-embedding-3-small')
    
    def _initialize_client(self):
        """Initialize provider client"""
        if self._client:
            return
        
        if self.provider == 'openai':
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package required for OpenAI embeddings")
        elif self.provider == 'mock':
            self._client = MockEmbeddingProvider()
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def embed(self, text: str) -> Embedding:
        """
        Generate embedding for text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding object
        """
        self._initialize_client()
        
        if self.provider == 'openai':
            response = self._client.embeddings.create(
                input=text,
                model=self.model
            )
            vector = response.data[0].embedding
        elif self.provider == 'mock':
            vector = self._client.embed(text)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
        
        return Embedding(
            text=text,
            vector=vector,
            model=self.model
        )
    
    def embed_batch(self, texts: List[str]) -> List[Embedding]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of Embedding objects
        """
        self._initialize_client()
        
        if self.provider == 'openai':
            response = self._client.embeddings.create(
                input=texts,
                model=self.model
            )
            vectors = [item.embedding for item in response.data]
            
            return [
                Embedding(text=text, vector=vector, model=self.model)
                for text, vector in zip(texts, vectors)
            ]
        elif self.provider == 'mock':
            return [self.embed(text) for text in texts]
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        emb1 = self.embed(text1)
        emb2 = self.embed(text2)
        
        return cosine_similarity(emb1.to_numpy(), emb2.to_numpy())


class MockEmbeddingProvider:
    """Mock provider for testing"""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
    
    def embed(self, text: str) -> List[float]:
        """Generate mock embedding"""
        # Use hash for deterministic but varied vectors
        np.random.seed(hash(text) % (2**32))
        vector = np.random.randn(self.dimension)
        # Normalize
        vector = vector / np.linalg.norm(vector)
        return vector.tolist()


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Similarity score (-1 to 1, typically 0-1 for embeddings)
    """
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))


def euclidean_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Compute Euclidean distance between vectors"""
    return float(np.linalg.norm(vec1 - vec2))


class VectorStore:
    """Simple in-memory vector store for embeddings"""
    
    def __init__(self, embedding_client: EmbeddingClient):
        self.embedding_client = embedding_client
        self.embeddings: List[Embedding] = []
        self.metadata: List[Dict[str, Any]] = []
    
    def add(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add text to vector store.
        
        Args:
            text: Text to add
            metadata: Optional metadata
        """
        embedding = self.embedding_client.embed(text)
        if metadata:
            embedding.metadata.update(metadata)
        
        self.embeddings.append(embedding)
        self.metadata.append(metadata or {})
    
    def add_batch(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Add multiple texts"""
        embeddings = self.embedding_client.embed_batch(texts)
        
        if metadatas:
            for emb, meta in zip(embeddings, metadatas):
                emb.metadata.update(meta)
        
        self.embeddings.extend(embeddings)
        self.metadata.extend(metadatas or [{} for _ in texts])
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar texts.
        
        Args:
            query: Query text
            top_k: Number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of results with text, similarity, and metadata
        """
        if not self.embeddings:
            return []
        
        # Get query embedding
        query_embedding = self.embedding_client.embed(query)
        query_vec = query_embedding.to_numpy()
        
        # Compute similarities
        similarities = []
        for i, emb in enumerate(self.embeddings):
            emb_vec = emb.to_numpy()
            sim = cosine_similarity(query_vec, emb_vec)
            
            if threshold is None or sim >= threshold:
                similarities.append({
                    'index': i,
                    'text': emb.text,
                    'similarity': sim,
                    'metadata': emb.metadata
                })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similarities[:top_k]
    
    def search_by_vector(
        self,
        vector: List[float],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search using a vector directly"""
        query_vec = np.array(vector)
        
        similarities = []
        for i, emb in enumerate(self.embeddings):
            emb_vec = emb.to_numpy()
            sim = cosine_similarity(query_vec, emb_vec)
            
            similarities.append({
                'index': i,
                'text': emb.text,
                'similarity': sim,
                'metadata': emb.metadata
            })
        
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]
    
    def delete(self, indices: List[int]) -> None:
        """Delete embeddings by index"""
        for i in sorted(indices, reverse=True):
            if 0 <= i < len(self.embeddings):
                del self.embeddings[i]
                del self.metadata[i]
    
    def clear(self) -> None:
        """Clear all embeddings"""
        self.embeddings.clear()
        self.metadata.clear()
    
    def size(self) -> int:
        """Get number of embeddings"""
        return len(self.embeddings)
    
    def save(self, filepath: str) -> None:
        """Save vector store to file"""
        data = {
            'embeddings': [emb.to_dict() for emb in self.embeddings],
            'metadata': self.metadata
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f)
    
    def load(self, filepath: str) -> None:
        """Load vector store from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.embeddings.clear()
        self.metadata.clear()
        
        for emb_data in data['embeddings']:
            emb = Embedding(
                text=emb_data['text'],
                vector=emb_data['vector'],
                model=emb_data['model'],
                metadata=emb_data.get('metadata', {}),
                created_at=datetime.fromisoformat(emb_data['created_at'])
            )
            self.embeddings.append(emb)
        
        self.metadata = data.get('metadata', [])


class SemanticSearch:
    """High-level semantic search interface"""
    
    def __init__(self, embedding_client: EmbeddingClient):
        self.embedding_client = embedding_client
        self.documents: List[str] = []
        self.vector_store = VectorStore(embedding_client)
    
    def add_documents(self, documents: List[str]) -> None:
        """Add documents to search index"""
        self.documents.extend(documents)
        self.vector_store.add_batch(
            documents,
            [{'doc_id': len(self.documents) - len(documents) + i} 
             for i in range(len(documents))]
        )
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search documents"""
        return self.vector_store.search(query, top_k=top_k)
    
    def find_similar(self, text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find similar documents to given text"""
        return self.search(text, top_k=top_k)


def cluster_embeddings(
    embeddings: List[Embedding],
    n_clusters: int = 5
) -> List[int]:
    """
    Cluster embeddings using K-means.
    
    Args:
        embeddings: List of embeddings
        n_clusters: Number of clusters
        
    Returns:
        List of cluster labels
    """
    try:
        from sklearn.cluster import KMeans
        
        vectors = np.array([emb.to_numpy() for emb in embeddings])
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(vectors)
        
        return labels.tolist()
    except ImportError:
        raise ImportError("scikit-learn required for clustering")


def reduce_dimensions(
    embeddings: List[Embedding],
    n_components: int = 2
) -> np.ndarray:
    """
    Reduce embedding dimensions for visualization.
    
    Args:
        embeddings: List of embeddings
        n_components: Target dimensions
        
    Returns:
        Reduced vectors
    """
    try:
        from sklearn.decomposition import PCA
        
        vectors = np.array([emb.to_numpy() for emb in embeddings])
        pca = PCA(n_components=n_components)
        reduced = pca.fit_transform(vectors)
        
        return reduced
    except ImportError:
        raise ImportError("scikit-learn required for PCA")
