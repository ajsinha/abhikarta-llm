# AI Org - Design Document

**Module:** AI Org (Artificial Intelligence Organization)  
**Version:** 1.4.8  
**Date:** December 2025  
**Author:** Abhikarta Team  
**Status:** Draft

---

## 1. Introduction

### 1.1 Purpose
This document provides the detailed technical design for the AI Org module, which enables creation and execution of AI-powered organizational structures within Abhikarta.

### 1.2 Scope
This design covers:
- Data models and database schema
- Core engine components
- Task execution flow
- HITL integration
- Event handling
- UI components
- API interfaces

### 1.3 Design Philosophy
The design follows these principles:
1. **Separation of Concerns**: Clear boundaries between org structure, execution, and UI
2. **Event-Driven**: Loosely coupled components communicating via events
3. **Human-Centric**: AI assists but humans remain in control
4. **Traceable**: Complete audit trail for compliance and debugging
5. **Extensible**: Easy to add new node types, notification channels

---

## 2. Data Model Design

### 2.1 Entity Relationship Diagram

```
┌─────────────────────┐     ┌─────────────────────┐
│      AIOrg          │     │      AIUser         │
├─────────────────────┤     ├─────────────────────┤
│ org_id (PK)         │     │ user_id (PK)        │
│ name                │     │ email               │
│ description         │     │ teams_id            │
│ status              │     │ slack_id            │
│ config              │     │ notification_prefs  │
│ created_by          │     └─────────────────────┘
│ created_at          │              │
│ updated_at          │              │ mapped_to
└─────────────────────┘              │
         │                           │
         │ has_many                  │
         ▼                           ▼
┌─────────────────────────────────────────────────┐
│                   AINode                         │
├─────────────────────────────────────────────────┤
│ node_id (PK)                                    │
│ org_id (FK) ─────────────────────────────────┐  │
│ parent_node_id (FK, nullable) - self ref     │  │
│ role_name                                    │  │
│ role_type (executive/manager/analyst/coord)  │  │
│ description                                  │  │
│ agent_config (JSON)                          │  │
│ human_mirror_id (FK to AIUser)               │  │
│ hitl_config (JSON)                           │  │
│ notification_config (JSON)                   │  │
│ position_x, position_y (for visual designer) │  │
│ status                                       │  │
│ created_at                                   │  │
│ updated_at                                   │  │
└─────────────────────────────────────────────────┘
         │
         │ receives/creates
         ▼
┌─────────────────────────────────────────────────┐
│                   AITask                         │
├─────────────────────────────────────────────────┤
│ task_id (PK)                                    │
│ org_id (FK)                                     │
│ parent_task_id (FK, nullable) - self ref       │
│ assigned_node_id (FK to AINode)                │
│ title                                          │
│ description                                    │
│ priority (low/medium/high/critical)            │
│ status (pending/in_progress/delegated/...)     │
│ input_data (JSON)                              │
│ output_data (JSON)                             │
│ context (JSON) - from parent                   │
│ deadline                                       │
│ started_at                                     │
│ completed_at                                   │
│ created_at                                     │
│ updated_at                                     │
└─────────────────────────────────────────────────┘
         │
         │ generates
         ▼
┌─────────────────────────────────────────────────┐
│                 AIResponse                       │
├─────────────────────────────────────────────────┤
│ response_id (PK)                                │
│ task_id (FK)                                    │
│ node_id (FK)                                    │
│ response_type (analysis/delegation/summary/...) │
│ content (JSON)                                  │
│ summary (TEXT)                                  │
│ confidence_score                               │
│ is_human_modified                              │
│ original_ai_content (JSON) - if modified       │
│ created_at                                     │
│ updated_at                                     │
└─────────────────────────────────────────────────┘
         │
         │ may_have
         ▼
┌─────────────────────────────────────────────────┐
│               AIHITLAction                       │
├─────────────────────────────────────────────────┤
│ action_id (PK)                                  │
│ org_id (FK)                                     │
│ node_id (FK)                                    │
│ task_id (FK, nullable)                          │
│ response_id (FK, nullable)                      │
│ user_id (FK) - human who took action           │
│ action_type (view/approve/reject/override/...)  │
│ original_content (JSON)                         │
│ modified_content (JSON)                         │
│ reason (TEXT)                                   │
│ created_at                                      │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│               AIEventLog                         │
├─────────────────────────────────────────────────┤
│ event_id (PK)                                   │
│ org_id (FK)                                     │
│ event_type                                      │
│ source_node_id (FK, nullable)                   │
│ target_node_id (FK, nullable)                   │
│ task_id (FK, nullable)                          │
│ payload (JSON)                                  │
│ created_at                                      │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│            AINotificationLog                     │
├─────────────────────────────────────────────────┤
│ notification_id (PK)                            │
│ org_id (FK)                                     │
│ node_id (FK)                                    │
│ channel (email/teams/slack/app)                 │
│ recipient                                       │
│ subject                                         │
│ content (TEXT)                                  │
│ status (pending/sent/failed)                    │
│ error_message (nullable)                        │
│ sent_at                                         │
│ created_at                                      │
└─────────────────────────────────────────────────┘
```

