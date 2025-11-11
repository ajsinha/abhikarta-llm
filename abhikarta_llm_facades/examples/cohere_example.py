"""
Cohere Provider Example - Abhikarta LLM Facades

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This document and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use of this document or the software
system it describes is strictly prohibited without explicit written permission from the
copyright holder.

Patent Pending: Certain architectural patterns and implementations described in this
document may be subject to patent applications.


Description:
Complete executable example demonstrating all features of the Cohere provider.
"""

import os
import sys
import json

from ..facades.cohere_facade import CohereFacade
from ..facades.llm_facade import GenerationConfig, ModelCapability


def example_basic_chat():
    """Basic chat completion example."""
    print("="*60)
    print("Example 1: Basic Chat Completion")
    print("="*60)
    
    llm = CohereFacade(
        model_name="command-r-plus"
    )
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain the theory of relativity in simple terms."}
    ]
    
    response = llm.chat_completion(messages)
    
    print(f"Response: {response['content']}")
    print(f"Tokens used: {response['usage']['total_tokens']}")
    print()


def example_streaming():
    """Streaming chat completion example."""
    print("="*60)
    print("Example 2: Streaming Response")
    print("="*60)
    
    llm = CohereFacade(
        model_name="command-r-plus"
    )
    
    messages = [
        {"role": "user", "content": "Write a short poem about artificial intelligence."}
    ]
    
    print("Response: ", end="")
    for chunk in llm.stream_chat_completion(messages):
        print(chunk, end="", flush=True)
    print("\n")


def example_with_config():
    """Chat with custom configuration."""
    print("="*60)
    print("Example 3: Custom Configuration")
    print("="*60)
    
    llm = CohereFacade(
        model_name="command-r-plus"
    )
    
    config = GenerationConfig(
        max_tokens=500,
        temperature=0.7,
        top_p=0.9
    )
    
    messages = [
        {"role": "user", "content": "Generate a creative story about space exploration."}
    ]
    
    response = llm.chat_completion(messages, config=config)
    print(f"Response: {response['content']}")
    print()


def example_function_calling():
    """Function calling example."""
    print("="*60)
    print("Example 4: Function Calling")
    print("="*60)
    
    llm = CohereFacade(
        model_name="command-r-plus"
    )
    
    # Check if function calling is supported
    if not llm.supports_capability(ModelCapability.FUNCTION_CALLING):
        print("Function calling not supported by this model")
        print()
        return
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"]
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]
    
    messages = [
        {"role": "user", "content": "What's the weather like in New York?"}
    ]
    
    response = llm.chat_completion(messages, tools=tools)
    
    if "tool_calls" in response:
        print("Tool calls:")
        for tool_call in response["tool_calls"]:
            print(f"  Function: {tool_call['function']['name']}")
            print(f"  Arguments: {tool_call['function']['arguments']}")
    else:
        print(f"Response: {response['content']}")
    print()


def example_model_info():
    """Display model information and capabilities."""
    print("="*60)
    print("Example 5: Model Information & Capabilities")
    print("="*60)
    
    llm = CohereFacade(
        model_name="command-r-plus"
    )
    
    # Get model info
    info = llm.get_model_info()
    print("Model Information:")
    print(json.dumps(info, indent=2))
    
    # Get capabilities
    print("\nSupported Capabilities:")
    capabilities = llm.get_capabilities()
    for cap in capabilities:
        print(f"  - {cap.value}")
    
    print()


def example_error_handling():
    """Error handling example."""
    print("="*60)
    print("Example 6: Error Handling")
    print("="*60)
    
    from ..facades.llm_facade import (
        RateLimitException,
        ContentFilterException,
        AuthenticationException,
        ContextLengthExceededException
    )
    
    llm = CohereFacade(
        model_name="command-r-plus"
    )
    
    try:
        # Intentionally long message to potentially trigger context limit
        long_message = "Tell me about " + ("AI " * 10000)
        
        messages = [
            {"role": "user", "content": long_message}
        ]
        
        response = llm.chat_completion(messages)
        print(f"Response: {response['content']}")
        
    except RateLimitException as e:
        print(f"Rate limit exceeded: {e}")
    except ContentFilterException as e:
        print(f"Content was filtered: {e}")
    except ContextLengthExceededException as e:
        print(f"Context too long: {e.provided} tokens > {e.maximum} max")
    except AuthenticationException as e:
        print(f"Authentication failed: {e}")
    except Exception as e:
        print(f"Error occurred: {e}")
    
    print()


def example_usage_stats():
    """Usage statistics and monitoring."""
    print("="*60)
    print("Example 7: Usage Statistics")
    print("="*60)
    
    llm = CohereFacade(
        model_name="command-r-plus"
    )
    
    # Make a few requests
    for i in range(3):
        messages = [
            {"role": "user", "content": f"Count to {i+1}"}
        ]
        response = llm.chat_completion(messages)
    
    # Get usage stats
    stats = llm.get_usage_stats()
    print("Usage Statistics:")
    print(f"  Total requests: {stats['total_requests']}")
    print(f"  Total tokens: {stats['total_tokens']}")
    print(f"  Average tokens/request: {stats['average_tokens_per_request']:.2f}")
    print(f"  Uptime: {stats['uptime_seconds']:.2f} seconds")
    
    # Health check
    if llm.health_check():
        print("\n✓ Service is healthy")
    else:
        print("\n✗ Service unavailable")
    
    print()


def example_context_manager():
    """Context manager usage."""
    print("="*60)
    print("Example 8: Context Manager")
    print("="*60)
    
    # Using context manager for automatic cleanup
    with CohereFacade(model_name="command-r-plus") as llm:
        messages = [
            {"role": "user", "content": "Hello! How are you?"}
        ]
        
        response = llm.chat_completion(messages)
        print(f"Response: {response['content']}")
    
    print("✓ Resources automatically cleaned up")
    print()


def main():
    """Run all examples."""
    print(f"\n{'='*60}")
    print(f"Cohere Provider Examples - Abhikarta LLM Facades")
    print(f"{'='*60}\n")
    
    # Check for API key
    if not os.getenv("COHERE_API_KEY"):
        print(f"Warning: COHERE_API_KEY environment variable not set")
        print("Some examples may fail without proper authentication")
        print()
    
    try:
        example_basic_chat()
        example_streaming()
        example_with_config()
        example_function_calling()
        example_model_info()
        example_error_handling()
        example_usage_stats()
        example_context_manager()
        
        print("="*60)
        print("All examples completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
