"""
Meta (Llama via Replicate) Facade Example

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Demonstrates:
- Llama models via Replicate
- Different model sizes
- Runtime config switching
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_switcher import ConfigSwitcher


def example_basic_chat(factory, model="llama-3.1-70b-instruct"):
    """Basic chat completion example."""
    print("\n" + "="*60)
    print("1. Basic Chat Completion")
    print("="*60)
    
    try:
        facade = factory.create_facade("meta", model)
        
        response = facade.chat_completion(
            messages=[{
                "role": "user",
                "content": "Explain what makes Llama unique in 2 sentences."
            }],
            max_tokens=200
        )
        
        print(f"✓ Model: {model}")
        print(f"✓ Response: {response['content']}")
        print(f"✓ Tokens used: {response['usage'].total_tokens}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_model_comparison(factory):
    """Compare different Llama model sizes."""
    print("\n" + "="*60)
    print("2. Model Size Comparison")
    print("="*60)
    
    models = [
        ("llama-3.1-8b-instruct", "8B - Fast & Efficient"),
        ("llama-3.1-70b-instruct", "70B - Balanced"),
        ("llama-3.1-405b-instruct", "405B - Most Capable")
    ]
    
    for model, description in models:
        try:
            facade = factory.create_facade("meta", model)
            cost = facade.estimate_cost(1000, 500)
            
            print(f"\n✓ {model}")
            print(f"  {description}")
            print(f"  Cost (1K+500): ${cost:.6f}")
            
        except Exception as e:
            print(f"\n✗ {model}: {e}")


def example_code_llama(factory):
    """Code Llama example."""
    print("\n" + "="*60)
    print("3. Code Llama")
    print("="*60)
    
    model = "codellama-70b"
    
    try:
        facade = factory.create_facade("meta", model)
        
        response = facade.chat_completion(
            messages=[{
                "role": "user",
                "content": "Write a Python function to calculate fibonacci numbers."
            }],
            max_tokens=300
        )
        
        print(f"✓ Model: {model}")
        print(f"✓ Code Llama is specialized for coding tasks")
        print(f"✓ Response:\n{response['content']}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def run_all_examples(config_mode="json"):
    """Run all Meta examples."""
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "META (LLAMA via REPLICATE) EXAMPLES" + " "*13 + "║")
    print("╚" + "="*58 + "╝")
    
    switcher = ConfigSwitcher(json_path="../config")
    factory = switcher.get_factory(config_mode)
    
    example_basic_chat(factory)
    example_model_comparison(factory)
    example_code_llama(factory)
    
    print("\n" + "="*60)
    print("✅ All Meta examples completed!")
    print("="*60)


if __name__ == "__main__":
    config_mode = os.getenv("CONFIG_MODE", "json")
    run_all_examples(config_mode)
