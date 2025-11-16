"""
Groq Facade Example

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Demonstrates:
- Ultra-fast inference
- Speed benchmarking
- Basic chat completion
- Runtime config switching
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_switcher import ConfigSwitcher


def example_basic_chat(factory, model="llama-3.1-70b-versatile"):
    """Basic chat completion example."""
    print("\n" + "="*60)
    print("1. Basic Chat Completion")
    print("="*60)
    
    try:
        facade = factory.create_facade("groq", model)
        
        response = facade.chat_completion(
            messages=[{
                "role": "user",
                "content": "Explain what makes Groq's inference fast in 2 sentences."
            }],
            max_tokens=200
        )
        
        print(f"✓ Model: {model}")
        print(f"✓ Response: {response['content']}")
        print(f"✓ Tokens used: {response['usage'].total_tokens}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_speed_benchmark(factory, model="llama-3.1-70b-versatile"):
    """Speed benchmarking example."""
    print("\n" + "="*60)
    print("2. Ultra-Fast Inference Speed")
    print("="*60)
    
    try:
        facade = factory.create_facade("groq", model)
        
        start = time.time()
        response = facade.chat_completion(
            messages=[{
                "role": "user",
                "content": "Count from 1 to 20, one number per line."
            }],
            max_tokens=100
        )
        end = time.time()
        
        duration = end - start
        tokens_per_sec = response['usage'].completion_tokens / duration
        
        print(f"✓ Model: {model}")
        print(f"✓ Tokens generated: {response['usage'].completion_tokens}")
        print(f"✓ Time: {duration:.3f} seconds")
        print(f"✓ Speed: {tokens_per_sec:.0f} tokens/second")
        print("\n✨ Groq achieves 500+ tokens/sec on average!")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_streaming_speed(factory, model="llama-3.1-8b-instant"):
    """Streaming speed example."""
    print("\n" + "="*60)
    print("3. Streaming Speed Test")
    print("="*60)
    
    try:
        facade = factory.create_facade("groq", model)
        
        print(f"✓ Model: {model}")
        print("✓ Streaming: ", end="", flush=True)
        
        start = time.time()
        chunk_count = 0
        
        for chunk in facade.stream_chat_completion(
            messages=[{
                "role": "user",
                "content": "Write a short paragraph about AI."
            }],
            max_tokens=100
        ):
            print(chunk, end="", flush=True)
            chunk_count += 1
        
        end = time.time()
        duration = end - start
        
        print(f"\n\n✓ Chunks: {chunk_count}")
        print(f"✓ Time: {duration:.3f} seconds")
        print(f"✓ First token latency: ~{duration/chunk_count:.3f}s")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_cost_comparison(factory):
    """Cost comparison example."""
    print("\n" + "="*60)
    print("4. Cost Efficiency")
    print("="*60)
    
    model = "llama-3.1-70b-versatile"
    
    try:
        facade = factory.create_facade("groq", model)
        
        # Estimate cost
        cost = facade.estimate_cost(1000, 500)
        
        print(f"✓ Model: {model}")
        print(f"✓ Cost for 1K input + 500 output: ${cost:.6f}")
        print("✓ Groq offers very competitive pricing!")
        print("✓ Free tier has generous limits")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def run_all_examples(config_mode="json"):
    """Run all Groq examples."""
    print("╔" + "="*58 + "╗")
    print("║" + " "*17 + "GROQ FACADE EXAMPLES" + " "*21 + "║")
    print("╚" + "="*58 + "╝")
    
    switcher = ConfigSwitcher(json_path="../config")
    factory = switcher.get_factory(config_mode)
    
    example_basic_chat(factory)
    example_speed_benchmark(factory)
    example_streaming_speed(factory)
    example_cost_comparison(factory)
    
    print("\n" + "="*60)
    print("✅ All Groq examples completed!")
    print("="*60)


if __name__ == "__main__":
    config_mode = os.getenv("CONFIG_MODE", "json")
    run_all_examples(config_mode)
