#!/usr/bin/env python3
"""
OpenAI (GPT) Example

Demonstrates OpenAI's capabilities:
- Chat completion
- Function calling
- Embeddings
- Image generation (DALL-E)

Usage:
    python example_openai.py
    python example_openai.py --config-source json
"""

import sys
sys.path.insert(0, '..')

import register_facades
from config_manager import get_factory


def example_chat(factory):
    """Basic chat with GPT-4."""
    print("\n" + "="*60)
    print("Example 1: GPT-4 Chat")
    print("="*60)
    
    facade = factory.create_facade("openai", "gpt-4-turbo-preview")
    
    response = facade.chat_completion(
        messages=[
            {"role": "system", "content": "You are a helpful coding assistant."},
            {"role": "user", "content": "Explain list comprehensions in Python."}
        ],
        max_tokens=200
    )
    
    print(f"\nResponse: {response['content']}")
    print(f"Tokens: {response['usage'].total_tokens}")
    print(f"Cost: ${facade.estimate_cost(response['usage'].prompt_tokens, response['usage'].completion_tokens):.6f}")


def example_function_calling(factory):
    """Function calling example."""
    print("\n" + "="*60)
    print("Example 2: Function Calling")
    print("="*60)
    
    facade = factory.create_facade("openai", "gpt-4-turbo-preview")
    
    tools = [{
        "type": "function",
        "function": {
            "name": "search_database",
            "description": "Search database for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Max results"}
                },
                "required": ["query"]
            }
        }
    }]
    
    response = facade.chat_completion(
        messages=[
            {"role": "user", "content": "Find recent customer orders"}
        ],
        tools=tools,
        max_tokens=200
    )
    
    print(f"\nResponse: {response['content']}")
    
    if response.get('tool_calls'):
        print("\nFunction calls:")
        for tc in response['tool_calls']:
            print(f"  - {tc['function']['name']}: {tc['function']['arguments']}")


def example_embeddings(factory):
    """Generate embeddings."""
    print("\n" + "="*60)
    print("Example 3: Embeddings")
    print("="*60)
    
    facade = factory.create_facade("openai", "text-embedding-3-large")
    
    texts = [
        "The quick brown fox jumps over the lazy dog",
        "A fast auburn fox leaps above an idle canine",
        "Python is a programming language"
    ]
    
    embeddings = facade.generate_embeddings(texts)
    
    print(f"\nGenerated {len(embeddings)} embeddings")
    print(f"Embedding dimensions: {len(embeddings[0])}")
    
    # Calculate similarity
    import numpy as np
    sim_1_2 = np.dot(embeddings[0], embeddings[1])
    sim_1_3 = np.dot(embeddings[0], embeddings[2])
    
    print(f"\nSimilarity (similar sentences): {sim_1_2:.4f}")
    print(f"Similarity (different sentences): {sim_1_3:.4f}")


def example_streaming(factory):
    """Streaming with GPT-3.5."""
    print("\n" + "="*60)
    print("Example 4: Streaming")
    print("="*60)
    
    facade = factory.create_facade("openai", "gpt-3.5-turbo")
    
    print("\nStreaming response:")
    for chunk in facade.stream_chat_completion(
        messages=[{"role": "user", "content": "Write a short poem about AI."}],
        max_tokens=100
    ):
        print(chunk, end="", flush=True)
    print("\n")


def example_json_mode(factory):
    """JSON mode example."""
    print("\n" + "="*60)
    print("Example 5: JSON Mode")
    print("="*60)
    
    facade = factory.create_facade("openai", "gpt-4-turbo-preview")
    
    response = facade.chat_completion(
        messages=[
            {"role": "system", "content": "You respond only with valid JSON."},
            {"role": "user", "content": "List 3 colors with their hex codes"}
        ],
        response_format={"type": "json_object"},
        max_tokens=200
    )
    
    print(f"\nJSON Response:\n{response['content']}")


def main():
    """Run all examples."""
    print("╔" + "="*58 + "╗")
    print("║" + " "*18 + "OPENAI (GPT) EXAMPLES" + " "*19 + "║")
    print("╚" + "="*58 + "╝")
    
    factory = get_factory()
    
    try:
        example_chat(factory)
        example_function_calling(factory)
        example_embeddings(factory)
        example_streaming(factory)
        example_json_mode(factory)
        
        print("\n" + "="*60)
        print("✓ All OpenAI examples completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nMake sure you have:")
        print("  1. Set OPENAI_API_KEY environment variable")
        print("  2. Installed: pip install openai numpy")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
