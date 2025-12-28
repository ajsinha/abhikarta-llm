"""
Abhikarta Actor Module - Pekko-inspired Actor System for Python

This module provides a comprehensive actor-based concurrency framework
inspired by Apache Pekko (incubating). It enables building highly
concurrent, distributed, and fault-tolerant applications.

Core Components:
- Actor: Base class for all actors
- ActorSystem: Container and manager for actors
- ActorRef: Immutable reference to an actor
- Props: Configuration for actor creation

Key Features:
- Message-based communication (tell/ask patterns)
- Location transparency
- Supervision hierarchies for fault tolerance
- Multiple dispatcher types (default, pinned, fork-join)
- Various mailbox implementations
- Scheduling and timers
- Common patterns (routers, event bus, circuit breaker)

ACKNOWLEDGEMENT:
This implementation is inspired by Apache Pekko (incubating), the
open-source fork of Akka, licensed under the Apache License 2.0.
We gratefully acknowledge the Apache Software Foundation and the
Pekko community for their pioneering work in actor-based concurrency.
Apache Pekko: https://pekko.apache.org/

Example Usage:
    from abhikarta.actor import Actor, ActorSystem, Props
    
    # Define an actor
    class GreeterActor(Actor):
        def receive(self, message):
            print(f"Hello, {message}!")
            if self.sender:
                self.sender.tell(f"Greeted {message}")
    
    # Create system and actor
    system = ActorSystem()
    greeter = system.actor_of(Props(GreeterActor), "greeter")
    
    # Send messages
    greeter.tell("World")
    
    # Cleanup
    system.terminate()

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha - ajsinha@gmail.com

Version: 1.2.3
"""

__version__ = '1.2.3'

# Core actor classes
from .actor import (
    Actor,
    TypedActor,
    ActorRef,
    ActorContext,
    ActorLifecycle,
    Envelope,
    MessagePriority,
    # System messages
    PoisonPill,
    Kill,
    Restart,
    Identify,
    ActorIdentity,
    Terminated,
    ReceiveTimeout,
    DeadLetter,
)

# Props and configuration
from .props import (
    Props,
    PropsBuilder,
    CommonProps,
)

# Actor system
from .system import (
    ActorSystem,
    ActorSystemConfig,
    ActorCell,
    create_actor_system,
    get_actor_system,
)

# Mailboxes
from .mailbox import (
    Mailbox,
    UnboundedMailbox,
    BoundedMailbox,
    PriorityMailbox,
    ControlAwareMailbox,
    DeadLetterMailbox,
    MailboxConfig,
    MailboxFactory,
)

# Dispatchers
from .dispatcher import (
    Dispatcher,
    DefaultDispatcher,
    PinnedDispatcher,
    CallingThreadDispatcher,
    ForkJoinDispatcher,
    BalancingDispatcher,
    DispatcherConfig,
    DispatcherFactory,
)

# Supervision
from .supervision import (
    SupervisorStrategy,
    OneForOneStrategy,
    AllForOneStrategy,
    ExponentialBackoffStrategy,
    RestartWithLimitStrategy,
    Directive,
    ChildFailure,
    DefaultStrategy,
)

# Scheduling
from .scheduler import (
    Scheduler,
    Cancellable,
    TimerScheduler,
)

# Patterns
from .patterns import (
    # Routers
    RouterActor,
    RoutingLogic,
    RoundRobinLogic,
    RandomLogic,
    BroadcastLogic,
    ScatterGatherLogic,
    ConsistentHashingLogic,
    SmallestMailboxLogic,
    GetRoutees,
    Routees,
    AddRoutee,
    RemoveRoutee,
    # Event Bus
    EventBus,
    # Aggregator
    AggregatorActor,
    AggregatorConfig,
    AggregatedResult,
    # Circuit Breaker
    CircuitBreaker,
    CircuitBreakerActor,
    CircuitState,
    CircuitBreakerStatus,
    CircuitBreakerInfo,
    CircuitBreakerReset,
    CircuitOpen,
    # Stashing
    StashingActor,
)

__all__ = [
    # Version
    '__version__',
    
    # Core
    'Actor',
    'TypedActor',
    'ActorRef',
    'ActorContext',
    'ActorLifecycle',
    'Envelope',
    'MessagePriority',
    
    # System Messages
    'PoisonPill',
    'Kill',
    'Restart',
    'Identify',
    'ActorIdentity',
    'Terminated',
    'ReceiveTimeout',
    'DeadLetter',
    
    # Props
    'Props',
    'PropsBuilder',
    'CommonProps',
    
    # System
    'ActorSystem',
    'ActorSystemConfig',
    'ActorCell',
    'create_actor_system',
    'get_actor_system',
    
    # Mailboxes
    'Mailbox',
    'UnboundedMailbox',
    'BoundedMailbox',
    'PriorityMailbox',
    'ControlAwareMailbox',
    'DeadLetterMailbox',
    'MailboxConfig',
    'MailboxFactory',
    
    # Dispatchers
    'Dispatcher',
    'DefaultDispatcher',
    'PinnedDispatcher',
    'CallingThreadDispatcher',
    'ForkJoinDispatcher',
    'BalancingDispatcher',
    'DispatcherConfig',
    'DispatcherFactory',
    
    # Supervision
    'SupervisorStrategy',
    'OneForOneStrategy',
    'AllForOneStrategy',
    'ExponentialBackoffStrategy',
    'RestartWithLimitStrategy',
    'Directive',
    'ChildFailure',
    'DefaultStrategy',
    
    # Scheduling
    'Scheduler',
    'Cancellable',
    'TimerScheduler',
    
    # Patterns - Routers
    'RouterActor',
    'RoutingLogic',
    'RoundRobinLogic',
    'RandomLogic',
    'BroadcastLogic',
    'ScatterGatherLogic',
    'ConsistentHashingLogic',
    'SmallestMailboxLogic',
    'GetRoutees',
    'Routees',
    'AddRoutee',
    'RemoveRoutee',
    
    # Patterns - Event Bus
    'EventBus',
    
    # Patterns - Aggregator
    'AggregatorActor',
    'AggregatorConfig',
    'AggregatedResult',
    
    # Patterns - Circuit Breaker
    'CircuitBreaker',
    'CircuitBreakerActor',
    'CircuitState',
    'CircuitBreakerStatus',
    'CircuitBreakerInfo',
    'CircuitBreakerReset',
    'CircuitOpen',
    
    # Patterns - Stashing
    'StashingActor',
]
