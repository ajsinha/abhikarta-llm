"""
Router Module - Message routing and load balancing

Routers distribute messages across multiple actors (routees) using
various strategies. Useful for scaling and load balancing.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha - ajsinha@gmail.com

Version: 1.2.3
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict, Type, Callable
from dataclasses import dataclass, field
import threading
import random
import hashlib
import logging

from .actor import Actor, ActorRef, Envelope, MessagePriority
from .props import Props

logger = logging.getLogger(__name__)


# Router-specific messages
@dataclass(frozen=True)
class Broadcast:
    """Send message to all routees."""
    message: Any


@dataclass(frozen=True)
class GetRoutees:
    """Request list of routees."""
    pass


@dataclass
class Routees:
    """Response with list of routees."""
    routees: List[ActorRef]


@dataclass(frozen=True)
class AddRoutee:
    """Add a routee to router."""
    routee: ActorRef


@dataclass(frozen=True)
class RemoveRoutee:
    """Remove a routee from router."""
    routee: ActorRef


class RoutingLogic(ABC):
    """
    Abstract base for routing logic.
    
    Determines how messages are distributed to routees.
    """
    
    @abstractmethod
    def select(self, message: Any, routees: List[ActorRef]) -> List[ActorRef]:
        """
        Select routee(s) for a message.
        
        Args:
            message: The message being routed
            routees: Available routees
            
        Returns:
            List of selected routees
        """
        pass


class RoundRobinLogic(RoutingLogic):
    """
    Round-robin routing logic.
    
    Distributes messages evenly across routees in circular order.
    """
    
    def __init__(self):
        self._index = 0
        self._lock = threading.Lock()
    
    def select(self, message: Any, routees: List[ActorRef]) -> List[ActorRef]:
        if not routees:
            return []
        
        with self._lock:
            idx = self._index % len(routees)
            self._index += 1
        
        return [routees[idx]]


class RandomLogic(RoutingLogic):
    """
    Random routing logic.
    
    Selects a random routee for each message.
    """
    
    def select(self, message: Any, routees: List[ActorRef]) -> List[ActorRef]:
        if not routees:
            return []
        return [random.choice(routees)]


class BroadcastLogic(RoutingLogic):
    """
    Broadcast routing logic.
    
    Sends message to all routees.
    """
    
    def select(self, message: Any, routees: List[ActorRef]) -> List[ActorRef]:
        return list(routees)


class ScatterGatherLogic(RoutingLogic):
    """
    Scatter-gather routing logic.
    
    Sends to all routees and collects responses.
    Used with ask pattern.
    """
    
    def select(self, message: Any, routees: List[ActorRef]) -> List[ActorRef]:
        return list(routees)


class SmallestMailboxLogic(RoutingLogic):
    """
    Smallest mailbox routing logic.
    
    Routes to the routee with the fewest pending messages.
    Provides natural load balancing.
    """
    
    def select(self, message: Any, routees: List[ActorRef]) -> List[ActorRef]:
        if not routees:
            return []
        
        # Get mailbox sizes (if available)
        sizes = []
        for routee in routees:
            try:
                cell = routee._cell
                if cell:
                    sizes.append((cell.mailbox.size(), routee))
                else:
                    sizes.append((0, routee))
            except:
                sizes.append((0, routee))
        
        # Sort by size and return smallest
        sizes.sort(key=lambda x: x[0])
        return [sizes[0][1]]


class ConsistentHashingLogic(RoutingLogic):
    """
    Consistent hashing routing logic.
    
    Routes messages based on a hash of the message key.
    Ensures messages with the same key go to the same routee.
    
    Example:
        # Messages for same user go to same routee
        router.tell(("user_123", "action"))  # Always same routee
    """
    
    def __init__(
        self,
        virtual_nodes: int = 100,
        hash_mapping: Optional[Callable[[Any], Any]] = None
    ):
        self._virtual_nodes = virtual_nodes
        self._hash_mapping = hash_mapping or self._default_hash_mapping
        self._ring: List[tuple] = []
        self._lock = threading.Lock()
    
    def _default_hash_mapping(self, message: Any) -> Any:
        """Extract hash key from message."""
        if isinstance(message, tuple) and len(message) >= 1:
            return message[0]  # Use first element as key
        return message
    
    def _hash(self, key: Any) -> int:
        """Compute hash for a key."""
        key_str = str(key)
        return int(hashlib.md5(key_str.encode()).hexdigest(), 16)
    
    def _build_ring(self, routees: List[ActorRef]) -> None:
        """Build the consistent hash ring."""
        ring = []
        for routee in routees:
            for i in range(self._virtual_nodes):
                vnode_key = f"{routee.path}-{i}"
                hash_val = self._hash(vnode_key)
                ring.append((hash_val, routee))
        ring.sort(key=lambda x: x[0])
        self._ring = ring
    
    def select(self, message: Any, routees: List[ActorRef]) -> List[ActorRef]:
        if not routees:
            return []
        
        with self._lock:
            # Rebuild ring if routees changed
            if len(self._ring) != len(routees) * self._virtual_nodes:
                self._build_ring(routees)
            
            if not self._ring:
                return [routees[0]]
            
            # Find routee for message
            key = self._hash_mapping(message)
            hash_val = self._hash(key)
            
            # Binary search for nearest node
            for ring_hash, routee in self._ring:
                if ring_hash >= hash_val:
                    return [routee]
            
            # Wrap around
            return [self._ring[0][1]]


class TailChoppingLogic(RoutingLogic):
    """
    Tail chopping routing logic.
    
    Sends to first routee, then after a delay to others.
    First response wins.
    """
    
    def __init__(self, interval: float = 0.1):
        self._interval = interval
    
    def select(self, message: Any, routees: List[ActorRef]) -> List[ActorRef]:
        # Returns all routees; actual tail-chopping done in router actor
        return list(routees)


class RouterActor(Actor):
    """
    Base router actor.
    
    Manages a pool of routees and routes messages using
    the configured routing logic.
    """
    
    def __init__(
        self,
        routing_logic: RoutingLogic,
        routees: Optional[List[ActorRef]] = None
    ):
        super().__init__()
        self._routing_logic = routing_logic
        self._routees: List[ActorRef] = list(routees) if routees else []
        self._lock = threading.Lock()
    
    def receive(self, message: Any) -> None:
        # Handle router management messages
        if isinstance(message, Broadcast):
            self._broadcast(message.message)
        elif isinstance(message, GetRoutees):
            self.sender.tell(Routees(tuple(self._routees)))
        elif isinstance(message, AddRoutee):
            self._add_routee(message.routee)
        elif isinstance(message, RemoveRoutee):
            self._remove_routee(message.routee)
        else:
            # Route to selected routees
            self._route(message)
    
    def _route(self, message: Any) -> None:
        """Route message to selected routees."""
        with self._lock:
            routees = list(self._routees)
        
        if not routees:
            logger.warning(f"No routees available for routing: {message}")
            self.context.system._dead_letters(
                Envelope(message, self.sender),
                self.self
            )
            return
        
        selected = self._routing_logic.select(message, routees)
        for routee in selected:
            routee.tell(message, sender=self.sender)
    
    def _broadcast(self, message: Any) -> None:
        """Broadcast message to all routees."""
        with self._lock:
            routees = list(self._routees)
        
        for routee in routees:
            routee.tell(message, sender=self.sender)
    
    def _add_routee(self, routee: ActorRef) -> None:
        """Add a routee."""
        with self._lock:
            if routee not in self._routees:
                self._routees.append(routee)
                self.context.watch(routee)
    
    def _remove_routee(self, routee: ActorRef) -> None:
        """Remove a routee."""
        with self._lock:
            if routee in self._routees:
                self._routees.remove(routee)
                self.context.unwatch(routee)
    
    def pre_start(self) -> None:
        """Watch all initial routees."""
        for routee in self._routees:
            self.context.watch(routee)


class PoolRouter(RouterActor):
    """
    Router that manages a pool of child actors.
    
    Creates and supervises routee actors as children.
    """
    
    def __init__(
        self,
        routing_logic: RoutingLogic,
        routee_props: Props,
        pool_size: int = 5
    ):
        super().__init__(routing_logic)
        self._routee_props = routee_props
        self._pool_size = pool_size
    
    def pre_start(self) -> None:
        """Create routee pool."""
        for i in range(self._pool_size):
            routee = self.context.spawn(
                self._routee_props,
                name=f"routee-{i}"
            )
            self._routees.append(routee)
            self.context.watch(routee)


class GroupRouter(RouterActor):
    """
    Router that routes to a group of existing actors.
    
    Does not create or supervise routees.
    """
    
    def __init__(
        self,
        routing_logic: RoutingLogic,
        routee_paths: List[str]
    ):
        super().__init__(routing_logic)
        self._routee_paths = routee_paths
    
    def pre_start(self) -> None:
        """Resolve routee paths to refs."""
        for path in self._routee_paths:
            ref = self.context.system.actor_selection(path)
            if ref:
                self._routees.append(ref)
                self.context.watch(ref)


# Convenience router props

def round_robin_pool(props: Props, size: int = 5) -> Props:
    """Create round-robin pool router props."""
    return Props(
        PoolRouter,
        args=(RoundRobinLogic(), props, size)
    )


def random_pool(props: Props, size: int = 5) -> Props:
    """Create random pool router props."""
    return Props(
        PoolRouter,
        args=(RandomLogic(), props, size)
    )


def broadcast_pool(props: Props, size: int = 5) -> Props:
    """Create broadcast pool router props."""
    return Props(
        PoolRouter,
        args=(BroadcastLogic(), props, size)
    )


def consistent_hashing_pool(
    props: Props,
    size: int = 5,
    virtual_nodes: int = 100
) -> Props:
    """Create consistent hashing pool router props."""
    return Props(
        PoolRouter,
        args=(ConsistentHashingLogic(virtual_nodes), props, size)
    )


def smallest_mailbox_pool(props: Props, size: int = 5) -> Props:
    """Create smallest mailbox pool router props."""
    return Props(
        PoolRouter,
        args=(SmallestMailboxLogic(), props, size)
    )


def round_robin_group(paths: List[str]) -> Props:
    """Create round-robin group router props."""
    return Props(
        GroupRouter,
        args=(RoundRobinLogic(), paths)
    )


def broadcast_group(paths: List[str]) -> Props:
    """Create broadcast group router props."""
    return Props(
        GroupRouter,
        args=(BroadcastLogic(), paths)
    )
