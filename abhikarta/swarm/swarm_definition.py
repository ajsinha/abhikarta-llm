"""
Swarm Definition - Configuration and metadata for agent swarms.

Defines the structure and configuration for swarms, including:
- Swarm metadata and settings
- Agent membership configuration
- Event subscriptions
- External trigger configurations

Version: 1.3.0
Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
import json


class SwarmStatus(Enum):
    """Swarm lifecycle status."""
    DRAFT = "draft"              # Being designed
    INACTIVE = "inactive"        # Defined but not running
    STARTING = "starting"        # Starting up
    ACTIVE = "active"            # Running
    PAUSED = "paused"            # Temporarily paused
    STOPPING = "stopping"        # Shutting down
    ERROR = "error"              # Error state


class TriggerType(Enum):
    """Types of external triggers for swarm activation."""
    KAFKA = "kafka"              # Kafka topic message
    RABBITMQ = "rabbitmq"        # RabbitMQ message
    ACTIVEMQ = "activemq"        # ActiveMQ message
    HTTP = "http"                # HTTP webhook
    SCHEDULE = "schedule"        # Cron schedule
    USER_QUERY = "user_query"    # Direct user input
    API = "api"                  # API call
    EVENT = "event"              # Internal event


@dataclass
class TriggerConfig:
    """Configuration for an external trigger."""
    trigger_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trigger_type: TriggerType = TriggerType.USER_QUERY
    name: str = ""
    description: str = ""
    
    # Trigger-specific config
    config: Dict[str, Any] = field(default_factory=dict)
    # e.g., for Kafka: {'topic': 'events', 'group': 'swarm-1'}
    # e.g., for Schedule: {'cron': '0 * * * *'}
    # e.g., for HTTP: {'endpoint': '/webhook/swarm-1', 'method': 'POST'}
    
    # Filtering
    filter_expression: Optional[str] = None  # Python expression to filter events
    
    # State
    is_active: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'trigger_id': self.trigger_id,
            'trigger_type': self.trigger_type.value,
            'name': self.name,
            'description': self.description,
            'config': self.config,
            'filter_expression': self.filter_expression,
            'is_active': self.is_active,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None,
            'trigger_count': self.trigger_count,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TriggerConfig':
        return cls(
            trigger_id=data.get('trigger_id', str(uuid.uuid4())),
            trigger_type=TriggerType(data.get('trigger_type', 'user_query')),
            name=data.get('name', ''),
            description=data.get('description', ''),
            config=data.get('config', {}),
            filter_expression=data.get('filter_expression'),
            is_active=data.get('is_active', True),
            last_triggered=datetime.fromisoformat(data['last_triggered']) if data.get('last_triggered') else None,
            trigger_count=data.get('trigger_count', 0),
        )


@dataclass
class EventSubscription:
    """Configuration for an agent's event subscription."""
    subscription_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    event_pattern: str = ""      # Pattern like "task.*", "result.search", etc.
    
    # Processing
    priority: int = 1            # Higher = processed first
    max_concurrent: int = 5      # Max concurrent processing
    timeout_seconds: int = 60    # Processing timeout
    
    # Filtering
    filter_headers: Dict[str, str] = field(default_factory=dict)
    filter_expression: Optional[str] = None
    
    # State
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'subscription_id': self.subscription_id,
            'agent_id': self.agent_id,
            'event_pattern': self.event_pattern,
            'priority': self.priority,
            'max_concurrent': self.max_concurrent,
            'timeout_seconds': self.timeout_seconds,
            'filter_headers': self.filter_headers,
            'filter_expression': self.filter_expression,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventSubscription':
        return cls(
            subscription_id=data.get('subscription_id', str(uuid.uuid4())),
            agent_id=data.get('agent_id', ''),
            event_pattern=data.get('event_pattern', ''),
            priority=data.get('priority', 1),
            max_concurrent=data.get('max_concurrent', 5),
            timeout_seconds=data.get('timeout_seconds', 60),
            filter_headers=data.get('filter_headers', {}),
            filter_expression=data.get('filter_expression'),
            is_active=data.get('is_active', True),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.utcnow(),
        )


@dataclass
class AgentMembership:
    """Configuration for an agent's membership in a swarm."""
    membership_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    agent_name: str = ""
    
    # Role in swarm
    role: str = "worker"         # worker, specialist, coordinator
    description: str = ""
    
    # Event subscriptions
    subscriptions: List[EventSubscription] = field(default_factory=list)
    
    # Resource limits
    max_instances: int = 10      # Max concurrent instances
    min_instances: int = 0       # Min instances to keep alive
    
    # Behavior
    auto_scale: bool = True      # Auto-scale based on load
    idle_timeout: int = 300      # Seconds before idle shutdown
    
    # State
    is_active: bool = True
    current_instances: int = 0
    total_tasks_processed: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'membership_id': self.membership_id,
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'role': self.role,
            'description': self.description,
            'subscriptions': [s.to_dict() for s in self.subscriptions],
            'max_instances': self.max_instances,
            'min_instances': self.min_instances,
            'auto_scale': self.auto_scale,
            'idle_timeout': self.idle_timeout,
            'is_active': self.is_active,
            'current_instances': self.current_instances,
            'total_tasks_processed': self.total_tasks_processed,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMembership':
        return cls(
            membership_id=data.get('membership_id', str(uuid.uuid4())),
            agent_id=data.get('agent_id', ''),
            agent_name=data.get('agent_name', ''),
            role=data.get('role', 'worker'),
            description=data.get('description', ''),
            subscriptions=[EventSubscription.from_dict(s) for s in data.get('subscriptions', [])],
            max_instances=data.get('max_instances', 10),
            min_instances=data.get('min_instances', 0),
            auto_scale=data.get('auto_scale', True),
            idle_timeout=data.get('idle_timeout', 300),
            is_active=data.get('is_active', True),
            current_instances=data.get('current_instances', 0),
            total_tasks_processed=data.get('total_tasks_processed', 0),
        )


