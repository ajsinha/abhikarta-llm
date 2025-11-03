"""
Async/Await Support Example

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import sys
import os
import asyncio
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from llm.abstraction import LLMClientFactory


async def async_complete(client, prompt):
    """Async wrapper for completion"""
    # Note: Current implementation is sync, this demonstrates the pattern
    # Real async would use aiohttp or async client libraries
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, client.complete, prompt)


async def async_chat(client, message):
    """Async wrapper for chat"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, client.chat, message)


async def parallel_requests_example():
    """Demonstrate parallel requests with async"""
    print("=" * 60)
    print("Async Parallel Requests Example")
    print("=" * 60)
    print()
    
    # Initialize factory
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    
    # Create clients
    client1 = factory.create_mock_client()
    client2 = factory.create_mock_client()
    client3 = factory.create_mock_client()
    
    # Prepare prompts
    prompts = [
        "What is Python?",
        "What is JavaScript?",
        "What is Go?"
    ]
    
    # Sequential execution (baseline)
    print("Sequential execution:")
    start_time = time.time()
    
    for prompt in prompts:
        response = client1.complete(prompt)
        print(f"  - {prompt[:30]}: {response[:50]}...")
    
    sequential_time = time.time() - start_time
    print(f"\nTime taken: {sequential_time:.2f}s")
    
    # Parallel execution with async
    print("\nParallel execution (async):")
    start_time = time.time()
    
    # Create tasks
    tasks = [
        async_complete(client1, prompts[0]),
        async_complete(client2, prompts[1]),
        async_complete(client3, prompts[2])
    ]
    
    # Run in parallel
    responses = await asyncio.gather(*tasks)
    
    for prompt, response in zip(prompts, responses):
        print(f"  - {prompt[:30]}: {response[:50]}...")
    
    parallel_time = time.time() - start_time
    print(f"\nTime taken: {parallel_time:.2f}s")
    print(f"Speedup: {sequential_time/parallel_time:.2f}x")


async def async_streaming_example():
    """Demonstrate async streaming"""
    print("\n" + "=" * 60)
    print("Async Streaming Example")
    print("=" * 60)
    print()
    
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    
    client = factory.create_mock_client()
    
    prompt = "Write a short story about AI"
    print(f"Prompt: {prompt}")
    print("Response: ", end="", flush=True)
    
    # Stream tokens
    loop = asyncio.get_event_loop()
    
    for token in client.stream_complete(prompt):
        print(token, end="", flush=True)
        await asyncio.sleep(0.01)  # Simulate async processing
    
    print("\n")


async def async_batch_processing():
    """Demonstrate async batch processing"""
    print("=" * 60)
    print("Async Batch Processing Example")
    print("=" * 60)
    print()
    
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    
    client = factory.create_mock_client()
    
    # Large batch of prompts
    prompts = [f"Explain topic {i}" for i in range(10)]
    
    print(f"Processing {len(prompts)} prompts...")
    start_time = time.time()
    
    # Create tasks for all prompts
    tasks = [async_complete(client, prompt) for prompt in prompts]
    
    # Process in parallel
    responses = await asyncio.gather(*tasks)
    
    elapsed_time = time.time() - start_time
    print(f"✓ Processed {len(responses)} prompts in {elapsed_time:.2f}s")
    print(f"  Average: {elapsed_time/len(responses):.2f}s per prompt")
    
    # Show history stats
    stats = client.get_history_summary()
    print(f"\nHistory: {stats['total_interactions']} interactions")
    print(f"Tokens: {stats['total_tokens']}")


async def main():
    """Main async function"""
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 12 + "ASYNC/AWAIT SUPPORT EXAMPLES" + " " * 17 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    try:
        await parallel_requests_example()
        await async_streaming_example()
        await async_batch_processing()
        
        print("=" * 60)
        print("All async examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run async main
    asyncio.run(main())
