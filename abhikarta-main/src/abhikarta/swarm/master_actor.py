"""
Master Actor - Intelligent choreographer for agent swarms.

The Master Actor is the brain of the swarm, responsible for:
- Receiving external triggers (Kafka, HTTP, scheduled, user queries)
- Analyzing situations using LLM
- Deciding what tasks to publish to the swarm
- Aggregating results from agents
- Making decisions about next steps

Version: 1.3.0
Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import uuid
import json

from .event_bus import SwarmEventBus, SwarmEvent, EventType, EventPriority

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """Types of decisions the master can make."""
    BROADCAST = "broadcast"          # Publish to all matching agents
    DIRECT = "direct"                # Send to specific agent
    AGGREGATE = "aggregate"          # Wait for and aggregate results
    COMPLETE = "complete"            # Task completed, return result
    RETRY = "retry"                  # Retry failed operation
    ESCALATE = "escalate"            # Escalate to human
    NO_ACTION = "no_action"          # No action needed


@dataclass
class MasterDecision:
    """A decision made by the master actor."""
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    decision_type: DecisionType = DecisionType.NO_ACTION
    
    # What triggered this decision
    trigger_event_id: str = ""
    
    # Decision details
    event_type: Optional[str] = None        # Event type to publish
    target_agents: List[str] = field(default_factory=list)  # Target agent IDs
    payload: Any = None                     # Payload to send
    
    # Metadata
    reasoning: str = ""                     # LLM reasoning
    confidence: float = 1.0                 # Decision confidence
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'decision_id': self.decision_id,
            'decision_type': self.decision_type.value,
            'trigger_event_id': self.trigger_event_id,
            'event_type': self.event_type,
            'target_agents': self.target_agents,
            'payload': self.payload,
            'reasoning': self.reasoning,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class MasterActorConfig:
    """Configuration for the master actor."""
    # LLM settings
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 4000
    
    # Prompts
    system_prompt: str = """You are the Master Actor, the intelligent choreographer of an AI agent swarm.

Your role is to:
1. Analyze incoming tasks and events
2. Decide which agents should handle them
3. Coordinate agent activities
4. Aggregate results
5. Determine when tasks are complete

You have access to the following agents in your swarm:
{agent_list}

Available event types you can publish:
- task.search: Request search operations
- task.analyze: Request analysis
- task.generate: Request content generation
- task.transform: Request data transformation
- task.validate: Request validation
- task.custom.{name}: Custom task types

Respond with a JSON decision object containing:
- decision_type: One of "broadcast", "direct", "aggregate", "complete", "retry", "escalate", "no_action"
- event_type: The event type to publish (if applicable)
- target_agents: List of agent IDs to target (empty for broadcast)
- payload: The data to send to agents
- reasoning: Your reasoning for this decision
"""
    
    decision_prompt: str = """Based on the current state and incoming event, make a decision.

Current swarm state:
{swarm_state}

Incoming event:
{event}

Previous results (if any):
{results}

