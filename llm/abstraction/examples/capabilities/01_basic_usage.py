"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.6

Example 01: Basic Usage
Demonstrates the simplest way to use the Abhikarta LLM library
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
llm_config_path = '/home/ashutosh/PycharmProjects/abhikarta-llm/config/llm_config.json'

from llm.abstraction.facade import UnifiedLLMFacade

def main():
    """Basic usage example showing core functionality"""
    
    print("=" * 70)
    print("EXAMPLE 01: BASIC USAGE")
    print("=" * 70)
    
    # Step 1: Configure the facade with a provider
    print("\n📝 Step 1: Configure the LLM facade")
    config = {
        'providers': {
            'mock': {
                'enabled': True,
                'model': 'mock-model'
            }
        }
    }
    print(f"   Configuration: {config}")
    
    # Step 2: Create the facade
    print("\n🔧 Step 2: Initialize UnifiedLLMFacade")
    facade = UnifiedLLMFacade(config)
    print(f"   ✅ Facade created successfully")
    
    # Step 3: Check available providers
    print("\n🔍 Step 3: Check available providers")
    providers = facade.get_available_providers()
    print(f"   Available providers: {providers}")
    
    # Step 4: Send a simple completion request
    print("\n💬 Step 4: Send a completion request")
    prompt = "What is artificial intelligence?"
    print(f"   Prompt: '{prompt}'")
    
    response = facade.complete(prompt)
    
    # Step 5: Display the response
    print("\n📤 Step 5: Response received")
    print(f"   Provider: {response.provider}")
    print(f"   Model: {response.model}")
    print(f"   Response length: {len(response.text)} characters")
    print(f"   Response preview: {response.text[:100]}...")
    
    # Step 6: Access response metadata
    print("\n📊 Step 6: Response metadata")
    print(f"   Timestamp: {response.timestamp}")
    print(f"   Tokens used: {response.tokens_used}")
    print(f"   Finish reason: {response.finish_reason}")
    
    print("\n" + "=" * 70)
    print("✅ EXAMPLE COMPLETE!")
    print("=" * 70)
    
    print("\n💡 What we learned:")
    print("   • How to configure the UnifiedLLMFacade")
    print("   • How to check available providers")
    print("   • How to send a simple completion request")
    print("   • How to access response data and metadata")
    
    print("\n📚 Next steps:")
    print("   • Try example 02 for multiple providers")
    print("   • Try example 03 for streaming responses")
    print("   • Try example 04 for chat conversations")

if __name__ == "__main__":
    main()

"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.6
"""
