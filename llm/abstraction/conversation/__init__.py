"""
Conversation Management

Built-in chat history and conversation tracking.

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com  
https://www.github.com/ajsinha/abhikarta
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class ConversationMessage:
    """Single message in conversation"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


class Conversation:
    """Manage conversation history"""
    
    def __init__(self, max_history: int = 50, system_message: Optional[str] = None):
        self.messages: List[ConversationMessage] = []
        self.max_history = max_history
        self.metadata: Dict[str, Any] = {}
        
        if system_message:
            self.add_system_message(system_message)
    
    def add_user_message(self, content: str, **metadata) -> None:
        """Add user message"""
        self.messages.append(ConversationMessage(
            role='user',
            content=content,
            metadata=metadata
        ))
        self._trim_history()
    
    def add_assistant_message(self, content: str, **metadata) -> None:
        """Add assistant message"""
        self.messages.append(ConversationMessage(
            role='assistant',
            content=content,
            metadata=metadata
        ))
        self._trim_history()
    
    def add_system_message(self, content: str) -> None:
        """Add system message"""
        self.messages.insert(0, ConversationMessage(
            role='system',
            content=content
        ))
    
    def get_context(self, max_tokens: Optional[int] = None) -> List[Dict[str, str]]:
        """Get conversation context for LLM"""
        if max_tokens:
            return self._truncate_to_tokens(max_tokens)
        
        return [
            {'role': msg.role, 'content': msg.content}
            for msg in self.messages
        ]
    
    def _truncate_to_tokens(self, max_tokens: int) -> List[Dict[str, str]]:
        """Truncate to fit token limit"""
        # Approximate: 1 token ≈ 4 characters
        max_chars = max_tokens * 4
        
        result = []
        total_chars = 0
        
        # Always include system message
        system_msgs = [msg for msg in self.messages if msg.role == 'system']
        for msg in system_msgs:
            result.append({'role': msg.role, 'content': msg.content})
            total_chars += len(msg.content)
        
        # Add messages from end until limit
        for msg in reversed(self.messages):
            if msg.role == 'system':
                continue
            
            msg_chars = len(msg.content)
            if total_chars + msg_chars > max_chars:
                break
            
            result.insert(len(system_msgs), {'role': msg.role, 'content': msg.content})
            total_chars += msg_chars
        
        return result
    
    def _trim_history(self) -> None:
        """Trim history to max_history"""
        # Keep system messages
        system_msgs = [msg for msg in self.messages if msg.role == 'system']
        other_msgs = [msg for msg in self.messages if msg.role != 'system']
        
        if len(other_msgs) > self.max_history:
            other_msgs = other_msgs[-self.max_history:]
        
        self.messages = system_msgs + other_msgs
    
    def summarize(self, llm_client: Any) -> str:
        """Generate summary of conversation"""
        prompt = f"Summarize this conversation:\n\n{self.format_history()}"
        
        if hasattr(llm_client, 'complete'):
            return llm_client.complete(prompt)
        return "Summary not available"
    
    def format_history(self) -> str:
        """Format conversation as text"""
        return "\n\n".join([
            f"{msg.role.title()}: {msg.content}"
            for msg in self.messages
        ])
    
    def save(self, filepath: str) -> None:
        """Save conversation"""
        data = {
            'messages': [msg.to_dict() for msg in self.messages],
            'metadata': self.metadata
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self, filepath: str) -> None:
        """Load conversation"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.messages = [
            ConversationMessage(
                role=msg['role'],
                content=msg['content'],
                timestamp=datetime.fromisoformat(msg['timestamp']),
                metadata=msg.get('metadata', {})
            )
            for msg in data['messages']
        ]
        self.metadata = data.get('metadata', {})
    
    def clear(self) -> None:
        """Clear conversation"""
        system_msgs = [msg for msg in self.messages if msg.role == 'system']
        self.messages = system_msgs


class ChatClient:
    """Client with conversation management"""
    
    def __init__(
        self,
        llm_client: Any,
        max_history: int = 50,
        system_message: Optional[str] = None
    ):
        self.llm_client = llm_client
        self.conversation = Conversation(max_history, system_message)
    
    def chat(self, message: str, **kwargs) -> str:
        """Send message and get response"""
        self.conversation.add_user_message(message)
        
        context = self.conversation.get_context(
            max_tokens=kwargs.pop('max_context_tokens', None)
        )
        
        # Get response
        if hasattr(self.llm_client, 'chat'):
            response = self.llm_client.chat(context, **kwargs)
        else:
            # Use complete with formatted context
            prompt = self.conversation.format_history()
            response = self.llm_client.complete(prompt, **kwargs)
        
        # Extract text
        response_text = response if isinstance(response, str) else getattr(response, 'text', str(response))
        
        self.conversation.add_assistant_message(response_text)
        return response_text
    
    def reset(self, keep_system: bool = True) -> None:
        """Reset conversation"""
        if keep_system:
            self.conversation.clear()
        else:
            self.conversation = Conversation(self.conversation.max_history)
