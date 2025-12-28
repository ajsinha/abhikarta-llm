# Abhikarta Actor System - Quickstart Guide

## Overview

The Abhikarta Actor System provides a powerful, Pekko-inspired framework for building highly concurrent, distributed, and fault-tolerant applications. This guide will help you get started with actors in minutes.

**Version:** 1.2.2

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Quick Start](#quick-start)
3. [Creating Actors](#creating-actors)
4. [Sending Messages](#sending-messages)
5. [Actor Lifecycle](#actor-lifecycle)
6. [Supervision & Fault Tolerance](#supervision--fault-tolerance)
7. [Common Patterns](#common-patterns)
8. [Best Practices](#best-practices)
9. [Integration with Abhikarta](#integration-with-abhikarta)

---

## Core Concepts

### What is an Actor?

An **Actor** is a computational entity that:
- Processes **messages** one at a time (sequential, no race conditions)
- Has **private state** not accessible by other actors
- Can **create child actors** (supervision hierarchy)
- Can **send messages** to other actors
- Can **change behavior** for subsequent messages

### Key Components

| Component | Description |
|-----------|-------------|
| `Actor` | Base class for all actors |
| `ActorRef` | Immutable reference to an actor |
| `ActorSystem` | Container managing all actors |
| `Props` | Configuration for creating actors |
| `Mailbox` | Queue holding messages for an actor |
| `Dispatcher` | Thread pool executing actors |

---

## Quick Start

### Installation

The actor module is included in Abhikarta-LLM:

```python
from abhikarta.actor import Actor, ActorSystem, Props
```

### Hello World Example

```python
from abhikarta.actor import Actor, ActorSystem, Props

# 1. Define an Actor
class GreeterActor(Actor):
    def receive(self, message):
        print(f"Hello, {message}!")

# 2. Create an ActorSystem
system = ActorSystem()

# 3. Create an Actor
greeter = system.actor_of(Props(GreeterActor), "greeter")

# 4. Send a Message
greeter.tell("World")  # Output: Hello, World!

# 5. Cleanup
system.terminate()
```

### Using Context Manager

```python
from abhikarta.actor import create_actor_system, Props

class MyActor(Actor):
    def receive(self, message):
        print(f"Received: {message}")

with create_actor_system("my-system") as system:
    actor = system.actor_of(Props(MyActor), "my-actor")
    actor.tell("Hello!")
    # System automatically terminates on exit
```

---

## Creating Actors

### Basic Actor

```python
from abhikarta.actor import Actor

class CounterActor(Actor):
    def __init__(self, initial_value=0):
        super().__init__()
        self.count = initial_value
    
    def receive(self, message):
        if message == "increment":
            self.count += 1
        elif message == "get":
            if self.sender:
                self.sender.tell(self.count)
```

### TypedActor (Type-Safe)

```python
from dataclasses import dataclass
from abhikarta.actor import TypedActor

@dataclass(frozen=True)
class Deposit:
    amount: float

@dataclass(frozen=True)
class Withdraw:
    amount: float

class BankAccount(TypedActor):
    def __init__(self):
        super().__init__()
        self.balance = 0.0
    
    @TypedActor.handler(Deposit)
    def handle_deposit(self, msg: Deposit):
        self.balance += msg.amount
    
    @TypedActor.handler(Withdraw)
    def handle_withdraw(self, msg: Withdraw):
        if self.balance >= msg.amount:
            self.balance -= msg.amount
```

### Props Configuration

```python
from abhikarta.actor import Props, PropsBuilder

# Simple props
props = Props(MyActor)

# Props with constructor arguments
props = Props(MyActor, args=("arg1",), kwargs={"key": "value"})

# Using builder pattern
props = (PropsBuilder(MyActor)
    .with_args("arg1")
    .with_pinned_dispatcher()  # Dedicated thread
    .with_bounded_mailbox(1000)  # Backpressure
    .build())
```

---

## Sending Messages

### Tell (Fire-and-Forget)

```python
# Basic tell
actor_ref.tell("message")

# Tell with sender (for replies)
actor_ref.tell("message", sender=self.self)

# Operator syntax
actor_ref << "message"
```

### Ask (Request-Response)

```python
from concurrent.futures import Future

# Send and get future
future = actor_ref.ask("get_status", timeout=5.0)

# Get result (blocks until ready)
result = future.result()

# Non-blocking check
if future.done():
    result = future.result()
```

### Forward (Preserve Sender)

```python
class RouterActor(Actor):
    def receive(self, message):
        # Forward to worker, keeping original sender
        self.worker.forward(message, self.context)
```

---

## Actor Lifecycle

### Lifecycle Hooks

```python
class MyActor(Actor):
    def pre_start(self):
        """Called before first message. Initialize resources."""
        self.connection = create_connection()
    
    def post_stop(self):
        """Called after actor stops. Cleanup resources."""
        self.connection.close()
    
    def pre_restart(self, reason, message):
        """Called before restart. Default: stops children."""
        super().pre_restart(reason, message)
    
    def post_restart(self, reason):
        """Called after restart. Default: calls pre_start."""
        super().post_restart(reason)
    
    def receive(self, message):
        # Handle messages
        pass
```

### Stopping Actors

```python
# From within actor
self.context.stop(self.self)

# Send poison pill (graceful)
actor_ref.tell(PoisonPill())

# Send kill (immediate)
actor_ref.tell(Kill())

# From parent
self.context.stop(child_ref)
```

---

## Supervision & Fault Tolerance

### Supervision Strategies

```python
from abhikarta.actor import OneForOneStrategy, AllForOneStrategy, Directive

# One-for-one: Only restart failed child
strategy = OneForOneStrategy(
    max_restarts=10,
    within_time=60.0,
    decider=lambda e: Directive.RESTART
)

# All-for-one: Restart all children on any failure
strategy = AllForOneStrategy(
    max_restarts=5,
    decider=lambda e: Directive.RESTART
)

# Apply to actor
props = Props(MyActor).with_supervisor(strategy)
```

### Directives

| Directive | Action |
|-----------|--------|
| `RESUME` | Continue processing, keep state |
| `RESTART` | Restart actor, clear state |
| `STOP` | Stop actor permanently |
| `ESCALATE` | Escalate to parent supervisor |

### Death Watch

```python
class ParentActor(Actor):
    def pre_start(self):
        self.child = self.context.actor_of(Props(ChildActor), "child")
        self.context.watch(self.child)  # Watch for termination
    
    def receive(self, message):
        if isinstance(message, Terminated):
            print(f"Child {message.actor} terminated!")
```

---

## Common Patterns

### Router (Load Balancing)

```python
from abhikarta.actor import RouterActor, RoundRobinLogic, Props

# Create router with 4 workers
router = system.actor_of(
    Props(RouterActor, args=(
        Props(WorkerActor),  # Worker props
        4,                    # Number of workers
        RoundRobinLogic()    # Routing strategy
    )),
    "router"
)

# Messages distributed to workers
for i in range(100):
    router.tell(WorkItem(i))
```

### Event Bus (Pub/Sub)

```python
from abhikarta.actor import EventBus

bus = EventBus()

# Subscribe to event type
bus.subscribe(my_actor, OrderEvent)

# Publish events
bus.publish(OrderEvent(order_id=123))  # All subscribers notified
```

### Circuit Breaker

```python
from abhikarta.actor import CircuitBreaker

breaker = CircuitBreaker(max_failures=5, reset_timeout=30.0)

if breaker.allow_request():
    try:
        result = call_external_service()
        breaker.record_success()
    except Exception:
        breaker.record_failure()
else:
    # Circuit is open, fail fast
    return fallback_response()
```

---

## Best Practices

### 1. Immutable Messages

```python
# ✅ Good: Immutable dataclass
@dataclass(frozen=True)
class OrderPlaced:
    order_id: str
    amount: float

# ❌ Bad: Mutable message
class OrderPlaced:
    def __init__(self, order_id):
        self.order_id = order_id  # Can be modified!
```

### 2. No Shared Mutable State

```python
# ✅ Good: Each actor has own state
class AccountActor(Actor):
    def __init__(self):
        self.balance = 0  # Private to this actor

# ❌ Bad: Shared state
shared_data = {}  # Multiple actors accessing this!
```

### 3. Tell, Don't Ask

```python
# ✅ Good: Fire-and-forget with callback
actor.tell(ProcessOrder(order, callback_actor))

# ⚠️ Use sparingly: Blocking ask
result = actor.ask(GetStatus()).result()  # Blocks!
```

### 4. Fail Fast & Let Supervisor Handle

```python
class WorkerActor(Actor):
    def receive(self, message):
        # ✅ Good: Let it crash, supervisor restarts
        result = process(message)  # May throw
        
        # ❌ Bad: Swallowing exceptions
        try:
            result = process(message)
        except Exception:
            pass  # Silent failure!
```

---

## Integration with Abhikarta

### AI Agent as Actor

```python
from abhikarta.actor import Actor, Props
from abhikarta.llm_provider import LLMFacade

class LLMAgentActor(Actor):
    def __init__(self, llm_facade: LLMFacade, model: str):
        super().__init__()
        self.llm = llm_facade
        self.model = model
    
    def receive(self, message):
        if isinstance(message, AgentQuery):
            # Call LLM
            response = self.llm.complete(
                model=self.model,
                prompt=message.question
            )
            if self.sender:
                self.sender.tell(AgentResponse(response))

# Create agent actor
agent = system.actor_of(
    Props(LLMAgentActor, args=(llm_facade, "gpt-4")),
    "llm-agent"
)
```

### Workflow Step as Actor

```python
class WorkflowStepActor(Actor):
    def __init__(self, step_config, next_step_ref):
        super().__init__()
        self.config = step_config
        self.next_step = next_step_ref
    
    def receive(self, message):
        if isinstance(message, StepInput):
            # Execute step logic
            result = self.execute_step(message.data)
            
            # Forward to next step
            if self.next_step:
                self.next_step.tell(StepInput(result), self.sender)
            elif self.sender:
                self.sender.tell(WorkflowComplete(result))
```

---

## Performance Tuning

### Dispatcher Selection

| Workload | Dispatcher | Config |
|----------|------------|--------|
| CPU-bound | Fork-Join | `with_fork_join_dispatcher()` |
| I/O-bound | Pinned | `with_pinned_dispatcher()` |
| Mixed | Default | (default) |
| Testing | CallingThread | `CallingThreadDispatcher()` |

### Mailbox Selection

| Scenario | Mailbox | Config |
|----------|---------|--------|
| General | Unbounded | (default) |
| Backpressure | Bounded | `with_bounded_mailbox(1000)` |
| Priority | Priority | `with_priority_mailbox()` |

---

## Acknowledgement

This actor system implementation is inspired by **Apache Pekko** (incubating), 
the open-source fork of Akka, licensed under the Apache License 2.0.

We gratefully acknowledge the Apache Software Foundation and the Pekko 
community for their pioneering work in actor-based concurrency.

- **Apache Pekko:** https://pekko.apache.org/
- **Pekko GitHub:** https://github.com/apache/pekko

---

*Copyright © 2025-2030, Abhikarta-LLM. All Rights Reserved.*
