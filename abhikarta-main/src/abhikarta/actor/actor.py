"""
Actor Base Module - Core actor implementation inspired by Apache Pekko

This module provides the foundational Actor class and message types for building
highly concurrent, thread-safe, and deadlock-safe distributed systems.

Design Philosophy:
- Everything is an actor that communicates via messages
- No shared mutable state between actors
- Location transparency - actors can be local or remote
- Supervision hierarchies for fault tolerance

Acknowledgement:
This implementation is inspired by Apache Pekko (incubating), the open-source
fork of Akka. We gratefully acknowledge the Apache Software Foundation and
the Pekko community for their pioneering work in actor-based concurrency.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha - ajsinha@gmail.com

Version: 1.3.0
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Type, Union
from enum import Enum, auto
import threading
import queue
import time
import uuid
import logging
import traceback
import weakref
from concurrent.futures import ThreadPoolExecutor, Future
from contextlib import contextmanager

logger = logging.getLogger(__name__)


# ============================================
# MESSAGE TYPES
# ============================================

class MessagePriority(Enum):
    """Priority levels for messages."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    SYSTEM = 3  # Reserved for system messages


@dataclass(frozen=True)
class Envelope:
    """
    Message envelope containing the message and metadata.
    
    Immutable to ensure thread safety.
    """
    message: Any
    sender: Optional['ActorRef'] = None
    priority: MessagePriority = MessagePriority.NORMAL
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    
    def __lt__(self, other):
        """For priority queue ordering."""
        if isinstance(other, Envelope):
            return self.priority.value > other.priority.value
        return NotImplemented


# System Messages
@dataclass(frozen=True)
class PoisonPill:
    """Stops the actor gracefully after processing current messages."""
    pass


@dataclass(frozen=True)
class Kill:
    """Immediately stops the actor, discarding pending messages."""
    pass


@dataclass(frozen=True)
class Restart:
    """Triggers actor restart."""
    reason: Optional[Exception] = None


@dataclass(frozen=True)
class Identify:
    """Request actor identity."""
    message_id: int = 0


@dataclass(frozen=True)
class ActorIdentity:
    """Response to Identify message."""
    ref: Optional['ActorRef']
    message_id: int = 0


@dataclass(frozen=True)
class Terminated:
    """Notification that a watched actor has terminated."""
    actor: 'ActorRef'
    existence_confirmed: bool = True


@dataclass(frozen=True)
class ReceiveTimeout:
    """Sent when actor hasn't received messages within timeout."""
    pass


@dataclass(frozen=True)
class DeadLetter:
    """Message that couldn't be delivered."""
    message: Any
    sender: Optional['ActorRef']
    recipient: 'ActorRef'


# ============================================
# ACTOR LIFECYCLE
# ============================================

class ActorLifecycle(Enum):
    """Actor lifecycle states."""
    CREATED = auto()
    STARTING = auto()
    RUNNING = auto()
    RESTARTING = auto()
    STOPPING = auto()
    STOPPED = auto()
    FAILED = auto()


# ============================================
# ACTOR REFERENCE
# ============================================

class ActorRef:
    """
    Immutable, serializable reference to an actor.
    
    ActorRef is the handle through which messages are sent to actors.
    It provides location transparency - the actual actor could be
    local or remote.
    """
    
    __slots__ = ('_path', '_uid', '_system_ref', '_mailbox_ref')
    
    def __init__(self, path: str, uid: str, system: 'ActorSystem', mailbox: 'Mailbox'):
        self._path = path
        self._uid = uid
        self._system_ref = weakref.ref(system)
        self._mailbox_ref = weakref.ref(mailbox)
    
    @property
    def path(self) -> str:
        """Actor path in the hierarchy."""
        return self._path
    
    @property
    def name(self) -> str:
        """Actor name (last component of path)."""
        return self._path.split('/')[-1]
    
    @property
    def uid(self) -> str:
        """Unique identifier for this incarnation."""
        return self._uid
    
    def tell(self, message: Any, sender: Optional['ActorRef'] = None) -> None:
        """
        Send a message to this actor (fire-and-forget).
        
        Also known as "!" operator in Scala.
        
        Args:
            message: The message to send
            sender: Optional sender reference for replies
        """
        mailbox = self._mailbox_ref()
        if mailbox is None:
            system = self._system_ref()
            if system:
                system._publish_dead_letter(DeadLetter(message, sender, self))
            return
        
        envelope = Envelope(message=message, sender=sender)
        mailbox.enqueue(envelope)
    
    def __lshift__(self, message: Any) -> None:
        """Operator << for sending messages: actor_ref << message"""
        self.tell(message)
    
    def ask(self, message: Any, timeout: float = 5.0) -> Future:
        """
        Send a message and get a Future for the response.
        
        Also known as "?" operator in Scala.
        
        Args:
            message: The message to send
            timeout: Timeout in seconds
            
        Returns:
            Future that will contain the response
        """
        system = self._system_ref()
        if system is None:
            future = Future()
            future.set_exception(RuntimeError("Actor system is terminated"))
            return future
        
        return system._ask(self, message, timeout)
    
    def forward(self, message: Any, context: 'ActorContext') -> None:
        """
        Forward a message keeping the original sender.
        
        Args:
            message: Message to forward
            context: Current actor's context
        """
        self.tell(message, context.sender)
    
    def __eq__(self, other):
        if isinstance(other, ActorRef):
            return self._path == other._path and self._uid == other._uid
        return False
    
    def __hash__(self):
        return hash((self._path, self._uid))
    
    def __repr__(self):
        return f"ActorRef({self._path})"
    
    def __str__(self):
        return self._path


