"""
Swarm Event Bus - Internal messaging for swarm communication.

Provides a dedicated event bus for intra-swarm communication with:
- Topic-based pub/sub
- Priority queuing
- Event history and replay
- Metrics and monitoring

Version: 1.3.0
Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import asyncio
import fnmatch
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import uuid
import json

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Standard swarm event types."""
    # Control events
    SWARM_START = "control.swarm.start"
    SWARM_STOP = "control.swarm.stop"
    SWARM_PAUSE = "control.swarm.pause"
    SWARM_RESUME = "control.swarm.resume"
    
    # Task events
    TASK_CREATED = "task.created"
    TASK_ASSIGNED = "task.assigned"
    TASK_STARTED = "task.started"
    TASK_PROGRESS = "task.progress"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_CANCELLED = "task.cancelled"
    
    # Agent events
    AGENT_SPAWNED = "agent.spawned"
    AGENT_READY = "agent.ready"
    AGENT_BUSY = "agent.busy"
    AGENT_IDLE = "agent.idle"
    AGENT_STOPPED = "agent.stopped"
    AGENT_ERROR = "agent.error"
    
    # Result events
    RESULT_READY = "result.ready"
    RESULT_PARTIAL = "result.partial"
    RESULT_AGGREGATED = "result.aggregated"
    
    # Master events
    MASTER_DECISION = "master.decision"
    MASTER_BROADCAST = "master.broadcast"
    MASTER_DIRECT = "master.direct"
    
    # Custom
    CUSTOM = "custom"


class EventPriority(Enum):
    """Event priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class SwarmEvent:
    """Event message for swarm communication."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""                    # e.g., "task.search", "result.ready"
    source: str = ""                        # Source actor/agent ID
    target: Optional[str] = None            # Target actor/agent ID (None = broadcast)
    
    # Payload
    payload: Any = None
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Metadata
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None    # Links related events
    parent_id: Optional[str] = None         # Parent event ID
    
    # Tracking
    ttl: Optional[int] = None               # Time to live in seconds
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'source': self.source,
            'target': self.target,
            'payload': self.payload,
            'headers': self.headers,
            'priority': self.priority.value,
            'timestamp': self.timestamp.isoformat(),
            'correlation_id': self.correlation_id,
            'parent_id': self.parent_id,
            'ttl': self.ttl,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SwarmEvent':
        return cls(
            event_id=data.get('event_id', str(uuid.uuid4())),
            event_type=data.get('event_type', ''),
            source=data.get('source', ''),
            target=data.get('target'),
            payload=data.get('payload'),
            headers=data.get('headers', {}),
            priority=EventPriority(data.get('priority', 1)),
            timestamp=datetime.fromisoformat(data['timestamp']) if data.get('timestamp') else datetime.now(timezone.utc),
            correlation_id=data.get('correlation_id'),
            parent_id=data.get('parent_id'),
            ttl=data.get('ttl'),
            retry_count=data.get('retry_count', 0),
            max_retries=data.get('max_retries', 3),
        )
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SwarmEvent':
        return cls.from_dict(json.loads(json_str))
    
    @classmethod
    def create_task(cls, task_type: str, payload: Any, 
                   source: str, correlation_id: str = None) -> 'SwarmEvent':
        """Create a task event."""
        return cls(
            event_type=f"task.{task_type}",
            source=source,
            payload=payload,
            correlation_id=correlation_id or str(uuid.uuid4())
        )
    
    @classmethod
    def create_result(cls, result_type: str, payload: Any,
                     source: str, parent_event: 'SwarmEvent') -> 'SwarmEvent':
        """Create a result event in response to another event."""
        return cls(
            event_type=f"result.{result_type}",
            source=source,
            target=parent_event.source,
            payload=payload,
            correlation_id=parent_event.correlation_id,
            parent_id=parent_event.event_id
        )


