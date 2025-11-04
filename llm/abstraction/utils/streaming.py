"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.3

Streaming Utilities - Comprehensive streaming support for LLM responses
"""

import time
from typing import Iterator, Any, Optional, Callable, List, TextIO
from dataclasses import dataclass


@dataclass
class StreamingMetrics:
    """
    Metrics for tracking streaming performance.
    """
    total_tokens: int = 0
    tokens_per_second: float = 0.0
    chunks_received: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    total_duration: float = 0.0
    
    def update(self, tokens: int = 1):
        """Update metrics with new tokens"""
        if self.start_time is None:
            self.start_time = time.time()
        
        self.total_tokens += tokens
        self.chunks_received += 1
        
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            self.tokens_per_second = self.total_tokens / elapsed
    
    def finalize(self):
        """Finalize metrics when streaming is complete"""
        if self.end_time is None:
            self.end_time = time.time()
        
        if self.start_time:
            self.total_duration = self.end_time - self.start_time


class StreamCollector:
    """Collects streaming chunks into a complete response."""
    
    def __init__(self):
        self.chunks: List[str] = []
        self.metrics = StreamingMetrics()
    
    def add(self, chunk: Any) -> str:
        """Add a chunk to the collector"""
        text = self._extract_text(chunk)
        if text:
            self.chunks.append(text)
            self.metrics.update(len(text.split()))
        return text
    
    def _extract_text(self, chunk: Any) -> str:
        """Extract text from various chunk formats"""
        if isinstance(chunk, str):
            return chunk
        if hasattr(chunk, 'text'):
            return chunk.text
        if hasattr(chunk, 'content'):
            return chunk.content
        if isinstance(chunk, dict):
            return chunk.get('text', chunk.get('content', ''))
        return str(chunk)
    
    def get_text(self) -> str:
        """Get the complete collected text"""
        return ''.join(self.chunks)
    
    def get_metrics(self) -> StreamingMetrics:
        """Get streaming metrics"""
        self.metrics.finalize()
        return self.metrics


class StreamWrapper:
    """Wraps a stream iterator to provide additional functionality."""
    
    def __init__(self, stream: Iterator[Any]):
        self.stream = stream
        self.collector = StreamCollector()
        self.metrics = self.collector.metrics
    
    def __iter__(self):
        """Iterate through the stream"""
        for chunk in self.stream:
            self.collector.add(chunk)
            yield chunk
        self.metrics.finalize()
    
    def get_text(self) -> str:
        """Get all collected text"""
        return self.collector.get_text()


class StreamingCallbacks:
    """Callback handlers for streaming events."""
    
    def __init__(
        self,
        on_start: Optional[Callable[[], None]] = None,
        on_chunk: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None
    ):
        self.on_start = on_start
        self.on_chunk = on_chunk
        self.on_complete = on_complete
        self.on_error = on_error
    
    def start(self):
        if self.on_start:
            self.on_start()
    
    def chunk(self, text: str):
        if self.on_chunk:
            self.on_chunk(text)
    
    def complete(self, full_text: str):
        if self.on_complete:
            self.on_complete(full_text)
    
    def error(self, exception: Exception):
        if self.on_error:
            self.on_error(exception)


class BufferedStream:
    """Buffers streaming chunks for smoother output."""
    
    def __init__(self, stream: Iterator[Any], buffer_size: int = 10):
        self.stream = stream
        self.buffer_size = buffer_size
        self.buffer: List[str] = []
    
    def __iter__(self):
        """Iterate with buffering"""
        for chunk in self.stream:
            text = _extract_text(chunk)
            self.buffer.append(text)
            
            if len(self.buffer) >= self.buffer_size:
                yield ''.join(self.buffer)
                self.buffer.clear()
        
        if self.buffer:
            yield ''.join(self.buffer)


def stream_to_file(stream: Iterator[Any], filepath: str, encoding: str = 'utf-8') -> StreamingMetrics:
    """
    Stream output directly to a file.
    
    Returns:
        StreamingMetrics with performance data
    """
    metrics = StreamingMetrics()
    
    with open(filepath, 'w', encoding=encoding) as f:
        for chunk in stream:
            text = _extract_text(chunk)
            f.write(text)
            f.flush()
            metrics.update(len(text.split()))
    
    metrics.finalize()
    return metrics


def tee_stream(stream: Iterator[Any], *outputs: TextIO) -> Iterator[Any]:
    """Split stream to multiple outputs (like Unix tee command)."""
    for chunk in stream:
        text = _extract_text(chunk)
        
        for output in outputs:
            output.write(text)
            output.flush()
        
        yield chunk


def merge_streams(*streams: Iterator[Any]) -> Iterator[str]:
    """Merge multiple streams into one."""
    for stream in streams:
        for chunk in stream:
            text = _extract_text(chunk)
            if text:
                yield text


def _extract_text(chunk: Any) -> str:
    """Helper function to extract text from various chunk formats"""
    if isinstance(chunk, str):
        return chunk
    if hasattr(chunk, 'text'):
        return chunk.text
    if hasattr(chunk, 'content'):
        return chunk.content
    if isinstance(chunk, dict):
        return chunk.get('text', chunk.get('content', ''))
    return str(chunk)


def print_stream(stream: Iterator[Any], end: str = '\n', flush: bool = True) -> str:
    """
    Print stream to stdout and return full text.
    
    Args:
        stream: The stream iterator
        end: String to append at end (default: newline)
        flush: Whether to flush after each chunk (default: True)
    
    Returns:
        Complete text from stream
    
    Example:
        full_text = print_stream(stream)
        print(f"\nTotal: {len(full_text)} chars")
    """
    collector = StreamCollector()
    
    for chunk in stream:
        text = collector.add(chunk)
        print(text, end='', flush=flush)
    
    print(end, end='')
    return collector.get_text()


def collect_stream_with_metrics(stream: Iterator[Any]) -> tuple[str, StreamingMetrics]:
    """
    Collect stream and return text with performance metrics.
    
    Args:
        stream: The stream iterator
    
    Returns:
        Tuple of (full_text, metrics)
    
    Example:
        text, metrics = collect_stream_with_metrics(stream)
        print(f"Text: {text}")
        print(f"Speed: {metrics.tokens_per_second:.2f} tokens/sec")
        print(f"Duration: {metrics.total_duration:.2f}s")
    """
    collector = StreamCollector()
    
    for chunk in stream:
        collector.add(chunk)
    
    metrics = collector.get_metrics()
    return collector.get_text(), metrics


# Legacy aliases
StreamMetrics = StreamingMetrics
StreamHandler = StreamCollector


__all__ = [
    'StreamingMetrics',
    'StreamCollector',
    'StreamWrapper',
    'StreamingCallbacks',
    'BufferedStream',
    'stream_to_file',
    'tee_stream',
    'merge_streams',
    'print_stream',
    'collect_stream_with_metrics',
    'StreamMetrics',
    'StreamHandler',
]


"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.3
"""
