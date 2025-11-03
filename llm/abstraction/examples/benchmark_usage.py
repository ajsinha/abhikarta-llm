"""Benchmarking Example"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from llm.abstraction import LLMClientFactory
from llm.abstraction.utils.benchmark import Benchmark

def main():
    print("=" * 60)
    print("Performance Benchmarking Example")
    print("=" * 60)
    
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    
    client = factory.create_mock_client()
    
    # Benchmark completion
    bench = Benchmark("Mock Completion")
    
    def completion_test():
        client.complete("Test prompt", max_tokens=100)
    
    print("\nBenchmarking completion...")
    result = bench.run(completion_test, iterations=100)
    bench.print_result(result)
    
    # Benchmark chat
    bench2 = Benchmark("Mock Chat")
    
    def chat_test():
        client.chat("Test message", max_tokens=100, use_history=False)
    
    print("\nBenchmarking chat...")
    result2 = bench2.run(chat_test, iterations=100)
    bench2.print_result(result2)
    
    print("\n" + "=" * 60)
    print("Benchmarking completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
