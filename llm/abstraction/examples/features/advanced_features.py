"""
Advanced Features Example

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import sys
import os
import asyncio
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
llm_config_path = '/home/ashutosh/PycharmProjects/abhikarta-llm/config/llm_config.json'

from llm.abstraction import LLMClientFactory
from llm.abstraction.utils import (
    RetryConfig, retry_with_backoff,
    RateLimiter,
    LRUCache, cached,
    AsyncLLMClient
)


def demo_retry_mechanism():
    """Demonstrate retry with exponential backoff"""
    print("\n" + "=" * 60)
    print("DEMO 1: Retry Mechanism with Exponential Backoff")
    print("=" * 60)
    
    factory = LLMClientFactory()
    factory.initialize(config_path=llm_config_path)
    client = factory.create_default_client()
    
    retry_config = RetryConfig(
        max_attempts=3,
        base_delay=0.5,
        exponential_base=2.0
    )
    
    @retry_with_backoff(
        retryable_exceptions=(Exception,),
        config=retry_config
    )
    def make_completion(prompt):
        return client.complete(prompt)
    
    print("\nMaking completion with retry protection...")
    response = make_completion("What is machine learning?")
    print(f"Response: {response[:100]}...")


def demo_rate_limiting():
    """Demonstrate rate limiting"""
    print("\n" + "=" * 60)
    print("DEMO 2: Rate Limiting")
    print("=" * 60)
    
    factory = LLMClientFactory()
    factory.initialize(config_path=llm_config_path)
    client = factory.create_default_client()
    
    # Create rate limiter (10 requests per minute)
    limiter = RateLimiter(requests_per_minute=10)
    
    print("\nMaking 5 rate-limited requests...")
    start = time.time()
    
    for i in range(5):
        limiter.acquire()
        response = client.complete(f"Question {i+1}")
        print(f"  Request {i+1}: {response[:50]}...")
    
    elapsed = time.time() - start
    print(f"\nCompleted 5 requests in {elapsed:.2f}s")


def demo_caching():
    """Demonstrate response caching"""
    print("\n" + "=" * 60)
    print("DEMO 3: Response Caching")
    print("=" * 60)
    
    factory = LLMClientFactory()
    factory.initialize(config_path=llm_config_path)
    client = factory.create_default_client()
    
    # Create cache
    cache = LRUCache(max_size=100, ttl_seconds=3600)
    
    @cached(cache)
    def cached_completion(prompt):
        return client.complete(prompt)
    
    print("\nFirst call (cache miss):")
    start = time.time()
    response1 = cached_completion("What is Python?")
    time1 = time.time() - start
    print(f"  Response: {response1[:50]}...")
    print(f"  Time: {time1:.4f}s")
    
    print("\nSecond call with same prompt (cache hit):")
    start = time.time()
    response2 = cached_completion("What is Python?")
    time2 = time.time() - start
    print(f"  Response: {response2[:50]}...")
    print(f"  Time: {time2:.4f}s")
    
    print(f"\nSpeedup: {time1/time2:.2f}x faster")
    print(f"Cache stats: {cache.get_stats()}")


async def demo_async_operations():
    """Demonstrate async/await support"""
    print("\n" + "=" * 60)
    print("DEMO 4: Async/Await Support")
    print("=" * 60)
    
    factory = LLMClientFactory()
    factory.initialize(config_path=llm_config_path)
    sync_client = factory.create_default_client()
    
    # Wrap in async client
    async_client = AsyncLLMClient(sync_client)
    
    print("\nAsync completion:")
    response = await async_client.complete("What is async programming?")
    print(f"  Response: {response[:100]}...")
    
    print("\nAsync batch processing (parallel):")
    prompts = [
        "What is AI?",
        "What is ML?",
        "What is DL?"
    ]
    
    start = time.time()
    responses = await async_client.batch_complete(prompts, max_tokens=50)
    elapsed = time.time() - start
    
    for i, response in enumerate(responses):
        print(f"  Response {i+1}: {response[:50]}...")
    
    print(f"\nProcessed {len(prompts)} requests in {elapsed:.2f}s")
    
    await async_client.close()


def demo_combined_features():
    """Demonstrate combined features"""
    print("\n" + "=" * 60)
    print("DEMO 5: Combined Features (Retry + Cache + Rate Limit)")
    print("=" * 60)
    
    factory = LLMClientFactory()
    factory.initialize(config_path=llm_config_path)
    client = factory.create_default_client()
    
    # Setup utilities
    cache = LRUCache(max_size=50)
    limiter = RateLimiter(requests_per_minute=10)
    retry_config = RetryConfig(max_attempts=3)
    
    @retry_with_backoff(config=retry_config)
    @cached(cache)
    def robust_completion(prompt):
        limiter.acquire()
        return client.complete(prompt)
    
    print("\nMaking robust completions with all protections...")
    
    questions = [
        "What is AI?",
        "What is ML?",
        "What is AI?"  # Duplicate - will use cache
    ]
    
    for i, question in enumerate(questions):
        print(f"\nQuestion {i+1}: {question}")
        response = robust_completion(question)
        print(f"  Answer: {response[:80]}...")
    
    print(f"\nCache stats: {cache.get_stats()}")
    print("Note: Question 3 was served from cache instantly!")


def main():
    """Run all demos"""
    print("=" * 60)
    print("Abhikarta LLM Abstraction - Advanced Features Demo")
    print("=" * 60)
    
    demos = [
        demo_retry_mechanism,
        demo_rate_limiting,
        demo_caching,
        demo_combined_features,
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\n✗ Demo failed: {str(e)}")
    
    # Async demo
    print("\nRunning async demo...")
    try:
        asyncio.run(demo_async_operations())
    except Exception as e:
        print(f"✗ Async demo failed: {str(e)}")
    
    print("\n" + "=" * 60)
    print("All demos completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
