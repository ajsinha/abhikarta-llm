"""
AI Org Data Models - Core entities for AI Organization.

This module defines the data structures for:
- AI Organizations (org charts)
- AI Nodes (positions in org chart)
- AI Tasks (work items)
- AI Responses (task outputs)
- HITL Actions (human interventions)

Version: 1.4.7
Copyright © 2025-2030, All Rights Reserved
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid


def _format_timestamp(dt: Optional[datetime]) -> Optional[str]:
    """
    Format datetime for SQLite storage.
    Uses space separator for Python 3.14 compatibility.
    """
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S.%f')


def _parse_timestamp(val: Optional[str]) -> Optional[datetime]:
    """
    Parse timestamp string to datetime.
    Handles both ISO format (T separator) and SQLite format (space separator).
    """
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    try:
        # Handle ISO format with T
        val = val.replace('T', ' ')
        # Try with microseconds first
        if '.' in val:
            return datetime.strptime(val, '%Y-%m-%d %H:%M:%S.%f')
        else:
            return datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
    except Exception:
        return datetime.now(timezone.utc)


class OrgStatus(Enum):
    """Status of an AI Organization."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class NodeType(Enum):
    """Type of node in the org chart."""
    EXECUTIVE = "executive"    # CEO, CTO, CFO - top level
    MANAGER = "manager"        # Department heads, PMs - middle level
    ANALYST = "analyst"        # Individual contributors - leaf level
    COORDINATOR = "coordinator"  # Cross-functional coordinators


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DELEGATED = "delegated"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    HUMAN_OVERRIDE = "human_override"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Priority level of a task."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResponseType(Enum):
    """Type of response from a node."""
    ANALYSIS = "analysis"
    DELEGATION_PLAN = "delegation_plan"
    SUBORDINATE_RESPONSE = "subordinate_response"
    SUMMARY = "summary"
    FINAL_OUTPUT = "final_output"
    HUMAN_OVERRIDE = "human_override"


class HITLActionType(Enum):
    """Type of HITL action."""
    VIEW = "view"
    APPROVE = "approve"
    REJECT = "reject"
    OVERRIDE = "override"
    PAUSE = "pause"
    RESUME = "resume"
    ESCALATE = "escalate"
    MESSAGE = "message"


class DelegationStrategy(Enum):
    """Strategy for delegating tasks to subordinates."""
    PARALLEL = "parallel"      # All at once
    SEQUENTIAL = "sequential"  # One at a time
    CONDITIONAL = "conditional"  # Based on conditions


