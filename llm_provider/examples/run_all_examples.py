"""
Run All Facade Examples

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

This script runs examples for all provider facades, demonstrating runtime config switching.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config_switcher import ConfigSwitcher


def print_header(title):
    """Print a formatted header."""
    width = 70
    print("\n" + "╔" + "="*(width-2) + "╗")
    print("║" + title.center(width-2) + "║")
    print("╚" + "="*(width-2) + "╝\n")


def run_provider_example(module_name, provider_name):
    """Run a single provider example."""
    try:
        print_header(f"{provider_name} EXAMPLES")
        
        # Import and run the example
        module = __import__(module_name)
        module.run_all_examples()
        
        return True
        
    except Exception as e:
        print(f"✗ Error running {provider_name} examples: {e}")
        return False


def main():
    """Run all examples."""
    print_header("ABHIKARTA MODEL FACADES - ALL EXAMPLES")
    
    print("🎯 This demonstrates:")
    print("   • All 13 provider facades")
    print("   • Runtime config switching (JSON/DB)")
    print("   • Provider-specific features")
    print("   • Error handling")
    print("\n" + "="*70)
    
    # Check config mode
    config_mode = os.getenv("CONFIG_MODE", "json")
    print(f"\n📁 Configuration mode: {config_mode.upper()}")
    print("   (Set CONFIG_MODE=db to use database configuration)")
    
    # List of all provider examples
    examples = [
        ("example_anthropic", "ANTHROPIC (Claude)"),
        ("example_openai", "OPENAI (GPT)"),
        ("example_google", "GOOGLE (Gemini)"),
        ("example_cohere", "COHERE"),
        ("example_mistral", "MISTRAL"),
        ("example_groq", "GROQ"),
        ("example_meta", "META (Llama)"),
        ("example_huggingface", "HUGGINGFACE"),
        ("example_together", "TOGETHER AI"),
        ("example_ollama", "OLLAMA (Local)"),
        ("example_awsbedrock", "AWS BEDROCK"),
        ("example_mock", "MOCK (Testing)")
    ]
    
    # Track results
    results = {}
    
    # Run each example
    for module_name, provider_name in examples:
        success = run_provider_example(module_name, provider_name)
        results[provider_name] = success
        
        if not success:
            print(f"\n⚠️  {provider_name} examples failed - continuing with others...")
    
    # Print summary
    print_header("SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"Results: {passed}/{total} providers succeeded\n")
    
    for provider, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {provider}")
    
    print("\n" + "="*70)
    
    if passed == total:
        print("\n🎉 All examples completed successfully!")
    else:
        print(f"\n⚠️  {total - passed} provider(s) had errors")
        print("   This is normal if API keys are not configured")
    
    print("\n💡 Tip: Use the mock provider to test without API keys:")
    print("   python example_mock.py")


if __name__ == "__main__":
    main()
