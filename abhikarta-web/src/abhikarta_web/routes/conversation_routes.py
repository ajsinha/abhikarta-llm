"""
Conversation Routes

API endpoints for conversational agents and workflows with memory.

Version: 1.5.3
Copyright © 2025-2030, All Rights Reserved
"""

import logging
import json
import time
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, session, render_template

logger = logging.getLogger(__name__)


class ConversationRoutes:
    """Routes for conversational chat with memory."""
    
    def __init__(self, app, db_facade):
        self.app = app
        self.db_facade = db_facade
        self._memory_manager = None
        self._register_routes()
    
    def _get_memory_manager(self):
        """Get or create the conversation memory manager."""
        if self._memory_manager is None:
            try:
                from abhikarta.services.conversation_memory import (
                    get_conversation_memory_manager,
                    init_conversation_memory_manager
                )
                self._memory_manager = get_conversation_memory_manager()
                if self._memory_manager is None:
                    self._memory_manager = init_conversation_memory_manager(self.db_facade)
            except Exception as e:
                logger.error(f"Failed to get conversation memory manager: {e}")
        return self._memory_manager
    
    def _register_routes(self):
        """Register all conversation routes."""
        
        # Import auth decorators
        try:
            from abhikarta_web.auth import login_required
        except ImportError:
            def login_required(f):
                return f
        
        @self.app.route('/api/conversations', methods=['POST'])
        @login_required
        def create_conversation():
            """Create a new conversation session."""
            memory_manager = self._get_memory_manager()
            if not memory_manager:
                return jsonify({'success': False, 'error': 'Conversation memory not available'}), 500
            
            data = request.get_json() or {}
            entity_type = data.get('entity_type', 'agent')
            entity_id = data.get('entity_id')
            
            if not entity_id:
                return jsonify({'success': False, 'error': 'entity_id is required'}), 400
            
            user_id = session.get('user_id', 'anonymous')
            
            conversation = memory_manager.create_conversation(
                entity_type=entity_type,
                entity_id=entity_id,
                user_id=user_id,
                metadata=data.get('metadata', {})
            )
            
            return jsonify({
                'success': True,
                'conversation': conversation.to_dict()
            })
        
        @self.app.route('/api/conversations/<conversation_id>', methods=['GET'])
        @login_required
        def get_conversation(conversation_id):
            """Get a conversation by ID."""
            memory_manager = self._get_memory_manager()
            if not memory_manager:
                return jsonify({'success': False, 'error': 'Conversation memory not available'}), 500
            
            conversation = memory_manager.get_conversation(conversation_id)
            if not conversation:
                return jsonify({'success': False, 'error': 'Conversation not found'}), 404
            
            return jsonify({
                'success': True,
                'conversation': conversation.to_dict()
            })
        
        @self.app.route('/api/conversations/<conversation_id>', methods=['DELETE'])
        @login_required
        def delete_conversation(conversation_id):
            """Delete a conversation."""
            memory_manager = self._get_memory_manager()
            if not memory_manager:
                return jsonify({'success': False, 'error': 'Conversation memory not available'}), 500
            
            success = memory_manager.delete_conversation(conversation_id)
            return jsonify({'success': success})
        
        @self.app.route('/api/conversations/<conversation_id>/clear', methods=['POST'])
        @login_required
        def clear_conversation(conversation_id):
            """Clear messages from a conversation."""
            memory_manager = self._get_memory_manager()
            if not memory_manager:
                return jsonify({'success': False, 'error': 'Conversation memory not available'}), 500
            
            success = memory_manager.clear_conversation(conversation_id)
            return jsonify({'success': success})
        
        @self.app.route('/api/conversations/entity/<entity_type>/<entity_id>', methods=['GET'])
        @login_required
        def get_entity_conversations(entity_type, entity_id):
            """Get all conversations for an entity."""
            memory_manager = self._get_memory_manager()
            if not memory_manager:
                return jsonify({'success': False, 'error': 'Conversation memory not available'}), 500
            
            user_id = session.get('user_id')
            conversations = memory_manager.get_conversations_for_entity(
                entity_type=entity_type,
                entity_id=entity_id,
                user_id=user_id
            )
            
            return jsonify({
                'success': True,
                'conversations': [c.to_dict() for c in conversations]
            })
        
        @self.app.route('/api/agents/<agent_id>/chat', methods=['POST'])
        @login_required
        def agent_chat(agent_id):
            """
            Send a chat message to a conversational agent.
            Maintains conversation history across requests.
            """
            memory_manager = self._get_memory_manager()
            if not memory_manager:
                return jsonify({'success': False, 'error': 'Conversation memory not available'}), 500
            
            data = request.get_json() or {}
            message = data.get('message', '').strip()
            conversation_id = data.get('conversation_id')
            
            if not message:
                return jsonify({'success': False, 'error': 'Message is required'}), 400
            
            user_id = session.get('user_id', 'anonymous')
            
            # Get or create conversation
            conversation = memory_manager.get_or_create_conversation(
                entity_type='agent',
                entity_id=agent_id,
                user_id=user_id,
                conversation_id=conversation_id
            )
            
            # Add user message
            memory_manager.add_message(conversation.conversation_id, 'human', message)
            
            start_time = time.time()
            
            try:
                # Get chat history for context
                chat_history = conversation.get_chat_history(max_messages=20)
                # Remove the last message (the one we just added) as it will be the input
                if chat_history:
                    chat_history = chat_history[:-1]
                
                # Execute agent with conversation history
                from abhikarta.langchain.agents import AgentExecutor as LangChainAgentExecutor
                
                executor = LangChainAgentExecutor(self.db_facade)
                result = executor.execute_agent(
                    agent_id=agent_id,
                    input_data=message,
                    chat_history=chat_history if chat_history else None
                )
                
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Add assistant response to conversation
                response_text = result.output or "I couldn't generate a response."
                memory_manager.add_message(
                    conversation.conversation_id, 
                    'assistant', 
                    response_text,
                    metadata={'execution_id': result.execution_id, 'duration_ms': duration_ms}
                )
                
                return jsonify({
                    'success': True,
                    'conversation_id': conversation.conversation_id,
                    'response': response_text,
                    'execution_id': result.execution_id,
                    'status': result.status,
                    'duration_ms': duration_ms,
                    'message_count': len(conversation.messages)
                })
                
            except Exception as e:
                logger.error(f"Agent chat error: {e}", exc_info=True)
                error_message = f"Error: {str(e)}"
                
                # Add error to conversation
                memory_manager.add_message(
                    conversation.conversation_id,
                    'assistant',
                    error_message,
                    metadata={'error': True}
                )
                
                return jsonify({
                    'success': False,
                    'conversation_id': conversation.conversation_id,
                    'error': str(e),
                    'response': error_message
                }), 500
        
        @self.app.route('/api/workflows/<workflow_id>/chat', methods=['POST'])
        @login_required
        def workflow_chat(workflow_id):
            """
            Send a chat message to a conversational workflow.
            Maintains conversation history across requests.
            """
            memory_manager = self._get_memory_manager()
            if not memory_manager:
                return jsonify({'success': False, 'error': 'Conversation memory not available'}), 500
            
            data = request.get_json() or {}
            message = data.get('message', '').strip()
            conversation_id = data.get('conversation_id')
            
            if not message:
                return jsonify({'success': False, 'error': 'Message is required'}), 400
            
            user_id = session.get('user_id', 'anonymous')
            
            # Get or create conversation
            conversation = memory_manager.get_or_create_conversation(
                entity_type='workflow',
                entity_id=workflow_id,
                user_id=user_id,
                conversation_id=conversation_id
            )
            
            # Add user message
            memory_manager.add_message(conversation.conversation_id, 'human', message)
            
            start_time = time.time()
            
            try:
                # Get chat history for context
                chat_history = conversation.get_chat_history(max_messages=20)
                if chat_history:
                    chat_history = chat_history[:-1]
                
                # Load workflow
                workflow_row = self.db_facade.fetch_one(
                    "SELECT * FROM workflows WHERE workflow_id = ?",
                    (workflow_id,)
                )
                
                if not workflow_row:
                    return jsonify({'success': False, 'error': 'Workflow not found'}), 404
                
                workflow = dict(workflow_row)
                
                # Execute workflow with chat history in input
                from abhikarta.workflow import WorkflowExecutor, DAGParser
                
                dag_def = json.loads(workflow.get('dag_definition', '{}'))
                dag_def['workflow_id'] = workflow_id
                dag_def['name'] = workflow.get('name', '')
                dag_def['python_modules'] = json.loads(workflow.get('python_modules', '{}'))
                
                parser = DAGParser()
                wf = parser.parse_dict(dag_def)
                
                if not wf:
                    return jsonify({'success': False, 'error': 'Failed to parse workflow'}), 500
                
                executor = WorkflowExecutor(self.db_facade, None, user_id)
                
                # Include chat history in input
                input_data = {
                    'input': message,
                    'chat_history': chat_history,
                    'conversation_id': conversation.conversation_id
                }
                
                execution = executor.execute_workflow(wf, input_data)
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Get response from execution output
                response_text = execution.output_data
                if isinstance(response_text, dict):
                    response_text = response_text.get('output', str(response_text))
                
                response_text = str(response_text) if response_text else "Workflow completed."
                
                # Add assistant response
                memory_manager.add_message(
                    conversation.conversation_id,
                    'assistant',
                    response_text,
                    metadata={'execution_id': execution.execution_id, 'duration_ms': duration_ms}
                )
                
                return jsonify({
                    'success': True,
                    'conversation_id': conversation.conversation_id,
                    'response': response_text,
                    'execution_id': execution.execution_id,
                    'status': execution.status,
                    'duration_ms': duration_ms,
                    'message_count': len(conversation.messages)
                })
                
            except Exception as e:
                logger.error(f"Workflow chat error: {e}", exc_info=True)
                error_message = f"Error: {str(e)}"
                
                memory_manager.add_message(
                    conversation.conversation_id,
                    'assistant',
                    error_message,
                    metadata={'error': True}
                )
                
                return jsonify({
                    'success': False,
                    'conversation_id': conversation.conversation_id,
                    'error': str(e),
                    'response': error_message
                }), 500
        
        @self.app.route('/agents/<agent_id>/chat')
        @login_required
        def agent_chat_page(agent_id):
            """Chat interface for conversational agents."""
            # Get agent details
            agent_row = self.db_facade.fetch_one(
                "SELECT * FROM agents WHERE agent_id = ?",
                (agent_id,)
            )
            
            if not agent_row:
                return render_template('errors/404.html'), 404
            
            agent = dict(agent_row)
            
            # Check if conversational type
            agent_type = agent.get('agent_type', '')
            if not agent_type:
                config = json.loads(agent.get('config', '{}'))
                agent_type = config.get('agent_type', 'conversational')
            
            # Get existing conversations
            memory_manager = self._get_memory_manager()
            conversations = []
            if memory_manager:
                user_id = session.get('user_id')
                conversations = memory_manager.get_conversations_for_entity(
                    'agent', agent_id, user_id, limit=20
                )
            
            return render_template('agents/chat.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   agent=agent,
                                   agent_type=agent_type,
                                   conversations=[c.to_dict() for c in conversations])
        
        @self.app.route('/workflows/<workflow_id>/chat')
        @login_required
        def workflow_chat_page(workflow_id):
            """Chat interface for conversational workflows."""
            # Get workflow details
            workflow_row = self.db_facade.fetch_one(
                "SELECT * FROM workflows WHERE workflow_id = ?",
                (workflow_id,)
            )
            
            if not workflow_row:
                return render_template('errors/404.html'), 404
            
            workflow = dict(workflow_row)
            
            # Check if conversational type
            dag_def = json.loads(workflow.get('dag_definition', '{}'))
            workflow_type = dag_def.get('workflow_type', '')
            
            # Get existing conversations
            memory_manager = self._get_memory_manager()
            conversations = []
            if memory_manager:
                user_id = session.get('user_id')
                conversations = memory_manager.get_conversations_for_entity(
                    'workflow', workflow_id, user_id, limit=20
                )
            
            return render_template('workflows/chat.html',
                                   fullname=session.get('fullname'),
                                   userid=session.get('user_id'),
                                   roles=session.get('roles', []),
                                   workflow=workflow,
                                   workflow_type=workflow_type,
                                   conversations=[c.to_dict() for c in conversations])
