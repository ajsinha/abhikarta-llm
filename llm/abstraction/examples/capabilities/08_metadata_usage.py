"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.6

Example 08: Metadata and Usage Statistics
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
llm_config_path = '/home/ashutosh/PycharmProjects/abhikarta-llm/config/llm_config.json'

from llm.abstraction.facade import UnifiedLLMFacade

def main():
    print("=" * 70 + "\nEXAMPLE 08: METADATA AND USAGE STATISTICS\n" + "=" * 70)
    
    config = {
        'providers': {
            'mock': {
                'enabled': True,
                'model': 'mock-model'
            }
        }
    }
    
    facade = UnifiedLLMFacade(config)
    
    print("\n📊 Response Metadata")
    
    # Make a request
    prompt = "Explain quantum computing in simple terms."
    response = facade.complete(prompt, temperature=0.7, max_tokens=200)
    
    print(f"\n✅ Response received!")
    print(f"\n📝 Content:")
    print(f"   {response.text[:100]}...")
    
    print(f"\n🏷️  Metadata:")
    print(f"   Provider:      {response.provider}")
    print(f"   Model:         {response.model}")
    print(f"   Finish Reason: {response.finish_reason}")
    
    print(f"\n💰 Token Usage:")
    print(f"   Prompt Tokens:     {response.metadata.get('prompt_tokens', 0)}")
    print(f"   Completion Tokens: {response.metadata.get('completion_tokens', 0)}")
    print(f"   Total Tokens:      {response.metadata.get('total_tokens', 0)}")
    
    print(f"\n🔍 Additional Info:")
    if response.metadata:
        for key, value in response.metadata.items():
            print(f"   {key}: {value}")
    
    print("\n💡 Using Metadata:")
    print("   • Track costs (tokens × price)")
    print("   • Monitor usage patterns")
    print("   • Debug model behavior")
    print("   • Optimize prompts")
    
    print("\n📝 Finish Reasons:")
    print("   • stop: Completed naturally")
    print("   • length: Hit max_tokens limit")
    print("   • content_filter: Content filtered")
    print("   • function_call: Called a function")
    
    print("\n✅ Example completed!")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.6"""
