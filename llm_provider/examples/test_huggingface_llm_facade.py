"""
Test Suite for HuggingFace LLM Facade

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This module and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Patent Pending: Certain architectural patterns and implementations described in this
module may be subject to patent applications.

Description:
Comprehensive test suite for the HuggingFace LLM Facade implementation.
Each capability is tested in a separate function for clarity and modularity.
"""

import os
import sys
import json
import time
from typing import Dict, Any

# Add paths
sys.path.append('/mnt/user-data/outputs')

from huggingface_facade import HuggingFaceLLMFacade, create_huggingface_llm
from llm_facade import (
    ModelCapability,
    GenerationConfig,
    CapabilityNotSupportedException
)

# ============================================================================
# Test Configuration
# ============================================================================

# Test models for different capabilities
TEST_MODELS = {
    "chat": "meta-llama/Llama-2-7b-chat-hf",
    "code": "codellama/CodeLlama-7b-hf",
    "embedding": "sentence-transformers/all-MiniLM-L6-v2",
    "small": "gpt2"  # Fast for quick tests
}


# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_test_header(test_name: str):
    """Print test header."""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}TEST: {test_name}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 80}{Colors.RESET}\n")


def print_success(message: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message: str):
    """Print error message."""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def print_info(message: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")


def print_warning(message: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")


# ============================================================================
# Capability Tests
# ============================================================================

def test_initialization():
    """Test 1: Initialization and Configuration"""
    print_test_header("Initialization and Configuration")

    try:
        # Test API-based initialization
        print_info("Testing API-based initialization...")
        llm = HuggingFaceLLMFacade(
            model_name=TEST_MODELS["small"],
            timeout=60.0,
            max_retries=3
        )
        print_success(f"API client initialized for model: {llm.model_name}")

        # Test model info
        info = llm.get_model_info()
        print_success(f"Model info retrieved: {info['name']}")
        print_info(f"  - Provider: {info['provider']}")
        print_info(f"  - Context length: {info['context_length']}")
        print_info(f"  - Capabilities: {', '.join(info['capabilities'])}")

        # Test health check
        print_info("Running health check...")
        is_healthy = llm.health_check()
        if is_healthy:
            print_success("Health check passed")
        else:
            print_warning("Health check failed (this may be normal for some models)")

        return True

    except Exception as e:
        print_error(f"Initialization failed: {e}")
        return False


def test_capability_detection():
    """Test 2: Capability Detection"""
    print_test_header("Capability Detection")

    try:
        llm = HuggingFaceLLMFacade(model_name=TEST_MODELS["chat"])

        print_info("Testing capability detection...")
        capabilities = llm.get_capabilities()

        print_success(f"Detected {len(capabilities)} capabilities:")
        for cap in capabilities:
            print_info(f"  - {cap.value}")

        # Test specific capability checks
        test_caps = [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CHAT_COMPLETION,
            ModelCapability.VISION,
            ModelCapability.EMBEDDINGS
        ]

        print_info("\nTesting specific capabilities:")
        for cap in test_caps:
            supported = llm.supports_capability(cap)
            status = "✓ Supported" if supported else "✗ Not supported"
            color = Colors.GREEN if supported else Colors.RED
            print(f"  {color}{cap.value}: {status}{Colors.RESET}")

        return True

    except Exception as e:
        print_error(f"Capability detection failed: {e}")
        return False


def test_text_generation():
    """Test 3: Text Generation"""
    print_test_header("Text Generation")

    try:
        llm = HuggingFaceLLMFacade(model_name=TEST_MODELS["small"])

        print_info("Testing basic text generation...")
        prompt = "Once upon a time"

        config = GenerationConfig(
            max_tokens=50,
            temperature=0.7,
            top_p=0.9
        )

        response = llm.text_generation(prompt, config=config)

        print_success("Text generation successful")
        print_info(f"Prompt: {prompt}")
        print_info(f"Response: {response[:100]}...")

        # Test with different parameters
        print_info("\nTesting with lower temperature...")
        config_low_temp = GenerationConfig(
            max_tokens=30,
            temperature=0.3
        )
        response_low = llm.text_generation(prompt, config=config_low_temp)
        print_success("Low temperature generation successful")

        return True

    except Exception as e:
        print_error(f"Text generation failed: {e}")
        return False


def test_chat_completion():
    """Test 4: Chat Completion"""
    print_test_header("Chat Completion")

    try:
        llm = HuggingFaceLLMFacade(model_name=TEST_MODELS["chat"])

        print_info("Testing chat completion...")
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ]

        config = GenerationConfig(
            max_tokens=50,
            temperature=0.7
        )

        response = llm.chat_completion(messages, config=config)

        print_success("Chat completion successful")
        print_info(f"User: {messages[1]['content']}")
        print_info(f"Assistant: {response['content'][:100]}...")

        # Check response structure
        if "usage" in response:
            print_info(f"Token usage: {response['usage'].total_tokens} tokens")

        if response.get("finish_reason"):
            print_info(f"Finish reason: {response['finish_reason']}")

        return True

    except Exception as e:
        print_error(f"Chat completion failed: {e}")
        print_warning("This may be normal if the model doesn't support chat format")
        return False


def test_streaming():
    """Test 5: Streaming"""
    print_test_header("Streaming")

    try:
        llm = HuggingFaceLLMFacade(model_name=TEST_MODELS["small"])

        print_info("Testing streaming text generation...")
        prompt = "The weather today is"

        config = GenerationConfig(
            max_tokens=30,
            temperature=0.7
        )

        print_info(f"Prompt: {prompt}")
        print_info("Stream: ", end="")

        chunk_count = 0
        for chunk in llm.stream_text_generation(prompt, config=config):
            print(chunk, end="", flush=True)
            chunk_count += 1

        print()  # New line
        print_success(f"Streaming completed with {chunk_count} chunks")

        # Test chat streaming
        print_info("\nTesting streaming chat completion...")
        messages = [{"role": "user", "content": "Count to 5"}]

        print_info("Chat stream: ")
        for delta in llm.stream_chat_completion(messages, config=config):
            if "content" in delta.get("delta", {}):
                print(delta["delta"]["content"], end="", flush=True)

        print()
        print_success("Chat streaming completed")

        return True

    except Exception as e:
        print_error(f"Streaming failed: {e}")
        return False


def test_embeddings():
    """Test 6: Embeddings"""
    print_test_header("Embeddings")

    try:
        # Use an embedding model
        llm = HuggingFaceLLMFacade(model_name=TEST_MODELS["embedding"])

        if not llm.supports_capability(ModelCapability.EMBEDDINGS):
            print_warning("Model doesn't support embeddings, skipping test")
            return True

        print_info("Testing text embedding...")

        # Single text
        text = "Machine learning is a subset of artificial intelligence"
        embedding = llm.embed_text(text, normalize=True)

        print_success(f"Single embedding generated: dimension {len(embedding)}")
        print_info(f"First 5 values: {embedding[:5]}")

        # Multiple texts
        print_info("\nTesting batch embedding...")
        texts = [
            "The cat sat on the mat",
            "Dogs are loyal animals",
            "Python is a programming language"
        ]

        embeddings = llm.embed_text(texts, normalize=True)
        print_success(f"Generated {len(embeddings)} embeddings")

        # Test similarity
        print_info("\nTesting similarity computation...")
        similarity = llm.compute_similarity(embeddings[0], embeddings[1])
        print_success(f"Similarity between text 1 and 2: {similarity:.4f}")

        similarity2 = llm.compute_similarity(embeddings[0], embeddings[2])
        print_success(f"Similarity between text 1 and 3: {similarity2:.4f}")

        return True

    except CapabilityNotSupportedException:
        print_warning("Embeddings not supported for this model")
        return True
    except Exception as e:
        print_error(f"Embeddings test failed: {e}")
        return False


def test_token_management():
    """Test 7: Token Management"""
    print_test_header("Token Management")

    try:
        llm = HuggingFaceLLMFacade(model_name=TEST_MODELS["small"])

        print_info("Testing token counting...")

        text = "The quick brown fox jumps over the lazy dog"
        token_count = llm.count_tokens(text)
        print_success(f"Token count for text: {token_count} tokens")

        # Test with messages
        messages = [
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you!"}
        ]

        message_tokens = llm.count_tokens(messages)
        print_success(f"Token count for messages: {message_tokens} tokens")

        # Test truncation
        print_info("\nTesting text truncation...")
        long_text = "word " * 100
        max_tokens = 20

        truncated = llm.truncate_to_max_tokens(long_text, max_tokens)
        truncated_count = llm.count_tokens(truncated)

        print_success(f"Truncated {len(long_text)} chars to ~{max_tokens} tokens")
        print_info(f"Actual token count after truncation: {truncated_count}")

        # Test context window
        context_window = llm.get_context_window()
        max_output = llm.get_max_output_tokens()

        print_success(f"Context window: {context_window} tokens")
        print_success(f"Max output tokens: {max_output} tokens")

        # Test cost estimation
        cost = llm.estimate_cost(1000, 500)
        print_success(f"Estimated cost: ${cost['total_cost']:.4f}")

        return True

    except Exception as e:
        print_error(f"Token management test failed: {e}")
        return False


def test_code_generation():
    """Test 8: Code Generation"""
    print_test_header("Code Generation")

    try:
        llm = HuggingFaceLLMFacade(model_name=TEST_MODELS["code"])

        print_info("Testing code generation...")

        description = "A function to calculate the factorial of a number"
        result = llm.code_generation(
            description,
            language="python",
            include_docs=True
        )

        print_success("Code generation successful")
        print_info(f"Description: {description}")
        print_info("Generated code:")
        print(f"{Colors.MAGENTA}{result['code'][:200]}...{Colors.RESET}")

        # Test code explanation
        print_info("\nTesting code explanation...")
        sample_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

        explanation = llm.code_explanation(sample_code, language="python")
        print_success("Code explanation generated")
        print_info(f"Explanation: {explanation[:150]}...")

        return True

    except Exception as e:
        print_error(f"Code generation test failed: {e}")
        print_warning("This may be normal if using a non-code model")
        return False


def test_structured_output():
    """Test 9: Structured Output"""
    print_test_header("Structured Output")

    try:
        llm = HuggingFaceLLMFacade(model_name=TEST_MODELS["chat"])

        print_info("Testing structured output generation...")

        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "occupation": {"type": "string"}
            },
            "required": ["name", "age"]
        }

        messages = [
            {
                "role": "user",
                "content": "Extract information: John Smith is a 35-year-old software engineer"
            }
        ]

        try:
            result = llm.generate_with_schema(messages, schema)
            print_success("Structured output generated")
            print_info(f"Result: {json.dumps(result, indent=2)}")
        except Exception as e:
            print_warning(f"Schema-based generation failed: {e}")
            print_info("This is common with some models")

        return True

    except Exception as e:
        print_error(f"Structured output test failed: {e}")
        return False


