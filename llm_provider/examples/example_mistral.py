"""
Mistral Facade Example

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Demonstrates:
- Basic chat completion
- MoE (Mixture of Experts) models
- Function calling
- Runtime config switching
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_switcher import ConfigSwitcher


def example_basic_chat(factory, model="mistral-large-latest"):
    """Basic chat completion example."""
    print("\n" + "="*60)
    print("1. Basic Chat Completion")
    print("="*60)
    
    try:
        facade = factory.create_facade("mistral", model)
        
        response = facade.chat_completion(
            messages=[{
                "role": "user",
                "content": "Explain Mixture of Experts architecture in 2 sentences."
            }],
            max_tokens=200
        )
        
        print(f"✓ Model: {model}")
        print(f"✓ Response: {response['content']}")
        print(f"✓ Tokens used: {response['usage'].total_tokens}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_mixtral(factory):
    """Mixtral MoE model example."""
    print("\n" + "="*60)
    print("2. Mixtral MoE Model")
    print("="*60)
    
    model = "mixtral-8x7b"
    
    try:
        facade = factory.create_facade("mistral", model)
        
        response = facade.chat_completion(
            messages=[{
                "role": "user",
                "content": "What are the benefits of MoE architecture?"
            }],
            max_tokens=150
        )
        
        print(f"✓ Model: {model}")
        print(f"✓ Mixtral uses 8 expert models (7B each)")
        print(f"✓ Response: {response['content']}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_function_calling(factory, model="mistral-large-latest"):
    """Function calling example."""
    print("\n" + "="*60)
    print("3. Function Calling")
    print("="*60)
    
    try:
        facade = factory.create_facade("mistral", model)
        
        tools = [{
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Perform mathematical calculation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["add", "subtract", "multiply", "divide"]
                        },
                        "a": {"type": "number"},
                        "b": {"type": "number"}
                    },
                    "required": ["operation", "a", "b"]
                }
            }
        }]
        
        response = facade.chat_completion(
            messages=[{
                "role": "user",
                "content": "What is 156 multiplied by 23?"
            }],
            tools=tools,
            max_tokens=200
        )
        
        print(f"✓ Response: {response['content']}")
        
        if response.get("tool_calls"):
            print("\n✓ Function called:")
            for tc in response["tool_calls"]:
                print(f"   {tc['function']['name']}: {tc['function']['arguments']}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def run_all_examples(config_mode="json"):
    """Run all Mistral examples."""
    print("╔" + "="*58 + "╗")
    print("║" + " "*16 + "MISTRAL FACADE EXAMPLES" + " "*19 + "║")
    print("╚" + "="*58 + "╝")
    
    switcher = ConfigSwitcher(json_path="../config")
    factory = switcher.get_factory(config_mode)
    
    example_basic_chat(factory)
    example_mixtral(factory)
    example_function_calling(factory)
    
    print("\n" + "="*60)
    print("✅ All Mistral examples completed!")
    print("="*60)


if __name__ == "__main__":
    config_mode = os.getenv("CONFIG_MODE", "json")
    run_all_examples(config_mode)
