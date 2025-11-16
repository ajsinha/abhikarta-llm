"""
AWS Bedrock Facade Example - Enterprise AI

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha | ajsinha@gmail.com
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_switcher import ConfigSwitcher


def example_basic_chat(factory, model="anthropic.claude-3-sonnet-20240229-v1:0"):
    """Basic AWS Bedrock chat."""
    print("\n" + "="*60)
    print("1. Enterprise Chat via AWS")
    print("="*60)
    
    try:
        facade = factory.create_facade("awsbedrock", model, region="us-east-1")
        
        response = facade.chat_completion(
            messages=[{"role": "user", "content": "What are AWS Bedrock benefits?"}],
            max_tokens=150
        )
        
        print(f"Model: {model}")
        print(f"Region: us-east-1")
        print(f"Response: {response['content']}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Ensure AWS credentials configured")


def run_all_examples(config_mode="json"):
    """Run all AWS Bedrock examples."""
    print("AWS BEDROCK FACADE EXAMPLES")
    
    switcher = ConfigSwitcher(json_path="../config")
    factory = switcher.get_factory(config_mode)
    
    example_basic_chat(factory)
    
    print("\nAll AWS Bedrock examples completed!")


if __name__ == "__main__":
    config_mode = os.getenv("CONFIG_MODE", "json")
    run_all_examples(config_mode)
