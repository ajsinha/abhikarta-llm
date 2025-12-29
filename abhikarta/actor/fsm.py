"""
FSM Actor Module - Finite State Machine actors

FSM actors provide structured state machine behavior with:
- Named states with data
- Transitions between states
- State timeouts
- Event handling per state

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha - ajsinha@gmail.com

Version: 1.3.0
"""

from abc import abstractmethod
from typing import Any, Optional, Dict, Callable, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum
import logging

from .actor import Actor

logger = logging.getLogger(__name__)


# FSM-specific messages
@dataclass(frozen=True)
class StateTimeout:
    """Sent when state timeout expires."""
    state_name: Any


@dataclass(frozen=True) 
class FSMState:
    """Current FSM state notification."""
    state_name: Any
    state_data: Any


S = TypeVar('S')  # State type
D = TypeVar('D')  # Data type


@dataclass
class State(Generic[S, D]):
    """
    FSM state with associated data.
    """
    state_name: S
    state_data: D
    timeout: Optional[float] = None  # State timeout in seconds
    
    def copy(self, **changes) -> 'State[S, D]':
        """Create a copy with optional changes."""
        return State(
            state_name=changes.get('state_name', self.state_name),
            state_data=changes.get('state_data', self.state_data),
            timeout=changes.get('timeout', self.timeout)
        )


class FSMActor(Actor, Generic[S, D]):
    """
    Finite State Machine actor.
    
    Provides structured state machine behavior. States are named
    and have associated data. State transitions are explicit and
    can trigger side effects.
    
    Example:
        class DoorFSM(FSMActor[str, dict]):
            def initial_state(self) -> State:
                return State("closed", {"locked": False})
            
            def when_closed(self, event, data):
                if event == "open":
                    return self.goto("open")
                elif event == "lock":
                    return self.stay().using({"locked": True})
            
            def when_open(self, event, data):
                if event == "close":
                    return self.goto("closed")
    
    State handlers are methods named `when_<state_name>`.
    """
    
    def __init__(self):
        super().__init__()
        self._current_state: Optional[State[S, D]] = None
        self._state_timeout_timer: Optional[str] = None
        self._next_state: Optional[State[S, D]] = None
        self._state_handlers: Dict[S, Callable] = {}
    
    @abstractmethod
    def initial_state(self) -> State[S, D]:
        """
        Define the initial state.
        
        Returns:
            Initial State with state_name and state_data
        """
        pass
    
    def pre_start(self) -> None:
        """Initialize FSM state."""
        super().pre_start()
        
        # Collect state handlers
        for attr_name in dir(self):
            if attr_name.startswith('when_'):
                state_name = attr_name[5:]  # Remove 'when_' prefix
                handler = getattr(self, attr_name)
                if callable(handler):
                    self._state_handlers[state_name] = handler
        
        # Set initial state
        initial = self.initial_state()
        self._transition_to(initial)
    
    def receive(self, message: Any) -> None:
        """Handle FSM events."""
        if isinstance(message, StateTimeout):
            self._handle_state_timeout()
        else:
            self._handle_event(message)
    
    def _handle_event(self, event: Any) -> None:
        """Handle an event in current state."""
        if self._current_state is None:
            logger.error("FSM not initialized")
            return
        
        state_name = self._current_state.state_name
        handler = self._state_handlers.get(state_name)
        
        if handler is None:
            # Try string conversion for enum states
            handler = self._state_handlers.get(str(state_name))
        
        if handler is None:
            self.unhandled(event)
            return
        
        # Call handler
        result = handler(event, self._current_state.state_data)
        
        # Process state transition
        if result is not None and isinstance(result, State):
            if result.state_name != self._current_state.state_name:
                self._transition_to(result)
            else:
                # Same state, just update data
                self._current_state = result
    
    def _handle_state_timeout(self) -> None:
        """Handle state timeout."""
        if self._current_state is None:
            return
        
        state_name = self._current_state.state_name
        handler = self._state_handlers.get(state_name)
        
        if handler:
            result = handler(StateTimeout(), self._current_state.state_data)
            if result is not None and isinstance(result, State):
                self._transition_to(result)
    
    def _transition_to(self, new_state: State[S, D]) -> None:
        """Transition to a new state."""
        old_state = self._current_state
        
        # Cancel existing timeout
        if self._state_timeout_timer:
            self.context.cancel_schedule(self._state_timeout_timer)
            self._state_timeout_timer = None
        
        # Transition callback
        self.on_transition(old_state, new_state)
        
        # Update state
        self._current_state = new_state
        
        # Set up new timeout
        if new_state.timeout and new_state.timeout > 0:
            self._state_timeout_timer = self.context.schedule_once(
                new_state.timeout,
                StateTimeout()
            )
        
        logger.debug(
            f"FSM transition: {old_state.state_name if old_state else 'None'} "
            f"-> {new_state.state_name}"
        )
    
    def on_transition(
        self,
        from_state: Optional[State[S, D]],
        to_state: State[S, D]
    ) -> None:
        """
        Called on state transition.
        
        Override for transition side effects.
        
        Args:
            from_state: Previous state (None if initial)
            to_state: New state
        """
        pass
    
    # DSL methods for state handlers
    
    def goto(self, state_name: S) -> State[S, D]:
        """
        Transition to a new state.
        
        Args:
            state_name: Target state name
            
        Returns:
            New State (data copied from current)
        """
        return State(
            state_name=state_name,
            state_data=self._current_state.state_data if self._current_state else None
        )
    
    def stay(self) -> State[S, D]:
        """
        Stay in current state.
        
        Returns:
            Current State (for chaining)
        """
        return self._current_state.copy() if self._current_state else State(None, None)
    
    def stop(self) -> None:
        """Stop the FSM actor."""
        self.context.self.stop()
    
    @property
    def state_name(self) -> Optional[S]:
        """Get current state name."""
        return self._current_state.state_name if self._current_state else None
    
    @property
    def state_data(self) -> Optional[D]:
        """Get current state data."""
        return self._current_state.state_data if self._current_state else None


