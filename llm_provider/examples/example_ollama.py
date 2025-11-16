"""
Ollama Facade Example - Local Model Execution

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha | ajsinha@gmail.com
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_switcher import ConfigSwitcher


def example_basic_chat(factory, model="llama3.1"):
    """Basic local chat completion."""
    print("\n" + "="*60)
    print("1. Local Chat (No API Calls!)")
    print("="*60)
    
    try:
        facade = factory.create_facade("ollama", model)
        
        response = facade.chat_completion(
            messages=[{"role": "user", "content": "Benefits of local models?"}],
            max_tokens=150
        )
        
        print(f"Model: {model}")
        print(f"Running locally - no API calls!")
        print(f"Response: {response['content']}")
        print(f"Cost: $0.00")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Install: curl -fsSL https://ollama.com/install.sh | sh")


def run_all_examples(config_mode="json"):
    """Run all Ollama examples."""
    print("OLLAMA (LOCAL) FACADE EXAMPLES")
    
    switcher = ConfigSwitcher(json_path="../config")
    factory = switcher.get_factory(config_mode)
    
    example_basic_chat(factory)
    
    print("\nAll Ollama examples completed!")


if __name__ == "__main__":
    config_mode = os.getenv("CONFIG_MODE", "json")
    run_all_examples(config_mode)
