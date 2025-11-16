"""
Cohere Facade Example

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Demonstrates:
- Basic chat completion
- RAG capabilities
- Embeddings
- Runtime config switching
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_switcher import ConfigSwitcher


def example_basic_chat(factory, model="command-r-plus"):
    """Basic chat completion example."""
    print("\n" + "="*60)
    print("1. Basic Chat Completion")
    print("="*60)
    
    try:
        facade = factory.create_facade("cohere", model)
        
        response = facade.chat_completion(
            messages=[{
                "role": "user",
                "content": "Explain what makes Cohere unique in 2 sentences."
            }],
            max_tokens=200
        )
        
        print(f"✓ Model: {model}")
        print(f"✓ Response: {response['content']}")
        print(f"✓ Tokens used: {response['usage'].total_tokens}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_embeddings(factory):
    """Embeddings example."""
    print("\n" + "="*60)
    print("2. Text Embeddings")
    print("="*60)
    
    model = "embed-english-v3.0"
    
    try:
        facade = factory.create_facade("cohere", model)
        
        texts = [
            "The cat sat on the mat",
            "A feline rested on the rug",
            "Python is a programming language"
        ]
        
        embeddings = facade.generate_embeddings(texts)
        
        print(f"✓ Model: {model}")
        print(f"✓ Generated {len(embeddings)} embeddings")
        print(f"✓ Embedding dimension: {len(embeddings[0])}")
        print("✓ Use cases:")
        print("   • Semantic search")
        print("   • Document clustering")
        print("   • Recommendation systems")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_rag(factory, model="command-r-plus"):
    """RAG (Retrieval Augmented Generation) example."""
    print("\n" + "="*60)
    print("3. RAG Capabilities")
    print("="*60)
    
    try:
        facade = factory.create_facade("cohere", model)
        
        # Simulate retrieved documents
        documents = [
            "Cohere specializes in enterprise AI solutions.",
            "Command-R models are optimized for RAG applications.",
            "Cohere offers multilingual support."
        ]
        
        context = "\n\n".join(documents)
        
        response = facade.chat_completion(
            messages=[{
                "role": "system",
                "content": f"Use this context to answer:\n{context}"
            }, {
                "role": "user",
                "content": "What does Cohere specialize in?"
            }],
            max_tokens=150
        )
        
        print(f"✓ RAG-enhanced response: {response['content']}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def run_all_examples(config_mode="json"):
    """Run all Cohere examples."""
    print("╔" + "="*58 + "╗")
    print("║" + " "*16 + "COHERE FACADE EXAMPLES" + " "*20 + "║")
    print("╚" + "="*58 + "╝")
    
    switcher = ConfigSwitcher(json_path="../config")
    factory = switcher.get_factory(config_mode)
    
    example_basic_chat(factory)
    example_embeddings(factory)
    example_rag(factory)
    
    print("\n" + "="*60)
    print("✅ All Cohere examples completed!")
    print("="*60)


if __name__ == "__main__":
    config_mode = os.getenv("CONFIG_MODE", "json")
    run_all_examples(config_mode)
