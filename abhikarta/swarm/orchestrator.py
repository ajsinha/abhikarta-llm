"""
Swarm Orchestrator - Lifecycle management for agent swarms.

The orchestrator manages the complete lifecycle of swarms:
- Creating and initializing swarms from definitions
- Starting/stopping swarms
- Managing external triggers
- Monitoring swarm health
- Persisting swarm state

Version: 1.3.0
Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import uuid

from .swarm_definition import (
    SwarmDefinition, SwarmConfig, SwarmStatus, 
    AgentMembership, TriggerConfig, TriggerType
)
from .event_bus import SwarmEventBus, SwarmEvent, EventType
from .master_actor import MasterActor, MasterActorConfig
from .swarm_agent import SwarmAgent, SwarmAgentPool, SwarmAgentConfig

logger = logging.getLogger(__name__)


# Global orchestrator instance
_orchestrator: Optional['SwarmOrchestrator'] = None


@dataclass
class SwarmInstance:
    """Running instance of a swarm."""
    definition: SwarmDefinition
    event_bus: SwarmEventBus
    master_actor: MasterActor
    agent_pools: Dict[str, SwarmAgentPool]
    trigger_tasks: Dict[str, asyncio.Task]
    
    started_at: datetime = None
    stopped_at: datetime = None
    
    @property
    def is_running(self) -> bool:
        return self.definition.status == SwarmStatus.ACTIVE


class SwarmOrchestrator:
    """
    Swarm Orchestrator - Central manager for all swarms.
    
    Handles:
    - Swarm lifecycle (create, start, stop, delete)
    - External trigger management
    - Health monitoring
    - Resource management
    
    Usage:
        orchestrator = SwarmOrchestrator(db_facade)
        
        # Start a swarm
        await orchestrator.start_swarm("swarm-1")
        
        # Handle user query
        result = await orchestrator.handle_user_query("swarm-1", "What is...")
        
        # Stop swarm
        await orchestrator.stop_swarm("swarm-1")
    """
    
    def __init__(self, db_facade=None, agent_registry: Dict[str, Any] = None):
        self.db_facade = db_facade
        self.agent_registry = agent_registry or {}
        
        self._swarms: Dict[str, SwarmInstance] = {}
        self._definitions: Dict[str, SwarmDefinition] = {}
        self._lock = asyncio.Lock()
        
        # External broker connections
        self._external_brokers: Dict[str, Any] = {}
        
        # Metrics
        self._metrics = {
            'swarms_started': 0,
            'swarms_stopped': 0,
            'total_executions': 0,
            'active_swarms': 0,
        }
    
    async def initialize(self) -> None:
        """Initialize the orchestrator."""
        # Load swarm definitions from database
        if self.db_facade:
            await self._load_definitions_from_db()
        
        logger.info("SwarmOrchestrator initialized")
    
    async def _load_definitions_from_db(self) -> None:
        """Load swarm definitions from database."""
        try:
            swarms = self.db_facade.fetch_all(
                "SELECT * FROM swarms WHERE status != 'deleted'"
            ) or []
            
            for row in swarms:
                definition = SwarmDefinition.from_json(row.get('definition_json', '{}'))
                definition.swarm_id = row['swarm_id']
                definition.name = row['name']
                definition.status = SwarmStatus(row.get('status', 'inactive'))
                self._definitions[definition.swarm_id] = definition
                
            logger.info(f"Loaded {len(self._definitions)} swarm definitions")
            
        except Exception as e:
            logger.error(f"Error loading swarm definitions: {e}")
    
    # =========================================================================
    # Swarm Lifecycle
    # =========================================================================
    
    async def create_swarm(self, definition: SwarmDefinition) -> str:
        """
        Create a new swarm from definition.
        
        Args:
            definition: Swarm definition
            
        Returns:
            Swarm ID
        """
        async with self._lock:
            # Generate ID if needed
            if not definition.swarm_id:
                definition.swarm_id = str(uuid.uuid4())
            
            definition.status = SwarmStatus.INACTIVE
            definition.created_at = datetime.utcnow()
            
            # Persist to database
            if self.db_facade:
                await self._save_definition(definition)
            
            # Store in memory
            self._definitions[definition.swarm_id] = definition
            
            logger.info(f"Created swarm: {definition.name} ({definition.swarm_id})")
            return definition.swarm_id
    
    async def start_swarm(self, swarm_id: str) -> bool:
        """
        Start a swarm.
        
        Args:
            swarm_id: Swarm to start
            
        Returns:
            True if started successfully
        """
        async with self._lock:
            definition = self._definitions.get(swarm_id)
            if not definition:
                logger.error(f"Swarm not found: {swarm_id}")
                return False
            
            if swarm_id in self._swarms:
                logger.warning(f"Swarm already running: {swarm_id}")
                return True
            
            try:
                definition.status = SwarmStatus.STARTING
                
                # Create event bus
                event_bus = SwarmEventBus(swarm_id)
                await event_bus.start()
                
                # Create master actor
                master_config = MasterActorConfig(
                    llm_provider=definition.config.llm_provider,
                    llm_model=definition.config.llm_model,
                    temperature=definition.config.llm_temperature,
                    max_tokens=definition.config.llm_max_tokens,
                    system_prompt=definition.config.master_system_prompt,
                    decision_prompt=definition.config.master_decision_prompt,
                    decision_timeout=definition.config.master_timeout,
                    aggregation_timeout=definition.config.swarm_timeout,
                    max_iterations=definition.config.max_iterations,
                )
                
                # Build agent registry for master
                agent_info = {}
                for membership in definition.agents:
                    agent_info[membership.agent_id] = {
                        'name': membership.agent_name,
                        'description': membership.description,
                        'role': membership.role,
                        'capabilities': [s.event_pattern for s in membership.subscriptions]
                    }
                
                master_actor = MasterActor(
                    swarm_id=swarm_id,
                    event_bus=event_bus,
                    config=master_config,
                    agent_registry=agent_info
                )
                await master_actor.start()
                
                # Create agent pools
                agent_pools = {}
                for membership in definition.agents:
                    if membership.is_active:
                        pool = SwarmAgentPool(
                            membership=membership,
                            event_bus=event_bus,
                            agent_executor=self._get_agent_executor(membership.agent_id)
                        )
                        await pool.start()
                        agent_pools[membership.agent_id] = pool
                
                # Start external triggers
                trigger_tasks = {}
                for trigger in definition.triggers:
                    if trigger.is_active:
                        task = await self._start_trigger(trigger, swarm_id)
                        if task:
                            trigger_tasks[trigger.trigger_id] = task
                
                # Create instance
                instance = SwarmInstance(
                    definition=definition,
                    event_bus=event_bus,
                    master_actor=master_actor,
                    agent_pools=agent_pools,
                    trigger_tasks=trigger_tasks,
                    started_at=datetime.utcnow()
                )
                
                self._swarms[swarm_id] = instance
                definition.status = SwarmStatus.ACTIVE
                self._metrics['swarms_started'] += 1
                self._metrics['active_swarms'] = len(self._swarms)
                
                # Persist status
                if self.db_facade:
                    await self._update_status(swarm_id, SwarmStatus.ACTIVE)
                
                logger.info(f"Started swarm: {definition.name} ({swarm_id})")
                return True
                
            except Exception as e:
                logger.error(f"Error starting swarm {swarm_id}: {e}")
                definition.status = SwarmStatus.ERROR
                return False
    
    async def stop_swarm(self, swarm_id: str) -> bool:
        """
        Stop a running swarm.
        
        Args:
            swarm_id: Swarm to stop
            
        Returns:
            True if stopped successfully
        """
        async with self._lock:
            instance = self._swarms.get(swarm_id)
            if not instance:
                logger.warning(f"Swarm not running: {swarm_id}")
                return False
            
            try:
                instance.definition.status = SwarmStatus.STOPPING
                
                # Stop triggers
                for task in instance.trigger_tasks.values():
                    task.cancel()
                
                # Stop agent pools
                for pool in instance.agent_pools.values():
                    await pool.stop()
                
                # Stop master actor
                await instance.master_actor.stop()
                
                # Stop event bus
                await instance.event_bus.stop()
                
                instance.stopped_at = datetime.utcnow()
                instance.definition.status = SwarmStatus.INACTIVE
                
                del self._swarms[swarm_id]
                self._metrics['swarms_stopped'] += 1
                self._metrics['active_swarms'] = len(self._swarms)
                
                # Persist status
                if self.db_facade:
                    await self._update_status(swarm_id, SwarmStatus.INACTIVE)
                
                logger.info(f"Stopped swarm: {swarm_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error stopping swarm {swarm_id}: {e}")
                return False
    
    async def delete_swarm(self, swarm_id: str) -> bool:
        """Delete a swarm definition."""
        # Stop if running
        if swarm_id in self._swarms:
            await self.stop_swarm(swarm_id)
        
        async with self._lock:
            if swarm_id in self._definitions:
                del self._definitions[swarm_id]
            
            if self.db_facade:
                try:
                    self.db_facade.execute(
                        "UPDATE swarms SET status = 'deleted' WHERE swarm_id = ?",
                        (swarm_id,)
                    )
                except:
                    pass
            
            logger.info(f"Deleted swarm: {swarm_id}")
            return True
    
    # =========================================================================
    # User Interaction
    # =========================================================================
    
    async def handle_user_query(self, swarm_id: str, query: str,
                               context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle a user query through a swarm.
        
        Args:
            swarm_id: Target swarm
            query: User's query
            context: Additional context
            
        Returns:
            Swarm processing result
        """
        instance = self._swarms.get(swarm_id)
        if not instance:
            return {
                'status': 'error',
                'error': f'Swarm not running: {swarm_id}'
            }
        
        self._metrics['total_executions'] += 1
        instance.definition.total_executions += 1
        
        # Delegate to master actor
        result = await instance.master_actor.handle_external_trigger(
            trigger_type='user_query',
            trigger_data={
                'query': query,
                'context': context or {}
            }
        )
        
        # Update statistics
        if result.get('status') == 'success':
            instance.definition.successful_executions += 1
        else:
            instance.definition.failed_executions += 1
        
        return result
    
    # =========================================================================
    # External Triggers
    # =========================================================================
    
    async def _start_trigger(self, trigger: TriggerConfig, 
                            swarm_id: str) -> Optional[asyncio.Task]:
        """Start an external trigger."""
        if trigger.trigger_type == TriggerType.SCHEDULE:
            return asyncio.create_task(
                self._schedule_trigger_loop(trigger, swarm_id)
            )
        elif trigger.trigger_type in (TriggerType.KAFKA, TriggerType.RABBITMQ, TriggerType.ACTIVEMQ):
            return asyncio.create_task(
                self._message_trigger_loop(trigger, swarm_id)
            )
        elif trigger.trigger_type == TriggerType.HTTP:
            # HTTP triggers are handled by web routes
            return None
        
        return None
    
    async def _schedule_trigger_loop(self, trigger: TriggerConfig, 
                                    swarm_id: str) -> None:
        """Run scheduled trigger loop."""
        import croniter
        
        cron_expr = trigger.config.get('cron', '0 * * * *')
        
        try:
            cron = croniter.croniter(cron_expr, datetime.utcnow())
        except:
            logger.error(f"Invalid cron expression: {cron_expr}")
            return
        
        while True:
            try:
                # Wait until next scheduled time
                next_time = cron.get_next(datetime)
                wait_seconds = (next_time - datetime.utcnow()).total_seconds()
                
                if wait_seconds > 0:
                    await asyncio.sleep(wait_seconds)
                
                # Execute trigger
                instance = self._swarms.get(swarm_id)
                if instance and instance.is_running:
                    await instance.master_actor.handle_external_trigger(
                        trigger_type='schedule',
                        trigger_data={
                            'trigger_id': trigger.trigger_id,
                            'trigger_name': trigger.name,
                            'scheduled_time': next_time.isoformat()
                        }
                    )
                    trigger.trigger_count += 1
                    trigger.last_triggered = datetime.utcnow()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Schedule trigger error: {e}")
                await asyncio.sleep(60)
    
    async def _message_trigger_loop(self, trigger: TriggerConfig, 
                                   swarm_id: str) -> None:
        """Run message broker trigger loop."""
        from abhikarta.messaging import create_broker, BrokerConfig, Message
        
        try:
            broker_config = BrokerConfig(
                broker_type=trigger.trigger_type.value,
                **trigger.config
            )
            broker = create_broker(broker_config)
            await broker.connect()
            
            async def on_message(message: Message):
                instance = self._swarms.get(swarm_id)
                if instance and instance.is_running:
                    # Apply filter if configured
                    if trigger.filter_expression:
                        try:
                            if not eval(trigger.filter_expression, {'message': message}):
                                return
                        except:
                            pass
                    
                    await instance.master_actor.handle_external_trigger(
                        trigger_type=trigger.trigger_type.value,
                        trigger_data={
                            'trigger_id': trigger.trigger_id,
                            'message': message.to_dict()
                        }
                    )
                    trigger.trigger_count += 1
                    trigger.last_triggered = datetime.utcnow()
            
            topic = trigger.config.get('topic', 'default')
            await broker.subscribe_handler(topic, on_message)
            
            # Keep alive
            while True:
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Message trigger error: {e}")
    
    # =========================================================================
    # Helpers
    # =========================================================================
    
    def _get_agent_executor(self, agent_id: str) -> Optional[Callable]:
        """Get executor for an agent from registry."""
        agent_info = self.agent_registry.get(agent_id)
        if agent_info and 'executor' in agent_info:
            return agent_info['executor']
        return None
    
    async def _save_definition(self, definition: SwarmDefinition) -> None:
        """Save definition to database."""
        if not self.db_facade:
            return
        
        try:
            self.db_facade.execute(
                """INSERT OR REPLACE INTO swarms 
                   (swarm_id, name, description, status, definition_json, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (definition.swarm_id, definition.name, definition.description,
                 definition.status.value, definition.to_json(),
                 definition.created_at.isoformat(), datetime.utcnow().isoformat())
            )
        except Exception as e:
            logger.error(f"Error saving swarm definition: {e}")
    
    async def _update_status(self, swarm_id: str, status: SwarmStatus) -> None:
        """Update swarm status in database."""
        if not self.db_facade:
            return
        
        try:
            self.db_facade.execute(
                "UPDATE swarms SET status = ?, updated_at = ? WHERE swarm_id = ?",
                (status.value, datetime.utcnow().isoformat(), swarm_id)
            )
        except Exception as e:
            logger.error(f"Error updating swarm status: {e}")
    
    # =========================================================================
    # Queries
    # =========================================================================
    
    def get_swarm(self, swarm_id: str) -> Optional[SwarmDefinition]:
        """Get swarm definition."""
        return self._definitions.get(swarm_id)
    
    def list_swarms(self, status: SwarmStatus = None) -> List[SwarmDefinition]:
        """List all swarms, optionally filtered by status."""
        swarms = list(self._definitions.values())
        if status:
            swarms = [s for s in swarms if s.status == status]
        return swarms
    
    def is_running(self, swarm_id: str) -> bool:
        """Check if swarm is running."""
        return swarm_id in self._swarms
    
    def get_metrics(self, swarm_id: str = None) -> Dict[str, Any]:
        """Get orchestrator or swarm metrics."""
        if swarm_id:
            instance = self._swarms.get(swarm_id)
            if instance:
                return {
                    'swarm_id': swarm_id,
                    'status': instance.definition.status.value,
                    'started_at': instance.started_at.isoformat() if instance.started_at else None,
                    'master_metrics': instance.master_actor.get_metrics(),
                    'event_bus_metrics': instance.event_bus.get_metrics(),
                    'agent_pool_metrics': {
                        aid: pool.get_metrics()
                        for aid, pool in instance.agent_pools.items()
                    }
                }
            return None
        
        return {
            **self._metrics,
            'definitions': len(self._definitions),
            'running_swarms': list(self._swarms.keys()),
        }


def get_orchestrator() -> SwarmOrchestrator:
    """Get or create the global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SwarmOrchestrator()
    return _orchestrator


def set_orchestrator(orchestrator: SwarmOrchestrator) -> None:
    """Set the global orchestrator instance."""
    global _orchestrator
    _orchestrator = orchestrator
