"""
Connection Pooling and Semantic Caching

Improve performance with connection reuse and intelligent caching.

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import urllib3
from typing import Optional, Dict, Any
import time


class ConnectionPool:
    """HTTP connection pooling for LLM APIs"""
    
    def __init__(self, pool_size: int = 10, timeout: int = 30):
        self.pool_manager = urllib3.PoolManager(
            num_pools=1,
            maxsize=pool_size,
            timeout=urllib3.Timeout(connect=timeout, read=timeout),
            retries=urllib3.Retry(total=3, backoff_factor=0.3)
        )
    
    def request(self, method: str, url: str, **kwargs) -> urllib3.HTTPResponse:
        """Make HTTP request using pool"""
        return self.pool_manager.request(method, url, **kwargs)


class SemanticCache:
    """Cache responses based on semantic similarity"""
    
    def __init__(
        self,
        embedding_client: Any,
        similarity_threshold: float = 0.95,
        max_size: int = 1000,
        ttl: int = 3600
    ):
        self.embedding_client = embedding_client
        self.similarity_threshold = similarity_threshold
        self.max_size = max_size
        self.ttl = ttl
        
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.embeddings: Dict[str, Any] = {}
    
    def get(self, prompt: str) -> Optional[str]:
        """Get cached response for similar prompt"""
        if not self.cache:
            return None
        
        # Get prompt embedding
        prompt_emb = self.embedding_client.embed(prompt)
        prompt_vec = prompt_emb.to_numpy()
        
        # Find most similar cached prompt
        best_similarity = 0
        best_response = None
        
        for cached_prompt, data in self.cache.items():
            # Check TTL
            if time.time() - data['timestamp'] > self.ttl:
                continue
            
            cached_emb = self.embeddings[cached_prompt]
            from ..embeddings import cosine_similarity
            similarity = cosine_similarity(prompt_vec, cached_emb.to_numpy())
            
            if similarity >= self.similarity_threshold and similarity > best_similarity:
                best_similarity = similarity
                best_response = data['response']
        
        return best_response
    
    def set(self, prompt: str, response: str) -> None:
        """Cache response"""
        # Check size limit
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        # Store embedding
        embedding = self.embedding_client.embed(prompt)
        self.embeddings[prompt] = embedding
        
        # Store response
        self.cache[prompt] = {
            'response': response,
            'timestamp': time.time()
        }
    
    def _evict_oldest(self) -> None:
        """Evict oldest cache entry"""
        if not self.cache:
            return
        
        oldest_prompt = min(
            self.cache.keys(),
            key=lambda k: self.cache[k]['timestamp']
        )
        
        del self.cache[oldest_prompt]
        del self.embeddings[oldest_prompt]
    
    def clear(self) -> None:
        """Clear cache"""
        self.cache.clear()
        self.embeddings.clear()
