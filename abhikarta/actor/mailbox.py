"""
Mailbox Module - Message queue implementations for actors

This module provides various mailbox implementations for different use cases:
- UnboundedMailbox: Default, no limit on queue size
- BoundedMailbox: Fixed capacity with backpressure
- PriorityMailbox: Orders messages by priority
- ControlAwareMailbox: Prioritizes system messages

Acknowledgement:
This implementation is inspired by Apache Pekko (incubating).

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha - ajsinha@gmail.com

Version: 1.3.0
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, List
from dataclasses import dataclass
import threading
import queue
import heapq
import time
import logging

from .actor import Envelope, MessagePriority, PoisonPill, Kill

logger = logging.getLogger(__name__)


class Mailbox(ABC):
    """
    Abstract base class for actor mailboxes.
    
    A mailbox is a message queue that holds messages until the actor
    processes them. Different implementations provide different
    ordering and capacity guarantees.
    """
    
    @abstractmethod
    def enqueue(self, envelope: Envelope) -> bool:
        """
        Add a message to the mailbox.
        
        Args:
            envelope: The message envelope
            
        Returns:
            True if enqueued successfully, False if rejected
        """
        pass
    
    @abstractmethod
    def dequeue(self, timeout: Optional[float] = None) -> Optional[Envelope]:
        """
        Remove and return the next message.
        
        Args:
            timeout: Optional timeout in seconds
            
        Returns:
            The next envelope, or None if empty/timeout
        """
        pass
    
    @abstractmethod
    def is_empty(self) -> bool:
        """Check if mailbox is empty."""
        pass
    
    @abstractmethod
    def size(self) -> int:
        """Get number of messages in mailbox."""
        pass
    
    @abstractmethod
    def clear(self) -> List[Envelope]:
        """Clear all messages and return them."""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close the mailbox, preventing further enqueues."""
        pass


class UnboundedMailbox(Mailbox):
    """
    Default mailbox with unlimited capacity.
    
    Messages are processed in FIFO order. This is the default
    mailbox type and suitable for most use cases.
    
    Thread-safe using a lock-free queue implementation.
    """
    
    def __init__(self):
        self._queue: queue.Queue = queue.Queue()
        self._closed = threading.Event()
        self._size = 0
        self._lock = threading.Lock()
    
    def enqueue(self, envelope: Envelope) -> bool:
        """Add message to queue."""
        if self._closed.is_set():
            return False
        
        self._queue.put(envelope)
        with self._lock:
            self._size += 1
        return True
    
    def dequeue(self, timeout: Optional[float] = None) -> Optional[Envelope]:
        """Get next message."""
        try:
            envelope = self._queue.get(timeout=timeout)
            with self._lock:
                self._size -= 1
            return envelope
        except queue.Empty:
            return None
    
    def is_empty(self) -> bool:
        """Check if empty."""
        return self._queue.empty()
    
    def size(self) -> int:
        """Get size."""
        with self._lock:
            return self._size
    
    def clear(self) -> List[Envelope]:
        """Clear and return all messages."""
        messages = []
        while not self._queue.empty():
            try:
                messages.append(self._queue.get_nowait())
            except queue.Empty:
                break
        with self._lock:
            self._size = 0
        return messages
    
    def close(self) -> None:
        """Close mailbox."""
        self._closed.set()


class BoundedMailbox(Mailbox):
    """
    Mailbox with fixed capacity for backpressure.
    
    When the mailbox is full, enqueue will block or reject
    new messages depending on configuration.
    
    Attributes:
        capacity: Maximum number of messages
        push_timeout: Timeout for blocking enqueue (None = non-blocking)
    """
    
    def __init__(self, capacity: int = 1000, push_timeout: Optional[float] = None):
        self._capacity = capacity
        self._push_timeout = push_timeout
        self._queue: queue.Queue = queue.Queue(maxsize=capacity)
        self._closed = threading.Event()
    
    def enqueue(self, envelope: Envelope) -> bool:
        """Add message, blocking or rejecting if full."""
        if self._closed.is_set():
            return False
        
        try:
            self._queue.put(envelope, block=self._push_timeout is not None,
                          timeout=self._push_timeout)
            return True
        except queue.Full:
            logger.warning(f"Mailbox full, message dropped: {type(envelope.message).__name__}")
            return False
    
    def dequeue(self, timeout: Optional[float] = None) -> Optional[Envelope]:
        """Get next message."""
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def is_empty(self) -> bool:
        """Check if empty."""
        return self._queue.empty()
    
    def size(self) -> int:
        """Get current size."""
        return self._queue.qsize()
    
    def clear(self) -> List[Envelope]:
        """Clear all messages."""
        messages = []
        while not self._queue.empty():
            try:
                messages.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return messages
    
    def close(self) -> None:
        """Close mailbox."""
        self._closed.set()
    
    @property
    def capacity(self) -> int:
        """Maximum capacity."""
        return self._capacity
    
    def is_full(self) -> bool:
        """Check if at capacity."""
        return self._queue.full()


