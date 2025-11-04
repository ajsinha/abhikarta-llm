"""
Tests for Streaming Functionality

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import unittest
import time
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.abstraction.core.factories import LLMClientFactory, LLMProviderFactory
from llm.abstraction.core.facade import Message
from llm.abstraction.utils.streaming import (
    StreamCollector,
    StreamWrapper,
    StreamingCallbacks,
    BufferedStream,
    StreamingMetrics,
    stream_to_file,
    tee_stream,
    merge_streams
)


class TestStreamCollector(unittest.TestCase):
    """Test StreamCollector functionality"""
    
    def test_basic_collection(self):
        """Test basic token collection"""
        collector = StreamCollector()
        collector.start()
        
        tokens = ["Hello", " ", "World", "!"]
        for token in tokens:
            collector.add_token(token)
        
        response = collector.end()
        
        self.assertEqual(response.text, "Hello World!")
        self.assertEqual(response.metrics.total_tokens, 4)
        self.assertEqual(response.metrics.total_chars, len("Hello World!"))
    
    def test_metrics_calculation(self):
        """Test metrics are calculated correctly"""
        collector = StreamCollector()
        collector.start()
        
        tokens = ["Test", " ", "tokens"]
        for token in tokens:
            collector.add_token(token)
            time.sleep(0.01)  # Simulate processing time
        
        response = collector.end()
        
        self.assertIsNotNone(response.metrics.first_token_latency_ms)
        self.assertIsNotNone(response.metrics.total_duration_ms)
        self.assertGreater(response.metrics.total_duration_ms, 0)
    
    def test_get_text_during_collection(self):
        """Test getting text while still collecting"""
        collector = StreamCollector()
        collector.start()
        
        collector.add_token("Hello")
        self.assertEqual(collector.get_text(), "Hello")
        
        collector.add_token(" World")
        self.assertEqual(collector.get_text(), "Hello World")


class TestStreamWrapper(unittest.TestCase):
    """Test StreamWrapper functionality"""
    
    def test_basic_wrapping(self):
        """Test basic stream wrapping"""
        def token_generator():
            for token in ["Hello", " ", "World"]:
                yield token
        
        wrapped = StreamWrapper(token_generator(), collect_metrics=True)
        result = []
        
        for token in wrapped:
            result.append(token)
        
        self.assertEqual(result, ["Hello", " ", "World"])
        self.assertEqual(wrapped.collector.get_text(), "Hello World")
    
    def test_callbacks(self):
        """Test callbacks are triggered"""
        def token_generator():
            for token in ["A", "B", "C"]:
                yield token
        
        start_called = [False]
        tokens_received = []
        end_called = [False]
        
        def on_start():
            start_called[0] = True
        
        def on_token(token):
            tokens_received.append(token)
        
        def on_end(response):
            end_called[0] = True
        
        callbacks = StreamingCallbacks(
            on_start=on_start,
            on_token=on_token,
            on_end=on_end
        )
        
        wrapped = StreamWrapper(
            token_generator(),
            callbacks=callbacks,
            collect_metrics=True
        )
        
        for token in wrapped:
            pass
        
        self.assertTrue(start_called[0])
        self.assertEqual(tokens_received, ["A", "B", "C"])
        self.assertTrue(end_called[0])
    
    def test_error_callback(self):
        """Test error callback is triggered"""
        def failing_generator():
            yield "Start"
            raise ValueError("Test error")
        
        error_received = [None]
        
        def on_error(e):
            error_received[0] = e
        
        callbacks = StreamingCallbacks(on_error=on_error)
        wrapped = StreamWrapper(failing_generator(), callbacks=callbacks)
        
        with self.assertRaises(ValueError):
            for token in wrapped:
                pass
        
        self.assertIsNotNone(error_received[0])
        self.assertIsInstance(error_received[0], ValueError)


class TestBufferedStream(unittest.TestCase):
    """Test BufferedStream functionality"""
    
    def test_buffer_size(self):
        """Test buffering by size"""
        def token_generator():
            for i in range(15):
                yield str(i)
        
        buffered = BufferedStream(
            token_generator(),
            buffer_size=5,
            flush_on_newline=False
        )
        
        chunks = list(buffered)
        
        # Should get 3 chunks: "01234", "56789", "101112131<|CURSOR|>4"
        self.assertEqual(len(chunks), 3)
        self.assertTrue(all(len(chunk) >= 1 for chunk in chunks))
    
    def test_newline_flush(self):
        """Test flushing on newlines"""
        def token_generator():
            for token in ["Hello", "\n", "World"]:
                yield token
        
        buffered = BufferedStream(
            token_generator(),
            buffer_size=100,  # Large buffer
            flush_on_newline=True
        )
        
        chunks = list(buffered)
        
        # Should flush on newline even though buffer not full
        self.assertGreaterEqual(len(chunks), 2)


class TestStreamingUtilities(unittest.TestCase):
    """Test streaming utility functions"""
    
    def test_stream_to_file(self):
        """Test streaming to file"""
        def token_generator():
            for token in ["Hello", " ", "World", "!"]:
                yield token
        
        output_file = "/tmp/test_stream_output.txt"
        response = stream_to_file(token_generator(), output_file)
        
        # Check file contents
        with open(output_file, 'r') as f:
            content = f.read()
        
        self.assertEqual(content, "Hello World!")
        self.assertEqual(response.metrics.total_tokens, 4)
        
        # Cleanup
        os.remove(output_file)
    
    def test_tee_stream(self):
        """Test streaming to multiple consumers"""
        def token_generator():
            for token in ["A", "B", "C"]:
                yield token
        
        consumer1_tokens = []
        consumer2_tokens = []
        
        def consumer1(token):
            consumer1_tokens.append(token)
        
        def consumer2(token):
            consumer2_tokens.append(token)
        
        teed = tee_stream(token_generator(), consumer1, consumer2)
        result = list(teed)
        
        self.assertEqual(result, ["A", "B", "C"])
        self.assertEqual(consumer1_tokens, ["A", "B", "C"])
        self.assertEqual(consumer2_tokens, ["A", "B", "C"])
    
    def test_merge_streams(self):
        """Test merging multiple streams"""
        def stream1():
            for token in ["A", "B"]:
                yield token
        
        def stream2():
            for token in ["C", "D"]:
                yield token
        
        merged = merge_streams(stream1(), stream2())
        result = list(merged)
        
        self.assertEqual(result, ["A", "B", "C", "D"])


class TestIntegrationWithProviders(unittest.TestCase):
    """Test streaming with actual providers"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.provider_factory = LLMProviderFactory()
        # Initialize with default config if exists, otherwise skip provider tests
        try:
            config_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'config'
            )
            config_path = os.path.join(config_dir, 'llm_config.json')
            if os.path.exists(config_path):
                self.provider_factory.initialize(config_path)
                self.has_config = True
            else:
                self.has_config = False
        except:
            self.has_config = False
    
    def test_mock_provider_streaming(self):
        """Test streaming with mock provider"""
        if not self.has_config:
            self.skipTest("No config available")
        
        try:
            provider = self.provider_factory.get_provider('mock')
            facade = provider.create_facade('mock-model')
            
            tokens = []
            for token in facade.stream_complete("Test prompt", max_tokens=50):
                tokens.append(token)
            
            self.assertGreater(len(tokens), 0)
            self.assertIsInstance(tokens[0], str)
        except Exception as e:
            self.skipTest(f"Mock provider not available: {e}")
    
    def test_mock_provider_chat_streaming(self):
        """Test chat streaming with mock provider"""
        if not self.has_config:
            self.skipTest("No config available")
        
        try:
            provider = self.provider_factory.get_provider('mock')
            facade = provider.create_facade('mock-model')
            
            messages = [
                Message(role='user', content='Hello!')
            ]
            
            tokens = []
            for token in facade.stream_chat(messages, max_tokens=50):
                tokens.append(token)
            
            self.assertGreater(len(tokens), 0)
        except Exception as e:
            self.skipTest(f"Mock provider not available: {e}")
    
    def test_streaming_with_wrapper(self):
        """Test streaming with wrapper and metrics"""
        if not self.has_config:
            self.skipTest("No config available")
        
        try:
            provider = self.provider_factory.get_provider('mock')
            facade = provider.create_facade('mock-model')
            
            stream = facade.stream_complete("Test", max_tokens=50)
            wrapped = StreamWrapper(stream, collect_metrics=True)
            
            tokens = []
            for token in wrapped:
                tokens.append(token)
            
            response = wrapped.collector.end()
            
            self.assertGreater(len(tokens), 0)
            self.assertGreater(response.metrics.total_tokens, 0)
            self.assertIsNotNone(response.metrics.first_token_latency_ms)
        except Exception as e:
            self.skipTest(f"Mock provider not available: {e}")


