"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.0.1

Example 01: Basic Usage
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from llm.abstraction.facade import UnifiedLLMFacade

print("="*70)
print("EXAMPLE 01: BASIC USAGE")
print("="*70)

config = {'providers': {'mock': {'enabled': True, 'model': 'mock-model'}}}

facade = UnifiedLLMFacade(config)
print(f"\n✅ Providers: {facade.get_available_providers()}")

response = facade.complete("What is AI?")
print(f"✅ Response: {response.text[:80]}...")

print("\n✅ EXAMPLE COMPLETE!")

"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | ajsinha@gmail.com | Version: 3.0.1
"""