class PriorityMailbox(Mailbox):
    """
    Mailbox that orders messages by priority.
    
    Higher priority messages are processed first.
    Within the same priority, FIFO order is maintained.
    """
    
    def __init__(self):
        self._heap: List[tuple] = []
        self._counter = 0  # For FIFO ordering within same priority
        self._lock = threading.Lock()
        self._not_empty = threading.Condition(self._lock)
        self._closed = threading.Event()
    
    def enqueue(self, envelope: Envelope) -> bool:
        """Add message in priority order."""
        if self._closed.is_set():
            return False
        
        with self._not_empty:
            # Negate priority for max-heap behavior (heapq is min-heap)
            entry = (-envelope.priority.value, self._counter, envelope)
            heapq.heappush(self._heap, entry)
            self._counter += 1
            self._not_empty.notify()
        return True
    
    def dequeue(self, timeout: Optional[float] = None) -> Optional[Envelope]:
        """Get highest priority message."""
        with self._not_empty:
            if not self._heap:
                if timeout is None:
                    return None
                self._not_empty.wait(timeout)
            
            if self._heap:
                _, _, envelope = heapq.heappop(self._heap)
                return envelope
            return None
    
    def is_empty(self) -> bool:
        """Check if empty."""
        with self._lock:
            return len(self._heap) == 0
    
    def size(self) -> int:
        """Get size."""
        with self._lock:
            return len(self._heap)
    
    def clear(self) -> List[Envelope]:
        """Clear and return all messages."""
        with self._lock:
            messages = [envelope for _, _, envelope in self._heap]
            self._heap = []
            return messages
    
    def close(self) -> None:
        """Close mailbox."""
        self._closed.set()
        with self._not_empty:
            self._not_empty.notify_all()


class ControlAwareMailbox(Mailbox):
    """
    Mailbox that prioritizes system/control messages.
    
    System messages (PoisonPill, Kill, etc.) are processed
    before regular messages regardless of arrival order.
    """
    
    def __init__(self, underlying: Optional[Mailbox] = None):
        self._control_queue: queue.Queue = queue.Queue()
        self._message_queue = underlying or UnboundedMailbox()
        self._lock = threading.Lock()
        self._closed = threading.Event()
    
    def _is_control_message(self, message: Any) -> bool:
        """Check if message is a control/system message."""
        return isinstance(message, (PoisonPill, Kill))
    
    def enqueue(self, envelope: Envelope) -> bool:
        """Route message to appropriate queue."""
        if self._closed.is_set():
            return False
        
        if self._is_control_message(envelope.message):
            self._control_queue.put(envelope)
            return True
        else:
            return self._message_queue.enqueue(envelope)
    
    def dequeue(self, timeout: Optional[float] = None) -> Optional[Envelope]:
        """Get control messages first, then regular messages."""
        # Check control queue first
        try:
            return self._control_queue.get_nowait()
        except queue.Empty:
            pass
        
        # Fall back to regular messages
        return self._message_queue.dequeue(timeout)
    
    def is_empty(self) -> bool:
        """Check if both queues are empty."""
        return self._control_queue.empty() and self._message_queue.is_empty()
    
    def size(self) -> int:
        """Get total size."""
        return self._control_queue.qsize() + self._message_queue.size()
    
    def clear(self) -> List[Envelope]:
        """Clear all messages."""
        messages = []
        while not self._control_queue.empty():
            try:
                messages.append(self._control_queue.get_nowait())
            except queue.Empty:
                break
        messages.extend(self._message_queue.clear())
        return messages
    
    def close(self) -> None:
        """Close both queues."""
        self._closed.set()
        self._message_queue.close()


class DeadLetterMailbox(Mailbox):
    """
    Special mailbox for dead letters (undeliverable messages).
    
    This mailbox collects messages that couldn't be delivered
    to their intended recipient. Useful for debugging and
    monitoring.
    """
    
    def __init__(self, max_size: int = 10000):
        self._queue: queue.Queue = queue.Queue()
        self._max_size = max_size
        self._dropped = 0
        self._lock = threading.Lock()
    
    def enqueue(self, envelope: Envelope) -> bool:
        """Store dead letter, dropping oldest if full."""
        with self._lock:
            if self._queue.qsize() >= self._max_size:
                try:
                    self._queue.get_nowait()
                    self._dropped += 1
                except queue.Empty:
                    pass
        
        self._queue.put(envelope)
        logger.debug(f"Dead letter: {type(envelope.message).__name__}")
        return True
    
    def dequeue(self, timeout: Optional[float] = None) -> Optional[Envelope]:
        """Get next dead letter."""
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def is_empty(self) -> bool:
        """Check if empty."""
        return self._queue.empty()
    
    def size(self) -> int:
        """Get size."""
        return self._queue.qsize()
    
    def clear(self) -> List[Envelope]:
        """Clear all dead letters."""
        messages = []
        while not self._queue.empty():
            try:
                messages.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return messages
    
    def close(self) -> None:
        """No-op for dead letter mailbox."""
        pass
    
    @property
    def dropped_count(self) -> int:
        """Number of messages dropped due to capacity."""
        with self._lock:
            return self._dropped


# ============================================
# MAILBOX FACTORY
# ============================================

@dataclass
class MailboxConfig:
    """Configuration for mailbox creation."""
    mailbox_type: str = "unbounded"
    capacity: int = 1000
    push_timeout: Optional[float] = None


class MailboxFactory:
    """Factory for creating mailboxes based on configuration."""
    
    _mailbox_types = {
        "unbounded": UnboundedMailbox,
        "bounded": BoundedMailbox,
        "priority": PriorityMailbox,
        "control-aware": ControlAwareMailbox,
    }
    
    @classmethod
    def create(cls, config: Optional[MailboxConfig] = None) -> Mailbox:
        """
        Create a mailbox based on configuration.
        
        Args:
            config: Mailbox configuration
            
        Returns:
            New mailbox instance
        """
        if config is None:
            config = MailboxConfig()
        
        mailbox_class = cls._mailbox_types.get(config.mailbox_type)
        if mailbox_class is None:
            raise ValueError(f"Unknown mailbox type: {config.mailbox_type}")
        
        if config.mailbox_type == "bounded":
            return mailbox_class(
                capacity=config.capacity,
                push_timeout=config.push_timeout
            )
        else:
            return mailbox_class()
    
    @classmethod
    def register(cls, name: str, mailbox_class: type) -> None:
        """Register a custom mailbox type."""
        cls._mailbox_types[name] = mailbox_class
