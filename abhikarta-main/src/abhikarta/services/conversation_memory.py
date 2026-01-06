"""
Conversation Memory Service

Manages conversation history for conversational agents and workflows.
Provides persistent storage and retrieval of chat messages.

Version: 1.5.3
Copyright © 2025-2030, All Rights Reserved
"""

import logging
import json
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """Represents a single message in a conversation."""
    role: str  # 'human', 'assistant', 'system'
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        return cls(
            role=data.get('role', 'human'),
            content=data.get('content', ''),
            timestamp=data.get('timestamp', datetime.now(timezone.utc).isoformat()),
            metadata=data.get('metadata', {})
        )
    
    def to_langchain_format(self) -> Tuple[str, str]:
        """Convert to LangChain message format (role, content)."""
        return (self.role, self.content)


@dataclass
class Conversation:
    """Represents a conversation session."""
    conversation_id: str
    entity_type: str  # 'agent' or 'workflow'
    entity_id: str
    user_id: str
    title: str = ""
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to the conversation."""
        message = ChatMessage(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.updated_at = datetime.now(timezone.utc).isoformat()
        
        # Auto-generate title from first human message
        if not self.title and role == 'human':
            self.title = content[:50] + ('...' if len(content) > 50 else '')
    
    def get_chat_history(self, max_messages: int = None) -> List[Tuple[str, str]]:
        """Get chat history in LangChain format."""
        messages = self.messages
        if max_messages:
            messages = messages[-max_messages:]
        return [msg.to_langchain_format() for msg in messages]
    
    def get_context_window(self, max_tokens: int = 4000, avg_chars_per_token: int = 4) -> List[ChatMessage]:
        """Get messages that fit within a context window."""
        max_chars = max_tokens * avg_chars_per_token
        selected = []
        total_chars = 0
        
        # Work backwards from most recent
        for msg in reversed(self.messages):
            msg_chars = len(msg.content)
            if total_chars + msg_chars > max_chars:
                break
            selected.insert(0, msg)
            total_chars += msg_chars
        
        return selected
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'conversation_id': self.conversation_id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'user_id': self.user_id,
            'title': self.title,
            'messages': [msg.to_dict() for msg in self.messages],
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        messages = [ChatMessage.from_dict(m) for m in data.get('messages', [])]
        return cls(
            conversation_id=data.get('conversation_id', ''),
            entity_type=data.get('entity_type', 'agent'),
            entity_id=data.get('entity_id', ''),
            user_id=data.get('user_id', ''),
            title=data.get('title', ''),
            messages=messages,
            created_at=data.get('created_at', datetime.now(timezone.utc).isoformat()),
            updated_at=data.get('updated_at', datetime.now(timezone.utc).isoformat()),
            metadata=data.get('metadata', {})
        )


class ConversationMemoryManager:
    """
    Manages conversation memory with both in-memory and persistent storage.
    """
    
    def __init__(self, db_facade=None, storage_path: str = None):
        """
        Initialize the conversation memory manager.
        
        Args:
            db_facade: Database facade for persistent storage
            storage_path: Optional file-based storage path
        """
        self.db_facade = db_facade
        self.storage_path = Path(storage_path) if storage_path else None
        self._cache: Dict[str, Conversation] = {}
        
        # Ensure database table exists
        if self.db_facade:
            self._ensure_table()
        
        # Ensure storage directory exists
        if self.storage_path:
            self.storage_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("ConversationMemoryManager initialized")
    
    def _ensure_table(self):
        """Create conversations table if it doesn't exist."""
        try:
            self.db_facade.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    title TEXT,
                    messages_json TEXT DEFAULT '[]',
                    metadata_json TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.db_facade.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_entity 
                ON conversations(entity_type, entity_id)
            """)
            self.db_facade.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_user 
                ON conversations(user_id)
            """)
            logger.info("Conversations table ensured")
        except Exception as e:
            logger.error(f"Failed to create conversations table: {e}")
    
    def create_conversation(self, entity_type: str, entity_id: str, 
                           user_id: str, metadata: Dict[str, Any] = None) -> Conversation:
        """
        Create a new conversation session.
        
        Args:
            entity_type: 'agent' or 'workflow'
            entity_id: ID of the agent or workflow
            user_id: User initiating the conversation
            metadata: Optional metadata
            
        Returns:
            New Conversation instance
        """
        conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
        
        conversation = Conversation(
            conversation_id=conversation_id,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            metadata=metadata or {}
        )
        
        # Cache it
        self._cache[conversation_id] = conversation
        
        # Persist to database
        self._save_to_db(conversation)
        
        logger.info(f"Created conversation {conversation_id} for {entity_type}/{entity_id}")
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation or None if not found
        """
        # Check cache first
        if conversation_id in self._cache:
            return self._cache[conversation_id]
        
        # Try database
        conversation = self._load_from_db(conversation_id)
        if conversation:
            self._cache[conversation_id] = conversation
            return conversation
        
        # Try file storage
        if self.storage_path:
            conversation = self._load_from_file(conversation_id)
            if conversation:
                self._cache[conversation_id] = conversation
                return conversation
        
        return None
    
    def get_or_create_conversation(self, entity_type: str, entity_id: str,
                                   user_id: str, conversation_id: str = None) -> Conversation:
        """
        Get existing conversation or create new one.
        
        Args:
            entity_type: 'agent' or 'workflow'
            entity_id: ID of the agent or workflow
            user_id: User ID
            conversation_id: Optional existing conversation ID
            
        Returns:
            Conversation instance
        """
        if conversation_id:
            conversation = self.get_conversation(conversation_id)
            if conversation:
                return conversation
        
        return self.create_conversation(entity_type, entity_id, user_id)
    
    def add_message(self, conversation_id: str, role: str, content: str,
                   metadata: Dict[str, Any] = None) -> bool:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: Conversation ID
            role: 'human' or 'assistant'
            content: Message content
            metadata: Optional message metadata
            
        Returns:
            True if successful
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            logger.warning(f"Conversation not found: {conversation_id}")
            return False
        
        conversation.add_message(role, content, metadata)
        self._save_to_db(conversation)
        
        return True
    
    def get_chat_history(self, conversation_id: str, 
                        max_messages: int = None) -> List[Tuple[str, str]]:
        """
        Get chat history for a conversation in LangChain format.
        
        Args:
            conversation_id: Conversation ID
            max_messages: Optional limit on messages
            
        Returns:
            List of (role, content) tuples
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return []
        
        return conversation.get_chat_history(max_messages)
    
    def get_conversations_for_entity(self, entity_type: str, entity_id: str,
                                     user_id: str = None, limit: int = 50) -> List[Conversation]:
        """
        Get all conversations for an entity.
        
        Args:
            entity_type: 'agent' or 'workflow'
            entity_id: Entity ID
            user_id: Optional user filter
            limit: Maximum conversations to return
            
        Returns:
            List of Conversations
        """
        if not self.db_facade:
            return []
        
        try:
            if user_id:
                rows = self.db_facade.fetch_all(
                    """SELECT * FROM conversations 
                       WHERE entity_type = ? AND entity_id = ? AND user_id = ?
                       ORDER BY updated_at DESC LIMIT ?""",
                    (entity_type, entity_id, user_id, limit)
                )
            else:
                rows = self.db_facade.fetch_all(
                    """SELECT * FROM conversations 
                       WHERE entity_type = ? AND entity_id = ?
                       ORDER BY updated_at DESC LIMIT ?""",
                    (entity_type, entity_id, limit)
                )
            
            conversations = []
            for row in (rows or []):
                conv = self._row_to_conversation(row)
                if conv:
                    conversations.append(conv)
            
            return conversations
        except Exception as e:
            logger.error(f"Error fetching conversations: {e}")
            return []
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            True if deleted
        """
        # Remove from cache
        if conversation_id in self._cache:
            del self._cache[conversation_id]
        
        # Remove from database
        if self.db_facade:
            try:
                self.db_facade.execute(
                    "DELETE FROM conversations WHERE conversation_id = ?",
                    (conversation_id,)
                )
                logger.info(f"Deleted conversation {conversation_id}")
                return True
            except Exception as e:
                logger.error(f"Error deleting conversation: {e}")
        
        return False
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """
        Clear messages from a conversation but keep the session.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            True if cleared
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        conversation.messages = []
        conversation.updated_at = datetime.now(timezone.utc).isoformat()
        self._save_to_db(conversation)
        
        logger.info(f"Cleared messages from conversation {conversation_id}")
        return True
    
    def _save_to_db(self, conversation: Conversation):
        """Save conversation to database."""
        if not self.db_facade:
            return
        
        try:
            self.db_facade.execute(
                """INSERT OR REPLACE INTO conversations 
                   (conversation_id, entity_type, entity_id, user_id, title,
                    messages_json, metadata_json, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    conversation.conversation_id,
                    conversation.entity_type,
                    conversation.entity_id,
                    conversation.user_id,
                    conversation.title,
                    json.dumps([m.to_dict() for m in conversation.messages]),
                    json.dumps(conversation.metadata),
                    conversation.created_at,
                    conversation.updated_at
                )
            )
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
    
    def _load_from_db(self, conversation_id: str) -> Optional[Conversation]:
        """Load conversation from database."""
        if not self.db_facade:
            return None
        
        try:
            row = self.db_facade.fetch_one(
                "SELECT * FROM conversations WHERE conversation_id = ?",
                (conversation_id,)
            )
            return self._row_to_conversation(row) if row else None
        except Exception as e:
            logger.error(f"Failed to load conversation: {e}")
            return None
    
    def _row_to_conversation(self, row) -> Optional[Conversation]:
        """Convert database row to Conversation object."""
        if not row:
            return None
        
        try:
            row_dict = dict(row) if hasattr(row, 'keys') else row
            
            messages_json = row_dict.get('messages_json', '[]')
            messages_data = json.loads(messages_json) if isinstance(messages_json, str) else messages_json
            messages = [ChatMessage.from_dict(m) for m in messages_data]
            
            metadata_json = row_dict.get('metadata_json', '{}')
            metadata = json.loads(metadata_json) if isinstance(metadata_json, str) else metadata_json
            
            return Conversation(
                conversation_id=row_dict.get('conversation_id', ''),
                entity_type=row_dict.get('entity_type', 'agent'),
                entity_id=row_dict.get('entity_id', ''),
                user_id=row_dict.get('user_id', ''),
                title=row_dict.get('title', ''),
                messages=messages,
                created_at=row_dict.get('created_at', ''),
                updated_at=row_dict.get('updated_at', ''),
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Error converting row to conversation: {e}")
            return None
    
    def _load_from_file(self, conversation_id: str) -> Optional[Conversation]:
        """Load conversation from file storage."""
        if not self.storage_path:
            return None
        
        file_path = self.storage_path / f"{conversation_id}.json"
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Conversation.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load conversation from file: {e}")
            return None


# Singleton instance
_memory_manager: Optional[ConversationMemoryManager] = None


def get_conversation_memory_manager() -> Optional[ConversationMemoryManager]:
    """Get the singleton ConversationMemoryManager instance."""
    return _memory_manager


def init_conversation_memory_manager(db_facade=None, storage_path: str = None) -> ConversationMemoryManager:
    """Initialize the singleton ConversationMemoryManager."""
    global _memory_manager
    _memory_manager = ConversationMemoryManager(db_facade, storage_path)
    return _memory_manager