### 2.2 Detailed Schema

#### 2.2.1 AIOrg Table
```sql
CREATE TABLE ai_orgs (
    org_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'draft',  -- draft, active, paused, archived
    config JSON,  -- org-level configuration
    event_bus_channel VARCHAR(100),  -- dedicated event channel
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_orgs_status ON ai_orgs(status);
CREATE INDEX idx_ai_orgs_created_by ON ai_orgs(created_by);
```

#### 2.2.2 AINode Table
```sql
CREATE TABLE ai_nodes (
    node_id VARCHAR(36) PRIMARY KEY,
    org_id VARCHAR(36) NOT NULL REFERENCES ai_orgs(org_id),
    parent_node_id VARCHAR(36) REFERENCES ai_nodes(node_id),
    
    -- Role Definition
    role_name VARCHAR(100) NOT NULL,
    role_type VARCHAR(20) NOT NULL,  -- executive, manager, analyst, coordinator
    description TEXT,
    
    -- Agent Configuration
    agent_id VARCHAR(36),  -- Reference to existing agent
    agent_config JSON,  -- Inline agent configuration
    
    -- Human Mirror
    human_name VARCHAR(255),
    human_email VARCHAR(255),
    human_teams_id VARCHAR(255),
    human_slack_id VARCHAR(255),
    
    -- HITL Configuration
    hitl_enabled BOOLEAN DEFAULT FALSE,
    hitl_approval_required BOOLEAN DEFAULT FALSE,
    hitl_review_delegation BOOLEAN DEFAULT FALSE,
    hitl_timeout_hours INTEGER DEFAULT 24,
    hitl_auto_proceed BOOLEAN DEFAULT TRUE,
    
    -- Notification Configuration
    notification_channels JSON,  -- ["email", "teams", "slack"]
    notification_triggers JSON,  -- Which events trigger notifications
    
    -- Visual Designer Position
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',  -- active, paused, disabled
    current_task_id VARCHAR(36),  -- Currently processing task
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_nodes_org ON ai_nodes(org_id);
CREATE INDEX idx_ai_nodes_parent ON ai_nodes(parent_node_id);
CREATE INDEX idx_ai_nodes_role_type ON ai_nodes(role_type);
```

#### 2.2.3 AITask Table
```sql
CREATE TABLE ai_tasks (
    task_id VARCHAR(36) PRIMARY KEY,
    org_id VARCHAR(36) NOT NULL REFERENCES ai_orgs(org_id),
    parent_task_id VARCHAR(36) REFERENCES ai_tasks(task_id),
    assigned_node_id VARCHAR(36) NOT NULL REFERENCES ai_nodes(node_id),
    
    -- Task Definition
    title VARCHAR(500) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'medium',  -- low, medium, high, critical
    
    -- Task Data
    input_data JSON,  -- Original task input
    output_data JSON,  -- Final output/response
    context JSON,  -- Context from parent task
    attachments JSON,  -- File references
    
    -- Execution State
    status VARCHAR(30) DEFAULT 'pending',
    -- pending, in_progress, delegated, waiting, completed, failed, human_override
    
    delegation_strategy VARCHAR(20),  -- parallel, sequential, conditional
    expected_responses INTEGER DEFAULT 0,  -- Number of subtasks
    received_responses INTEGER DEFAULT 0,
    
    -- Timing
    deadline TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Error Handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_tasks_org ON ai_tasks(org_id);
CREATE INDEX idx_ai_tasks_parent ON ai_tasks(parent_task_id);
CREATE INDEX idx_ai_tasks_node ON ai_tasks(assigned_node_id);
CREATE INDEX idx_ai_tasks_status ON ai_tasks(status);
```

