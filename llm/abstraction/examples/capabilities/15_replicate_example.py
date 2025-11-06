"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.6

Example 15: Replicate Provider
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
llm_config_path = '/home/ashutosh/PycharmProjects/abhikarta-llm/config/llm_config.json'

from llm.abstraction.facade import UnifiedLLMFacade

def main():
    print("=" * 70 + "\nEXAMPLE 15: REPLICATE\n" + "=" * 70)
    
    # Replicate configuration
    config = {
        'providers': {
            'replicate': {
                'enabled': True,
                'api_key': os.getenv('REPLICATE_API_TOKEN', 'your-replicate-key'),
                'model': 'meta/llama-2-70b-chat'
            }
        }
    }
    
    try:
        facade = UnifiedLLMFacade(config)
        response = facade.complete("What is Replicate platform?")
        print(f"\nResponse: {response.text[:200]}...")
        print(f"\nModel: {response.model}")
        print("\n✅ Example completed!")
    except Exception as e:
        print(f"\n⚠️  Replicate not configured: {e}")
        print("\n💡 To use Replicate:")
        print("   1. Sign up at https://replicate.com")
        print("   2. Get API token")
        print("   3. Set REPLICATE_API_TOKEN environment variable")
        print("   4. Pay-per-use pricing")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.6"""
