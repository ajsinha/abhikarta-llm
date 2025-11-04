"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.6

Example 06: Provider Switching
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from llm.abstraction.facade import UnifiedLLMFacade

def main():
    print("=" * 70 + "\nEXAMPLE 06: PROVIDER SWITCHING\n" + "=" * 70)
    
    # Configure multiple providers
    config = {
        'providers': {
            'mock': {
                'enabled': True,
                'model': 'mock-model'
            }
            # In production, add other providers:
            # 'openai': {'enabled': True, 'api_key': '...', 'model': 'gpt-4'},
            # 'anthropic': {'enabled': True, 'api_key': '...', 'model': 'claude-3-opus'},
        },
        'default_provider': 'mock'
    }
    
    facade = UnifiedLLMFacade(config)
    prompt = "What is artificial intelligence?"
    
    print("\n🔄 Switching Between Providers")
    
    # Use default provider
    print("\n1️⃣ Using default provider:")
    response = facade.complete(prompt)
    print(f"   Provider: {response.provider}")
    print(f"   Model: {response.model}")
    print(f"   Response: {response.text[:80]}...")
    
    # Explicitly specify provider
    print("\n2️⃣ Explicitly using 'mock' provider:")
    response = facade.complete(prompt, provider='mock')
    print(f"   Provider: {response.provider}")
    print(f"   Model: {response.model}")
    print(f"   Response: {response.text[:80]}...")
    
    print("\n💡 Provider Switching Benefits:")
    print("   • Cost optimization (use cheaper models for simple tasks)")
    print("   • Fallback (switch if primary provider fails)")
    print("   • A/B testing (compare model outputs)")
    print("   • Feature access (use specific provider features)")
    
    print("\n📝 Usage Pattern:")
    print("   # Use default")
    print("   response = facade.complete(prompt)")
    print()
    print("   # Specify provider")
    print("   response = facade.complete(prompt, provider='openai')")
    print("   response = facade.complete(prompt, provider='anthropic')")
    
    print("\n✅ Example completed!")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.6"""
