"""
Workflow Data Models

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha | Email: ajsinha@gmail.com

Legal Notice: This module and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited without explicit 
written permission from the copyright holder.

Patent Pending: Certain architectural patterns and implementations described in this module 
may be subject to patent applications.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid


class WorkflowStatus(Enum):
    """Workflow status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class ExecutionStatus(Enum):
    """Execution status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeExecutionStatus(Enum):
    """Node execution status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class TaskType(Enum):
    """Human task type enumeration"""
    APPROVAL = "approval"
    INPUT = "input"
    REVIEW = "review"


class TaskStatus(Enum):
    """Human task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    TIMEOUT = "timeout"
    ESCALATED = "escalated"


class NodeType(Enum):
    """Node type enumeration"""
    LLM = "llm"
    TOOL = "tool"
    HUMAN = "human"
    CONDITIONAL = "conditional"
    PARALLEL = "parallel"
    ITERATOR = "iterator"
    START = "start"
    END = "end"
    SUBWORKFLOW = "subworkflow"


@dataclass
class WorkflowNode:
    """Workflow node definition"""
    node_id: str
    node_type: str
    name: str
    description: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    input_mappings: Dict[str, str] = field(default_factory=dict)
    output_mappings: Dict[str, str] = field(default_factory=dict)
    timeout: int = 300  # seconds
    retry_count: int = 0
    retry_backoff: str = "exponential"
    error_behavior: str = "fail"  # fail, skip, retry
    condition: Optional[str] = None


@dataclass
class WorkflowEdge:
    """Workflow edge definition"""
    source: str
    target: str
    condition: Optional[str] = None
    priority: int = 0


@dataclass
class WorkflowDefinition:
    """Complete workflow definition"""
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Workflow:
    """Workflow entity"""
    workflow_id: str
    name: str
    description: str
    version: str
    definition_json: Dict[str, Any]
    status: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    tags: Optional[List[str]] = None

    @staticmethod
    def generate_id() -> str:
        """Generate a new workflow ID"""
        return str(uuid.uuid4())


@dataclass
class WorkflowExecution:
    """Workflow execution entity"""
    execution_id: str
    workflow_id: str
    workflow_version: str
    status: str
    triggered_by: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    input_parameters: Optional[Dict[str, Any]] = None
    output_results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_metadata: Optional[Dict[str, Any]] = None

    @staticmethod
    def generate_id() -> str:
        """Generate a new execution ID"""
        return str(uuid.uuid4())


@dataclass
class NodeExecution:
    """Node execution entity"""
    node_execution_id: str
    execution_id: str
    node_id: str
    node_type: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    iteration_index: Optional[int] = None

    @staticmethod
    def generate_id() -> str:
        """Generate a new node execution ID"""
        return str(uuid.uuid4())


@dataclass
class HumanTask:
    """Human task entity"""
    task_id: str
    execution_id: str
    node_execution_id: str
    assigned_to: str
    task_type: str
    status: str
    created_at: datetime
    responded_at: Optional[datetime] = None
    response_data: Optional[Dict[str, Any]] = None
    comments: Optional[str] = None
    timeout_at: Optional[datetime] = None

    @staticmethod
    def generate_id() -> str:
        """Generate a new task ID"""
        return str(uuid.uuid4())


@dataclass
class WorkflowVariable:
    """Workflow variable entity"""
    variable_id: str
    execution_id: str
    variable_name: str
    variable_value: Any
    scope: str
    node_execution_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @staticmethod
    def generate_id() -> str:
        """Generate a new variable ID"""
        return str(uuid.uuid4())


@dataclass
class AuditLog:
    """Audit log entity"""
    log_id: str
    execution_id: str
    timestamp: datetime
    log_level: str
    message: str
    context_data: Optional[Dict[str, Any]] = None
    source: Optional[str] = None

    @staticmethod
    def generate_id() -> str:
        """Generate a new log ID"""
        return str(uuid.uuid4())
