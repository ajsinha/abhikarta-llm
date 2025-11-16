"""
Together AI Facade Example

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_switcher import ConfigSwitcher


def example_basic_chat(factory, model="meta-llama/Llama-3-70b-chat-hf"):
    """Basic chat completion example."""
    print("\n" + "="*60)
    print("1. Basic Chat Completion")
    print("="*60)
    
    try:
        facade = factory.create_facade("together", model)
        
        response = facade.chat_completion(
            messages=[{"role": "user", "content": "What makes Together AI unique?"}],
            max_tokens=150
        )
        
        print(f"Model: {model}")
        print(f"Response: {response['content']}")
        
    except Exception as e:
        print(f"Error: {e}")


def run_all_examples(config_mode="json"):
    """Run all Together AI examples."""
    print("TOGETHER AI FACADE EXAMPLES")
    
    switcher = ConfigSwitcher(json_path="../config")
    factory = switcher.get_factory(config_mode)
    
    example_basic_chat(factory)
    
    print("\nAll Together AI examples completed!")


if __name__ == "__main__":
    config_mode = os.getenv("CONFIG_MODE", "json")
    run_all_examples(config_mode)
