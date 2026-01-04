"""
Scheduler Module - Time-based message scheduling

This module provides scheduling capabilities for actors:
- One-time delayed messages
- Periodic/recurring messages
- Cancellable scheduled tasks

Acknowledgement:
This implementation is inspired by Apache Pekko (incubating).

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha - ajsinha@gmail.com

Version: 1.3.0
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Optional
import threading
import time
import heapq
import uuid
import logging

from .actor import ActorRef

logger = logging.getLogger(__name__)


class Cancellable(ABC):
    """
    Handle for a scheduled task that can be cancelled.
    """
    
    @abstractmethod
    def cancel(self) -> bool:
        """
        Cancel the scheduled task.
        
        Returns:
            True if successfully cancelled, False if already executed/cancelled
        """
        pass
    
    @abstractmethod
    def is_cancelled(self) -> bool:
        """Check if the task has been cancelled."""
        pass


@dataclass
class ScheduledTask:
    """Internal representation of a scheduled task."""
    task_id: str
    execute_at: float
    receiver: ActorRef
    message: Any
    sender: Optional[ActorRef]
    interval: Optional[float]  # For recurring tasks
    cancelled: bool = False
    
    def __lt__(self, other):
        """For heap ordering by execution time."""
        return self.execute_at < other.execute_at


class CancellableTask(Cancellable):
    """Cancellable handle for a scheduled task."""
    
    def __init__(self, task: ScheduledTask, scheduler: 'Scheduler'):
        self._task = task
        self._scheduler = scheduler
    
    def cancel(self) -> bool:
        """Cancel the task."""
        if self._task.cancelled:
            return False
        self._task.cancelled = True
        return True
    
    def is_cancelled(self) -> bool:
        """Check if cancelled."""
        return self._task.cancelled


class Scheduler:
    """
    Scheduler for time-based message delivery.
    
    The scheduler uses a priority queue (heap) to efficiently
    manage scheduled tasks and a background thread to dispatch
    them at the appropriate time.
    
    Features:
    - One-time delayed messages
    - Periodic recurring messages
    - Cancellable tasks
    - High-precision timing
    """
    
    def __init__(self, tick_duration: float = 0.01):
        """
        Initialize the scheduler.
        
        Args:
            tick_duration: Time resolution in seconds (default 10ms)
        """
        self._tick_duration = tick_duration
        self._tasks: list = []  # Heap of ScheduledTask
        self._lock = threading.Lock()
        self._shutdown = threading.Event()
        self._new_task = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._started = False
    
    def start(self) -> None:
        """Start the scheduler background thread."""
        if self._started:
            return
        
        self._shutdown.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="actor-scheduler",
            daemon=True
        )
        self._thread.start()
        self._started = True
        logger.info("Scheduler started")
    
    def stop(self) -> None:
        """Stop the scheduler."""
        self._shutdown.set()
        self._new_task.set()  # Wake up the thread
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        
        self._started = False
        logger.info("Scheduler stopped")
    
    def _run(self) -> None:
        """Background thread that dispatches scheduled tasks."""
        while not self._shutdown.is_set():
            next_wake: Optional[float] = None
            
            with self._lock:
                current_time = time.time()
                
                # Process all tasks that are ready
                while self._tasks and self._tasks[0].execute_at <= current_time:
                    task = heapq.heappop(self._tasks)
                    
                    if not task.cancelled:
                        # Execute the task
                        try:
                            task.receiver.tell(task.message, task.sender)
                        except Exception as e:
                            logger.error(f"Error delivering scheduled message: {e}")
                        
                        # Re-schedule if recurring
                        if task.interval is not None and not task.cancelled:
                            task.execute_at = current_time + task.interval
                            heapq.heappush(self._tasks, task)
                
                # Calculate next wake time
                if self._tasks:
                    next_wake = self._tasks[0].execute_at - current_time
            
            # Wait for next task or new task
            if next_wake is not None:
                self._new_task.wait(timeout=max(0.001, next_wake))
            else:
                self._new_task.wait(timeout=1.0)
            
            self._new_task.clear()
    
    def schedule_once(self, delay: float, receiver: ActorRef, message: Any,
                     sender: Optional[ActorRef] = None) -> Cancellable:
        """
        Schedule a message to be sent once after a delay.
        
        Args:
            delay: Delay in seconds
            receiver: Target actor
            message: Message to send
            sender: Optional sender reference
            
        Returns:
            Cancellable handle
        """
        task = ScheduledTask(
            task_id=str(uuid.uuid4()),
            execute_at=time.time() + delay,
            receiver=receiver,
            message=message,
            sender=sender,
            interval=None
        )
        
        with self._lock:
            heapq.heappush(self._tasks, task)
        
        self._new_task.set()  # Wake up scheduler thread
        
        return CancellableTask(task, self)
    
    def schedule_repeatedly(self, initial_delay: float, interval: float,
                           receiver: ActorRef, message: Any,
                           sender: Optional[ActorRef] = None) -> Cancellable:
        """
        Schedule a message to be sent repeatedly.
        
        Args:
            initial_delay: Initial delay before first message
            interval: Interval between subsequent messages
            receiver: Target actor
            message: Message to send
            sender: Optional sender reference
            
        Returns:
            Cancellable handle
        """
        task = ScheduledTask(
            task_id=str(uuid.uuid4()),
            execute_at=time.time() + initial_delay,
            receiver=receiver,
            message=message,
            sender=sender,
            interval=interval
        )
        
        with self._lock:
            heapq.heappush(self._tasks, task)
        
        self._new_task.set()
        
        return CancellableTask(task, self)
    
    def schedule_at(self, timestamp: float, receiver: ActorRef, message: Any,
                   sender: Optional[ActorRef] = None) -> Cancellable:
        """
        Schedule a message to be sent at a specific time.
        
        Args:
            timestamp: Unix timestamp for delivery
            receiver: Target actor
            message: Message to send
            sender: Optional sender reference
            
        Returns:
            Cancellable handle
        """
        delay = max(0, timestamp - time.time())
        return self.schedule_once(delay, receiver, message, sender)
    
    def schedule_with_fixed_delay(self, initial_delay: float, delay: float,
                                  receiver: ActorRef, message: Any,
                                  sender: Optional[ActorRef] = None) -> Cancellable:
        """
        Schedule with fixed delay between message completion and next send.
        
        Similar to schedule_repeatedly but measures delay from when
        the previous message was sent, not from a fixed schedule.
        
        Args:
            initial_delay: Initial delay
            delay: Delay between messages
            receiver: Target actor
            message: Message to send
            sender: Optional sender reference
            
        Returns:
            Cancellable handle
        """
        # In this simplified implementation, same as schedule_repeatedly
        return self.schedule_repeatedly(initial_delay, delay, receiver, message, sender)
    
    @property
    def pending_count(self) -> int:
        """Number of pending scheduled tasks."""
        with self._lock:
            return len([t for t in self._tasks if not t.cancelled])
    
    def cancel_all(self) -> int:
        """
        Cancel all pending tasks.
        
        Returns:
            Number of tasks cancelled
        """
        count = 0
        with self._lock:
            for task in self._tasks:
                if not task.cancelled:
                    task.cancelled = True
                    count += 1
        return count


class TimerScheduler:
    """
    Actor-specific timer interface.
    
    Provides a simplified API for actors to schedule messages to
    themselves, automatically handling cancellation on actor stop.
    """
    
    def __init__(self, scheduler: Scheduler, actor_ref: ActorRef):
        self._scheduler = scheduler
        self._actor = actor_ref
        self._timers: dict = {}
        self._lock = threading.Lock()
    
    def start_single_timer(self, key: Any, message: Any, delay: float) -> None:
        """
        Start a single-shot timer.
        
        If a timer with the same key already exists, it will be cancelled.
        
        Args:
            key: Timer key for cancellation
            message: Message to send when timer fires
            delay: Delay in seconds
        """
        self.cancel(key)
        
        cancellable = self._scheduler.schedule_once(
            delay, self._actor, message
        )
        
        with self._lock:
            self._timers[key] = cancellable
    
    def start_timer_at_fixed_rate(self, key: Any, message: Any,
                                  initial_delay: float, interval: float) -> None:
        """
        Start a repeating timer at fixed rate.
        
        Args:
            key: Timer key
            message: Message to send
            initial_delay: Initial delay
            interval: Interval between messages
        """
        self.cancel(key)
        
        cancellable = self._scheduler.schedule_repeatedly(
            initial_delay, interval, self._actor, message
        )
        
        with self._lock:
            self._timers[key] = cancellable
    
    def start_timer_with_fixed_delay(self, key: Any, message: Any,
                                     initial_delay: float, delay: float) -> None:
        """
        Start a repeating timer with fixed delay.
        
        Args:
            key: Timer key
            message: Message to send
            initial_delay: Initial delay
            delay: Delay between messages
        """
        self.cancel(key)
        
        cancellable = self._scheduler.schedule_with_fixed_delay(
            initial_delay, delay, self._actor, message
        )
        
        with self._lock:
            self._timers[key] = cancellable
    
    def cancel(self, key: Any) -> None:
        """
        Cancel a timer.
        
        Args:
            key: Timer key
        """
        with self._lock:
            if key in self._timers:
                self._timers[key].cancel()
                del self._timers[key]
    
    def cancel_all(self) -> None:
        """Cancel all timers for this actor."""
        with self._lock:
            for cancellable in self._timers.values():
                cancellable.cancel()
            self._timers.clear()
    
    def is_timer_active(self, key: Any) -> bool:
        """
        Check if a timer is active.
        
        Args:
            key: Timer key
            
        Returns:
            True if timer exists and is not cancelled
        """
        with self._lock:
            cancellable = self._timers.get(key)
            return cancellable is not None and not cancellable.is_cancelled()