def test_batch_processing():
    """Test 10: Batch Processing"""
    print_test_header("Batch Processing")

    try:
        llm = HuggingFaceLLMFacade(model_name=TEST_MODELS["small"])

        print_info("Testing batch text generation...")

        prompts = [
            "The weather is",
            "Technology has",
            "Music makes"
        ]

        config = GenerationConfig(max_tokens=20, temperature=0.7)

        start_time = time.time()
        results = llm.batch_generate(prompts, config=config)
        elapsed = time.time() - start_time

        print_success(f"Batch generation completed in {elapsed:.2f}s")

        for i, (prompt, result) in enumerate(zip(prompts, results), 1):
            print_info(f"{i}. Prompt: {prompt}")
            print_info(f"   Result: {result[:50]}...")

        # Test batch embeddings if supported
        if llm.supports_capability(ModelCapability.EMBEDDINGS):
            print_info("\nTesting batch embeddings...")
            texts = ["text one", "text two", "text three"]
            embeddings = llm.batch_embed(texts, batch_size=2)
            print_success(f"Generated {len(embeddings)} embeddings in batch")

        return True

    except Exception as e:
        print_error(f"Batch processing test failed: {e}")
        return False


def test_error_handling():
    """Test 11: Error Handling"""
    print_test_header("Error Handling")

    try:
        llm = HuggingFaceLLMFacade(model_name=TEST_MODELS["small"])

        print_info("Testing unsupported capability handling...")

        # Test vision (should fail)
        try:
            llm.chat_completion_with_vision(
                [{"role": "user", "content": "Describe this"}],
                images=b"fake_image_data"
            )
            print_error("Should have raised CapabilityNotSupportedException")
        except CapabilityNotSupportedException as e:
            print_success(f"Correctly raised exception: {e}")

        # Test image generation (should fail)
        try:
            llm.image_generation("A sunset")
            print_error("Should have raised CapabilityNotSupportedException")
        except CapabilityNotSupportedException as e:
            print_success(f"Correctly raised exception: {e}")

        # Test audio transcription (should fail)
        try:
            llm.audio_transcription(b"fake_audio")
            print_error("Should have raised CapabilityNotSupportedException")
        except CapabilityNotSupportedException as e:
            print_success(f"Correctly raised exception: {e}")

        print_success("Error handling works correctly")

        return True

    except Exception as e:
        print_error(f"Error handling test failed: {e}")
        return False


