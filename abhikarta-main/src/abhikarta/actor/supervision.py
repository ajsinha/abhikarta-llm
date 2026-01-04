"""
Supervision Module - Fault tolerance and error handling strategies

This module provides supervision strategies that define how parent
actors handle failures in their children. This is the foundation
of fault-tolerant actor systems.

Supervision Strategies:
- OneForOneStrategy: Only restart the failed child
- AllForOneStrategy: Restart all children on any failure
- ExponentialBackoffStrategy: Restart with increasing delays

Acknowledgement:
This implementation is inspired by Apache Pekko (incubating).

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha - ajsinha@gmail.com

Version: 1.3.0
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type
from enum import Enum, auto
import time
import logging

logger = logging.getLogger(__name__)


class Directive(Enum):
    """
    Supervision directive - what to do with a failed actor.
    """
    RESUME = auto()    # Resume message processing, keep state
    RESTART = auto()   # Restart the actor, clear state
    STOP = auto()      # Stop the actor permanently
    ESCALATE = auto()  # Escalate to parent supervisor


@dataclass
class ChildFailure:
    """
    Information about a child actor failure.
    """
    child: 'ActorRef'
    cause: Exception
    message: Optional[Any] = None
    failure_count: int = 1


class SupervisorStrategy(ABC):
    """
    Abstract base class for supervision strategies.
    
    A supervision strategy defines how a supervisor (parent actor)
    handles failures in its children.
    """
    
    @abstractmethod
    def handle_failure(self, failure: ChildFailure) -> Directive:
        """
        Determine what to do with a failed child.
        
        Args:
            failure: Information about the failure
            
        Returns:
            Directive indicating action to take
        """
        pass
    
    @abstractmethod
    def reset(self, child: 'ActorRef') -> None:
        """
        Reset failure tracking for a child.
        
        Called when a child successfully processes messages.
        
        Args:
            child: The child actor
        """
        pass


@dataclass
class DeciderResult:
    """Result from a failure decider."""
    directive: Directive
    log_failure: bool = True


class OneForOneStrategy(SupervisorStrategy):
    """
    Supervise each child independently.
    
    When a child fails, only that child is affected by the
    directive. Other children continue running normally.
    
    This is the most common strategy and suitable for actors
    that are independent of each other.
    
    Args:
        max_restarts: Maximum restart attempts within time window
        within_time: Time window in seconds for restart counting
        decider: Function to decide action based on exception
    """
    
    def __init__(self,
                 max_restarts: int = 10,
                 within_time: float = 60.0,
                 decider: Optional[Callable[[Exception], Directive]] = None):
        self._max_restarts = max_restarts
        self._within_time = within_time
        self._decider = decider or self._default_decider
        self._failure_counts: Dict[str, List[float]] = {}
        self._lock = __import__('threading').Lock()
    
    def _default_decider(self, exception: Exception) -> Directive:
        """Default decision based on exception type."""
        if isinstance(exception, (ValueError, TypeError, AttributeError)):
            return Directive.RESUME
        elif isinstance(exception, RuntimeError):
            return Directive.RESTART
        else:
            return Directive.ESCALATE
    
    def handle_failure(self, failure: ChildFailure) -> Directive:
        """Handle child failure."""
        child_path = str(failure.child)
        current_time = time.time()
        
        with self._lock:
            # Get or create failure history
            if child_path not in self._failure_counts:
                self._failure_counts[child_path] = []
            
            # Add current failure
            self._failure_counts[child_path].append(current_time)
            
            # Remove old failures outside time window
            cutoff = current_time - self._within_time
            self._failure_counts[child_path] = [
                t for t in self._failure_counts[child_path] if t > cutoff
            ]
            
            recent_failures = len(self._failure_counts[child_path])
        
        # Get directive from decider
        directive = self._decider(failure.cause)
        
        # Check restart limit
        if directive == Directive.RESTART and recent_failures > self._max_restarts:
            logger.warning(
                f"Max restarts ({self._max_restarts}) exceeded for {child_path}, "
                f"stopping actor"
            )
            return Directive.STOP
        
        logger.info(
            f"Supervision decision for {child_path}: {directive.name} "
            f"(failures: {recent_failures}/{self._max_restarts})"
        )
        
        return directive
    
    def reset(self, child: 'ActorRef') -> None:
        """Reset failure count for child."""
        child_path = str(child)
        with self._lock:
            if child_path in self._failure_counts:
                del self._failure_counts[child_path]


class AllForOneStrategy(SupervisorStrategy):
    """
    Supervise all children as a group.
    
    When any child fails, all children are affected by the
    directive. This is useful when children depend on each
    other and must maintain consistent state.
    
    Args:
        max_restarts: Maximum restart attempts within time window
        within_time: Time window in seconds
        decider: Function to decide action based on exception
    """
    
    def __init__(self,
                 max_restarts: int = 10,
                 within_time: float = 60.0,
                 decider: Optional[Callable[[Exception], Directive]] = None):
        self._max_restarts = max_restarts
        self._within_time = within_time
        self._decider = decider or self._default_decider
        self._failure_times: List[float] = []
        self._lock = __import__('threading').Lock()
    
    def _default_decider(self, exception: Exception) -> Directive:
        """Default decision based on exception type."""
        if isinstance(exception, (ValueError, TypeError)):
            return Directive.RESTART
        else:
            return Directive.ESCALATE
    
    def handle_failure(self, failure: ChildFailure) -> Directive:
        """Handle child failure - affects all children."""
        current_time = time.time()
        
        with self._lock:
            # Add current failure
            self._failure_times.append(current_time)
            
            # Remove old failures
            cutoff = current_time - self._within_time
            self._failure_times = [t for t in self._failure_times if t > cutoff]
            
            recent_failures = len(self._failure_times)
        
        # Get directive from decider
        directive = self._decider(failure.cause)
        
        # Check restart limit
        if directive == Directive.RESTART and recent_failures > self._max_restarts:
            logger.warning(
                f"Max restarts ({self._max_restarts}) exceeded, stopping all children"
            )
            return Directive.STOP
        
        logger.info(
            f"AllForOne decision: {directive.name} "
            f"(failures: {recent_failures}/{self._max_restarts})"
        )
        
        return directive
    
    def reset(self, child: 'ActorRef') -> None:
        """Reset failure count (no-op for AllForOne)."""
        pass
    
    def reset_all(self) -> None:
        """Reset all failure counts."""
        with self._lock:
            self._failure_times = []


class ExponentialBackoffStrategy(SupervisorStrategy):
    """
    Restart with exponentially increasing delays.
    
    This strategy prevents rapid restart loops that can
    overwhelm the system. Each restart waits longer than
    the previous one.
    
    Args:
        min_backoff: Minimum backoff duration in seconds
        max_backoff: Maximum backoff duration in seconds
        random_factor: Random jitter factor (0-1)
        max_restarts: Maximum restart attempts
    """
    
    def __init__(self,
                 min_backoff: float = 0.1,
                 max_backoff: float = 30.0,
                 random_factor: float = 0.2,
                 max_restarts: int = 10):
        self._min_backoff = min_backoff
        self._max_backoff = max_backoff
        self._random_factor = random_factor
        self._max_restarts = max_restarts
        self._restart_counts: Dict[str, int] = {}
        self._last_restart: Dict[str, float] = {}
        self._lock = __import__('threading').Lock()
    
    def _calculate_backoff(self, restart_count: int) -> float:
        """Calculate backoff duration with jitter."""
        import random
        
        # Exponential backoff
        backoff = self._min_backoff * (2 ** restart_count)
        backoff = min(backoff, self._max_backoff)
        
        # Add random jitter
        jitter = backoff * self._random_factor * random.random()
        return backoff + jitter
    
    def handle_failure(self, failure: ChildFailure) -> Directive:
        """Handle failure with backoff delay."""
        child_path = str(failure.child)
        
        with self._lock:
            # Increment restart count
            self._restart_counts[child_path] = self._restart_counts.get(child_path, 0) + 1
            restart_count = self._restart_counts[child_path]
            
            # Check max restarts
            if restart_count > self._max_restarts:
                logger.warning(f"Max restarts exceeded for {child_path}, stopping")
                return Directive.STOP
            
            # Calculate and apply backoff
            backoff = self._calculate_backoff(restart_count)
            self._last_restart[child_path] = time.time()
        
        logger.info(
            f"Backoff restart for {child_path}: waiting {backoff:.2f}s "
            f"(attempt {restart_count}/{self._max_restarts})"
        )
        
        time.sleep(backoff)
        return Directive.RESTART
    
    def reset(self, child: 'ActorRef') -> None:
        """Reset backoff state for child."""
        child_path = str(child)
        with self._lock:
            if child_path in self._restart_counts:
                del self._restart_counts[child_path]
            if child_path in self._last_restart:
                del self._last_restart[child_path]
    
    def get_restart_count(self, child: 'ActorRef') -> int:
        """Get current restart count for child."""
        child_path = str(child)
        with self._lock:
            return self._restart_counts.get(child_path, 0)


class RestartWithLimitStrategy(SupervisorStrategy):
    """
    Restart with rate limiting.
    
    Limits the rate of restarts to prevent rapid cycling.
    
    Args:
        max_restarts_per_minute: Maximum restarts allowed per minute
        decider: Function to decide action based on exception
    """
    
    def __init__(self,
                 max_restarts_per_minute: int = 5,
                 decider: Optional[Callable[[Exception], Directive]] = None):
        self._max_per_minute = max_restarts_per_minute
        self._decider = decider or (lambda e: Directive.RESTART)
        self._restart_times: Dict[str, List[float]] = {}
        self._lock = __import__('threading').Lock()
    
    def handle_failure(self, failure: ChildFailure) -> Directive:
        """Handle failure with rate limiting."""
        child_path = str(failure.child)
        current_time = time.time()
        
        with self._lock:
            # Get or create restart history
            if child_path not in self._restart_times:
                self._restart_times[child_path] = []
            
            # Remove restarts older than 1 minute
            cutoff = current_time - 60.0
            self._restart_times[child_path] = [
                t for t in self._restart_times[child_path] if t > cutoff
            ]
            
            recent_restarts = len(self._restart_times[child_path])
            
            # Check rate limit
            if recent_restarts >= self._max_per_minute:
                logger.warning(
                    f"Restart rate limit ({self._max_per_minute}/min) exceeded "
                    f"for {child_path}"
                )
                return Directive.STOP
            
            # Record this restart
            self._restart_times[child_path].append(current_time)
        
        return self._decider(failure.cause)
    
    def reset(self, child: 'ActorRef') -> None:
        """Reset restart history for child."""
        child_path = str(child)
        with self._lock:
            if child_path in self._restart_times:
                del self._restart_times[child_path]


# ============================================
# DEFAULT STRATEGIES
# ============================================

class DefaultStrategy:
    """Factory for common supervision strategies."""
    
    @staticmethod
    def stoppingStrategy() -> SupervisorStrategy:
        """Strategy that stops failed actors."""
        return OneForOneStrategy(
            max_restarts=0,
            decider=lambda e: Directive.STOP
        )
    
    @staticmethod
    def restartingStrategy(max_restarts: int = 10) -> SupervisorStrategy:
        """Strategy that restarts failed actors."""
        return OneForOneStrategy(
            max_restarts=max_restarts,
            decider=lambda e: Directive.RESTART
        )
    
    @staticmethod
    def resumingStrategy() -> SupervisorStrategy:
        """Strategy that resumes failed actors."""
        return OneForOneStrategy(
            decider=lambda e: Directive.RESUME
        )
    
    @staticmethod
    def escalatingStrategy() -> SupervisorStrategy:
        """Strategy that escalates all failures."""
        return OneForOneStrategy(
            decider=lambda e: Directive.ESCALATE
        )