@dataclass
class AIOrg:
    """
    Represents an AI Organization (org chart).
    
    An AI Org is a hierarchical structure of AI nodes that can
    receive tasks, delegate to subordinates, and aggregate results.
    """
    org_id: str
    name: str
    description: str
    status: OrgStatus
    config: Dict[str, Any]
    event_bus_channel: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    
    # Transient fields (not persisted directly)
    nodes: List['AINode'] = field(default_factory=list)
    root_node_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        created_by: str,
        config: Optional[Dict[str, Any]] = None
    ) -> 'AIOrg':
        """Create a new AI Organization."""
        org_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        return cls(
            org_id=org_id,
            name=name,
            description=description,
            status=OrgStatus.DRAFT,
            config=config or {},
            event_bus_channel=f"aiorg:{org_id}",
            created_by=created_by,
            created_at=now,
            updated_at=now
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for persistence."""
        return {
            "org_id": self.org_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "config": self.config,
            "event_bus_channel": self.event_bus_channel,
            "created_by": self.created_by,
            "created_at": _format_timestamp(self.created_at),
            "updated_at": _format_timestamp(self.updated_at),
            "root_node_id": self.root_node_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIOrg':
        """Create from dictionary."""
        return cls(
            org_id=data["org_id"],
            name=data["name"],
            description=data.get("description", ""),
            status=OrgStatus(data.get("status", "draft")),
            config=data.get("config", {}),
            event_bus_channel=data.get("event_bus_channel", f"aiorg:{data['org_id']}"),
            created_by=data.get("created_by", "system"),
            created_at=_parse_timestamp(data.get("created_at")) or datetime.now(timezone.utc),
            updated_at=_parse_timestamp(data.get("updated_at")) or datetime.now(timezone.utc),
            root_node_id=data.get("root_node_id")
        )


@dataclass
class HITLConfig:
    """Configuration for Human-in-the-Loop at a node."""
    enabled: bool = False
    approval_required: bool = False
    review_delegation: bool = False
    timeout_hours: int = 24
    auto_proceed: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "approval_required": self.approval_required,
            "review_delegation": self.review_delegation,
            "timeout_hours": self.timeout_hours,
            "auto_proceed": self.auto_proceed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HITLConfig':
        if not data:
            return cls()
        return cls(
            enabled=data.get("enabled", False),
            approval_required=data.get("approval_required", False),
            review_delegation=data.get("review_delegation", False),
            timeout_hours=data.get("timeout_hours", 24),
            auto_proceed=data.get("auto_proceed", True)
        )


@dataclass
class HumanMirror:
    """Human employee represented by an AI node."""
    name: str
    email: str
    teams_id: Optional[str] = None
    slack_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "email": self.email,
            "teams_id": self.teams_id,
            "slack_id": self.slack_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HumanMirror':
        if not data:
            return cls(name="", email="")
        return cls(
            name=data.get("name", ""),
            email=data.get("email", ""),
            teams_id=data.get("teams_id"),
            slack_id=data.get("slack_id")
        )


@dataclass
class AINode:
    """
    Represents a position/role in the AI Organization.
    
    Each node has:
    - Role definition (name, type, description)
    - AI agent configuration
    - Human mirror (the person this AI represents)
    - HITL settings
    - Notification preferences
    """
    node_id: str
    org_id: str
    parent_node_id: Optional[str]
    
    # Role definition
    role_name: str
    role_type: NodeType
    description: str
    
    # Agent configuration
    agent_id: Optional[str]  # Reference to existing agent
    agent_config: Dict[str, Any]  # Inline configuration
    
    # Human mirror
    human_mirror: HumanMirror
    
    # HITL configuration
    hitl_config: HITLConfig
    
    # Notification channels
    notification_channels: List[str]  # ["email", "teams", "slack"]
    notification_triggers: List[str]  # Events that trigger notifications
    
    # Visual designer position
    position_x: int
    position_y: int
    
    # Status
    status: str  # active, paused, disabled
    current_task_id: Optional[str]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Transient
    children: List['AINode'] = field(default_factory=list)
    
    @classmethod
    def create(
        cls,
        org_id: str,
        role_name: str,
        role_type: NodeType,
        description: str,
        parent_node_id: Optional[str] = None,
        agent_config: Optional[Dict[str, Any]] = None,
        human_mirror: Optional[HumanMirror] = None,
        hitl_config: Optional[HITLConfig] = None,
        notification_channels: Optional[List[str]] = None,
        position_x: int = 0,
        position_y: int = 0
    ) -> 'AINode':
        """Create a new AI Node."""
        node_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        return cls(
            node_id=node_id,
            org_id=org_id,
            parent_node_id=parent_node_id,
            role_name=role_name,
            role_type=role_type,
            description=description,
            agent_id=None,
            agent_config=agent_config or {},
            human_mirror=human_mirror or HumanMirror(name="", email=""),
            hitl_config=hitl_config or HITLConfig(),
            notification_channels=notification_channels or ["email"],
            notification_triggers=["task_completed", "hitl_required"],
            position_x=position_x,
            position_y=position_y,
            status="active",
            current_task_id=None,
            created_at=now,
            updated_at=now
        )
    
    def is_root(self) -> bool:
        """Check if this is the root node (CEO)."""
        return self.parent_node_id is None
    
    def is_leaf(self) -> bool:
        """Check if this is a leaf node (no children)."""
        return len(self.children) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for persistence."""
        return {
            "node_id": self.node_id,
            "org_id": self.org_id,
            "parent_node_id": self.parent_node_id,
            "role_name": self.role_name,
            "role_type": self.role_type.value,
            "description": self.description,
            "agent_id": self.agent_id,
            "agent_config": self.agent_config,
            "human_name": self.human_mirror.name,
            "human_email": self.human_mirror.email,
            "human_teams_id": self.human_mirror.teams_id,
            "human_slack_id": self.human_mirror.slack_id,
            "hitl_enabled": self.hitl_config.enabled,
            "hitl_approval_required": self.hitl_config.approval_required,
            "hitl_review_delegation": self.hitl_config.review_delegation,
            "hitl_timeout_hours": self.hitl_config.timeout_hours,
            "hitl_auto_proceed": self.hitl_config.auto_proceed,
            "notification_channels": self.notification_channels,
            "notification_triggers": self.notification_triggers,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "status": self.status,
            "current_task_id": self.current_task_id,
            "created_at": _format_timestamp(self.created_at),
            "updated_at": _format_timestamp(self.updated_at)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AINode':
        """Create from dictionary."""
        human_mirror = HumanMirror(
            name=data.get("human_name", ""),
            email=data.get("human_email", ""),
            teams_id=data.get("human_teams_id"),
            slack_id=data.get("human_slack_id")
        )
        hitl_config = HITLConfig(
            enabled=data.get("hitl_enabled", False),
            approval_required=data.get("hitl_approval_required", False),
            review_delegation=data.get("hitl_review_delegation", False),
            timeout_hours=data.get("hitl_timeout_hours", 24),
            auto_proceed=data.get("hitl_auto_proceed", True)
        )
        return cls(
            node_id=data["node_id"],
            org_id=data["org_id"],
            parent_node_id=data.get("parent_node_id"),
            role_name=data["role_name"],
            role_type=NodeType(data.get("role_type", "analyst")),
            description=data.get("description", ""),
            agent_id=data.get("agent_id"),
            agent_config=data.get("agent_config", {}),
            human_mirror=human_mirror,
            hitl_config=hitl_config,
            notification_channels=data.get("notification_channels", ["email"]),
            notification_triggers=data.get("notification_triggers", []),
            position_x=data.get("position_x", 0),
            position_y=data.get("position_y", 0),
            status=data.get("status", "active"),
            current_task_id=data.get("current_task_id"),
            created_at=_parse_timestamp(data.get("created_at")) or datetime.now(timezone.utc),
            updated_at=_parse_timestamp(data.get("updated_at")) or datetime.now(timezone.utc)
        )


@dataclass
class AITask:
    """
    Represents a task assigned to a node.
    
    Tasks flow through the org chart:
    - Created at root or delegated from parent
    - Can be decomposed into subtasks
    - Generate responses when completed
    """
    task_id: str
    org_id: str
    parent_task_id: Optional[str]
    assigned_node_id: str
    
    # Task definition
    title: str
    description: str
    priority: TaskPriority
    
    # Task data
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    context: Dict[str, Any]  # Context from parent
    attachments: List[str]  # File references
    
    # Execution state
    status: TaskStatus
    delegation_strategy: Optional[DelegationStrategy]
    expected_responses: int
    received_responses: int
    
    # Timing
    deadline: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    # Error handling
    error_message: Optional[str]
    retry_count: int
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Transient
    subtasks: List['AITask'] = field(default_factory=list)
    responses: List['AIResponse'] = field(default_factory=list)
    
    @classmethod
    def create(
        cls,
        org_id: str,
        assigned_node_id: str,
        title: str,
        description: str,
        input_data: Dict[str, Any],
        parent_task_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        deadline: Optional[datetime] = None
    ) -> 'AITask':
        """Create a new task."""
        task_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        return cls(
            task_id=task_id,
            org_id=org_id,
            parent_task_id=parent_task_id,
            assigned_node_id=assigned_node_id,
            title=title,
            description=description,
            priority=priority,
            input_data=input_data,
            output_data=None,
            context=context or {},
            attachments=[],
            status=TaskStatus.PENDING,
            delegation_strategy=None,
            expected_responses=0,
            received_responses=0,
            deadline=deadline,
            started_at=None,
            completed_at=None,
            error_message=None,
            retry_count=0,
            created_at=now,
            updated_at=now
        )
    
    def is_root_task(self) -> bool:
        """Check if this is a root task (no parent)."""
        return self.parent_task_id is None
    
    def all_responses_received(self) -> bool:
        """Check if all expected responses have been received."""
        return self.received_responses >= self.expected_responses
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for persistence."""
        return {
            "task_id": self.task_id,
            "org_id": self.org_id,
            "parent_task_id": self.parent_task_id,
            "assigned_node_id": self.assigned_node_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "context": self.context,
            "attachments": self.attachments,
            "status": self.status.value,
            "delegation_strategy": self.delegation_strategy.value if self.delegation_strategy else None,
            "expected_responses": self.expected_responses,
            "received_responses": self.received_responses,
            "deadline": _format_timestamp(self.deadline),
            "started_at": _format_timestamp(self.started_at),
            "completed_at": _format_timestamp(self.completed_at),
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "created_at": _format_timestamp(self.created_at),
            "updated_at": _format_timestamp(self.updated_at)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AITask':
        """Create from dictionary."""
        return cls(
            task_id=data["task_id"],
            org_id=data["org_id"],
            parent_task_id=data.get("parent_task_id"),
            assigned_node_id=data["assigned_node_id"],
            title=data["title"],
            description=data.get("description", ""),
            priority=TaskPriority(data.get("priority", "medium")),
            input_data=data.get("input_data", {}),
            output_data=data.get("output_data"),
            context=data.get("context", {}),
            attachments=data.get("attachments", []),
            status=TaskStatus(data.get("status", "pending")),
            delegation_strategy=DelegationStrategy(data["delegation_strategy"]) if data.get("delegation_strategy") else None,
            expected_responses=data.get("expected_responses", 0),
            received_responses=data.get("received_responses", 0),
            deadline=_parse_timestamp(data.get("deadline")),
            started_at=_parse_timestamp(data.get("started_at")),
            completed_at=_parse_timestamp(data.get("completed_at")),
            error_message=data.get("error_message"),
            retry_count=data.get("retry_count", 0),
            created_at=_parse_timestamp(data.get("created_at")) or datetime.now(timezone.utc),
            updated_at=_parse_timestamp(data.get("updated_at")) or datetime.now(timezone.utc)
        )


@dataclass
class AIResponse:
    """
    Represents a response from a node for a task.
    
    Responses contain:
    - Analysis, delegation plans, summaries, or final outputs
    - Quality metrics
    - HITL modification tracking
    """
    response_id: str
    task_id: str
    node_id: str
    
    # Response content
    response_type: ResponseType
    content: Dict[str, Any]
    summary: str
    reasoning: str  # AI thought process
    
    # Quality metrics
    confidence_score: Optional[float]
    quality_score: Optional[float]
    
    # HITL tracking
    is_human_modified: bool
    original_ai_content: Optional[Dict[str, Any]]
    modification_reason: Optional[str]
    modified_by: Optional[str]
    modified_at: Optional[datetime]
    
    # Timestamp
    created_at: datetime
    
    @classmethod
    def create(
        cls,
        task_id: str,
        node_id: str,
        response_type: ResponseType,
        content: Dict[str, Any],
        summary: str = "",
        reasoning: str = "",
        confidence_score: Optional[float] = None
    ) -> 'AIResponse':
        """Create a new response."""
        response_id = str(uuid.uuid4())
        return cls(
            response_id=response_id,
            task_id=task_id,
            node_id=node_id,
            response_type=response_type,
            content=content,
            summary=summary,
            reasoning=reasoning,
            confidence_score=confidence_score,
            quality_score=None,
            is_human_modified=False,
            original_ai_content=None,
            modification_reason=None,
            modified_by=None,
            modified_at=None,
            created_at=datetime.now(timezone.utc)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for persistence."""
        return {
            "response_id": self.response_id,
            "task_id": self.task_id,
            "node_id": self.node_id,
            "response_type": self.response_type.value,
            "content": self.content,
            "summary": self.summary,
            "reasoning": self.reasoning,
            "confidence_score": self.confidence_score,
            "quality_score": self.quality_score,
            "is_human_modified": self.is_human_modified,
            "original_ai_content": self.original_ai_content,
            "modification_reason": self.modification_reason,
            "modified_by": self.modified_by,
            "modified_at": _format_timestamp(self.modified_at),
            "created_at": _format_timestamp(self.created_at)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIResponse':
        """Create from dictionary."""
        return cls(
            response_id=data["response_id"],
            task_id=data["task_id"],
            node_id=data["node_id"],
            response_type=ResponseType(data.get("response_type", "analysis")),
            content=data.get("content", {}),
            summary=data.get("summary", ""),
            reasoning=data.get("reasoning", ""),
            confidence_score=data.get("confidence_score"),
            quality_score=data.get("quality_score"),
            is_human_modified=data.get("is_human_modified", False),
            original_ai_content=data.get("original_ai_content"),
            modification_reason=data.get("modification_reason"),
            modified_by=data.get("modified_by"),
            modified_at=_parse_timestamp(data.get("modified_at")),
            created_at=_parse_timestamp(data.get("created_at")) or datetime.now(timezone.utc)
        )


@dataclass
class AIHITLAction:
    """
    Records a Human-in-the-Loop action.
    
    All HITL interventions are logged for audit trail.
    """
    action_id: str
    org_id: str
    node_id: str
    task_id: Optional[str]
    response_id: Optional[str]
    
    # Action details
    user_id: str
    action_type: HITLActionType
    
    # Content
    original_content: Optional[Dict[str, Any]]
    modified_content: Optional[Dict[str, Any]]
    reason: Optional[str]
    message: Optional[str]
    
    # Metadata
    ip_address: Optional[str]
    user_agent: Optional[str]
    
    # Timestamp
    created_at: datetime
    
    @classmethod
    def create(
        cls,
        org_id: str,
        node_id: str,
        user_id: str,
        action_type: HITLActionType,
        task_id: Optional[str] = None,
        response_id: Optional[str] = None,
        original_content: Optional[Dict[str, Any]] = None,
        modified_content: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None,
        message: Optional[str] = None
    ) -> 'AIHITLAction':
        """Create a new HITL action."""
        action_id = str(uuid.uuid4())
        return cls(
            action_id=action_id,
            org_id=org_id,
            node_id=node_id,
            task_id=task_id,
            response_id=response_id,
            user_id=user_id,
            action_type=action_type,
            original_content=original_content,
            modified_content=modified_content,
            reason=reason,
            message=message,
            ip_address=None,
            user_agent=None,
            created_at=datetime.now(timezone.utc)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for persistence."""
        return {
            "action_id": self.action_id,
            "org_id": self.org_id,
            "node_id": self.node_id,
            "task_id": self.task_id,
            "response_id": self.response_id,
            "user_id": self.user_id,
            "action_type": self.action_type.value,
            "original_content": self.original_content,
            "modified_content": self.modified_content,
            "reason": self.reason,
            "message": self.message,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": _format_timestamp(self.created_at)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIHITLAction':
        """Create from dictionary."""
        return cls(
            action_id=data["action_id"],
            org_id=data["org_id"],
            node_id=data["node_id"],
            task_id=data.get("task_id"),
            response_id=data.get("response_id"),
            user_id=data["user_id"],
            action_type=HITLActionType(data.get("action_type", "view")),
            original_content=data.get("original_content"),
            modified_content=data.get("modified_content"),
            reason=data.get("reason"),
            message=data.get("message"),
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
            created_at=_parse_timestamp(data.get("created_at")) or datetime.now(timezone.utc)
        )


@dataclass
class AIEventLog:
    """Log entry for org events."""
    event_id: str
    org_id: str
    event_type: str
    source_node_id: Optional[str]
    target_node_id: Optional[str]
    task_id: Optional[str]
    payload: Dict[str, Any]
    created_at: datetime
    
    @classmethod
    def create(
        cls,
        org_id: str,
        event_type: str,
        payload: Dict[str, Any],
        source_node_id: Optional[str] = None,
        target_node_id: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> 'AIEventLog':
        """Create a new event log entry."""
        return cls(
            event_id=str(uuid.uuid4()),
            org_id=org_id,
            event_type=event_type,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            task_id=task_id,
            payload=payload,
            created_at=datetime.now(timezone.utc)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "org_id": self.org_id,
            "event_type": self.event_type,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "task_id": self.task_id,
            "payload": self.payload,
            "created_at": _format_timestamp(self.created_at)
        }


@dataclass
class HITLQueueItem:
    """Item in the HITL review queue."""
    item_id: str
    org_id: str
    node_id: str
    task_id: str
    review_type: str  # task_received, response_approval, delegation_review
    content: Optional[AIResponse]
    status: str  # pending, approved, rejected, overridden, timeout
    created_at: datetime
    expires_at: Optional[datetime]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_id": self.item_id,
            "org_id": self.org_id,
            "node_id": self.node_id,
            "task_id": self.task_id,
            "review_type": self.review_type,
            "content": self.content.to_dict() if self.content else None,
            "status": self.status,
            "created_at": _format_timestamp(self.created_at),
            "expires_at": _format_timestamp(self.expires_at)
        }
