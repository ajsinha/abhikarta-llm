"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.6

Example 02: Multiple Providers
Demonstrates how to configure and use multiple LLM providers
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
llm_config_path = '/home/ashutosh/PycharmProjects/abhikarta-llm/config/llm_config.json'

from llm.abstraction.facade import UnifiedLLMFacade

def main():
    """Example showing multiple provider configuration and usage"""
    
    print("=" * 70)
    print("EXAMPLE 02: MULTIPLE PROVIDERS")
    print("=" * 70)
    
    # Step 1: Configure multiple providers
    print("\n📝 Step 1: Configure multiple providers")
    config = {
        'providers': {
            'mock': {
                'enabled': True,
                'model': 'mock-model'
            }
            # In production, you would add real providers:
            # 'openai': {
            #     'enabled': True,
            #     'api_key': 'your-openai-key',
            #     'model': 'gpt-4'
            # },
            # 'anthropic': {
            #     'enabled': True,
            #     'api_key': 'your-anthropic-key',
            #     'model': 'claude-3-opus'
            # }
        },
        'default_provider': 'mock'
    }
    print(f"   Configured providers: {list(config['providers'].keys())}")
    
    # Step 2: Initialize facade
    print("\n🔧 Step 2: Initialize facade with multiple providers")
    facade = UnifiedLLMFacade(config)
    print(f"   ✅ Facade initialized")
    
    # Step 3: List available providers
    print("\n🔍 Step 3: List all available providers")
    available_providers = facade.get_available_providers()
    print(f"   Available: {available_providers}")
    print(f"   Count: {len(available_providers)} provider(s)")
    
    # Step 4: Test each provider
    print("\n💬 Step 4: Test each provider with the same prompt")
    prompt = "Hello! Tell me about yourself in one sentence."
    print(f"   Prompt: '{prompt}'")
    print()
    
    for provider in available_providers:
        print(f"   Testing provider: {provider.upper()}")
        try:
            response = facade.complete(prompt, provider=provider)
            print(f"   ✅ Provider: {response.provider}")
            print(f"      Model: {response.model}")
            print(f"      Response: {response.text[:80]}...")
            print()
        except Exception as e:
            print(f"   ❌ Error with {provider}: {str(e)}")
            print()
    
    # Step 5: Compare responses
    print("\n📊 Step 5: Provider comparison")
    print("   Benefits of multiple providers:")
    print("   • Cost optimization - use cheaper models for simple tasks")
    print("   • Redundancy - fallback if one provider fails")
    print("   • Feature access - different providers have different capabilities")
    print("   • A/B testing - compare outputs from different models")
    
    # Step 6: Show provider switching
    print("\n🔄 Step 6: Switching providers dynamically")
    print("   # Use default provider:")
    print("   response = facade.complete(prompt)")
    print()
    print("   # Explicitly specify provider:")
    print("   response = facade.complete(prompt, provider='openai')")
    print("   response = facade.complete(prompt, provider='anthropic')")
    
    print("\n" + "=" * 70)
    print("✅ EXAMPLE COMPLETE!")
    print("=" * 70)
    
    print("\n💡 What we learned:")
    print("   • How to configure multiple providers")
    print("   • How to list available providers")
    print("   • How to test each provider")
    print("   • Benefits of using multiple providers")
    print("   • How to switch between providers dynamically")
    
    print("\n📚 Next steps:")
    print("   • Try example 06 for advanced provider switching")
    print("   • Try example 07 for error handling across providers")
    print("   • Add real provider API keys to test production providers")

if __name__ == "__main__":
    main()

"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.6
"""