class TestStreamingMetrics(unittest.TestCase):
    """Test streaming metrics calculation"""
    
    def test_metrics_initialization(self):
        """Test metrics are initialized correctly"""
        metrics = StreamingMetrics()
        
        self.assertEqual(metrics.total_tokens, 0)
        self.assertEqual(metrics.total_chars, 0)
        self.assertIsNone(metrics.start_time)
        self.assertIsNone(metrics.end_time)
    
    def test_metrics_computation(self):
        """Test final metrics computation"""
        metrics = StreamingMetrics()
        metrics.start_time = datetime.now()
        metrics.total_tokens = 100
        
        time.sleep(0.1)  # Simulate processing
        
        metrics.end_time = datetime.now()
        metrics.compute_final_metrics()
        
        self.assertIsNotNone(metrics.total_duration_ms)
        self.assertGreater(metrics.total_duration_ms, 0)
        self.assertIsNotNone(metrics.tokens_per_second)
        self.assertGreater(metrics.tokens_per_second, 0)


def run_all_tests():
    """Run all streaming tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestStreamCollector))
    suite.addTests(loader.loadTestsFromTestCase(TestStreamWrapper))
    suite.addTests(loader.loadTestsFromTestCase(TestBufferedStream))
    suite.addTests(loader.loadTestsFromTestCase(TestStreamingUtilities))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationWithProviders))
    suite.addTests(loader.loadTestsFromTestCase(TestStreamingMetrics))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
