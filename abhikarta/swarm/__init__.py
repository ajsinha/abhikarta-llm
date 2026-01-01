"""
Abhikarta Swarm Module - Intelligent Agent Swarms.

This module provides a framework for creating and managing swarms of
cooperative AI agents that communicate through an event-driven architecture.

Key Components:
- SwarmDefinition: Configuration and metadata for a swarm
- MasterActor: Choreographer that coordinates agent activities
- SwarmAgent: Event-reactive agents that perform tasks
- SwarmEventBus: Internal messaging for swarm communication
- SwarmOrchestrator: Lifecycle management for swarms

Architecture:
    External Triggers (Kafka/HTTP/Schedule/User)
           │
           ▼
    ┌─────────────────┐
    │  Master Actor   │ ◄─── LLM + Tools
    │  (Choreographer)│
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Swarm Event Bus │
    └───┬───┬───┬───┬─┘
        │   │   │   │
        ▼   ▼   ▼   ▼
    [Agent1][Agent2][Agent3][AgentN]
        │   │   │   │
        └───┴───┴───┘
             │
             ▼
    [Results to Master]

Version: 1.3.0
Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

from .swarm_definition import (
    SwarmDefinition,
    SwarmConfig,
    SwarmStatus,
    AgentMembership,
    EventSubscription,
    TriggerConfig,
    TriggerType
)

from .master_actor import (
    MasterActor,
    MasterActorConfig,
    MasterDecision,
    DecisionType
)

from .swarm_agent import (
    SwarmAgent,
    SwarmAgentConfig,
    AgentState
)

from .event_bus import (
    SwarmEventBus,
    SwarmEvent,
    EventType,
    EventPriority
)

from .orchestrator import (
    SwarmOrchestrator,
    get_orchestrator
)

from .swarm_template import (
    SwarmTemplate,
    SwarmTemplateManager
)

__all__ = [
    # Definition
    'SwarmDefinition',
    'SwarmConfig',
    'SwarmStatus',
    'AgentMembership',
    'EventSubscription',
    'TriggerConfig',
    'TriggerType',
    
    # Master Actor
    'MasterActor',
    'MasterActorConfig',
    'MasterDecision',
    'DecisionType',
    
    # Swarm Agent
    'SwarmAgent',
    'SwarmAgentConfig',
    'AgentState',
    
    # Event Bus
    'SwarmEventBus',
    'SwarmEvent',
    'EventType',
    'EventPriority',
    
    # Orchestrator
    'SwarmOrchestrator',
    'get_orchestrator',
    
    # Templates
    'SwarmTemplate',
    'SwarmTemplateManager',
]

__version__ = '1.3.0'
