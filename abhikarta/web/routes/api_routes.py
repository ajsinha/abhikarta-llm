"""
API Routes Module - Handles REST API endpoints

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

from flask import request, jsonify, session, g, current_app
import logging
import json
import hashlib
from datetime import datetime
from functools import wraps

from .abstract_routes import AbstractRoutes

logger = logging.getLogger(__name__)


def validate_api_key(api_key):
    """
    Validate an API key and return the associated user info.
    
    Args:
        api_key: The raw API key string
        
    Returns:
        dict with user info if valid, None otherwise
    """
    if not api_key or not api_key.startswith('abk_'):
        return None
    
    try:
        from abhikarta.database import get_db_facade
        db = get_db_facade()
        
        # Hash the key to compare with stored hash
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Look up the key
        result = db.fetch_one(
            """SELECT ak.*, u.fullname, u.is_active as user_is_active
               FROM api_keys ak
               JOIN users u ON ak.user_id = u.user_id
               WHERE ak.key_hash = ? AND ak.is_active = 1""",
            (key_hash,)
        )
        
        if not result:
            return None
        
        # Check if key is expired
        if result.get('expires_at'):
            expires_at = result['expires_at']
            if isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            if datetime.now() > expires_at:
                return None
        
        # Check if user is active
        if not result.get('user_is_active'):
            return None
        
        # Update usage stats
        db.execute(
            """UPDATE api_keys 
               SET usage_count = usage_count + 1, last_used_at = ? 
               WHERE key_id = ?""",
            (datetime.now().isoformat(), result['key_id'])
        )
        
        # Get user roles
        roles = db.fetch_all(
            "SELECT role_name FROM user_roles WHERE user_id = ?",
            (result['user_id'],)
        )
        role_names = [r['role_name'] for r in roles] if roles else []
        
        return {
            'user_id': result['user_id'],
            'fullname': result['fullname'],
            'key_id': result['key_id'],
            'key_name': result['name'],
            'roles': role_names,
            'is_admin': 'super_admin' in role_names or 'domain_admin' in role_names,
            'rate_limit': result.get('rate_limit', 1000)
        }
        
    except Exception as e:
        logger.error(f"Error validating API key: {e}", exc_info=True)
        return None


def get_api_auth():
    """
    Get authentication info from either session or API key.
    
    Returns:
        dict with user info if authenticated, None otherwise
    """
    # First check for API key in headers
    api_key = request.headers.get('Authorization', '')
    if api_key.startswith('Bearer '):
        api_key = api_key[7:]
    elif not api_key:
        api_key = request.headers.get('X-API-Key', '')
    
    if api_key:
        return validate_api_key(api_key)
    
    # Fall back to session authentication
    if 'user_id' in session:
        return {
            'user_id': session.get('user_id'),
            'fullname': session.get('fullname'),
            'roles': session.get('roles', []),
            'is_admin': session.get('is_admin', False),
            'key_id': None
        }
    
    return None


def api_login_required(f):
    """Decorator to require authentication for API endpoints (session or API key)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_info = get_api_auth()
        if not auth_info:
            return jsonify({
                'success': False,
                'error': {'code': 'AUTH_001', 'message': 'Authentication required. Use session cookie or API key.'},
                'timestamp': datetime.now().isoformat()
            }), 401
        
        # Store auth info in flask.g for use in the endpoint
        g.auth = auth_info
        return f(*args, **kwargs)
    return decorated_function


