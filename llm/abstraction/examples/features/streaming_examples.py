"""
Streaming Examples for Abhikarta LLM

Demonstrates various streaming capabilities and use cases.

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import sys
import os
import time
from typing import List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
llm_config_path = '/home/ashutosh/PycharmProjects/abhikarta-llm/config/llm_config.json'

from llm.abstraction.core.factories import LLMClientFactory
from llm.abstraction.core.facade import Message
from llm.abstraction.utils.streaming import (
    StreamWrapper,
    StreamingCallbacks,
    StreamCollector,
    BufferedStream,
    stream_to_file,
    tee_stream
)


def example_1_basic_streaming():
    """Example 1: Basic streaming with real-time output"""
    print("="*70)
    print("EXAMPLE 1: Basic Streaming")
    print("="*70)
    
    factory = LLMClientFactory()
    
    # Create client
    client = factory.create_client('mock', model='mock-model')
    facade = factory.create_facade('mock', 'mock-model')
    
    prompt = "Write a short story about a robot learning to paint."
    
    print("\nStreaming response:")
    print("-" * 70)
    
    # Stream and print tokens as they arrive
    for token in facade.stream_complete(prompt, max_tokens=200):
        print(token, end='', flush=True)
    
    print("\n" + "="*70 + "\n")


def example_2_streaming_with_metrics():
    """Example 2: Streaming with performance metrics"""
    print("="*70)
    print("EXAMPLE 2: Streaming with Metrics")
    print("="*70)
    
    factory = LLMClientFactory()
    facade = factory.create_facade('mock', 'mock-model')
    
    prompt = "Explain quantum computing in simple terms."
    
    # Wrap stream with metrics collection
    stream = facade.stream_complete(prompt, max_tokens=150)
    wrapped_stream = StreamWrapper(stream, collect_metrics=True)
    
    print("\nStreaming response:")
    print("-" * 70)
    
    # Stream tokens
    for token in wrapped_stream:
        print(token, end='', flush=True)
    
    # Get final response with metrics
    response = wrapped_stream.collector.end()
    
    print("\n" + "-" * 70)
    print("\n📊 Streaming Metrics:")
    print(f"  Total tokens: {response.metrics.total_tokens}")
    print(f"  Total characters: {response.metrics.total_chars}")
    print(f"  Duration: {response.metrics.total_duration_ms:.2f}ms")
    print(f"  First token latency: {response.metrics.first_token_latency_ms:.2f}ms")
    print(f"  Tokens per second: {response.metrics.tokens_per_second:.2f}")
    print("="*70 + "\n")


def example_3_streaming_with_callbacks():
    """Example 3: Streaming with event callbacks"""
    print("="*70)
    print("EXAMPLE 3: Streaming with Callbacks")
    print("="*70)
    
    factory = LLMClientFactory()
    facade = factory.create_facade('mock', 'mock-model')
    
    # Define callbacks
    token_count = [0]  # Use list for mutability in closure
    
    def on_start():
        print("\n🚀 Stream started!")
        print("-" * 70)
    
    def on_token(token: str):
        token_count[0] += 1
        if token_count[0] % 10 == 0:
            print(f" [{token_count[0]}]", end='', flush=True)
    
    def on_end(response):
        print(f"\n{'=' * 70}")
        print(f"✅ Stream completed!")
        print(f"📝 Total text length: {len(response.text)} characters")
        print(f"🔢 Total tokens: {response.metrics.total_tokens}")
    
    def on_error(error):
        print(f"\n❌ Error occurred: {error}")
    
    callbacks = StreamingCallbacks(
        on_start=on_start,
        on_token=on_token,
        on_end=on_end,
        on_error=on_error
    )
    
    prompt = "List 20 interesting facts about space."
    stream = facade.stream_complete(prompt, max_tokens=300)
    wrapped_stream = StreamWrapper(stream, callbacks=callbacks, collect_metrics=True)
    
    # Consume stream (callbacks will be triggered)
    for token in wrapped_stream:
        print(token, end='', flush=True)
    
    print("\n" + "="*70 + "\n")


def example_4_chat_streaming():
    """Example 4: Streaming chat conversation"""
    print("="*70)
    print("EXAMPLE 4: Chat Streaming")
    print("="*70)
    
    factory = LLMClientFactory()
    facade = factory.create_facade('mock', 'mock-model')
    
    # Create conversation
    messages = [
        Message(role='system', content='You are a helpful assistant.'),
        Message(role='user', content='What are the three laws of robotics?'),
    ]
    
    print("\n💬 Chat Response:")
    print("-" * 70)
    
    # Stream chat response
    full_response = []
    for token in facade.stream_chat(messages, max_tokens=200):
        print(token, end='', flush=True)
        full_response.append(token)
    
    print("\n" + "-" * 70)
    print(f"✅ Complete response: {len(''.join(full_response))} characters")
    print("="*70 + "\n")


def example_5_buffered_streaming():
    """Example 5: Buffered streaming for better display"""
    print("="*70)
    print("EXAMPLE 5: Buffered Streaming")
    print("="*70)
    
    factory = LLMClientFactory()
    facade = factory.create_facade('mock', 'mock-model')
    
    prompt = "Write a haiku about programming."
    
    # Buffer tokens before displaying
    stream = facade.stream_complete(prompt, max_tokens=100)
    buffered = BufferedStream(stream, buffer_size=5, flush_on_newline=True)
    
    print("\nBuffered response (updates in chunks):")
    print("-" * 70)
    
    for chunk in buffered:
        print(chunk, end='', flush=True)
        time.sleep(0.1)  # Simulate processing
    
    print("\n" + "="*70 + "\n")


def example_6_stream_to_file():
    """Example 6: Stream directly to file"""
    print("="*70)
    print("EXAMPLE 6: Stream to File")
    print("="*70)
    
    factory = LLMClientFactory()
    facade = factory.create_facade('mock', 'mock-model')
    
    prompt = "Write a detailed explanation of machine learning."
    output_file = "/tmp/stream_output.txt"
    
    print(f"\n📝 Streaming to file: {output_file}")
    print("-" * 70)
    
    # Stream directly to file
    stream = facade.stream_complete(prompt, max_tokens=300)
    response = stream_to_file(stream, output_file)
    
    print(f"✅ Completed!")
    print(f"  File size: {os.path.getsize(output_file)} bytes")
    print(f"  Tokens: {response.metrics.total_tokens}")
    print(f"  Duration: {response.metrics.total_duration_ms:.2f}ms")
    
    # Show first 200 characters
    with open(output_file, 'r') as f:
        content = f.read()
        preview = content[:200] + "..." if len(content) > 200 else content
        print(f"\n📄 Preview:\n{preview}")
    
    print("="*70 + "\n")


def example_7_multiple_consumers():
    """Example 7: Stream to multiple consumers simultaneously"""
    print("="*70)
    print("EXAMPLE 7: Multiple Stream Consumers")
    print("="*70)
    
    factory = LLMClientFactory()
    facade = factory.create_facade('mock', 'mock-model')
    
    prompt = "Describe the water cycle."
    
    # Set up multiple consumers
    display_buffer = []
    file_buffer = []
    
    def display_consumer(token: str):
        """Consumer that displays tokens"""
        display_buffer.append(token)
    
    def file_consumer(token: str):
        """Consumer that saves to file"""
        file_buffer.append(token)
    
    print("\n🔀 Streaming to multiple consumers...")
    print("-" * 70)
    
    # Tee stream to multiple consumers
    stream = facade.stream_complete(prompt, max_tokens=200)
    teed_stream = tee_stream(stream, display_consumer, file_consumer)
    
    # Consume stream
    for token in teed_stream:
        print(token, end='', flush=True)
    
    print("\n" + "-" * 70)
    print(f"✅ Display buffer: {len(''.join(display_buffer))} chars")
    print(f"✅ File buffer: {len(''.join(file_buffer))} chars")
    print("="*70 + "\n")


def example_8_streaming_comparison():
    """Example 8: Compare streaming vs non-streaming performance"""
    print("="*70)
    print("EXAMPLE 8: Streaming vs Non-Streaming Comparison")
    print("="*70)
    
    factory = LLMClientFactory()
    facade = factory.create_facade('mock', 'mock-model')
    
    prompt = "Explain the theory of relativity."
    
    # Test non-streaming
    print("\n⏱️  Non-Streaming (wait for complete response):")
    print("-" * 70)
    start_time = time.time()
    response = facade.complete(prompt, max_tokens=200)
    non_stream_duration = time.time() - start_time
    print(f"Duration: {non_stream_duration:.3f}s")
    print(f"Time to first content: {non_stream_duration:.3f}s")
    
    # Test streaming
    print("\n⏱️  Streaming (immediate feedback):")
    print("-" * 70)
    start_time = time.time()
    first_token_time = None
    token_count = 0
    
    for token in facade.stream_complete(prompt, max_tokens=200):
        if first_token_time is None:
            first_token_time = time.time() - start_time
        token_count += 1
        print(token, end='', flush=True)
    
    stream_duration = time.time() - start_time
    
    print("\n" + "-" * 70)
    print("\n📊 Performance Comparison:")
    print(f"  Non-streaming total time: {non_stream_duration:.3f}s")
    print(f"  Streaming total time: {stream_duration:.3f}s")
    print(f"  ⚡ Time to first token: {first_token_time:.3f}s")
    print(f"  📈 User experience improvement: {((non_stream_duration - first_token_time) / non_stream_duration * 100):.1f}%")
    print("="*70 + "\n")


def example_9_progressive_display():
    """Example 9: Progressive display with word-by-word streaming"""
    print("="*70)
    print("EXAMPLE 9: Progressive Word-by-Word Display")
    print("="*70)
    
    factory = LLMClientFactory()
    facade = factory.create_facade('mock', 'mock-model')
    
    prompt = "Tell me a joke about programmers."
    
    print("\n😄 Streaming joke:")
    print("-" * 70)
    
    word_buffer = ""
    for token in facade.stream_complete(prompt, max_tokens=100):
        word_buffer += token
        
        # Display complete words
        if ' ' in word_buffer or '\n' in word_buffer:
            words = word_buffer.split()
            for word in words[:-1]:
                print(word, end=' ', flush=True)
                time.sleep(0.05)  # Simulate typing effect
            word_buffer = words[-1] if words else ""
    
    # Display remaining buffer
    if word_buffer:
        print(word_buffer, end='', flush=True)
    
    print("\n" + "="*70 + "\n")


def example_10_real_world_chat_ui():
    """Example 10: Simulated chat UI with streaming"""
    print("="*70)
    print("EXAMPLE 10: Chat UI Simulation")
    print("="*70)
    
    factory = LLMClientFactory()
    facade = factory.create_facade('mock', 'mock-model')
    
    conversation = [
        Message(role='system', content='You are a friendly AI assistant.')
    ]
    
    user_messages = [
        "Hello! How are you?",
        "Can you help me understand neural networks?",
        "Thank you! That was helpful."
    ]
    
    for user_msg in user_messages:
        print(f"\n👤 User: {user_msg}")
        
        # Add user message
        conversation.append(Message(role='user', content=user_msg))
        
        print("🤖 Assistant: ", end='', flush=True)
        
        # Stream assistant response
        assistant_response = []
        for token in facade.stream_chat(conversation, max_tokens=150):
            print(token, end='', flush=True)
            assistant_response.append(token)
            time.sleep(0.02)  # Typing effect
        
        # Add assistant response to conversation
        conversation.append(
            Message(role='assistant', content=''.join(assistant_response))
        )
        
        print()  # New line after response
    
    print("\n" + "="*70 + "\n")


def main():
    """Run all examples"""
    examples = [
        ("Basic Streaming", example_1_basic_streaming),
        ("Streaming with Metrics", example_2_streaming_with_metrics),
        ("Streaming with Callbacks", example_3_streaming_with_callbacks),
        ("Chat Streaming", example_4_chat_streaming),
        ("Buffered Streaming", example_5_buffered_streaming),
        ("Stream to File", example_6_stream_to_file),
        ("Multiple Consumers", example_7_multiple_consumers),
        ("Performance Comparison", example_8_streaming_comparison),
        ("Progressive Display", example_9_progressive_display),
        ("Chat UI Simulation", example_10_real_world_chat_ui),
    ]
    
    print("\n" + "🌊" * 35)
    print("ABHIKARTA LLM - STREAMING EXAMPLES")
    print("🌊" * 35 + "\n")
    
    for i, (name, example_func) in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            print(f"❌ Example {i} failed: {e}\n")
    
    print("=" * 70)
    print("✅ All examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
