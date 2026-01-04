"""
Messaging Base Classes - Abstract interfaces for pub/sub messaging.

Provides:
- MessageBroker: Abstract base for all message brokers
- Message: Standard message envelope
- Subscription: Topic subscription configuration
- Backpressure handling strategies

Version: 1.4.8
Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
import json
import uuid
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class BackpressureStrategy(Enum):
    """Strategy for handling backpressure."""
    DROP_OLDEST = "drop_oldest"      # Drop oldest messages when buffer full
    DROP_NEWEST = "drop_newest"      # Drop new messages when buffer full
    BLOCK = "block"                  # Block publisher until space available
    BUFFER_OVERFLOW = "overflow"     # Allow buffer to grow (memory risk)
    SAMPLE = "sample"                # Sample messages (1 in N)


class DeliveryGuarantee(Enum):
    """Message delivery guarantee level."""
    AT_MOST_ONCE = "at_most_once"    # Fire and forget
    AT_LEAST_ONCE = "at_least_once"  # May have duplicates
    EXACTLY_ONCE = "exactly_once"    # Transactional (if supported)


class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class BrokerConfig:
    """Configuration for a message broker."""
    broker_type: str                          # kafka, rabbitmq, activemq, memory
    hosts: List[str] = field(default_factory=lambda: ["localhost"])
    port: int = 9092
    username: Optional[str] = None
    password: Optional[str] = None
    
    # Connection settings
    connection_timeout: int = 30              # seconds
    retry_attempts: int = 3
    retry_delay: float = 1.0                  # seconds
    
    # Consumer settings
    consumer_group: str = "abhikarta-default"
    auto_commit: bool = True
    commit_interval: int = 5000               # ms
    max_poll_records: int = 500
    session_timeout: int = 30000              # ms
    
    # Producer settings
    acks: str = "all"                         # 0, 1, all
    batch_size: int = 16384
    linger_ms: int = 5
    compression: str = "gzip"                 # none, gzip, snappy, lz4
    
    # Backpressure
    backpressure_strategy: BackpressureStrategy = BackpressureStrategy.BLOCK
    buffer_size: int = 10000
    
    # Delivery
    delivery_guarantee: DeliveryGuarantee = DeliveryGuarantee.AT_LEAST_ONCE
    
    # Dead Letter Queue
    enable_dlq: bool = True
    dlq_suffix: str = ".dlq"
    max_retries: int = 3
    
    # SSL/TLS
    ssl_enabled: bool = False
    ssl_ca_location: Optional[str] = None
    ssl_cert_location: Optional[str] = None
    ssl_key_location: Optional[str] = None
    
    # Additional options
    extra_config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'broker_type': self.broker_type,
            'hosts': self.hosts,
            'port': self.port,
            'username': self.username,
            'consumer_group': self.consumer_group,
            'backpressure_strategy': self.backpressure_strategy.value,
            'delivery_guarantee': self.delivery_guarantee.value,
            'enable_dlq': self.enable_dlq,
            'ssl_enabled': self.ssl_enabled,
        }


@dataclass
class Message:
    """Standard message envelope for pub/sub communication."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    topic: str = ""
    payload: Any = None
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = ""                          # Sender identifier
    correlation_id: Optional[str] = None      # For request-response
    reply_to: Optional[str] = None            # Reply topic
    
    # Delivery
    priority: MessagePriority = MessagePriority.NORMAL
    ttl: Optional[int] = None                 # Time to live in seconds
    partition_key: Optional[str] = None       # For ordering
    
    # Tracking
    attempt: int = 1                          # Delivery attempt number
    original_timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'topic': self.topic,
            'payload': self.payload,
            'headers': self.headers,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'correlation_id': self.correlation_id,
            'reply_to': self.reply_to,
            'priority': self.priority.value,
            'ttl': self.ttl,
            'partition_key': self.partition_key,
            'attempt': self.attempt,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create from dictionary."""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            topic=data.get('topic', ''),
            payload=data.get('payload'),
            headers=data.get('headers', {}),
            timestamp=datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else datetime.utcnow(),
            source=data.get('source', ''),
            correlation_id=data.get('correlation_id'),
            reply_to=data.get('reply_to'),
            priority=MessagePriority(data.get('priority', 1)),
            ttl=data.get('ttl'),
            partition_key=data.get('partition_key'),
            attempt=data.get('attempt', 1),
        )
    
    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Deserialize from JSON."""
        return cls.from_dict(json.loads(json_str))


@dataclass
class PublishResult:
    """Result of a publish operation."""
    success: bool
    message_id: str
    topic: str
    partition: Optional[int] = None
    offset: Optional[int] = None
    timestamp: Optional[datetime] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'message_id': self.message_id,
            'topic': self.topic,
            'partition': self.partition,
            'offset': self.offset,
            'error': self.error,
        }


@dataclass
class ConsumeResult:
    """Result of a consume operation."""
    success: bool
    message: Optional[Message] = None
    error: Optional[str] = None
    should_retry: bool = False
    send_to_dlq: bool = False


@dataclass
class Subscription:
    """Topic subscription configuration."""
    topic_pattern: str                        # Topic or pattern (e.g., "task.*")
    handler: 'MessageHandler'
    group_id: Optional[str] = None
    
    # Processing
    max_concurrent: int = 10                  # Max concurrent message processing
    timeout: int = 30                         # Processing timeout in seconds
    
    # Retry
    retry_on_failure: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0                  # Base delay, exponential backoff
    
    # Filtering
    filter_headers: Dict[str, str] = field(default_factory=dict)
    filter_func: Optional[Callable[[Message], bool]] = None
    
    # State
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


# =============================================================================
# HANDLER INTERFACE
# =============================================================================

