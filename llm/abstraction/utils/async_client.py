"""
Async/Await Support for LLM Operations

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import asyncio
from typing import List, AsyncIterator, Optional
from concurrent.futures import ThreadPoolExecutor
from ..core.client import LLMClient
from ..core.facade import Message


class AsyncLLMClient:
    """Async wrapper for LLMClient"""
    
    def __init__(self, sync_client: LLMClient, executor: Optional[ThreadPoolExecutor] = None):
        self.sync_client = sync_client
        self.executor = executor or ThreadPoolExecutor(max_workers=10)
        self.loop = asyncio.get_event_loop()
    
    async def complete(self, prompt: str, **kwargs) -> str:
        """Async completion"""
        return await self.loop.run_in_executor(
            self.executor,
            lambda: self.sync_client.complete(prompt, **kwargs)
        )
    
    async def chat(self, message: str, **kwargs) -> str:
        """Async chat"""
        return await self.loop.run_in_executor(
            self.executor,
            lambda: self.sync_client.chat(message, **kwargs)
        )
    
    async def stream_complete(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Async stream completion"""
        for token in self.sync_client.stream_complete(prompt, **kwargs):
            yield token
            await asyncio.sleep(0)
    
    async def stream_chat(self, message: str, **kwargs) -> AsyncIterator[str]:
        """Async stream chat"""
        for token in self.sync_client.stream_chat(message, **kwargs):
            yield token
            await asyncio.sleep(0)
    
    async def batch_complete(self, prompts: List[str], **kwargs) -> List[str]:
        """Async batch completion"""
        tasks = [self.complete(prompt, **kwargs) for prompt in prompts]
        return await asyncio.gather(*tasks)
    
    def get_history_summary(self) -> dict:
        """Get history (sync operation)"""
        return self.sync_client.get_history_summary()
    
    async def close(self):
        """Close executor"""
        self.executor.shutdown(wait=True)