#### 2.2.4 AIResponse Table
```sql
CREATE TABLE ai_responses (
    response_id VARCHAR(36) PRIMARY KEY,
    task_id VARCHAR(36) NOT NULL REFERENCES ai_tasks(task_id),
    node_id VARCHAR(36) NOT NULL REFERENCES ai_nodes(node_id),
    
    -- Response Content
    response_type VARCHAR(30) NOT NULL,
    -- analysis, delegation_plan, subordinate_response, summary, final_output
    
    content JSON NOT NULL,  -- Structured response content
    summary TEXT,  -- Human-readable summary
    reasoning TEXT,  -- AI reasoning/thought process
    
    -- Quality Metrics
    confidence_score FLOAT,
    quality_score FLOAT,
    
    -- HITL Modifications
    is_human_modified BOOLEAN DEFAULT FALSE,
    original_ai_content JSON,  -- Preserved if modified
    modification_reason TEXT,
    modified_by VARCHAR(100),
    modified_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_responses_task ON ai_responses(task_id);
CREATE INDEX idx_ai_responses_node ON ai_responses(node_id);
CREATE INDEX idx_ai_responses_type ON ai_responses(response_type);
```

#### 2.2.5 AIHITLAction Table
```sql
CREATE TABLE ai_hitl_actions (
    action_id VARCHAR(36) PRIMARY KEY,
    org_id VARCHAR(36) NOT NULL REFERENCES ai_orgs(org_id),
    node_id VARCHAR(36) NOT NULL REFERENCES ai_nodes(node_id),
    task_id VARCHAR(36) REFERENCES ai_tasks(task_id),
    response_id VARCHAR(36) REFERENCES ai_responses(response_id),
    
    -- Action Details
    user_id VARCHAR(100) NOT NULL,  -- Human who took action
    action_type VARCHAR(30) NOT NULL,
    -- view, approve, reject, override, pause, resume, escalate, message
    
    -- Content
    original_content JSON,
    modified_content JSON,
    reason TEXT,
    message TEXT,
    
    -- Metadata
    ip_address VARCHAR(50),
    user_agent TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_hitl_org ON ai_hitl_actions(org_id);
CREATE INDEX idx_ai_hitl_node ON ai_hitl_actions(node_id);
CREATE INDEX idx_ai_hitl_user ON ai_hitl_actions(user_id);
CREATE INDEX idx_ai_hitl_task ON ai_hitl_actions(task_id);
```

---

## 3. Component Design

### 3.1 Core Components Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AI Org Module                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  OrgManager  │  │ TaskEngine   │  │ HITLManager  │              │
│  │              │  │              │  │              │              │
│  │ - create_org │  │ - submit     │  │ - queue_for  │              │
│  │ - add_node   │  │ - delegate   │  │   _review    │              │
│  │ - remove_node│  │ - aggregate  │  │ - approve    │              │
│  │ - activate   │  │ - complete   │  │ - override   │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                  │                      │
│         └────────────────┼──────────────────┘                      │
│                          │                                          │
│                          ▼                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      AINodeActor                              │  │
│  │  Each node in the org is represented by an actor that:        │  │
│  │  - Receives tasks from parent                                 │  │
│  │  - Processes using AI agent                                   │  │
│  │  - Delegates to children if needed                            │  │
│  │  - Aggregates child responses                                 │  │
│  │  - Reports back to parent                                     │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                          │                                          │
│         ┌────────────────┼────────────────┐                        │
│         ▼                ▼                ▼                        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐               │
│  │ EventBus     │ │ Notifier     │ │ Persistence  │               │
│  │              │ │              │ │              │               │
│  │ - publish    │ │ - email      │ │ - save       │               │
│  │ - subscribe  │ │ - teams      │ │ - load       │               │
│  │ - broadcast  │ │ - slack      │ │ - query      │               │
│  └──────────────┘ └──────────────┘ └──────────────┘               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 OrgManager Class

