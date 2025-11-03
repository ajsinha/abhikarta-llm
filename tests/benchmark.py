"""
Performance Benchmarking Tool

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import sys
import os
import time
from statistics import mean, stdev

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.abstraction import LLMClientFactory


class Benchmark:
    """Performance benchmarking utility"""
    
    def __init__(self, name: str):
        self.name = name
        self.times = []
    
    def run(self, func, iterations: int = 10):
        """Run benchmark"""
        print(f"\nBenchmarking: {self.name}")
        print(f"Iterations: {iterations}")
        print("-" * 60)
        
        for i in range(iterations):
            start = time.time()
            func()
            elapsed = time.time() - start
            self.times.append(elapsed)
            print(f"  Iteration {i+1}: {elapsed:.4f}s")
        
        self.print_stats()
    
    def print_stats(self):
        """Print statistics"""
        if not self.times:
            return
        
        avg = mean(self.times)
        min_time = min(self.times)
        max_time = max(self.times)
        std = stdev(self.times) if len(self.times) > 1 else 0
        
        print("-" * 60)
        print(f"Average: {avg:.4f}s")
        print(f"Min:     {min_time:.4f}s")
        print(f"Max:     {max_time:.4f}s")
        print(f"StdDev:  {std:.4f}s")
        print(f"Throughput: {1/avg:.2f} ops/sec")


def benchmark_factory_initialization():
    """Benchmark factory initialization"""
    def init():
        factory = LLMClientFactory()
        factory.initialize(config_path="config/llm_config.json")
    
    bench = Benchmark("Factory Initialization")
    bench.run(init, iterations=10)


def benchmark_client_creation():
    """Benchmark client creation"""
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    
    def create():
        client = factory.create_default_client()
    
    bench = Benchmark("Client Creation")
    bench.run(create, iterations=100)


def benchmark_completion():
    """Benchmark completion operations"""
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    client = factory.create_default_client()
    
    def complete():
        client.complete("What is AI?", max_tokens=100)
    
    bench = Benchmark("Completion Operations")
    bench.run(complete, iterations=50)


def benchmark_chat():
    """Benchmark chat operations"""
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    client = factory.create_default_client()
    
    def chat():
        client.chat("Hello!", max_tokens=100)
    
    bench = Benchmark("Chat Operations")
    bench.run(chat, iterations=50)


def benchmark_history_operations():
    """Benchmark history operations"""
    factory = LLMClientFactory()
    factory.initialize(config_path="config/llm_config.json")
    client = factory.create_default_client()
    
    # Add some history
    for i in range(50):
        client.complete(f"Prompt {i}")
    
    def get_stats():
        client.get_history_summary()
    
    bench = Benchmark("History Statistics")
    bench.run(get_stats, iterations=1000)


def run_all_benchmarks():
    """Run all benchmarks"""
    print("=" * 60)
    print("LLM Abstraction System - Performance Benchmarks")
    print("=" * 60)
    
    benchmarks = [
        ("Factory Initialization", benchmark_factory_initialization),
        ("Client Creation", benchmark_client_creation),
        ("Completion Operations", benchmark_completion),
        ("Chat Operations", benchmark_chat),
        ("History Operations", benchmark_history_operations),
    ]
    
    for name, bench_func in benchmarks:
        try:
            bench_func()
        except Exception as e:
            print(f"\n✗ Benchmark '{name}' failed: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Benchmarking Complete")
    print("=" * 60)


if __name__ == "__main__":
    run_all_benchmarks()
