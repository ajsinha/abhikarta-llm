"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.6

Example 13: HuggingFace Provider
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
llm_config_path = '/home/ashutosh/PycharmProjects/abhikarta-llm/config/llm_config.json'

from llm.abstraction.facade import UnifiedLLMFacade

def main():
    print("=" * 70 + "\nEXAMPLE 13: HUGGINGFACE\n" + "=" * 70)
    
    # HuggingFace configuration
    model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
    config = {
        'providers': {
            'huggingface': {
                'enabled': True,
                'api_key': os.getenv('HUGGINGFACE_API_KEY', 'your-hf-key'),
                'model': {'name': model_id},
                'endpoint': 'https://api-inference.huggingface.co'
            }
        }
    }
    
    try:
        facade = UnifiedLLMFacade(config)
        response = facade.complete("Explain transformers in AI:")
        print(f"\nResponse: {response.text[:200]}...")
        print(f"\nModel: {response.model}")
        print("\n✅ Example completed!")
    except Exception as e:
        print(f"\n⚠️  HuggingFace not configured: {e}")
        print("\n💡 To use HuggingFace:")
        print("   1. Sign up at https://huggingface.co")
        print("   2. Get API token")
        print("   3. Set HUGGINGFACE_API_KEY environment variable")
        print("   4. Choose from 100,000+ models")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.6"""
