"""
AI Org Task Engine - Task processing and delegation.

This module handles:
- Task submission to root node
- Task analysis and delegation decisions
- Subordinate response collection
- Response aggregation and summarization
- Task completion and reporting

Version: 1.4.5
Copyright © 2025-2030, All Rights Reserved
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import asyncio

from .models import (
    AIOrg, AINode, AITask, AIResponse, AIEventLog,
    TaskStatus, TaskPriority, ResponseType, DelegationStrategy, NodeType
)
from .db_ops import AIORGDBOps
from .prompts import AIORGPrompts

logger = logging.getLogger(__name__)


class TaskEngine:
    """
    Handles task processing through the AI Organization hierarchy.
    
    Responsibilities:
    - Submit tasks to org's root node
    - Process tasks at each node using AI
    - Delegate tasks to subordinates
    - Collect and aggregate responses
    - Synthesize summaries up the chain
    """
    
    def __init__(
        self,
        db_ops: AIORGDBOps,
        llm_facade=None,
        event_bus=None,
        notification_manager=None
    ):
        """
        Initialize TaskEngine.
        
        Args:
            db_ops: Database operations instance
            llm_facade: LLM facade for AI processing
            event_bus: Event bus for real-time updates
            notification_manager: Notification manager for alerts
        """
        self.db = db_ops
        self.llm = llm_facade
        self.event_bus = event_bus
        self.notifier = notification_manager
        self.prompts = AIORGPrompts()
    
    # =========================================================================
    # TASK SUBMISSION
    # =========================================================================
    
    async def submit_task(
        self,
        org_id: str,
        title: str,
        description: str,
        input_data: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        deadline: Optional[datetime] = None,
        submitted_by: str = "system"
    ) -> AITask:
        """
        Submit a new task to the organization's root node.
        
        This is the entry point for external task requests.
        The task will be assigned to the CEO node for processing.
        
        Args:
            org_id: Organization ID
            title: Task title
            description: Detailed task description
            input_data: Additional task input data
            priority: Task priority
            deadline: Optional deadline
            submitted_by: Who submitted the task
            
        Returns:
            Created AITask instance
        """
        # Get root node (CEO)
        root_node = self.db.get_root_node(org_id)
        if not root_node:
            raise ValueError(f"Organization {org_id} has no root node")
        
        # Create task
        task = AITask.create(
            org_id=org_id,
            assigned_node_id=root_node.node_id,
            title=title,
            description=description,
            input_data=input_data,
            priority=priority,
            deadline=deadline
        )
        
        # Add submission context
        task.context = {
            "submitted_by": submitted_by,
            "submitted_at": datetime.utcnow().isoformat()
        }
        
        if self.db.save_task(task):
            logger.info(f"Submitted task '{title}' to org {org_id}")
            
            # Log event
            self._log_event(org_id, "TASK_SUBMITTED", {
                "task_id": task.task_id,
                "title": title,
                "assigned_to": root_node.role_name
            }, target_node_id=root_node.node_id, task_id=task.task_id)
            
            # Publish event
            if self.event_bus:
                await self._publish_event(org_id, {
                    "type": "TASK_CREATED",
                    "task_id": task.task_id,
                    "node_id": root_node.node_id,
                    "title": title
                })
            
            # Start processing (in background)
            asyncio.create_task(self._process_task(task, root_node))
            
            return task
        else:
            raise Exception(f"Failed to save task: {title}")
    
    # =========================================================================
    # TASK PROCESSING
    # =========================================================================
    
    async def _process_task(self, task: AITask, node: AINode) -> None:
        """
        Process a task at a specific node.
        
        The node's AI agent analyzes the task and decides:
        1. Complete the task directly (for leaf nodes or simple tasks)
        2. Delegate to subordinates (for manager nodes)
        
        Args:
            task: Task to process
            node: Node processing the task
        """
        try:
            # Update task status
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.utcnow()
            self.db.save_task(task)
            
            # Update node's current task
            node.current_task_id = task.task_id
            self.db.save_node(node)
            
            # Log event
            self._log_event(task.org_id, "TASK_PROCESSING", {
                "task_id": task.task_id,
                "node_id": node.node_id
            }, source_node_id=node.node_id, task_id=task.task_id)
            
            # Get subordinates
            subordinates = self.db.get_child_nodes(node.node_id)
            
            # Analyze task
            analysis = await self._analyze_task(task, node, subordinates)
            
            if analysis.get("needs_delegation") and subordinates:
                # Delegate to subordinates
                await self._delegate_task(task, node, analysis, subordinates)
            else:
                # Complete directly
                response = await self._complete_task_directly(task, node)
                await self._finalize_task(task, node, response)
            
        except Exception as e:
            logger.error(f"Error processing task {task.task_id}: {e}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            self.db.save_task(task)
    
    async def _analyze_task(
        self,
        task: AITask,
        node: AINode,
        subordinates: List[AINode]
    ) -> Dict[str, Any]:
        """
        Analyze task and decide on action.
        
        Uses AI to determine if task should be:
        - Completed directly by this node
        - Delegated to subordinates
        """
        if not self.llm:
            # Without LLM, default behavior based on node type
            if node.role_type in [NodeType.ANALYST] or not subordinates:
                return {"needs_delegation": False}
            return {"needs_delegation": True, "delegation_plan": self._default_delegation(task, subordinates)}
        
        # Build prompt for LLM
        prompt = self.prompts.get_analysis_prompt(task, node, subordinates)
        
        try:
            # Call LLM
            response = await self.llm.generate_async(
                prompt=prompt,
                system_prompt=self.prompts.SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse response
            result = self._parse_llm_response(response)
            return result
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            # Fallback to default behavior
            if subordinates:
                return {"needs_delegation": True, "delegation_plan": self._default_delegation(task, subordinates)}
            return {"needs_delegation": False}
    
    def _default_delegation(self, task: AITask, subordinates: List[AINode]) -> Dict[str, Any]:
        """Create default delegation plan when LLM is unavailable."""
        subtasks = []
        for i, sub in enumerate(subordinates):
            subtasks.append({
                "title": f"{task.title} - Part {i+1}",
                "description": f"Analyze and provide findings for: {task.description}",
                "assigned_to": sub.node_id,
                "priority": task.priority.value
            })
        
        return {
            "strategy": "parallel",
            "subtasks": subtasks,
            "summary_instructions": "Synthesize all subordinate responses into a comprehensive report."
        }
    
    async def _delegate_task(
        self,
        task: AITask,
        node: AINode,
        analysis: Dict[str, Any],
        subordinates: List[AINode]
    ) -> None:
        """
        Delegate task to subordinates.
        
        Creates subtasks and assigns to appropriate subordinates.
        """
        delegation_plan = analysis.get("delegation_plan", {})
        subtasks_plan = delegation_plan.get("subtasks", [])
        strategy = DelegationStrategy(delegation_plan.get("strategy", "parallel"))
        
        # Update task status
        task.status = TaskStatus.DELEGATED
        task.delegation_strategy = strategy
        task.expected_responses = len(subtasks_plan)
        task.received_responses = 0
        self.db.save_task(task)
        
        # Create and save delegation response
        delegation_response = AIResponse.create(
            task_id=task.task_id,
            node_id=node.node_id,
            response_type=ResponseType.DELEGATION_PLAN,
            content=delegation_plan,
            summary=f"Delegating to {len(subtasks_plan)} subordinates using {strategy.value} strategy"
        )
        self.db.save_response(delegation_response)
        
        # Create subtasks
        created_subtasks = []
        sub_map = {s.node_id: s for s in subordinates}
        
        for subtask_plan in subtasks_plan:
            assigned_to = subtask_plan.get("assigned_to")
            if assigned_to not in sub_map:
                # Find appropriate subordinate
                assigned_to = subordinates[0].node_id if subordinates else None
            
            if not assigned_to:
                continue
            
            subtask = AITask.create(
                org_id=task.org_id,
                assigned_node_id=assigned_to,
                title=subtask_plan.get("title", f"Subtask of {task.title}"),
                description=subtask_plan.get("description", task.description),
                input_data=subtask_plan.get("input_data", task.input_data),
                parent_task_id=task.task_id,
                context={
                    "parent_task": task.title,
                    "parent_node": node.role_name,
                    "instructions": subtask_plan.get("instructions", "")
                },
                priority=TaskPriority(subtask_plan.get("priority", task.priority.value))
            )
            
            if self.db.save_task(subtask):
                created_subtasks.append(subtask)
                
                # Log delegation
                self._log_event(task.org_id, "TASK_DELEGATED", {
                    "parent_task_id": task.task_id,
                    "subtask_id": subtask.task_id,
                    "assigned_to": assigned_to
                }, source_node_id=node.node_id, target_node_id=assigned_to, task_id=subtask.task_id)
        
        # Update expected responses count
        task.expected_responses = len(created_subtasks)
        self.db.save_task(task)
        
        # Update task status to waiting
        task.status = TaskStatus.WAITING
        self.db.save_task(task)
        
        # Process subtasks
        if strategy == DelegationStrategy.PARALLEL:
            # Start all subtasks concurrently
            for subtask in created_subtasks:
                sub_node = sub_map.get(subtask.assigned_node_id)
                if sub_node:
                    asyncio.create_task(self._process_task(subtask, sub_node))
        else:
            # Sequential processing
            for subtask in created_subtasks:
                sub_node = sub_map.get(subtask.assigned_node_id)
                if sub_node:
                    await self._process_task(subtask, sub_node)
    
    async def _complete_task_directly(
        self,
        task: AITask,
        node: AINode
    ) -> AIResponse:
        """
        Complete task directly without delegation.
        
        The node processes the task using its AI agent.
        """
        if not self.llm:
            # Without LLM, create placeholder response
            return AIResponse.create(
                task_id=task.task_id,
                node_id=node.node_id,
                response_type=ResponseType.ANALYSIS,
                content={
                    "findings": f"Task '{task.title}' analyzed by {node.role_name}",
                    "recommendations": ["Further analysis recommended"],
                    "status": "completed_without_llm"
                },
                summary=f"Analysis completed by {node.role_name}",
                reasoning="Completed without LLM - placeholder response"
            )
        
        # Build prompt
        prompt = self.prompts.get_execution_prompt(task, node)
        
        try:
            # Call LLM
            response_text = await self.llm.generate_async(
                prompt=prompt,
                system_prompt=self.prompts.get_role_system_prompt(node),
                temperature=0.5,
                max_tokens=3000
            )
            
            # Parse response
            content = self._parse_llm_response(response_text)
            
            return AIResponse.create(
                task_id=task.task_id,
                node_id=node.node_id,
                response_type=ResponseType.ANALYSIS,
                content=content,
                summary=content.get("summary", f"Analysis by {node.role_name}"),
                reasoning=content.get("reasoning", "")
            )
            
        except Exception as e:
            logger.error(f"LLM execution failed: {e}")
            return AIResponse.create(
                task_id=task.task_id,
                node_id=node.node_id,
                response_type=ResponseType.ANALYSIS,
                content={"error": str(e), "partial_analysis": "Error during processing"},
                summary=f"Error during analysis: {e}"
            )
    
    # =========================================================================
    # RESPONSE AGGREGATION
    # =========================================================================
    
    async def receive_subordinate_response(
        self,
        parent_task_id: str,
        subtask: AITask,
        response: AIResponse
    ) -> None:
        """
        Handle response from a subordinate.
        
        When all subordinates have responded, triggers aggregation.
        """
        parent_task = self.db.get_task(parent_task_id)
        if not parent_task:
            logger.error(f"Parent task not found: {parent_task_id}")
            return
        
        # Update received count
        parent_task.received_responses += 1
        self.db.save_task(parent_task)
        
        # Log event
        self._log_event(parent_task.org_id, "RESPONSE_RECEIVED", {
            "parent_task_id": parent_task_id,
            "subtask_id": subtask.task_id,
            "received": parent_task.received_responses,
            "expected": parent_task.expected_responses
        }, task_id=parent_task_id)
        
        # Check if all responses received
        if parent_task.received_responses >= parent_task.expected_responses:
            # Get parent node
            parent_node = self.db.get_node(parent_task.assigned_node_id)
            if parent_node:
                await self._aggregate_responses(parent_task, parent_node)
    
    async def _aggregate_responses(
        self,
        task: AITask,
        node: AINode
    ) -> None:
        """
        Aggregate all subordinate responses into a summary.
        
        Uses AI to synthesize findings from all subordinates.
        """
        # Get all subtasks and their responses
        subtasks = self.db.get_subtasks(task.task_id)
        all_responses = []
        
        for subtask in subtasks:
            responses = self.db.get_task_responses(subtask.task_id)
            # Get the final response for each subtask
            if responses:
                final_response = responses[-1]  # Most recent
                all_responses.append({
                    "subtask_title": subtask.title,
                    "assigned_node": subtask.assigned_node_id,
                    "response": final_response.content,
                    "summary": final_response.summary
                })
        
        # Create aggregated response
        if not self.llm:
            # Without LLM, create simple aggregation
            summary_content = {
                "subordinate_count": len(all_responses),
                "subordinate_summaries": [r["summary"] for r in all_responses],
                "aggregated_findings": "Aggregation completed without LLM"
            }
            summary_text = f"Aggregated {len(all_responses)} subordinate responses"
        else:
            # Use LLM to synthesize
            prompt = self.prompts.get_aggregation_prompt(task, node, all_responses)
            
            try:
                response_text = await self.llm.generate_async(
                    prompt=prompt,
                    system_prompt=self.prompts.get_role_system_prompt(node),
                    temperature=0.3,
                    max_tokens=4000
                )
                
                summary_content = self._parse_llm_response(response_text)
                summary_text = summary_content.get("executive_summary", "Summary generated")
                
            except Exception as e:
                logger.error(f"LLM aggregation failed: {e}")
                summary_content = {"error": str(e), "raw_responses": all_responses}
                summary_text = f"Aggregation error: {e}"
        
        # Create summary response
        summary_response = AIResponse.create(
            task_id=task.task_id,
            node_id=node.node_id,
            response_type=ResponseType.SUMMARY,
            content=summary_content,
            summary=summary_text,
            reasoning=f"Synthesized from {len(all_responses)} subordinate responses"
        )
        self.db.save_response(summary_response)
        
        # Finalize the task
        await self._finalize_task(task, node, summary_response)
    
    # =========================================================================
    # TASK FINALIZATION
    # =========================================================================
    
    async def _finalize_task(
        self,
        task: AITask,
        node: AINode,
        response: AIResponse
    ) -> None:
        """
        Finalize a task and propagate up the chain.
        """
        # Save response
        self.db.save_response(response)
        
        # Update task
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.output_data = response.content
        self.db.save_task(task)
        
        # Clear node's current task
        node.current_task_id = None
        self.db.save_node(node)
        
        # Log completion
        self._log_event(task.org_id, "TASK_COMPLETED", {
            "task_id": task.task_id,
            "node_id": node.node_id,
            "response_id": response.response_id
        }, source_node_id=node.node_id, task_id=task.task_id)
        
        # Publish event
        if self.event_bus:
            await self._publish_event(task.org_id, {
                "type": "TASK_COMPLETED",
                "task_id": task.task_id,
                "node_id": node.node_id
            })
        
        # If this is a subtask, notify parent
        if task.parent_task_id:
            await self.receive_subordinate_response(
                task.parent_task_id,
                task,
                response
            )
        else:
            # This is the root task - send final notification
            await self._send_final_notification(task, node, response)
    
    async def _send_final_notification(
        self,
        task: AITask,
        node: AINode,
        response: AIResponse
    ) -> None:
        """
        Send final notification when root task completes.
        """
        if not self.notifier:
            logger.info(f"Task {task.task_id} completed - no notifier configured")
            return
        
        # Build notification content
        content = {
            "subject": f"AI Org Task Complete: {task.title}",
            "summary": response.summary,
            "task_id": task.task_id,
            "org_id": task.org_id,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        }
        
        # Send to human mirror
        if node.human_mirror.email:
            try:
                await self.notifier.send_email(
                    to=node.human_mirror.email,
                    subject=content["subject"],
                    body=self._format_email_body(task, response)
                )
            except Exception as e:
                logger.error(f"Failed to send email notification: {e}")
        
        if node.human_mirror.teams_id and "teams" in node.notification_channels:
            try:
                await self.notifier.send_teams_message(
                    channel=node.human_mirror.teams_id,
                    message=content
                )
            except Exception as e:
                logger.error(f"Failed to send Teams notification: {e}")
    
    def _format_email_body(self, task: AITask, response: AIResponse) -> str:
        """Format email body for task completion."""
        return f"""
