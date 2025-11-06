"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.6

Example 05: Parameters - Temperature and Control
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
llm_config_path = '/home/ashutosh/PycharmProjects/abhikarta-llm/config/llm_config.json'

from llm.abstraction.facade import UnifiedLLMFacade

def main():
    print("=" * 70 + "\nEXAMPLE 05: PARAMETERS - TEMPERATURE AND CONTROL\n" + "=" * 70)
    
    config = {
        'providers': {
            'mock': {
                'enabled': True,
                'model': 'mock-model'
            }
        }
    }
    
    facade = UnifiedLLMFacade(config)
    prompt = "Write a creative story about a robot."
    
    print("\n🎛️  Temperature Controls Randomness")
    
    # Low temperature (deterministic)
    print("\n1️⃣ Temperature 0.0 (Deterministic):")
    response = facade.complete(prompt, temperature=0.0, max_tokens=100)
    print(f"   Response: {response.text[:80]}...")
    
    # Medium temperature (balanced)
    print("\n2️⃣ Temperature 0.7 (Balanced - Default):")
    response = facade.complete(prompt, temperature=0.7, max_tokens=100)
    print(f"   Response: {response.text[:80]}...")
    
    # High temperature (creative)
    print("\n3️⃣ Temperature 1.0 (Creative):")
    response = facade.complete(prompt, temperature=1.0, max_tokens=100)
    print(f"   Response: {response.text[:80]}...")
    
    print("\n📊 Other Parameters:")
    print("   • max_tokens: Limits response length")
    print("   • top_p: Nucleus sampling (alternative to temperature)")
    print("   • frequency_penalty: Reduces repetition")
    print("   • presence_penalty: Encourages topic diversity")
    
    print("\n💡 Temperature Guide:")
    print("   • 0.0-0.3: Focused, deterministic (factual tasks)")
    print("   • 0.4-0.7: Balanced (general use)")
    print("   • 0.8-1.0: Creative, diverse (creative writing)")
    print("   • 1.0+: Very random (experimental)")
    
    print("\n✅ Example completed!")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.6"""
