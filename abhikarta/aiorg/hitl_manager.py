"""
AI Org HITL Manager - Human-in-the-Loop management.

This module handles:
- Queueing items for human review
- Processing approvals, rejections, overrides
- Managing HITL timeouts
- Audit logging of all human interventions

Version: 1.4.5
Copyright © 2025-2030, All Rights Reserved
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import uuid

from .models import (
    AINode, AITask, AIResponse, AIHITLAction, HITLQueueItem,
    HITLActionType, ResponseType
)
from .db_ops import AIORGDBOps

logger = logging.getLogger(__name__)


class HITLManager:
    """
    Manages Human-in-the-Loop interactions.
    
    Responsibilities:
    - Queue items for human review
    - Process human decisions (approve, reject, override)
    - Handle timeouts and auto-proceed logic
    - Maintain audit trail
    - Send notifications for pending reviews
    """
    
    def __init__(
        self,
        db_ops: AIORGDBOps,
        event_bus=None,
        notification_manager=None
    ):
        """
        Initialize HITLManager.
        
        Args:
            db_ops: Database operations instance
            event_bus: Event bus for real-time updates
            notification_manager: For sending HITL alerts
        """
        self.db = db_ops
        self.event_bus = event_bus
        self.notifier = notification_manager
    
    # =========================================================================
    # QUEUE MANAGEMENT
    # =========================================================================
    
    async def queue_for_review(
        self,
        node: AINode,
        task: AITask,
        review_type: str,
        content: Optional[AIResponse] = None
    ) -> HITLQueueItem:
        """
        Queue an item for human review.
        
        Args:
            node: Node requesting review
            task: Associated task
            review_type: Type of review needed
                - 'task_received': Review incoming task before processing
                - 'response_approval': Review response before sending to parent
                - 'delegation_review': Review delegation plan before executing
            content: Optional content to review (e.g., AI-generated response)
            
        Returns:
            Created queue item
        """
        # Calculate expiration
        timeout_hours = node.hitl_config.timeout_hours
        expires_at = datetime.utcnow() + timedelta(hours=timeout_hours)
        
        item = HITLQueueItem(
            item_id=str(uuid.uuid4()),
            org_id=task.org_id,
            node_id=node.node_id,
            task_id=task.task_id,
            review_type=review_type,
            content=content,
            status="pending",
            created_at=datetime.utcnow(),
            expires_at=expires_at
        )
        
        # Save to database
        self._save_queue_item(item)
        
        logger.info(f"Queued HITL review: {review_type} for node {node.role_name}")
        
        # Send notification to human mirror
        await self._notify_review_required(node, task, item)
        
        # Publish event
        if self.event_bus:
            await self.event_bus.publish_async(f"aiorg:{task.org_id}", {
                "type": "HITL_REQUIRED",
                "item_id": item.item_id,
                "node_id": node.node_id,
                "task_id": task.task_id,
                "review_type": review_type,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return item
    
    def get_pending_reviews(self, user_email: str) -> List[Dict[str, Any]]:
        """
        Get all pending HITL reviews for a user.
        
        Args:
            user_email: Email of the human mirror
            
        Returns:
            List of pending review items with context
        """
        # Get nodes where user is human mirror
        nodes = self.db.get_nodes_by_email(user_email)
        node_ids = [n.node_id for n in nodes]
        
        if not node_ids:
            return []
        
        # Get pending items for these nodes
        items = self._get_pending_items_for_nodes(node_ids)
        
        # Enrich with context
        enriched = []
        for item in items:
            node = self.db.get_node(item.node_id)
            task = self.db.get_task(item.task_id)
            org = self.db.get_org(item.org_id)
            
            enriched.append({
                "item": item.to_dict(),
                "node": {
                    "node_id": node.node_id,
                    "role_name": node.role_name,
                    "role_type": node.role_type.value
                } if node else None,
                "task": {
                    "task_id": task.task_id,
                    "title": task.title,
                    "status": task.status.value
                } if task else None,
                "org": {
                    "org_id": org.org_id,
                    "name": org.name
                } if org else None,
                "time_remaining": self._calculate_time_remaining(item)
            })
        
        return enriched
    
    def get_queue_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific queue item with full context."""
        item = self._get_queue_item(item_id)
        if not item:
            return None
        
        node = self.db.get_node(item.node_id)
        task = self.db.get_task(item.task_id)
        org = self.db.get_org(item.org_id)
        
        # Get responses if available
        responses = self.db.get_task_responses(item.task_id) if task else []
        
        return {
            "item": item.to_dict(),
            "node": node.to_dict() if node else None,
            "task": task.to_dict() if task else None,
            "org": org.to_dict() if org else None,
            "responses": [r.to_dict() for r in responses],
            "ai_content": item.content.to_dict() if item.content else None
        }
    
    # =========================================================================
    # HITL ACTIONS
    # =========================================================================
    
    async def approve(
        self,
        item_id: str,
        user_id: str,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Approve a pending item.
        
        The original AI content proceeds as-is.
        
        Args:
            item_id: Queue item ID
            user_id: User approving
            comment: Optional comment
            
        Returns:
            Result dict with status
        """
        item = self._get_queue_item(item_id)
        if not item:
            return {"success": False, "error": "Item not found"}
        
        if item.status != "pending":
            return {"success": False, "error": f"Item is not pending (status: {item.status})"}
        
        # Log the action
        action = AIHITLAction.create(
            org_id=item.org_id,
            node_id=item.node_id,
            user_id=user_id,
            action_type=HITLActionType.APPROVE,
            task_id=item.task_id,
            original_content=item.content.to_dict() if item.content else None,
            message=comment
        )
        self.db.save_hitl_action(action)
        
        # Update item status
        item.status = "approved"
        self._save_queue_item(item)
        
        logger.info(f"HITL approved: {item_id} by {user_id}")
        
        # Trigger continuation
        await self._continue_after_hitl(item, approved=True)
        
        return {"success": True, "action_id": action.action_id}
    
    async def reject(
        self,
        item_id: str,
        user_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Reject a pending item.
        
        The task may be re-processed or marked as failed.
        
        Args:
            item_id: Queue item ID
            user_id: User rejecting
            reason: Reason for rejection
            
        Returns:
            Result dict with status
        """
        item = self._get_queue_item(item_id)
        if not item:
            return {"success": False, "error": "Item not found"}
        
        if item.status != "pending":
            return {"success": False, "error": f"Item is not pending (status: {item.status})"}
        
        # Log the action
        action = AIHITLAction.create(
            org_id=item.org_id,
            node_id=item.node_id,
            user_id=user_id,
            action_type=HITLActionType.REJECT,
            task_id=item.task_id,
            original_content=item.content.to_dict() if item.content else None,
            reason=reason
        )
        self.db.save_hitl_action(action)
        
        # Update item status
        item.status = "rejected"
        self._save_queue_item(item)
        
        logger.info(f"HITL rejected: {item_id} by {user_id}")
        
        # Handle rejection - may require re-processing
        await self._handle_rejection(item, reason)
        
        return {"success": True, "action_id": action.action_id}
    
    async def override(
        self,
        item_id: str,
        user_id: str,
        new_content: Dict[str, Any],
        reason: str
    ) -> Dict[str, Any]:
        """
        Override AI content with human-provided content.
        
        The human's content replaces the AI-generated content.
        
        Args:
            item_id: Queue item ID
            user_id: User overriding
            new_content: Human-provided content
            reason: Reason for override
            
        Returns:
            Result dict with status
        """
        item = self._get_queue_item(item_id)
        if not item:
            return {"success": False, "error": "Item not found"}
        
        if item.status != "pending":
            return {"success": False, "error": f"Item is not pending (status: {item.status})"}
        
        # Store original content
        original_content = item.content.to_dict() if item.content else None
        
        # Create new response with human content
        node = self.db.get_node(item.node_id)
        new_response = AIResponse.create(
            task_id=item.task_id,
            node_id=item.node_id,
            response_type=ResponseType.HUMAN_OVERRIDE,
            content=new_content,
            summary=new_content.get("summary", "Human override"),
            reasoning=f"Human override by {user_id}: {reason}"
        )
        new_response.is_human_modified = True
        new_response.original_ai_content = original_content
        new_response.modification_reason = reason
        new_response.modified_by = user_id
        new_response.modified_at = datetime.utcnow()
        
        self.db.save_response(new_response)
        
        # Log the action
        action = AIHITLAction.create(
            org_id=item.org_id,
            node_id=item.node_id,
            user_id=user_id,
            action_type=HITLActionType.OVERRIDE,
            task_id=item.task_id,
            response_id=new_response.response_id,
            original_content=original_content,
            modified_content=new_content,
            reason=reason
        )
        self.db.save_hitl_action(action)
        
        # Update item
        item.status = "overridden"
        item.content = new_response
        self._save_queue_item(item)
        
        logger.info(f"HITL override: {item_id} by {user_id}")
        
        # Continue with new content
        await self._continue_after_hitl(item, approved=True, use_response=new_response)
        
        return {"success": True, "action_id": action.action_id, "response_id": new_response.response_id}
    
    async def add_message(
        self,
        item_id: str,
        user_id: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Add a message/note to the HITL item.
        
        Messages become part of the audit trail but don't change the flow.
        
        Args:
            item_id: Queue item ID
            user_id: User adding message
            message: Message content
            
        Returns:
            Result dict with status
        """
        item = self._get_queue_item(item_id)
        if not item:
            return {"success": False, "error": "Item not found"}
        
        # Log the action
        action = AIHITLAction.create(
            org_id=item.org_id,
            node_id=item.node_id,
            user_id=user_id,
            action_type=HITLActionType.MESSAGE,
            task_id=item.task_id,
            message=message
        )
        self.db.save_hitl_action(action)
        
        logger.info(f"HITL message added: {item_id} by {user_id}")
        
        return {"success": True, "action_id": action.action_id}
    
    async def pause_node(
        self,
        node_id: str,
        user_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Pause a node's activities.
        
        The node will stop processing new tasks until resumed.
        
        Args:
            node_id: Node to pause
            user_id: User pausing
            reason: Reason for pause
            
        Returns:
            Result dict with status
        """
        node = self.db.get_node(node_id)
        if not node:
            return {"success": False, "error": "Node not found"}
        
        # Update node status
        node.status = "paused"
        self.db.save_node(node)
        
        # Log action
        action = AIHITLAction.create(
            org_id=node.org_id,
            node_id=node_id,
            user_id=user_id,
            action_type=HITLActionType.PAUSE,
            reason=reason
        )
        self.db.save_hitl_action(action)
        
        logger.info(f"Node paused: {node_id} by {user_id}")
        
        return {"success": True, "action_id": action.action_id}
    
    async def resume_node(
        self,
        node_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Resume a paused node.
        
        Args:
            node_id: Node to resume
            user_id: User resuming
            
        Returns:
            Result dict with status
        """
        node = self.db.get_node(node_id)
        if not node:
            return {"success": False, "error": "Node not found"}
        
        # Update node status
        node.status = "active"
        self.db.save_node(node)
        
        # Log action
        action = AIHITLAction.create(
            org_id=node.org_id,
            node_id=node_id,
            user_id=user_id,
            action_type=HITLActionType.RESUME
        )
        self.db.save_hitl_action(action)
        
        logger.info(f"Node resumed: {node_id} by {user_id}")
        
        return {"success": True, "action_id": action.action_id}
    
    # =========================================================================
    # TIMEOUT HANDLING
    # =========================================================================
    
    async def check_timeouts(self) -> int:
        """
        Check for and handle expired HITL items.
        
        Items past their expiration are either:
        - Auto-approved if auto_proceed is enabled
        - Escalated or failed otherwise
        
        Returns:
            Number of items processed
        """
        expired_items = self._get_expired_items()
        processed = 0
        
        for item in expired_items:
            node = self.db.get_node(item.node_id)
            if not node:
                continue
            
            if node.hitl_config.auto_proceed:
                # Auto-approve
                logger.info(f"Auto-approving expired HITL item: {item.item_id}")
                await self.approve(item.item_id, "system_timeout", "Auto-approved due to timeout")
            else:
                # Mark as timed out
                item.status = "timeout"
                self._save_queue_item(item)
                
                # Log timeout
                action = AIHITLAction.create(
                    org_id=item.org_id,
                    node_id=item.node_id,
                    user_id="system",
                    action_type=HITLActionType.VIEW,  # Using VIEW for timeout logging
                    task_id=item.task_id,
                    message="HITL timeout - manual intervention required"
                )
                self.db.save_hitl_action(action)
            
            processed += 1
        
        return processed
    
    # =========================================================================
    # AUDIT TRAIL
    # =========================================================================
    
    def get_hitl_history(
        self,
        org_id: Optional[str] = None,
        node_id: Optional[str] = None,
        task_id: Optional[str] = None,
        limit: int = 100
    ) -> List[AIHITLAction]:
        """Get HITL action history with optional filters."""
        return self.db.get_hitl_actions(
            org_id=org_id,
            node_id=node_id,
            task_id=task_id,
            limit=limit
        )
    
    def get_user_activity(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get HITL activity for a specific user."""
        # This would need a custom query
        # For now, return empty list
        return []
    
    # =========================================================================
    # PRIVATE HELPERS
    # =========================================================================
    
    def _save_queue_item(self, item: HITLQueueItem) -> bool:
        """Save queue item to database."""
        try:
            import json
            self.db.db.execute("""
                INSERT OR REPLACE INTO ai_hitl_queue
                (item_id, org_id, node_id, task_id, review_type, content, status, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.item_id, item.org_id, item.node_id, item.task_id,
                item.review_type,
                json.dumps(item.content.to_dict()) if item.content else None,
                item.status,
                item.created_at.isoformat() if item.created_at else None,
                item.expires_at.isoformat() if item.expires_at else None
            ))
            self.db.db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save queue item: {e}")
            return False
    
    def _get_queue_item(self, item_id: str) -> Optional[HITLQueueItem]:
        """Get queue item from database."""
        try:
            import json
            result = self.db.db.execute(
                "SELECT * FROM ai_hitl_queue WHERE item_id = ?",
                (item_id,)
            ).fetchone()
            
            if result:
                data = dict(result)
                content_data = json.loads(data['content']) if data.get('content') else None
                content = AIResponse.from_dict(content_data) if content_data else None
                
                return HITLQueueItem(
                    item_id=data['item_id'],
                    org_id=data['org_id'],
                    node_id=data['node_id'],
                    task_id=data['task_id'],
                    review_type=data['review_type'],
                    content=content,
                    status=data['status'],
                    created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.utcnow(),
                    expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
                )
            return None
        except Exception as e:
            logger.error(f"Failed to get queue item: {e}")
            return None
    
    def _get_pending_items_for_nodes(self, node_ids: List[str]) -> List[HITLQueueItem]:
        """Get pending items for a list of nodes."""
        items = []
        for node_id in node_ids:
            try:
                import json
                results = self.db.db.execute(
                    "SELECT * FROM ai_hitl_queue WHERE node_id = ? AND status = 'pending' ORDER BY created_at",
                    (node_id,)
                ).fetchall()
                
                for row in results:
                    data = dict(row)
                    content_data = json.loads(data['content']) if data.get('content') else None
                    content = AIResponse.from_dict(content_data) if content_data else None
                    
                    items.append(HITLQueueItem(
                        item_id=data['item_id'],
                        org_id=data['org_id'],
                        node_id=data['node_id'],
                        task_id=data['task_id'],
                        review_type=data['review_type'],
                        content=content,
                        status=data['status'],
                        created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.utcnow(),
                        expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
                    ))
            except Exception as e:
                logger.error(f"Failed to get pending items: {e}")
        
        return items
    
    def _get_expired_items(self) -> List[HITLQueueItem]:
        """Get all expired pending items."""
        now = datetime.utcnow().isoformat()
        items = []
        
        try:
            import json
            results = self.db.db.execute(
                "SELECT * FROM ai_hitl_queue WHERE status = 'pending' AND expires_at < ?",
                (now,)
            ).fetchall()
            
            for row in results:
                data = dict(row)
                content_data = json.loads(data['content']) if data.get('content') else None
                content = AIResponse.from_dict(content_data) if content_data else None
                
                items.append(HITLQueueItem(
                    item_id=data['item_id'],
                    org_id=data['org_id'],
                    node_id=data['node_id'],
                    task_id=data['task_id'],
                    review_type=data['review_type'],
                    content=content,
                    status=data['status'],
                    created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.utcnow(),
                    expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
                ))
        except Exception as e:
            logger.error(f"Failed to get expired items: {e}")
        
        return items
    
    def _calculate_time_remaining(self, item: HITLQueueItem) -> Optional[str]:
        """Calculate human-readable time remaining."""
        if not item.expires_at:
            return None
        
        remaining = item.expires_at - datetime.utcnow()
        if remaining.total_seconds() <= 0:
            return "Expired"
        
        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    
    async def _notify_review_required(
        self,
        node: AINode,
        task: AITask,
        item: HITLQueueItem
    ) -> None:
        """Send notification that HITL review is required."""
        if not self.notifier:
            return
        
        if not node.human_mirror.email:
            return
        
        try:
            subject = f"HITL Review Required: {task.title}"
            body = f"""
Human-in-the-Loop Review Required

Role: {node.role_name}
Task: {task.title}
Review Type: {item.review_type}
Expires: {item.expires_at}

Please log in to the HITL Dashboard to review and take action.

---
Abhikarta AI Org
"""
            
            await self.notifier.send_email(
                to=node.human_mirror.email,
                subject=subject,
                body=body
            )
        except Exception as e:
            logger.error(f"Failed to send HITL notification: {e}")
    
    async def _continue_after_hitl(
        self,
        item: HITLQueueItem,
        approved: bool,
        use_response: Optional[AIResponse] = None
    ) -> None:
        """Continue task processing after HITL decision."""
        if self.event_bus:
            await self.event_bus.publish_async(f"aiorg:{item.org_id}", {
                "type": "HITL_APPROVED" if approved else "HITL_REJECTED",
                "item_id": item.item_id,
                "node_id": item.node_id,
                "task_id": item.task_id,
                "review_type": item.review_type,
                "response_id": use_response.response_id if use_response else None,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def _handle_rejection(
        self,
        item: HITLQueueItem,
        reason: str
    ) -> None:
        """Handle rejected HITL item."""
        # Update task status
        task = self.db.get_task(item.task_id)
        if task:
            task.status = "failed"
            task.error_message = f"HITL rejected: {reason}"
            self.db.save_task(task)
        
        if self.event_bus:
            await self.event_bus.publish_async(f"aiorg:{item.org_id}", {
                "type": "HITL_REJECTED",
                "item_id": item.item_id,
                "node_id": item.node_id,
                "task_id": item.task_id,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            })