```python
class OrgManager:
    """
    Manages AI Organization lifecycle and structure.
    """
    
    def __init__(self, db_facade, agent_manager, event_bus):
        self.db = db_facade
        self.agent_manager = agent_manager
        self.event_bus = event_bus
        self.active_orgs: Dict[str, 'AIOrg'] = {}
    
    def create_org(
        self,
        name: str,
        description: str,
        created_by: str,
        config: Optional[Dict] = None
    ) -> AIOrg:
        """Create a new AI Organization."""
        pass
    
    def load_org(self, org_id: str) -> AIOrg:
        """Load an org from database and initialize actors."""
        pass
    
    def activate_org(self, org_id: str) -> bool:
        """Activate an org, starting all node actors."""
        pass
    
    def pause_org(self, org_id: str) -> bool:
        """Pause all activities in an org."""
        pass
    
    def add_node(
        self,
        org_id: str,
        role_name: str,
        role_type: str,
        parent_node_id: Optional[str],
        agent_config: Dict,
        human_mirror: Dict,
        hitl_config: Dict
    ) -> AINode:
        """Add a node to the org chart."""
        pass
    
    def remove_node(self, node_id: str) -> bool:
        """Remove a node (must have no active tasks)."""
        pass
    
    def restructure(
        self,
        node_id: str,
        new_parent_id: str
    ) -> bool:
        """Move a node to a new parent."""
        pass
    
    def export_to_json(self, org_id: str) -> Dict:
        """Export org chart as JSON."""
        pass
    
    def import_from_json(
        self,
        json_data: Dict,
        created_by: str
    ) -> AIOrg:
        """Import org chart from JSON."""
        pass
```

### 3.3 TaskEngine Class

```python
class TaskEngine:
    """
    Handles task submission, delegation, and aggregation.
    """
    
    def __init__(
        self,
        db_facade,
        org_manager: OrgManager,
        llm_facade,
        event_bus
    ):
        self.db = db_facade
        self.org_manager = org_manager
        self.llm = llm_facade
        self.event_bus = event_bus
    
    async def submit_task(
        self,
        org_id: str,
        title: str,
        description: str,
        input_data: Dict,
        priority: str = "medium",
        deadline: Optional[datetime] = None
    ) -> AITask:
        """
        Submit a new task to the org's root node.
        This is the entry point for external requests.
        """
        pass
    
    async def process_task(
        self,
        task: AITask,
        node: AINode
    ) -> AIResponse:
        """
        Process a task at a specific node.
        The node's AI agent analyzes and decides next action.
        """
        pass
    
    async def delegate_task(
        self,
        parent_task: AITask,
        delegation_plan: Dict,
        node: AINode
    ) -> List[AITask]:
        """
        Delegate task to subordinates based on plan.
        Creates subtasks and assigns to child nodes.
        """
        pass
    
    async def aggregate_responses(
        self,
        parent_task: AITask,
        responses: List[AIResponse],
        node: AINode
    ) -> AIResponse:
        """
        Aggregate subordinate responses into summary.
        Uses AI to synthesize findings.
        """
        pass
    
    async def complete_task(
        self,
        task: AITask,
        response: AIResponse
    ) -> None:
        """
        Mark task as complete and notify parent.
        """
        pass
    
    async def escalate_to_human(
        self,
        task: AITask,
        node: AINode,
        reason: str
    ) -> None:
        """
        Escalate task to human for intervention.
        """
        pass
```

### 3.4 AINodeActor Class

