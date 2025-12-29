"""
User Routes Module - Handles user-specific routes and functionality

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This document and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use of this document or the software
system it describes is strictly prohibited without explicit written permission from the
copyright holder. This document is provided "as is" without warranty of any kind, either
expressed or implied. The copyright holder shall not be liable for any damages arising
from the use of this document or the software system it describes.

Patent Pending: Certain architectural patterns and implementations described in this
document may be subject to patent applications.
"""

from flask import render_template, request, redirect, url_for, session, flash
import logging

from .abstract_routes import AbstractRoutes, login_required

logger = logging.getLogger(__name__)


class UserRoutes(AbstractRoutes):
    """
    Handles user-specific routes for the application.
    
    This class manages routes for regular users including dashboard,
    agent catalog, and execution history.
    
    Attributes:
        app: Flask application instance
        user_facade: UserFacade instance for user operations
        db_facade: DatabaseFacade instance for database operations
    """
    
    def __init__(self, app):
        """
        Initialize UserRoutes.
        
        Args:
            app: Flask application instance
        """
        super().__init__(app)
        logger.info("UserRoutes initialized")
    
    def register_routes(self):
        """Register all user routes."""
        
        @self.app.route('/user/dashboard')
        @login_required
        def user_dashboard():
            """User dashboard with available agents and recent executions."""
            user_id = session.get('user_id')
            
            # Get published agents available to this user
            agents = []
            try:
                agents = self.db_facade.agents.get_all_agents(status='published')
            except Exception as e:
                logger.error(f"Error getting agents: {e}")
            
            # Get user's recent executions
            executions = []
            try:
                executions = self.db_facade.executions.get_recent_executions(user_id=user_id, limit=10)
            except Exception as e:
                logger.error(f"Error getting executions: {e}")
            
            return render_template('user/dashboard.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   agents=agents,
                                   executions=executions)
        
        @self.app.route('/user/agents')
        @login_required
        def user_agents():
            """List available agents for the user."""
            # Get published agents
            agents = []
            try:
                agents = self.db_facade.agents.get_all_agents(status='published')
            except Exception as e:
                logger.error(f"Error getting agents: {e}")
            
            return render_template('user/agents.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   agents=agents)
        
        @self.app.route('/user/agents/<agent_id>')
        @login_required
        def user_agent_detail(agent_id):
            """View agent details."""
            agent = None
            try:
                agent = self.db_facade.fetch_one(
                    "SELECT * FROM agents WHERE agent_id = ? AND status = 'published'",
                    (agent_id,)
                )
            except Exception as e:
                logger.error(f"Error getting agent: {e}")
            
            if not agent:
                flash('Agent not found or not available', 'error')
                return redirect(url_for('user_agents'))
            
            return render_template('user/agent_detail.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   agent=agent)
        
        @self.app.route('/user/agents/<agent_id>/execute', methods=['GET', 'POST'])
        @login_required
        def execute_agent(agent_id):
            """Execute an agent using LangChain."""
            agent = None
            try:
                agent = self.db_facade.fetch_one(
                    "SELECT * FROM agents WHERE agent_id = ? AND status = 'published'",
                    (agent_id,)
                )
            except Exception as e:
                logger.error(f"Error getting agent: {e}")
            
            if not agent:
                flash('Agent not found or not available', 'error')
                return redirect(url_for('user_agents'))
            
            if request.method == 'POST':
                import uuid
                import json
                from datetime import datetime
                
                input_data = request.form.get('input_data', '')
                execution_id = f"exec_{uuid.uuid4().hex[:16]}"
                started_at = datetime.now()
                
                try:
                    # Create execution record with 'running' status
                    self.db_facade.execute(
                        """INSERT INTO executions 
                           (execution_id, agent_id, user_id, status, input_data, started_at)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (execution_id, agent_id, session.get('user_id'), 'running',
                         input_data, started_at.isoformat())
                    )
                    
                    # Execute agent using LangChain
                    try:
                        from abhikarta.langchain.agents import AgentExecutor as LangChainAgentExecutor
                        
                        executor = LangChainAgentExecutor(self.db_facade)
                        result = executor.execute_agent(agent_id, input_data)
                        
                        # Update execution record with results
                        self.db_facade.execute(
                            """UPDATE executions SET 
                               status = ?, output_data = ?, error_message = ?,
                               completed_at = ?, duration_ms = ?, metadata = ?
                               WHERE execution_id = ?""",
                            (
                                result.status,
                                result.output,
                                result.error_message,
                                datetime.now().isoformat(),
                                result.duration_ms,
                                json.dumps({
                                    'intermediate_steps': result.intermediate_steps,
                                    'tool_calls': result.tool_calls,
                                    'execution_mode': 'langchain'
                                }),
                                execution_id
                            )
                        )
                        
                        if result.status == 'completed':
                            flash(f'Agent execution completed successfully!', 'success')
                        else:
                            flash(f'Agent execution finished with status: {result.status}', 'warning')
                            
                    except ImportError as ie:
                        # LangChain not available, log for manual processing
                        logger.warning(f"LangChain not available, execution pending: {ie}")
                        self.db_facade.execute(
                            "UPDATE executions SET status = 'pending', metadata = ? WHERE execution_id = ?",
                            (json.dumps({'note': 'LangChain not installed', 'error': str(ie)}), execution_id)
                        )
                        flash(f'Agent execution queued: {execution_id}', 'info')
                    
                    self.log_audit('execute_agent', 'agent', agent_id, 
                                   {'execution_id': execution_id})
                    
                    return redirect(url_for('execution_detail', execution_id=execution_id))
                    
                except Exception as e:
                    logger.error(f"Error executing agent: {e}", exc_info=True)
                    # Update execution as failed
                    try:
                        self.db_facade.execute(
                            """UPDATE executions SET 
                               status = 'failed', error_message = ?, completed_at = ?
                               WHERE execution_id = ?""",
                            (str(e), datetime.now().isoformat(), execution_id)
                        )
                    except:
                        pass
                    flash(f'Agent execution failed: {str(e)}', 'error')
            
            return render_template('user/execute_agent.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   agent=agent)
        
        @self.app.route('/user/executions')
        @login_required
        def user_executions():
            """List user's execution history including swarm executions."""
            user_id = session.get('user_id')
            
            executions = []
            swarm_executions = []
            
            try:
                # Get agent/workflow executions
                executions = self.db_facade.executions.get_all_executions(user_id=user_id)
            except Exception as e:
                logger.error(f"Error getting executions: {e}")
            
            try:
                # Get swarm executions
                swarm_executions = self.db_facade.fetch_all(
                    """SELECT se.*, s.name as swarm_name 
                       FROM swarm_executions se
                       LEFT JOIN swarms s ON se.swarm_id = s.swarm_id
                       WHERE se.user_id = ?
                       ORDER BY se.created_at DESC
                       LIMIT 100""",
                    (user_id,)
                ) or []
            except Exception as e:
                logger.error(f"Error getting swarm executions: {e}")
            
            return render_template('user/executions.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   executions=executions,
                                   swarm_executions=swarm_executions)
        
        @self.app.route('/user/executions/<execution_id>')
        @login_required
        def execution_detail(execution_id):
            """View execution details."""
            user_id = session.get('user_id')
            is_admin = session.get('is_admin', False)
            
            execution = None
            try:
                execution = self.db_facade.executions.get_execution(execution_id)
                # Check access - non-admins can only see their own
                if execution and not is_admin and execution.get('user_id') != user_id:
                    execution = None
            except Exception as e:
                logger.error(f"Error getting execution: {e}")
            
            if not execution:
                flash('Execution not found', 'error')
                return redirect(url_for('user_executions'))
            
            # Get agent info using delegate
            agent = None
            try:
                agent = self.db_facade.agents.get_agent(execution['agent_id'])
            except Exception as e:
                logger.error(f"Error getting agent: {e}")
            
            return render_template('user/execution_detail.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   execution=execution,
                                   agent=agent)
        
        @self.app.route('/user/executions/<execution_id>/progress')
        @login_required
        def execution_progress(execution_id):
            """View execution progress with visual feedback."""
            user_id = session.get('user_id')
            is_admin = session.get('is_admin', False)
            
            execution = None
            try:
                if is_admin:
                    execution = self.db_facade.fetch_one(
                        "SELECT * FROM executions WHERE execution_id = ?",
                        (execution_id,)
                    )
                else:
                    execution = self.db_facade.fetch_one(
                        "SELECT * FROM executions WHERE execution_id = ? AND user_id = ?",
                        (execution_id, user_id)
                    )
            except Exception as e:
                logger.error(f"Error getting execution: {e}")
            
            if not execution:
                flash('Execution not found', 'error')
                return redirect(url_for('user_executions'))
            
            # Get agent/workflow info
            agent = None
            workflow = None
            
            if execution.get('agent_id'):
                agent = self.db_facade.fetch_one(
                    "SELECT name, agent_id FROM agents WHERE agent_id = ?",
                    (execution['agent_id'],)
                )
            if execution.get('workflow_id'):
                workflow = self.db_facade.fetch_one(
                    "SELECT name, workflow_id FROM workflows WHERE workflow_id = ?",
                    (execution['workflow_id'],)
                )
            
            # Get execution steps
            steps = self.db_facade.fetch_all(
                """SELECT * FROM execution_steps 
                   WHERE execution_id = ? 
                   ORDER BY step_number ASC""",
                (execution_id,)
            ) or []
            
            # Calculate progress
            total_steps = len(steps) if steps else 1
            completed_steps = len([s for s in steps if s.get('status') == 'completed'])
            progress_percent = int((completed_steps / total_steps) * 100) if total_steps > 0 else 0
            
            return render_template('user/execution_progress.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   execution=execution,
                                   agent=agent,
                                   workflow=workflow,
                                   steps=steps,
                                   total_steps=total_steps,
                                   completed_steps=completed_steps,
                                   progress_percent=progress_percent)
        
        @self.app.route('/user/executions/<execution_id>/trace')
        @login_required
        def execution_trace(execution_id):
            """View execution trace with step-by-step details."""
            user_id = session.get('user_id')
            is_admin = session.get('is_admin', False)
            
            execution = None
            try:
                if is_admin:
                    execution = self.db_facade.fetch_one(
                        "SELECT * FROM executions WHERE execution_id = ?",
                        (execution_id,)
                    )
                else:
                    execution = self.db_facade.fetch_one(
                        "SELECT * FROM executions WHERE execution_id = ? AND user_id = ?",
                        (execution_id, user_id)
                    )
            except Exception as e:
                logger.error(f"Error getting execution: {e}")
            
            if not execution:
                flash('Execution not found', 'error')
                return redirect(url_for('user_executions'))
            
            # Get execution steps/trace
            trace_steps = []
            try:
                steps = self.db_facade.fetch_all(
                    """SELECT * FROM execution_steps 
                       WHERE execution_id = ? 
                       ORDER BY step_number ASC""",
                    (execution_id,)
                ) or []
                
                for step in steps:
                    trace_steps.append({
                        'step_name': step.get('step_name', f"Step {step.get('step_number', '?')}"),
                        'step_type': step.get('step_type', 'unknown'),
                        'status': step.get('status', 'pending'),
                        'message': step.get('message'),
                        'input': step.get('input_data'),
                        'output': step.get('output_data'),
                        'error': step.get('error'),
                        'timestamp': step.get('started_at'),
                        'duration': step.get('duration')
                    })
            except Exception as e:
                logger.error(f"Error getting execution steps: {e}")
            
            # Calculate statistics
            success_count = len([s for s in trace_steps if s['status'] == 'completed'])
            error_count = len([s for s in trace_steps if s['status'] == 'failed'])
            tool_calls = len([s for s in trace_steps if s['step_type'] in ('tool', 'tool_call')])
            
            return render_template('user/execution_trace.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   execution=execution,
                                   trace_steps=trace_steps,
                                   success_count=success_count,
                                   error_count=error_count,
                                   tool_calls=tool_calls)
        
        # =====================================================================
        # HITL (Human-in-the-Loop) Routes
        # =====================================================================
        
        @self.app.route('/user/hitl')
        @login_required
        def user_hitl_tasks():
            """View user's HITL tasks."""
            from abhikarta.hitl import HITLManager
            
            user_id = session.get('user_id')
            is_reviewer = 'hitl_reviewer' in session.get('roles', [])
            
            manager = HITLManager(self.db_facade)
            
            # Get tasks assigned to user (and unassigned if reviewer)
            tasks = manager.get_user_tasks(user_id, include_unassigned=is_reviewer)
            stats = manager.get_stats(user_id)
            
            return render_template('user/hitl_tasks.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   tasks=tasks,
                                   stats=stats,
                                   is_reviewer=is_reviewer)
        
        @self.app.route('/user/hitl/<task_id>')
        @login_required
        def user_hitl_detail(task_id):
            """View HITL task details."""
            from abhikarta.hitl import HITLManager
            
            user_id = session.get('user_id')
            is_reviewer = 'hitl_reviewer' in session.get('roles', [])
            is_admin = session.get('is_admin', False)
            
            manager = HITLManager(self.db_facade)
            task = manager.get_task(task_id)
            
            if not task:
                flash('Task not found', 'error')
                return redirect(url_for('user_hitl_tasks'))
            
            # Check access: assigned to user, user is reviewer, or admin
            if task.assigned_to != user_id and not is_reviewer and not is_admin:
                flash('You do not have access to this task', 'error')
                return redirect(url_for('user_hitl_tasks'))
            
            comments = manager.get_comments(task_id, include_internal=is_admin)
            
            # Get agent/workflow info if linked
            agent = None
            workflow = None
            execution = None
            
            if task.agent_id:
                agent = self.db_facade.fetch_one(
                    "SELECT name, agent_id FROM agents WHERE agent_id = ?",
                    (task.agent_id,)
                )
            if task.workflow_id:
                workflow = self.db_facade.fetch_one(
                    "SELECT name, workflow_id FROM workflows WHERE workflow_id = ?",
                    (task.workflow_id,)
                )
            if task.execution_id:
                execution = self.db_facade.fetch_one(
                    "SELECT execution_id, status, started_at FROM executions WHERE execution_id = ?",
                    (task.execution_id,)
                )
            
            # Get list of users for reassignment (if reviewer/admin)
            users = []
            if is_reviewer or is_admin:
                users = self.db_facade.fetch_all(
                    "SELECT user_id, fullname FROM users WHERE is_active = 1 ORDER BY fullname"
                ) or []
            
            return render_template('user/hitl_detail.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   task=task,
                                   comments=comments,
                                   agent=agent,
                                   workflow=workflow,
                                   execution=execution,
                                   users=users,
                                   is_reviewer=is_reviewer,
                                   is_admin=is_admin)
        
        @self.app.route('/user/hitl/<task_id>/claim', methods=['POST'])
        @login_required
        def user_hitl_claim(task_id):
            """Claim an unassigned HITL task."""
            from abhikarta.hitl import HITLManager
            
            user_id = session.get('user_id')
            manager = HITLManager(self.db_facade)
            
            task = manager.get_task(task_id)
            if not task:
                flash('Task not found', 'error')
                return redirect(url_for('user_hitl_tasks'))
            
            if task.assigned_to:
                flash('Task is already assigned', 'warning')
                return redirect(url_for('user_hitl_detail', task_id=task_id))
            
            manager.assign_task(task_id, user_id, user_id, "Self-claimed")
            self.log_audit('claim_hitl', 'hitl_task', task_id)
            
            flash('Task claimed successfully', 'success')
            return redirect(url_for('user_hitl_detail', task_id=task_id))
        
        @self.app.route('/user/hitl/<task_id>/start', methods=['POST'])
        @login_required
        def user_hitl_start(task_id):
            """Start working on a HITL task."""
            from abhikarta.hitl import HITLManager
            
            user_id = session.get('user_id')
            manager = HITLManager(self.db_facade)
            
            task = manager.get_task(task_id)
            if not task or task.assigned_to != user_id:
                flash('Task not found or not assigned to you', 'error')
                return redirect(url_for('user_hitl_tasks'))
            
            manager.start_task(task_id, user_id)
            self.log_audit('start_hitl', 'hitl_task', task_id)
            
            flash('Task started', 'success')
            return redirect(url_for('user_hitl_detail', task_id=task_id))
        
        @self.app.route('/user/hitl/<task_id>/comment', methods=['POST'])
        @login_required
        def user_hitl_comment(task_id):
            """Add a comment to a HITL task."""
            from abhikarta.hitl import HITLManager
            
            user_id = session.get('user_id')
            comment_text = request.form.get('comment', '').strip()
            
            if not comment_text:
                flash('Comment cannot be empty', 'error')
                return redirect(url_for('user_hitl_detail', task_id=task_id))
            
            manager = HITLManager(self.db_facade)
            manager.add_comment(task_id, user_id, comment_text)
            self.log_audit('comment_hitl', 'hitl_task', task_id)
            
            flash('Comment added', 'success')
            return redirect(url_for('user_hitl_detail', task_id=task_id))
        
        @self.app.route('/user/hitl/<task_id>/resolve', methods=['POST'])
        @login_required
        def user_hitl_resolve(task_id):
            """Resolve (approve/reject) a HITL task."""
            from abhikarta.hitl import HITLManager
            import json
            
            user_id = session.get('user_id')
            resolution = request.form.get('resolution')  # 'approve' or 'reject'
            comment = request.form.get('comment', '').strip()
            response_data_str = request.form.get('response_data', '{}')
            
            try:
                response_data = json.loads(response_data_str) if response_data_str else {}
            except:
                response_data = {'raw_input': response_data_str}
            
            manager = HITLManager(self.db_facade)
            task = manager.get_task(task_id)
            
            if not task:
                flash('Task not found', 'error')
                return redirect(url_for('user_hitl_tasks'))
            
            # Check permission
            is_reviewer = 'hitl_reviewer' in session.get('roles', [])
            is_admin = session.get('is_admin', False)
            
            if task.assigned_to != user_id and not is_reviewer and not is_admin:
                flash('You cannot resolve this task', 'error')
                return redirect(url_for('user_hitl_detail', task_id=task_id))
            
            if resolution == 'approve':
                manager.approve_task(task_id, user_id, response_data, comment)
                flash('Task approved', 'success')
            elif resolution == 'reject':
                manager.reject_task(task_id, user_id, response_data, comment)
                flash('Task rejected', 'warning')
            else:
                flash('Invalid resolution', 'error')
                return redirect(url_for('user_hitl_detail', task_id=task_id))
            
            self.log_audit(f'{resolution}_hitl', 'hitl_task', task_id, 
                          {'comment': comment})
            
            return redirect(url_for('user_hitl_tasks'))
        
        @self.app.route('/user/hitl/<task_id>/assign', methods=['POST'])
        @login_required
        def user_hitl_assign(task_id):
            """Reassign a HITL task (reviewers/admins only)."""
            from abhikarta.hitl import HITLManager
            
            user_id = session.get('user_id')
            is_reviewer = 'hitl_reviewer' in session.get('roles', [])
            is_admin = session.get('is_admin', False)
            
            if not is_reviewer and not is_admin:
                flash('You cannot reassign tasks', 'error')
                return redirect(url_for('user_hitl_detail', task_id=task_id))
            
            assign_to = request.form.get('assign_to')
            reason = request.form.get('reason', '').strip()
            
            if not assign_to:
                flash('Please select a user', 'error')
                return redirect(url_for('user_hitl_detail', task_id=task_id))
            
            manager = HITLManager(self.db_facade)
            manager.assign_task(task_id, assign_to, user_id, reason)
            self.log_audit('assign_hitl', 'hitl_task', task_id, 
                          {'assigned_to': assign_to, 'reason': reason})
            
            flash(f'Task assigned to {assign_to}', 'success')
            return redirect(url_for('user_hitl_detail', task_id=task_id))
        
        # =====================================================================
        # Tools Routes
        # =====================================================================
        
        @self.app.route('/tools')
        @login_required
        def tools_list():
            """List all available tools in the tools registry."""
            from abhikarta.tools import get_tools_registry
            from abhikarta.mcp import get_mcp_manager
            
            registry = get_tools_registry()
            mcp_manager = get_mcp_manager()
            
            # Get all tools
            all_tools = registry.list_tools()
            
            # Build tool data with source info
            tools_data = []
            for tool in all_tools:
                source = tool.metadata.source if tool.metadata else 'built-in'
                source_type = 'built-in'
                source_server = None
                
                if source:
                    if source.startswith('mcp:'):
                        source_type = 'mcp'
                        source_server = source.replace('mcp:', '')
                    elif source.startswith('db:'):
                        source_type = 'code_fragment'
                    elif source.startswith('prebuilt:'):
                        source_type = 'prebuilt'
                
                # Get schema for parameters
                schema = tool.get_schema()
                params_list = []
                if schema and schema.parameters:
                    for param in schema.parameters:
                        params_list.append({
                            'name': param.name,
                            'type': param.param_type,
                            'required': param.required,
                            'description': param.description or ''
                        })
                
                tools_data.append({
                    'name': tool.name,
                    'tool_id': tool.tool_id,
                    'description': tool.description or '',
                    'type': tool.tool_type.value if tool.tool_type else 'unknown',
                    'category': tool.category.value if tool.category else 'general',
                    'enabled': tool.is_enabled,
                    'source_type': source_type,
                    'source_server': source_server,
                    'source': source or 'built-in',
                    'parameters': params_list,
                    'version': tool.metadata.version if tool.metadata else '1.0.0'
                })
            
            # Get MCP server stats
            mcp_stats = mcp_manager.get_stats()
            
            # Get registry stats
            registry_stats = registry.get_stats()
            
            return render_template('user/tools.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   tools=tools_data,
                                   mcp_stats=mcp_stats,
                                   registry_stats=registry_stats)
        
        @self.app.route('/tools/<tool_name>')
        @login_required
        def tool_detail(tool_name):
            """View detailed information about a specific tool."""
            from abhikarta.tools import get_tools_registry
            import json
            
            registry = get_tools_registry()
            tool = registry.get(tool_name)
            
            if not tool:
                flash(f'Tool "{tool_name}" not found', 'error')
                return redirect(url_for('tools_list'))
            
            # Get source info - only from metadata
            source = tool.metadata.source if tool.metadata else 'built-in'
            source_type = 'built-in'
            source_server = None
            
            if source:
                if source.startswith('mcp:'):
                    source_type = 'mcp'
                    source_server = source.replace('mcp:', '')
                elif source.startswith('db:'):
                    source_type = 'code_fragment'
                elif source.startswith('prebuilt:'):
                    source_type = 'prebuilt'
            
            # Get schema and parameters
            schema = tool.get_schema()
            parameters = []
            if schema and schema.parameters:
                parameters = schema.parameters
            
            # Get JSON schema for display
            schema_json = json.dumps(schema.to_json_schema() if schema else {}, indent=2)
            
            return render_template('user/tool_detail.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   tool=tool,
                                   source_type=source_type,
                                   source_server=source_server,
                                   parameters=parameters,
                                   schema_json=schema_json)
        
        @self.app.route('/tools/<tool_name>/test')
        @login_required
        def tool_test(tool_name):
            """Test/execute a specific tool."""
            from abhikarta.tools import get_tools_registry
            
            registry = get_tools_registry()
            tool = registry.get(tool_name)
            
            if not tool:
                flash(f'Tool "{tool_name}" not found', 'error')
                return redirect(url_for('tools_list'))
            
            # Get source info - only from metadata
            source = tool.metadata.source if tool.metadata else 'built-in'
            source_type = 'built-in'
            source_server = None
            
            if source:
                if source.startswith('mcp:'):
                    source_type = 'mcp'
                    source_server = source.replace('mcp:', '')
                elif source.startswith('db:'):
                    source_type = 'code_fragment'
                elif source.startswith('prebuilt:'):
                    source_type = 'prebuilt'
            
            # Get schema and parameters
            schema = tool.get_schema()
            parameters = []
            if schema and schema.parameters:
                parameters = schema.parameters
            
            return render_template('user/tool_test.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   tool=tool,
                                   source_type=source_type,
                                   source_server=source_server,
                                   parameters=parameters)
        
        @self.app.route('/api/tools')
        @login_required
        def api_tools_list():
            """API endpoint to get all tools as JSON."""
            from abhikarta.tools import get_tools_registry
            import json
            from flask import jsonify
            
            registry = get_tools_registry()
            catalog = registry.export_catalog()
            
            return jsonify({
                'success': True,
                'tools': catalog,
                'count': len(catalog)
            })
        
        @self.app.route('/api/tools/<tool_name>')
        @login_required
        def api_tool_detail(tool_name):
            """API endpoint to get tool details."""
            from abhikarta.tools import get_tools_registry
            from flask import jsonify
            
            registry = get_tools_registry()
            tool = registry.get(tool_name)
            
            if not tool:
                return jsonify({'success': False, 'error': 'Tool not found'}), 404
            
            schema = tool.get_schema()
            
            return jsonify({
                'success': True,
                'tool': {
                    'name': tool.name,
                    'tool_id': tool.tool_id,
                    'description': tool.description,
                    'type': tool.tool_type.value,
                    'category': tool.category.value,
                    'enabled': tool.is_enabled,
                    'schema': schema.to_json_schema() if schema else None,
                    'metadata': tool.metadata.to_dict() if tool.metadata else None
                }
            })
        
        @self.app.route('/api/tools/<tool_name>/execute', methods=['POST'])
        @login_required
        def api_tool_execute(tool_name):
            """API endpoint to execute a tool."""
            from abhikarta.tools import get_tools_registry
            from flask import jsonify
            
            registry = get_tools_registry()
            tool = registry.get(tool_name)
            
            if not tool:
                return jsonify({'success': False, 'error': 'Tool not found'}), 404
            
            if not tool.is_enabled:
                return jsonify({'success': False, 'error': 'Tool is disabled'}), 400
            
            params = request.get_json() or {}
            
            try:
                result = registry.execute(tool_name, **params)
                return jsonify({
                    'success': result.success,
                    'output': result.output,
                    'error': result.error,
                    'execution_time_ms': result.execution_time_ms
                })
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/tools/refresh-mcp', methods=['POST'])
        @login_required
        def api_refresh_mcp_tools():
            """API endpoint to refresh MCP server tools."""
            from abhikarta.mcp import get_mcp_manager
            from flask import jsonify
            
            if not session.get('is_admin'):
                return jsonify({'success': False, 'error': 'Admin access required'}), 403
            
            manager = get_mcp_manager()
            
            # Check health of all servers and reconnect if needed
            results = {}
            for server_id in manager.get_server_ids():
                server = manager.get_server(server_id)
                if server:
                    healthy, latency = manager.check_health(server_id)
                    if not healthy and server.config.auto_connect:
                        manager.connect_server(server_id)
                        healthy, latency = manager.check_health(server_id)
                    results[server_id] = {
                        'name': server.name,
                        'healthy': healthy,
                        'latency_ms': latency,
                        'tool_count': server.state.tool_count
                    }
            
            return jsonify({
                'success': True,
                'servers': results
            })
        
        logger.info("User routes registered")
