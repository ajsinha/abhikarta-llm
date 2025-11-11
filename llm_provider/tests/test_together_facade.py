"""
Test Suite for Together LLM Facade

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This module and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Description:
Comprehensive test suite for the Together LLM Facade implementation.
"""

import os
import sys
import pytest

sys.path.append('/home/claude/llm_facades')
sys.path.append('/mnt/user-data/uploads')

from together_facade import TogetherLLMFacade, create_together_llm
from llm_facade import ModelCapability, GenerationConfig

TEST_MODEL = "meta-llama/Llama-3-8b-chat-hf"
ENV_VAR = "TOGETHER_API_KEY"


@pytest.fixture
def llm():
    """Create LLM instance for testing."""
    if ENV_VAR != "None" and not os.getenv(ENV_VAR):
        pytest.skip(f"{ENV_VAR} not set")
    return TogetherLLMFacade(model_name=TEST_MODEL)


def test_initialization():
    """Test initialization."""
    if ENV_VAR != "None" and not os.getenv(ENV_VAR):
        pytest.skip(f"{ENV_VAR} not set")
    
    llm = TogetherLLMFacade(model_name=TEST_MODEL)
    assert llm.model_name == TEST_MODEL
    assert llm.provider_name == "together"
    print(f"✓ Initialized {llm.model_name}")


def test_model_info(llm):
    """Test getting model info."""
    info = llm.get_model_info()
    assert info['name'] == TEST_MODEL
    assert info['provider'] == "together"
    print(f"✓ Model info: {info}")


def test_capabilities(llm):
    """Test capability detection."""
    caps = llm.get_capabilities()
    assert len(caps) > 0
    assert llm.supports_capability(ModelCapability.TEXT_GENERATION)
    print(f"✓ Capabilities: {[c.value for c in caps]}")


def test_text_generation(llm):
    """Test text generation."""
    response = llm.text_generation(
        prompt="Say hello",
        config=GenerationConfig(max_tokens=10)
    )
    assert response
    print(f"✓ Generated: {str(response)[:50]}")


def test_chat_completion(llm):
    """Test chat completion."""
    response = llm.chat_completion(
        messages=[{"role": "user", "content": "Hi"}],
        config=GenerationConfig(max_tokens=10)
    )
    assert "content" in response
    print(f"✓ Chat response: {response['content'][:50]}")


def test_conversation(llm):
    """Test conversation management."""
    conv = llm.start_conversation()
    response = llm.continue_conversation(conv, "Hello")
    assert len(conv["messages"]) == 2
    print(f"✓ Conversation: {response[:50]}")


def test_factory():
    """Test factory function."""
    if ENV_VAR != "None" and not os.getenv(ENV_VAR):
        pytest.skip(f"{ENV_VAR} not set")
    
    llm = create_together_llm(TEST_MODEL)
    assert isinstance(llm, TogetherLLMFacade)
    print("✓ Factory function works")


if __name__ == "__main__":
    print(f"\n============================================================")
    print(f"Together LLM Facade Tests")
    print(f"============================================================\n")
    
    if ENV_VAR != "None" and not os.getenv(ENV_VAR):
        print(f"⚠ Skipping tests - {ENV_VAR} not set")
    else:
        try:
            test_initialization()
            llm = TogetherLLMFacade(model_name=TEST_MODEL)
            test_model_info(llm)
            test_capabilities(llm)
            test_text_generation(llm)
            test_chat_completion(llm)
            test_conversation(llm)
            test_factory()
            print("\n✓ All tests passed!")
        except Exception as e:
            print(f"\n✗ Test failed: {e}")
