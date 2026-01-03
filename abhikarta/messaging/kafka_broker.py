"""
Kafka Message Broker - Apache Kafka implementation.

Provides integration with Apache Kafka for high-throughput,
distributed messaging with support for:
- Partitioned topics
- Consumer groups
- Exactly-once semantics
- Compression
- SSL/SASL authentication

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
    BrokerConfig,
    DeliveryGuarantee
)

logger = logging.getLogger(__name__)


class KafkaBroker(MessageBroker):
    """
    Apache Kafka message broker implementation.
    
    Requires: confluent-kafka or aiokafka
    
    Usage:
        config = BrokerConfig(
            broker_type='kafka',
            hosts=['localhost:9092'],
            consumer_group='my-group'
        )
        broker = KafkaBroker(config)
        await broker.connect()
    """
    
    def __init__(self, config: BrokerConfig):
        super().__init__(config)
        self._producer = None
        self._consumer = None
        self._admin_client = None
        self._consumer_task = None
        self._kafka_available = False
        
        # Check if kafka library is available
        try:
            from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
            from aiokafka.admin import AIOKafkaAdminClient
            self._kafka_available = True
        except ImportError:
            logger.warning("aiokafka not installed. Kafka broker will not be available.")
            logger.warning("Install with: pip install aiokafka")
    
    def _get_bootstrap_servers(self) -> str:
        """Get bootstrap servers string."""
        if len(self.config.hosts) == 1 and ':' not in self.config.hosts[0]:
            return f"{self.config.hosts[0]}:{self.config.port}"
        return ','.join(self.config.hosts)
    
    async def connect(self) -> bool:
        """Connect to Kafka cluster."""
        if not self._kafka_available:
            logger.error("Kafka library not available")
            return False
        
        try:
            from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
            
            bootstrap_servers = self._get_bootstrap_servers()
            
            # Producer configuration
            producer_config = {
                'bootstrap_servers': bootstrap_servers,
                'acks': 'all' if self.config.acks == 'all' else int(self.config.acks),
                'compression_type': self.config.compression if self.config.compression != 'none' else None,
                'linger_ms': self.config.linger_ms,
                'max_batch_size': self.config.batch_size,
            }
            
            # Add SSL config if enabled
            if self.config.ssl_enabled:
                producer_config.update({
                    'security_protocol': 'SSL',
                    'ssl_cafile': self.config.ssl_ca_location,
                    'ssl_certfile': self.config.ssl_cert_location,
                    'ssl_keyfile': self.config.ssl_key_location,
                })
            
            # Add SASL config if credentials provided
            if self.config.username and self.config.password:
                producer_config.update({
                    'security_protocol': 'SASL_SSL' if self.config.ssl_enabled else 'SASL_PLAINTEXT',
                    'sasl_mechanism': 'PLAIN',
                    'sasl_plain_username': self.config.username,
                    'sasl_plain_password': self.config.password,
                })
            
            self._producer = AIOKafkaProducer(
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                **producer_config
            )
            await self._producer.start()
            
            self._connected = True
            logger.info(f"Connected to Kafka at {bootstrap_servers}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Kafka."""
        if self._consumer_task:
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass
        
        if self._consumer:
            await self._consumer.stop()
            self._consumer = None
        
        if self._producer:
            await self._producer.stop()
            self._producer = None
        
        self._connected = False
        logger.info("Disconnected from Kafka")
    
    async def publish(self, message: Message) -> PublishResult:
        """Publish a message to Kafka topic."""
        if not self._connected or not self._producer:
            return PublishResult(
                success=False,
                message_id=message.id,
                topic=message.topic,
                error="Not connected to Kafka"
            )
        
        try:
            # Prepare message value
            value = message.to_dict()
            
            # Prepare headers
            headers = [(k, v.encode('utf-8')) for k, v in message.headers.items()]
            
            # Send message
            result = await self._producer.send_and_wait(
                topic=message.topic,
                value=value,
                key=message.partition_key.encode('utf-8') if message.partition_key else None,
                headers=headers
            )
            
            self._metrics['messages_published'] += 1
            
            return PublishResult(
                success=True,
                message_id=message.id,
                topic=message.topic,
                partition=result.partition,
                offset=result.offset,
                timestamp=datetime.fromtimestamp(result.timestamp / 1000) if result.timestamp else None
            )
            
        except Exception as e:
            logger.error(f"Failed to publish to Kafka: {e}")
            return PublishResult(
                success=False,
                message_id=message.id,
                topic=message.topic,
                error=str(e)
            )
    
    async def subscribe(self, subscription: Subscription) -> bool:
        """Subscribe to Kafka topic(s)."""
        if not self._kafka_available:
            return False
        
        try:
            from aiokafka import AIOKafkaConsumer
            
            bootstrap_servers = self._get_bootstrap_servers()
            
            # Consumer configuration
            consumer_config = {
                'bootstrap_servers': bootstrap_servers,
                'group_id': subscription.group_id or self.config.consumer_group,
                'auto_offset_reset': 'earliest',
                'enable_auto_commit': self.config.auto_commit,
                'max_poll_records': self.config.max_poll_records,
                'session_timeout_ms': self.config.session_timeout,
            }
            
            # Add security config
            if self.config.ssl_enabled:
                consumer_config.update({
                    'security_protocol': 'SSL',
                    'ssl_cafile': self.config.ssl_ca_location,
                })
            
            if self.config.username:
                consumer_config.update({
                    'security_protocol': 'SASL_SSL' if self.config.ssl_enabled else 'SASL_PLAINTEXT',
                    'sasl_mechanism': 'PLAIN',
                    'sasl_plain_username': self.config.username,
                    'sasl_plain_password': self.config.password,
                })
            
            # Create consumer
            self._consumer = AIOKafkaConsumer(
                subscription.topic_pattern,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                **consumer_config
            )
            await self._consumer.start()
            
            # Store subscription
            self._subscriptions[subscription.topic_pattern] = subscription
            
            # Start consumer loop
            self._consumer_task = asyncio.create_task(
                self._consume_loop(subscription)
            )
            
            logger.info(f"Subscribed to Kafka topic: {subscription.topic_pattern}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to subscribe to Kafka: {e}")
            return False
    
    async def _consume_loop(self, subscription: Subscription) -> None:
        """Consumer loop for processing messages."""
        try:
            async for record in self._consumer:
                try:
                    # Convert to Message
                    message = Message.from_dict(record.value)
                    message.topic = record.topic
                    
                    # Extract headers
                    if record.headers:
                        message.headers = {
                            k: v.decode('utf-8') for k, v in record.headers
                        }
                    
                    # Handle message
                    result = await subscription.handler.handle(message)
                    
                    if result.success:
                        self._metrics['messages_consumed'] += 1
                        if not self.config.auto_commit:
                            await self._consumer.commit()
                    else:
                        self._metrics['messages_failed'] += 1
                        if result.send_to_dlq:
                            await self._send_to_dlq(message)
                            
                except Exception as e:
                    logger.error(f"Error processing Kafka message: {e}")
                    self._metrics['messages_failed'] += 1
                    
        except asyncio.CancelledError:
            logger.info("Kafka consumer loop cancelled")
        except Exception as e:
            logger.error(f"Kafka consumer loop error: {e}")
    
    async def _send_to_dlq(self, message: Message) -> None:
        """Send failed message to dead letter queue."""
        dlq_topic = message.topic + self.config.dlq_suffix
        dlq_message = Message(
            topic=dlq_topic,
            payload=message.to_dict(),
            headers={
                **message.headers,
                'original_topic': message.topic,
                'error': 'processing_failed'
            }
        )
        await self.publish(dlq_message)
        self._metrics['messages_dlq'] += 1
    
    async def unsubscribe(self, topic_pattern: str) -> bool:
        """Unsubscribe from Kafka topic."""
        if topic_pattern in self._subscriptions:
            del self._subscriptions[topic_pattern]
        
        if self._consumer_task:
            self._consumer_task.cancel()
            self._consumer_task = None
        
        if self._consumer:
            await self._consumer.stop()
            self._consumer = None
        
        logger.info(f"Unsubscribed from Kafka topic: {topic_pattern}")
        return True
    
    async def create_topic(self, topic: str, partitions: int = 1,
                          replication: int = 1) -> bool:
        """Create a Kafka topic."""
        if not self._kafka_available:
            return False
        
        try:
            from aiokafka.admin import AIOKafkaAdminClient, NewTopic
            
            admin = AIOKafkaAdminClient(
                bootstrap_servers=self._get_bootstrap_servers()
            )
            await admin.start()
            
            new_topic = NewTopic(
                name=topic,
                num_partitions=partitions,
                replication_factor=replication
            )
            await admin.create_topics([new_topic])
            await admin.close()
            
            logger.info(f"Created Kafka topic: {topic}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Kafka topic: {e}")
            return False
    
    async def delete_topic(self, topic: str) -> bool:
        """Delete a Kafka topic."""
        if not self._kafka_available:
            return False
        
        try:
            from aiokafka.admin import AIOKafkaAdminClient
            
            admin = AIOKafkaAdminClient(
                bootstrap_servers=self._get_bootstrap_servers()
            )
            await admin.start()
            await admin.delete_topics([topic])
            await admin.close()
            
            logger.info(f"Deleted Kafka topic: {topic}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete Kafka topic: {e}")
            return False
    
    async def list_topics(self) -> List[str]:
        """List all Kafka topics."""
        if not self._kafka_available:
            return []
        
        try:
            from aiokafka.admin import AIOKafkaAdminClient
            
            admin = AIOKafkaAdminClient(
                bootstrap_servers=self._get_bootstrap_servers()
            )
            await admin.start()
            metadata = await admin.describe_cluster()
            topics = list(await admin.list_topics())
            await admin.close()
            
            return topics
            
        except Exception as e:
            logger.error(f"Failed to list Kafka topics: {e}")
            return []