What should we do next? Respond with a JSON decision."""
    
    # Timeouts
    decision_timeout: int = 60              # LLM decision timeout
    aggregation_timeout: int = 120          # Wait for results timeout
    
    # Limits
    max_iterations: int = 50                # Max decision iterations
    max_pending_tasks: int = 100            # Max pending tasks


class MasterActor:
    """
    Master Actor - Choreographer for the swarm.
    
    The master actor is always loaded and coordinates all swarm activities.
    It uses LLM to make intelligent decisions about task distribution and
    result aggregation.
    
    Usage:
        config = MasterActorConfig(llm_model="gpt-4o")
        master = MasterActor("swarm-1", event_bus, config)
        await master.start()
        
        # Handle external trigger
        await master.handle_external_trigger(trigger_data)
    """
    
    def __init__(self, swarm_id: str, event_bus: SwarmEventBus, 
                 config: MasterActorConfig, agent_registry: Dict[str, Any] = None):
        self.swarm_id = swarm_id
        self.event_bus = event_bus
        self.config = config
        self.agent_registry = agent_registry or {}
        
        self._actor_id = f"master-{swarm_id}"
        self._running = False
        
        # State
        self._pending_tasks: Dict[str, Dict] = {}  # correlation_id -> task state
        self._decisions: List[MasterDecision] = []
        self._iteration_count = 0
        
        # LLM client (lazy loaded)
        self._llm_client = None
        
        # Metrics
        self._metrics = {
            'triggers_received': 0,
            'decisions_made': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
        }
    
    async def start(self) -> None:
        """Start the master actor."""
        self._running = True
        
        # Subscribe to result events
        await self.event_bus.subscribe("result.*", self._handle_result, priority=10)
        await self.event_bus.subscribe("agent.*", self._handle_agent_event, priority=5)
        await self.event_bus.subscribe("control.*", self._handle_control_event, priority=20)
        
        logger.info(f"Master actor started for swarm {self.swarm_id}")
    
    async def stop(self) -> None:
        """Stop the master actor."""
        self._running = False
        logger.info(f"Master actor stopped for swarm {self.swarm_id}")
    
    async def handle_external_trigger(self, trigger_type: str, 
                                      trigger_data: Any,
                                      correlation_id: str = None) -> Dict[str, Any]:
        """
        Handle an external trigger (Kafka message, HTTP request, schedule, etc.)
        
        Args:
            trigger_type: Type of trigger (kafka, http, schedule, user_query)
            trigger_data: Trigger payload
            correlation_id: Optional correlation ID for tracking
            
        Returns:
            Final result after swarm processing
        """
        self._metrics['triggers_received'] += 1
        correlation_id = correlation_id or str(uuid.uuid4())
        
        # Initialize task state
        self._pending_tasks[correlation_id] = {
            'trigger_type': trigger_type,
            'trigger_data': trigger_data,
            'start_time': datetime.utcnow(),
            'results': [],
            'status': 'processing',
            'iterations': 0,
        }
        
        # Create initial event
        trigger_event = SwarmEvent(
            event_type=f"trigger.{trigger_type}",
            source=self._actor_id,
            payload=trigger_data,
            correlation_id=correlation_id,
            priority=EventPriority.HIGH
        )
        
        # Make initial decision
        decision = await self._make_decision(trigger_event)
        
        # Execute decision
        await self._execute_decision(decision, correlation_id)
        
        # Wait for completion or timeout
        result = await self._wait_for_completion(correlation_id)
        
        return result
    
    async def _make_decision(self, event: SwarmEvent) -> MasterDecision:
        """Use LLM to make a decision about the event."""
        self._iteration_count += 1
        
        if self._iteration_count > self.config.max_iterations:
            logger.warning("Max iterations reached, forcing completion")
            return MasterDecision(
                decision_type=DecisionType.COMPLETE,
                trigger_event_id=event.event_id,
                reasoning="Max iterations reached"
            )
        
        try:
            # Build context for LLM
            agent_list = self._format_agent_list()
            swarm_state = self._format_swarm_state(event.correlation_id)
            results = self._format_results(event.correlation_id)
            
            system_prompt = self.config.system_prompt.format(
                agent_list=agent_list
            )
            
            user_prompt = self.config.decision_prompt.format(
                swarm_state=swarm_state,
                event=json.dumps(event.to_dict(), indent=2, default=str),
                results=results
            )
            
            # Call LLM
            response = await self._call_llm(system_prompt, user_prompt)
            
            # Parse decision
            decision = self._parse_decision(response, event.event_id)
            
            self._decisions.append(decision)
            self._metrics['decisions_made'] += 1
            
            # Log decision
            await self.event_bus.publish(SwarmEvent(
                event_type=EventType.MASTER_DECISION.value,
                source=self._actor_id,
                payload=decision.to_dict(),
                correlation_id=event.correlation_id
            ))
            
            return decision
            
        except Exception as e:
            logger.error(f"Decision making error: {e}")
            return MasterDecision(
                decision_type=DecisionType.NO_ACTION,
                trigger_event_id=event.event_id,
                reasoning=f"Error: {str(e)}"
            )
    
    async def _execute_decision(self, decision: MasterDecision, 
                               correlation_id: str) -> None:
        """Execute a decision by publishing appropriate events."""
        if decision.decision_type == DecisionType.NO_ACTION:
            return
        
        if decision.decision_type == DecisionType.COMPLETE:
            self._pending_tasks[correlation_id]['status'] = 'completed'
            return
        
        if decision.decision_type in (DecisionType.BROADCAST, DecisionType.DIRECT):
            event = SwarmEvent(
                event_type=decision.event_type or "task.custom",
                source=self._actor_id,
                target=decision.target_agents[0] if decision.target_agents else None,
                payload=decision.payload,
                correlation_id=correlation_id,
                priority=EventPriority.NORMAL
            )
            await self.event_bus.publish(event)
        
        elif decision.decision_type == DecisionType.AGGREGATE:
            # Wait mode - handled in wait_for_completion
            pass
        
        elif decision.decision_type == DecisionType.RETRY:
            # Re-publish with incremented retry count
            event = SwarmEvent(
                event_type=decision.event_type or "task.retry",
                source=self._actor_id,
                payload=decision.payload,
                correlation_id=correlation_id,
                priority=EventPriority.HIGH
            )
            await self.event_bus.publish(event)
        
        elif decision.decision_type == DecisionType.ESCALATE:
            # Publish escalation event for HITL
            event = SwarmEvent(
                event_type="escalate.human",
                source=self._actor_id,
                payload={
                    'reason': decision.reasoning,
                    'context': decision.payload
                },
                correlation_id=correlation_id,
                priority=EventPriority.CRITICAL
            )
            await self.event_bus.publish(event)
    
    async def _handle_result(self, event: SwarmEvent) -> None:
        """Handle result events from agents."""
        correlation_id = event.correlation_id
        
        if correlation_id and correlation_id in self._pending_tasks:
            task_state = self._pending_tasks[correlation_id]
            task_state['results'].append({
                'agent': event.source,
                'event_type': event.event_type,
                'payload': event.payload,
                'timestamp': event.timestamp.isoformat()
            })
            task_state['iterations'] += 1
            
            # Check if we should make another decision
            if task_state['status'] == 'processing':
                decision = await self._make_decision(event)
                await self._execute_decision(decision, correlation_id)
    
    async def _handle_agent_event(self, event: SwarmEvent) -> None:
        """Handle agent lifecycle events."""
        logger.debug(f"Agent event: {event.event_type} from {event.source}")
    
    async def _handle_control_event(self, event: SwarmEvent) -> None:
        """Handle control events."""
        logger.debug(f"Control event: {event.event_type}")
    
    async def _wait_for_completion(self, correlation_id: str) -> Dict[str, Any]:
        """Wait for task completion or timeout."""
        timeout = self.config.aggregation_timeout
        start_time = datetime.utcnow()
        
        while True:
            task_state = self._pending_tasks.get(correlation_id)
            
            if not task_state:
                return {'status': 'error', 'error': 'Task not found'}
            
            if task_state['status'] == 'completed':
                self._metrics['tasks_completed'] += 1
                return {
                    'status': 'success',
                    'results': task_state['results'],
                    'iterations': task_state['iterations'],
                    'duration': (datetime.utcnow() - task_state['start_time']).total_seconds()
                }
            
            if task_state['status'] == 'failed':
                self._metrics['tasks_failed'] += 1
                return {
                    'status': 'failed',
                    'error': task_state.get('error', 'Unknown error'),
                    'results': task_state['results']
                }
            
            # Check timeout
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            if elapsed > timeout:
                self._metrics['tasks_failed'] += 1
                return {
                    'status': 'timeout',
                    'results': task_state['results'],
                    'iterations': task_state['iterations']
                }
            
            await asyncio.sleep(0.1)
    
    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Call the LLM for decision making."""
        # This is a simplified implementation
        # In production, use the actual LLM client from abhikarta
        try:
            # Try to use the LLM adapter
            from abhikarta.llm import LLMAdapter
            
            if not self._llm_client:
                self._llm_client = LLMAdapter(
                    provider=self.config.llm_provider,
                    model=self.config.llm_model
                )
            
            response = await self._llm_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            return response.content
            
        except ImportError:
            # Fallback: simple rule-based decision
            logger.warning("LLM adapter not available, using rule-based fallback")
            return json.dumps({
                'decision_type': 'broadcast',
                'event_type': 'task.process',
                'target_agents': [],
                'payload': {'instruction': 'Process this request'},
                'reasoning': 'Rule-based fallback'
            })
    
    def _parse_decision(self, response: str, trigger_event_id: str) -> MasterDecision:
        """Parse LLM response into a decision."""
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response)
            
            return MasterDecision(
                decision_type=DecisionType(data.get('decision_type', 'no_action')),
                trigger_event_id=trigger_event_id,
                event_type=data.get('event_type'),
                target_agents=data.get('target_agents', []),
                payload=data.get('payload'),
                reasoning=data.get('reasoning', '')
            )
        except Exception as e:
            logger.error(f"Failed to parse decision: {e}")
            return MasterDecision(
                decision_type=DecisionType.NO_ACTION,
                trigger_event_id=trigger_event_id,
                reasoning=f"Parse error: {str(e)}"
            )
    
    def _format_agent_list(self) -> str:
        """Format agent list for LLM context."""
        lines = []
        for agent_id, agent_info in self.agent_registry.items():
            lines.append(f"- {agent_id}: {agent_info.get('description', 'No description')}")
            if agent_info.get('capabilities'):
                lines.append(f"  Capabilities: {', '.join(agent_info['capabilities'])}")
        return '\n'.join(lines) if lines else "No agents registered"
    
    def _format_swarm_state(self, correlation_id: str = None) -> str:
        """Format current swarm state for LLM context."""
        task_state = self._pending_tasks.get(correlation_id, {})
        return json.dumps({
            'pending_tasks': len(self._pending_tasks),
            'current_task': {
                'iterations': task_state.get('iterations', 0),
                'results_count': len(task_state.get('results', [])),
                'status': task_state.get('status', 'unknown')
            },
            'total_decisions': len(self._decisions)
        }, indent=2)
    
    def _format_results(self, correlation_id: str = None) -> str:
        """Format results for LLM context."""
        task_state = self._pending_tasks.get(correlation_id, {})
        results = task_state.get('results', [])
        
        if not results:
            return "No results yet"
        
        return json.dumps(results[-5:], indent=2, default=str)  # Last 5 results
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get master actor metrics."""
        return {
            **self._metrics,
            'pending_tasks': len(self._pending_tasks),
            'total_decisions': len(self._decisions),
            'iteration_count': self._iteration_count,
        }
