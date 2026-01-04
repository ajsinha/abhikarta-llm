"""
HITL (Human-in-the-Loop) Routes - User-facing routes for HITL task management.

Allows users to:
- View pending HITL tasks assigned to them
- Respond to tasks (approve, reject, provide input)
- View task history

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import json
import logging
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session, jsonify

from .abstract_routes import AbstractRoutes, login_required

logger = logging.getLogger(__name__)


class HITLRoutes(AbstractRoutes):
    """User-facing HITL task routes."""
    
    def register_routes(self):
        """Register all HITL routes."""
        
        @self.app.route('/hitl')
        @login_required
        def hitl_tasks():
            """View pending HITL tasks for current user."""
            from abhikarta.hitl import HITLManager
            
            user_id = session.get('user_id')
            status_filter = request.args.get('status', 'pending')
            
            manager = HITLManager(self.db_facade)
            
            # Get tasks assigned to user or unassigned
            if status_filter == 'all':
                tasks = manager.get_all_tasks(limit=100)
            else:
                tasks = manager.get_all_tasks(status=status_filter, limit=100)
            
            # Filter to show tasks assigned to user or unassigned
            user_tasks = [t for t in tasks 
                         if t.assigned_to == user_id or t.assigned_to is None]
            
            stats = manager.get_stats()
            
            return render_template('hitl/tasks.html',
                                   fullname=session.get('fullname'),
                                   userid=user_id,
                                   roles=session.get('roles', []),
                                   tasks=user_tasks,
                                   stats=stats,
                                   status_filter=status_filter)
        
        @self.app.route('/hitl/<task_id>')
        @login_required
        def hitl_detail(task_id):
            """View HITL task details."""
            from abhikarta.hitl import HITLManager
            
            manager = HITLManager(self.db_facade)
            task = manager.get_task(task_id)
            
            if not task:
                flash('Task not found', 'error')
                return redirect(url_for('hitl_tasks'))
            
            # Get workflow info if available
            workflow = None
            if task.workflow_id:
                workflow = self.db_facade.fetch_one(
                    "SELECT * FROM workflows WHERE workflow_id = ?",
                    (task.workflow_id,)
                )
            
            return render_template('hitl/detail.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   task=task,
                                   workflow=workflow)
        
        @self.app.route('/hitl/<task_id>/respond', methods=['POST'])
        @login_required
        def hitl_respond(task_id):
            """Respond to an HITL task."""
            from abhikarta.hitl import HITLManager
            
            user_id = session.get('user_id')
            manager = HITLManager(self.db_facade)
            task = manager.get_task(task_id)
            
            if not task:
                flash('Task not found', 'error')
                return redirect(url_for('hitl_tasks'))
            
            action = request.form.get('action', 'complete')
            response_text = request.form.get('response', '')
            
            try:
                # Parse response as JSON if possible
                try:
                    response_data = json.loads(response_text) if response_text else {}
                except:
                    response_data = {'text': response_text}
                
                if action == 'approve':
                    manager.complete_task(
                        task_id=task_id,
                        response_data={'approved': True, **response_data},
                        completed_by=user_id
                    )
                    flash('Task approved successfully', 'success')
                    
                elif action == 'reject':
                    manager.complete_task(
                        task_id=task_id,
                        response_data={'approved': False, 'rejected': True, **response_data},
                        completed_by=user_id
                    )
                    flash('Task rejected', 'warning')
                    
                elif action == 'complete':
                    manager.complete_task(
                        task_id=task_id,
                        response_data=response_data,
                        completed_by=user_id
                    )
                    flash('Task completed successfully', 'success')
                
                # Log audit
                self.log_audit('hitl_respond', 'hitl_task', task_id, {'action': action})
                
                # Resume workflow if applicable
                if task.execution_id:
                    self._resume_workflow(task, response_data)
                    
            except Exception as e:
                logger.error(f"Error responding to task: {e}")
                flash(f'Error: {str(e)}', 'error')
            
            return redirect(url_for('hitl_tasks'))
        
        @self.app.route('/hitl/<task_id>/claim', methods=['POST'])
        @login_required
        def hitl_claim(task_id):
            """Claim an HITL task."""
            from abhikarta.hitl import HITLManager
            
            user_id = session.get('user_id')
            manager = HITLManager(self.db_facade)
            
            try:
                manager.assign_task(task_id, user_id)
                flash('Task claimed successfully', 'success')
                self.log_audit('hitl_claim', 'hitl_task', task_id)
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
            
            return redirect(url_for('hitl_detail', task_id=task_id))
        
        @self.app.route('/api/hitl/pending')
        @login_required
        def api_hitl_pending():
            """Get count of pending HITL tasks (for navbar notification)."""
            from abhikarta.hitl import HITLManager
            
            user_id = session.get('user_id')
            manager = HITLManager(self.db_facade)
            
            # Get pending tasks for user
            tasks = manager.get_all_tasks(status='pending', limit=100)
            user_tasks = [t for t in tasks 
                         if t.assigned_to == user_id or t.assigned_to is None]
            
            return jsonify({
                'count': len(user_tasks),
                'tasks': [{'task_id': t.task_id, 'title': t.title} for t in user_tasks[:5]]
            })
    
    def _resume_workflow(self, task, response_data):
        """Resume a paused workflow after HITL completion."""
        try:
            # Update the execution with HITL response
            self.db_facade.execute("""
                UPDATE workflow_executions 
                SET status = 'running',
                    metadata = json_set(COALESCE(metadata, '{}'), 
                                       '$.hitl_response', ?)
                WHERE execution_id = ?
            """, (json.dumps(response_data), task.execution_id))
            
            logger.info(f"Workflow {task.execution_id} marked for resumption")
            
            # Note: In a real implementation, you would trigger the workflow
            # executor to resume from the HITL node. This could be done via:
            # - A background task queue (Celery, RQ, etc.)
            # - A webhook
            # - Polling from the executor
            
        except Exception as e:
            logger.error(f"Failed to resume workflow: {e}")
