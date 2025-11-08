"""
Model CRUD Operations Test Suite

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

This script tests all CRUD operations for both database and JSON implementations.
"""

import sys
import os
import tempfile
import json
from model_registry_db import ModelRegistryDB
from model_registry_json import ModelRegistryJSON
from exceptions import (
    ModelAlreadyExistsException,
    ModelNotFoundException,
    ProviderNotFoundException
)


def test_create_operations():
    """Test model creation operations."""
    print("\n" + "=" * 70)
    print("TESTING CREATE OPERATIONS")
    print("=" * 70)
    
    # Create a temporary database
    print("\n1. Testing Database Implementation...")
    ModelRegistryDB.reset_instance()
    db_registry = ModelRegistryDB.get_instance(db_path=":memory:")
    
    # Create a test provider first
    provider_data = {
        "provider": "test_provider",
        "api_base_url": "https://api.test.com",
        "enabled": True,
        "models": []
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(provider_data, f)
        temp_file = f.name
    
    try:
        db_registry.load_json_file(temp_file)
        
        # Create a new model
        model_data = {
            'name': 'test-model-v1',
            'description': 'Test model for CRUD operations',
            'version': '1.0',
            'enabled': True,
            'context_window': 8192,
            'max_output': 4096,
            'cost': {
                'input_per_1m': 1.0,
                'output_per_1m': 2.0
            },
            'supports_streaming': True,
            'supports_function_calling': True,
            'capabilities': {
                'chat': True,
                'streaming': True
            },
            'strengths': ['Fast inference', 'Good reasoning'],
            'release_date': '2024-01-01'
        }
        
        model = db_registry.create_model('test_provider', model_data)
        print(f"   ✓ Created model: {model.name}")
        print(f"   ✓ Version: {model.version}")
        print(f"   ✓ Context window: {model.context_window:,} tokens")
        
        # Try to create duplicate (should fail)
        try:
            db_registry.create_model('test_provider', model_data)
            print("   ✗ Should have raised ModelAlreadyExistsException")
            return False
        except ModelAlreadyExistsException as e:
            print(f"   ✓ Correctly prevented duplicate: {e.model_name}")
        
    finally:
        os.unlink(temp_file)
    
    # Test JSON implementation
    print("\n2. Testing JSON Implementation...")
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create provider config
        config_file = os.path.join(tmpdir, "test_provider.json")
        with open(config_file, 'w') as f:
            json.dump(provider_data, f)
        
        ModelRegistryJSON.reset_instance()
        json_registry = ModelRegistryJSON.get_instance(tmpdir)
        
        model = json_registry.create_model('test_provider', model_data)
        print(f"   ✓ Created model: {model.name}")
        
        # Verify it was written to file
        with open(config_file, 'r') as f:
            data = json.load(f)
            assert len(data['models']) == 1
            print("   ✓ Model persisted to JSON file")
    
    print("\n✅ CREATE OPERATIONS: ALL TESTS PASSED")
    return True


def test_update_operations():
    """Test model update operations."""
    print("\n" + "=" * 70)
    print("TESTING UPDATE OPERATIONS")
    print("=" * 70)
    
    # Setup
    ModelRegistryDB.reset_instance()
    registry = ModelRegistryDB.get_instance(db_path=":memory:")
    
    provider_data = {
        "provider": "test_provider",
        "api_base_url": "https://api.test.com",
        "enabled": True,
        "models": [{
            'name': 'test-model',
            'description': 'Original description',
            'version': '1.0',
            'enabled': True,
            'context_window': 8192,
            'max_output': 4096,
            'cost': {'input_per_1m': 1.0, 'output_per_1m': 2.0},
            
            'supports_streaming': True,
            'supports_function_calling': True,
            'capabilities': {'chat': True},
            'strengths': ['Original strength'],
            'release_date': '2024-01-01'
        }]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(provider_data, f)
        temp_file = f.name
    
    try:
        registry.load_json_file(temp_file)
        
        # Test basic property updates
        print("\n1. Testing basic property updates...")
        
        model = registry.update_model_description(
            'test_provider',
            'test-model',
            'Updated description'
        )
        assert model.description == 'Updated description'
        print("   ✓ Description updated")
        
        model = registry.update_model_version('test_provider', 'test-model', '2.0')
        assert model.version == '2.0'
        print("   ✓ Version updated")
        
        model = registry.update_model_context_window('test_provider', 'test-model', 16384)
        assert model.context_window == 16384
        print("   ✓ Context window updated")
        
        model = registry.update_model_max_output('test_provider', 'test-model', 8192)
        assert model.max_output == 8192
        print("   ✓ Max output updated")
        
        model = registry.update_model_costs('test_provider', 'test-model', 0.5, 1.0)
        assert model.cost.get('input_per_1m') == 0.5
        assert model.cost.get('output_per_1m') == 1.0
        print("   ✓ Costs updated")
        
        # Test capability management
        print("\n2. Testing capability management...")
        
        model = registry.add_model_capability('test_provider', 'test-model', 'vision', True)
        assert model.has_capability('vision')
        print("   ✓ Capability added")
        
        model = registry.update_model_capability('test_provider', 'test-model', 'vision', False)
        assert model.capabilities.get('vision') == False
        print("   ✓ Capability updated")
        
        model = registry.remove_model_capability('test_provider', 'test-model', 'vision')
        assert not model.has_capability('vision')
        print("   ✓ Capability removed")
        
        new_caps = {'chat': True, 'streaming': True, 'function_calling': True}
        model = registry.update_model_capabilities('test_provider', 'test-model', new_caps)
        assert model.capabilities == new_caps
        print("   ✓ All capabilities replaced")
        
        # Test strength management
        print("\n3. Testing strength management...")
        
        model = registry.add_model_strength('test_provider', 'test-model', 'New strength')
        assert 'New strength' in model.strengths
        print("   ✓ Strength added")
        
        model = registry.remove_model_strength('test_provider', 'test-model', 'Original strength')
        assert 'Original strength' not in model.strengths
        print("   ✓ Strength removed")
        
        new_strengths = ['Strength 1', 'Strength 2', 'Strength 3']
        model = registry.update_model_strengths('test_provider', 'test-model', new_strengths)
        assert model.strengths == new_strengths
        print("   ✓ All strengths replaced")
        
        # Test batch update
        print("\n4. Testing batch update...")
        
        updates = {
            'description': 'Batch updated',
            'version': '3.0',
            'context_window': 32768
        }
        model = registry.update_model('test_provider', 'test-model', updates)
        assert model.description == 'Batch updated'
        assert model.version == '3.0'
        assert model.context_window == 32768
        print("   ✓ Batch update successful")
        
        # Test validation
        print("\n5. Testing validation...")
        
        try:
            registry.update_model_context_window('test_provider', 'test-model', -1)
            print("   ✗ Should have raised ValueError for negative context window")
            return False
        except ValueError:
            print("   ✓ Negative context window rejected")
        
        try:
            registry.update_model_costs('test_provider', 'test-model', -1.0, 2.0)
            print("   ✗ Should have raised ValueError for negative cost")
            return False
        except ValueError:
            print("   ✓ Negative cost rejected")
        
    finally:
        os.unlink(temp_file)
    
    print("\n✅ UPDATE OPERATIONS: ALL TESTS PASSED")
    return True


def test_delete_operations():
    """Test model deletion operations."""
    print("\n" + "=" * 70)
    print("TESTING DELETE OPERATIONS")
    print("=" * 70)
    
    # Setup
    ModelRegistryDB.reset_instance()
    registry = ModelRegistryDB.get_instance(db_path=":memory:")
    
    provider_data = {
        "provider": "test_provider",
        "api_base_url": "https://api.test.com",
        "enabled": True,
        "models": [{
            'name': 'model-to-delete',
            'description': 'Will be deleted',
            'version': '1.0',
            'enabled': True,
            'context_window': 8192,
            'max_output': 4096,
            'cost': {'input_per_1m': 1.0, 'output_per_1m': 2.0},
            
            'supports_streaming': True,
            'supports_function_calling': True,
            'capabilities': {'chat': True},
            'release_date': '2024-01-01'
        }]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(provider_data, f)
        temp_file = f.name
    
    try:
        registry.load_json_file(temp_file)
        
        print("\n1. Verifying model exists...")
        model = registry.get_model_from_provider_by_name('test_provider', 'model-to-delete')
        print(f"   ✓ Model exists: {model.name}")
        
        print("\n2. Deleting model...")
        registry.delete_model('test_provider', 'model-to-delete')
        print("   ✓ Delete operation completed")
        
        print("\n3. Verifying model was deleted...")
        try:
            model = registry.get_model_from_provider_by_name('test_provider', 'model-to-delete')
            print("   ✗ Model should not exist")
            return False
        except ModelNotFoundException:
            print("   ✓ Model successfully deleted")
        
        print("\n4. Testing delete of non-existent model...")
        try:
            registry.delete_model('test_provider', 'non-existent-model')
            print("   ✗ Should have raised ModelNotFoundException")
            return False
        except ModelNotFoundException:
            print("   ✓ Correctly raised exception for non-existent model")
        
    finally:
        os.unlink(temp_file)
    
    print("\n✅ DELETE OPERATIONS: ALL TESTS PASSED")
    return True


def test_json_persistence():
    """Test that JSON changes persist to file."""
    print("\n" + "=" * 70)
    print("TESTING JSON PERSISTENCE")
    print("=" * 70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create initial config
        provider_data = {
            "provider": "test_provider",
            "api_base_url": "https://api.test.com",
            "enabled": True,
            "models": []
        }
        
        config_file = os.path.join(tmpdir, "test_provider.json")
        with open(config_file, 'w') as f:
            json.dump(provider_data, f)
        
        print("\n1. Creating model...")
        ModelRegistryJSON.reset_instance()
        registry = ModelRegistryJSON.get_instance(tmpdir)
        
        model_data = {
            'name': 'persistent-model',
            'description': 'Test persistence',
            'version': '1.0',
            'enabled': True,
            'context_window': 8192,
            'max_output': 4096,
            'cost': {'input_per_1m': 1.0, 'output_per_1m': 2.0},
            
            'supports_streaming': True,
            'supports_function_calling': True,
            'capabilities': {'chat': True},
            'release_date': '2024-01-01'
        }
        
        registry.create_model('test_provider', model_data)
        print("   ✓ Model created")
        
        print("\n2. Verifying file was updated...")
        with open(config_file, 'r') as f:
            data = json.load(f)
        
        assert len(data['models']) == 1
        assert data['models'][0]['name'] == 'persistent-model'
        print("   ✓ Model persisted to file")
        
        print("\n3. Updating model...")
        registry.update_model_version('test_provider', 'persistent-model', '2.0')
        
        with open(config_file, 'r') as f:
            data = json.load(f)
        
        assert data['models'][0]['version'] == '2.0'
        print("   ✓ Update persisted to file")
        
        print("\n4. Deleting model...")
        registry.delete_model('test_provider', 'persistent-model')
        
        with open(config_file, 'r') as f:
            data = json.load(f)
        
        assert len(data['models']) == 0
        print("   ✓ Delete persisted to file")
    
    print("\n✅ JSON PERSISTENCE: ALL TESTS PASSED")
    return True


def main():
    """Run all CRUD tests."""
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "MODEL CRUD OPERATIONS TEST SUITE" + " " * 16 + "║")
    print("║" + " " * 25 + "Version 2.4" + " " * 32 + "║")
    print("╚" + "=" * 68 + "╝")
    
    results = {
        'create': test_create_operations(),
        'update': test_update_operations(),
        'delete': test_delete_operations(),
        'persistence': test_json_persistence()
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
    print(f"TOTAL: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\n🎉 ALL CRUD TESTS PASSED!")
        print("\nVersion 2.4 CRUD Operations Verified:")
        print("  ✓ Create operations (1 method)")
        print("  ✓ Update operations (15 methods)")
        print("  ✓ Delete operations (1 method)")
        print("  ✓ JSON persistence")
        print("  ✓ Database integration")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED - Please check the errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
