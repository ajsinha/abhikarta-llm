"""
Swarm Agent - Event-reactive agents that perform tasks within a swarm.

Swarm agents are spawned on-demand when events match their subscriptions.
They perform tasks and report results back to the master actor.

Version: 1.3.0
Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import uuid
import json

from .event_bus import SwarmEventBus, SwarmEvent, EventType, EventPriority
from .swarm_definition import AgentMembership, EventSubscription

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Agent lifecycle states."""
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class SwarmAgentConfig:
    """Configuration for a swarm agent instance."""
    agent_id: str = ""                      # Linked agent definition ID
    instance_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Agent definition
    name: str = ""
    description: str = ""
    
    # LLM settings (if agent uses LLM)
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    temperature: float = 0.7
    system_prompt: str = ""
    
    # Behavior
    timeout: int = 60                       # Task timeout in seconds
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Resources
    max_concurrent: int = 5                 # Max concurrent tasks
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'agent_id': self.agent_id,
            'instance_id': self.instance_id,
            'name': self.name,
            'description': self.description,
            'llm_provider': self.llm_provider,
            'llm_model': self.llm_model,
            'temperature': self.temperature,
            'system_prompt': self.system_prompt,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'max_concurrent': self.max_concurrent,
        }


class SwarmAgent:
    """
    Swarm Agent - Event-reactive worker in a swarm.
    
    Agents are spawned on-demand when the event bus receives events
    matching their subscriptions. They process tasks and report results
    back through the event bus.
    
    Usage:
        config = SwarmAgentConfig(
            agent_id="search-agent",
            name="Search Agent",
            system_prompt="You are a search specialist..."
        )
        agent = SwarmAgent(config, event_bus, membership)
        await agent.start()
    """
    
    def __init__(self, config: SwarmAgentConfig, 
                 event_bus: SwarmEventBus,
                 membership: AgentMembership = None,
                 agent_executor: Callable = None):
        self.config = config
        self.event_bus = event_bus
        self.membership = membership
        self._agent_executor = agent_executor
        
        self._actor_id = f"agent-{config.agent_id}-{config.instance_id[:8]}"
        self._running = False
        self._state = AgentState.IDLE
        
        # Task tracking
        self._active_tasks: Dict[str, Dict] = {}
        self._semaphore = asyncio.Semaphore(config.max_concurrent)
        
        # Metrics
        self._metrics = {
            'tasks_received': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_processing_time': 0.0,
        }
        
        # LLM client
        self._llm_client = None
    
    @property
    def state(self) -> AgentState:
        return self._state
    
    @property
    def is_busy(self) -> bool:
        return len(self._active_tasks) >= self.config.max_concurrent
    
    async def start(self) -> None:
        """Start the agent and subscribe to events."""
        self._running = True
        self._state = AgentState.IDLE
        
        # Subscribe to configured event patterns
        if self.membership:
            for subscription in self.membership.subscriptions:
                if subscription.is_active:
                    await self.event_bus.subscribe(
                        subscription.event_pattern,
                        self._handle_event,
                        priority=subscription.priority
                    )
                    logger.debug(f"Agent {self._actor_id} subscribed to {subscription.event_pattern}")
        
        # Announce ready
        await self.event_bus.publish(SwarmEvent(
            event_type=EventType.AGENT_READY.value,
            source=self._actor_id,
            payload={
                'agent_id': self.config.agent_id,
                'instance_id': self.config.instance_id,
                'capabilities': self._get_capabilities()
            }
        ))
        
        logger.info(f"Swarm agent started: {self._actor_id}")
    
    async def stop(self) -> None:
        """Stop the agent."""
        self._running = False
        self._state = AgentState.STOPPED
        
        # Announce stopped
        await self.event_bus.publish(SwarmEvent(
            event_type=EventType.AGENT_STOPPED.value,
            source=self._actor_id,
            payload={'agent_id': self.config.agent_id}
        ))
        
        logger.info(f"Swarm agent stopped: {self._actor_id}")
    
    async def _handle_event(self, event: SwarmEvent) -> None:
        """Handle incoming events matching subscriptions."""
        if not self._running:
            return
        
        # Check if targeted at another agent
        if event.target and event.target != self._actor_id and event.target != self.config.agent_id:
            return
        
        self._metrics['tasks_received'] += 1
        
        # Use semaphore for concurrency control
        async with self._semaphore:
            await self._process_task(event)
    
    async def _process_task(self, event: SwarmEvent) -> None:
        """Process a task event."""
        task_id = event.event_id
        start_time = datetime.now(timezone.utc)
        
        # Track task
        self._active_tasks[task_id] = {
            'event': event,
            'start_time': start_time,
            'status': 'processing'
        }
        
        # Update state
        self._state = AgentState.PROCESSING
        await self.event_bus.publish(SwarmEvent(
            event_type=EventType.AGENT_BUSY.value,
            source=self._actor_id,
            payload={'task_id': task_id}
        ))
        
        try:
            # Execute the task
            result = await self._execute_task(event)
            
            # Publish result
            await self.event_bus.publish(SwarmEvent(
                event_type=f"result.{event.event_type.split('.')[-1]}",
                source=self._actor_id,
                target=event.source,  # Reply to sender (usually master)
                payload=result,
                correlation_id=event.correlation_id,
                parent_id=event.event_id
            ))
            
            self._metrics['tasks_completed'] += 1
            self._active_tasks[task_id]['status'] = 'completed'
            
        except Exception as e:
            logger.error(f"Task processing error: {e}")
            self._metrics['tasks_failed'] += 1
            self._active_tasks[task_id]['status'] = 'failed'
            self._active_tasks[task_id]['error'] = str(e)
            
            # Publish error
            await self.event_bus.publish(SwarmEvent(
                event_type=EventType.TASK_FAILED.value,
                source=self._actor_id,
                target=event.source,
                payload={
                    'error': str(e),
                    'task_id': task_id,
                    'original_event': event.event_type
                },
                correlation_id=event.correlation_id,
                parent_id=event.event_id
            ))
        
        finally:
            # Update processing time
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            self._metrics['total_processing_time'] += elapsed
            
            # Remove from active tasks
            del self._active_tasks[task_id]
            
            # Update state
            if not self._active_tasks:
                self._state = AgentState.IDLE
                await self.event_bus.publish(SwarmEvent(
                    event_type=EventType.AGENT_IDLE.value,
                    source=self._actor_id
                ))
    
    async def _execute_task(self, event: SwarmEvent) -> Any:
        """
        Execute the actual task.
        
        Override this method or provide an agent_executor for custom behavior.
        """
        # If custom executor provided, use it
        if self._agent_executor:
            if asyncio.iscoroutinefunction(self._agent_executor):
                return await self._agent_executor(event, self.config)
            else:
                return self._agent_executor(event, self.config)
        
        # Default: Use LLM if system prompt provided
        if self.config.system_prompt:
            return await self._execute_with_llm(event)
        
        # Fallback: Echo back
        return {
            'status': 'processed',
            'agent': self._actor_id,
            'input': event.payload,
            'message': 'No executor configured, echoing input'
        }
    
    async def _execute_with_llm(self, event: SwarmEvent) -> Any:
        """Execute task using LLM."""
        try:
            from abhikarta.llm import LLMAdapter
            
            if not self._llm_client:
                self._llm_client = LLMAdapter(
                    provider=self.config.llm_provider,
                    model=self.config.llm_model
                )
            
            # Build prompt from event
            user_prompt = self._build_prompt_from_event(event)
            
            response = await self._llm_client.generate(
                prompt=user_prompt,
                system_prompt=self.config.system_prompt,
                temperature=self.config.temperature
            )
            
            return {
                'status': 'success',
                'agent': self._actor_id,
                'result': response.content,
                'model': self.config.llm_model
            }
            
        except ImportError:
            logger.warning("LLM adapter not available")
            return {
                'status': 'error',
                'error': 'LLM adapter not available'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _build_prompt_from_event(self, event: SwarmEvent) -> str:
        """Build a prompt from an event."""
        if isinstance(event.payload, str):
            return event.payload
        elif isinstance(event.payload, dict):
            if 'prompt' in event.payload:
                return event.payload['prompt']
            elif 'query' in event.payload:
                return event.payload['query']
            elif 'instruction' in event.payload:
                return event.payload['instruction']
            else:
                return json.dumps(event.payload, indent=2)
        else:
            return str(event.payload)
    
    def _get_capabilities(self) -> List[str]:
        """Get agent capabilities based on subscriptions."""
        capabilities = []
        if self.membership:
            for sub in self.membership.subscriptions:
                # Extract capability from event pattern
                parts = sub.event_pattern.split('.')
                if len(parts) > 1:
                    capabilities.append(parts[-1].replace('*', 'any'))
        return capabilities
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics."""
        return {
            **self._metrics,
            'state': self._state.value,
            'active_tasks': len(self._active_tasks),
            'avg_processing_time': (
                self._metrics['total_processing_time'] / 
                max(1, self._metrics['tasks_completed'])
            ),
        }


class SwarmAgentPool:
    """
    Pool of swarm agents for auto-scaling.
    
    Manages agent instances based on load, spawning new agents
    when needed and stopping idle ones.
    """
    
    def __init__(self, membership: AgentMembership, 
                 event_bus: SwarmEventBus,
                 agent_executor: Callable = None):
        self.membership = membership
        self.event_bus = event_bus
        self._agent_executor = agent_executor
        
        self._agents: Dict[str, SwarmAgent] = {}
        self._lock = asyncio.Lock()
        
        # Auto-scaling
        self._scale_check_task = None
        self._scale_interval = 5.0  # seconds
    
    async def start(self) -> None:
        """Start the agent pool."""
        # Start minimum instances
        for _ in range(self.membership.min_instances):
            await self._spawn_agent()
        
        # Start auto-scaling if enabled
        if self.membership.auto_scale:
            self._scale_check_task = asyncio.create_task(self._auto_scale_loop())
        
        logger.info(f"Agent pool started for {self.membership.agent_id}")
    
    async def stop(self) -> None:
        """Stop all agents in the pool."""
        if self._scale_check_task:
            self._scale_check_task.cancel()
        
        for agent in list(self._agents.values()):
            await agent.stop()
        
        self._agents.clear()
        logger.info(f"Agent pool stopped for {self.membership.agent_id}")
    
    async def _spawn_agent(self) -> SwarmAgent:
        """Spawn a new agent instance."""
        async with self._lock:
            if len(self._agents) >= self.membership.max_instances:
                return None
            
            config = SwarmAgentConfig(
                agent_id=self.membership.agent_id,
                name=self.membership.agent_name,
                description=self.membership.description,
                max_concurrent=5,
                timeout=60
            )
            
            agent = SwarmAgent(
                config=config,
                event_bus=self.event_bus,
                membership=self.membership,
                agent_executor=self._agent_executor
            )
            
            await agent.start()
            self._agents[config.instance_id] = agent
            self.membership.current_instances = len(self._agents)
            
            return agent
    
    async def _stop_agent(self, instance_id: str) -> None:
        """Stop an agent instance."""
        async with self._lock:
            if instance_id in self._agents:
                agent = self._agents[instance_id]
                await agent.stop()
                del self._agents[instance_id]
                self.membership.current_instances = len(self._agents)
    
    async def _auto_scale_loop(self) -> None:
        """Auto-scaling loop."""
        while True:
            try:
                await asyncio.sleep(self._scale_interval)
                
                # Count busy agents
                busy_count = sum(1 for a in self._agents.values() if a.is_busy)
                total = len(self._agents)
                
                # Scale up if all busy and under max
                if busy_count == total and total < self.membership.max_instances:
                    await self._spawn_agent()
                    logger.debug(f"Scaled up {self.membership.agent_id}: {total + 1} instances")
                
                # Scale down if mostly idle and above min
                idle_count = sum(1 for a in self._agents.values() if a.state == AgentState.IDLE)
                if idle_count > 1 and total > self.membership.min_instances:
                    # Find an idle agent to stop
                    for instance_id, agent in list(self._agents.items()):
                        if agent.state == AgentState.IDLE:
                            await self._stop_agent(instance_id)
                            logger.debug(f"Scaled down {self.membership.agent_id}: {total - 1} instances")
                            break
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto-scale error: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get pool metrics."""
        return {
            'total_instances': len(self._agents),
            'busy_instances': sum(1 for a in self._agents.values() if a.is_busy),
            'idle_instances': sum(1 for a in self._agents.values() if a.state == AgentState.IDLE),
            'agent_metrics': {
                instance_id: agent.get_metrics()
                for instance_id, agent in self._agents.items()
            }
        }