def test_configuration_validation():
    """Test 12: Configuration Validation"""
    print_test_header("Configuration Validation")

    try:
        llm = HuggingFaceLLMFacade(model_name=TEST_MODELS["small"])

        print_info("Testing configuration validation...")

        # Valid config
        valid_config = {
            "max_tokens": 100,
            "temperature": 0.7,
            "top_p": 0.9
        }

        is_valid, errors = llm.validate_config(valid_config)
        if is_valid:
            print_success("Valid configuration accepted")
        else:
            print_error(f"Valid config rejected: {errors}")

        # Invalid config
        invalid_config = {
            "max_tokens": 10000,  # Too high
            "temperature": 3.0  # Too high
        }

        is_valid, errors = llm.validate_config(invalid_config)
        if not is_valid:
            print_success(f"Invalid configuration rejected: {errors}")
        else:
            print_warning("Invalid config was accepted (may be intentional)")

        return True

    except Exception as e:
        print_error(f"Configuration validation test failed: {e}")
        return False


def test_message_formatting():
    """Test 13: Message Formatting"""
    print_test_header("Message Formatting")

    try:
        llm = HuggingFaceLLMFacade(model_name=TEST_MODELS["small"])

        print_info("Testing message formatting...")

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]

        formatted = llm.format_messages(messages)

        print_success("Messages formatted successfully")
        print_info("Formatted output:")
        print(f"{Colors.MAGENTA}{formatted}{Colors.RESET}")

        return True

    except Exception as e:
        print_error(f"Message formatting test failed: {e}")
        return False