class SwarmEventBus:
    """
    Internal event bus for swarm communication.
    
    Provides topic-based pub/sub with priority queuing and event history.
    
    Usage:
        bus = SwarmEventBus("swarm-1")
        await bus.start()
        
        # Subscribe
        await bus.subscribe("task.*", my_handler)
        
        # Publish
        event = SwarmEvent(event_type="task.search", payload={"query": "..."})
        await bus.publish(event)
    """
    
    def __init__(self, swarm_id: str, max_history: int = 10000):
        self.swarm_id = swarm_id
        self._max_history = max_history
        self._running = False
        
        # Subscribers: pattern -> list of (callback, priority)
        self._subscribers: Dict[str, List[tuple]] = {}
        
        # Event queue with priority
        self._queue: asyncio.PriorityQueue = None
        
        # Event history
        self._history: List[SwarmEvent] = []
        
        # Metrics
        self._metrics = {
            'events_published': 0,
            'events_delivered': 0,
            'events_failed': 0,
            'events_dropped': 0,
        }
        
        # Processing task
        self._processor_task = None
        self._lock = asyncio.Lock()
    
    async def start(self) -> None:
        """Start the event bus."""
        self._queue = asyncio.PriorityQueue()
        self._running = True
        self._processor_task = asyncio.create_task(self._process_events())
        logger.info(f"SwarmEventBus started for swarm {self.swarm_id}")
    
    async def stop(self) -> None:
        """Stop the event bus."""
        self._running = False
        
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        
        logger.info(f"SwarmEventBus stopped for swarm {self.swarm_id}")
    
    async def publish(self, event: SwarmEvent) -> bool:
        """
        Publish an event to the bus.
        
        Args:
            event: Event to publish
            
        Returns:
            True if published successfully
        """
        if not self._running:
            logger.warning("Event bus not running")
            return False
        
        # Add to queue with priority (negative for higher priority first)
        priority = -event.priority.value
        await self._queue.put((priority, event.timestamp.timestamp(), event))
        
        # Add to history
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history.pop(0)
        
        self._metrics['events_published'] += 1
        logger.debug(f"Published event: {event.event_type} from {event.source}")
        
        return True
    
    async def subscribe(self, pattern: str, callback: Callable[[SwarmEvent], Any],
                       priority: int = 0) -> str:
        """
        Subscribe to events matching a pattern.
        
        Args:
            pattern: Event type pattern (supports wildcards: *, #)
            callback: Async function to call with matching events
            priority: Subscriber priority (higher = called first)
            
        Returns:
            Subscription ID
        """
        subscription_id = str(uuid.uuid4())
        
        async with self._lock:
            if pattern not in self._subscribers:
                self._subscribers[pattern] = []
            
            self._subscribers[pattern].append((subscription_id, callback, priority))
            # Sort by priority (higher first)
            self._subscribers[pattern].sort(key=lambda x: -x[2])
        
        logger.debug(f"Subscribed to pattern: {pattern}")
        return subscription_id
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe by subscription ID."""
        async with self._lock:
            for pattern, subscribers in self._subscribers.items():
                self._subscribers[pattern] = [
                    s for s in subscribers if s[0] != subscription_id
                ]
        return True
    
    async def _process_events(self) -> None:
        """Process events from the queue."""
        while self._running:
            try:
                # Get next event (with timeout to allow shutdown)
                try:
                    _, _, event = await asyncio.wait_for(
                        self._queue.get(), 
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Check TTL
                if event.ttl:
                    age = (datetime.now(timezone.utc) - event.timestamp).total_seconds()
                    if age > event.ttl:
                        self._metrics['events_dropped'] += 1
                        logger.debug(f"Dropped expired event: {event.event_id}")
                        continue
                
                # Find matching subscribers
                delivered = 0
                for pattern, subscribers in self._subscribers.items():
                    if self._matches_pattern(event.event_type, pattern):
                        # Check target filter
                        if event.target:
                            # Direct message - only deliver to target
                            for sub_id, callback, _ in subscribers:
                                if event.target in sub_id:
                                    try:
                                        if asyncio.iscoroutinefunction(callback):
                                            await callback(event)
                                        else:
                                            callback(event)
                                        delivered += 1
                                    except Exception as e:
                                        logger.error(f"Subscriber error: {e}")
                                        self._metrics['events_failed'] += 1
                        else:
                            # Broadcast - deliver to all matching
                            for sub_id, callback, _ in subscribers:
                                try:
                                    if asyncio.iscoroutinefunction(callback):
                                        await callback(event)
                                    else:
                                        callback(event)
                                    delivered += 1
                                except Exception as e:
                                    logger.error(f"Subscriber error: {e}")
                                    self._metrics['events_failed'] += 1
                
                self._metrics['events_delivered'] += delivered
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Event processing error: {e}")
    
    def _matches_pattern(self, event_type: str, pattern: str) -> bool:
        """Check if event type matches subscription pattern."""
        if pattern == event_type:
            return True
        
        # Convert to fnmatch style
        fn_pattern = pattern.replace('.', '/').replace('*', '[^/]*').replace('#', '**')
        fn_event = event_type.replace('.', '/')
        
        return fnmatch.fnmatch(fn_event, fn_pattern)
    
    def get_history(self, event_type: str = None, 
                   limit: int = 100,
                   correlation_id: str = None) -> List[SwarmEvent]:
        """Get event history with optional filtering."""
        events = self._history
        
        if event_type:
            events = [e for e in events if self._matches_pattern(e.event_type, event_type)]
        
        if correlation_id:
            events = [e for e in events if e.correlation_id == correlation_id]
        
        return events[-limit:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get event bus metrics."""
        return {
            **self._metrics,
            'queue_size': self._queue.qsize() if self._queue else 0,
            'history_size': len(self._history),
            'subscriber_count': sum(len(s) for s in self._subscribers.values()),
        }
    
    def clear_history(self) -> None:
        """Clear event history."""
        self._history.clear()
