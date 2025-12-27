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
                agents = self.db_facade.fetch_all(
                    "SELECT * FROM agents WHERE status = 'published' ORDER BY name"
                )
            except Exception as e:
                logger.error(f"Error getting agents: {e}")
            
            # Get user's recent executions
            executions = []
            try:
                executions = self.db_facade.fetch_all(
                    "SELECT * FROM executions WHERE user_id = ? ORDER BY started_at DESC LIMIT 10",
                    (user_id,)
                )
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
                agents = self.db_facade.fetch_all(
                    "SELECT * FROM agents WHERE status = 'published' ORDER BY name"
                )
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
            """Execute an agent."""
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
                
                try:
                    # Create execution record
                    self.db_facade.execute(
                        """INSERT INTO executions 
                           (execution_id, agent_id, user_id, status, input_data, started_at)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (execution_id, agent_id, session.get('user_id'), 'running',
                         input_data, datetime.now().isoformat())
                    )
                    
                    self.log_audit('execute_agent', 'agent', agent_id, 
                                   {'execution_id': execution_id})
                    
                    flash(f'Agent execution started: {execution_id}', 'success')
                    return redirect(url_for('execution_detail', execution_id=execution_id))
                except Exception as e:
                    logger.error(f"Error starting execution: {e}")
                    flash('Failed to start agent execution', 'error')
            
            return render_template('user/execute_agent.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   agent=agent)
        
        @self.app.route('/user/executions')
        @login_required
        def user_executions():
            """List user's execution history."""
            user_id = session.get('user_id')
            
            executions = []
            try:
                executions = self.db_facade.fetch_all(
                    "SELECT * FROM executions WHERE user_id = ? ORDER BY started_at DESC",
                    (user_id,)
                )
            except Exception as e:
                logger.error(f"Error getting executions: {e}")
            
            return render_template('user/executions.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   executions=executions)
        
        @self.app.route('/user/executions/<execution_id>')
        @login_required
        def execution_detail(execution_id):
            """View execution details."""
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
            
            # Get agent info
            agent = None
            try:
                agent = self.db_facade.fetch_one(
                    "SELECT * FROM agents WHERE agent_id = ?",
                    (execution['agent_id'],)
                )
            except Exception as e:
                logger.error(f"Error getting agent: {e}")
            
            return render_template('user/execution_detail.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   execution=execution,
                                   agent=agent)
        
        logger.info("User routes registered")