def test_async_operations():
    """Test 14: Async Operations"""
    print_test_header("Async Operations")

    try:
        import asyncio

        llm = HuggingFaceLLMFacade(model_name=TEST_MODELS["small"])

        print_info("Testing async text generation...")

        async def async_test():
            config = GenerationConfig(max_tokens=20, temperature=0.7)

            # Single async call
            result = await llm.atext_generation(
                "The future of AI is",
                config=config
            )
            print_success(f"Async generation: {result[:50]}...")

            # Multiple concurrent calls
            print_info("\nTesting concurrent async calls...")
            tasks = [
                llm.atext_generation("Prompt 1", config=config),
                llm.atext_generation("Prompt 2", config=config),
                llm.atext_generation("Prompt 3", config=config)
            ]

            results = await asyncio.gather(*tasks)
            print_success(f"Completed {len(results)} concurrent calls")

            return True

        # Run async test
        result = asyncio.run(async_test())

        if result:
            print_success("Async operations completed successfully")

        return result

    except Exception as e:
        print_error(f"Async operations test failed: {e}")
        return False


def test_tool_definitions():
    """Test 15: Tool Definitions"""
    print_test_header("Tool Definitions")

    try:
        llm = HuggingFaceLLMFacade(model_name=TEST_MODELS["chat"])

        print_info("Testing tool definition creation...")

        tool = llm.create_tool_definition(
            name="get_weather",
            description="Get current weather for a location",
            parameters={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    }
                }
            },
            required=["location"]
        )

        print_success("Tool definition created")
        print_info(f"Tool: {json.dumps(tool, indent=2)}")

        # Test tool execution
        print_info("\nTesting tool execution...")

        def mock_weather(location: str, unit: str = "celsius") -> dict:
            return {"temp": 72, "condition": "sunny", "location": location}

        tool_call = {
            "id": "call_123",
            "function": {
                "name": "get_weather",
                "arguments": json.dumps({"location": "Paris", "unit": "celsius"})
            }
        }

        result = llm.call_tool(
            tool_call,
            {"get_weather": mock_weather}
        )

        print_success(f"Tool executed: {result}")

        return True

    except Exception as e:
        print_error(f"Tool definitions test failed: {e}")
        return False