# ============================================
# ACTOR CONTEXT
# ============================================

class ActorContext:
    """
    Runtime context available to an actor during message processing.
    
    Provides access to:
    - Self reference
    - Sender of current message
    - Parent actor
    - Children actors
    - Actor system
    - Supervision
    - Scheduling
    """
    
    def __init__(self, 
                 actor: 'Actor',
                 self_ref: ActorRef,
                 system: 'ActorSystem',
                 parent: Optional[ActorRef] = None):
        self._actor = actor
        self._self = self_ref
        self._system = system
        self._parent = parent
        self._children: Dict[str, ActorRef] = {}
        self._watchers: List[ActorRef] = []
        self._watching: List[ActorRef] = []
        self._sender: Optional[ActorRef] = None
        self._receive_timeout: Optional[float] = None
        self._lock = threading.RLock()
    
    @property
    def self(self) -> ActorRef:
        """Reference to self."""
        return self._self
    
    @property
    def sender(self) -> Optional[ActorRef]:
        """Sender of the current message being processed."""
        return self._sender
    
    @property
    def parent(self) -> Optional[ActorRef]:
        """Parent actor reference."""
        return self._parent
    
    @property
    def children(self) -> Dict[str, ActorRef]:
        """Dictionary of child actors."""
        with self._lock:
            return dict(self._children)
    
    @property
    def system(self) -> 'ActorSystem':
        """The actor system."""
        return self._system
    
    def actor_of(self, props: 'Props', name: Optional[str] = None) -> ActorRef:
        """
        Create a child actor.
        
        Args:
            props: Actor properties/configuration
            name: Optional actor name (generated if not provided)
            
        Returns:
            ActorRef to the new child actor
        """
        if name is None:
            name = f"actor-{uuid.uuid4().hex[:8]}"
        
        child_path = f"{self._self.path}/{name}"
        
        with self._lock:
            if name in self._children:
                raise ValueError(f"Child actor '{name}' already exists")
            
            child_ref = self._system._create_actor(props, child_path, self._self)
            self._children[name] = child_ref
            return child_ref
    
    def stop(self, actor: ActorRef) -> None:
        """
        Stop an actor.
        
        Args:
            actor: The actor to stop
        """
        if actor == self._self:
            self._system._stop_actor(self._self)
        elif actor.name in self._children:
            with self._lock:
                del self._children[actor.name]
            self._system._stop_actor(actor)
        else:
            actor.tell(PoisonPill())
    
    def watch(self, actor: ActorRef) -> ActorRef:
        """
        Watch another actor for termination.
        
        Args:
            actor: The actor to watch
            
        Returns:
            The watched actor reference
        """
        with self._lock:
            if actor not in self._watching:
                self._watching.append(actor)
                self._system._register_watcher(actor, self._self)
        return actor
    
    def unwatch(self, actor: ActorRef) -> ActorRef:
        """
        Stop watching an actor.
        
        Args:
            actor: The actor to unwatch
            
        Returns:
            The unwatched actor reference
        """
        with self._lock:
            if actor in self._watching:
                self._watching.remove(actor)
                self._system._unregister_watcher(actor, self._self)
        return actor
    
    def set_receive_timeout(self, timeout: Optional[float]) -> None:
        """
        Set a timeout for receiving messages.
        
        If no message is received within the timeout, a ReceiveTimeout
        message will be sent to the actor.
        
        Args:
            timeout: Timeout in seconds, or None to disable
        """
        self._receive_timeout = timeout
    
    def become(self, behavior: Callable[[Any], None]) -> None:
        """
        Change the actor's message handling behavior.
        
        Args:
            behavior: New message handler function
        """
        self._actor._behavior_stack.append(behavior)
    
    def unbecome(self) -> None:
        """Revert to the previous behavior."""
        if len(self._actor._behavior_stack) > 1:
            self._actor._behavior_stack.pop()
    
    def schedule_once(self, delay: float, receiver: ActorRef, message: Any) -> 'Cancellable':
        """
        Schedule a message to be sent once after a delay.
        
        Args:
            delay: Delay in seconds
            receiver: Target actor
            message: Message to send
            
        Returns:
            Cancellable handle
        """
        return self._system.scheduler.schedule_once(delay, receiver, message, self._self)
    
    def schedule_repeatedly(self, initial_delay: float, interval: float,
                           receiver: ActorRef, message: Any) -> 'Cancellable':
        """
        Schedule a message to be sent repeatedly.
        
        Args:
            initial_delay: Initial delay in seconds
            interval: Interval between messages in seconds
            receiver: Target actor
            message: Message to send
            
        Returns:
            Cancellable handle
        """
        return self._system.scheduler.schedule_repeatedly(
            initial_delay, interval, receiver, message, self._self
        )