@dataclass
class SwarmConfig:
    """Configuration settings for a swarm."""
    # Event bus
    event_bus_type: str = "memory"    # memory, kafka, rabbitmq
    event_bus_config: Dict[str, Any] = field(default_factory=dict)
    
    # Master actor LLM
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 4000
    
    # Master actor prompt
    master_system_prompt: str = ""
    master_decision_prompt: str = ""
    
    # Timeouts
    master_timeout: int = 120         # Master decision timeout
    agent_timeout: int = 60           # Default agent timeout
    swarm_timeout: int = 600          # Overall swarm task timeout
    
    # Limits
    max_iterations: int = 100         # Max event cycles per task
    max_agents: int = 50              # Max concurrent agents
    max_events_per_second: int = 100  # Rate limiting
    
    # Retry
    retry_on_failure: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Logging
    log_all_events: bool = True
    log_decisions: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_bus_type': self.event_bus_type,
            'event_bus_config': self.event_bus_config,
            'llm_provider': self.llm_provider,
            'llm_model': self.llm_model,
            'llm_temperature': self.llm_temperature,
            'llm_max_tokens': self.llm_max_tokens,
            'master_system_prompt': self.master_system_prompt,
            'master_decision_prompt': self.master_decision_prompt,
            'master_timeout': self.master_timeout,
            'agent_timeout': self.agent_timeout,
            'swarm_timeout': self.swarm_timeout,
            'max_iterations': self.max_iterations,
            'max_agents': self.max_agents,
            'max_events_per_second': self.max_events_per_second,
            'retry_on_failure': self.retry_on_failure,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'log_all_events': self.log_all_events,
            'log_decisions': self.log_decisions,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SwarmConfig':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class SwarmDefinition:
    """
    Complete definition of an agent swarm.
    
    A swarm consists of:
    - A master actor that choreographs activities
    - Multiple agent members that react to events
    - An event bus for internal communication
    - External triggers for activation
    """
    swarm_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    
    # Configuration
    config: SwarmConfig = field(default_factory=SwarmConfig)
    
    # Agent members
    agents: List[AgentMembership] = field(default_factory=list)
    
    # External triggers
    triggers: List[TriggerConfig] = field(default_factory=list)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    category: str = "general"
    
    # State
    status: SwarmStatus = SwarmStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    
    # Statistics
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_events_processed: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'swarm_id': self.swarm_id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'config': self.config.to_dict(),
            'agents': [a.to_dict() for a in self.agents],
            'triggers': [t.to_dict() for t in self.triggers],
            'tags': self.tags,
            'category': self.category,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by,
            'total_executions': self.total_executions,
            'successful_executions': self.successful_executions,
            'failed_executions': self.failed_executions,
            'total_events_processed': self.total_events_processed,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SwarmDefinition':
        """Create from dictionary."""
        return cls(
            swarm_id=data.get('swarm_id', str(uuid.uuid4())),
            name=data.get('name', ''),
            description=data.get('description', ''),
            version=data.get('version', '1.0.0'),
            config=SwarmConfig.from_dict(data.get('config', {})),
            agents=[AgentMembership.from_dict(a) for a in data.get('agents', [])],
            triggers=[TriggerConfig.from_dict(t) for t in data.get('triggers', [])],
            tags=data.get('tags', []),
            category=data.get('category', 'general'),
            status=SwarmStatus(data.get('status', 'draft')),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.utcnow(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.utcnow(),
            created_by=data.get('created_by', ''),
            total_executions=data.get('total_executions', 0),
            successful_executions=data.get('successful_executions', 0),
            failed_executions=data.get('failed_executions', 0),
            total_events_processed=data.get('total_events_processed', 0),
        )
    
    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), indent=2, default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SwarmDefinition':
        """Deserialize from JSON."""
        return cls.from_dict(json.loads(json_str))
    
    def add_agent(self, agent_id: str, agent_name: str, 
                  event_patterns: List[str], role: str = "worker") -> AgentMembership:
        """Add an agent to the swarm."""
        membership = AgentMembership(
            agent_id=agent_id,
            agent_name=agent_name,
            role=role,
            subscriptions=[
                EventSubscription(agent_id=agent_id, event_pattern=p)
                for p in event_patterns
            ]
        )
        self.agents.append(membership)
        self.updated_at = datetime.utcnow()
        return membership
    
    def add_trigger(self, trigger_type: TriggerType, name: str, 
                   config: Dict[str, Any]) -> TriggerConfig:
        """Add an external trigger."""
        trigger = TriggerConfig(
            trigger_type=trigger_type,
            name=name,
            config=config
        )
        self.triggers.append(trigger)
        self.updated_at = datetime.utcnow()
        return trigger
    
    def get_agent(self, agent_id: str) -> Optional[AgentMembership]:
        """Get agent membership by ID."""
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent
        return None
    
    def get_subscriptions_for_event(self, event_type: str) -> List[EventSubscription]:
        """Get all subscriptions matching an event type."""
        import fnmatch
        subscriptions = []
        for agent in self.agents:
            if agent.is_active:
                for sub in agent.subscriptions:
                    if sub.is_active and fnmatch.fnmatch(event_type, sub.event_pattern):
                        subscriptions.append(sub)
        return sorted(subscriptions, key=lambda s: -s.priority)
