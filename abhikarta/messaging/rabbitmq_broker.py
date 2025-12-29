"""
RabbitMQ Message Broker - RabbitMQ/AMQP implementation.

Provides integration with RabbitMQ for reliable messaging with support for:
- Exchanges and queues
- Message acknowledgment
- Dead letter queues
- Priority queues

Version: 1.3.0
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


class RabbitMQBroker(MessageBroker):
    """
    RabbitMQ message broker implementation.
    
    Requires: aio-pika
    
    Usage:
        config = BrokerConfig(
            broker_type='rabbitmq',
            hosts=['localhost'],
            port=5672,
            username='guest',
            password='guest'
        )
        broker = RabbitMQBroker(config)
        await broker.connect()
    """
    
    def __init__(self, config: BrokerConfig):
        super().__init__(config)
        self._connection = None
        self._channel = None
        self._exchange = None
        self._rabbitmq_available = False
        
        # Check if library is available
        try:
            import aio_pika
            self._rabbitmq_available = True
        except ImportError:
            logger.warning("aio-pika not installed. RabbitMQ broker will not be available.")
            logger.warning("Install with: pip install aio-pika")
    
    async def connect(self) -> bool:
        """Connect to RabbitMQ."""
        if not self._rabbitmq_available:
            logger.error("RabbitMQ library not available")
            return False
        
        try:
            import aio_pika
            
            host = self.config.hosts[0] if self.config.hosts else 'localhost'
            url = f"amqp://{self.config.username or 'guest'}:{self.config.password or 'guest'}@{host}:{self.config.port}/"
            
            self._connection = await aio_pika.connect_robust(url)
            self._channel = await self._connection.channel()
            
            # Declare default exchange
            self._exchange = await self._channel.declare_exchange(
                'abhikarta',
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )
            
            self._connected = True
            logger.info(f"Connected to RabbitMQ at {host}:{self.config.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from RabbitMQ."""
        if self._channel:
            await self._channel.close()
        if self._connection:
            await self._connection.close()
        
        self._connected = False
        logger.info("Disconnected from RabbitMQ")
    
    async def publish(self, message: Message) -> PublishResult:
        """Publish a message to RabbitMQ."""
        if not self._connected or not self._exchange:
            return PublishResult(
                success=False,
                message_id=message.id,
                topic=message.topic,
                error="Not connected to RabbitMQ"
            )
        
        try:
            import aio_pika
            
            amqp_message = aio_pika.Message(
                body=message.to_json().encode(),
                message_id=message.id,
                correlation_id=message.correlation_id,
                headers=message.headers,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )
            
            await self._exchange.publish(
                amqp_message,
                routing_key=message.topic
            )
            
            self._metrics['messages_published'] += 1
            
            return PublishResult(
                success=True,
                message_id=message.id,
                topic=message.topic,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to publish to RabbitMQ: {e}")
            return PublishResult(
                success=False,
                message_id=message.id,
                topic=message.topic,
                error=str(e)
            )
    
    async def subscribe(self, subscription: Subscription) -> bool:
        """Subscribe to RabbitMQ queue."""
        if not self._rabbitmq_available or not self._channel:
            return False
        
        try:
            import aio_pika
            
            # Declare queue
            queue = await self._channel.declare_queue(
                f"{subscription.topic_pattern}.queue",
                durable=True
            )
            
            # Bind to exchange with routing key pattern
            await queue.bind(self._exchange, routing_key=subscription.topic_pattern)
            
            # Start consuming
            async def on_message(message: aio_pika.IncomingMessage):
                async with message.process():
                    try:
                        msg = Message.from_json(message.body.decode())
                        result = await subscription.handler.handle(msg)
                        
                        if result.success:
                            self._metrics['messages_consumed'] += 1
                        else:
                            self._metrics['messages_failed'] += 1
                            
                    except Exception as e:
                        logger.error(f"Error processing RabbitMQ message: {e}")
            
            await queue.consume(on_message)
            
            self._subscriptions[subscription.topic_pattern] = subscription
            logger.info(f"Subscribed to RabbitMQ: {subscription.topic_pattern}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to subscribe to RabbitMQ: {e}")
            return False
    
    async def unsubscribe(self, topic_pattern: str) -> bool:
        """Unsubscribe from RabbitMQ queue."""
        if topic_pattern in self._subscriptions:
            del self._subscriptions[topic_pattern]
        return True
    
    async def create_topic(self, topic: str, partitions: int = 1,
                          replication: int = 1) -> bool:
        """Create a RabbitMQ queue (topics are routing keys)."""
        # In RabbitMQ, topics are just routing keys; queues are created on subscribe
        return True
    
    async def delete_topic(self, topic: str) -> bool:
        """Delete a RabbitMQ queue."""
        try:
            if self._channel:
                await self._channel.queue_delete(f"{topic}.queue")
            return True
        except:
            return False
    
    async def list_topics(self) -> List[str]:
        """List topics (not directly supported in RabbitMQ)."""
        return list(self._subscriptions.keys())
