"""
Dispatcher Module - Thread pool management for actor execution

This module provides dispatchers that manage thread pools and
schedule actor message processing. Different dispatcher types
optimize for different workloads.

Dispatcher Types:
- DefaultDispatcher: Shared thread pool for most actors
- PinnedDispatcher: Dedicated thread per actor
- CallingThreadDispatcher: Runs in calling thread (testing)
- ForkJoinDispatcher: Work-stealing for CPU-bound tasks

Acknowledgement:
This implementation is inspired by Apache Pekko (incubating).

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha - ajsinha@gmail.com

Version: 1.2.5
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, Future
import threading
import queue
import time
import os
import logging

logger = logging.getLogger(__name__)


class Dispatcher(ABC):
    """
    Abstract base class for dispatchers.
    
    A dispatcher is responsible for:
    - Managing a pool of threads
    - Scheduling actor message processing
    - Ensuring thread safety guarantees
    """
    
    @abstractmethod
    def execute(self, task: Callable[[], None]) -> None:
        """
        Execute a task.
        
        Args:
            task: The task to execute
        """
        pass
    
    @abstractmethod
    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the dispatcher.
        
        Args:
            wait: Wait for pending tasks to complete
        """
        pass
    
    @property
    @abstractmethod
    def is_shutdown(self) -> bool:
        """Check if dispatcher is shutdown."""
        pass


@dataclass
class DispatcherConfig:
    """Configuration for dispatcher creation."""
    dispatcher_type: str = "default"
    thread_pool_size: int = field(default_factory=lambda: os.cpu_count() or 4)
    throughput: int = 5  # Messages per actor dispatch
    throughput_deadline: float = 0.0  # Max time per dispatch (0 = unlimited)


