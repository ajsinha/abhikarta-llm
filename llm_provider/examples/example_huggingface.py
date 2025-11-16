"""
HuggingFace Facade Example

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Demonstrates:
- Access to 100K+ models
- Popular open-source models
- Runtime config switching
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_switcher import ConfigSwitcher


def example_basic_chat(factory, model="mistralai/Mistral-7B-Instruct-v0.2"):
    """Basic chat completion example."""
    print("\n" + "="*60)
    print("1. Basic Chat Completion")
    print("="*60)
    
    try:
        facade = factory.create_facade("huggingface", model)
        
        response = facade.chat_completion(
            messages=[{
                "role": "user",
                "content": "What makes HuggingFace special?"
            }],
            max_tokens=150
        )
        
        print(f"✓ Model: {model}")
        print(f"✓ Response: {response['content']}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_model_variety(factory):
    """Demonstrate model variety."""
    print("\n" + "="*60)
    print("2. Model Variety")
    print("="*60)
    
    models = [
        ("mistralai/Mistral-7B-Instruct-v0.2", "Mistral 7B"),
        ("microsoft/phi-2", "Microsoft Phi-2"),
        ("tiiuae/falcon-7b-instruct", "Falcon 7B")
    ]
    
    print("✓ HuggingFace provides access to 100,000+ models!")
    print("\nPopular models:")
    
    for model, name in models:
        print(f"   • {name}")
        print(f"     {model}")


def example_open_source_benefits(factory):
    """Open source benefits."""
    print("\n" + "="*60)
    print("3. Open Source Benefits")
    print("="*60)
    
    print("✓ Benefits of HuggingFace:")
    print("   • Access to 100K+ open-source models")
    print("   • Community-driven development")
    print("   • Transparent model cards")
    print("   • Free tier available")
    print("   • Research-friendly")
    print("   • Self-hosting options")


def run_all_examples(config_mode="json"):
    """Run all HuggingFace examples."""
    print("╔" + "="*58 + "╗")
    print("║" + " "*14 + "HUGGINGFACE FACADE EXAMPLES" + " "*17 + "║")
    print("╚" + "="*58 + "╝")
    
    switcher = ConfigSwitcher(json_path="../config")
    factory = switcher.get_factory(config_mode)
    
    example_basic_chat(factory)
    example_model_variety(factory)
    example_open_source_benefits(factory)
    
    print("\n" + "="*60)
    print("✅ All HuggingFace examples completed!")
    print("="*60)


if __name__ == "__main__":
    config_mode = os.getenv("CONFIG_MODE", "json")
    run_all_examples(config_mode)
