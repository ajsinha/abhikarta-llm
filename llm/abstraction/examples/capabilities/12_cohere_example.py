"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.6

Example 12: Cohere Provider
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
llm_config_path = '/home/ashutosh/PycharmProjects/abhikarta-llm/config/llm_config.json'

from llm.abstraction.facade import UnifiedLLMFacade

def main():
    print("=" * 70 + "\nEXAMPLE 12: COHERE\n" + "=" * 70)
    
    # Cohere configuration
    config = {
        'providers': {
            'cohere': {
                'enabled': True,
                'api_key': os.getenv('COHERE_API_KEY', 'your-cohere-key'),
                'model': 'command',
                'temperature': 0.7
            }
        }
    }
    
    try:
        facade = UnifiedLLMFacade(config)
        response = facade.complete("What makes Cohere unique?")
        print(f"\nResponse: {response.text[:200]}...")
        print(f"\nModel: {response.model}")
        print("\n✅ Example completed!")
    except Exception as e:
        print(f"\n⚠️  Cohere not configured: {e}")
        print("\n💡 To use Cohere:")
        print("   1. Sign up at https://cohere.ai")
        print("   2. Get API key")
        print("   3. Set COHERE_API_KEY environment variable")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.6"""
