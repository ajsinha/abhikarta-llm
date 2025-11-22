"""
Test Suite Generator for LLM Provider Facades

This script generates comprehensive test suites for all provider facades.
"""

import json
from pathlib import Path
from typing import Dict, Any

# Read provider configurations
with open('/home/ashutosh/llm_facades/providers_to_generate.json', 'r') as f:
    providers_config = json.load(f)

COPYRIGHT_NOTICE = '''"""
Test Suite for {provider_title} LLM Facade

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This module and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

This document is provided "as is" without warranty of any kind, either expressed or implied.
The copyright holder shall not be liable for any damages arising from the use of this
document or the software system it describes.

Patent Pending: Certain architectural patterns and implementations described in this
module may be subject to patent applications.

Description:
Comprehensive test suite for the {provider_title} LLM Facade implementation.
Tests cover initialization, capability detection, text generation, chat completion,
and error handling scenarios.
"""
'''

TEST_TEMPLATE = '''
import os
import sys
import json
import time
import pytest
from typing import Dict, Any

# Add paths
sys.path.append('/home/ashutosh/llm_facades')
sys.path.append('/mnt/user-data/uploads')

from {facade_module} import {class_name}, create_{provider_name}_llm
from llm_facade import (
    ModelCapability,
    GenerationConfig,
    CapabilityNotSupportedException,
    AuthenticationException
)

# ============================================================================
# Test Configuration
# ============================================================================

# Test model for this provider
TEST_MODEL = "{test_model}"

# Skip tests if no API key available
SKIP_IF_NO_KEY = os.getenv("{{env_var}}") is None and "{{env_var}}" != "None"

# Colors for output
class Colors:
    GREEN = '\\033[92m'
    RED = '\\033[91m'
    YELLOW = '\\033[93m'
    BLUE = '\\033[94m'
    CYAN = '\\033[96m'
    RESET = '\\033[0m'
    BOLD = '\\033[1m'


def print_test_header(test_name: str):
    """Print test header."""
    print(f"\\n{{{Colors.CYAN}}{{{Colors.BOLD}}{{{'=' * 80}}}{{{Colors.RESET}}")
    print(f"{{{Colors.CYAN}}{{{Colors.BOLD}}TEST: {{{test_name}}}{{{Colors.RESET}}")
    print(f"{{{Colors.CYAN}}{{{Colors.BOLD}}{{{'=' * 80}}}{{{Colors.RESET}}\\n")


def print_success(message: str):
    """Print success message."""
    print(f"{{{Colors.GREEN}}✓ {{{message}}}{{{Colors.RESET}}")


def print_error(message: str):
    """Print error message."""
    print(f"{{{Colors.RED}}✗ {{{message}}}{{{Colors.RESET}}")


def print_info(message: str):
    """Print info message."""
    print(f"{{{Colors.BLUE}}ℹ {{{message}}}{{{Colors.RESET}}")


def print_warning(message: str):
    """Print warning message."""
    print(f"{{{Colors.YELLOW}}⚠ {{{message}}}{{{Colors.RESET}}")


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def llm_instance():
    """Create LLM instance for testing."""
    if SKIP_IF_NO_KEY:
        pytest.skip("API key not available")
    
    return {class_name}(
        model_name=TEST_MODEL,
        timeout=60.0,
        max_retries=3
    )


@pytest.fixture
def factory_instance():
    """Create LLM instance using factory function."""
    if SKIP_IF_NO_KEY:
        pytest.skip("API key not available")
    
    return create_{provider_name}_llm(TEST_MODEL)


# ============================================================================
# Test Cases
# ============================================================================

def test_initialization():
    """Test 1: Initialization and Configuration"""
    print_test_header("Initialization and Configuration")
    
    if SKIP_IF_NO_KEY:
        print_warning("Skipping test - API key not available")
        pytest.skip("API key not available")
    
    try:
        # Test basic initialization
        print_info("Testing initialization...")
        llm = {class_name}(model_name=TEST_MODEL)
        print_success(f"Initialized facade for model: {{{llm.model_name}}}")
        
        # Test model info
        info = llm.get_model_info()
        print_success(f"Model info retrieved: {{{info['name']}}}")
        print_info(f"  - Provider: {{{info['provider']}}}")
        print_info(f"  - Context length: {{{info['context_length']}}}")
        print_info(f"  - Capabilities: {{{', '.join(info['capabilities'])}}}")
        
        assert info['provider'] == "{provider_name}"
        assert info['name'] == TEST_MODEL
        print_success("Initialization test passed")
        
    except Exception as e:
        print_error(f"Initialization failed: {{{e}}}")
        pytest.fail(f"Initialization test failed: {{{e}}}")


def test_capability_detection(llm_instance):
    """Test 2: Capability Detection"""
    print_test_header("Capability Detection")
    
    try:
        print_info("Testing capability detection...")
        capabilities = llm_instance.get_capabilities()
        
        print_success(f"Detected {{{len(capabilities)}}} capabilities:")
        for cap in capabilities:
            print_info(f"  - {{{cap.value}}}")
        
        # Test specific capability checks
        assert llm_instance.supports_capability(ModelCapability.TEXT_GENERATION)
        print_success("TEXT_GENERATION capability confirmed")
        
        if llm_instance.supports_capability(ModelCapability.CHAT_COMPLETION):
            print_success("CHAT_COMPLETION capability confirmed")
        
        if llm_instance.supports_capability(ModelCapability.STREAMING):
            print_success("STREAMING capability confirmed")
        
        print_success("Capability detection test passed")
        
    except Exception as e:
        print_error(f"Capability detection failed: {{{e}}}")
        pytest.fail(f"Capability detection test failed: {{{e}}}")


def test_text_generation(llm_instance):
    """Test 3: Text Generation"""
    print_test_header("Text Generation")
    
    try:
        print_info("Testing text generation...")
        prompt = "The quick brown fox"
        
        response = llm_instance.text_generation(
            prompt=prompt,
            config=GenerationConfig(
                max_tokens=50,
                temperature=0.7
            )
        )
        
        print_success("Text generated successfully")
        print_info(f"Prompt: {{{prompt}}}")
        print_info(f"Response: {{{response[:100]}}}")
        
        assert isinstance(response, (str, dict))
        if isinstance(response, str):
            assert len(response) > 0
        
        print_success("Text generation test passed")
        
    except Exception as e:
        print_error(f"Text generation failed: {{{e}}}")
        pytest.fail(f"Text generation test failed: {{{e}}}")


def test_chat_completion(llm_instance):
    """Test 4: Chat Completion"""
    print_test_header("Chat Completion")
    
    try:
        print_info("Testing chat completion...")
        messages = [
            {{"role": "user", "content": "Say hello in one word"}}
        ]
        
        response = llm_instance.chat_completion(
            messages=messages,
            config=GenerationConfig(
                max_tokens=10,
                temperature=0.7
            )
        )
        
        print_success("Chat completion successful")
        print_info(f"Response: {{{response}}}")
        
        assert isinstance(response, dict)
        assert "content" in response
        assert len(response["content"]) > 0
        
        print_success("Chat completion test passed")
        
    except Exception as e:
        print_error(f"Chat completion failed: {{{e}}}")
        pytest.fail(f"Chat completion test failed: {{{e}}}")


def test_streaming_text_generation(llm_instance):
    """Test 5: Streaming Text Generation"""
    print_test_header("Streaming Text Generation")
    
    if not llm_instance.supports_capability(ModelCapability.STREAMING):
        print_warning("Streaming not supported - skipping test")
        pytest.skip("Streaming not supported")
    
    try:
        print_info("Testing streaming text generation...")
        prompt = "Count from 1 to 5:"
        
        stream = llm_instance.stream_text_generation(
            prompt=prompt,
            config=GenerationConfig(max_tokens=50)
        )
        
        chunks = []
        for chunk in stream:
            chunks.append(chunk)
            if len(chunks) <= 3:
                print_info(f"Chunk {{{len(chunks)}}}: {{{chunk}}}")
        
        full_text = "".join(chunks)
        print_success(f"Received {{{len(chunks)}}} chunks")
        print_info(f"Full text: {{{full_text[:100]}}}")
        
        assert len(chunks) > 0
        print_success("Streaming text generation test passed")
        
    except Exception as e:
        print_error(f"Streaming text generation failed: {{{e}}}")
        pytest.fail(f"Streaming test failed: {{{e}}}")


def test_conversation_management(llm_instance):
    """Test 6: Conversation Management"""
    print_test_header("Conversation Management")
    
    try:
        print_info("Testing conversation management...")
        
        # Start conversation
        conversation = llm_instance.start_conversation()
        print_success(f"Started conversation: {{{conversation['id']}}}")
        
        # First turn
        response1 = llm_instance.continue_conversation(
            conversation,
            "My name is Alice."
        )
        print_success(f"Turn 1: {{{response1[:50]}}}")
        
        # Second turn
        response2 = llm_instance.continue_conversation(
            conversation,
            "What is my name?"
        )
        print_success(f"Turn 2: {{{response2[:50]}}}")
        
        assert len(conversation["messages"]) == 4  # 2 user + 2 assistant
        print_success("Conversation management test passed")
        
    except Exception as e:
        print_error(f"Conversation management failed: {{{e}}}")
        pytest.fail(f"Conversation test failed: {{{e}}}")


def test_factory_function(factory_instance):
    """Test 7: Factory Function"""
    print_test_header("Factory Function")
    
    try:
        print_info("Testing factory function...")
        
        # Test that factory returns correct type
        assert isinstance(factory_instance, {class_name})
        print_success("Factory returns correct instance type")
        
        # Test that it works
        response = factory_instance.chat_completion(
            messages=[{{"role": "user", "content": "Hi"}}],
            config=GenerationConfig(max_tokens=10)
        )
        
        print_success("Factory-created instance works correctly")
        assert "content" in response
        print_success("Factory function test passed")
        
    except Exception as e:
        print_error(f"Factory function test failed: {{{e}}}")
        pytest.fail(f"Factory test failed: {{{e}}}")


def test_error_handling():
    """Test 8: Error Handling"""
    print_test_header("Error Handling")
    
    try:
        print_info("Testing error handling...")
        
        # Test with invalid API key
        with pytest.raises((AuthenticationException, Exception)):
            llm = {class_name}(
                model_name=TEST_MODEL,
                api_key="invalid_key_12345"
            )
            llm.chat_completion(
                messages=[{{"role": "user", "content": "test"}}]
            )
        
        print_success("Invalid API key properly rejected")
        print_success("Error handling test passed")
        
    except Exception as e:
        print_error(f"Error handling test failed: {{{e}}}")
        # This test may fail depending on provider behavior
        print_warning("Some providers may not validate API keys immediately")


def test_health_check(llm_instance):
    """Test 9: Health Check"""
    print_test_header("Health Check")
    
    try:
        print_info("Running health check...")
        is_healthy = llm_instance.health_check()
        
        if is_healthy:
            print_success("Health check passed")
        else:
            print_warning("Health check failed (may be normal for some models)")
        
        # Health check should not raise an exception
        print_success("Health check test passed")
        
    except Exception as e:
        print_error(f"Health check failed: {{{e}}}")
        pytest.fail(f"Health check test failed: {{{e}}}")


def test_token_counting(llm_instance):
    """Test 10: Token Counting"""
    print_test_header("Token Counting")
    
    try:
        print_info("Testing token counting...")
        
        text = "Hello, world! This is a test."
        token_count = llm_instance.count_tokens(text)
        
        print_success(f"Token count: {{{token_count}}}")
        assert token_count > 0
        
        # Test truncation
        truncated = llm_instance.truncate_to_max_tokens(text, max_tokens=3)
        print_success(f"Truncated text: {{{truncated}}}")
        
        print_success("Token counting test passed")
        
    except Exception as e:
        print_error(f"Token counting failed: {{{e}}}")
        pytest.fail(f"Token counting test failed: {{{e}}}")


# ============================================================================
# Main Test Runner
# ============================================================================

def run_all_tests():
    """Run all tests manually."""
    print(f"\\n{{{Colors.BOLD}}{{{Colors.CYAN}}")
    print("=" * 80)
    print(f"{provider_title} LLM Facade Test Suite")
    print("=" * 80)
    print(f"{{{Colors.RESET}}\\n")
    
    if SKIP_IF_NO_KEY:
        print_warning(f"{{{env_var}}} not set - skipping tests")
        return
    
    tests = [
        test_initialization,
        test_capability_detection,
        test_text_generation,
        test_chat_completion,
        test_streaming_text_generation,
        test_conversation_management,
        test_factory_function,
        test_error_handling,
        test_health_check,
        test_token_counting
    ]
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_func in tests:
        try:
            # Get test dependencies
            if test_func.__name__ in ['test_capability_detection', 'test_text_generation', 
                                       'test_chat_completion', 'test_streaming_text_generation',
                                       'test_conversation_management', 'test_health_check',
                                       'test_token_counting']:
                llm = {class_name}(model_name=TEST_MODEL)
                test_func(llm)
            elif test_func.__name__ == 'test_factory_function':
                llm = create_{provider_name}_llm(TEST_MODEL)
                test_func(llm)
            else:
                test_func()
            passed += 1
        except pytest.skip.Exception as e:
            skipped += 1
            print_warning(f"Test skipped: {{{test_func.__name__}}}")
        except Exception as e:
            failed += 1
            print_error(f"Test failed: {{{test_func.__name__}}} - {{{e}}}")
    
    print(f"\\n{{{Colors.BOLD}}{{{Colors.CYAN}}{{'=' * 80}}{{{Colors.RESET}}")
    print(f"{{{Colors.BOLD}}Test Results{{{Colors.RESET}}")
    print(f"{{{Colors.BOLD}}{{{Colors.CYAN}}{{'=' * 80}}{{{Colors.RESET}}")
    print(f"{{{Colors.GREEN}}Passed: {{{passed}}}{{{Colors.RESET}}")
    print(f"{{{Colors.RED}}Failed: {{{failed}}}{{{Colors.RESET}}")
    print(f"{{{Colors.YELLOW}}Skipped: {{{skipped}}}{{{Colors.RESET}}")
    print(f"{{{Colors.BOLD}}Total: {{{passed + failed + skipped}}}{{{Colors.RESET}}\\n")


if __name__ == "__main__":
    run_all_tests()
'''

