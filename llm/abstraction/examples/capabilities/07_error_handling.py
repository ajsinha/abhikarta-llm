"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.6

Example 07: Error Handling
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
llm_config_path = '/home/ashutosh/PycharmProjects/abhikarta-llm/config/llm_config.json'

from llm.abstraction.facade import UnifiedLLMFacade

def main():
    print("=" * 70 + "\nEXAMPLE 07: ERROR HANDLING\n" + "=" * 70)
    
    config = {
        'providers': {
            'mock': {
                'enabled': True,
                'model': 'mock-model'
            }
        }
    }
    
    facade = UnifiedLLMFacade(config)
    
    print("\n🛡️  Robust Error Handling")
    
    # Example 1: Normal operation
    print("\n1️⃣ Normal Operation:")
    try:
        response = facade.complete("Hello!")
        print(f"   ✅ Success: {response.text[:50]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Example 2: Empty prompt
    print("\n2️⃣ Empty Prompt:")
    try:
        response = facade.complete("")
        print(f"   ✅ Success: {response.text[:50]}...")
    except ValueError as e:
        print(f"   ❌ Caught ValueError: {e}")
    except Exception as e:
        print(f"   ❌ Caught Exception: {e}")
    
    # Example 3: Invalid provider
    print("\n3️⃣ Invalid Provider:")
    try:
        response = facade.complete("Test", provider='nonexistent')
        print(f"   ✅ Success: {response.text[:50]}...")
    except ValueError as e:
        print(f"   ❌ Caught ValueError: {e}")
    except Exception as e:
        print(f"   ❌ Caught Exception: {e}")
    
    print("\n💡 Error Handling Best Practices:")
    print("   • Always use try-except blocks")
    print("   • Catch specific exceptions (ValueError, ConnectionError)")
    print("   • Log errors for debugging")
    print("   • Implement retry logic for transient failures")
    print("   • Provide fallback behavior")
    
    print("\n📝 Common Errors:")
    print("   • ValueError: Invalid parameters or configuration")
    print("   • ConnectionError: Network issues")
    print("   • TimeoutError: Request took too long")
    print("   • AuthenticationError: Invalid API key")
    
    print("\n✅ Example completed!")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.6"""