class MessageHandler(ABC):
    """Abstract base class for message handlers."""
    
    @abstractmethod
    async def handle(self, message: Message) -> ConsumeResult:
        """
        Handle a received message.
        
        Args:
            message: The message to handle
            
        Returns:
            ConsumeResult indicating success/failure and next steps
        """
        pass
    
    def on_error(self, message: Message, error: Exception) -> None:
        """Called when message handling fails."""
        logger.error(f"Error handling message {message.id}: {error}")
    
    def on_success(self, message: Message) -> None:
        """Called when message handling succeeds."""
        logger.debug(f"Successfully handled message {message.id}")


class FunctionHandler(MessageHandler):
    """Wrapper to create a handler from a function."""
    
    def __init__(self, func: Callable[[Message], Any]):
        self._func = func
        self._is_async = asyncio.iscoroutinefunction(func)
    
    async def handle(self, message: Message) -> ConsumeResult:
        try:
            if self._is_async:
                result = await self._func(message)
            else:
                result = self._func(message)
            
            return ConsumeResult(success=True, message=message)
        except Exception as e:
            logger.error(f"Handler error: {e}")
            return ConsumeResult(
                success=False,
                message=message,
                error=str(e),
                should_retry=True
            )


# =============================================================================
# ABSTRACT BROKER
# =============================================================================

class MessageBroker(ABC):
    """
    Abstract base class for message brokers.
    
    Provides a unified interface for pub/sub messaging across different
    broker implementations (Kafka, RabbitMQ, ActiveMQ, etc.)
    """
    
    def __init__(self, config: BrokerConfig):
        self.config = config
        self._connected = False
        self._subscriptions: Dict[str, Subscription] = {}
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._backpressure_count = 0
        self._metrics = {
            'messages_published': 0,
            'messages_consumed': 0,
            'messages_failed': 0,
            'messages_dlq': 0,
        }
    
    @property
    def is_connected(self) -> bool:
        """Check if broker is connected."""
        return self._connected
    
    @property
    def broker_type(self) -> str:
        """Get broker type."""
        return self.config.broker_type
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to the message broker.
        
        Returns:
            True if connected successfully
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the message broker."""
        pass
    
    @abstractmethod
    async def publish(self, message: Message) -> PublishResult:
        """
        Publish a message to a topic.
        
        Args:
            message: Message to publish
            
        Returns:
            PublishResult with success/failure info
        """
        pass
    
    @abstractmethod
    async def subscribe(self, subscription: Subscription) -> bool:
        """
        Subscribe to a topic with a handler.
        
        Args:
            subscription: Subscription configuration
            
        Returns:
            True if subscribed successfully
        """
        pass
    
    @abstractmethod
    async def unsubscribe(self, topic_pattern: str) -> bool:
        """
        Unsubscribe from a topic.
        
        Args:
            topic_pattern: Topic pattern to unsubscribe from
            
        Returns:
            True if unsubscribed successfully
        """
        pass
    
    @abstractmethod
    async def create_topic(self, topic: str, partitions: int = 1, 
                          replication: int = 1) -> bool:
        """
        Create a topic.
        
        Args:
            topic: Topic name
            partitions: Number of partitions
            replication: Replication factor
            
        Returns:
            True if created successfully
        """
        pass
    
    @abstractmethod
    async def delete_topic(self, topic: str) -> bool:
        """Delete a topic."""
        pass
    
    @abstractmethod
    async def list_topics(self) -> List[str]:
        """List all topics."""
        pass
    
    # =========================================================================
    # Convenience Methods
    # =========================================================================
    
    async def publish_json(self, topic: str, payload: Dict[str, Any],
                          headers: Dict[str, str] = None,
                          correlation_id: str = None) -> PublishResult:
        """Convenience method to publish JSON payload."""
        message = Message(
            topic=topic,
            payload=payload,
            headers=headers or {},
            correlation_id=correlation_id,
            source=f"abhikarta-{self.broker_type}"
        )
        return await self.publish(message)
    
    async def subscribe_handler(self, topic: str, 
                               handler: Callable[[Message], Any]) -> bool:
        """Convenience method to subscribe with a function handler."""
        subscription = Subscription(
            topic_pattern=topic,
            handler=FunctionHandler(handler)
        )
        return await self.subscribe(subscription)
    
    # =========================================================================
    # Backpressure Handling
    # =========================================================================
    
    def _check_backpressure(self) -> bool:
        """
        Check if backpressure should be applied.
        
        Returns:
            True if should apply backpressure
        """
        if self._backpressure_count >= self.config.buffer_size:
            strategy = self.config.backpressure_strategy
            
            if strategy == BackpressureStrategy.BLOCK:
                logger.warning("Backpressure: blocking publisher")
                return True
            elif strategy == BackpressureStrategy.DROP_NEWEST:
                logger.warning("Backpressure: dropping new message")
                return True
            elif strategy == BackpressureStrategy.DROP_OLDEST:
                logger.warning("Backpressure: would drop oldest")
                # Implementation specific
                return False
            elif strategy == BackpressureStrategy.SAMPLE:
                # Sample 1 in 10 messages
                return self._backpressure_count % 10 != 0
        
        return False
    
    # =========================================================================
    # Metrics
    # =========================================================================
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get broker metrics."""
        return {
            **self._metrics,
            'connected': self._connected,
            'subscriptions': len(self._subscriptions),
            'backpressure_count': self._backpressure_count,
        }
    
    def reset_metrics(self) -> None:
        """Reset metrics counters."""
        for key in self._metrics:
            self._metrics[key] = 0
    
    # =========================================================================
    # Context Manager
    # =========================================================================
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
