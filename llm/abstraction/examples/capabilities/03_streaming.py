"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.6

Example 03: Streaming Responses
Demonstrates how to use streaming for real-time token-by-token responses
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
llm_config_path = '/home/ashutosh/PycharmProjects/abhikarta-llm/config/llm_config.json'

from llm.abstraction.facade import UnifiedLLMFacade
from llm.abstraction.utils.streaming import StreamHandler
import time

def main():
    """Example showing streaming responses for better UX"""
    
    print("=" * 70)
    print("EXAMPLE 03: STREAMING RESPONSES")
    print("=" * 70)
    
    # Step 1: Configure facade
    print("\n📝 Step 1: Configure facade for streaming")
    config = {
        'providers': {
            'mock': {
                'enabled': True,
                'model': 'mock-model'
            }
            # For real streaming, use providers like:
            # 'openai': {
            #     'enabled': True,
            #     'api_key': 'your-key',
            #     'model': 'gpt-4',
            #     'stream': True
            # }
        }
    }
    
    facade = UnifiedLLMFacade(config)
    print(f"   ✅ Facade configured for streaming")
    
    # Step 2: Create stream handler
    print("\n🔧 Step 2: Create StreamHandler")
    handler = StreamHandler()
    print(f"   ✅ StreamHandler created")
    
    # Step 3: Demonstrate streaming
    print("\n💬 Step 3: Stream a response")
    prompt = "Explain the benefits of streaming responses in LLM applications."
    print(f"   Prompt: '{prompt}'")
    print(f"\n   Streaming response:\n")
    print("   " + "-" * 60)
    print("   ", end='', flush=True)
    
    try:
        chunk_count = 0
        start_time = time.time()
        full_response = ""
        
        for chunk in facade.stream_complete(prompt):
            text = handler.process_chunk(chunk)
            if text:
                print(text, end='', flush=True)
                full_response += text
                chunk_count += 1
        
        elapsed = time.time() - start_time
        print("\n   " + "-" * 60)
        
        # Step 4: Show statistics
        print(f"\n📊 Step 4: Streaming statistics")
        print(f"   Chunks received: {chunk_count}")
        print(f"   Total characters: {len(full_response)}")
        print(f"   Time elapsed: {elapsed:.2f} seconds")
        if chunk_count > 0:
            print(f"   Average chunk size: {len(full_response) / chunk_count:.1f} chars")
        
    except Exception as e:
        print(f"\n   ⚠️  Note: {str(e)}")
        print(f"      Mock provider has limited streaming support")
        print(f"      Use real providers (OpenAI, Anthropic) for full streaming")
    
    # Step 5: Explain benefits
    print(f"\n💡 Step 5: Why use streaming?")
    print(f"   Benefits of streaming responses:")
    print(f"   • Better UX - Users see responses as they're generated")
    print(f"   • Lower latency - Time to first token is faster")
    print(f"   • Interruption - Can cancel long responses early")
    print(f"   • Feedback - Show progress indicators during generation")
    
    # Step 6: Show usage patterns
    print(f"\n🎯 Step 6: Common streaming patterns")
    print(f"   ")
    print(f"   # Basic streaming:")
    print(f"   for chunk in facade.stream_complete(prompt):")
    print(f"       text = handler.process_chunk(chunk)")
    print(f"       print(text, end='', flush=True)")
    print(f"   ")
    print(f"   # With error handling:")
    print(f"   try:")
    print(f"       for chunk in facade.stream_complete(prompt):")
    print(f"           process_chunk(chunk)")
    print(f"   except StreamingError as e:")
    print(f"       handle_error(e)")
    
    print("\n" + "=" * 70)
    print("✅ EXAMPLE COMPLETE!")
    print("=" * 70)
    
    print("\n💡 What we learned:")
    print("   • How to configure streaming")
    print("   • How to use StreamHandler")
    print("   • How to process streaming chunks")
    print("   • Benefits of streaming responses")
    print("   • Common streaming patterns")
    
    print("\n📚 Next steps:")
    print("   • Try with real providers (OpenAI, Anthropic) for full streaming")
    print("   • Implement custom streaming UIs")
    print("   • Add progress indicators and cancellation")

if __name__ == "__main__":
    main()

"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.6
"""
