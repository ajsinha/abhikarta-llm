"""
Agent Manager - Agent CRUD and lifecycle management.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.

Patent Pending: Certain architectural patterns and implementations described in this
software may be subject to patent applications.
"""

import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Supported agent types."""
    REACT = "react"
    PLAN_AND_EXECUTE = "plan_and_execute"
    TOOL_CALLING = "tool_calling"
    CONVERSATIONAL = "conversational"
    RETRIEVAL = "retrieval"
    CUSTOM = "custom"


class AgentStatus(Enum):
    """Agent lifecycle status."""
    DRAFT = "draft"
    TESTING = "testing"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


@dataclass
class AgentNode:
    """Represents a node in the agent workflow."""
    node_id: str
    node_type: str  # llm, tool, condition, input, output
    name: str
    config: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0})


@dataclass
class AgentEdge:
    """Represents an edge connecting nodes."""
    edge_id: str
    source_node: str
    target_node: str
    condition: Optional[str] = None
    label: Optional[str] = None


@dataclass
class AgentWorkflow:
    """Represents the complete agent workflow definition."""
    nodes: List[AgentNode] = field(default_factory=list)
    edges: List[AgentEdge] = field(default_factory=list)
    entry_node: Optional[str] = None
    exit_nodes: List[str] = field(default_factory=list)


@dataclass
class Agent:
    """Agent entity."""
    agent_id: str
    name: str
    description: str
    agent_type: str
    version: str = "1.0.0"
    status: str = "draft"
    config: Dict[str, Any] = field(default_factory=dict)
    workflow: Dict[str, Any] = field(default_factory=dict)
    llm_config: Dict[str, Any] = field(default_factory=dict)
    tools: List[str] = field(default_factory=list)
    hitl_config: Dict[str, Any] = field(default_factory=dict)
    created_by: str = ""
    created_at: str = ""
    updated_at: str = ""
    published_at: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class AgentManager:
    """
    Manages agent lifecycle including CRUD operations,
    versioning, and status transitions.
    """
    
    def __init__(self, db_facade=None):
        """
        Initialize AgentManager.
        
        Args:
            db_facade: Database facade for persistence
        """
        self.db_facade = db_facade
        self._agents: Dict[str, Agent] = {}  # In-memory cache
        logger.info("AgentManager initialized")
    
    def create_agent(self, name: str, description: str, agent_type: str,
                     created_by: str, config: Dict = None) -> Agent:
        """
        Create a new agent.
        
        Args:
            name: Agent name
            description: Agent description
            agent_type: Type of agent (react, plan_and_execute, etc.)
            created_by: User ID of creator
            config: Optional configuration
            
        Returns:
            Created Agent object
        """
        from abhikarta.utils.helpers import generate_id, get_timestamp
        
        agent_id = generate_id("agent")
        now = get_timestamp()
        
        agent = Agent(
            agent_id=agent_id,
            name=name,
            description=description,
            agent_type=agent_type,
            config=config or {},
            created_by=created_by,
            created_at=now,
            updated_at=now
        )
        
        # Store in database if available
        if self.db_facade:
            self._save_to_db(agent)
        
        # Cache in memory
        self._agents[agent_id] = agent
        
        logger.info(f"Created agent: {agent_id} - {name}")
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get agent by ID.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent object or None
        """
        # Check cache first
        if agent_id in self._agents:
            return self._agents[agent_id]
        
        # Load from database
        if self.db_facade:
            agent = self._load_from_db(agent_id)
            if agent:
                self._agents[agent_id] = agent
                return agent
        
        return None
    
    def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> Optional[Agent]:
        """
        Update an agent.
        
        Args:
            agent_id: Agent ID
            updates: Dictionary of fields to update
            
        Returns:
            Updated Agent or None
        """
        agent = self.get_agent(agent_id)
        if not agent:
            return None
        
        from abhikarta.utils.helpers import get_timestamp
        
        # Update allowed fields
        allowed_fields = ['name', 'description', 'config', 'workflow', 
                          'llm_config', 'tools', 'hitl_config', 'tags']
        
        for field_name in allowed_fields:
            if field_name in updates:
                setattr(agent, field_name, updates[field_name])
        
        agent.updated_at = get_timestamp()
        
        # Persist changes
        if self.db_facade:
            self._save_to_db(agent)
        
        logger.info(f"Updated agent: {agent_id}")
        return agent
    
    def update_workflow(self, agent_id: str, workflow: Dict[str, Any]) -> Optional[Agent]:
        """
        Update agent workflow (from visual designer).
        
        Args:
            agent_id: Agent ID
            workflow: Workflow definition with nodes and edges
            
        Returns:
            Updated Agent or None
        """
        return self.update_agent(agent_id, {'workflow': workflow})
    
    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            True if deleted
        """
        if agent_id in self._agents:
            del self._agents[agent_id]
        
        if self.db_facade:
            try:
                self.db_facade.execute(
                    "DELETE FROM agents WHERE agent_id = ?",
                    (agent_id,)
                )
                logger.info(f"Deleted agent: {agent_id}")
                return True
            except Exception as e:
                logger.error(f"Error deleting agent: {e}")
                return False
        
        return True
    
    def list_agents(self, status: str = None, agent_type: str = None,
                    created_by: str = None, limit: int = 100) -> List[Agent]:
        """
        List agents with optional filters.
        
        Args:
            status: Filter by status
            agent_type: Filter by agent type
            created_by: Filter by creator
            limit: Maximum results
            
        Returns:
            List of Agent objects
        """
        if self.db_facade:
            query = "SELECT * FROM agents WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
            if agent_type:
                query += " AND agent_type = ?"
                params.append(agent_type)
            if created_by:
                query += " AND created_by = ?"
                params.append(created_by)
            
            query += f" ORDER BY updated_at DESC LIMIT {limit}"
            
            rows = self.db_facade.fetch_all(query, tuple(params))
            return [self._row_to_agent(row) for row in rows]
        
        # Return from cache
        agents = list(self._agents.values())
        if status:
            agents = [a for a in agents if a.status == status]
        if agent_type:
            agents = [a for a in agents if a.agent_type == agent_type]
        if created_by:
            agents = [a for a in agents if a.created_by == created_by]
        
        return agents[:limit]
    
    def change_status(self, agent_id: str, new_status: str, 
                      changed_by: str) -> Optional[Agent]:
        """
        Change agent status with validation.
        
        Args:
            agent_id: Agent ID
            new_status: New status
            changed_by: User making the change
            
        Returns:
            Updated Agent or None
        """
        agent = self.get_agent(agent_id)
        if not agent:
            return None
        
        # Validate status transition
        valid_transitions = {
            'draft': ['testing', 'archived'],
            'testing': ['draft', 'pending_review', 'archived'],
            'pending_review': ['testing', 'approved', 'draft'],
            'approved': ['published', 'draft'],
            'published': ['deprecated', 'archived'],
            'deprecated': ['archived', 'published'],
            'archived': ['draft']
        }
        
        current_status = agent.status
        if new_status not in valid_transitions.get(current_status, []):
            logger.warning(f"Invalid status transition: {current_status} -> {new_status}")
            return None
        
        from abhikarta.utils.helpers import get_timestamp
        
        agent.status = new_status
        agent.updated_at = get_timestamp()
        
        if new_status == 'published':
            agent.published_at = get_timestamp()
        
        if self.db_facade:
            self._save_to_db(agent)
        
        logger.info(f"Agent {agent_id} status changed: {current_status} -> {new_status}")
        return agent
    
    def clone_agent(self, agent_id: str, new_name: str, 
                    created_by: str) -> Optional[Agent]:
        """
        Clone an existing agent.
        
        Args:
            agent_id: Source agent ID
            new_name: Name for the clone
            created_by: User creating the clone
            
        Returns:
            New Agent or None
        """
        source = self.get_agent(agent_id)
        if not source:
            return None
        
        return self.create_agent(
            name=new_name,
            description=f"Clone of {source.name}",
            agent_type=source.agent_type,
            created_by=created_by,
            config={
                **source.config,
                'workflow': source.workflow,
                'llm_config': source.llm_config,
                'tools': source.tools.copy(),
                'hitl_config': source.hitl_config
            }
        )
    
    def get_agent_types(self) -> List[Dict[str, str]]:
        """Get list of available agent types."""
        return [
            {"value": "react", "name": "ReAct Agent", 
             "description": "Reasoning and Acting agent that iterates until completion"},
            {"value": "plan_and_execute", "name": "Plan and Execute",
             "description": "Plans steps first, then executes them"},
            {"value": "tool_calling", "name": "Tool Calling",
             "description": "Direct tool invocation based on user intent"},
            {"value": "conversational", "name": "Conversational",
             "description": "Multi-turn conversational agent with memory"},
            {"value": "retrieval", "name": "Retrieval Augmented",
             "description": "RAG agent with document retrieval"},
            {"value": "custom", "name": "Custom Workflow",
             "description": "Custom workflow defined via visual designer"}
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        agents = self.list_agents(limit=10000)
        
        status_counts = {}
        type_counts = {}
        
        for agent in agents:
            status_counts[agent.status] = status_counts.get(agent.status, 0) + 1
            type_counts[agent.agent_type] = type_counts.get(agent.agent_type, 0) + 1
        
        return {
            'total': len(agents),
            'by_status': status_counts,
            'by_type': type_counts,
            'published': status_counts.get('published', 0),
            'draft': status_counts.get('draft', 0)
        }
    
    def _save_to_db(self, agent: Agent):
        """Save agent to database."""
        if not self.db_facade:
            return
        
        try:
            # Check if exists
            existing = self.db_facade.fetch_one(
                "SELECT agent_id FROM agents WHERE agent_id = ?",
                (agent.agent_id,)
            )
            
            if existing:
                # Update
                self.db_facade.execute("""
                    UPDATE agents SET 
                        name = ?, description = ?, agent_type = ?, version = ?,
                        status = ?, config = ?, created_by = ?, updated_at = ?
                    WHERE agent_id = ?
                """, (
                    agent.name, agent.description, agent.agent_type, agent.version,
                    agent.status, json.dumps(agent.config), agent.created_by,
                    agent.updated_at, agent.agent_id
                ))
            else:
                # Insert
                self.db_facade.execute("""
                    INSERT INTO agents (agent_id, name, description, agent_type, 
                        version, status, config, created_by, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    agent.agent_id, agent.name, agent.description, agent.agent_type,
                    agent.version, agent.status, json.dumps(agent.config),
                    agent.created_by, agent.created_at, agent.updated_at
                ))
        except Exception as e:
            logger.error(f"Error saving agent to DB: {e}")
    
    def _load_from_db(self, agent_id: str) -> Optional[Agent]:
        """Load agent from database."""
        if not self.db_facade:
            return None
        
        try:
            row = self.db_facade.fetch_one(
                "SELECT * FROM agents WHERE agent_id = ?",
                (agent_id,)
            )
            if row:
                return self._row_to_agent(row)
        except Exception as e:
            logger.error(f"Error loading agent from DB: {e}")
        
        return None
    
    def _row_to_agent(self, row: Dict) -> Agent:
        """Convert database row to Agent."""
        config = row.get('config', '{}')
        if isinstance(config, str):
            config = json.loads(config)
        
        return Agent(
            agent_id=row['agent_id'],
            name=row['name'],
            description=row.get('description', ''),
            agent_type=row['agent_type'],
            version=row.get('version', '1.0.0'),
            status=row.get('status', 'draft'),
            config=config,
            workflow=config.get('workflow', {}),
            llm_config=config.get('llm_config', {}),
            tools=config.get('tools', []),
            hitl_config=config.get('hitl_config', {}),
            created_by=row.get('created_by', ''),
            created_at=row.get('created_at', ''),
            updated_at=row.get('updated_at', ''),
            tags=config.get('tags', [])
        )
