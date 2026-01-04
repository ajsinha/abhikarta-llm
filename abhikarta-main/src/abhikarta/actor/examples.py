"""
Actor Examples Module - Comprehensive examples for the Abhikarta Actor System

This module provides working examples demonstrating various actor patterns
and use cases for building scalable, concurrent applications.

Examples included:
1. Basic Actor - Simple message handling
2. Counter Actor - Stateful actor
3. Bank Account - Typed actor with domain messages
4. Worker Pool - Router pattern for load distribution
5. Chat Room - Event-driven pub/sub
6. Ping Pong - Actor communication
7. Pipeline - Sequential processing
8. Supervisor - Fault tolerance patterns
9. Agent Actor - AI agent as actor
10. Workflow Actor - Workflow execution as actor

Acknowledgement:
This implementation is inspired by Apache Pekko (incubating).

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha - ajsinha@gmail.com

Version: 1.3.0
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import time
import random
import logging

from .actor import Actor, TypedActor, ActorRef, PoisonPill, Terminated
from .props import Props, PropsBuilder
from .system import ActorSystem, create_actor_system
from .patterns import (
    RouterActor, RoundRobinLogic, EventBus, StashingActor
)
from .supervision import OneForOneStrategy, Directive

logger = logging.getLogger(__name__)


# ============================================
# EXAMPLE 1: BASIC ACTOR
# ============================================

class GreeterActor(Actor):
    """
    Simple actor that greets people.
    
    Demonstrates:
    - Basic message handling
    - Replying to sender
    - Actor lifecycle hooks
    
    Usage:
        greeter = system.actor_of(Props(GreeterActor), "greeter")
        greeter.tell("Alice")  # Prints: Hello, Alice!
    """
    
    def __init__(self):
        super().__init__()
        self.greeting_count = 0
    
    def pre_start(self) -> None:
        logger.info(f"GreeterActor starting at {self.self.path}")
    
    def post_stop(self) -> None:
        logger.info(f"GreeterActor stopped. Total greetings: {self.greeting_count}")
    
    def receive(self, message: Any) -> None:
        if isinstance(message, str):
            self.greeting_count += 1
            print(f"Hello, {message}! (Greeting #{self.greeting_count})")
            
            if self.sender:
                self.sender.tell(f"Greeted {message}")
        else:
            self.unhandled(message)


# ============================================
# EXAMPLE 2: COUNTER ACTOR (STATEFUL)
# ============================================

@dataclass(frozen=True)
class Increment:
    """Increment counter by amount."""
    amount: int = 1


@dataclass(frozen=True)
class Decrement:
    """Decrement counter by amount."""
    amount: int = 1


@dataclass(frozen=True)
class GetCount:
    """Request current count."""
    pass


@dataclass(frozen=True)
class CountResult:
    """Response with current count."""
    count: int


class CounterActor(Actor):
    """
    Stateful counter actor.
    
    Demonstrates:
    - Private mutable state
    - Multiple message types
    - Request-response pattern
    
    Usage:
        counter = system.actor_of(Props(CounterActor), "counter")
        counter.tell(Increment(5))
        future = counter.ask(GetCount())
        result = future.result()  # CountResult(count=5)
    """
    
    def __init__(self, initial_value: int = 0):
        super().__init__()
        self._count = initial_value
    
    def receive(self, message: Any) -> None:
        if isinstance(message, Increment):
            self._count += message.amount
        elif isinstance(message, Decrement):
            self._count -= message.amount
        elif isinstance(message, GetCount):
            if self.sender:
                self.sender.tell(CountResult(self._count))
        else:
            self.unhandled(message)


# ============================================
# EXAMPLE 3: BANK ACCOUNT (TYPED ACTOR)
# ============================================

@dataclass(frozen=True)
class Deposit:
    """Deposit money into account."""
    amount: float


@dataclass(frozen=True)
class Withdraw:
    """Withdraw money from account."""
    amount: float


@dataclass(frozen=True)
class GetBalance:
    """Request current balance."""
    pass


@dataclass(frozen=True)
class BalanceResult:
    """Response with balance."""
    balance: float
    success: bool = True


@dataclass(frozen=True)
class TransactionResult:
    """Result of a transaction."""
    success: bool
    new_balance: float
    message: str = ""


class BankAccountActor(TypedActor):
    """
    Bank account using TypedActor for type-safe message handling.
    
    Usage:
        account = system.actor_of(
            Props(BankAccountActor, args=("ACC001", 1000.0)),
            "account-001"
        )
        account.tell(Deposit(500.0))
    """
    
    def __init__(self, account_id: str, initial_balance: float = 0.0):
        super().__init__()
        self.account_id = account_id
        self._balance = initial_balance
    
    @TypedActor.handler(Deposit)
    def handle_deposit(self, msg: Deposit) -> None:
        if msg.amount > 0:
            self._balance += msg.amount
            if self.sender:
                self.sender.tell(TransactionResult(True, self._balance))
    
    @TypedActor.handler(Withdraw)
    def handle_withdraw(self, msg: Withdraw) -> None:
        if msg.amount <= self._balance:
            self._balance -= msg.amount
            if self.sender:
                self.sender.tell(TransactionResult(True, self._balance))
        elif self.sender:
            self.sender.tell(TransactionResult(False, self._balance, "Insufficient funds"))
    
    @TypedActor.handler(GetBalance)
    def handle_get_balance(self, msg: GetBalance) -> None:
        if self.sender:
            self.sender.tell(BalanceResult(self._balance))


# ============================================
# EXAMPLE 4: WORKER POOL (ROUTER)
# ============================================

@dataclass(frozen=True)
class WorkItem:
    """A unit of work."""
    item_id: str
    data: Any


@dataclass(frozen=True)
class WorkResult:
    """Result of processing."""
    item_id: str
    result: Any
    worker_id: str


class WorkerActor(Actor):
    """Worker that processes work items."""
    
    def __init__(self):
        super().__init__()
        self.processed_count = 0
    
    def receive(self, message: Any) -> None:
        if isinstance(message, WorkItem):
            self.processed_count += 1
            result = f"Processed: {message.data}"
            if self.sender:
                self.sender.tell(WorkResult(message.item_id, result, self.self.name))


def create_worker_pool(system: ActorSystem, pool_size: int = 4) -> ActorRef:
    """Create a worker pool with round-robin routing."""
    return system.actor_of(
        Props(RouterActor, args=(
            Props(WorkerActor),
            pool_size,
            RoundRobinLogic()
        )),
        "worker-pool"
    )


# ============================================
# EXAMPLE 5: PING PONG
# ============================================

@dataclass(frozen=True)
class Ping:
    count: int


@dataclass(frozen=True)
class Pong:
    count: int


class PingActor(Actor):
    """Actor that sends pings."""
    
    def __init__(self, max_pings: int = 10):
        super().__init__()
        self._max_pings = max_pings
    
    def receive(self, message: Any) -> None:
        if isinstance(message, ActorRef):
            message.tell(Ping(1), self.self)
            print(f"Ping: 1")
        elif isinstance(message, Pong):
            if message.count < self._max_pings:
                next_count = message.count + 1
                print(f"Ping: {next_count}")
                self.sender.tell(Ping(next_count), self.self)
            else:
                print(f"Complete! Total: {message.count}")


class PongActor(Actor):
    """Actor that responds with pongs."""
    
    def receive(self, message: Any) -> None:
        if isinstance(message, Ping):
            print(f"Pong: {message.count}")
            if self.sender:
                self.sender.tell(Pong(message.count), self.self)


# ============================================
# EXAMPLE 6: AI AGENT ACTOR
# ============================================

@dataclass(frozen=True)
class AgentQuery:
    """Query for the AI agent."""
    query_id: str
    question: str


@dataclass(frozen=True)
class AgentResponse:
    """Response from AI agent."""
    query_id: str
    answer: str
    confidence: float


class AIAgentActor(StashingActor):
    """
    AI Agent as an actor - integration point for LLM processing.
    
    Demonstrates stashing for handling concurrent queries.
    """
    
    def __init__(self, agent_name: str):
        super().__init__()
        self.agent_name = agent_name
        self._processing = False
        self._current_query = None
    
    def receive(self, message: Any) -> None:
        if isinstance(message, AgentQuery):
            if self._processing:
                self.stash((self.sender, message))
            else:
                self._process_query(message)
        elif isinstance(message, str) and message == "complete":
            self._complete_processing()
    
    def _process_query(self, query: AgentQuery) -> None:
        self._processing = True
        self._current_query = query
        # Simulate async LLM call
        self.context.schedule_once(0.1, self.self, "complete")
    
    def _complete_processing(self) -> None:
        response = AgentResponse(
            self._current_query.query_id,
            f"Answer to: {self._current_query.question}",
            random.uniform(0.8, 0.99)
        )
        if self.sender:
            self.sender.tell(response)
        self._processing = False
        self._current_query = None
        self.unstash()


# ============================================
# EXAMPLE RUNNER
# ============================================

def run_all_examples():
    """Run all actor examples."""
    print("\n=== Greeter Example ===")
    with create_actor_system("example") as system:
        greeter = system.actor_of(Props(GreeterActor), "greeter")
        greeter.tell("World")
        time.sleep(0.1)
    
    print("\n=== Counter Example ===")
    with create_actor_system("example") as system:
        counter = system.actor_of(Props(CounterActor, args=(0,)), "counter")
        counter.tell(Increment(5))
        counter.tell(Increment(3))
        counter.tell(Decrement(2))
        future = counter.ask(GetCount())
        print(f"Count: {future.result(timeout=2.0).count}")
    
    print("\n=== Ping-Pong Example ===")
    with create_actor_system("example") as system:
        pong = system.actor_of(Props(PongActor), "pong")
        ping = system.actor_of(Props(PingActor, args=(5,)), "ping")
        ping.tell(pong)
        time.sleep(0.5)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_all_examples()