```python
class AINodeActor(BaseActor):
    """
    Actor representing a node in the AI Org.
    Each node runs as an independent actor that:
    - Receives messages from parent/children
    - Processes tasks using AI agent
    - Maintains its own state
    """
    
    def __init__(
        self,
        node_id: str,
        node_config: AINode,
        task_engine: TaskEngine,
        hitl_manager: 'HITLManager',
        notifier: 'OrgNotifier'
    ):
        super().__init__(f"aiorg_node_{node_id}")
        self.node_id = node_id
        self.config = node_config
        self.task_engine = task_engine
        self.hitl_manager = hitl_manager
        self.notifier = notifier
        
        self.current_task: Optional[AITask] = None
        self.pending_subtasks: Dict[str, AITask] = {}
        self.received_responses: Dict[str, AIResponse] = {}
    
    async def receive_task(
        self,
        task: AITask,
        context: Dict
    ) -> None:
        """
        Receive a task from parent node or external.
        """
        self.current_task = task
        
        # HITL check: review before processing?
        if self.config.hitl_review_delegation:
            await self.hitl_manager.queue_for_review(
                self.node_id,
                task,
                review_type="task_received"
            )
            return  # Will continue when approved
        
        await self._process_task(task)
    
    async def _process_task(self, task: AITask) -> None:
        """
        Internal task processing logic.
        """
        # Get AI agent decision
        response = await self.task_engine.process_task(task, self.config)
        
        if response.response_type == "delegation_plan":
            # Need to delegate to subordinates
            await self._delegate_to_subordinates(task, response)
        else:
            # Can complete directly
            await self._complete_and_report(task, response)
    
    async def _delegate_to_subordinates(
        self,
        task: AITask,
        delegation_plan: AIResponse
    ) -> None:
        """
        Create subtasks and assign to children.
        """
        subtasks = await self.task_engine.delegate_task(
            task,
            delegation_plan.content,
            self.config
        )
        
        self.pending_subtasks = {st.task_id: st for st in subtasks}
        
        # Update task status
        task.status = "delegated"
        task.expected_responses = len(subtasks)
        task.received_responses = 0
        await self.task_engine.db.update_task(task)
        
        # Publish delegation events
        for subtask in subtasks:
            await self.event_bus.publish(f"aiorg:{task.org_id}", {
                "type": "TASK_DELEGATED",
                "parent_node": self.node_id,
                "child_node": subtask.assigned_node_id,
                "task_id": subtask.task_id
            })
    
    async def receive_subordinate_response(
        self,
        subtask_id: str,
        response: AIResponse
    ) -> None:
        """
        Receive response from a subordinate.
        """
        self.received_responses[subtask_id] = response
        
        # Update parent task
        self.current_task.received_responses += 1
        await self.task_engine.db.update_task(self.current_task)
        
        # Check if all responses received
        if len(self.received_responses) >= len(self.pending_subtasks):
            await self._aggregate_and_report()
    
    async def _aggregate_and_report(self) -> None:
        """
        Aggregate all subordinate responses and report to parent.
        """
        summary = await self.task_engine.aggregate_responses(
            self.current_task,
            list(self.received_responses.values()),
            self.config
        )
        
        # HITL check: approval before sending?
        if self.config.hitl_approval_required:
            await self.hitl_manager.queue_for_review(
                self.node_id,
                self.current_task,
                review_type="response_approval",
                content=summary
            )
            return
        
        await self._complete_and_report(self.current_task, summary)
    
    async def _complete_and_report(
        self,
        task: AITask,
        response: AIResponse
    ) -> None:
        """
        Complete task and send response to parent.
        """
        await self.task_engine.complete_task(task, response)
        
        # Send notification
        await self.notifier.send_completion_notification(
            self.config,
            task,
            response
        )
        
        # If not root, report to parent
        if self.config.parent_node_id:
            await self.event_bus.publish(f"aiorg:{task.org_id}", {
                "type": "RESPONSE_RECEIVED",
                "from_node": self.node_id,
                "to_node": self.config.parent_node_id,
                "task_id": task.parent_task_id,
                "response_id": response.response_id
            })
        else:
            # Root node - task complete
            await self._finalize_org_task(task, response)
    
    async def _finalize_org_task(
        self,
        task: AITask,
        response: AIResponse
    ) -> None:
        """
        Finalize task at root level - send final report.
        """
        await self.notifier.send_final_report(
            self.config,
            task,
            response
        )
        
        await self.event_bus.publish(f"aiorg:{task.org_id}", {
            "type": "ORG_TASK_COMPLETE",
            "task_id": task.task_id,
            "response_id": response.response_id
        })
```

### 3.5 HITLManager Class

