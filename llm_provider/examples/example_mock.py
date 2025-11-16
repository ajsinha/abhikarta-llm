"""
Mock Facade Example - Testing Without API Keys

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha | ajsinha@gmail.com
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_switcher import ConfigSwitcher


def example_basic_chat(factory, model="mock-advanced"):
    """Basic mock chat - no API key needed."""
    print("\n" + "="*60)
    print("1. Mock Chat (No API Key!)")
    print("="*60)
    
    try:
        facade = factory.create_facade("mock", model)
        
        response = facade.chat_completion(
            messages=[{"role": "user", "content": "Test message"}],
            max_tokens=100
        )
        
        print(f"Model: {model}")
        print(f"No API key required!")
        print(f"Response: {response['content']}")
        print(f"Tokens: {response['usage'].total_tokens}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_all_capabilities(factory):
    """Test all capabilities work."""
    print("\n" + "="*60)
    print("2. All Capabilities Work")
    print("="*60)
    
    try:
        facade = factory.create_facade("mock", "mock-advanced")
        
        # Chat
        response = facade.chat_completion([{"role": "user", "content": "Test"}])
        print(f"Chat: {response['content'][:40]}...")
        
        # Streaming
        chunks = list(facade.stream_chat_completion([{"role": "user", "content": "Test"}]))
        print(f"Streaming: {len(chunks)} chunks")
        
        # Vision
        response = facade.chat_completion_with_vision(
            [{"role": "user", "content": "Describe"}],
            images=["test.jpg"]
        )
        print(f"Vision: {response['content'][:40]}...")
        
        # Embeddings
        embeddings = facade.generate_embeddings(["test"])
        print(f"Embeddings: {len(embeddings[0])} dimensions")
        
        print("\nAll capabilities work!")
        
    except Exception as e:
        print(f"Error: {e}")


def run_all_examples(config_mode="json"):
    """Run all Mock examples."""
    print("MOCK (TESTING) FACADE EXAMPLES")
    
    switcher = ConfigSwitcher(json_path="../config")
    factory = switcher.get_factory(config_mode)
    
    example_basic_chat(factory)
    example_all_capabilities(factory)
    
    print("\nAll Mock examples completed!")


if __name__ == "__main__":
    config_mode = os.getenv("CONFIG_MODE", "json")
    run_all_examples(config_mode)
