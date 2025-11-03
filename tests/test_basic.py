"""
Basic tests for LLM Abstraction System

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.abstraction import LLMClientFactory, LLMException


def test_factory_initialization():
    """Test factory initialization"""
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    print("✓ Factory initialization successful")


def test_mock_provider():
    """Test mock provider"""
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    
    client = factory.create_client(provider='mock', model='mock-model')
    assert client is not None
    print("✓ Mock provider client created successfully")


def test_completion():
    """Test completion"""
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    
    client = factory.create_mock_client()
    response = client.complete("Hello, world!")
    
    assert response is not None
    assert len(response) > 0
    print(f"✓ Completion test passed: {response[:50]}...")


def test_chat():
    """Test chat"""
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    
    client = factory.create_mock_client()
    response = client.chat("What is AI?")
    
    assert response is not None
    assert len(response) > 0
    print(f"✓ Chat test passed: {response[:50]}...")


def test_streaming():
    """Test streaming"""
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    
    client = factory.create_mock_client()
    
    tokens = []
    for token in client.stream_complete("Test prompt"):
        tokens.append(token)
    
    assert len(tokens) > 0
    print(f"✓ Streaming test passed: received {len(tokens)} tokens")


def test_history():
    """Test history management"""
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    
    client = factory.create_mock_client()
    
    # Make some interactions
    client.complete("First prompt")
    client.chat("Second message")
    
    # Check history
    stats = client.get_history_summary()
    assert stats['total_interactions'] == 2
    print(f"✓ History test passed: {stats['total_interactions']} interactions recorded")


def test_multi_model():
    """Test multiple models"""
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    
    client1 = factory.create_client(provider='mock', model='mock-model')
    client2 = factory.create_client(provider='mock', model='mock-advanced')
    
    assert client1.model_name == 'mock-model'
    assert client2.model_name == 'mock-advanced'
    print("✓ Multi-model test passed")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running Abhikarta LLM Abstraction Tests")
    print("=" * 60)
    print()
    
    tests = [
        ("Factory Initialization", test_factory_initialization),
        ("Mock Provider", test_mock_provider),
        ("Completion", test_completion),
        ("Chat", test_chat),
        ("Streaming", test_streaming),
        ("History Management", test_history),
        ("Multi-Model", test_multi_model),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"Testing {name}...", end=" ")
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ FAILED: {str(e)}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
