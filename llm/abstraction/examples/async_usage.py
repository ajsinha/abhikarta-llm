"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.4
"""

"""Async Usage Example"""
import sys
import os
import asyncio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from llm.abstraction import LLMClientFactory

# Note: For full async support, providers would need async implementations
# This example demonstrates the concept

async def async_example():
    print("=" * 60)
    print("Async Usage Example")
    print("=" * 60)
    
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    
    # Create clients for multiple providers
    clients = [
        factory.create_mock_client(),
        factory.create_client(provider='mock', model='mock-advanced'),
    ]
    
    # Concurrent requests (mock synchronous version)
    print("\nMaking concurrent requests...")
    
    tasks = []
    for i, client in enumerate(clients):
        # Simulate async by running in executor
        async def make_request(c, idx):
            await asyncio.sleep(0.1)  # Simulate network delay
            return c.complete(f"Question {idx}")
        
        tasks.append(make_request(client, i))
    
    results = await asyncio.gather(*tasks)
    
    for i, result in enumerate(results):
        print(f"\nClient {i} response: {result[:100]}...")
    
    print("\n" + "=" * 60)
    print("Async example completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(async_example())
