"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.6

Example 04: Chat Messages with History
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from llm.abstraction.facade import UnifiedLLMFacade

def main():
    print("=" * 70 + "\nEXAMPLE 04: CHAT MESSAGES WITH HISTORY\n" + "=" * 70)
    
    # Configure provider (using mock for demo)
    config = {
        'providers': {
            'mock': {
                'enabled': True,
                'model': 'mock-model'
            }
        }
    }
    
    print("\n📝 Chat with Message History")
    print("\nConversation:")
    
    facade = UnifiedLLMFacade(config)
    
    # Build conversation history
    messages = [
        {'role': 'system', 'content': 'You are a helpful AI assistant.'},
        {'role': 'user', 'content': 'What is Python?'},
        {'role': 'assistant', 'content': 'Python is a high-level programming language.'},
        {'role': 'user', 'content': 'What are its main features?'}
    ]
    
    # Display conversation
    for msg in messages:
        role = msg['role'].upper()
        content = msg['content']
        print(f"\n{role}: {content}")
    
    # Get response with history
    print("\n" + "-" * 70)
    print("Sending chat with message history...")
    
    response = facade.chat(messages)
    
    print(f"\nASSISTANT: {response.text}")
    print(f"\nModel: {response.model}")
    print(f"Provider: {response.provider}")
    print(f"Tokens used: {response.metadata.get('total_tokens', 0)}")
    
    print("\n💡 Key Points:")
    print("   • Messages include role and content")
    print("   • Roles: 'system', 'user', 'assistant'")
    print("   • System messages set behavior")
    print("   • History provides context")
    
    print("\n✅ Example completed!")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.6"""
