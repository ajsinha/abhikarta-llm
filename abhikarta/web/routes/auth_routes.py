"""
Auth Routes Module - Handles authentication routes and functionality

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

from flask import render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
import logging

from .abstract_routes import AbstractRoutes

logger = logging.getLogger(__name__)


class AuthRoutes(AbstractRoutes):
    """
    Handles authentication routes for the application.
    
    This class manages login, logout, and session management.
    
    Attributes:
        app: Flask application instance
        user_facade: UserFacade instance for user operations
    """
    
    def __init__(self, app):
        """
        Initialize AuthRoutes.
        
        Args:
            app: Flask application instance
        """
        super().__init__(app)
        logger.info("AuthRoutes initialized")
    
    def register_routes(self):
        """Register all authentication routes."""
        
        @self.app.route('/')
        def index():
            """Root route - redirect to login or dashboard."""
            if 'user_id' in session:
                if session.get('is_admin', False):
                    return redirect(url_for('admin_dashboard'))
                return redirect(url_for('user_dashboard'))
            return redirect(url_for('login'))
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            """
            Handle user login.
            
            GET: Display login form
            POST: Process login credentials
            """
            if request.method == 'POST':
                user_id = request.form.get('user_id', '').strip()
                password = request.form.get('password', '')
                
                if not user_id or not password:
                    flash('Please enter both user ID and password', 'error')
                    return render_template('auth/login.html')
                
                # Authenticate user
                user = self.user_facade.authenticate(user_id, password)
                
                if user:
                    # Set session data
                    session['user_id'] = user['user_id']
                    session['fullname'] = user.get('fullname', user_id)
                    session['email'] = user.get('email', '')
                    session['roles'] = user.get('roles', [])
                    session['is_admin'] = self.user_facade.is_admin(user_id)
                    session['logged_in_at'] = datetime.now().isoformat()
                    
                    # Log audit
                    self.log_audit('login', 'user', user_id, {'ip': request.remote_addr})
                    
                    logger.info(f"User logged in: {user_id}")
                    flash(f'Welcome, {user.get("fullname", user_id)}!', 'success')
                    
                    # Redirect based on role
                    if session['is_admin']:
                        return redirect(url_for('admin_dashboard'))
                    return redirect(url_for('user_dashboard'))
                else:
                    logger.warning(f"Failed login attempt for user: {user_id}")
                    flash('Invalid user ID or password', 'error')
                    return render_template('auth/login.html')
            
            # GET request - show login form
            return render_template('auth/login.html')
        
        @self.app.route('/logout')
        def logout():
            """Handle user logout."""
            user_id = session.get('user_id')
            
            if user_id:
                # Log audit
                self.log_audit('logout', 'user', user_id)
                logger.info(f"User logged out: {user_id}")
            
            # Clear session
            session.clear()
            flash('You have been logged out successfully', 'info')
            return redirect(url_for('login'))
        
        @self.app.route('/profile')
        def profile():
            """Display user profile."""
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            user = self.user_facade.get_user(session['user_id'])
            if not user:
                session.clear()
                return redirect(url_for('login'))
            
            return render_template('auth/profile.html',
                                   user=user,
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []))
        
        @self.app.route('/change-password', methods=['GET', 'POST'])
        def change_password():
            """Handle password change."""
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            if request.method == 'POST':
                current_password = request.form.get('current_password', '')
                new_password = request.form.get('new_password', '')
                confirm_password = request.form.get('confirm_password', '')
                
                # Validate inputs
                if not all([current_password, new_password, confirm_password]):
                    flash('Please fill in all fields', 'error')
                    return render_template('auth/change_password.html',
                                           fullname=session.get('fullname'),
                                           userid=session.get('user_id'),
                                           roles=session.get('roles', []))
                
                if new_password != confirm_password:
                    flash('New passwords do not match', 'error')
                    return render_template('auth/change_password.html',
                                           fullname=session.get('fullname'),
                                           userid=session.get('user_id'),
                                           roles=session.get('roles', []))
                
                # Verify current password
                user = self.user_facade.authenticate(session['user_id'], current_password)
                if not user:
                    flash('Current password is incorrect', 'error')
                    return render_template('auth/change_password.html',
                                           fullname=session.get('fullname'),
                                           userid=session.get('user_id'),
                                           roles=session.get('roles', []))
                
                # Change password
                if self.user_facade.change_password(session['user_id'], new_password):
                    self.log_audit('password_change', 'user', session['user_id'])
                    flash('Password changed successfully', 'success')
                    return redirect(url_for('profile'))
                else:
                    flash('Failed to change password', 'error')
            
            return render_template('auth/change_password.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []))
        
        @self.app.route('/help')
        def help():
            """Display help and documentation page."""
            return render_template('help/help.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   is_admin=session.get('is_admin', False))
        
        @self.app.route('/help/<page>')
        def help_page(page):
            """Display individual help page."""
            # Map URL slugs to template files
            page_map = {
                'getting-started': 'help/pages/getting_started.html',
                'agent-designer': 'help/pages/agent_designer.html',
                'agent_visual_designer': 'help/pages/agent_visual_designer.html',
                'workflow_visual_designer': 'help/pages/workflow_visual_designer.html',
                'workflow-dags': 'help/pages/workflow_dags.html',
                'llm-providers': 'help/pages/llm_providers.html',
                'mcp-plugins': 'help/pages/mcp_plugins.html',
                'tools-system': 'help/pages/tools_system.html',
                'prebuilt-tools': 'help/pages/prebuilt_tools.html',
                'banking-solutions': 'help/pages/banking_solutions.html',
                'actors': 'help/pages/actors.html',
                'swarms': 'help/pages/swarms.html',
                'messaging': 'help/pages/messaging.html',
                'hitl': 'help/pages/hitl.html',
                'executions-logging': 'help/pages/executions_logging.html',
                'api-reference': 'help/pages/api_reference.html',
                'rbac': 'help/pages/rbac.html',
                'configuration': 'help/pages/configuration.html',
                'troubleshooting': 'help/pages/troubleshooting.html',
                'prebuilt': 'help/pages/prebuilt.html',
                'code-fragments': 'help/pages/code_fragments.html',
                'llm-management': 'help/pages/llm_management.html',
                'glossary': 'help/pages/glossary.html',
                'database-schema': 'help/pages/database_schema.html',
                # v1.4.0 tutorials
                'cot-tot': 'help/pages/cot-tot.html',
                'goal-based-agents': 'help/pages/goal-based-agents.html',
                'react-reflect-hierarchical': 'help/pages/react-reflect-hierarchical.html',
                'notifications': 'help/pages/notifications.html',
                # v1.4.6 AI Organizations
                'aiorg': 'help/pages/aiorg.html',
            }
            
            template = page_map.get(page)
            if not template:
                return render_template('errors/404.html'), 404
            
            return render_template(template,
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   is_admin=session.get('is_admin', False))
        
        @self.app.route('/help/providers/<provider>')
        def help_provider(provider):
            """Display individual LLM provider page."""
            provider_map = {
                'openai': 'help/providers/openai.html',
                'anthropic': 'help/providers/anthropic.html',
                'google': 'help/providers/google.html',
                'mistral': 'help/providers/mistral.html',
                'cohere': 'help/providers/cohere.html',
                'huggingface': 'help/providers/huggingface.html',
                'bedrock': 'help/providers/bedrock.html',
                'azure': 'help/providers/azure.html',
                'ollama': 'help/providers/ollama.html',
                'groq': 'help/providers/groq.html',
                'together': 'help/providers/together.html',
            }
            
            template = provider_map.get(provider)
            if not template:
                return render_template('errors/404.html'), 404
            
            return render_template(template,
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   is_admin=session.get('is_admin', False))
        
        @self.app.route('/about')
        def about():
            """Display about page with competitive analysis."""
            return render_template('help/about.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   is_admin=session.get('is_admin', False))
        
        @self.app.route('/about/<page>')
        def about_page(page):
            """Display individual about page."""
            page_map = {
                'features': 'help/about/features.html',
                'architecture': 'help/about/architecture.html',
                'comparison': 'help/about/comparison.html',
                'technology': 'help/about/technology.html',
                'roadmap': 'help/about/roadmap.html',
                'legal': 'help/about/legal.html',
            }
            
            template = page_map.get(page)
            if not template:
                return render_template('errors/404.html'), 404
            
            return render_template(template,
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   is_admin=session.get('is_admin', False))
        
        # =========================================================
        # MARKDOWN DOCUMENTATION ROUTES
        # =========================================================
        
        @self.app.route('/docs')
        def markdown_docs():
            """Display list of markdown documentation files."""
            return render_template('help/markdown_docs.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   is_admin=session.get('is_admin', False))
        
        @self.app.route('/docs/<filename>')
        def markdown_viewer(filename):
            """Display markdown file rendered as HTML."""
            # Map of allowed markdown files with their titles
            doc_titles = {
                'README': 'README - Project Overview',
                'QUICKSTART': 'Quick Start Guide',
                'DESIGN': 'Architecture Design',
                'ACTORS': 'Actor System',
                'PATENT_APPLICATION': 'Patent Application',
                'PATENT_WORTHINESS_ANALYSIS': 'Patent Worthiness Analysis',
                'LEGAL_NOTICE': 'Legal Notice',
                'COT_TOT_TUTORIAL': 'Chain of Thought & Tree of Thought Tutorial',
                'GOAL_BASED_AGENTS_TUTORIAL': 'Goal-Based Agents Tutorial',
                'NOTIFICATION_QUICKSTART': 'Notifications Quick Start',
                'NOTIFICATION_ARCHITECTURE': 'Notifications Architecture',
                'REACT_REFLECT_HIERARCHICAL_TUTORIAL': 'ReAct, Reflect & Hierarchical Agents Tutorial',
                'REQUIREMENTS': 'Requirements Specification',
                'RESEARCH_PAPER': 'Research Paper - AI Agent Orchestration',
                'AIORG_ARCHITECTURE': 'AI Organization Architecture',
                'AIORG_DESIGN': 'AI Organization Design',
                'AIORG_QUICKSTART': 'AI Organization Quick Start',
                'AIORG_REQUIREMENTS': 'AI Organization Requirements',
            }
            
            title = doc_titles.get(filename, filename)
            
            return render_template('help/markdown_viewer.html',
                                   filename=filename,
                                   title=title,
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   is_admin=session.get('is_admin', False))
        
        @self.app.route('/api/markdown/<filename>')
        def api_markdown(filename):
            """API endpoint to serve markdown content."""
            import os
            
            # Base path for the project
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            
            # Map of allowed files and their paths
            file_map = {
                'README': os.path.join(base_path, 'README.md'),
                'QUICKSTART': os.path.join(base_path, 'docs', 'QUICKSTART.md'),
                'DESIGN': os.path.join(base_path, 'docs', 'DESIGN.md'),
                'ACTORS': os.path.join(base_path, 'docs', 'ACTORS.md'),
                'REQUIREMENTS': os.path.join(base_path, 'docs', 'REQUIREMENTS.md'),
                'PATENT_APPLICATION': os.path.join(base_path, 'docs', 'PATENT_APPLICATION.md'),
                'PATENT_WORTHINESS_ANALYSIS': os.path.join(base_path, 'docs', 'PATENT_WORTHINESS_ANALYSIS.md'),
                'LEGAL_NOTICE': os.path.join(base_path, 'LEGAL_NOTICE.md'),
                # v1.4.0 tutorials
                'COT_TOT_TUTORIAL': os.path.join(base_path, 'docs', 'COT_TOT_TUTORIAL.md'),
                'GOAL_BASED_AGENTS_TUTORIAL': os.path.join(base_path, 'docs', 'GOAL_BASED_AGENTS_TUTORIAL.md'),
                'REACT_REFLECT_HIERARCHICAL_TUTORIAL': os.path.join(base_path, 'docs', 'REACT_REFLECT_HIERARCHICAL_TUTORIAL.md'),
                'NOTIFICATION_QUICKSTART': os.path.join(base_path, 'docs', 'NOTIFICATION_QUICKSTART.md'),
                'NOTIFICATION_ARCHITECTURE': os.path.join(base_path, 'docs', 'NOTIFICATION_ARCHITECTURE.md'),
                # Research paper
                'RESEARCH_PAPER': os.path.join(base_path, 'docs', 'RESEARCH_PAPER.md'),
                # AI Organization docs
                'AIORG_ARCHITECTURE': os.path.join(base_path, 'docs', 'AIORG_ARCHITECTURE.md'),
                'AIORG_DESIGN': os.path.join(base_path, 'docs', 'AIORG_DESIGN.md'),
                'AIORG_QUICKSTART': os.path.join(base_path, 'docs', 'AIORG_QUICKSTART.md'),
                'AIORG_REQUIREMENTS': os.path.join(base_path, 'docs', 'AIORG_REQUIREMENTS.md'),
            }
            
            file_path = file_map.get(filename)
            
            if not file_path or not os.path.exists(file_path):
                return jsonify({'success': False, 'error': f'File not found: {filename}'}), 404
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return jsonify({'success': True, 'content': content, 'filename': filename})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        logger.info("Auth routes registered")
