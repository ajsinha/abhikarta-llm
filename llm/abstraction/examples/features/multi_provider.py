"""
Multi-Provider Example for Abhikarta LLM Abstraction System

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
llm_config_path = '/home/ashutosh/PycharmProjects/abhikarta-llm/config/llm_config.json'

from llm.abstraction import LLMClientFactory


def compare_providers(factory, prompt):
    """Compare responses from different providers"""
    
    providers = ['mock']  # Start with mock
    
    # Try to add real providers if API keys are available
    if os.environ.get('ANTHROPIC_API_KEY'):
        providers.append('anthropic')
    
    if os.environ.get('OPENAI_API_KEY'):
        providers.append('openai')
    
    print(f"\nPrompt: '{prompt}'")
    print("=" * 60)
    
    for provider in providers:
        try:
            # Get default model for provider
            if provider == 'mock':
                model = 'mock-model'
            elif provider == 'anthropic':
                model = 'claude-3-haiku-20240307'
            elif provider == 'openai':
                model = 'gpt-3.5-turbo'
            else:
                continue
            
            print(f"\n{provider.upper()} ({model}):")
            print("-" * 60)
            
            # Create client for this provider
            client = factory.create_client(provider=provider, model=model)
            
            # Get response
            response = client.complete(prompt, max_tokens=150)
            print(response)
            
            # Show statistics
            stats = client.get_history_summary()
            if stats['total_tokens'] > 0:
                print(f"\nTokens used: {stats['total_tokens']}")
                print(f"Estimated cost: ${stats['total_cost']:.4f}")
            
        except Exception as e:
            print(f"Error with {provider}: {str(e)}")


def main():
    """Demonstrate multi-provider usage"""
    
    print("=" * 60)
    print("Abhikarta LLM Abstraction - Multi-Provider Example")
    print("=" * 60)
    
    # Initialize factory
    factory = LLMClientFactory()
    factory.initialize(config_path=llm_config_path)
    
    # List available providers
    print("\nAvailable providers:")
    provider_factory = factory._provider_factory
    providers = provider_factory.list_available_providers()
    for provider in providers:
        print(f"  - {provider}")
    
    # Compare responses from different providers
    print("\n" + "=" * 60)
    print("COMPARISON 1: Simple Question")
    print("=" * 60)
    compare_providers(factory, "What is artificial intelligence?")
    
    print("\n" + "=" * 60)
    print("COMPARISON 2: Creative Task")
    print("=" * 60)
    compare_providers(factory, "Write a haiku about programming")
    
    # Demonstrate switching providers mid-conversation
    print("\n" + "=" * 60)
    print("DEMONSTRATION: Switching Providers")
    print("=" * 60)
    
    print("\nStarting with Mock provider...")
    client1 = factory.create_client(provider='mock', model='mock-model')
    response1 = client1.chat("Hello, how are you?")
    print(f"Mock: {response1}")
    
    if os.environ.get('ANTHROPIC_API_KEY'):
        print("\nSwitching to Anthropic provider...")
        client2 = factory.create_client(provider='anthropic', model='claude-3-haiku-20240307')
        response2 = client2.chat("Hello, how are you?")
        print(f"Anthropic: {response2}")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    
    print("\nNote: To test with real providers, set environment variables:")
    print("  export ANTHROPIC_API_KEY=your_key_here")
    print("  export OPENAI_API_KEY=your_key_here")


if __name__ == "__main__":
    main()
