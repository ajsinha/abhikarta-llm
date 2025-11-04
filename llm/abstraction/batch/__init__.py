"""
Batch Processing

Efficient processing of multiple prompts in parallel.

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import asyncio
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


@dataclass
class BatchResult:
    """Result from batch processing"""
    results: List[Any]
    failed: List[Dict[str, Any]]
    total: int
    successful: int
    duration_seconds: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class BatchProcessor:
    """Process multiple prompts efficiently"""
    
    def __init__(
        self,
        llm_client: Any,
        batch_size: int = 10,
        max_concurrent: int = 5,
        retry_failed: bool = True
    ):
        self.llm_client = llm_client
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent
        self.retry_failed = retry_failed
    
    async def process_batch_async(
        self,
        prompts: List[str],
        **kwargs
    ) -> BatchResult:
        """Process prompts concurrently (async)"""
        start_time = time.time()
        results = []
        failed = []
        
        for i in range(0, len(prompts), self.batch_size):
            batch = prompts[i:i + self.batch_size]
            
            tasks = [
                self._process_single_async(idx + i, prompt, **kwargs)
                for idx, prompt in enumerate(batch)
            ]
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for idx, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    failed.append({
                        'index': i + idx,
                        'prompt': batch[idx],
                        'error': str(result)
                    })
                else:
                    results.append(result)
        
        duration = time.time() - start_time
        
        return BatchResult(
            results=results,
            failed=failed,
            total=len(prompts),
            successful=len(results),
            duration_seconds=duration
        )
    
    def process_batch_sync(
        self,
        prompts: List[str],
        **kwargs
    ) -> BatchResult:
        """Process prompts with thread pool"""
        start_time = time.time()
        results = []
        failed = []
        
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            futures = {
                executor.submit(self._process_single_sync, idx, prompt, **kwargs): idx
                for idx, prompt in enumerate(prompts)
            }
            
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    failed.append({
                        'index': idx,
                        'prompt': prompts[idx],
                        'error': str(e)
                    })
        
        duration = time.time() - start_time
        
        return BatchResult(
            results=results,
            failed=failed,
            total=len(prompts),
            successful=len(results),
            duration_seconds=duration
        )
    
    async def _process_single_async(
        self,
        index: int,
        prompt: str,
        **kwargs
    ) -> Any:
        """Process single prompt (async)"""
        if hasattr(self.llm_client, 'acomplete'):
            return await self.llm_client.acomplete(prompt, **kwargs)
        else:
            # Fallback to sync
            return self.llm_client.complete(prompt, **kwargs)
    
    def _process_single_sync(
        self,
        index: int,
        prompt: str,
        **kwargs
    ) -> Any:
        """Process single prompt (sync)"""
        return self.llm_client.complete(prompt, **kwargs)


class RateLimitedBatchProcessor(BatchProcessor):
    """Batch processor with rate limiting"""
    
    def __init__(
        self,
        llm_client: Any,
        requests_per_minute: int = 60,
        **kwargs
    ):
        super().__init__(llm_client, **kwargs)
        self.requests_per_minute = requests_per_minute
        self.min_interval = 60.0 / requests_per_minute
        self.last_request_time = 0
    
    async def _process_single_async(self, index: int, prompt: str, **kwargs) -> Any:
        """Process with rate limiting"""
        # Wait if needed
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            await asyncio.sleep(self.min_interval - elapsed)
        
        self.last_request_time = time.time()
        return await super()._process_single_async(index, prompt, **kwargs)