# DSL helpers for fluent state definition

class StateBuilder(Generic[S, D]):
    """
    Builder for constructing states fluently.
    
    Example:
        return (self.goto("processing")
                    .using({"items": items})
                    .for_max(30.0))
    """
    
    def __init__(self, state_name: S, data: Optional[D] = None):
        self._state_name = state_name
        self._data = data
        self._timeout: Optional[float] = None
    
    def using(self, data: D) -> 'StateBuilder[S, D]':
        """Set state data."""
        self._data = data
        return self
    
    def for_max(self, timeout: float) -> 'StateBuilder[S, D]':
        """Set state timeout."""
        self._timeout = timeout
        return self
    
    def build(self) -> State[S, D]:
        """Build the State object."""
        return State(
            state_name=self._state_name,
            state_data=self._data,
            timeout=self._timeout
        )
    
    def __iter__(self):
        """Allow unpacking as State."""
        state = self.build()
        yield state


class FSMActorWithBuilder(FSMActor[S, D]):
    """
    FSM Actor with builder DSL methods.
    """
    
    def goto(self, state_name: S) -> StateBuilder[S, D]:
        """Create state builder for transition."""
        current_data = self._current_state.state_data if self._current_state else None
        return StateBuilder(state_name, current_data)
    
    def stay(self) -> StateBuilder[S, D]:
        """Create state builder for staying."""
        if self._current_state:
            return StateBuilder(
                self._current_state.state_name,
                self._current_state.state_data
            )
        return StateBuilder(None, None)


# Common FSM patterns

class StateMachine(Enum):
    """Example state machine states."""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class RetryFSM(FSMActor[str, dict]):
    """
    FSM with retry logic.
    
    Example of retry pattern with exponential backoff.
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0
    ):
        super().__init__()
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def initial_state(self) -> State[str, dict]:
        return State("idle", {"retries": 0, "task": None})
    
    def when_idle(self, event, data):
        if isinstance(event, dict) and "task" in event:
            return self.goto("processing").using({
                "retries": 0,
                "task": event["task"]
            })
    
    def when_processing(self, event, data):
        if event == "success":
            return self.goto("completed")
        elif event == "failure":
            retries = data.get("retries", 0) + 1
            if retries >= self.max_retries:
                return self.goto("failed")
            else:
                delay = min(
                    self.base_delay * (2 ** retries),
                    self.max_delay
                )
                return (self.goto("waiting")
                        .using({**data, "retries": retries})
                        .for_max(delay))
    
    def when_waiting(self, event, data):
        if isinstance(event, StateTimeout):
            return self.goto("processing")
    
    def when_completed(self, event, data):
        pass  # Terminal state
    
    def when_failed(self, event, data):
        pass  # Terminal state