```python
class HITLManager:
    """
    Manages Human-in-the-Loop interactions.
    """
    
    def __init__(
        self,
        db_facade,
        event_bus,
        notifier: 'OrgNotifier'
    ):
        self.db = db_facade
        self.event_bus = event_bus
        self.notifier = notifier
        
        # Queue of items awaiting human review
        self.review_queue: Dict[str, HITLQueueItem] = {}
    
    async def queue_for_review(
        self,
        node_id: str,
        task: AITask,
        review_type: str,
        content: Optional[AIResponse] = None
    ) -> str:
        """
        Queue an item for human review.
        """
        queue_item = HITLQueueItem(
            item_id=str(uuid.uuid4()),
            node_id=node_id,
            task_id=task.task_id,
            review_type=review_type,
            content=content,
            status="pending",
            created_at=datetime.utcnow()
        )
        
        self.review_queue[queue_item.item_id] = queue_item
        await self.db.save_hitl_queue_item(queue_item)
        
        # Notify human
        node = await self.db.get_node(node_id)
        await self.notifier.send_hitl_notification(node, queue_item)
        
        return queue_item.item_id
    
    async def get_pending_reviews(
        self,
        user_email: str
    ) -> List[HITLQueueItem]:
        """
        Get all pending reviews for a human user.
        """
        return await self.db.get_pending_hitl_items(user_email)
    
    async def approve(
        self,
        item_id: str,
        user_id: str,
        comment: Optional[str] = None
    ) -> bool:
        """
        Approve a pending item.
        """
        item = self.review_queue.get(item_id)
        if not item:
            item = await self.db.get_hitl_queue_item(item_id)
        
        # Log action
        await self._log_action(
            item,
            user_id,
            "approve",
            comment=comment
        )
        
        # Continue processing
        await self._continue_processing(item)
        
        return True
    
    async def override(
        self,
        item_id: str,
        user_id: str,
        new_content: Dict,
        reason: str
    ) -> bool:
        """
        Override AI content with human content.
        """
        item = await self.db.get_hitl_queue_item(item_id)
        
        # Create modified response
        original = item.content
        modified = AIResponse(
            response_id=str(uuid.uuid4()),
            task_id=item.task_id,
            node_id=item.node_id,
            response_type=original.response_type if original else "human_override",
            content=new_content,
            is_human_modified=True,
            original_ai_content=original.content if original else None,
            modification_reason=reason,
            modified_by=user_id
        )
        
        await self.db.save_response(modified)
        
        # Log action
        await self._log_action(
            item,
            user_id,
            "override",
            original_content=original.content if original else None,
            modified_content=new_content,
            reason=reason
        )
        
        # Continue with modified content
        item.content = modified
        await self._continue_processing(item)
        
        return True
    
    async def pause_node(
        self,
        node_id: str,
        user_id: str,
        reason: str
    ) -> bool:
        """
        Pause a node's activities.
        """
        node = await self.db.get_node(node_id)
        node.status = "paused"
        await self.db.update_node(node)
        
        await self._log_action(
            HITLQueueItem(node_id=node_id),
            user_id,
            "pause",
            reason=reason
        )
        
        return True
    
    async def _continue_processing(
        self,
        item: 'HITLQueueItem'
    ) -> None:
        """
        Continue processing after HITL approval.
        """
        # Publish event to resume node processing
        await self.event_bus.publish(f"aiorg:{item.org_id}", {
            "type": "HITL_APPROVED",
            "node_id": item.node_id,
            "task_id": item.task_id,
            "review_type": item.review_type,
            "content": item.content.to_dict() if item.content else None
        })
    
    async def _log_action(
        self,
        item: 'HITLQueueItem',
        user_id: str,
        action_type: str,
        **kwargs
    ) -> None:
        """
        Log HITL action for audit trail.
        """
        action = AIHITLAction(
            action_id=str(uuid.uuid4()),
            org_id=item.org_id,
            node_id=item.node_id,
            task_id=item.task_id,
            user_id=user_id,
            action_type=action_type,
            **kwargs
        )
        await self.db.save_hitl_action(action)
```

---

## 4. Task Execution Flow

### 4.1 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        TASK EXECUTION FLOW                               │
└─────────────────────────────────────────────────────────────────────────┘

External Request
      │
      ▼
┌─────────────┐
│ Task Input  │ ───► User submits task via UI or webhook
│   Screen    │
└─────┬───────┘
      │
      ▼
┌─────────────┐
│    CEO      │ ───► Root node receives task
│   (Root)    │
└─────┬───────┘
      │
      │ AI Analysis: "This requires multiple specialists"
      │
      ▼
┌─────────────────────────────────────────┐
│         DELEGATION PLAN CREATED          │
│                                          │
│  Subtask 1: Technical Analysis → PM-Tech │
│  Subtask 2: Market Analysis → PM-Market  │
│  Subtask 3: Financial Analysis → CFO     │
└─────────────────────────────────────────┘
      │
      │ Parallel Delegation
      ├─────────────────┬─────────────────┐
      ▼                 ▼                 ▼
┌──────────┐     ┌──────────┐     ┌──────────┐
│ PM-Tech  │     │PM-Market │     │   CFO    │
└────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │
     │ Delegate       │ Delegate       │ Self-complete
     ▼                ▼                ▼
┌─────────┐    ┌─────────┐      ┌─────────────┐
│Analyst 1│    │Analyst 3│      │ Financial   │
│Analyst 2│    │Analyst 4│      │  Analysis   │
└────┬────┘    └────┬────┘      │  Response   │
     │              │           └──────┬──────┘
     │ Responses    │ Responses        │
     ▼              ▼                  │
