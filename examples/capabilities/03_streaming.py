"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.0.1

Example 03: Streaming Responses
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from llm.abstraction.facade import UnifiedLLMFacade
from llm.abstraction.utils.streaming import StreamHandler

print("="*70)
print("EXAMPLE 03: STREAMING")
print("="*70)

config = {'providers': {'mock': {'enabled': True}}}
facade = UnifiedLLMFacade(config)

handler = StreamHandler()
print("\nStreaming: ", end='', flush=True)

try:
    for chunk in facade.stream_complete("Tell me about AI"):
        text = handler.process_chunk(chunk)
        print(text, end='', flush=True)
except:
    print("Note: Streaming not available for mock provider")

print("\n\n✅ EXAMPLE COMPLETE!")

"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | ajsinha@gmail.com | Version: 3.0.1
"""