# ============================================
# ACTOR BASE CLASS
# ============================================

class Actor(ABC):
    """
    Base class for all actors.
    
    An actor is a computational entity that:
    - Processes messages one at a time
    - Has private state not accessible by other actors
    - Can create child actors
    - Can send messages to other actors
    - Can change its behavior for subsequent messages
    
    Subclasses must implement the `receive` method.
    
    Example:
        class GreetingActor(Actor):
            def __init__(self):
                super().__init__()
                self.greeting_count = 0
            
            def receive(self, message):
                if isinstance(message, str):
                    self.greeting_count += 1
                    print(f"Hello, {message}! (Greeting #{self.greeting_count})")
                    if self.context.sender:
                        self.context.sender.tell(f"Greeted {message}")
    """
    
    def __init__(self):
        self._context: Optional[ActorContext] = None
        self._behavior_stack: List[Callable[[Any], None]] = []
        self._lifecycle = ActorLifecycle.CREATED
    
    @property
    def context(self) -> ActorContext:
        """Actor's runtime context."""
        if self._context is None:
            raise RuntimeError("Actor context not initialized")
        return self._context
    
    @property
    def self(self) -> ActorRef:
        """Reference to self."""
        return self.context.self
    
    @property
    def sender(self) -> Optional[ActorRef]:
        """Sender of current message."""
        return self.context.sender
    
    def _set_context(self, context: ActorContext) -> None:
        """Internal: Set the actor context."""
        self._context = context
        self._behavior_stack = [self.receive]
    
    @abstractmethod
    def receive(self, message: Any) -> None:
        """
        Process an incoming message.
        
        This method must be implemented by all actor subclasses.
        
        Args:
            message: The received message
        """
        pass
    
    def pre_start(self) -> None:
        """
        Called before the actor starts processing messages.
        
        Override this for initialization logic.
        """
        pass
    
    def post_stop(self) -> None:
        """
        Called after the actor has stopped.
        
        Override this for cleanup logic.
        """
        pass
    
    def pre_restart(self, reason: Exception, message: Optional[Any]) -> None:
        """
        Called before actor restart.
        
        Default behavior stops all children.
        
        Args:
            reason: The exception that caused the restart
            message: The message being processed when failure occurred
        """
        for child_ref in self.context.children.values():
            self.context.stop(child_ref)
        self.post_stop()
    
    def post_restart(self, reason: Exception) -> None:
        """
        Called after actor restart.
        
        Default behavior calls pre_start.
        
        Args:
            reason: The exception that caused the restart
        """
        self.pre_start()
    
    def unhandled(self, message: Any) -> None:
        """
        Called when a message is not handled by receive.
        
        Args:
            message: The unhandled message
        """
        if isinstance(message, Terminated):
            logger.warning(f"Unhandled Terminated message for {message.actor}")
        else:
            logger.debug(f"Unhandled message in {self.self}: {type(message).__name__}")
    
    def _process_message(self, envelope: Envelope) -> None:
        """Internal: Process a single message envelope."""
        self._context._sender = envelope.sender
        message = envelope.message
        
        try:
            # Get current behavior
            if self._behavior_stack:
                behavior = self._behavior_stack[-1]
                behavior(message)
            else:
                self.receive(message)
        except Exception as e:
            logger.error(f"Error processing message in {self.self}: {e}")
            raise
        finally:
            self._context._sender = None


class TypedActor(Actor):
    """
    Actor with type-based message dispatch.
    
    Provides automatic routing of messages based on their type,
    similar to pattern matching.
    
    Example:
        class BankAccount(TypedActor):
            def __init__(self):
                super().__init__()
                self.balance = 0
            
            @TypedActor.handler(Deposit)
            def handle_deposit(self, msg: Deposit):
                self.balance += msg.amount
            
            @TypedActor.handler(Withdraw)
            def handle_withdraw(self, msg: Withdraw):
                if self.balance >= msg.amount:
                    self.balance -= msg.amount
    """
    
    _handlers: Dict[Type, Callable] = {}
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._handlers = {}
        for name in dir(cls):
            # Skip dunder attributes to avoid AttributeError on __abstractmethods__
            if name.startswith('__'):
                continue
            try:
                method = getattr(cls, name)
                if hasattr(method, '_message_type'):
                    cls._handlers[method._message_type] = method
            except AttributeError:
                # Skip attributes that can't be accessed
                continue
    
    @staticmethod
    def handler(message_type: Type):
        """Decorator to register a message handler."""
        def decorator(func):
            func._message_type = message_type
            return func
        return decorator
    
    def receive(self, message: Any) -> None:
        """Route message to appropriate handler based on type."""
        handler = self._handlers.get(type(message))
        if handler:
            handler(self, message)
        else:
            self.unhandled(message)
