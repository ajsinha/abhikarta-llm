"""
Abhikarta Messaging Module - Unified Pub/Sub Interface.

This module provides a consistent interface for message-based communication
across different message brokers (Kafka, RabbitMQ, ActiveMQ) with:
- Abstract pub/sub interface
- Backpressure handling
- Configuration-driven broker selection
- Message serialization/deserialization
- Dead letter queue support
- Retry mechanisms

Version: 1.4.8
Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

from .base import (
    MessageBroker,
    Message,
    MessageHandler,
    Subscription,
    PublishResult,
    ConsumeResult,
    BrokerConfig,
    BackpressureStrategy,
    DeliveryGuarantee
)

from .kafka_broker import KafkaBroker
from .rabbitmq_broker import RabbitMQBroker
from .activemq_broker import ActiveMQBroker
from .memory_broker import InMemoryBroker

from .factory import (
    create_broker,
    get_broker,
    BrokerFactory
)

__all__ = [
    # Base classes
    'MessageBroker',
    'Message',
    'MessageHandler',
    'Subscription',
    'PublishResult',
    'ConsumeResult',
    'BrokerConfig',
    'BackpressureStrategy',
    'DeliveryGuarantee',
    
    # Implementations
    'KafkaBroker',
    'RabbitMQBroker',
    'ActiveMQBroker',
    'InMemoryBroker',
    
    # Factory
    'create_broker',
    'get_broker',
    'BrokerFactory',
]

__version__ = '1.4.8'
