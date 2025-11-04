"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.3
"""

"""Performance Benchmarking Utilities"""
import time
import statistics
from typing import Callable, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class BenchmarkResult:
    name: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    median_time: float
    std_dev: float
    ops_per_second: float
    timestamp: datetime = field(default_factory=datetime.now)

class Benchmark:
    def __init__(self, name: str = "Benchmark"):
        self.name = name
        self.results: List[BenchmarkResult] = []
    
    def run(self, func: Callable, iterations: int = 100, *args, **kwargs) -> BenchmarkResult:
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            func(*args, **kwargs)
            end = time.perf_counter()
            times.append(end - start)
        
        total_time = sum(times)
        result = BenchmarkResult(
            name=self.name,
            iterations=iterations,
            total_time=total_time,
            avg_time=statistics.mean(times),
            min_time=min(times),
            max_time=max(times),
            median_time=statistics.median(times),
            std_dev=statistics.stdev(times) if len(times) > 1 else 0.0,
            ops_per_second=iterations / total_time if total_time > 0 else 0
        )
        self.results.append(result)
        return result
    
    def compare(self, funcs: Dict[str, Callable], iterations: int = 100, *args, **kwargs) -> Dict[str, BenchmarkResult]:
        results = {}
        for name, func in funcs.items():
            bench = Benchmark(name)
            results[name] = bench.run(func, iterations, *args, **kwargs)
        return results
    
    def print_result(self, result: BenchmarkResult):
        print(f"\n{result.name} Benchmark Results:")
        print(f"  Iterations: {result.iterations}")
        print(f"  Total Time: {result.total_time:.4f}s")
        print(f"  Average: {result.avg_time*1000:.2f}ms")
        print(f"  Median: {result.median_time*1000:.2f}ms")
        print(f"  Min: {result.min_time*1000:.2f}ms")
        print(f"  Max: {result.max_time*1000:.2f}ms")
        print(f"  Std Dev: {result.std_dev*1000:.2f}ms")
        print(f"  Ops/sec: {result.ops_per_second:.2f}")
