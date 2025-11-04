"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.6

Example 10: Provider Information
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from llm.abstraction.facade import UnifiedLLMFacade
from llm.abstraction.providers import PROVIDER_REGISTRY

def main():
    print("=" * 70 + "\nEXAMPLE 10: PROVIDER INFORMATION\n" + "=" * 70)
    
    print("\n🔌 Available Providers")
    print("=" * 70)
    
    # List all providers
    for i, (name, provider_class) in enumerate(PROVIDER_REGISTRY.items(), 1):
        print(f"\n{i:2d}. {name:15s} - {provider_class.__name__}")
    
    print(f"\n📊 Total: {len(PROVIDER_REGISTRY)} providers")
    
    # Configure and show active provider
    config = {
        'providers': {
            'mock': {
                'enabled': True,
                'model': 'mock-model'
            }
        }
    }
    
    facade = UnifiedLLMFacade(config)
    
    print("\n" + "=" * 70)
    print("🎯 Active Configuration")
    print("=" * 70)
    
    # Make a test request
    response = facade.complete("Hello!")
    
    print(f"\nActive Provider: {response.provider}")
    print(f"Model:          {response.model}")
    print(f"Response:       {response.text[:50]}...")
    
    print("\n" + "=" * 70)
    print("📋 Provider Categories")
    print("=" * 70)
    
    print("\n☁️  Cloud Providers (8):")
    cloud = ['openai', 'anthropic', 'google', 'awsbedrock', 'cohere', 'groq', 'mistral', 'together']
    for p in cloud:
        if p in PROVIDER_REGISTRY:
            print(f"   • {p}")
    
    print("\n🏠 Self-Hosted (4):")
    selfhosted = ['ollama', 'huggingface', 'replicate', 'meta']
    for p in selfhosted:
        if p in PROVIDER_REGISTRY:
            print(f"   • {p}")
    
    print("\n🧪 Testing (1):")
    print("   • mock")
    
    print("\n💡 Provider Selection Guide:")
    print("   • OpenAI: Best overall quality (GPT-4)")
    print("   • Anthropic: Long context (Claude)")
    print("   • Google: Fast and affordable (Gemini)")
    print("   • AWS Bedrock: Enterprise (multiple models)")
    print("   • Ollama: Local and private")
    print("   • Mock: Testing without API keys")
    
    print("\n✅ Example completed!")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.6"""
