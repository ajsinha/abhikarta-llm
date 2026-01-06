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
            """User dashboard with available entities and recent executions."""
            user_id = session.get('user_id')
            
            # Get published agents available to this user
            agents = []
            try:
                agents = self.db_facade.agents.get_all_agents(status='published')
            except Exception as e:
                logger.error(f"Error getting agents: {e}", exc_info=True)
            
            # Get published workflows
            workflows = []
            try:
                workflows = self.db_facade.fetch_all(
                    "SELECT * FROM workflows WHERE status = 'published' ORDER BY updated_at DESC"
                ) or []
            except Exception as e:
                logger.error(f"Error getting workflows: {e}", exc_info=True)
            
            # Get published swarms
            swarms = []
            try:
                swarms = self.db_facade.fetch_all(
                    "SELECT * FROM swarms WHERE status = 'published' ORDER BY updated_at DESC"
                ) or []
            except Exception as e:
                logger.error(f"Error getting swarms: {e}", exc_info=True)
            
            # Get published AI orgs
            aiorgs = []
            try:
                aiorgs = self.db_facade.fetch_all(
                    "SELECT * FROM ai_orgs WHERE status = 'published' ORDER BY updated_at DESC"
                ) or []
            except Exception as e:
                logger.error(f"Error getting AI orgs: {e}", exc_info=True)
            
            # Get user's recent executions
            executions = []
            try:
                executions = self.db_facade.executions.get_recent_executions(user_id=user_id, limit=10)
            except Exception as e:
                logger.error(f"Error getting executions: {e}", exc_info=True)
            
            return render_template('user/dashboard.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   agents=agents,
                                   workflows=workflows,
                                   swarms=swarms,
                                   aiorgs=aiorgs,
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
                logger.error(f"Error getting agents: {e}", exc_info=True)
            
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
                logger.error(f"Error getting agent: {e}", exc_info=True)
            
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
                logger.error(f"Error getting agent: {e}", exc_info=True)
            
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
                raw_executions = self.db_facade.executions.get_all_executions(user_id=user_id)
                
                # Add entity_type to each execution
                for exec_row in (raw_executions or []):
                    exec_dict = dict(exec_row) if exec_row else {}
                    
                    # Determine entity type from execution ID prefix or metadata
                    execution_id = exec_dict.get('execution_id', '')
                    entity_type = 'agent'  # default
                    
                    # Parse from new traceable execution ID format
                    if execution_id.startswith('wflow_'):
                        entity_type = 'workflow'
                    elif execution_id.startswith('agent_'):
                        entity_type = 'agent'
                    elif execution_id.startswith('swarm_'):
                        entity_type = 'swarm'
                    elif execution_id.startswith('aiorg_'):
                        entity_type = 'aiorg'
                    else:
                        # Fallback: check metadata
                        metadata = exec_dict.get('metadata', '{}')
                        if isinstance(metadata, str):
                            try:
                                metadata = json.loads(metadata)
                            except:
                                metadata = {}
                        
                        if metadata.get('entity_type'):
                            entity_type = metadata['entity_type']
                        elif metadata.get('execution_mode') == 'langgraph':
                            entity_type = 'workflow'
                        else:
                            # Check if agent_id is actually a workflow_id
                            ref_id = exec_dict.get('agent_id')
                            if ref_id:
                                try:
                                    workflow = self.db_facade.fetch_one(
                                        "SELECT workflow_id FROM workflows WHERE workflow_id = ?",
                                        (ref_id,)
                                    )
                                    if workflow:
                                        entity_type = 'workflow'
                                except:
                                    pass
                    
                    exec_dict['entity_type'] = entity_type
                    executions.append(exec_dict)
                    
            except Exception as e:
                logger.error(f"Error getting executions: {e}", exc_info=True)
            
            try:
                # Get swarm executions
                swarm_executions = self.db_facade.fetch_all(
                    """SELECT se.*, s.name as swarm_name 
                       FROM swarm_executions se
                       LEFT JOIN swarms s ON se.swarm_id = s.swarm_id
                       WHERE se.user_id = ?
                       ORDER BY se.started_at DESC
                       LIMIT 100""",
                    (user_id,)
                ) or []
            except Exception as e:
                logger.error(f"Error getting swarm executions: {e}", exc_info=True)
            
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
                logger.error(f"Error getting execution: {e}", exc_info=True)
            
            if not execution:
                flash('Execution not found', 'error')
                return redirect(url_for('user_executions'))
            
            # Get agent info using delegate
            agent = None
            try:
                agent = self.db_facade.agents.get_agent(execution['agent_id'])
            except Exception as e:
                logger.error(f"Error getting agent: {e}", exc_info=True)
            
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
                logger.error(f"Error getting execution: {e}", exc_info=True)
            
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
                logger.error(f"Error getting execution: {e}", exc_info=True)
            
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
                logger.error(f"Error getting execution steps: {e}", exc_info=True)
            
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
        
        @self.app.route('/user/executions/<execution_id>/log')
        @login_required
        def execution_log(execution_id):
            """View detailed execution log file."""
            import json
            from pathlib import Path
            from datetime import datetime
            import os
            
            user_id = session.get('user_id')
            is_admin = session.get('is_admin', False)
            
            # Verify user has access to this execution
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
                logger.error(f"Error getting execution: {e}", exc_info=True)
            
            if not execution:
                flash('Execution not found', 'error')
                return redirect(url_for('user_executions'))
            
            # Convert execution dict to mutable and format datetime fields
            execution = dict(execution) if execution else {}
            
            # Format started_at for template
            if execution.get('started_at'):
                started = execution['started_at']
                if isinstance(started, datetime):
                    execution['started_at_formatted'] = started.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(started, str):
                    execution['started_at_formatted'] = started[:19] if len(started) > 19 else started
                else:
                    execution['started_at_formatted'] = str(started)
            else:
                execution['started_at_formatted'] = 'N/A'
            
            # Determine entity type from execution
            # Note: The executions table uses agent_id to store workflow_id for workflow executions
            # We need to check metadata and validate against actual tables
            entity_type = 'workflow'  # default
            
            # Check metadata for explicit entity type or execution mode
            metadata = execution.get('metadata', {})
            if isinstance(metadata, str):
                try:
                    import json as json_mod
                    metadata = json_mod.loads(metadata)
                except:
                    metadata = {}
            
            execution_mode = metadata.get('execution_mode', '')
            explicit_entity_type = metadata.get('entity_type', '')
            
            if explicit_entity_type:
                entity_type = explicit_entity_type
            elif execution_mode == 'langgraph':
                # LangGraph execution mode is used for workflows
                entity_type = 'workflow'
            elif execution.get('swarm_id'):
                entity_type = 'swarm'
            elif execution.get('aiorg_id'):
                entity_type = 'aiorg'
            else:
                # Check if agent_id is actually a workflow_id or agent_id
                # by looking up in the respective tables
                ref_id = execution.get('agent_id') or execution.get('workflow_id')
                if ref_id:
                    try:
                        # Check workflows table first
                        workflow = self.db_facade.fetch_one(
                            "SELECT workflow_id FROM workflows WHERE workflow_id = ?",
                            (ref_id,)
                        )
                        if workflow:
                            entity_type = 'workflow'
                        else:
                            # Check agents table
                            agent = self.db_facade.fetch_one(
                                "SELECT agent_id FROM agents WHERE agent_id = ?",
                                (ref_id,)
                            )
                            if agent:
                                entity_type = 'agent'
                    except Exception as db_err:
                        logger.warning(f"Error determining entity type: {db_err}")
            
            logger.info(f"Determined entity_type: {entity_type} for execution {execution_id}")
            
            # Try to load execution log
            log_content = None
            log_found = False
            log_error = None
            
            # Try multiple approaches to find the log file
            possible_paths = []
            
            # Get the project root directory (where run_server.py is)
            import sys
            project_root = os.getcwd()  # Usually where server was started
            
            # Also try to find it via the module paths
            for path in sys.path:
                if 'abhikarta' in path.lower() or path.endswith('src'):
                    # Go up to find project root
                    potential_root = os.path.dirname(os.path.dirname(path))
                    if os.path.exists(os.path.join(potential_root, 'executionlog')):
                        project_root = potential_root
                        break
                    # Also try just the parent
                    potential_root = os.path.dirname(path)
                    if os.path.exists(os.path.join(potential_root, 'executionlog')):
                        project_root = potential_root
                        break
            
            # Try to find project root by looking for run_server.py
            for check_dir in [os.getcwd(), os.path.dirname(os.getcwd())] + sys.path[:5]:
                if os.path.exists(os.path.join(check_dir, 'run_server.py')):
                    project_root = check_dir
                    break
                if os.path.exists(os.path.join(check_dir, 'executionlog')):
                    project_root = check_dir
                    break
            
            logger.info(f"Execution log search - Project root: {project_root}, CWD: {os.getcwd()}, Entity: {entity_type}")
            
            # Approach 1: Use the execution logger service with auto-detection
            try:
                from abhikarta.services.execution_logger import get_execution_logger, EntityType
                exec_logger = get_execution_logger()
                
                # First try auto-detection from execution ID (for new traceable IDs)
                auto_result = exec_logger.find_log_file(execution_id)
                if auto_result:
                    detected_type, log_path = auto_result
                    log_data = exec_logger.read_log_file(detected_type, execution_id)
                    if log_data:
                        log_found = True
                        if isinstance(log_data, dict):
                            log_content = json.dumps(log_data, indent=2, default=str)
                        else:
                            log_content = str(log_data)
                        logger.info(f"Found execution log via auto-detection: {log_path} (type: {detected_type.value})")
                        entity_type = detected_type.value  # Update entity_type to detected one
                
                if not log_found:
                    # Map entity type string to EntityType enum
                    entity_type_enum = {
                        'workflow': EntityType.WORKFLOW,
                        'agent': EntityType.AGENT,
                        'swarm': EntityType.SWARM,
                        'aiorg': EntityType.AIORG
                    }.get(entity_type, EntityType.WORKFLOW)
                    
                    # Get path from logger and check with absolute path
                    log_path = exec_logger.get_log_path(entity_type_enum, execution_id)
                    abs_log_path = os.path.abspath(log_path)
                    possible_paths.append(f"Logger: {abs_log_path}")
                    
                    # Try reading via logger
                    log_data = exec_logger.read_log_file(entity_type_enum, execution_id)
                
                    if log_data:
                        log_found = True
                        if isinstance(log_data, dict):
                            log_content = json.dumps(log_data, indent=2, default=str)
                        else:
                            log_content = str(log_data)
                        logger.info(f"Found execution log via logger service: {abs_log_path}")
                    else:
                        # Logger didn't find it, try direct read with absolute path
                        if os.path.exists(abs_log_path):
                            with open(abs_log_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            try:
                                log_data = json.loads(content)
                                log_content = json.dumps(log_data, indent=2, default=str)
                            except json.JSONDecodeError:
                                log_content = content
                            log_found = True
                            logger.info(f"Found execution log via direct read: {abs_log_path}")
                    
            except ImportError as ie:
                logger.warning(f"Execution logger import failed: {ie}")
            except Exception as e:
                logger.warning(f"Execution logger read failed: {e}")
            
            # Approach 2: Direct file search if logger didn't find it
            if not log_found:
                # Build list of base paths to search
                base_paths = [
                    os.path.join(project_root, 'executionlog'),
                    'executionlog',
                    './executionlog',
                    os.path.join(os.getcwd(), 'executionlog'),
                    os.path.abspath('executionlog'),
                ]
                
                # Also check parent directories
                current = os.getcwd()
                for _ in range(3):  # Go up 3 levels max
                    parent = os.path.dirname(current)
                    if parent != current:
                        base_paths.append(os.path.join(parent, 'executionlog'))
                        current = parent
                
                # Remove duplicates while preserving order
                seen = set()
                unique_base_paths = []
                for p in base_paths:
                    abs_p = os.path.abspath(p)
                    if abs_p not in seen:
                        seen.add(abs_p)
                        unique_base_paths.append(p)
                
                for base in unique_base_paths:
                    for ext in ['.json', '.log']:
                        check_path = os.path.join(base, entity_type, f"{execution_id}{ext}")
                        abs_check_path = os.path.abspath(check_path)
                        possible_paths.append(abs_check_path)
                        
                        logger.debug(f"Checking path: {abs_check_path} (exists: {os.path.exists(abs_check_path)})")
                        
                        if os.path.exists(abs_check_path):
                            try:
                                with open(abs_check_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                # Try to parse as JSON
                                if ext == '.json':
                                    try:
                                        log_data = json.loads(content)
                                        log_content = json.dumps(log_data, indent=2, default=str)
                                    except json.JSONDecodeError:
                                        log_content = content
                                else:
                                    log_content = content
                                
                                log_found = True
                                logger.info(f"Found execution log at: {abs_check_path}")
                                break
                            except Exception as read_err:
                                logger.warning(f"Failed to read {abs_check_path}: {read_err}")
                    
                    if log_found:
                        break
            
            if not log_found:
                # List files in executionlog directory for debugging
                debug_info = []
                for base in ['executionlog', os.path.join(project_root, 'executionlog')]:
                    entity_dir = os.path.join(base, entity_type)
                    if os.path.exists(entity_dir):
                        try:
                            files = os.listdir(entity_dir)[:5]  # First 5 files
                            debug_info.append(f"Files in {entity_dir}: {files}")
                        except:
                            pass
                
                log_error = (
                    f"Execution log file not found for execution {execution_id}.\n\n"
                    f"Entity type: {entity_type}\n"
                    f"Working directory: {os.getcwd()}\n\n"
                    f"Searched paths:\n" + "\n".join(f"  • {p}" for p in possible_paths[:8]) +
                    (f"\n\nDebug info:\n" + "\n".join(debug_info) if debug_info else "") +
                    f"\n\nLog files are generated for executions started after v1.5.1."
                )
                logger.warning(f"Execution log not found. Entity: {entity_type}, ID: {execution_id}")
            
            return render_template('user/execution_log.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   execution=execution,
                                   entity_type=entity_type,
                                   log_content=log_content,
                                   log_found=log_found,
                                   log_error=log_error)
        
        @self.app.route('/api/executions/<execution_id>/log')
        @login_required
        def api_execution_log(execution_id):
            """API endpoint to get execution log as JSON."""
            from flask import jsonify
            import json
            import os
            import sys
            
            user_id = session.get('user_id')
            is_admin = session.get('is_admin', False)
            
            # Verify user has access
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
                return jsonify({'success': False, 'error': str(e)}), 500
            
            if not execution:
                return jsonify({'success': False, 'error': 'Execution not found'}), 404
            
            # Determine entity type - check metadata and validate against tables
            entity_type = 'workflow'  # default
            
            # Check metadata for explicit entity type or execution mode
            metadata = execution.get('metadata', {})
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}
            
            execution_mode = metadata.get('execution_mode', '')
            explicit_entity_type = metadata.get('entity_type', '')
            
            if explicit_entity_type:
                entity_type = explicit_entity_type
            elif execution_mode == 'langgraph':
                entity_type = 'workflow'
            elif execution.get('swarm_id'):
                entity_type = 'swarm'
            elif execution.get('aiorg_id'):
                entity_type = 'aiorg'
            else:
                # Check if agent_id is actually a workflow_id
                ref_id = execution.get('agent_id') or execution.get('workflow_id')
                if ref_id:
                    try:
                        workflow = self.db_facade.fetch_one(
                            "SELECT workflow_id FROM workflows WHERE workflow_id = ?",
                            (ref_id,)
                        )
                        if workflow:
                            entity_type = 'workflow'
                        else:
                            agent = self.db_facade.fetch_one(
                                "SELECT agent_id FROM agents WHERE agent_id = ?",
                                (ref_id,)
                            )
                            if agent:
                                entity_type = 'agent'
                    except:
                        pass
            
            log_data = None
            possible_paths = []
            
            # Find project root
            project_root = os.getcwd()
            for check_dir in [os.getcwd()] + sys.path[:5]:
                if os.path.exists(os.path.join(check_dir, 'run_server.py')) or \
                   os.path.exists(os.path.join(check_dir, 'executionlog')):
                    project_root = check_dir
                    break
            
            # Approach 1: Try execution logger service
            try:
                from abhikarta.services.execution_logger import get_execution_logger, EntityType
                exec_logger = get_execution_logger()
                
                entity_type_enum = {
                    'workflow': EntityType.WORKFLOW,
                    'agent': EntityType.AGENT,
                    'swarm': EntityType.SWARM,
                    'aiorg': EntityType.AIORG
                }.get(entity_type, EntityType.WORKFLOW)
                
                log_path = exec_logger.get_log_path(entity_type_enum, execution_id)
                abs_log_path = os.path.abspath(log_path)
                possible_paths.append(abs_log_path)
                
                log_data = exec_logger.read_log_file(entity_type_enum, execution_id)
                
                # Try direct read if logger didn't find it
                if not log_data and os.path.exists(abs_log_path):
                    with open(abs_log_path, 'r', encoding='utf-8') as f:
                        log_data = json.load(f)
                    
            except ImportError:
                pass
            except Exception as e:
                logger.warning(f"Execution logger read failed: {e}")
            
            # Approach 2: Direct file search
            if not log_data:
                base_paths = [
                    os.path.join(project_root, 'executionlog'),
                    'executionlog',
                    './executionlog',
                    os.path.join(os.getcwd(), 'executionlog'),
                ]
                
                for base in base_paths:
                    for ext in ['.json', '.log']:
                        check_path = os.path.join(base, entity_type, f"{execution_id}{ext}")
                        possible_paths.append(check_path)
                        
                        if os.path.exists(check_path):
                            try:
                                with open(check_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                if ext == '.json':
                                    log_data = json.loads(content)
                                else:
                                    log_data = {'content': content}
                                break
                            except Exception as read_err:
                                logger.warning(f"Failed to read {check_path}: {read_err}")
                    
                    if log_data:
                        break
            
            if log_data:
                return jsonify({
                    'success': True,
                    'execution_id': execution_id,
                    'entity_type': entity_type,
                    'log': log_data
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Execution log not found',
                    'searched_paths': possible_paths[:5],
                    'message': 'Log files are generated for executions started after v1.5.1'
                }), 404
        
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
            status_filter = request.args.get('status', '')
            
            manager = HITLManager(self.db_facade)
            
            # Always include unassigned tasks so users can claim them
            # This allows any user to see and respond to HITL tasks
            tasks = manager.get_user_tasks(user_id, status=status_filter if status_filter else None, 
                                          include_unassigned=True)
            stats = manager.get_stats(user_id)
            
            return render_template('user/hitl_tasks.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   tasks=tasks,
                                   stats=stats,
                                   is_reviewer=is_reviewer,
                                   status_filter=status_filter)
        
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
            from abhikarta.tools.tool_documentation import get_tool_documentation
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
            
            # Get tool documentation (sample input/output, detailed description)
            tool_doc = get_tool_documentation(tool_name, tool)
            
            return render_template('user/tool_detail.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   tool=tool,
                                   source_type=source_type,
                                   source_server=source_server,
                                   parameters=parameters,
                                   schema_json=schema_json,
                                   tool_doc=tool_doc)
        
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
                logger.error(f"Tool execution error: {e}", exc_info=True)
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
        
        # ======================================================================
        # USER CODE FRAGMENTS ROUTES (v1.4.8)
        # ======================================================================
        
        @self.app.route('/user/code-fragments')
        @login_required
        def user_code_fragments():
            """Display user's code fragments."""
            user_id = session.get('user_id')
            
            try:
                fragments = self.db_facade.code_fragments.get_user_fragments(user_id)
                categories = self.db_facade.code_fragments.get_categories()
                status_counts = self.db_facade.code_fragments.get_user_fragment_stats(user_id)
                
                return render_template('user/code_fragments.html',
                                       fragments=fragments,
                                       categories=categories,
                                       status_counts=status_counts)
            except Exception as e:
                logger.error(f"Error loading user code fragments: {e}", exc_info=True)
                flash('Error loading code fragments', 'error')
                return redirect(url_for('user_dashboard'))
        
        @self.app.route('/user/code-fragments/create', methods=['GET', 'POST'])
        @login_required
        def create_code_fragment():
            """Create a new code fragment."""
            user_id = session.get('user_id')
            
            if request.method == 'POST':
                name = request.form.get('name', '').strip()
                module_name = request.form.get('module_name', '').strip()
                description = request.form.get('description', '').strip()
                language = request.form.get('language', 'python')
                code = request.form.get('code', '')
                version = request.form.get('version', '1.0.0')
                category = request.form.get('category', 'general')
                tags_str = request.form.get('tags', '')
                dependencies_str = request.form.get('dependencies', '')
                entry_point = request.form.get('entry_point', '').strip()
                
                # Validation
                if not name:
                    flash('Fragment name is required', 'error')
                    return render_template('user/create_code_fragment.html',
                                           categories=self.db_facade.code_fragments.get_categories())
                
                if not code:
                    flash('Fragment code is required', 'error')
                    return render_template('user/create_code_fragment.html',
                                           categories=self.db_facade.code_fragments.get_categories())
                
                # Generate module_name if not provided
                if not module_name:
                    module_name = self.db_facade.code_fragments.name_to_module_name(name)
                
                # Validate module_name is a valid Python identifier
                if not self.db_facade.code_fragments.is_valid_python_identifier(module_name):
                    flash(f'Invalid module name: "{module_name}". Must be a valid Python identifier.', 'error')
                    return render_template('user/create_code_fragment.html',
                                           categories=self.db_facade.code_fragments.get_categories())
                
                # Check for duplicate module_name
                if self.db_facade.code_fragments.module_name_exists(module_name):
                    flash(f'Module name "{module_name}" already exists. Please choose a different name.', 'error')
                    return render_template('user/create_code_fragment.html',
                                           categories=self.db_facade.code_fragments.get_categories())
                
                # Parse tags and dependencies
                import json
                try:
                    tags = json.dumps([t.strip() for t in tags_str.split(',') if t.strip()]) if tags_str else '[]'
                    dependencies = json.dumps([d.strip() for d in dependencies_str.split(',') if d.strip()]) if dependencies_str else '[]'
                except:
                    tags = '[]'
                    dependencies = '[]'
                
                try:
                    fragment_id = self.db_facade.code_fragments.create_fragment(
                        name=name,
                        module_name=module_name,
                        description=description,
                        language=language,
                        code=code,
                        version=version,
                        category=category,
                        tags=tags,
                        dependencies=dependencies,
                        entry_point=entry_point,
                        created_by=user_id,
                        status='draft',
                        source='web'
                    )
                    
                    if fragment_id:
                        self.log_audit('create_code_fragment', 'code_fragment', fragment_id)
                        flash('Code fragment created successfully', 'success')
                        return redirect(url_for('user_view_code_fragment', fragment_id=fragment_id))
                    else:
                        flash('Error creating code fragment', 'error')
                except Exception as e:
                    logger.error(f"Error creating code fragment: {e}", exc_info=True)
                    flash(f'Error creating code fragment: {str(e)}', 'error')
            
            categories = self.db_facade.code_fragments.get_categories()
            return render_template('user/create_code_fragment.html',
                                   categories=categories)
        
        @self.app.route('/user/code-fragments/<fragment_id>')
        @login_required
        def user_view_code_fragment(fragment_id):
            """View a code fragment."""
            user_id = session.get('user_id')
            
            try:
                fragment = self.db_facade.code_fragments.get_fragment(fragment_id)
                
                if not fragment:
                    flash('Code fragment not found', 'error')
                    return redirect(url_for('user_code_fragments'))
                
                # Check ownership (users can only view their own drafts/pending, but can view any approved/published)
                is_owner = fragment.get('created_by') == user_id
                is_public = fragment.get('status') in ('approved', 'published')
                
                if not is_owner and not is_public:
                    flash('You do not have permission to view this fragment', 'error')
                    return redirect(url_for('user_code_fragments'))
                
                return render_template('user/view_code_fragment.html',
                                       fragment=fragment,
                                       is_owner=is_owner)
            except Exception as e:
                logger.error(f"Error viewing code fragment: {e}", exc_info=True)
                flash('Error loading code fragment', 'error')
                return redirect(url_for('user_code_fragments'))
        
        @self.app.route('/user/code-fragments/<fragment_id>/edit', methods=['GET', 'POST'])
        @login_required
        def user_edit_code_fragment(fragment_id):
            """Edit a code fragment (only owner and only if status allows)."""
            user_id = session.get('user_id')
            
            try:
                fragment = self.db_facade.code_fragments.get_fragment(fragment_id)
                
                if not fragment:
                    flash('Code fragment not found', 'error')
                    return redirect(url_for('user_code_fragments'))
                
                # Check ownership
                if fragment.get('created_by') != user_id:
                    flash('You can only edit your own code fragments', 'error')
                    return redirect(url_for('user_code_fragments'))
                
                # Check if editable (draft or testing only)
                if fragment.get('status') not in ('draft', 'testing'):
                    flash('This code fragment cannot be edited in its current status', 'warning')
                    return redirect(url_for('user_view_code_fragment', fragment_id=fragment_id))
                
                if request.method == 'POST':
                    name = request.form.get('name', '').strip()
                    description = request.form.get('description', '').strip()
                    language = request.form.get('language', 'python')
                    code = request.form.get('code', '')
                    version = request.form.get('version', fragment.get('version', '1.0.0'))
                    category = request.form.get('category', 'general')
                    tags_str = request.form.get('tags', '')
                    dependencies_str = request.form.get('dependencies', '')
                    
                    # Validation
                    if not name:
                        flash('Fragment name is required', 'error')
                        return render_template('user/edit_code_fragment.html',
                                               fragment=fragment,
                                               categories=self.db_facade.code_fragments.get_categories())
                    
                    if self.db_facade.code_fragments.name_exists(name, exclude_id=fragment_id):
                        flash('Fragment name already exists', 'error')
                        return render_template('user/edit_code_fragment.html',
                                               fragment=fragment,
                                               categories=self.db_facade.code_fragments.get_categories())
                    
                    import json
                    try:
                        tags = json.dumps([t.strip() for t in tags_str.split(',') if t.strip()]) if tags_str else '[]'
                        dependencies = json.dumps([d.strip() for d in dependencies_str.split(',') if d.strip()]) if dependencies_str else '[]'
                    except:
                        tags = fragment.get('tags', '[]')
                        dependencies = fragment.get('dependencies', '[]')
                    
                    success = self.db_facade.code_fragments.update_fragment(
                        fragment_id,
                        updated_by=user_id,
                        name=name,
                        description=description,
                        language=language,
                        code=code,
                        version=version,
                        category=category,
                        tags=tags,
                        dependencies=dependencies
                    )
                    
                    if success:
                        self.log_audit('update_code_fragment', 'code_fragment', fragment_id)
                        flash('Code fragment updated successfully', 'success')
                        return redirect(url_for('user_view_code_fragment', fragment_id=fragment_id))
                    else:
                        flash('Error updating code fragment', 'error')
                
                categories = self.db_facade.code_fragments.get_categories()
                return render_template('user/edit_code_fragment.html',
                                       fragment=fragment,
                                       categories=categories)
            except Exception as e:
                logger.error(f"Error editing code fragment: {e}", exc_info=True)
                flash('Error loading code fragment', 'error')
                return redirect(url_for('user_code_fragments'))
        
        @self.app.route('/user/code-fragments/<fragment_id>/submit', methods=['POST'])
        @login_required
        def submit_code_fragment_for_review(fragment_id):
            """Submit a code fragment for admin review."""
            user_id = session.get('user_id')
            
            try:
                fragment = self.db_facade.code_fragments.get_fragment(fragment_id)
                
                if not fragment:
                    flash('Code fragment not found', 'error')
                    return redirect(url_for('user_code_fragments'))
                
                # Check ownership
                if fragment.get('created_by') != user_id:
                    flash('You can only submit your own code fragments', 'error')
                    return redirect(url_for('user_code_fragments'))
                
                # Check current status
                if fragment.get('status') not in ('draft', 'testing'):
                    flash('This code fragment cannot be submitted for review', 'warning')
                    return redirect(url_for('user_view_code_fragment', fragment_id=fragment_id))
                
                success = self.db_facade.code_fragments.submit_for_review(fragment_id, user_id)
                
                if success:
                    self.log_audit('submit_code_fragment_review', 'code_fragment', fragment_id)
                    flash('Code fragment submitted for review', 'success')
                else:
                    flash('Error submitting code fragment for review', 'error')
                
                return redirect(url_for('user_view_code_fragment', fragment_id=fragment_id))
            except Exception as e:
                logger.error(f"Error submitting code fragment for review: {e}", exc_info=True)
                flash('Error submitting for review', 'error')
                return redirect(url_for('user_code_fragments'))
        
        @self.app.route('/user/code-fragments/<fragment_id>/delete', methods=['POST'])
        @login_required
        def delete_user_code_fragment(fragment_id):
            """Delete a code fragment (only owner and only if draft)."""
            user_id = session.get('user_id')
            
            try:
                fragment = self.db_facade.code_fragments.get_fragment(fragment_id)
                
                if not fragment:
                    flash('Code fragment not found', 'error')
                    return redirect(url_for('user_code_fragments'))
                
                # Check ownership
                if fragment.get('created_by') != user_id:
                    flash('You can only delete your own code fragments', 'error')
                    return redirect(url_for('user_code_fragments'))
                
                # Only allow deletion of drafts
                if fragment.get('status') != 'draft':
                    flash('Only draft code fragments can be deleted', 'warning')
                    return redirect(url_for('user_view_code_fragment', fragment_id=fragment_id))
                
                success = self.db_facade.code_fragments.delete_fragment(fragment_id)
                
                if success:
                    self.log_audit('delete_code_fragment', 'code_fragment', fragment_id)
                    flash('Code fragment deleted', 'success')
                else:
                    flash('Error deleting code fragment', 'error')
                
                return redirect(url_for('user_code_fragments'))
            except Exception as e:
                logger.error(f"Error deleting code fragment: {e}", exc_info=True)
                flash('Error deleting code fragment', 'error')
                return redirect(url_for('user_code_fragments'))
        
        @self.app.route('/user/code-fragments/browse')
        @login_required
        def browse_code_fragments():
            """Browse approved/published code fragments."""
            category = request.args.get('category')
            language = request.args.get('language')
            
            try:
                fragments = self.db_facade.code_fragments.get_usable_fragments(
                    category=category,
                    language=language
                )
                categories = self.db_facade.code_fragments.get_categories()
                
                return render_template('user/browse_code_fragments.html',
                                       fragments=fragments,
                                       categories=categories,
                                       selected_category=category,
                                       selected_language=language)
            except Exception as e:
                logger.error(f"Error browsing code fragments: {e}", exc_info=True)
                flash('Error loading code fragments', 'error')
                return redirect(url_for('user_dashboard'))
        
        logger.info("User routes registered")