┌─────────┐    ┌─────────┐            │
│PM-Tech  │    │PM-Market│            │
│ Summary │    │ Summary │            │
└────┬────┘    └────┬────┘            │
     │              │                  │
     └──────────────┼──────────────────┘
                    │
                    ▼
           ┌───────────────┐
           │   CEO (Root)  │
           │  Aggregation  │
           └───────┬───────┘
                   │
                   │ All responses received
                   ▼
           ┌───────────────┐
           │    FINAL      │
           │    SUMMARY    │
           └───────┬───────┘
                   │
                   │ Notify human mirror
                   ▼
           ┌───────────────┐
           │  Email/Teams  │
           │ Notification  │
           └───────────────┘
```

### 4.2 HITL Intervention Flow

```
Normal Flow
     │
     ▼
┌────────────────┐
│ AI Generates   │
│   Response     │
└───────┬────────┘
        │
        │ HITL Enabled?
        ▼
    ┌───────┐
    │ Yes   │───────────────────────────┐
    └───┬───┘                           │
        │                               │
        │ No                            ▼
        │                    ┌──────────────────┐
        ▼                    │ Queue for Review │
┌────────────────┐           └────────┬─────────┘
│  Continue to   │                    │
│    Parent      │           ┌────────▼─────────┐
└────────────────┘           │ Notify Human     │
                             │ (Email/Teams)    │
                             └────────┬─────────┘
                                      │
                             ┌────────▼─────────┐
                             │ Human Reviews    │
                             │ in HITL Dashboard│
                             └────────┬─────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
            ┌───────────┐    ┌───────────┐     ┌───────────┐
            │  Approve  │    │  Override │     │  Reject   │
            └─────┬─────┘    └─────┬─────┘     └─────┬─────┘
                  │                │                 │
                  │                │                 │
                  ▼                ▼                 ▼
            ┌───────────┐    ┌───────────┐     ┌───────────┐
            │ Continue  │    │Use Human  │     │ Re-process│
            │ with AI   │    │ Content   │     │ or Fail   │
            │ Response  │    │           │     │           │
            └───────────┘    └───────────┘     └───────────┘
```

---

## 5. UI Design

### 5.1 Page Structure

```
/aiorg/                         - AI Org Home/List
/aiorg/create                   - Create New Org
/aiorg/<org_id>                 - View Org Details
/aiorg/<org_id>/designer        - Visual Org Designer
/aiorg/<org_id>/tasks           - Task Management
/aiorg/<org_id>/tasks/<task_id> - Task Details
/aiorg/<org_id>/monitor         - Real-time Monitor
/aiorg/hitl                     - HITL Dashboard (user-specific)
/aiorg/hitl/<item_id>           - HITL Review Screen
```

### 5.2 Visual Designer Wireframe

```
┌─────────────────────────────────────────────────────────────────────┐
│  AI Org Designer: Project Analysis Team                    [Save]   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────┐                        │
│  │              [Toolbar]                   │                        │
│  │ [Add Node] [Delete] [Connect] [Zoom +/-] │                        │
│  └─────────────────────────────────────────┘                        │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                                                              │   │
│  │                       ┌──────────┐                          │   │
│  │                       │   CEO    │                          │   │
│  │                       │ J. Smith │                          │   │
│  │                       └────┬─────┘                          │   │
│  │                            │                                │   │
│  │            ┌───────────────┼───────────────┐                │   │
│  │            │               │               │                │   │
│  │      ┌─────▼────┐   ┌─────▼────┐   ┌─────▼────┐            │   │
│  │      │ PM-Tech  │   │PM-Market │   │   CFO    │            │   │
│  │      │ A. Kumar │   │ B. Chen  │   │ C. Wilson│            │   │
│  │      └────┬─────┘   └────┬─────┘   └──────────┘            │   │
│  │           │              │                                  │   │
│  │     ┌─────┴────┐   ┌─────┴────┐                            │   │
│  │     │          │   │          │                            │   │
│  │  ┌──▼──┐  ┌──▼──┐ ┌──▼──┐  ┌──▼──┐                        │   │
│  │  │Dev 1│  │Dev 2│ │Mkt 1│  │Mkt 2│                        │   │
│  │  └─────┘  └─────┘ └─────┘  └─────┘                        │   │
│  │                                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Properties: PM-Tech                                         │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │ Role Name:    [Project Manager - Technical    ]             │   │
│  │ Role Type:    [Manager                      ▼]              │   │
│  │ Description:  [Manages technical analysis team ]            │   │
│  │                                                              │   │
│  │ Human Mirror:                                                │   │
│  │ Name:         [Anish Kumar                   ]              │   │
│  │ Email:        [anish.kumar@company.com       ]              │   │
│  │ Teams ID:     [anish.kumar                   ]              │   │
│  │                                                              │   │
│  │ AI Agent:     [Technical Analyst Agent      ▼]              │   │
│  │                                                              │   │
│  │ HITL Settings:                                               │   │
│  │ [✓] Enable HITL                                             │   │
│  │ [ ] Require approval before sending                         │   │
│  │ [✓] Review delegation decisions                             │   │
│  │ Timeout: [24] hours                                         │   │
│  │                                                              │   │
│  │ Notifications: [✓] Email [✓] Teams [ ] Slack               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.3 HITL Dashboard Wireframe