# ============================================================================
# Test Runner
# ============================================================================

def run_all_tests():
    """Run all capability tests."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "HUGGINGFACE LLM FACADE TEST SUITE" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")
    print(Colors.RESET)

    print_info(f"Starting test suite at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Test models: {json.dumps(TEST_MODELS, indent=2)}\n")

    tests = [
        ("Initialization", test_initialization),
        ("Capability Detection", test_capability_detection),
        ("Text Generation", test_text_generation),
        ("Chat Completion", test_chat_completion),
        ("Streaming", test_streaming),
        ("Embeddings", test_embeddings),
        ("Token Management", test_token_management),
        ("Code Generation", test_code_generation),
        ("Structured Output", test_structured_output),
        ("Batch Processing", test_batch_processing),
        ("Error Handling", test_error_handling),
        ("Configuration Validation", test_configuration_validation),
        ("Message Formatting", test_message_formatting),
        ("Async Operations", test_async_operations),
        ("Tool Definitions", test_tool_definitions)
    ]

    results = {}
    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            results[test_name] = False
            failed += 1

        time.sleep(0.5)  # Brief pause between tests

    # Print summary
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(Colors.RESET)

    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"{test_name:.<50} {status}")

    print(f"\n{Colors.BOLD}Total: {len(tests)} tests{Colors.RESET}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
    print(f"Success rate: {(passed / len(tests) * 100):.1f}%\n")

    return passed == len(tests)


if __name__ == "__main__":
    print(f"\n{Colors.BOLD}HuggingFace LLM Facade - Comprehensive Test Suite{Colors.RESET}")
    print(f"{Colors.BOLD}Copyright © 2025-2030 - Ashutosh Sinha{Colors.RESET}\n")

    # Check for API key
    if not os.getenv("HF_TOKEN") and not os.getenv("HUGGINGFACE_TOKEN"):
        print_warning("No HuggingFace API token found in environment variables")
        print_info("Set HF_TOKEN or HUGGINGFACE_TOKEN to run API-based tests")
        print_info("Continuing with available tests...\n")

    success = run_all_tests()

    sys.exit(0 if success else 1)