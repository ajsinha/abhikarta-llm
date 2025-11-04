"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.0.1

Example 02: Multiple Providers
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from llm.abstraction.facade import UnifiedLLMFacade

print("="*70)
print("EXAMPLE 02: MULTIPLE PROVIDERS")
print("="*70)

config = {'providers': {'mock': {'enabled': True}}}
facade = UnifiedLLMFacade(config)

for provider in facade.get_available_providers():
    print(f"\n{provider.upper()}:")
    response = facade.complete("Hello", provider=provider)
    print(f"  {response.text[:60]}...")

print("\n✅ EXAMPLE COMPLETE!")

"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | ajsinha@gmail.com | Version: 3.0.1
"""
