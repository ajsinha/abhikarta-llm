"""
ActiveMQ Message Broker - Apache ActiveMQ/STOMP implementation.

Provides integration with Apache ActiveMQ for enterprise messaging with:
- STOMP protocol support
- Durable subscriptions
- Message selectors
- Virtual topics

Version: 1.4.8
Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
import json

from .base import (
    MessageBroker,
    Message,
    Subscription,
    PublishResult,
    ConsumeResult,
    BrokerConfig
)

logger = logging.getLogger(__name__)


class ActiveMQBroker(MessageBroker):
    """
    Apache ActiveMQ message broker implementation using STOMP.
    
    Requires: stomp.py or aiostomp
    
    Usage:
        config = BrokerConfig(
            broker_type='activemq',
            hosts=['localhost'],
            port=61613,  # STOMP port
            username='admin',
            password='admin'
        )
        broker = ActiveMQBroker(config)
        await broker.connect()
    """
    
    def __init__(self, config: BrokerConfig):
        super().__init__(config)
        self._connection = None
        self._activemq_available = False
        
        # Check if library is available
        try:
            import stomp
            self._activemq_available = True
        except ImportError:
            logger.warning("stomp.py not installed. ActiveMQ broker will not be available.")
            logger.warning("Install with: pip install stomp.py")
    
    async def connect(self) -> bool:
        """Connect to ActiveMQ via STOMP."""
        if not self._activemq_available:
            logger.error("ActiveMQ library not available")
            return False
        
        try:
            import stomp
            
            host = self.config.hosts[0] if self.config.hosts else 'localhost'
            
            self._connection = stomp.Connection(
                [(host, self.config.port or 61613)]
            )
            
            # Create listener for messages
            self._connection.set_listener('', self._StompListener(self))
            
            self._connection.connect(
                self.config.username or 'admin',
                self.config.password or 'admin',
                wait=True
            )
            
            self._connected = True
            logger.info(f"Connected to ActiveMQ at {host}:{self.config.port or 61613}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to ActiveMQ: {e}")
            return False
    
    class _StompListener:
        """Internal STOMP listener for handling messages."""
        
        def __init__(self, broker: 'ActiveMQBroker'):
            self._broker = broker
        
        def on_message(self, frame):
            """Handle received message."""
            try:
                message = Message.from_json(frame.body)
                destination = frame.headers.get('destination', '')
                message.topic = destination.replace('/topic/', '').replace('/queue/', '')
                
                # Find matching subscription
                for pattern, sub in self._broker._subscriptions.items():
                    if self._matches(message.topic, pattern):
                        asyncio.create_task(sub.handler.handle(message))
                        break
                        
            except Exception as e:
                logger.error(f"Error processing ActiveMQ message: {e}")
        
        def _matches(self, topic: str, pattern: str) -> bool:
            if '*' not in pattern and '>' not in pattern:
                return topic == pattern
            # ActiveMQ uses * for single word, > for multiple
            import fnmatch
            return fnmatch.fnmatch(topic, pattern.replace('>', '*'))
        
        def on_error(self, frame):
            logger.error(f"ActiveMQ error: {frame.body}")
    
    async def disconnect(self) -> None:
        """Disconnect from ActiveMQ."""
        if self._connection:
            self._connection.disconnect()
        
        self._connected = False
        logger.info("Disconnected from ActiveMQ")
    
    async def publish(self, message: Message) -> PublishResult:
        """Publish a message to ActiveMQ."""
        if not self._connected or not self._connection:
            return PublishResult(
                success=False,
                message_id=message.id,
                topic=message.topic,
                error="Not connected to ActiveMQ"
            )
        
        try:
            destination = f"/topic/{message.topic}"
            
            self._connection.send(
                destination=destination,
                body=message.to_json(),
                headers={
                    'message-id': message.id,
                    'correlation-id': message.correlation_id or '',
                    **message.headers
                }
            )
            
            self._metrics['messages_published'] += 1
            
            return PublishResult(
                success=True,
                message_id=message.id,
                topic=message.topic,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to publish to ActiveMQ: {e}")
            return PublishResult(
                success=False,
                message_id=message.id,
                topic=message.topic,
                error=str(e)
            )
    
    async def subscribe(self, subscription: Subscription) -> bool:
        """Subscribe to ActiveMQ destination."""
        if not self._activemq_available or not self._connection:
            return False
        
        try:
            destination = f"/topic/{subscription.topic_pattern}"
            
            self._connection.subscribe(
                destination=destination,
                id=subscription.topic_pattern,
                ack='client-individual' if not self.config.auto_commit else 'auto'
            )
            
            self._subscriptions[subscription.topic_pattern] = subscription
            logger.info(f"Subscribed to ActiveMQ: {subscription.topic_pattern}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to subscribe to ActiveMQ: {e}")
            return False
    
    async def unsubscribe(self, topic_pattern: str) -> bool:
        """Unsubscribe from ActiveMQ destination."""
        if self._connection and topic_pattern in self._subscriptions:
            self._connection.unsubscribe(id=topic_pattern)
            del self._subscriptions[topic_pattern]
        return True
    
    async def create_topic(self, topic: str, partitions: int = 1,
                          replication: int = 1) -> bool:
        """Create topic (auto-created in ActiveMQ)."""
        return True
    
    async def delete_topic(self, topic: str) -> bool:
        """Delete topic (requires admin API)."""
        logger.warning("Topic deletion requires ActiveMQ admin console")
        return False
    
    async def list_topics(self) -> List[str]:
        """List topics (requires admin API)."""
        return list(self._subscriptions.keys())
