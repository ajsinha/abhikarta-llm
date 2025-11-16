"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


from typing import Dict, Any, Callable
import json
import asyncio

class KafkaConsumerAdapter:
    """Adapter for Kafka event consumption"""
    
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.consumers = {}
    
    async def subscribe(
        self,
        topic: str,
        group_id: str,
        handler: Callable,
        **config
    ):
        """Subscribe to Kafka topic"""
        # Note: Requires kafka-python library
        try:
            from kafka import KafkaConsumer
            
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                **config
            )
            
            self.consumers[topic] = consumer
            
            # Start consumption loop
            asyncio.create_task(self._consume_loop(consumer, handler))
            
        except ImportError:
            print("kafka-python not installed. Install with: pip install kafka-python")
    
    async def _consume_loop(self, consumer, handler):
        """Async consumption loop"""
        while True:
            messages = consumer.poll(timeout_ms=1000)
            for topic_partition, records in messages.items():
                for record in records:
                    try:
                        await handler(record.value)
                    except Exception as e:
                        print(f"Error handling message: {e}")
            
            await asyncio.sleep(0.1)
    
    def close(self):
        """Close all consumers"""
        for consumer in self.consumers.values():
            consumer.close()
