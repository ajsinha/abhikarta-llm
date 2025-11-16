#!/usr/bin/env python3
"""
Anthropic (Claude) Example

Demonstrates Claude's capabilities:
- Chat completion
- Streaming
- Vision
- Tool use

Usage:
    python example_anthropic.py
    python example_anthropic.py --config-source json
    python example_anthropic.py --config-source db
"""

import sys
sys.path.insert(0, '..')

import register_facades
from config_manager import get_factory
from PIL import Image
import io


def example_basic_chat(factory):
    """Basic chat completion."""
    print("\n" + "="*60)
    print("Example 1: Basic Chat")
    print("="*60)
    
    facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
    
    response = facade.chat_completion(
        messages=[
            {"role": "user", "content": "Explain quantum computing in 2 sentences."}
        ],
        max_tokens=200
    )
    
    print(f"\nResponse: {response['content']}")
    print(f"Tokens: {response['usage'].total_tokens}")
    print(f"Cost: ${facade.estimate_cost(response['usage'].prompt_tokens, response['usage'].completion_tokens):.6f}")


def example_streaming(factory):
    """Streaming response."""
    print("\n" + "="*60)
    print("Example 2: Streaming")
    print("="*60)
    
    facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
    
    messages = [
        {"role": "user", "content": "Write a haiku about programming."}
    ]
    
    print("\nStreaming response:")
    for chunk in facade.stream_chat_completion(messages, max_tokens=100):
        print(chunk, end="", flush=True)
    print("\n")


def example_vision(factory):
    """Vision capabilities (requires image file)."""
    print("\n" + "="*60)
    print("Example 3: Vision")
    print("="*60)
    
    facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
    
    # Create a simple test image
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 350, 250], outline='blue', width=5)
    draw.text((150, 130), "Test Chart", fill='black')
    
    response = facade.chat_completion_with_vision(
        messages=[
            {"role": "user", "content": "Describe what you see in this image."}
        ],
        images=[img],
        max_tokens=200
    )
    
    print(f"\nVision Response: {response['content']}")


def example_tool_use(factory):
    """Tool use / function calling."""
    print("\n" + "="*60)
    print("Example 4: Tool Use")
    print("="*60)
    
    facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
    
    tools = [{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["location"]
            }
        }
    }]
    
    response = facade.chat_completion(
        messages=[
            {"role": "user", "content": "What's the weather like in San Francisco?"}
        ],
        tools=tools,
        max_tokens=200
    )
    
    print(f"\nResponse: {response['content']}")
    
    if response.get('tool_calls'):
        print("\nTool calls requested:")
        for tc in response['tool_calls']:
            print(f"  - {tc['function']['name']}: {tc['function']['arguments']}")


def example_multi_turn(factory):
    """Multi-turn conversation."""
    print("\n" + "="*60)
    print("Example 5: Multi-Turn Conversation")
    print("="*60)
    
    facade = factory.create_facade("anthropic", "claude-3-5-sonnet-20241022")
    
    messages = []
    
    # Turn 1
    messages.append({"role": "user", "content": "I'm learning Python."})
    response = facade.chat_completion(messages, max_tokens=150)
    messages.append({"role": "assistant", "content": response["content"]})
    print(f"\nUser: I'm learning Python.")
    print(f"Assistant: {response['content'][:100]}...")
    
    # Turn 2
    messages.append({"role": "user", "content": "What should I learn first?"})
    response = facade.chat_completion(messages, max_tokens=150)
    print(f"\nUser: What should I learn first?")
    print(f"Assistant: {response['content'][:100]}...")


def main():
    """Run all examples."""
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "ANTHROPIC (CLAUDE) EXAMPLES" + " "*15 + "║")
    print("╚" + "="*58 + "╝")
    
    # Get factory with runtime config selection
    factory = get_factory()
    
    try:
        # Run examples
        example_basic_chat(factory)
        example_streaming(factory)
        example_vision(factory)
        example_tool_use(factory)
        example_multi_turn(factory)
        
        print("\n" + "="*60)
        print("✓ All Anthropic examples completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nMake sure you have:")
        print("  1. Set ANTHROPIC_API_KEY environment variable")
        print("  2. Installed: pip install anthropic")
        print("  3. Configuration files in ./config/ directory")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
