"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.0.1

Example 04: New Providers (Groq, Mistral, Together, Ollama)
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

print("="*70)
print("EXAMPLE 04: NEW PROVIDERS")
print("="*70)

providers_info = {
    'groq': {
        'name': 'Groq',
        'speed': 'Ultra-fast (500+ tok/s)',
        'cost': '$',
        'key_env': 'GROQ_API_KEY',
        'model': 'mixtral-8x7b-32768'
    },
    'mistral': {
        'name': 'Mistral AI',
        'speed': 'Fast',
        'cost': '$$',
        'key_env': 'MISTRAL_API_KEY',
        'model': 'mistral-small'
    },
    'together': {
        'name': 'Together AI',
        'speed': 'Fast',
        'cost': '$',
        'key_env': 'TOGETHER_API_KEY',
        'model': 'meta-llama/Llama-2-70b-chat-hf'
    },
    'ollama': {
        'name': 'Ollama',
        'speed': 'Medium',
        'cost': 'FREE (Local)',
        'key_env': 'None (local)',
        'model': 'llama2'
    }
}

print("\nNew Providers in v3.0.1:\n")
for provider, info in providers_info.items():
    print(f"✅ {info['name']}")
    print(f"   Speed: {info['speed']}")
    print(f"   Cost: {info['cost']}")
    print(f"   API Key: {info['key_env']}")
    print(f"   Model: {info['model']}")
    print()

print("To use:")
print("  export GROQ_API_KEY='your-key'")
print("  config = {'providers': {'groq': {'enabled': True}}}")

print("\n✅ EXAMPLE COMPLETE!")

"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | ajsinha@gmail.com | Version: 3.0.1
"""
