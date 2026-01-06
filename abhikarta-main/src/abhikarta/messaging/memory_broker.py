"""
In-Memory Message Broker - For testing and internal swarm communication.

Provides a lightweight, in-process message broker that's perfect for:
- Local development and testing
- Swarm internal event bus
- Single-node deployments
- Integration tests

Version: 1.4.8
Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import asyncio
import fnmatch
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Set
from queue import Queue, Empty
import threading

from .base import (
    MessageBroker,
    Message,
    MessageHandler,
    Subscription,
    PublishResult,
    ConsumeResult,
    BrokerConfig
)

logger = logging.getLogger(__name__)


@dataclass
class TopicInfo:
    """Information about an in-memory topic."""
    name: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    message_count: int = 0
    subscriber_count: int = 0


class InMemoryBroker(MessageBroker):
    """
    In-memory message broker for testing and internal communication.
    
    Features:
    - Topic-based pub/sub with wildcard support
    - Message history retention
    - Synchronous and async message delivery
    - No external dependencies
    
    Usage:
        config = BrokerConfig(broker_type='memory')
        broker = InMemoryBroker(config)
        await broker.connect()
        
        # Subscribe
        await broker.subscribe_handler('events.*', my_handler)
        
        # Publish
        await broker.publish_json('events.user', {'action': 'login'})
    """
    
    def __init__(self, config: BrokerConfig):
        super().__init__(config)
        self._topics: Dict[str, TopicInfo] = {}
        self._queues: Dict[str, asyncio.Queue] = defaultdict(lambda: asyncio.Queue())
        self._subscribers: Dict[str, List[Subscription]] = defaultdict(list)
        self._message_history: Dict[str, List[Message]] = defaultdict(list)
        self._history_limit = config.extra_config.get('history_limit', 1000)
        self._consumer_tasks: Dict[str, asyncio.Task] = {}
        self._running = False
        self._lock = asyncio.Lock()
    
    async def connect(self) -> bool:
        """Connect (initialize) the in-memory broker."""
        try:
            self._connected = True
            self._running = True
            logger.info("InMemoryBroker connected")
            return True
        except Exception as e:
            logger.error(f"Failed to connect InMemoryBroker: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect and clean up resources."""
        self._running = False
        
        # Cancel all consumer tasks
        for task in self._consumer_tasks.values():
            task.cancel()
        
        if self._consumer_tasks:
            await asyncio.gather(*self._consumer_tasks.values(), return_exceptions=True)
        
        self._consumer_tasks.clear()
        self._connected = False
        logger.info("InMemoryBroker disconnected")
    
    async def publish(self, message: Message) -> PublishResult:
        """Publish a message to a topic."""
        if not self._connected:
            return PublishResult(
                success=False,
                message_id=message.id,
                topic=message.topic,
                error="Broker not connected"
            )
        
        topic = message.topic
        
        # Ensure topic exists
        if topic not in self._topics:
            await self.create_topic(topic)
        
        # Update metrics
        self._topics[topic].message_count += 1
        self._metrics['messages_published'] += 1
        
        # Store in history
        self._message_history[topic].append(message)
        if len(self._message_history[topic]) > self._history_limit:
            self._message_history[topic].pop(0)
        
        # Deliver to matching subscribers
        delivered = 0
        async with self._lock:
            for pattern, subscriptions in self._subscribers.items():
                if self._matches_pattern(topic, pattern):
                    for sub in subscriptions:
                        if sub.is_active:
                            try:
                                # Check filter
                                if sub.filter_func and not sub.filter_func(message):
                                    continue
                                
                                # Check header filters
                                if sub.filter_headers:
                                    match = all(
                                        message.headers.get(k) == v 
                                        for k, v in sub.filter_headers.items()
                                    )
                                    if not match:
                                        continue
                                
                                # Deliver asynchronously
                                asyncio.create_task(
                                    self._deliver_message(message, sub)
                                )
                                delivered += 1
                            except Exception as e:
                                logger.error(f"Error delivering to subscriber: {e}")
        
        return PublishResult(
            success=True,
            message_id=message.id,
            topic=topic,
            partition=0,
            offset=self._topics[topic].message_count,
            timestamp=datetime.now(timezone.utc)
        )
    
    async def _deliver_message(self, message: Message, subscription: Subscription) -> None:
        """Deliver a message to a subscription handler."""
        try:
            result = await asyncio.wait_for(
                subscription.handler.handle(message),
                timeout=subscription.timeout
            )
            
            if result.success:
                self._metrics['messages_consumed'] += 1
                subscription.handler.on_success(message)
            else:
                self._metrics['messages_failed'] += 1
                
                # Retry logic
                if result.should_retry and subscription.retry_on_failure:
                    if message.attempt < subscription.max_retries:
                        message.attempt += 1
                        delay = subscription.retry_delay * (2 ** (message.attempt - 1))
                        await asyncio.sleep(delay)
                        await self._deliver_message(message, subscription)
                    elif result.send_to_dlq and self.config.enable_dlq:
                        await self._send_to_dlq(message)
                        
        except asyncio.TimeoutError:
            logger.error(f"Timeout delivering message {message.id}")
            self._metrics['messages_failed'] += 1
        except Exception as e:
            logger.error(f"Error delivering message: {e}")
            subscription.handler.on_error(message, e)
            self._metrics['messages_failed'] += 1
    
    async def _send_to_dlq(self, message: Message) -> None:
        """Send message to dead letter queue."""
        dlq_topic = message.topic + self.config.dlq_suffix
        dlq_message = Message(
            topic=dlq_topic,
            payload=message.to_dict(),
            headers={
                **message.headers,
                'original_topic': message.topic,
                'failure_reason': 'max_retries_exceeded'
            },
            source='dlq'
        )
        await self.publish(dlq_message)
        self._metrics['messages_dlq'] += 1
    
    def _matches_pattern(self, topic: str, pattern: str) -> bool:
        """Check if topic matches a subscription pattern."""
        # Support wildcards: * matches single level, # matches multiple
        if pattern == topic:
            return True
        
        # Convert pattern to fnmatch style
        fn_pattern = pattern.replace('.', '/').replace('*', '[^/]*').replace('#', '**')
        fn_topic = topic.replace('.', '/')
        
        return fnmatch.fnmatch(fn_topic, fn_pattern)
    
    async def subscribe(self, subscription: Subscription) -> bool:
        """Subscribe to a topic pattern."""
        try:
            async with self._lock:
                self._subscribers[subscription.topic_pattern].append(subscription)
                
                # Update subscriber count for exact topics
                if subscription.topic_pattern in self._topics:
                    self._topics[subscription.topic_pattern].subscriber_count += 1
            
            logger.info(f"Subscribed to pattern: {subscription.topic_pattern}")
            return True
        except Exception as e:
            logger.error(f"Failed to subscribe: {e}")
            return False
    
    async def unsubscribe(self, topic_pattern: str) -> bool:
        """Unsubscribe from a topic pattern."""
        try:
            async with self._lock:
                if topic_pattern in self._subscribers:
                    del self._subscribers[topic_pattern]
                    
                    if topic_pattern in self._topics:
                        self._topics[topic_pattern].subscriber_count -= 1
            
            logger.info(f"Unsubscribed from pattern: {topic_pattern}")
            return True
        except Exception as e:
            logger.error(f"Failed to unsubscribe: {e}")
            return False
    
    async def create_topic(self, topic: str, partitions: int = 1,
                          replication: int = 1) -> bool:
        """Create a topic."""
        if topic not in self._topics:
            self._topics[topic] = TopicInfo(name=topic)
            logger.debug(f"Created topic: {topic}")
        return True
    
    async def delete_topic(self, topic: str) -> bool:
        """Delete a topic."""
        if topic in self._topics:
            del self._topics[topic]
            if topic in self._message_history:
                del self._message_history[topic]
            logger.debug(f"Deleted topic: {topic}")
        return True
    
    async def list_topics(self) -> List[str]:
        """List all topics."""
        return list(self._topics.keys())
    
    # =========================================================================
    # Additional Methods for In-Memory Broker
    # =========================================================================
    
    def get_topic_info(self, topic: str) -> Optional[TopicInfo]:
        """Get information about a topic."""
        return self._topics.get(topic)
    
    def get_message_history(self, topic: str, limit: int = 100) -> List[Message]:
        """Get message history for a topic."""
        history = self._message_history.get(topic, [])
        return history[-limit:]
    
    def clear_history(self, topic: str = None) -> None:
        """Clear message history."""
        if topic:
            self._message_history[topic].clear()
        else:
            self._message_history.clear()
    
    def get_subscriber_count(self, topic_pattern: str = None) -> int:
        """Get subscriber count."""
        if topic_pattern:
            return len(self._subscribers.get(topic_pattern, []))
        return sum(len(subs) for subs in self._subscribers.values())
    
    async def replay_messages(self, topic: str, from_offset: int = 0,
                             handler: MessageHandler = None) -> int:
        """Replay historical messages."""
        messages = self._message_history.get(topic, [])
        replayed = 0
        
        for msg in messages[from_offset:]:
            if handler:
                await handler.handle(msg)
            replayed += 1
        
        return replayed
