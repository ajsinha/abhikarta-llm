"""
Performance Benchmarking Script

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import sys
import os
import time
import statistics
from typing import List, Callable

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from llm.abstraction import LLMClientFactory


class BenchmarkResult:
    """Store benchmark results"""
    
    def __init__(self, name: str, times: List[float], success_count: int, failure_count: int):
        self.name = name
        self.times = times
        self.success_count = success_count
        self.failure_count = failure_count
        
        if times:
            self.mean = statistics.mean(times)
            self.median = statistics.median(times)
            self.min = min(times)
            self.max = max(times)
            self.stdev = statistics.stdev(times) if len(times) > 1 else 0
        else:
            self.mean = self.median = self.min = self.max = self.stdev = 0
    
    def __str__(self):
        return (
            f"{self.name}:\n"
            f"  Runs: {len(self.times)} ({self.success_count} success, {self.failure_count} failed)\n"
            f"  Mean: {self.mean*1000:.2f}ms\n"
            f"  Median: {self.median*1000:.2f}ms\n"
            f"  Min: {self.min*1000:.2f}ms\n"
            f"  Max: {self.max*1000:.2f}ms\n"
            f"  StdDev: {self.stdev*1000:.2f}ms"
        )


def benchmark(func: Callable, iterations: int = 10, warmup: int = 2) -> BenchmarkResult:
    """
    Benchmark a function.
    
    Args:
        func: Function to benchmark
        iterations: Number of iterations
        warmup: Number of warmup iterations
        
    Returns:
        BenchmarkResult object
    """
    # Warmup
    for _ in range(warmup):
        try:
            func()
        except:
            pass
    
    # Actual benchmark
    times = []
    success_count = 0
    failure_count = 0
    
    for _ in range(iterations):
        start_time = time.time()
        try:
            func()
            elapsed = time.time() - start_time
            times.append(elapsed)
            success_count += 1
        except Exception as e:
            failure_count += 1
    
    return BenchmarkResult(func.__name__, times, success_count, failure_count)


def benchmark_initialization():
    """Benchmark factory initialization"""
    print("Benchmarking Factory Initialization")
    print("-" * 60)
    
    def init_factory():
        factory = LLMClientFactory()
        factory.initialize(config_path="config/llm_config.json")
    
    result = benchmark(init_factory, iterations=10)
    print(result)
    print()


def benchmark_client_creation():
    """Benchmark client creation"""
    print("Benchmarking Client Creation")
    print("-" * 60)
    
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    
    def create_mock_client():
        client = factory.create_mock_client()
    
    result = benchmark(create_mock_client, iterations=100)
    print(result)
    print()


def benchmark_completions():
    """Benchmark completion operations"""
    print("Benchmarking Completions")
    print("-" * 60)
    
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    client = factory.create_mock_client()
    
    prompts = {
        "short": "Hello",
        "medium": "What is artificial intelligence? Please explain in detail.",
        "long": "Write a comprehensive essay about the history, current state, and future prospects of artificial intelligence, covering key milestones, major breakthroughs, current applications, and potential future developments."
    }
    
    for name, prompt in prompts.items():
        def complete():
            client.complete(prompt)
        complete.__name__ = f"complete_{name}"
        
        result = benchmark(complete, iterations=20)
        print(result)
        print()


def benchmark_chat():
    """Benchmark chat operations"""
    print("Benchmarking Chat Operations")
    print("-" * 60)
    
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    client = factory.create_mock_client()
    
    def single_turn_chat():
        client.clear_conversation()
        client.chat("Hello, how are you?")
    
    def multi_turn_chat():
        client.clear_conversation()
        client.chat("Hello!")
        client.chat("What is AI?")
        client.chat("How does it work?")
    
    result1 = benchmark(single_turn_chat, iterations=20)
    print(result1)
    print()
    
    result2 = benchmark(multi_turn_chat, iterations=10)
    print(result2)
    print()


def benchmark_streaming():
    """Benchmark streaming operations"""
    print("Benchmarking Streaming")
    print("-" * 60)
    
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    client = factory.create_mock_client()
    
    def stream_complete():
        tokens = list(client.stream_complete("Write a story"))
    
    result = benchmark(stream_complete, iterations=20)
    print(result)
    print()


def benchmark_history():
    """Benchmark history operations"""
    print("Benchmarking History Operations")
    print("-" * 60)
    
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    client = factory.create_mock_client()
    
    # Populate history
    for i in range(50):
        client.complete(f"Prompt {i}")
    
    def get_history_stats():
        stats = client.get_history_summary()
    
    def search_history():
        results = client.history.search("Prompt")
    
    def export_history():
        client.export_history("/tmp/test_history.json")
    
    result1 = benchmark(get_history_stats, iterations=100)
    print(result1)
    print()
    
    result2 = benchmark(search_history, iterations=100)
    print(result2)
    print()
    
    result3 = benchmark(export_history, iterations=10)
    print(result3)
    print()


def benchmark_batch_processing():
    """Benchmark batch processing"""
    print("Benchmarking Batch Processing")
    print("-" * 60)
    
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    client = factory.create_mock_client()
    
    batch_sizes = [1, 5, 10, 20]
    
    for size in batch_sizes:
        prompts = [f"Prompt {i}" for i in range(size)]
        
        def batch_complete():
            client.batch_complete(prompts)
        batch_complete.__name__ = f"batch_complete_{size}"
        
        result = benchmark(batch_complete, iterations=10)
        print(result)
        print()


def memory_usage_test():
    """Test memory usage"""
    print("Memory Usage Test")
    print("-" * 60)
    
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Initial memory
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        print(f"Initial memory: {mem_before:.2f} MB")
        
        # Create multiple clients
        factory = LLMClientFactory()
        factory.initialize(config_path="config/llm_config.json")
        
        clients = []
        for i in range(10):
            client = factory.create_mock_client()
            # Generate some history
            for j in range(50):
                client.complete(f"Test prompt {j}")
            clients.append(client)
        
        # Final memory
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        print(f"After 10 clients: {mem_after:.2f} MB")
        print(f"Memory increase: {mem_after - mem_before:.2f} MB")
        print(f"Average per client: {(mem_after - mem_before) / 10:.2f} MB")
        
    except ImportError:
        print("psutil not installed. Run: pip install psutil")
    
    print()


def run_all_benchmarks():
    """Run all performance benchmarks"""
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "PERFORMANCE BENCHMARKING SUITE" + " " * 17 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    start_time = time.time()
    
    benchmark_initialization()
    benchmark_client_creation()
    benchmark_completions()
    benchmark_chat()
    benchmark_streaming()
    benchmark_history()
    benchmark_batch_processing()
    memory_usage_test()
    
    total_time = time.time() - start_time
    
    print("=" * 60)
    print(f"Total benchmark time: {total_time:.2f}s")
    print("=" * 60)


if __name__ == "__main__":
    run_all_benchmarks()