def api_admin_required(f):
    """Decorator to require admin role for API endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_info = get_api_auth()
        if not auth_info:
            return jsonify({
                'success': False,
                'error': {'code': 'AUTH_001', 'message': 'Authentication required'},
                'timestamp': datetime.now().isoformat()
            }), 401
        if not auth_info.get('is_admin', False):
            return jsonify({
                'success': False,
                'error': {'code': 'AUTH_002', 'message': 'Admin access required'},
                'timestamp': datetime.now().isoformat()
            }), 403
        
        g.auth = auth_info
        return f(*args, **kwargs)
    return decorated_function


class APIRoutes(AbstractRoutes):
    """
    Handles REST API endpoints for the application.
    
    This class manages JSON API endpoints for programmatic access.
    
    Attributes:
        app: Flask application instance
        db_facade: DatabaseFacade instance for database operations
        user_facade: UserFacade instance for user operations
    """
    
    def __init__(self, app):
        """
        Initialize APIRoutes.
        
        Args:
            app: Flask application instance
        """
        super().__init__(app)
        logger.info("APIRoutes initialized")
    
    def _success_response(self, data=None, message=None):
        """Generate success response."""
        response = {
            'success': True,
            'timestamp': datetime.now().isoformat()
        }
        if data is not None:
            response['data'] = data
        if message:
            response['message'] = message
        return jsonify(response)
    
    def _error_response(self, code, message, status_code=400):
        """Generate error response."""
        return jsonify({
            'success': False,
            'error': {'code': code, 'message': message},
            'timestamp': datetime.now().isoformat()
        }), status_code
    
    def register_routes(self):
        """Register all API routes."""
        
        # ==================== Authentication API ====================
        
        @self.app.route('/api/auth/session', methods=['GET'])
        def api_get_session():
            """Get current session information."""
            if 'user_id' not in session:
                return self._error_response('AUTH_001', 'Not authenticated', 401)
            
            return self._success_response({
                'user_id': session.get('user_id'),
                'fullname': session.get('fullname'),
                'email': session.get('email'),
                'roles': session.get('roles', []),
                'is_admin': session.get('is_admin', False)
            })
        
        @self.app.route('/api/auth/login', methods=['POST'])
        def api_login():
            """API login endpoint."""
            data = request.get_json() or {}
            user_id = data.get('user_id', '').strip()
            password = data.get('password', '')
            
            if not user_id or not password:
                return self._error_response('AUTH_003', 'User ID and password required')
            
            user = self.user_facade.authenticate(user_id, password)
            if user:
                session['user_id'] = user['user_id']
                session['fullname'] = user.get('fullname', user_id)
                session['email'] = user.get('email', '')
                session['roles'] = user.get('roles', [])
                session['is_admin'] = self.user_facade.is_admin(user_id)
                
                return self._success_response({
                    'user_id': user['user_id'],
                    'fullname': user.get('fullname'),
                    'roles': user.get('roles', [])
                }, 'Login successful')
            
            return self._error_response('AUTH_004', 'Invalid credentials', 401)
        
        @self.app.route('/api/auth/logout', methods=['POST'])
        def api_logout():
            """API logout endpoint."""
            session.clear()
            return self._success_response(message='Logout successful')
        
        # ==================== Users API ====================
        
        @self.app.route('/api/users', methods=['GET'])
        @api_admin_required
        def api_list_users():
            """List all users."""
            users = self.user_facade.list_users()
            return self._success_response(users)
        
        # Note: GET /api/users/<user_id> is defined in admin_routes.py
        
        @self.app.route('/api/users', methods=['POST'])
        @api_admin_required
        def api_create_user():
            """Create a new user."""
            data = request.get_json() or {}
            
            if not data.get('user_id') or not data.get('password'):
                return self._error_response('USER_002', 'User ID and password required')
            
            if self.user_facade.create_user(data):
                return self._success_response(
                    self.user_facade.get_user(data['user_id']),
                    'User created successfully'
                )
            return self._error_response('USER_003', 'User already exists')
        
        @self.app.route('/api/users/<user_id>', methods=['PUT'])
        @api_admin_required
        def api_update_user(user_id):
            """Update a user."""
            data = request.get_json() or {}
            
            if self.user_facade.update_user(user_id, data):
                return self._success_response(
                    self.user_facade.get_user(user_id),
                    'User updated successfully'
                )
            return self._error_response('USER_001', 'User not found', 404)
        
        @self.app.route('/api/users/<user_id>', methods=['DELETE'])
        @api_admin_required
        def api_delete_user(user_id):
            """Delete a user."""
            if self.user_facade.delete_user(user_id):
                return self._success_response(message='User deleted successfully')
            return self._error_response('USER_001', 'User not found', 404)
        
        # ==================== Agents API ====================
        
        @self.app.route('/api/agents', methods=['GET'])
        @api_login_required
        def api_list_agents():
            """List agents."""
            is_admin = session.get('is_admin', False)
            
            try:
                if is_admin:
                    agents = self.db_facade.fetch_all(
                        "SELECT * FROM agents ORDER BY created_at DESC"
                    )
                else:
                    agents = self.db_facade.fetch_all(
                        "SELECT * FROM agents WHERE status = 'published' ORDER BY name"
                    )
                return self._success_response(agents)
            except Exception as e:
                logger.error(f"Error listing agents: {e}", exc_info=True)
                return self._error_response('AGENT_001', 'Failed to list agents', 500)
        
        @self.app.route('/api/agents/<agent_id>', methods=['GET'])
        @api_login_required
        def api_get_agent(agent_id):
            """Get agent by ID."""
            try:
                agent = self.db_facade.fetch_one(
                    "SELECT * FROM agents WHERE agent_id = ?",
                    (agent_id,)
                )
                if agent:
                    return self._success_response(agent)
                return self._error_response('AGENT_002', 'Agent not found', 404)
            except Exception as e:
                logger.error(f"Error getting agent: {e}", exc_info=True)
                return self._error_response('AGENT_001', 'Failed to get agent', 500)
        
        @self.app.route('/api/agents', methods=['POST'])
        @api_admin_required
        def api_create_agent():
            """Create a new agent."""
            import uuid
            data = request.get_json() or {}
            
            if not data.get('name'):
                return self._error_response('AGENT_003', 'Agent name required')
            
            agent_id = f"agent_{uuid.uuid4().hex[:12]}"
            
            try:
                self.db_facade.execute(
                    """INSERT INTO agents 
                       (agent_id, name, description, agent_type, config, status, created_by)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (agent_id, data.get('name'), data.get('description', ''),
                     data.get('agent_type', 'react'), 
                     json.dumps(data.get('config', {})), 'draft',
                     session.get('user_id'))
                )
                
                agent = self.db_facade.fetch_one(
                    "SELECT * FROM agents WHERE agent_id = ?",
                    (agent_id,)
                )
                return self._success_response(agent, 'Agent created successfully')
            except Exception as e:
                logger.error(f"Error creating agent: {e}", exc_info=True)
                return self._error_response('AGENT_001', 'Failed to create agent', 500)
        
        @self.app.route('/api/agents/<agent_id>', methods=['PUT'])
        @api_admin_required
        def api_update_agent(agent_id):
            """Update an agent."""
            data = request.get_json() or {}
            
            try:
                self.db_facade.execute(
                    """UPDATE agents 
                       SET name = ?, description = ?, agent_type = ?, config = ?,
                           updated_at = ?
                       WHERE agent_id = ?""",
                    (data.get('name'), data.get('description'),
                     data.get('agent_type'), json.dumps(data.get('config', {})),
                     datetime.now().isoformat(), agent_id)
                )
                
                agent = self.db_facade.fetch_one(
                    "SELECT * FROM agents WHERE agent_id = ?",
                    (agent_id,)
                )
                if agent:
                    return self._success_response(agent, 'Agent updated successfully')
                return self._error_response('AGENT_002', 'Agent not found', 404)
            except Exception as e:
                logger.error(f"Error updating agent: {e}", exc_info=True)
                return self._error_response('AGENT_001', 'Failed to update agent', 500)
        
        # Note: DELETE /api/agents/<agent_id> is defined in agent_routes.py
        
        @self.app.route('/api/agents/<agent_id>/execute', methods=['POST'])
        @api_login_required
        def api_execute_agent(agent_id):
            """Execute an agent."""
            import uuid
            data = request.get_json() or {}
            
            try:
                agent = self.db_facade.fetch_one(
                    "SELECT * FROM agents WHERE agent_id = ? AND status = 'published'",
                    (agent_id,)
                )
                
                if not agent:
                    return self._error_response('AGENT_004', 'Agent not available', 404)
                
                execution_id = f"exec_{uuid.uuid4().hex[:16]}"
                
                self.db_facade.execute(
                    """INSERT INTO executions 
                       (execution_id, agent_id, user_id, status, input_data, started_at)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (execution_id, agent_id, session.get('user_id'), 'pending',
                     json.dumps(data.get('input', {})), datetime.now().isoformat())
                )
                
                return self._success_response({
                    'execution_id': execution_id,
                    'agent_id': agent_id,
                    'status': 'pending'
                }, 'Execution started')
            except Exception as e:
                logger.error(f"Error executing agent: {e}", exc_info=True)
                return self._error_response('EXEC_001', 'Failed to execute agent', 500)
        
        # ==================== Executions API ====================
        
        @self.app.route('/api/executions', methods=['GET'])
        @api_login_required
        def api_list_executions():
            """List executions."""
            user_id = session.get('user_id')
            is_admin = session.get('is_admin', False)
            
            try:
                if is_admin:
                    executions = self.db_facade.fetch_all(
                        "SELECT * FROM executions ORDER BY started_at DESC LIMIT 100"
                    )
                else:
                    executions = self.db_facade.fetch_all(
                        "SELECT * FROM executions WHERE user_id = ? ORDER BY started_at DESC",
                        (user_id,)
                    )
                return self._success_response(executions)
            except Exception as e:
                logger.error(f"Error listing executions: {e}", exc_info=True)
                return self._error_response('EXEC_002', 'Failed to list executions', 500)
        
        @self.app.route('/api/executions/<execution_id>', methods=['GET'])
        @api_login_required
        def api_get_execution(execution_id):
            """Get execution by ID."""
            user_id = session.get('user_id')
            is_admin = session.get('is_admin', False)
            
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
                
                if execution:
                    # Parse JSON fields
                    if execution.get('input_data'):
                        try:
                            execution['input_data'] = json.loads(execution['input_data'])
                        except:
                            pass
                    if execution.get('output_data'):
                        try:
                            execution['output_data'] = json.loads(execution['output_data'])
                        except:
                            pass
                    return jsonify({'success': True, 'execution': execution})
                return self._error_response('EXEC_003', 'Execution not found', 404)
            except Exception as e:
                logger.error(f"Error getting execution: {e}", exc_info=True)
                return self._error_response('EXEC_002', 'Failed to get execution', 500)
        
        @self.app.route('/api/executions/<execution_id>/status', methods=['GET'])
        @api_login_required
        def api_get_execution_status(execution_id):
            """Get execution status for progress monitoring."""
            user_id = session.get('user_id')
            is_admin = session.get('is_admin', False)
            
            try:
                if is_admin:
                    execution = self.db_facade.fetch_one(
                        "SELECT status, duration_ms, total_tokens, error_message FROM executions WHERE execution_id = ?",
                        (execution_id,)
                    )
                else:
                    execution = self.db_facade.fetch_one(
                        "SELECT status, duration_ms, total_tokens, error_message FROM executions WHERE execution_id = ? AND user_id = ?",
                        (execution_id, user_id)
                    )
                
                if not execution:
                    return jsonify({'status': 'not_found'})
                
                # Get step counts
                steps = self.db_facade.fetch_all(
                    "SELECT status FROM execution_steps WHERE execution_id = ?",
                    (execution_id,)
                ) or []
                
                total_steps = len(steps)
                completed_steps = len([s for s in steps if s.get('status') == 'completed'])
                progress = int((completed_steps / total_steps) * 100) if total_steps > 0 else 0
                
                return jsonify({
                    'status': execution.get('status'),
                    'progress': progress,
                    'completed_steps': completed_steps,
                    'total_steps': total_steps,
                    'duration_ms': execution.get('duration_ms'),
                    'total_tokens': execution.get('total_tokens'),
                    'error_message': execution.get('error_message')
                })
                
            except Exception as e:
                logger.error(f"Error getting execution status: {e}", exc_info=True)
                return jsonify({'status': 'error', 'error': str(e)})
        
        @self.app.route('/api/executions/<execution_id>/trace', methods=['GET'])
        @api_login_required
        def api_get_execution_trace(execution_id):
            """Get execution trace/steps."""
            user_id = session.get('user_id')
            is_admin = session.get('is_admin', False)
            
            try:
                # Verify user has access to this execution
                if is_admin:
                    execution = self.db_facade.fetch_one(
                        "SELECT execution_id FROM executions WHERE execution_id = ?",
                        (execution_id,)
                    )
                else:
                    execution = self.db_facade.fetch_one(
                        "SELECT execution_id FROM executions WHERE execution_id = ? AND user_id = ?",
                        (execution_id, user_id)
                    )
                
                if not execution:
                    return self._error_response('EXEC_003', 'Execution not found', 404)
                
                # Get execution steps
                steps = self.db_facade.fetch_all(
                    "SELECT * FROM execution_steps WHERE execution_id = ? ORDER BY step_number ASC",
                    (execution_id,)
                )
                
                return jsonify({'success': True, 'steps': steps or []})
            except Exception as e:
                logger.error(f"Error getting execution trace: {e}", exc_info=True)
                return self._error_response('EXEC_004', 'Failed to get trace', 500)
        
        @self.app.route('/api/executions/<execution_id>/retry', methods=['POST'])
        @api_login_required
        def api_retry_execution(execution_id):
            """Retry a failed execution."""
            user_id = session.get('user_id')
            is_admin = session.get('is_admin', False)
            
            try:
                # Get original execution
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
                
                if not execution:
                    return self._error_response('EXEC_003', 'Execution not found', 404)
                
                # Parse input data
                input_data = {}
                if execution.get('input_data'):
                    try:
                        input_data = json.loads(execution['input_data'])
                    except:
                        pass
                
                agent_id = execution.get('agent_id')
                
                # Check if it's a workflow
                workflow = self.db_facade.fetch_one(
                    "SELECT * FROM workflows WHERE workflow_id = ?",
                    (agent_id,)
                )
                
                if workflow:
                    # Re-execute workflow
                    from abhikarta.workflow import WorkflowExecutor, DAGParser
                    
                    dag_def = json.loads(workflow.get('dag_definition', '{}'))
                    dag_def['workflow_id'] = agent_id
                    dag_def['name'] = workflow['name']
                    dag_def['python_modules'] = json.loads(workflow.get('python_modules', '{}'))
                    
                    parser = DAGParser()
                    wf = parser.parse_dict(dag_def)
                    
                    if wf:
                        executor = WorkflowExecutor(self.db_facade, None, user_id)
                        new_execution = executor.execute_workflow(wf, input_data)
                        return jsonify({
                            'success': True,
                            'new_execution_id': new_execution.execution_id
                        })
                
                return self._error_response('EXEC_005', 'Cannot retry this execution type', 400)
                
            except Exception as e:
                logger.error(f"Error retrying execution: {e}", exc_info=True)
                return self._error_response('EXEC_006', 'Failed to retry execution', 500)
        
        @self.app.route('/api/llm/calls', methods=['GET'])
        @api_login_required
        def api_list_llm_calls():
            """List LLM calls for current user."""
            user_id = session.get('user_id')
            is_admin = session.get('is_admin', False)
            limit = request.args.get('limit', 100, type=int)
            
            try:
                if is_admin:
                    calls = self.db_facade.fetch_all(
                        "SELECT * FROM llm_calls ORDER BY created_at DESC LIMIT ?",
                        (limit,)
                    )
                else:
                    calls = self.db_facade.fetch_all(
                        "SELECT * FROM llm_calls WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                        (user_id, limit)
                    )
                return jsonify({'success': True, 'calls': calls or []})
            except Exception as e:
                logger.error(f"Error listing LLM calls: {e}", exc_info=True)
                return self._error_response('LLM_001', 'Failed to list LLM calls', 500)
        
        @self.app.route('/api/llm/usage', methods=['GET'])
        @api_login_required
        def api_llm_usage_stats():
            """Get LLM usage statistics."""
            user_id = session.get('user_id')
            is_admin = session.get('is_admin', False)
            days = request.args.get('days', 30, type=int)
            
            try:
                if is_admin:
                    stats = self.db_facade.fetch_one("""
                        SELECT 
                            COUNT(*) as total_calls,
                            SUM(input_tokens) as total_input_tokens,
                            SUM(output_tokens) as total_output_tokens,
                            SUM(total_tokens) as total_tokens,
                            SUM(cost_estimate) as total_cost,
                            AVG(latency_ms) as avg_latency
                        FROM llm_calls 
                        WHERE created_at > datetime('now', ?)
                    """, (f'-{days} days',))
                else:
                    stats = self.db_facade.fetch_one("""
                        SELECT 
                            COUNT(*) as total_calls,
                            SUM(input_tokens) as total_input_tokens,
                            SUM(output_tokens) as total_output_tokens,
                            SUM(total_tokens) as total_tokens,
                            SUM(cost_estimate) as total_cost,
                            AVG(latency_ms) as avg_latency
                        FROM llm_calls 
                        WHERE user_id = ? AND created_at > datetime('now', ?)
                    """, (user_id, f'-{days} days'))
                
                return jsonify({'success': True, 'stats': stats or {}})
            except Exception as e:
                logger.error(f"Error getting LLM usage: {e}", exc_info=True)
                return self._error_response('LLM_002', 'Failed to get usage stats', 500)
        
        # ==================== MCP Plugins API ====================
        
        @self.app.route('/api/mcp/plugins', methods=['GET'])
        @api_admin_required
        def api_list_mcp_plugins():
            """List MCP plugins."""
            try:
                plugins = self.db_facade.fetch_all(
                    "SELECT * FROM mcp_plugins ORDER BY name"
                )
                return self._success_response(plugins)
            except Exception as e:
                logger.error(f"Error listing MCP plugins: {e}", exc_info=True)
                return self._error_response('MCP_001', 'Failed to list plugins', 500)
        
        @self.app.route('/api/mcp/plugins/<plugin_id>', methods=['GET'])
        @api_admin_required
        def api_get_mcp_plugin(plugin_id):
            """Get MCP plugin by ID."""
            try:
                plugin = self.db_facade.fetch_one(
                    "SELECT * FROM mcp_plugins WHERE plugin_id = ?",
                    (plugin_id,)
                )
                if plugin:
                    return self._success_response(plugin)
                return self._error_response('MCP_002', 'Plugin not found', 404)
            except Exception as e:
                logger.error(f"Error getting MCP plugin: {e}", exc_info=True)
                return self._error_response('MCP_001', 'Failed to get plugin', 500)
        
        # ==================== Health Check ====================
        
        @self.app.route('/api/health', methods=['GET'])
        def api_health_check():
            """Health check endpoint."""
            return self._success_response({
                'status': 'healthy',
                'version': self.app.config.get('APP_VERSION', '1.0.0'),
                'database': self.app.config.get('SETTINGS').database.type
            })
        
        # ==================== MCP Tool Servers ====================
        
        @self.app.route('/api/mcp-tools', methods=['GET'])
        @api_login_required
        def api_get_mcp_tools():
            """Get all tools from active MCP Tool Servers."""
            try:
                servers = self.db_facade.fetch_all(
                    "SELECT * FROM mcp_tool_servers WHERE is_active = 1"
                ) or []
                
                all_tools = []
                for server in servers:
                    try:
                        cached_tools = json.loads(server.get('cached_tools', '[]'))
                        for tool in cached_tools:
                            tool['_server_id'] = server['server_id']
                            tool['_server_name'] = server['name']
                            all_tools.append(tool)
                    except:
                        pass
                
                return self._success_response({
                    'tools': all_tools,
                    'server_count': len(servers),
                    'tool_count': len(all_tools)
                })
            except Exception as e:
                logger.error(f"Error getting MCP tools: {e}", exc_info=True)
                return self._error_response('MCP_TOOLS_001', 'Failed to get tools', 500)
        
        @self.app.route('/api/mcp-tool-servers', methods=['GET'])
        @api_login_required
        def api_get_mcp_tool_servers():
            """Get list of MCP Tool Servers."""
            try:
                active_only = request.args.get('active_only', 'true').lower() == 'true'
                
                if active_only:
                    servers = self.db_facade.fetch_all(
                        "SELECT server_id, name, description, base_url, tool_count, is_active, last_refresh FROM mcp_tool_servers WHERE is_active = 1 ORDER BY name"
                    ) or []
                else:
                    servers = self.db_facade.fetch_all(
                        "SELECT server_id, name, description, base_url, tool_count, is_active, last_refresh FROM mcp_tool_servers ORDER BY name"
                    ) or []
                
                return self._success_response({
                    'servers': servers,
                    'count': len(servers)
                })
            except Exception as e:
                logger.error(f"Error getting MCP tool servers: {e}", exc_info=True)
                return self._error_response('MCP_SERVERS_001', 'Failed to get servers', 500)
        
        @self.app.route('/api/mcp-tool-servers/<server_id>/tools', methods=['GET'])
        @api_login_required
        def api_get_server_tools(server_id):
            """Get tools from a specific MCP Tool Server."""
            try:
                server = self.db_facade.fetch_one(
                    "SELECT * FROM mcp_tool_servers WHERE server_id = ?",
                    (server_id,)
                )
                
                if not server:
                    return self._error_response('MCP_SERVERS_002', 'Server not found', 404)
                
                tools = json.loads(server.get('cached_tools', '[]'))
                
                return self._success_response({
                    'server_id': server_id,
                    'server_name': server['name'],
                    'tools': tools,
                    'tool_count': len(tools),
                    'last_refresh': server.get('last_refresh')
                })
            except Exception as e:
                logger.error(f"Error getting server tools: {e}", exc_info=True)
                return self._error_response('MCP_SERVERS_003', 'Failed to get tools', 500)
        
        logger.info("API routes registered")