class DefaultDispatcher(Dispatcher):
    """
    Default dispatcher using a shared thread pool.
    
    This is the most common dispatcher type, suitable for
    most actors. It balances resource usage with responsiveness.
    
    Attributes:
        pool_size: Number of threads in the pool
        throughput: Max messages processed per dispatch
    """
    
    def __init__(self, pool_size: Optional[int] = None, throughput: int = 5):
        self._pool_size = pool_size or (os.cpu_count() or 4) * 2
        self._throughput = throughput
        self._executor = ThreadPoolExecutor(
            max_workers=self._pool_size,
            thread_name_prefix="actor-dispatcher"
        )
        self._shutdown = False
        self._lock = threading.Lock()
        self._pending_tasks = 0
        
        logger.info(f"DefaultDispatcher initialized with {self._pool_size} threads")
    
    def execute(self, task: Callable[[], None]) -> None:
        """Execute task in thread pool."""
        if self._shutdown:
            logger.warning("Dispatcher is shutdown, task rejected")
            return
        
        with self._lock:
            self._pending_tasks += 1
        
        def wrapped_task():
            try:
                task()
            finally:
                with self._lock:
                    self._pending_tasks -= 1
        
        self._executor.submit(wrapped_task)
    
    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the thread pool."""
        with self._lock:
            self._shutdown = True
        self._executor.shutdown(wait=wait)
        logger.info("DefaultDispatcher shutdown complete")
    
    @property
    def is_shutdown(self) -> bool:
        """Check shutdown state."""
        return self._shutdown
    
    @property
    def pool_size(self) -> int:
        """Thread pool size."""
        return self._pool_size
    
    @property
    def pending_tasks(self) -> int:
        """Number of pending tasks."""
        with self._lock:
            return self._pending_tasks


class PinnedDispatcher(Dispatcher):
    """
    Dispatcher that provides a dedicated thread per actor.
    
    Use this for actors that:
    - Perform blocking I/O
    - Need guaranteed thread affinity
    - Should not share threads with other actors
    
    Note: Creates one thread per actor, so use sparingly.
    """
    
    def __init__(self):
        self._threads: Dict[int, threading.Thread] = {}
        self._queues: Dict[int, queue.Queue] = {}
        self._shutdown = False
        self._lock = threading.Lock()
        self._next_id = 0
    
    def get_thread_id(self) -> int:
        """Get a unique thread ID for an actor."""
        with self._lock:
            thread_id = self._next_id
            self._next_id += 1
            
            # Create queue and thread
            task_queue: queue.Queue = queue.Queue()
            self._queues[thread_id] = task_queue
            
            def worker():
                while True:
                    try:
                        task = task_queue.get(timeout=1.0)
                        if task is None:
                            break
                        try:
                            task()
                        except Exception as e:
                            logger.error(f"Error in pinned thread {thread_id}: {e}")
                    except queue.Empty:
                        if self._shutdown:
                            break
            
            thread = threading.Thread(
                target=worker,
                name=f"pinned-{thread_id}",
                daemon=True
            )
            thread.start()
            self._threads[thread_id] = thread
            
            return thread_id
    
    def execute(self, task: Callable[[], None], thread_id: Optional[int] = None) -> None:
        """Execute task on specified thread."""
        if self._shutdown:
            return
        
        if thread_id is None:
            thread_id = self.get_thread_id()
        
        with self._lock:
            task_queue = self._queues.get(thread_id)
            if task_queue:
                task_queue.put(task)
    
    def release_thread(self, thread_id: int) -> None:
        """Release a pinned thread."""
        with self._lock:
            task_queue = self._queues.get(thread_id)
            if task_queue:
                task_queue.put(None)  # Signal thread to exit
                del self._queues[thread_id]
    
    def shutdown(self, wait: bool = True) -> None:
        """Shutdown all threads."""
        self._shutdown = True
        
        with self._lock:
            for task_queue in self._queues.values():
                task_queue.put(None)
        
        if wait:
            for thread in self._threads.values():
                thread.join(timeout=5.0)
        
        logger.info("PinnedDispatcher shutdown complete")
    
    @property
    def is_shutdown(self) -> bool:
        """Check shutdown state."""
        return self._shutdown
    
    @property
    def thread_count(self) -> int:
        """Number of active threads."""
        with self._lock:
            return len(self._threads)


class CallingThreadDispatcher(Dispatcher):
    """
    Dispatcher that runs tasks in the calling thread.
    
    Primarily used for testing and debugging, as it makes
    actor execution synchronous and deterministic.
    
    Warning: Can cause deadlocks if actors send messages
    to each other in a cycle!
    """
    
    def __init__(self):
        self._shutdown = False
    
    def execute(self, task: Callable[[], None]) -> None:
        """Execute task immediately in calling thread."""
        if self._shutdown:
            return
        task()
    
    def shutdown(self, wait: bool = True) -> None:
        """Mark as shutdown."""
        self._shutdown = True
    
    @property
    def is_shutdown(self) -> bool:
        """Check shutdown state."""
        return self._shutdown


class ForkJoinDispatcher(Dispatcher):
    """
    Work-stealing dispatcher for CPU-bound workloads.
    
    Each thread has its own work queue. When idle, threads
    steal work from other threads' queues. This provides
    better cache locality and load balancing for compute-heavy
    actors.
    """
    
    def __init__(self, parallelism: Optional[int] = None):
        self._parallelism = parallelism or os.cpu_count() or 4
        self._queues: List[queue.Queue] = [queue.Queue() for _ in range(self._parallelism)]
        self._threads: List[threading.Thread] = []
        self._shutdown = False
        self._lock = threading.Lock()
        self._next_queue = 0
        
        # Start worker threads
        for i in range(self._parallelism):
            thread = threading.Thread(
                target=self._worker,
                args=(i,),
                name=f"fork-join-{i}",
                daemon=True
            )
            thread.start()
            self._threads.append(thread)
        
        logger.info(f"ForkJoinDispatcher initialized with {self._parallelism} threads")
    
    def _worker(self, worker_id: int) -> None:
        """Worker thread that processes and steals tasks."""
        my_queue = self._queues[worker_id]
        
        while not self._shutdown:
            # Try own queue first
            try:
                task = my_queue.get(timeout=0.001)
                if task is not None:
                    try:
                        task()
                    except Exception as e:
                        logger.error(f"Error in fork-join worker {worker_id}: {e}")
                continue
            except queue.Empty:
                pass
            
            # Try stealing from other queues
            stolen = False
            for i in range(self._parallelism):
                if i != worker_id:
                    try:
                        task = self._queues[i].get_nowait()
                        if task is not None:
                            try:
                                task()
                            except Exception as e:
                                logger.error(f"Error in fork-join worker {worker_id}: {e}")
                            stolen = True
                            break
                    except queue.Empty:
                        pass
            
            if not stolen:
                time.sleep(0.001)  # Brief sleep if no work
    
    def execute(self, task: Callable[[], None]) -> None:
        """Submit task to least-loaded queue."""
        if self._shutdown:
            return
        
        # Round-robin distribution
        with self._lock:
            queue_idx = self._next_queue
            self._next_queue = (self._next_queue + 1) % self._parallelism
        
        self._queues[queue_idx].put(task)
    
    def shutdown(self, wait: bool = True) -> None:
        """Shutdown all workers."""
        self._shutdown = True
        
        if wait:
            for thread in self._threads:
                thread.join(timeout=5.0)
        
        logger.info("ForkJoinDispatcher shutdown complete")
    
    @property
    def is_shutdown(self) -> bool:
        """Check shutdown state."""
        return self._shutdown


class BalancingDispatcher(Dispatcher):
    """
    Dispatcher that balances load across multiple underlying dispatchers.
    
    Routes tasks to the least-loaded dispatcher, providing
    automatic load balancing across multiple thread pools.
    """
    
    def __init__(self, dispatchers: Optional[List[Dispatcher]] = None,
                 pool_count: int = 2):
        if dispatchers:
            self._dispatchers = dispatchers
        else:
            self._dispatchers = [
                DefaultDispatcher() for _ in range(pool_count)
            ]
        self._shutdown = False
        self._next_dispatcher = 0
        self._lock = threading.Lock()
    
    def execute(self, task: Callable[[], None]) -> None:
        """Route task to next dispatcher."""
        if self._shutdown:
            return
        
        with self._lock:
            dispatcher = self._dispatchers[self._next_dispatcher]
            self._next_dispatcher = (self._next_dispatcher + 1) % len(self._dispatchers)
        
        dispatcher.execute(task)
    
    def shutdown(self, wait: bool = True) -> None:
        """Shutdown all underlying dispatchers."""
        self._shutdown = True
        for dispatcher in self._dispatchers:
            dispatcher.shutdown(wait)
        logger.info("BalancingDispatcher shutdown complete")
    
    @property
    def is_shutdown(self) -> bool:
        """Check shutdown state."""
        return self._shutdown


# ============================================
# DISPATCHER FACTORY
# ============================================

class DispatcherFactory:
    """Factory for creating dispatchers based on configuration."""
    
    _dispatcher_types = {
        "default": DefaultDispatcher,
        "pinned": PinnedDispatcher,
        "calling-thread": CallingThreadDispatcher,
        "fork-join": ForkJoinDispatcher,
        "balancing": BalancingDispatcher,
    }
    
    @classmethod
    def create(cls, config: Optional[DispatcherConfig] = None) -> Dispatcher:
        """
        Create a dispatcher based on configuration.
        
        Args:
            config: Dispatcher configuration
            
        Returns:
            New dispatcher instance
        """
        if config is None:
            config = DispatcherConfig()
        
        dispatcher_class = cls._dispatcher_types.get(config.dispatcher_type)
        if dispatcher_class is None:
            raise ValueError(f"Unknown dispatcher type: {config.dispatcher_type}")
        
        if config.dispatcher_type == "default":
            return dispatcher_class(pool_size=config.thread_pool_size,
                                   throughput=config.throughput)
        elif config.dispatcher_type == "fork-join":
            return dispatcher_class(parallelism=config.thread_pool_size)
        else:
            return dispatcher_class()
    
    @classmethod
    def register(cls, name: str, dispatcher_class: type) -> None:
        """Register a custom dispatcher type."""
        cls._dispatcher_types[name] = dispatcher_class
