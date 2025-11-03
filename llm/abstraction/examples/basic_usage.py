"""
Basic Usage Example for Abhikarta LLM Abstraction System

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from llm.abstraction import LLMClientFactory


def main():
    """Demonstrate basic usage of the LLM abstraction system"""
    
    print("=" * 60)
    print("Abhikarta LLM Abstraction - Basic Usage Example")
    print("=" * 60)
    
    # Initialize the client factory
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    
    # Create a client with the default provider (mock)
    print("\n1. Creating client with default provider (mock)...")
    client = factory.create_default_client()
    print(f"   Created: {client}")
    
    # Simple completion
    print("\n2. Simple completion example:")
    prompt = "What is the capital of France?"
    print(f"   Prompt: {prompt}")
    response = client.complete(prompt)
    print(f"   Response: {response}")
    
    # Chat interaction
    print("\n3. Chat interaction example:")
    message = "Hello! Can you help me with Python programming?"
    print(f"   Message: {message}")
    response = client.chat(message)
    print(f"   Response: {response}")
    
    # Follow-up message (uses conversation history)
    print("\n4. Follow-up message:")
    message = "What are some best practices?"
    print(f"   Message: {message}")
    response = client.chat(message)
    print(f"   Response: {response}")
    
    # View history statistics
    print("\n5. Interaction history statistics:")
    stats = client.get_history_summary()
    print(f"   Total interactions: {stats['total_interactions']}")
    print(f"   Total tokens: {stats['total_tokens']}")
    print(f"   Providers: {stats['providers']}")
    print(f"   Models: {stats['models']}")
    
    # Streaming example
    print("\n6. Streaming completion example:")
    prompt = "Count from 1 to 5"
    print(f"   Prompt: {prompt}")
    print("   Response: ", end="", flush=True)
    for token in client.stream_complete(prompt):
        print(token, end="", flush=True)
    print()
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
