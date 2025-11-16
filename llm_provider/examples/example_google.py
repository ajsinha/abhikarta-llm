"""
Google (Gemini) Facade Example

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Demonstrates:
- Basic chat completion
- Multimodal capabilities
- Thinking mode (Gemini 2.0)
- Runtime config switching
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_switcher import ConfigSwitcher


def example_basic_chat(factory, model="gemini-2.0-flash-exp"):
    """Basic chat completion example."""
    print("\n" + "="*60)
    print("1. Basic Chat Completion")
    print("="*60)
    
    try:
        facade = factory.create_facade("google", model)
        
        response = facade.chat_completion(
            messages=[{
                "role": "user",
                "content": "Explain what makes Gemini unique in 2 sentences."
            }],
            max_tokens=200
        )
        
        print(f"✓ Model: {model}")
        print(f"✓ Response: {response['content']}")
        print(f"✓ Tokens used: {response['usage'].total_tokens}")
        print(f"✓ Context window: {facade.get_context_window_size():,} tokens")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_streaming(factory, model="gemini-2.0-flash-exp"):
    """Streaming response example."""
    print("\n" + "="*60)
    print("2. Streaming Response")
    print("="*60)
    
    try:
        facade = factory.create_facade("google", model)
        
        print("✓ Streaming response: ", end="", flush=True)
        
        for chunk in facade.stream_chat_completion(
            messages=[{
                "role": "user",
                "content": "Count from 1 to 5 with one number per line."
            }],
            max_tokens=100
        ):
            print(chunk, end="", flush=True)
        
        print("\n✓ Streaming completed")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_multimodal(factory, model="gemini-2.0-flash-exp"):
    """Multimodal capabilities example."""
    print("\n" + "="*60)
    print("3. Multimodal Capabilities")
    print("="*60)
    
    try:
        facade = factory.create_facade("google", model)
        
        if not facade.supports_capability("vision"):
            print(f"⚠️  Vision not supported by {model}")
            return
        
        print("✓ Multimodal is supported")
        print("ℹ️  Gemini supports:")
        print("   • Text")
        print("   • Images (multiple)")
        print("   • Audio (some models)")
        print("   • Video (some models)")
        print("\n   Usage:")
        print("   from PIL import Image")
        print("   images = [Image.open('img1.png'), Image.open('img2.png')]")
        print("   response = facade.chat_completion_with_vision(messages, images=images)")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_long_context(factory, model="gemini-1.5-pro"):
    """Long context example."""
    print("\n" + "="*60)
    print("4. Long Context Window")
    print("="*60)
    
    try:
        facade = factory.create_facade("google", model)
        
        context_size = facade.get_context_window_size()
        print(f"✓ Model: {model}")
        print(f"✓ Context window: {context_size:,} tokens")
        
        if context_size >= 1_000_000:
            print(f"✓ This model can process documents up to ~{context_size // 4:,} characters!")
            print("ℹ️  Use cases:")
            print("   • Entire codebases")
            print("   • Long documents")
            print("   • Full books")
            print("   • Extended conversations")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_thinking_mode(factory):
    """Thinking mode example (Gemini 2.0)."""
    print("\n" + "="*60)
    print("5. Thinking Mode (Gemini 2.0)")
    print("="*60)
    
    model = "gemini-2.0-flash-thinking-exp"
    
    try:
        facade = factory.create_facade("google", model)
        
        response = facade.chat_completion(
            messages=[{
                "role": "user",
                "content": "Solve: If a train leaves NYC at 3pm going 80mph, and another leaves LA at 1pm going 60mph, when do they meet? Show your reasoning."
            }],
            max_tokens=500
        )
        
        print(f"✓ Model: {model}")
        print(f"✓ Response with thinking:")
        print(response['content'])
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("ℹ️  Thinking mode models may not be available in all regions")


def run_all_examples(config_mode="json"):
    """Run all Google examples."""
    print("╔" + "="*58 + "╗")
    print("║" + " "*12 + "GOOGLE (GEMINI) FACADE EXAMPLES" + " "*15 + "║")
    print("╚" + "="*58 + "╝")
    
    switcher = ConfigSwitcher(json_path="../config")
    factory = switcher.get_factory(config_mode)
    
    example_basic_chat(factory)
    example_streaming(factory)
    example_multimodal(factory)
    example_long_context(factory)
    example_thinking_mode(factory)
    
    print("\n" + "="*60)
    print("✅ All Google examples completed!")
    print("="*60)


if __name__ == "__main__":
    config_mode = os.getenv("CONFIG_MODE", "json")
    run_all_examples(config_mode)
