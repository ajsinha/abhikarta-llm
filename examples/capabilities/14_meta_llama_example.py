"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.3

Example 14: Meta Llama Provider (Direct)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from llm.abstraction.facade import UnifiedLLMFacade

def main():
    print("=" * 70 + "\nEXAMPLE 14: META LLAMA (DIRECT)\n" + "=" * 70)
    
    # Meta Llama configuration (requires local model)
    config = {
        'providers': {
            'meta': {
                'enabled': True,
                'model': 'llama-2-7b',
                'model_path': '/path/to/llama-2-7b-chat'
            }
        }
    }
    
    try:
        facade = UnifiedLLMFacade(config)
        response = facade.complete("What is Llama?")
        print(f"\nResponse: {response.text[:200]}...")
        print(f"\nModel: {response.model}")
        print("\n✅ Example completed!")
    except Exception as e:
        print(f"\n⚠️  Meta Llama not configured: {e}")
        print("\n💡 To use Meta Llama:")
        print("   1. Download Llama models from Meta")
        print("   2. Accept license agreement")
        print("   3. Set model_path to local directory")
        print("   4. Or use Ollama/HuggingFace instead")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.3"""
