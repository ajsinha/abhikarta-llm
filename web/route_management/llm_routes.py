"""
LLM Routes Module - Handles LLM chat interactions with session management

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha | Email: ajsinha@gmail.com

Legal Notice:
This module and the associated software architecture are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Patent Pending: Certain architectural patterns and implementations described in this
module may be subject to patent applications.
"""

from flask import render_template, request, redirect, url_for, session, flash, jsonify, Response, stream_with_context
from web.route_management.abstract_routes import login_required
from web.route_management.abstract_routes import AbstractRoutes
import logging
import json
from typing import Dict, Any, List, Optional
import time
from datetime import datetime
import os
import shutil
from werkzeug.utils import secure_filename

from llm_provider.llm_interaction_logger import LLMInteractionLogger

logger = logging.getLogger(__name__)


class LLMRoutes(AbstractRoutes):
    """
    Handles LLM chat interaction routes with session-based facade caching.

    This class manages:
    - Chat interface rendering
    - Provider and model selection
    - Chat message sending and receiving
    - Conversation history management
    - Streaming responses
    - Session lifecycle and facade caching
    - Automatic cleanup on session end
    - File uploads per chat session
    - Tool management per chat session

    Attributes:
        app: Flask application instance
        llm_facade_factory: Factory for creating LLM facade instances
        model_provider_registry: Registry of model providers
        facade_cache: Cache manager for LLM facades
    """

    # Allowed file extensions for upload
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx',
                          'xls', 'xlsx', 'csv', 'json', 'xml', 'md', 'py', 'js',
                          'html', 'css', 'java', 'cpp', 'c', 'h', 'sql', 'yaml', 'yml'}

    # Maximum file size (16MB)
    MAX_FILE_SIZE = 16 * 1024 * 1024

    # Base directory for session file uploads
    UPLOAD_BASE_DIR = 'uploads/chat_sessions'

    def __init__(self, app, db_connection_pool_name: str):
        """
        Initialize LLMRoutes.

        Args:
            app: Flask application instance
            db_connection_pool_name: Database connection pool name
        """
        super().__init__(app, db_connection_pool_name)

        # Initialize interaction logger
        self.interaction_logger = None  # Will be initialized after db_pool is set

        # Store active chat sessions (in production, use Redis or database)
        self._active_chat_sessions: Dict[str, Dict[str, Any]] = {}

        # Store session files mapping (session_id -> list of files)
        self._session_files: Dict[str, List[Dict[str, Any]]] = {}

        # Store session tools mapping (session_id -> list of tool names)
        self._session_tools: Dict[str, List[str]] = {}

        # Available tools (hardcoded for now, can be loaded from DB later)
        self._available_tools: List[Dict[str, Any]] = [
            {
                'name': 'web_search',
                'display_name': 'Web Search',
                'description': 'Search the web for current information',
                'icon': 'fas fa-search',
                'category': 'search'
            },
            {
                'name': 'code_interpreter',
                'display_name': 'Code Interpreter',
                'description': 'Execute Python code and analyze data',
                'icon': 'fas fa-code',
                'category': 'execution'
            },
            {
                'name': 'file_reader',
                'display_name': 'File Reader',
                'description': 'Read and analyze uploaded files',
                'icon': 'fas fa-file-alt',
                'category': 'files'
            },
            {
                'name': 'calculator',
                'display_name': 'Calculator',
                'description': 'Perform mathematical calculations',
                'icon': 'fas fa-calculator',
                'category': 'utility'
            },
            {
                'name': 'image_analysis',
                'display_name': 'Image Analysis',
                'description': 'Analyze and describe images',
                'icon': 'fas fa-image',
                'category': 'vision'
            },
            {
                'name': 'document_qa',
                'display_name': 'Document Q&A',
                'description': 'Answer questions about documents',
                'icon': 'fas fa-file-pdf',
                'category': 'rag'
            },
            {
                'name': 'sql_query',
                'display_name': 'SQL Query',
                'description': 'Query databases using natural language',
                'icon': 'fas fa-database',
                'category': 'database'
            },
            {
                'name': 'api_caller',
                'display_name': 'API Caller',
                'description': 'Make API calls to external services',
                'icon': 'fas fa-plug',
                'category': 'integration'
            },
            {
                'name': 'text_to_speech',
                'display_name': 'Text to Speech',
                'description': 'Convert text to spoken audio',
                'icon': 'fas fa-volume-up',
                'category': 'audio'
            },
            {
                'name': 'summarizer',
                'display_name': 'Summarizer',
                'description': 'Summarize long texts and documents',
                'icon': 'fas fa-compress-alt',
                'category': 'text'
            }
        ]

        # Ensure upload directory exists
        os.makedirs(self.UPLOAD_BASE_DIR, exist_ok=True)

        logger.info("LLMRoutes initialized with facade caching, file upload, and tool management")

    def _allowed_file(self, filename: str) -> bool:
        """
        Check if file extension is allowed.

        Args:
            filename: Name of the file

        Returns:
            True if extension is allowed, False otherwise
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def _get_session_upload_dir(self, chat_session_id: str) -> str:
        """
        Get the upload directory for a specific chat session.

        Args:
            chat_session_id: Chat session identifier

        Returns:
            Path to session upload directory
        """
        session_dir = os.path.join(self.UPLOAD_BASE_DIR, chat_session_id)
        os.makedirs(session_dir, exist_ok=True)
        return session_dir

    def _cleanup_session_files(self, chat_session_id: str) -> int:
        """
        Clean up uploaded files for a session.

        Args:
            chat_session_id: Chat session identifier

        Returns:
            Number of files deleted
        """
        try:
            session_dir = os.path.join(self.UPLOAD_BASE_DIR, chat_session_id)
            files_deleted = 0

            if os.path.exists(session_dir):
                for filename in os.listdir(session_dir):
                    file_path = os.path.join(session_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        files_deleted += 1

                # Remove the directory
                os.rmdir(session_dir)

            # Clear from memory
            if chat_session_id in self._session_files:
                del self._session_files[chat_session_id]

            logger.info(f"Cleaned up {files_deleted} files for session {chat_session_id}")
            return files_deleted

        except Exception as e:
            logger.error(f"Error cleaning up session files: {e}", exc_info=True)
            return 0

    def _cleanup_session_tools(self, chat_session_id: str) -> int:
        """
        Clean up tools for a session.

        Args:
            chat_session_id: Chat session identifier

        Returns:
            Number of tools removed
        """
        try:
            tools_removed = 0
            if chat_session_id in self._session_tools:
                tools_removed = len(self._session_tools[chat_session_id])
                del self._session_tools[chat_session_id]

            logger.info(f"Cleaned up {tools_removed} tools for session {chat_session_id}")
            return tools_removed

        except Exception as e:
            logger.error(f"Error cleaning up session tools: {e}", exc_info=True)
            return 0

    def _get_or_create_chat_session(self) -> str:
        """
        Get current chat session ID or create new one.

        Returns:
            Chat session ID
        """
        chat_session_id = session.get('chat_session_id')

        if not chat_session_id:
            chat_session_id = self.generate_interaction_session_id()
            session['chat_session_id'] = chat_session_id
            session['chat_session_created_at'] = datetime.now().isoformat()

            # Track active session
            self._active_chat_sessions[chat_session_id] = {
                'user_id': session.get('userid'),
                'created_at': datetime.now(),
                'last_activity': datetime.now()
            }

            # Initialize session files and tools
            self._session_files[chat_session_id] = []
            self._session_tools[chat_session_id] = []

            logger.info(f"Created new chat session: {chat_session_id} for user {session.get('userid')}")
        else:
            # Update last activity
            if chat_session_id in self._active_chat_sessions:
                self._active_chat_sessions[chat_session_id]['last_activity'] = datetime.now()

            # Ensure session files and tools are initialized
            if chat_session_id not in self._session_files:
                self._session_files[chat_session_id] = []
            if chat_session_id not in self._session_tools:
                self._session_tools[chat_session_id] = []

        return chat_session_id

    def _end_chat_session(self, chat_session_id: str) -> bool:
        """
        End a chat session and clean up resources.

        Args:
            chat_session_id: Chat session to end

        Returns:
            True if session was ended, False if not found
        """
        try:
            # Evict all facades for this session
            evicted = self.facade_cache.evict_session(chat_session_id)

            # Clean up session files
            files_deleted = self._cleanup_session_files(chat_session_id)

            # Clean up session tools
            tools_removed = self._cleanup_session_tools(chat_session_id)

            # Remove from active sessions
            if chat_session_id in self._active_chat_sessions:
                del self._active_chat_sessions[chat_session_id]

            # Clear from Flask session
            if session.get('chat_session_id') == chat_session_id:
                session.pop('chat_session_id', None)
                session.pop('chat_session_created_at', None)

            logger.info(
                f"Ended chat session {chat_session_id}: "
                f"Evicted {evicted} facade(s), deleted {files_deleted} file(s), "
                f"removed {tools_removed} tool(s)"
            )

            return True

        except Exception as e:
            logger.error(f"Error ending chat session {chat_session_id}: {e}", exc_info=True)
            return False

    def _get_cached_facade(self, chat_session_id: str, provider_name: str,
                          model_name: str):
        """
        Get or create cached LLM facade for session.

        Args:
            chat_session_id: Chat session identifier
            provider_name: Provider name
            model_name: Model name

        Returns:
            LLM facade instance
        """
        def create_facade():
            """Factory function to create new facade."""
            return self.llm_facade_factory.create_facade(
                provider_name=provider_name,
                model_name=model_name
            )

        return self.facade_cache.get_or_create(
            chat_session_id=chat_session_id,
            provider_name=provider_name,
            model_name=model_name,
            factory_func=create_facade
        )

    def _initialize_interaction_logger(self):
        """Initialize interaction logger if db_pool is available."""

        if not self.interaction_logger:
            try:
                self.interaction_logger = LLMInteractionLogger(self.db_connection_pool_name)
                logger.info("Interaction logger initialized")
            except Exception as e:
                logger.warning(f"Could not initialize interaction logger: {e}")



    def register_routes(self):
        """Register all LLM-related routes."""

        # Initialize interaction logger if db_pool is available
        self._initialize_interaction_logger()

        @self.app.route('/llm/chat', methods=['GET'])
        @login_required
        def llm_chat():
            """Render the chat interface page."""
            userid = session.get('userid')

            # Get or create chat session
            chat_session_id = self._get_or_create_chat_session()

            logger.info(
                f"User {userid} accessing chat interface "
                f"(session: {chat_session_id})"
            )

            return render_template('chat/chat.html',
                                 fullname=session.get('fullname'),
                                 userid=userid,
                                 roles=session.get('roles', []),
                                 chat_session_id=chat_session_id)

        @self.app.route('/llm/chat/help', methods=['GET'])
        @login_required
        def llm_chat_help():
            """Render the chat help documentation page."""
            userid = session.get('userid')

            logger.info(f"User {userid} accessing chat help documentation")

            return render_template('chat/chat_help.html',
                                 fullname=session.get('fullname'),
                                 userid=userid,
                                 roles=session.get('roles', []))

        # ==================== FILE UPLOAD ROUTES ====================

        @self.app.route('/api/llm/chat/files', methods=['GET'])
        @login_required
        def get_session_files():
            """
            Get list of files uploaded for current chat session.

            Returns:
                JSON response with list of files
            """
            try:
                chat_session_id = session.get('chat_session_id')

                if not chat_session_id:
                    return jsonify({
                        'success': False,
                        'error': 'No active chat session'
                    }), 400

                # Get files from memory or scan directory
                files = self._session_files.get(chat_session_id, [])

                # If no files in memory, scan directory
                if not files:
                    session_dir = os.path.join(self.UPLOAD_BASE_DIR, chat_session_id)
                    if os.path.exists(session_dir):
                        for filename in os.listdir(session_dir):
                            file_path = os.path.join(session_dir, filename)
                            if os.path.isfile(file_path):
                                stat = os.stat(file_path)
                                files.append({
                                    'name': filename,
                                    'size': stat.st_size,
                                    'uploaded_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                    'path': file_path
                                })
                        self._session_files[chat_session_id] = files

                return jsonify({
                    'success': True,
                    'chat_session_id': chat_session_id,
                    'files': files,
                    'count': len(files)
                })

            except Exception as e:
                logger.error(f"Error getting session files: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/llm/chat/files/upload', methods=['POST'])
        @login_required
        def upload_session_file():
            """
            Upload a file for the current chat session.

            Returns:
                JSON response with upload status
            """
            try:
                chat_session_id = session.get('chat_session_id')

                if not chat_session_id:
                    return jsonify({
                        'success': False,
                        'error': 'No active chat session'
                    }), 400

                # Check if file is in request
                if 'file' not in request.files:
                    return jsonify({
                        'success': False,
                        'error': 'No file provided'
                    }), 400

                file = request.files['file']

                # Check if file was selected
                if file.filename == '':
                    return jsonify({
                        'success': False,
                        'error': 'No file selected'
                    }), 400

                # Check file extension
                if not self._allowed_file(file.filename):
                    return jsonify({
                        'success': False,
                        'error': f'File type not allowed. Allowed types: {", ".join(self.ALLOWED_EXTENSIONS)}'
                    }), 400

                # Check file size
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)

                if file_size > self.MAX_FILE_SIZE:
                    return jsonify({
                        'success': False,
                        'error': f'File too large. Maximum size: {self.MAX_FILE_SIZE // (1024*1024)}MB'
                    }), 400

                # Secure the filename
                filename = secure_filename(file.filename)

                # Add timestamp to avoid collisions
                base, ext = os.path.splitext(filename)
                timestamp = int(time.time() * 1000)
                unique_filename = f"{base}_{timestamp}{ext}"

                # Get session upload directory
                session_dir = self._get_session_upload_dir(chat_session_id)
                file_path = os.path.join(session_dir, unique_filename)

                # Save file
                file.save(file_path)

                # Add to session files
                file_info = {
                    'name': unique_filename,
                    'original_name': filename,
                    'size': file_size,
                    'uploaded_at': datetime.now().isoformat(),
                    'path': file_path
                }

                if chat_session_id not in self._session_files:
                    self._session_files[chat_session_id] = []
                self._session_files[chat_session_id].append(file_info)

                logger.info(
                    f"File uploaded: {unique_filename} for session {chat_session_id} "
                    f"by user {session.get('userid')}"
                )

                return jsonify({
                    'success': True,
                    'message': 'File uploaded successfully',
                    'file': file_info
                })

            except Exception as e:
                logger.error(f"Error uploading file: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/llm/chat/files/<filename>', methods=['DELETE'])
        @login_required
        def delete_session_file(filename: str):
            """
            Delete a file from the current chat session.

            Args:
                filename: Name of the file to delete

            Returns:
                JSON response with deletion status
            """
            try:
                chat_session_id = session.get('chat_session_id')

                if not chat_session_id:
                    return jsonify({
                        'success': False,
                        'error': 'No active chat session'
                    }), 400

                # Find the file in session files
                files = self._session_files.get(chat_session_id, [])
                file_to_delete = None

                for f in files:
                    if f['name'] == filename:
                        file_to_delete = f
                        break

                if not file_to_delete:
                    return jsonify({
                        'success': False,
                        'error': 'File not found'
                    }), 404

                # Delete the file from disk
                if os.path.exists(file_to_delete['path']):
                    os.remove(file_to_delete['path'])

                # Remove from session files
                self._session_files[chat_session_id] = [
                    f for f in files if f['name'] != filename
                ]

                logger.info(
                    f"File deleted: {filename} from session {chat_session_id} "
                    f"by user {session.get('userid')}"
                )

                return jsonify({
                    'success': True,
                    'message': 'File deleted successfully'
                })

            except Exception as e:
                logger.error(f"Error deleting file: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/llm/chat/files/allowed-types', methods=['GET'])
        @login_required
        def get_allowed_file_types():
            """
            Get list of allowed file types for upload.

            Returns:
                JSON response with allowed file types
            """
            return jsonify({
                'success': True,
                'allowed_extensions': list(self.ALLOWED_EXTENSIONS),
                'max_file_size': self.MAX_FILE_SIZE,
                'max_file_size_mb': self.MAX_FILE_SIZE // (1024 * 1024)
            })

        # ==================== TOOL MANAGEMENT ROUTES ====================

        @self.app.route('/api/llm/tools/available', methods=['GET'])
        @login_required
        def get_available_tools():
            """
            Get list of all available tools.

            Returns:
                JSON response with list of available tools
            """
            try:
                # Group tools by category
                tools_by_category = {}
                for tool in self._available_tools:
                    category = tool.get('category', 'general')
                    if category not in tools_by_category:
                        tools_by_category[category] = []
                    tools_by_category[category].append(tool)

                return jsonify({
                    'success': True,
                    'tools': self._available_tools,
                    'tools_by_category': tools_by_category,
                    'count': len(self._available_tools)
                })

            except Exception as e:
                logger.error(f"Error getting available tools: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/llm/chat/tools', methods=['GET'])
        @login_required
        def get_session_tools():
            """
            Get list of tools enabled for current chat session.

            Returns:
                JSON response with list of enabled tools
            """
            try:
                chat_session_id = session.get('chat_session_id')

                if not chat_session_id:
                    return jsonify({
                        'success': False,
                        'error': 'No active chat session'
                    }), 400

                enabled_tool_names = self._session_tools.get(chat_session_id, [])

                # Get full tool info for enabled tools
                enabled_tools = [
                    tool for tool in self._available_tools
                    if tool['name'] in enabled_tool_names
                ]

                return jsonify({
                    'success': True,
                    'chat_session_id': chat_session_id,
                    'tools': enabled_tools,
                    'tool_names': enabled_tool_names,
                    'count': len(enabled_tools)
                })

            except Exception as e:
                logger.error(f"Error getting session tools: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/llm/chat/tools', methods=['POST'])
        @login_required
        def add_session_tool():
            """
            Add a tool to the current chat session.

            Request JSON:
            {
                "tool_name": "tool_name"
            }

            Returns:
                JSON response with addition status
            """
            try:
                chat_session_id = session.get('chat_session_id')

                if not chat_session_id:
                    return jsonify({
                        'success': False,
                        'error': 'No active chat session'
                    }), 400

                data = request.get_json()
                if not data or 'tool_name' not in data:
                    return jsonify({
                        'success': False,
                        'error': 'Tool name is required'
                    }), 400

                tool_name = data['tool_name']

                # Check if tool exists
                tool_exists = any(t['name'] == tool_name for t in self._available_tools)
                if not tool_exists:
                    return jsonify({
                        'success': False,
                        'error': f'Tool "{tool_name}" not found'
                    }), 404

                # Initialize session tools if needed
                if chat_session_id not in self._session_tools:
                    self._session_tools[chat_session_id] = []

                # Check if already added
                if tool_name in self._session_tools[chat_session_id]:
                    return jsonify({
                        'success': False,
                        'error': f'Tool "{tool_name}" is already enabled'
                    }), 400

                # Add tool
                self._session_tools[chat_session_id].append(tool_name)

                # Get full tool info
                tool_info = next(
                    (t for t in self._available_tools if t['name'] == tool_name),
                    None
                )

                logger.info(
                    f"Tool added: {tool_name} for session {chat_session_id} "
                    f"by user {session.get('userid')}"
                )

                return jsonify({
                    'success': True,
                    'message': f'Tool "{tool_name}" enabled',
                    'tool': tool_info
                })

            except Exception as e:
                logger.error(f"Error adding tool: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/llm/chat/tools/<tool_name>', methods=['DELETE'])
        @login_required
        def remove_session_tool(tool_name: str):
            """
            Remove a tool from the current chat session.

            Args:
                tool_name: Name of the tool to remove

            Returns:
                JSON response with removal status
            """
            try:
                chat_session_id = session.get('chat_session_id')

                if not chat_session_id:
                    return jsonify({
                        'success': False,
                        'error': 'No active chat session'
                    }), 400

                # Check if tool is enabled
                if chat_session_id not in self._session_tools or \
                   tool_name not in self._session_tools[chat_session_id]:
                    return jsonify({
                        'success': False,
                        'error': f'Tool "{tool_name}" is not enabled'
                    }), 404

                # Remove tool
                self._session_tools[chat_session_id].remove(tool_name)

                logger.info(
                    f"Tool removed: {tool_name} from session {chat_session_id} "
                    f"by user {session.get('userid')}"
                )

                return jsonify({
                    'success': True,
                    'message': f'Tool "{tool_name}" disabled'
                })

            except Exception as e:
                logger.error(f"Error removing tool: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/llm/chat/tools/bulk', methods=['POST'])
        @login_required
        def set_session_tools_bulk():
            """
            Set multiple tools for the current chat session at once.

            Request JSON:
            {
                "tool_names": ["tool1", "tool2", ...]
            }

            Returns:
                JSON response with status
            """
            try:
                chat_session_id = session.get('chat_session_id')

                if not chat_session_id:
                    return jsonify({
                        'success': False,
                        'error': 'No active chat session'
                    }), 400

                data = request.get_json()
                if not data or 'tool_names' not in data:
                    return jsonify({
                        'success': False,
                        'error': 'Tool names array is required'
                    }), 400

                tool_names = data['tool_names']

                # Validate all tools exist
                available_names = {t['name'] for t in self._available_tools}
                invalid_tools = [t for t in tool_names if t not in available_names]

                if invalid_tools:
                    return jsonify({
                        'success': False,
                        'error': f'Invalid tools: {", ".join(invalid_tools)}'
                    }), 400

                # Set tools (replace existing)
                self._session_tools[chat_session_id] = list(set(tool_names))

                logger.info(
                    f"Tools set for session {chat_session_id}: {tool_names} "
                    f"by user {session.get('userid')}"
                )

                return jsonify({
                    'success': True,
                    'message': f'{len(tool_names)} tools enabled',
                    'tools': self._session_tools[chat_session_id]
                })

            except Exception as e:
                logger.error(f"Error setting tools: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        # ==================== EXISTING ROUTES ====================

        @self.app.route('/api/llm/chat/new', methods=['POST'])
        @login_required
        def new_chat_session():
            """
            Create a new chat session.

            Returns:
                JSON response with new session ID
            """
            try:
                # End current session if exists
                current_session_id = session.get('chat_session_id')
                if current_session_id:
                    self._end_chat_session(current_session_id)

                # Create new session
                chat_session_id = self.generate_interaction_session_id()
                session['chat_session_id'] = chat_session_id
                session['chat_session_created_at'] = datetime.now().isoformat()

                # Track active session
                self._active_chat_sessions[chat_session_id] = {
                    'user_id': session.get('userid'),
                    'created_at': datetime.now(),
                    'last_activity': datetime.now()
                }

                # Initialize session files and tools
                self._session_files[chat_session_id] = []
                self._session_tools[chat_session_id] = []

                logger.info(f"New chat session created: {chat_session_id}")

                return jsonify({
                    'success': True,
                    'chat_session_id': chat_session_id,
                    'message': 'New chat session created'
                })

            except Exception as e:
                logger.error(f"Error creating new chat session: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/llm/chat/end', methods=['POST'])
        @login_required
        def end_chat_session():
            """
            End current chat session and clean up resources.

            Returns:
                JSON response indicating success
            """
            try:
                chat_session_id = session.get('chat_session_id')

                if not chat_session_id:
                    return jsonify({
                        'success': False,
                        'error': 'No active chat session'
                    }), 400

                # End the session
                success = self._end_chat_session(chat_session_id)

                if success:
                    return jsonify({
                        'success': True,
                        'message': 'Chat session ended successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to end chat session'
                    }), 500

            except Exception as e:
                logger.error(f"Error ending chat session: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/llm/chat/session/info', methods=['GET'])
        @login_required
        def get_session_info():
            """
            Get information about current chat session.

            Returns:
                JSON with session info and cache statistics
            """
            try:
                chat_session_id = session.get('chat_session_id')

                if not chat_session_id:
                    return jsonify({
                        'success': False,
                        'error': 'No active chat session'
                    }), 400

                # Get session info
                session_info = self._active_chat_sessions.get(chat_session_id, {})

                # Get cache stats
                cache_stats = self.facade_cache.get_stats()

                # Get facades for this session
                session_facades = cache_stats.get('facades_by_session', {}).get(chat_session_id, 0)

                # Get file and tool counts
                file_count = len(self._session_files.get(chat_session_id, []))
                tool_count = len(self._session_tools.get(chat_session_id, []))

                return jsonify({
                    'success': True,
                    'chat_session_id': chat_session_id,
                    'created_at': session.get('chat_session_created_at'),
                    'cached_facades': session_facades,
                    'file_count': file_count,
                    'tool_count': tool_count,
                    'cache_stats': {
                        'total_cached_facades': cache_stats.get('total_cached_facades', 0),
                        'active_sessions': cache_stats.get('active_sessions', 0)
                    }
                })

            except Exception as e:
                logger.error(f"Error getting session info: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/llm/providers', methods=['GET'])
        @login_required
        def get_providers():
            """
            Get list of available LLM providers.

            Returns:
                JSON response with list of providers
            """
            try:
                if not self.model_provider_registry:
                    return jsonify({
                        'success': False,
                        'error': 'Model provider registry not initialized'
                    }), 500

                # Reload from database to get latest providers
                try:
                    self.model_provider_registry.reload_from_storage()
                except Exception as reload_error:
                    logger.warning(f"Failed to reload registry: {reload_error}")

                # Get all enabled providers
                providers = self.model_provider_registry.get_all_providers(
                    include_disabled=False
                )

                provider_list = []
                for provider_name, provider_obj in providers.items():
                    provider_list.append({
                        'name': provider_name,
                        'display_name': provider_name.title(),
                        'enabled': provider_obj.enabled,
                        'model_count': len([m for m in provider_obj.models if m.enabled])
                    })

                # Sort by display name
                provider_list.sort(key=lambda x: x['display_name'])

                logger.info(f"Returning {len(provider_list)} providers")

                return jsonify({
                    'success': True,
                    'providers': provider_list
                })

            except Exception as e:
                logger.error(f"Error getting providers: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/llm/models/<provider_name>', methods=['GET'])
        @login_required
        def get_provider_models(provider_name: str):
            """
            Get list of models for a specific provider.

            Args:
                provider_name: Name of the provider

            Returns:
                JSON response with list of models
            """
            try:
                if not self.model_provider_registry:
                    return jsonify({
                        'success': False,
                        'error': 'Model provider registry not initialized'
                    }), 500

                # Get provider
                try:
                    provider = self.model_provider_registry.get_provider_by_name(provider_name)
                except Exception as e:
                    error_msg = str(e)
                    if 'not found' in error_msg.lower():
                        return jsonify({
                            'success': False,
                            'error': f'Provider {provider_name} not found'
                        }), 404
                    elif 'disabled' in error_msg.lower():
                        return jsonify({
                            'success': False,
                            'error': f'Provider {provider_name} is disabled'
                        }), 403
                    else:
                        return jsonify({
                            'success': False,
                            'error': f'Error accessing provider: {error_msg}'
                        }), 500

                # Get enabled models
                models = provider.get_all_models(include_disabled=False)

                model_list = []
                for model in models:
                    model_info = {
                        'name': model.name,
                        'display_name': f"{model.name} ({model.version})",
                        'version': model.version,
                        'description': model.description,
                        'context_window': model.context_window,
                        'max_output': model.max_output,
                        'capabilities': model.capabilities,
                        'cost': model.cost
                    }
                    model_list.append(model_info)

                # Sort by name
                model_list.sort(key=lambda x: x['name'])

                logger.info(f"Returning {len(model_list)} models for provider {provider_name}")

                return jsonify({
                    'success': True,
                    'provider': provider_name,
                    'models': model_list
                })

            except Exception as e:
                logger.error(f"Error getting models for provider {provider_name}: {e}",
                           exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/llm/chat/send', methods=['POST'])
        @login_required
        def send_chat_message():
            """
            Send a chat message and get response.

            Request JSON:
            {
                "provider": "provider_name",
                "model": "model_name",
                "message": "user message",
                "conversation_history": [...],  # Optional
                "parameters": {...}  # Optional generation parameters
            }

            Returns:
                JSON response with assistant reply and metadata
            """
            try:
                data = request.get_json()

                if not data:
                    return jsonify({
                        'success': False,
                        'error': 'No data provided'
                    }), 400

                provider_name = data.get('provider')
                model_name = data.get('model')
                user_message = data.get('message', '').strip()
                conversation_history = data.get('conversation_history', [])
                parameters = data.get('parameters', {})

                # Validate inputs
                if not provider_name or not model_name or not user_message:
                    return jsonify({
                        'success': False,
                        'error': 'Provider, model, and message are required'
                    }), 400

                # Get or create chat session
                chat_session_id = self._get_or_create_chat_session()

                # Build messages array
                messages = []

                if conversation_history:
                    messages.extend(conversation_history)

                messages.append({
                    'role': 'user',
                    'content': user_message
                })

                # Check if factory is initialized
                if not self.llm_facade_factory:
                    return jsonify({
                        'success': False,
                        'error': 'LLM facade factory not initialized'
                    }), 500

                # Get or create cached facade
                try:
                    llm = self._get_cached_facade(
                        chat_session_id=chat_session_id,
                        provider_name=provider_name,
                        model_name=model_name
                    )
                except Exception as e:
                    logger.error(f"Error getting LLM facade: {e}", exc_info=True)
                    return jsonify({
                        'success': False,
                        'error': f'Failed to initialize LLM: {str(e)}'
                    }), 500

                # Call LLM
                start_time = time.time()

                try:
                    # Extract generation parameters
                    max_tokens = parameters.get('max_tokens', 4096)
                    temperature = parameters.get('temperature', 0.7)
                    top_p = parameters.get('top_p')

                    # Call chat completion
                    response = llm.chat_completion(
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        top_p=top_p
                    )

                    elapsed_time = time.time() - start_time

                    # Extract response content
                    assistant_message = response.get('content', '')

                    # Extract metadata
                    metadata = response.get('metadata', {})
                    usage = response.get('usage', {})

                    logger.info(
                        f"Chat completed for user {session.get('userid')} - "
                        f"Provider: {provider_name}, Model: {model_name}, "
                        f"Session: {chat_session_id}, "
                        f"Time: {elapsed_time:.2f}s"
                    )

                    # Log interaction to database
                    if self.interaction_logger:
                        try:
                            self.interaction_logger.log_interaction(
                                user_id=session.get('userid', 'unknown'),
                                session_id=session.get('session_id', 'unknown'),
                                chat_session_id=chat_session_id,
                                interaction_type='chat',
                                provider_name=provider_name,
                                model_name=model_name,
                                user_data=user_message,
                                llm_response=assistant_message,
                                request_parameters={
                                    'max_tokens': max_tokens,
                                    'temperature': temperature,
                                    'top_p': top_p
                                },
                                response_metadata=metadata,
                                response_time_ms=int(elapsed_time * 1000),
                                prompt_tokens=usage.get('prompt_tokens'),
                                completion_tokens=usage.get('completion_tokens'),
                                total_tokens=usage.get('total_tokens'),
                                status='success',
                                cached_facade=True,
                                streaming=False,
                                client_ip=request.remote_addr,
                                user_agent=request.headers.get('User-Agent')
                            )
                        except Exception as log_error:
                            logger.error(f"Error logging interaction: {log_error}")

                    return jsonify({
                        'success': True,
                        'response': assistant_message,
                        'metadata': {
                            'model': model_name,
                            'provider': provider_name,
                            'chat_session_id': chat_session_id,
                            'elapsed_time': elapsed_time,
                            'timestamp': datetime.now().isoformat(),
                            'usage': usage,
                            'finish_reason': metadata.get('finish_reason'),
                            'cached_facade': True  # Indicates facade was reused
                        }
                    })

                except Exception as e:
                    logger.error(f"Error calling LLM: {e}", exc_info=True)

                    # Log error interaction to database
                    if self.interaction_logger:
                        try:
                            self.interaction_logger.log_interaction(
                                user_id=session.get('userid', 'unknown'),
                                session_id=session.get('session_id', 'unknown'),
                                chat_session_id=chat_session_id,
                                interaction_type='chat',
                                provider_name=provider_name,
                                model_name=model_name,
                                user_data=user_message,
                                llm_response='',  # Empty response on error
                                request_parameters={
                                    'max_tokens': parameters.get('max_tokens', 4096),
                                    'temperature': parameters.get('temperature', 0.7),
                                    'top_p': parameters.get('top_p')
                                },
                                response_metadata={},
                                response_time_ms=int((time.time() - start_time) * 1000),
                                status='error',
                                error_message=str(e),
                                cached_facade=False,
                                streaming=False,
                                client_ip=request.remote_addr,
                                user_agent=request.headers.get('User-Agent')
                            )
                        except Exception as log_error:
                            logger.error(f"Error logging failed interaction: {log_error}")

                    return jsonify({
                        'success': False,
                        'error': f'LLM call failed: {str(e)}'
                    }), 500

            except Exception as e:
                logger.error(f"Error in send_chat_message: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/llm/chat/stream', methods=['POST'])
        @login_required
        def stream_chat_message():
            """
            Send a chat message and stream the response.

            Request JSON: Same as send_chat_message

            Returns:
                Server-Sent Events stream with response chunks
            """
            try:
                data = request.get_json()

                if not data:
                    return jsonify({
                        'success': False,
                        'error': 'No data provided'
                    }), 400

                provider_name = data.get('provider')
                model_name = data.get('model')
                user_message = data.get('message', '').strip()
                conversation_history = data.get('conversation_history', [])
                parameters = data.get('parameters', {})

                # Validate inputs
                if not provider_name or not model_name or not user_message:
                    return jsonify({
                        'success': False,
                        'error': 'Provider, model, and message are required'
                    }), 400

                # Get or create chat session
                chat_session_id = self._get_or_create_chat_session()

                def generate():
                    """Generator function for streaming response."""
                    try:
                        # Build messages array
                        messages = []

                        if conversation_history:
                            messages.extend(conversation_history)

                        messages.append({
                            'role': 'user',
                            'content': user_message
                        })

                        # Get cached facade
                        llm = self._get_cached_facade(
                            chat_session_id=chat_session_id,
                            provider_name=provider_name,
                            model_name=model_name
                        )

                        # Extract parameters
                        max_tokens = parameters.get('max_tokens', 4096)
                        temperature = parameters.get('temperature', 0.7)
                        top_p = parameters.get('top_p')

                        # Call streaming chat completion
                        stream = llm.stream_chat_completion(
                            messages=messages,
                            max_tokens=max_tokens,
                            temperature=temperature,
                            top_p=top_p
                        )

                        # Stream chunks
                        for chunk in stream:
                            if chunk:
                                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

                        # Send completion event
                        yield f"data: {json.dumps({'done': True})}\n\n"

                    except Exception as e:
                        logger.error(f"Error in streaming: {e}", exc_info=True)
                        yield f"data: {json.dumps({'error': str(e)})}\n\n"

                return Response(
                    stream_with_context(generate()),
                    mimetype='text/event-stream',
                    headers={
                        'Cache-Control': 'no-cache',
                        'X-Accel-Buffering': 'no'
                    }
                )

            except Exception as e:
                logger.error(f"Error in stream_chat_message: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/llm/registry/reload', methods=['POST'])
        @login_required
        def reload_registry():
            """
            Manually reload the model registry from database.

            Returns:
                JSON response indicating success
            """
            try:
                if not self.model_provider_registry:
                    return jsonify({
                        'success': False,
                        'error': 'Model provider registry not initialized'
                    }), 500

                # Reload from storage
                self.model_provider_registry.reload_from_storage()

                # Get updated counts
                providers = self.model_provider_registry.get_all_providers(include_disabled=False)

                logger.info(f"Registry reloaded by user {session.get('userid')} - {len(providers)} providers loaded")

                return jsonify({
                    'success': True,
                    'message': 'Model registry reloaded successfully',
                    'provider_count': len(providers)
                })

            except Exception as e:
                logger.error(f"Error reloading registry: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        logger.info("LLM routes registered with session management, file upload, and tool management")


__all__ = ['LLMRoutes']