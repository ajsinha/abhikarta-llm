#!/usr/bin/env python3
"""
Diagnostic script for langchain-ollama installation issues.
Run this in your virtual environment to check the installation status.

Usage:
    python diagnose_langchain_ollama.py
"""

import sys
import importlib.util

def main():
    print("=" * 60)
    print("LangChain-Ollama Diagnostic Tool")
    print("=" * 60)
    print()
    
    # Check Python version
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print()
    
    # Check if langchain_ollama is in sys.path
    print("Checking langchain-ollama installation...")
    print("-" * 40)
    
    # Method 1: importlib.util.find_spec
    spec = importlib.util.find_spec('langchain_ollama')
    if spec is None:
        print("❌ langchain_ollama NOT FOUND via importlib.util.find_spec")
        print("   The package may not be installed.")
    else:
        print(f"✓ langchain_ollama found at: {spec.origin}")
    
    # Method 2: Try direct import
    print()
    print("Attempting direct import...")
    print("-" * 40)
    try:
        import langchain_ollama
        print(f"✓ Successfully imported langchain_ollama")
        print(f"  Package location: {langchain_ollama.__file__}")
        if hasattr(langchain_ollama, '__version__'):
            print(f"  Version: {langchain_ollama.__version__}")
    except ImportError as e:
        print(f"❌ ImportError: {e}")
    except TypeError as e:
        print(f"❌ TypeError (likely Pydantic/Python version issue): {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
    
    # Method 3: Try importing ChatOllama specifically
    print()
    print("Attempting to import ChatOllama...")
    print("-" * 40)
    try:
        from langchain_ollama import ChatOllama
        print("✓ Successfully imported ChatOllama")
    except ImportError as e:
        print(f"❌ ImportError: {e}")
    except TypeError as e:
        print(f"❌ TypeError: {e}")
        print("   This is likely a Pydantic version compatibility issue.")
        print("   Try: pip install 'pydantic>=2.5.0,<3.0.0'")
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
    
    # Check related packages
    print()
    print("Checking related packages...")
    print("-" * 40)
    
    packages_to_check = [
        'langchain',
        'langchain_core',
        'langchain_community',
        'pydantic',
        'ollama',
    ]
    
    for pkg in packages_to_check:
        try:
            mod = importlib.import_module(pkg)
            version = getattr(mod, '__version__', 'unknown')
            print(f"✓ {pkg}: {version}")
        except ImportError:
            print(f"❌ {pkg}: NOT INSTALLED")
        except Exception as e:
            print(f"⚠ {pkg}: Error - {e}")
    
    # Recommendations
    print()
    print("=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    print("""
If langchain-ollama is not found:
    pip install langchain-ollama

If you see TypeError related to 'subscriptable':
    This is a Python 3.14 / Pydantic compatibility issue.
    Use Python 3.12 or 3.13 instead.

If you see other ImportErrors:
    1. First uninstall conflicting packages:
       pip uninstall langchain-ollama langchain langchain-core -y
    
    2. Then reinstall with compatible versions:
       pip install "langchain>=0.2.0,<0.4.0" "langchain-core>=0.2.0,<0.4.0"
       pip install langchain-ollama ollama
    
    3. Verify installation:
       pip show langchain-ollama

If the package is installed but still fails:
    Check for namespace conflicts or corrupted installation:
       pip install --force-reinstall langchain-ollama
""")

if __name__ == '__main__':
    main()
