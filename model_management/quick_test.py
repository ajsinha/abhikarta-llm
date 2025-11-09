"""
Abhikarta LLM Model Registry System - Quick Test Script

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

This script performs quick validation tests on the registry implementations.
"""

import sys
from model_registry_db import ModelRegistryDB
from model_registry_json import ModelRegistryJSON
from model_management import ModelCapability
from exceptions import (
    ProviderNotFoundException,
    ModelNotFoundException,
    NoModelsAvailableException
)


def test_database_implementation():
    """Test the database implementation."""
    print("\n" + "=" * 70)
    print("DATABASE IMPLEMENTATION TEST")
    print("=" * 70)
    
    try:
        # Use in-memory database for testing
        print("\n1. Initializing in-memory database...")
        ModelRegistryDB.reset_instance()
        registry = ModelRegistryDB.get_instance(db_connection_pool_name=":memory:")
        print("   ✓ Database initialized")
        
        # Test auto-reload API
        print("\n2. Testing auto-reload API...")
        registry.start_auto_reload(interval_minutes=5)
        registry.stop_auto_reload()
        print("   ✓ Auto-reload API works (no-op for database)")
        
        # Test summary
        print("\n3. Getting registry summary...")
        summary = registry.get_registry_summary()
        print(f"   - Providers: {summary['provider_count']}")
        print(f"   - Total models: {summary['total_model_count']}")
        print("   ✓ Summary retrieved successfully")
        
        print("\n✅ DATABASE IMPLEMENTATION: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ DATABASE IMPLEMENTATION: TEST FAILED")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_json_implementation():
    """Test the JSON implementation."""
    print("\n" + "=" * 70)
    print("JSON IMPLEMENTATION TEST")
    print("=" * 70)
    
    import os
    import tempfile
    import json
    
    try:
        # Create temporary directory with test config
        print("\n1. Setting up temporary test directory...")
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test provider config
            test_config = {
                "provider": "test_provider",
                "api_base_url": "https://api.test.com",
                "enabled": True,
                "models": [
                    {
                        "name": "test-model",
                        "description": "A test model for validation",
                        "version": "1.0",
                        "enabled": True,
                        "context_window": 8192,
                        "max_output": 4096,
                        "input_cost_per_million": 1.0,
                        "output_cost_per_million": 2.0,
                        "supports_streaming": True,
                        "supports_function_calling": True,
                        "capabilities": {
                            "chat": True,
                            "streaming": True
                        },
                        "release_date": "2024-01-01"
                    }
                ]
            }
            
            config_path = os.path.join(tmpdir, "test_provider.json")
            with open(config_path, 'w') as f:
                json.dump(test_config, f)
            
            print(f"   ✓ Created test config: {config_path}")
            
            # Initialize registry
            print("\n2. Initializing JSON registry...")
            ModelRegistryJSON.reset_instance()
            registry = ModelRegistryJSON.get_instance(tmpdir)
            print("   ✓ Registry initialized")
            
            # Test auto-reload API
            print("\n3. Testing auto-reload API...")
            registry.start_auto_reload(interval_minutes=2)
            summary = registry.get_registry_summary()
            print(f"   - Auto-reload enabled: {summary['auto_reload_enabled']}")
            print(f"   - Interval: {summary['auto_reload_interval_minutes']} minutes")
            registry.stop_auto_reload()
            print("   ✓ Auto-reload API works")
            
            # Test provider query
            print("\n4. Testing provider query...")
            providers = registry.get_all_providers()
            print(f"   - Found {len(providers)} providers")
            if "test_provider" in providers:
                print("   ✓ Test provider loaded successfully")
            else:
                raise Exception("Test provider not found")
            
            # Test model query
            print("\n5. Testing model query...")
            provider = providers["test_provider"]
            models = provider.get_all_models()
            print(f"   - Found {len(models)} models")
            print("   ✓ Models loaded successfully")
            
            # Test capability validation method (NEW!)
            print("\n6. Testing capability validation method...")
            try:
                model = registry.get_model_from_provider_by_name_capability(
                    "test_provider",
                    "test-model",
                    "chat"
                )
                print(f"   ✓ Found model with chat capability: {model.name}")
            except NoModelsAvailableException:
                print("   ✗ Capability validation failed")
                raise
            
            # Test invalid capability
            print("\n7. Testing invalid capability handling...")
            try:
                model = registry.get_model_from_provider_by_name_capability(
                    "test_provider",
                    "test-model",
                    "vision"  # This should fail
                )
                print("   ✗ Should have raised exception")
                raise Exception("Expected NoModelsAvailableException")
            except NoModelsAvailableException:
                print("   ✓ Correctly raised NoModelsAvailableException")
        
        print("\n✅ JSON IMPLEMENTATION: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ JSON IMPLEMENTATION: TEST FAILED")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_consistency():
    """Test that both implementations have consistent APIs."""
    print("\n" + "=" * 70)
    print("API CONSISTENCY TEST")
    print("=" * 70)
    
    try:
        print("\n1. Checking method availability...")
        
        # Check ModelRegistryDB methods
        db_methods = [
            'get_provider_by_name',
            'get_all_providers',
            'get_model_from_provider_by_name',
            'get_model_from_provider_by_name_capability',  # NEW!
            'get_all_models_for_capability',
            'get_cheapest_model_for_capability',
            'start_auto_reload',  # NEW!
            'stop_auto_reload',   # NEW!
            'reload_from_storage',
            'enable_provider',
            'disable_provider',
            'enable_model',
            'disable_model',
            'get_provider_count',
            'get_total_model_count',
            'get_registry_summary'
        ]
        
        ModelRegistryDB.reset_instance()
        db_registry = ModelRegistryDB.get_instance(db_connection_pool_name=":memory:")
        
        missing_db = []
        for method in db_methods:
            if not hasattr(db_registry, method):
                missing_db.append(method)
        
        if missing_db:
            print(f"   ✗ Missing methods in ModelRegistryDB: {missing_db}")
            return False
        
        print("   ✓ ModelRegistryDB has all required methods")
        
        # Check ModelRegistryJSON methods
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            ModelRegistryJSON.reset_instance()
            json_registry = ModelRegistryJSON.get_instance(tmpdir)
            
            missing_json = []
            for method in db_methods:
                if not hasattr(json_registry, method):
                    missing_json.append(method)
            
            if missing_json:
                print(f"   ✗ Missing methods in ModelRegistryJSON: {missing_json}")
                return False
            
            print("   ✓ ModelRegistryJSON has all required methods")
        
        print("\n2. Verifying new methods...")
        print("   ✓ get_model_from_provider_by_name_capability - Available")
        print("   ✓ start_auto_reload - Available")
        print("   ✓ stop_auto_reload - Available")
        
        print("\n✅ API CONSISTENCY: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ API CONSISTENCY: TEST FAILED")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "ABHIKARTA MODEL REGISTRY QUICK TEST" + " " * 18 + "║")
    print("║" + " " * 20 + "Version 2.3 Validation" + " " * 25 + "║")
    print("╚" + "=" * 68 + "╝")
    
    results = {
        'database': test_database_implementation(),
        'json': test_json_implementation(),
        'api_consistency': test_api_consistency()
    }
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.upper():20s} {status}")
    
    print("\n" + "-" * 70)
    print(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - System is working correctly!")
        print("\nVersion 2.3 Features Verified:")
        print("  ✓ Auto-reload API (both implementations)")
        print("  ✓ Capability validation method")
        print("  ✓ API consistency across implementations")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED - Please check the errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
