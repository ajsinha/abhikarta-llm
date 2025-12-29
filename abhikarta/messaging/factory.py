"""
Broker Factory - Dynamic broker creation and management.

Provides factory pattern for creating message brokers based on configuration,
with support for singleton instances and connection pooling.

Version: 1.3.0
Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import logging
from typing import Dict, Optional, Type

from .base import MessageBroker, BrokerConfig
from .kafka_broker import KafkaBroker
from .rabbitmq_broker import RabbitMQBroker
from .activemq_broker import ActiveMQBroker
from .memory_broker import InMemoryBroker

logger = logging.getLogger(__name__)


# Global broker registry for singleton instances
_broker_instances: Dict[str, MessageBroker] = {}


class BrokerFactory:
    """
    Factory for creating message broker instances.
    
    Usage:
        # Create from config
        broker = BrokerFactory.create(config)
        
        # Get or create singleton
        broker = BrokerFactory.get_or_create('main', config)
    """
    
    # Broker type to class mapping
    BROKER_TYPES: Dict[str, Type[MessageBroker]] = {
        'kafka': KafkaBroker,
        'rabbitmq': RabbitMQBroker,
        'activemq': ActiveMQBroker,
        'memory': InMemoryBroker,
        'inmemory': InMemoryBroker,
    }
    
    @classmethod
    def create(cls, config: BrokerConfig) -> MessageBroker:
        """
        Create a new broker instance.
        
        Args:
            config: Broker configuration
            
        Returns:
            MessageBroker instance
            
        Raises:
            ValueError: If broker type is not supported
        """
        broker_type = config.broker_type.lower()
        
        if broker_type not in cls.BROKER_TYPES:
            raise ValueError(
                f"Unsupported broker type: {broker_type}. "
                f"Supported types: {list(cls.BROKER_TYPES.keys())}"
            )
        
        broker_class = cls.BROKER_TYPES[broker_type]
        return broker_class(config)
    
    @classmethod
    def get_or_create(cls, name: str, config: BrokerConfig) -> MessageBroker:
        """
        Get existing broker or create new one.
        
        Args:
            name: Unique name for the broker instance
            config: Broker configuration (used only if creating new)
            
        Returns:
            MessageBroker instance
        """
        if name not in _broker_instances:
            _broker_instances[name] = cls.create(config)
            logger.info(f"Created broker instance: {name} ({config.broker_type})")
        
        return _broker_instances[name]
    
    @classmethod
    def get(cls, name: str) -> Optional[MessageBroker]:
        """
        Get existing broker instance by name.
        
        Args:
            name: Broker instance name
            
        Returns:
            MessageBroker instance or None if not found
        """
        return _broker_instances.get(name)
    
    @classmethod
    def remove(cls, name: str) -> bool:
        """
        Remove a broker instance.
        
        Args:
            name: Broker instance name
            
        Returns:
            True if removed, False if not found
        """
        if name in _broker_instances:
            del _broker_instances[name]
            logger.info(f"Removed broker instance: {name}")
            return True
        return False
    
    @classmethod
    def list_instances(cls) -> Dict[str, str]:
        """
        List all broker instances.
        
        Returns:
            Dict mapping name to broker type
        """
        return {
            name: broker.broker_type 
            for name, broker in _broker_instances.items()
        }
    
    @classmethod
    def register_type(cls, name: str, broker_class: Type[MessageBroker]) -> None:
        """
        Register a custom broker type.
        
        Args:
            name: Type name
            broker_class: Broker class
        """
        cls.BROKER_TYPES[name.lower()] = broker_class
        logger.info(f"Registered broker type: {name}")


# Convenience functions
def create_broker(config: BrokerConfig) -> MessageBroker:
    """Create a new broker instance."""
    return BrokerFactory.create(config)


def get_broker(name: str) -> Optional[MessageBroker]:
    """Get an existing broker instance."""
    return BrokerFactory.get(name)


def create_memory_broker() -> InMemoryBroker:
    """Create an in-memory broker for testing/development."""
    config = BrokerConfig(broker_type='memory')
    return InMemoryBroker(config)


def create_kafka_broker(hosts: list = None, **kwargs) -> KafkaBroker:
    """Create a Kafka broker with common defaults."""
    config = BrokerConfig(
        broker_type='kafka',
        hosts=hosts or ['localhost:9092'],
        **kwargs
    )
    return KafkaBroker(config)


def create_rabbitmq_broker(host: str = 'localhost', **kwargs) -> RabbitMQBroker:
    """Create a RabbitMQ broker with common defaults."""
    config = BrokerConfig(
        broker_type='rabbitmq',
        hosts=[host],
        port=kwargs.pop('port', 5672),
        username=kwargs.pop('username', 'guest'),
        password=kwargs.pop('password', 'guest'),
        **kwargs
    )
    return RabbitMQBroker(config)
