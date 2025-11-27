"""
Workflow Routes

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha | Email: ajsinha@gmail.com

Legal Notice: This module and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited without explicit 
written permission from the copyright holder.

Patent Pending: Certain architectural patterns and implementations described in this module 
may be subject to patent applications.
"""

from flask import render_template, request, jsonify, session, redirect, url_for, flash
import logging
from datetime import datetime

from web.route_management.abstract_routes import AbstractRoutes
from workflow_management.workflow_db_handler import WorkflowDBHandler
from workflow_management.workflow_execution_engine import WorkflowExecutionEngine
from workflow_management.workflow_langgraph_engine import LangGraphWorkflowEngine
from workflow_management.models.workflow_models import (
    Workflow, WorkflowStatus
)
from web.route_management.abstract_routes import login_required

logger = logging.getLogger(__name__)





class WorkflowRoutes(AbstractRoutes):
    """Workflow management routes"""

    def __init__(self, app, db_connection_pool_name: str):
        """
        Initialize workflow routes.

        Args:
            app: Flask application instance
            db_connection_pool_name: Database connection pool name
        """
        super().__init__(app, db_connection_pool_name)
        self.db_handler = WorkflowDBHandler(db_connection_pool_name)
        #self.execution_engine = WorkflowExecutionEngine(self.db_handler)
        self.execution_engine = LangGraphWorkflowEngine(
            db_handler=self.db_handler,
            max_workers=10
        )
        logger.info("Workflow routes initialized")

    def register_routes(self):
        """Register all workflow-related routes"""
        
        # Register custom template filters for datetime handling
        try:
            from web.template_filters import register_template_filters
            register_template_filters(self.app)
            logger.info("Workflow template filters registered")
        except Exception as e:
            logger.warning(f"Could not register workflow template filters: {e}")

        # ============ Workflow Management Routes ============

        @self.app.route('/workflow/dashboard')
        @login_required
        def workflow_dashboard():
            """Workflow dashboard"""
            userid = session.get('userid')
            fullname = session.get('fullname')
            is_admin = session.get('is_admin', False)

            # Get statistics
            stats = self.db_handler.get_execution_statistics()
            
            # Get recent executions
            recent_executions = self.db_handler.list_executions(
                triggered_by=userid if not is_admin else None,
                limit=10
            )

            # Get pending tasks for user
            pending_tasks = self.db_handler.list_user_tasks(
                assigned_to=userid,
                status='pending'
            )

            return render_template('workflow/dashboard.html',
                                 userid=userid,
                                 fullname=fullname,
                                 is_admin=is_admin,
                                 stats=stats,
                                 recent_executions=recent_executions,
                                 pending_tasks=pending_tasks)

        @self.app.route('/workflow/list')
        @login_required
        def list_workflows():
            """List all workflows"""
            userid = session.get('userid')
            is_admin = session.get('is_admin', False)

            # Get filter parameters
            status = request.args.get('status')
            created_by = request.args.get('created_by')

            # Non-admin users can only see their own workflows
            if not is_admin and not created_by:
                created_by = userid

            workflows = self.db_handler.list_workflows(
                status=status,
                created_by=created_by
            )

            return render_template('workflow/list.html',
                                 workflows=workflows,
                                 userid=userid,
                                 is_admin=is_admin)

        @self.app.route('/workflow/create', methods=['GET'])
        def create_workflow_page():
            return render_template('workflow/create_enhanced.html')

        @self.app.route('/workflow/create', methods=['POST'])
        @login_required
        def create_workflow():
            """Create a new workflow"""
            data = request.json
            workflow_type = data.get('workflow_type', 'json')

            try:
                userid = session.get('userid')
                data = request.get_json()

                # Create workflow
                workflow = Workflow(
                    workflow_id=Workflow.generate_id(),
                    name=data['name'],
                    description=data.get('description', ''),
                    version=data.get('version', '1.0.0'),
                    definition_json=data['definition'],  # Stores both formats
                    status='draft',
                    created_by='current_user',
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    tags=data.get('tags', [])
                )

                if self.db_handler.create_workflow(workflow):
                    return jsonify({
                        'success': True,
                        'workflow_id': workflow.workflow_id,
                        'message': 'Workflow created successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to create workflow'
                    }), 500

            except Exception as e:
                logger.error(f"Error creating workflow: {e}")
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500

        @self.app.route('/workflow/<workflow_id>')
        @login_required
        def view_workflow(workflow_id):
            """View workflow details"""
            workflow = self.db_handler.get_workflow(workflow_id)
            if not workflow:
                flash('Workflow not found', 'error')
                return redirect(url_for('list_workflows'))

            # Get execution history
            executions = self.db_handler.list_executions(
                workflow_id=workflow_id,
                limit=20
            )

            return render_template('workflow/view.html',
                                 workflow=workflow,
                                 executions=executions)

        @self.app.route('/workflow/<workflow_id>/edit', methods=['GET', 'POST'])
        @login_required
        def edit_workflow(workflow_id):
            """Edit workflow"""
            workflow = self.db_handler.get_workflow(workflow_id)
            if not workflow:
                flash('Workflow not found', 'error')
                return redirect(url_for('list_workflows'))

            # Check permissions
            userid = session.get('userid')
            is_admin = session.get('is_admin', False)
            if not is_admin and workflow.created_by != userid:
                flash('You do not have permission to edit this workflow', 'error')
                return redirect(url_for('view_workflow', workflow_id=workflow_id))

            if request.method == 'GET':
                return render_template('workflow/edit.html', workflow=workflow)

            try:
                data = request.get_json()
                workflow.description = data.get('description', workflow.description)
                workflow.definition_json = data.get('definition', workflow.definition_json)
                workflow.status = data.get('status', workflow.status)
                workflow.tags = data.get('tags', workflow.tags)

                if self.db_handler.update_workflow(workflow):
                    return jsonify({
                        'success': True,
                        'message': 'Workflow updated successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to update workflow'
                    }), 500

            except Exception as e:
                logger.error(f"Error updating workflow: {e}")
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500

        @self.app.route('/workflow/<workflow_id>/delete', methods=['POST'])
        @login_required
        def delete_workflow(workflow_id):
            """Delete workflow"""
            workflow = self.db_handler.get_workflow(workflow_id)
            if not workflow:
                return jsonify({'success': False, 'message': 'Workflow not found'}), 404

            # Check permissions
            userid = session.get('userid')
            is_admin = session.get('is_admin', False)
            if not is_admin and workflow.created_by != userid:
                return jsonify({
                    'success': False,
                    'message': 'Permission denied'
                }), 403

            if self.db_handler.delete_workflow(workflow_id):
                return jsonify({
                    'success': True,
                    'message': 'Workflow deleted successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to delete workflow'
                }), 500

        # ============ Execution Routes ============

        @self.app.route('/workflow/<workflow_id>/execute', methods=['POST'])
        @login_required
        def execute_workflow(workflow_id):
            """Execute a workflow"""
            try:
                userid = session.get('userid')
                data = request.get_json() or {}
                input_parameters = data.get('input_parameters', {})

                execution_id = self.execution_engine.start_execution(
                    workflow_id=workflow_id,
                    triggered_by=userid,
                    input_parameters=input_parameters
                )

                return jsonify({
                    'success': True,
                    'execution_id': execution_id,
                    'message': 'Workflow execution started'
                })

            except Exception as e:
                logger.error(f"Error executing workflow: {e}")
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500

        @self.app.route('/workflow/execution/<execution_id>')
        @login_required
        def view_execution(execution_id):
            """View execution details"""
            execution = self.db_handler.get_execution(execution_id)
            if not execution:
                flash('Execution not found', 'error')
                return redirect(url_for('workflow_dashboard'))

            # Get node executions
            node_executions = self.db_handler.get_node_executions(execution_id)

            # Get workflow
            workflow = self.db_handler.get_workflow(execution.workflow_id)

            # Get audit logs
            audit_logs = self.db_handler.get_audit_logs(execution_id, limit=100)

            return render_template('workflow/execution_detail.html',
                                 execution=execution,
                                 workflow=workflow,
                                 node_executions=node_executions,
                                 audit_logs=audit_logs)

        @self.app.route('/workflow/execution/<execution_id>/pause', methods=['POST'])
        @login_required
        def pause_execution(execution_id):
            """Pause execution"""
            if self.execution_engine.pause_execution(execution_id):
                return jsonify({'success': True, 'message': 'Execution paused'})
            return jsonify({'success': False, 'message': 'Failed to pause execution'}), 500

        @self.app.route('/workflow/execution/<execution_id>/resume', methods=['POST'])
        @login_required
        def resume_execution(execution_id):
            """Resume execution"""
            if self.execution_engine.resume_execution(execution_id):
                return jsonify({'success': True, 'message': 'Execution resumed'})
            return jsonify({'success': False, 'message': 'Failed to resume execution'}), 500

        @self.app.route('/workflow/execution/<execution_id>/cancel', methods=['POST'])
        @login_required
        def cancel_execution(execution_id):
            """Cancel execution"""
            if self.execution_engine.cancel_execution(execution_id):
                return jsonify({'success': True, 'message': 'Execution cancelled'})
            return jsonify({'success': False, 'message': 'Failed to cancel execution'}), 500

        @self.app.route('/workflow/executions')
        @login_required
        def list_executions():
            """List executions"""
            userid = session.get('userid')
            is_admin = session.get('is_admin', False)

            # Get filter parameters
            workflow_id = request.args.get('workflow_id')
            status = request.args.get('status')

            executions = self.db_handler.list_executions(
                workflow_id=workflow_id,
                status=status,
                triggered_by=userid if not is_admin else None,
                limit=50
            )

            return render_template('workflow/executions.html',
                                 executions=executions,
                                 userid=userid,
                                 is_admin=is_admin)

        # ============ Human Task Routes ============

        @self.app.route('/workflow/tasks')
        @login_required
        def list_tasks():
            """List user tasks"""
            userid = session.get('userid')
            status = request.args.get('status')

            tasks = self.db_handler.list_user_tasks(
                assigned_to=userid,
                status=status,
                limit=50
            )

            # Get execution details for each task
            task_details = []
            for task in tasks:
                execution = self.db_handler.get_execution(task.execution_id)
                workflow = self.db_handler.get_workflow(execution.workflow_id) if execution else None
                task_details.append({
                    'task': task,
                    'execution': execution,
                    'workflow': workflow
                })

            return render_template('workflow/tasks.html',
                                 task_details=task_details,
                                 userid=userid)

        @self.app.route('/workflow/task/<task_id>')
        @login_required
        def view_task(task_id):
            """View task details"""
            task = self.db_handler.get_human_task(task_id)
            if not task:
                flash('Task not found', 'error')
                return redirect(url_for('list_tasks'))

            # Check if user is assigned to this task
            userid = session.get('userid')
            if task.assigned_to != userid:
                flash('You are not assigned to this task', 'error')
                return redirect(url_for('list_tasks'))

            # Get execution and workflow details
            execution = self.db_handler.get_execution(task.execution_id)
            workflow = self.db_handler.get_workflow(execution.workflow_id) if execution else None

            return render_template('workflow/task_detail.html',
                                 task=task,
                                 execution=execution,
                                 workflow=workflow)

        @self.app.route('/workflow/task/<task_id>/respond', methods=['POST'])
        @login_required
        def respond_to_task(task_id):
            """Respond to a human task"""
            try:
                task = self.db_handler.get_human_task(task_id)
                if not task:
                    return jsonify({'success': False, 'message': 'Task not found'}), 404

                # Check if user is assigned to this task
                userid = session.get('userid')
                if task.assigned_to != userid:
                    return jsonify({'success': False, 'message': 'Permission denied'}), 403

                data = request.get_json()
                task.status = data.get('status', 'completed')
                task.responded_at = datetime.now()
                task.response_data = data.get('response_data', {})
                task.comments = data.get('comments', '')

                if self.db_handler.update_human_task(task):
                    return jsonify({
                        'success': True,
                        'message': 'Task response submitted successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to submit task response'
                    }), 500

            except Exception as e:
                logger.error(f"Error responding to task: {e}")
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500

        # ============ Analytics Routes ============

        @self.app.route('/workflow/analytics')
        @login_required
        def workflow_analytics():
            """Workflow analytics dashboard"""
            # Get statistics
            stats_7days = self.db_handler.get_execution_statistics(days=7)
            stats_30days = self.db_handler.get_execution_statistics(days=30)

            return render_template('workflow/analytics.html',
                                 stats_7days=stats_7days,
                                 stats_30days=stats_30days)

        @self.app.route('/workflow/api/statistics')
        @login_required
        def get_workflow_statistics():
            """API endpoint for workflow statistics"""
            workflow_id = request.args.get('workflow_id')
            days = int(request.args.get('days', 30))

            stats = self.db_handler.get_execution_statistics(
                workflow_id=workflow_id,
                days=days
            )

            return jsonify(stats)

        logger.info("All workflow routes registered successfully")