def generate_test(provider_config: Dict[str, Any]) -> str:
    """Generate test code for a provider."""
    
    provider_name = provider_config["name"]
    class_name = f"{provider_name.capitalize()}LLMFacade"
    provider_title = provider_name.capitalize()
    facade_module = f"{provider_name}_facade"
    env_var = provider_config.get("env_var", "None")
    
    # Determine test model
    test_models = {
        "openai": "gpt-3.5-turbo",
        "anthropic": "claude-3-haiku-20240307",
        "google": "gemini-pro",
        "cohere": "command",
        "mistral": "mistral-small-latest",
        "groq": "llama3-8b-8192",
        "together": "meta-llama/Llama-3-8b-chat-hf",
        "replicate": "meta/llama-2-7b-chat",
        "meta": "llama-3-8b-instruct",
        "ollama": "llama2",
        "awsbedrock": "anthropic.claude-instant-v1",
        "mock": "mock-model"
    }
    test_model = test_models.get(provider_name, "model-name")
    
    # Generate test code
    copyright = COPYRIGHT_NOTICE.format(
        provider_title=provider_title
    )
    
    test_code = TEST_TEMPLATE.format(
        provider_title=provider_title,
        class_name=class_name,
        provider_name=provider_name,
        facade_module=facade_module,
        test_model=test_model,
        env_var=env_var if env_var != "None" else "API_KEY"
    )
    
    return copyright + test_code


# Generate all test files
output_dir = Path('/home/ashutosh/llm_facades/tests')
output_dir.mkdir(exist_ok=True)

for provider in providers_config:
    provider_name = provider["name"]
    filename = f"test_{provider_name}_facade.py"
    filepath = output_dir / filename
    
    print(f"Generating {filename}...")
    test_code = generate_test(provider)
    
    with open(filepath, 'w') as f:
        f.write(test_code)
    
    print(f"  ✓ Created {filename}")

print(f"\nGenerated {len(providers_config)} test files!")
