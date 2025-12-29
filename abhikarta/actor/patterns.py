"""
Patterns Module - Common actor patterns and utilities

This module provides ready-to-use implementations of common actor
patterns for building scalable systems:
- Routers: Load balancing and routing
- Event Bus: Pub/sub messaging
- Aggregators: Collecting responses
- Circuit Breakers: Fault tolerance

Acknowledgement:
This implementation is inspired by Apache Pekko (incubating).

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha - ajsinha@gmail.com

Version: 1.3.0
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Set, Type
from enum import Enum, auto
import threading
import random
import time
import logging

from .actor import Actor, ActorRef, TypedActor, ReceiveTimeout
from .props import Props

logger = logging.getLogger(__name__)


# ============================================
# ROUTER PATTERNS
# ============================================

class RoutingLogic(ABC):
    """Base class for routing logic."""
    
    @abstractmethod
    def select(self, message: Any, routees: List[ActorRef]) -> List[ActorRef]:
        """
        Select routees for a message.
        
        Args:
            message: The message being routed
            routees: Available routees
            
        Returns:
            List of selected routees
        """
        pass


class RoundRobinLogic(RoutingLogic):
    """Round-robin routing - each message to next routee in sequence."""
    
    def __init__(self):
        self._index = 0
        self._lock = threading.Lock()
    
    def select(self, message: Any, routees: List[ActorRef]) -> List[ActorRef]:
        if not routees:
            return []
        
        with self._lock:
            routee = routees[self._index % len(routees)]
            self._index += 1
        
        return [routee]


class RandomLogic(RoutingLogic):
    """Random routing - each message to random routee."""
    
    def select(self, message: Any, routees: List[ActorRef]) -> List[ActorRef]:
        if not routees:
            return []
        return [random.choice(routees)]


class BroadcastLogic(RoutingLogic):
    """Broadcast routing - each message to all routees."""
    
    def select(self, message: Any, routees: List[ActorRef]) -> List[ActorRef]:
        return list(routees)


class ScatterGatherLogic(RoutingLogic):
    """Scatter-gather - message to all, first response wins."""
    
    def select(self, message: Any, routees: List[ActorRef]) -> List[ActorRef]:
        return list(routees)


class SmallestMailboxLogic(RoutingLogic):
    """Route to routee with smallest mailbox (for local actors)."""
    
    def select(self, message: Any, routees: List[ActorRef]) -> List[ActorRef]:
        if not routees:
            return []
        # In a full implementation, would check mailbox sizes
        return [random.choice(routees)]


class ConsistentHashingLogic(RoutingLogic):
    """
    Consistent hashing - messages with same key go to same routee.
    
    Message must have a 'hash_key' attribute or be hashable.
    """
    
    def __init__(self, virtual_nodes: int = 100):
        self._virtual_nodes = virtual_nodes
        self._ring: Dict[int, int] = {}
        self._sorted_keys: List[int] = []
        self._lock = threading.Lock()
    
    def _build_ring(self, routees: List[ActorRef]) -> None:
        """Build consistent hash ring."""
        self._ring = {}
        for i, routee in enumerate(routees):
            for j in range(self._virtual_nodes):
                key = hash(f"{routee.path}:{j}")
                self._ring[key] = i
        self._sorted_keys = sorted(self._ring.keys())
    
    def select(self, message: Any, routees: List[ActorRef]) -> List[ActorRef]:
        if not routees:
            return []
        
        with self._lock:
            if len(self._ring) != len(routees) * self._virtual_nodes:
                self._build_ring(routees)
            
            # Get hash key from message
            if hasattr(message, 'hash_key'):
                hash_key = hash(message.hash_key)
            else:
                hash_key = hash(message)
            
            # Find closest node in ring
            for key in self._sorted_keys:
                if hash_key <= key:
                    return [routees[self._ring[key]]]
            
            # Wrap around
            if self._sorted_keys:
                return [routees[self._ring[self._sorted_keys[0]]]]
        
        return [routees[0]]


class RouterActor(Actor):
    """
    Actor that routes messages to a pool of routees.
    
    Example:
        # Create router with 5 worker routees
        router = system.actor_of(
            Props(RouterActor, args=(
                Props(WorkerActor),
                5,
                RoundRobinLogic()
            )),
            "router"
        )
        
        # Messages are routed to workers
        router.tell(WorkMessage(data))
    """
    
    def __init__(self, routee_props: Props, num_routees: int,
                 routing_logic: Optional[RoutingLogic] = None):
        super().__init__()
        self._routee_props = routee_props
        self._num_routees = num_routees
        self._routing_logic = routing_logic or RoundRobinLogic()
        self._routees: List[ActorRef] = []
    
    def pre_start(self) -> None:
        """Create routee pool."""
        for i in range(self._num_routees):
            routee = self.context.actor_of(self._routee_props, f"routee-{i}")
            self._routees.append(routee)
            self.context.watch(routee)
        logger.info(f"Router {self.self.path} started with {self._num_routees} routees")
    
    def receive(self, message: Any) -> None:
        """Route message to selected routees."""
        if isinstance(message, GetRoutees):
            if self.sender:
                self.sender.tell(Routees(list(self._routees)))
        elif isinstance(message, AddRoutee):
            self._add_routee(message.props, message.name)
        elif isinstance(message, RemoveRoutee):
            self._remove_routee(message.ref)
        else:
            # Route the message
            selected = self._routing_logic.select(message, self._routees)
            for routee in selected:
                routee.tell(message, self.sender)
    
    def _add_routee(self, props: Props, name: Optional[str] = None) -> None:
        """Add a new routee."""
        if name is None:
            name = f"routee-{len(self._routees)}"
        routee = self.context.actor_of(props, name)
        self._routees.append(routee)
        self.context.watch(routee)
    
    def _remove_routee(self, ref: ActorRef) -> None:
        """Remove a routee."""
        if ref in self._routees:
            self._routees.remove(ref)
            self.context.stop(ref)


@dataclass(frozen=True)
class GetRoutees:
    """Request to get list of routees."""
    pass


@dataclass(frozen=True)
class Routees:
    """Response containing list of routees."""
    routees: List[ActorRef]


@dataclass(frozen=True)
class AddRoutee:
    """Request to add a routee."""
    props: Props
    name: Optional[str] = None


@dataclass(frozen=True)
class RemoveRoutee:
    """Request to remove a routee."""
    ref: ActorRef


# ============================================
# EVENT BUS PATTERN
# ============================================

class EventBus:
    """
    Pub/Sub event bus for decoupled communication.
    
    Actors can subscribe to event types and receive all events
    of that type published to the bus.
    
    Example:
        bus = EventBus()
        bus.subscribe(my_actor, OrderEvent)
        bus.publish(OrderEvent(order_id=123))
    """
    
    def __init__(self):
        self._subscribers: Dict[Type, Set[ActorRef]] = {}
        self._lock = threading.Lock()
    
    def subscribe(self, subscriber: ActorRef, event_type: Type) -> None:
        """
        Subscribe to an event type.
        
        Args:
            subscriber: Actor to receive events
            event_type: Type of events to receive
        """
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = set()
            self._subscribers[event_type].add(subscriber)
    
    def unsubscribe(self, subscriber: ActorRef, event_type: Optional[Type] = None) -> None:
        """
        Unsubscribe from events.
        
        Args:
            subscriber: Actor to unsubscribe
            event_type: Specific type, or None for all types
        """
        with self._lock:
            if event_type:
                if event_type in self._subscribers:
                    self._subscribers[event_type].discard(subscriber)
            else:
                for subs in self._subscribers.values():
                    subs.discard(subscriber)
    
    def publish(self, event: Any, sender: Optional[ActorRef] = None) -> int:
        """
        Publish an event to all subscribers.
        
        Args:
            event: Event to publish
            sender: Optional sender reference
            
        Returns:
            Number of subscribers notified
        """
        event_type = type(event)
        count = 0
        
        with self._lock:
            # Get subscribers for this type and parent types
            subscribers = set()
            for t, subs in self._subscribers.items():
                if isinstance(event, t):
                    subscribers.update(subs)
        
        for subscriber in subscribers:
            subscriber.tell(event, sender)
            count += 1
        
        return count
    
    def subscriber_count(self, event_type: Type) -> int:
        """Get number of subscribers for an event type."""
        with self._lock:
            return len(self._subscribers.get(event_type, set()))


# ============================================
# AGGREGATOR PATTERN
# ============================================

@dataclass
class AggregatorConfig:
    """Configuration for aggregator."""
    expected_replies: int
    timeout: float = 5.0
    reply_type: Optional[Type] = None


class AggregatorActor(Actor):
    """
    Collects responses from multiple actors.
    
    Waits for a specified number of replies or timeout,
    then sends aggregated result to the original requester.
    
    Example:
        # Send to multiple services
        aggregator = system.actor_of(Props(
            AggregatorActor,
            args=(client_ref, AggregatorConfig(expected_replies=3))
        ))
        
        for service in services:
            service.tell(request, aggregator)
    """
    
    def __init__(self, reply_to: ActorRef, config: AggregatorConfig):
        super().__init__()
        self._reply_to = reply_to
        self._config = config
        self._replies: List[Any] = []
        self._completed = False
    
    def pre_start(self) -> None:
        """Set timeout."""
        self.context.set_receive_timeout(self._config.timeout)
    
    def receive(self, message: Any) -> None:
        """Collect replies."""
        if self._completed:
            return
        
        if isinstance(message, ReceiveTimeout):
            self._complete()
            return
        
        # Check if expected type
        if self._config.reply_type:
            if not isinstance(message, self._config.reply_type):
                return
        
        self._replies.append(message)
        
        if len(self._replies) >= self._config.expected_replies:
            self._complete()
    
    def _complete(self) -> None:
        """Send aggregated result."""
        self._completed = True
        self._reply_to.tell(AggregatedResult(list(self._replies)), self.self)
        self.context.stop(self.self)


@dataclass
class AggregatedResult:
    """Result from aggregator."""
    replies: List[Any]


# ============================================
# CIRCUIT BREAKER PATTERN
# ============================================

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = auto()     # Normal operation
    OPEN = auto()       # Failing, rejecting requests
    HALF_OPEN = auto()  # Testing if recovered


class CircuitBreaker:
    """
    Circuit breaker for protecting against cascading failures.
    
    Tracks failures and "opens" the circuit when a threshold is
    exceeded, preventing further calls until recovery.
    
    Example:
        breaker = CircuitBreaker(max_failures=5, reset_timeout=30.0)
        
        if breaker.allow_request():
            try:
                result = call_service()
                breaker.record_success()
            except Exception as e:
                breaker.record_failure()
    """
    
    def __init__(self, max_failures: int = 5, reset_timeout: float = 30.0,
                 half_open_max_calls: int = 1):
        self._max_failures = max_failures
        self._reset_timeout = reset_timeout
        self._half_open_max_calls = half_open_max_calls
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_calls = 0
        self._lock = threading.Lock()
    
    @property
    def state(self) -> CircuitState:
        """Current circuit state."""
        with self._lock:
            self._check_reset()
            return self._state
    
    def _check_reset(self) -> None:
        """Check if circuit should transition from open to half-open."""
        if self._state == CircuitState.OPEN:
            if self._last_failure_time:
                elapsed = time.time() - self._last_failure_time
                if elapsed >= self._reset_timeout:
                    self._state = CircuitState.HALF_OPEN
                    self._half_open_calls = 0
                    logger.info("Circuit breaker transitioning to HALF_OPEN")
    
    def allow_request(self) -> bool:
        """
        Check if a request should be allowed.
        
        Returns:
            True if request should proceed, False if rejected
        """
        with self._lock:
            self._check_reset()
            
            if self._state == CircuitState.CLOSED:
                return True
            elif self._state == CircuitState.OPEN:
                return False
            else:  # HALF_OPEN
                if self._half_open_calls < self._half_open_max_calls:
                    self._half_open_calls += 1
                    return True
                return False
    
    def record_success(self) -> None:
        """Record a successful call."""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                logger.info("Circuit breaker CLOSED after successful half-open call")
            elif self._state == CircuitState.CLOSED:
                self._failure_count = 0
    
    def record_failure(self) -> None:
        """Record a failed call."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                logger.warning("Circuit breaker OPEN after half-open failure")
            elif self._state == CircuitState.CLOSED:
                if self._failure_count >= self._max_failures:
                    self._state = CircuitState.OPEN
                    logger.warning(
                        f"Circuit breaker OPEN after {self._failure_count} failures"
                    )
    
    def reset(self) -> None:
        """Manually reset the circuit breaker."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._last_failure_time = None


class CircuitBreakerActor(Actor):
    """
    Actor wrapper with circuit breaker protection.
    
    Wraps another actor and applies circuit breaker logic
    to protect against failures.
    """
    
    def __init__(self, target_props: Props, 
                 max_failures: int = 5,
                 reset_timeout: float = 30.0):
        super().__init__()
        self._target_props = target_props
        self._breaker = CircuitBreaker(max_failures, reset_timeout)
        self._target: Optional[ActorRef] = None
    
    def pre_start(self) -> None:
        """Create target actor."""
        self._target = self.context.actor_of(self._target_props, "target")
        self.context.watch(self._target)
    
    def receive(self, message: Any) -> None:
        """Forward message if circuit allows."""
        if isinstance(message, CircuitBreakerStatus):
            if self.sender:
                self.sender.tell(CircuitBreakerInfo(self._breaker.state))
        elif isinstance(message, CircuitBreakerReset):
            self._breaker.reset()
        elif self._target:
            if self._breaker.allow_request():
                self._target.tell(message, self.sender)
            else:
                if self.sender:
                    self.sender.tell(CircuitOpen())


@dataclass(frozen=True)
class CircuitBreakerStatus:
    """Request circuit breaker status."""
    pass


@dataclass(frozen=True)
class CircuitBreakerInfo:
    """Circuit breaker status response."""
    state: CircuitState


@dataclass(frozen=True)
class CircuitBreakerReset:
    """Request to reset circuit breaker."""
    pass


@dataclass(frozen=True)
class CircuitOpen:
    """Response when circuit is open."""
    pass


# ============================================
# STASH PATTERN
# ============================================

class StashingActor(Actor):
    """
    Actor that can stash messages for later processing.
    
    Useful when an actor needs to defer message processing
    until some condition is met.
    
    Example:
        class InitializingActor(StashingActor):
            def __init__(self):
                super().__init__()
                self._initialized = False
            
            def receive(self, message):
                if isinstance(message, InitComplete):
                    self._initialized = True
                    self.unstash_all()  # Process deferred messages
                elif not self._initialized:
                    self.stash(message)  # Defer until initialized
                else:
                    self.handle_message(message)
    """
    
    def __init__(self):
        super().__init__()
        self._stash: List[Any] = []
        self._stash_lock = threading.Lock()
    
    def stash(self, message: Any = None) -> None:
        """
        Stash a message for later processing.
        
        Args:
            message: Message to stash (uses current message if None)
        """
        if message is None:
            message = self.context._sender, getattr(self, '_current_message', None)
        with self._stash_lock:
            self._stash.append(message)
    
    def unstash(self) -> None:
        """Process one stashed message."""
        with self._stash_lock:
            if self._stash:
                sender, message = self._stash.pop(0)
                self.self.tell(message, sender)
    
    def unstash_all(self) -> None:
        """Process all stashed messages."""
        with self._stash_lock:
            while self._stash:
                sender, message = self._stash.pop(0)
                self.self.tell(message, sender)
    
    def clear_stash(self) -> int:
        """Clear all stashed messages."""
        with self._stash_lock:
            count = len(self._stash)
            self._stash.clear()
            return count
    
    @property
    def stash_size(self) -> int:
        """Number of stashed messages."""
        with self._stash_lock:
            return len(self._stash)