AI Organization Task Completed

Task: {task.title}
Status: Completed
Completed At: {task.completed_at}

Summary:
{response.summary}

Detailed Findings:
{json.dumps(response.content, indent=2)}

---
This is an automated notification from Abhikarta AI Org.
"""
    
    # =========================================================================
    # UTILITIES
    # =========================================================================
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured format."""
        # Try to parse as JSON
        try:
            # Look for JSON block in response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                return json.loads(json_str)
            elif response_text.strip().startswith("{"):
                return json.loads(response_text)
            else:
                # Return as text content
                return {"text_response": response_text, "needs_delegation": False}
        except json.JSONDecodeError:
            return {"text_response": response_text, "needs_delegation": False}
    
    def _log_event(
        self,
        org_id: str,
        event_type: str,
        payload: Dict[str, Any],
        source_node_id: Optional[str] = None,
        target_node_id: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> None:
        """Log an event to database."""
        event = AIEventLog.create(
            org_id=org_id,
            event_type=event_type,
            payload=payload,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            task_id=task_id
        )
        self.db.save_event_log(event)
    
    async def _publish_event(self, org_id: str, event: Dict[str, Any]) -> None:
        """Publish event to event bus."""
        if self.event_bus:
            channel = f"aiorg:{org_id}"
            event["timestamp"] = datetime.utcnow().isoformat()
            await self.event_bus.publish_async(channel, event)
    
    # =========================================================================
    # TASK QUERIES
    # =========================================================================
    
    def get_task_tree(self, task_id: str) -> Dict[str, Any]:
        """
        Get complete task tree with subtasks and responses.
        
        Returns hierarchical structure showing task delegation.
        """
        task = self.db.get_task(task_id)
        if not task:
            return {}
        
        def build_tree(t: AITask) -> Dict[str, Any]:
            responses = self.db.get_task_responses(t.task_id)
            subtasks = self.db.get_subtasks(t.task_id)
            node = self.db.get_node(t.assigned_node_id)
            
            return {
                "task_id": t.task_id,
                "title": t.title,
                "status": t.status.value,
                "assigned_to": {
                    "node_id": t.assigned_node_id,
                    "role_name": node.role_name if node else "Unknown"
                },
                "responses": [r.to_dict() for r in responses],
                "subtasks": [build_tree(st) for st in subtasks]
            }
        
        return build_tree(task)
    
    def get_org_active_tasks(self, org_id: str) -> List[AITask]:
        """Get all active tasks for an organization."""
        tasks = []
        for status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.DELEGATED, TaskStatus.WAITING]:
            tasks.extend(self.db.get_org_tasks(org_id, status))
        return tasks