```
┌─────────────────────────────────────────────────────────────────────┐
│  HITL Dashboard - Welcome, Anish Kumar                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  My AI Mirrors:                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Project Analysis Team                                         │  │
│  │ Role: PM-Tech | Status: 🟢 Active | Tasks: 3 in progress     │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │ Research Organization                                         │  │
│  │ Role: Lead Researcher | Status: 🟡 Awaiting Review | Tasks: 1│  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ⚠️ Items Requiring Review (2):                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 🔴 Response Approval Required                     [Review]    │  │
│  │ Org: Project Analysis Team                                    │  │
│  │ Task: Analyze API architecture feasibility                    │  │
│  │ Waiting since: 2 hours ago                                    │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │ 🟡 Delegation Review                              [Review]    │  │
│  │ Org: Research Organization                                    │  │
│  │ Task: Market size research for APAC region                    │  │
│  │ Waiting since: 30 minutes ago                                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Recent Activity:                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ ✓ Task completed: "Competitor analysis" - 1 hour ago         │  │
│  │ ✓ Delegated to: Dev1, Dev2 - 2 hours ago                     │  │
│  │ ⚡ Received task: "Technical feasibility" - 3 hours ago       │  │
│  │ ✓ Summary approved by you - Yesterday                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. API Design

### 6.1 REST Endpoints

```
# Org Management
POST   /api/aiorg                      - Create org
GET    /api/aiorg                      - List orgs
GET    /api/aiorg/<org_id>             - Get org details
PUT    /api/aiorg/<org_id>             - Update org
DELETE /api/aiorg/<org_id>             - Delete org
POST   /api/aiorg/<org_id>/activate    - Activate org
POST   /api/aiorg/<org_id>/pause       - Pause org

# Node Management
POST   /api/aiorg/<org_id>/nodes       - Add node
GET    /api/aiorg/<org_id>/nodes       - List nodes
GET    /api/aiorg/<org_id>/nodes/<id>  - Get node
PUT    /api/aiorg/<org_id>/nodes/<id>  - Update node
DELETE /api/aiorg/<org_id>/nodes/<id>  - Delete node

# Task Management
POST   /api/aiorg/<org_id>/tasks       - Submit task
GET    /api/aiorg/<org_id>/tasks       - List tasks
GET    /api/aiorg/<org_id>/tasks/<id>  - Get task details
GET    /api/aiorg/<org_id>/tasks/<id>/tree - Get task tree

# HITL
GET    /api/aiorg/hitl/pending         - Get pending reviews
GET    /api/aiorg/hitl/<item_id>       - Get review item
POST   /api/aiorg/hitl/<item_id>/approve   - Approve
POST   /api/aiorg/hitl/<item_id>/override  - Override
POST   /api/aiorg/hitl/<item_id>/reject    - Reject

# Export/Import
GET    /api/aiorg/<org_id>/export      - Export as JSON
POST   /api/aiorg/import               - Import from JSON
```

---

## 7. Security Considerations

### 7.1 Access Control
- Org access controlled by creator and explicit grants
- HITL actions require node's human mirror or admin
- Sensitive data encrypted at rest

### 7.2 Audit Logging
- All actions logged with user, timestamp, IP
- Immutable audit trail for compliance
- Log retention configurable

### 7.3 Data Protection
- PII minimization in logs
- Secure notification channels
- API key protection for external integrations

---

## 8. Traceability Matrix

| Requirement | Component | Database Table | UI Page |
|-------------|-----------|----------------|---------|
| REQ-001 | OrgManager.create_org | ai_orgs | /aiorg/create |
| REQ-006 | OrgManager.add_node | ai_nodes | /aiorg/designer |
| REQ-015 | TaskEngine.submit_task | ai_tasks | /aiorg/tasks |
| REQ-030 | HITLManager | ai_hitl_actions | /aiorg/hitl |
| REQ-034 | OrgNotifier | ai_notification_log | N/A |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2025-12-30 | Abhikarta Team | Initial draft |

