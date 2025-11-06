"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.6

Example 09: Batch Requests
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
llm_config_path = '/home/ashutosh/PycharmProjects/abhikarta-llm/config/llm_config.json'

from llm.abstraction.facade import UnifiedLLMFacade

def main():
    print("=" * 70 + "\nEXAMPLE 09: BATCH REQUESTS\n" + "=" * 70)
    
    config = {
        'providers': {
            'mock': {
                'enabled': True,
                'model': 'mock-model'
            }
        }
    }
    
    facade = UnifiedLLMFacade(config)
    
    print("\n📦 Processing Multiple Prompts")
    
    # Define multiple prompts
    prompts = [
        "What is Python?",
        "What is JavaScript?",
        "What is Java?",
        "What is C++?",
        "What is Go?"
    ]
    
    print(f"\n🔄 Processing {len(prompts)} prompts...")
    
    # Process batch
    results = []
    for i, prompt in enumerate(prompts, 1):
        print(f"\n{i}. {prompt}")
        response = facade.complete(prompt, max_tokens=50)
        results.append({
            'prompt': prompt,
            'response': response.text,
            'tokens': response.metadata.get('total_tokens', 0)
        })
        print(f"   Answer: {response.text[:60]}...")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Batch Processing Summary")
    print("=" * 70)
    
    total_tokens = sum(r['tokens'] for r in results)
    print(f"\nTotal prompts:  {len(results)}")
    print(f"Total tokens:   {total_tokens}")
    print(f"Average tokens: {total_tokens // len(results)}")
    
    print("\n💡 Batch Processing Tips:")
    print("   • Process multiple requests efficiently")
    print("   • Use async/parallel processing for speed")
    print("   • Monitor rate limits")
    print("   • Handle errors gracefully")
    print("   • Track costs and usage")
    
    print("\n📝 Use Cases:")
    print("   • Data classification")
    print("   • Bulk translation")
    print("   • Content generation")
    print("   • Sentiment analysis")
    print("   • Question answering")
    
    print("\n✅ Example completed!")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.6"""
