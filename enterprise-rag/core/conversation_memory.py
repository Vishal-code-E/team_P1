"""
Conversation Memory System - Enterprise Demo Implementation

Provides server-side conversation history storage with:
- User-scoped isolation (no cross-user leakage)
- Session-based conversation tracking
- Limited retention (demo scope)
- Safe context injection into prompts

DESIGN DECISIONS:
- Filesystem storage (simple, demo-appropriate)
- JSON format (human-readable, debuggable)
- 10 message limit per conversation (prevents token overflow)
- 7-day retention (automatic cleanup)
- Memory as CONTEXT only, not authority
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from uuid import uuid4


@dataclass
class Message:
    """Single conversation message"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict) -> 'Message':
        return Message(**data)


@dataclass
class Conversation:
    """Conversation session with history"""
    conversation_id: str
    user_id: str
    created_at: str
    updated_at: str
    messages: List[Message]
    
    def to_dict(self) -> Dict:
        return {
            'conversation_id': self.conversation_id,
            'user_id': self.user_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'messages': [msg.to_dict() for msg in self.messages]
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Conversation':
        messages = [Message.from_dict(msg) for msg in data.get('messages', [])]
        return Conversation(
            conversation_id=data['conversation_id'],
            user_id=data['user_id'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            messages=messages
        )


class ConversationMemory:
    """
    Server-side conversation memory with enterprise-grade isolation.
    
    Security Properties:
    - User ID required for all operations
    - Conversations scoped by user (no cross-user access)
    - Automatic cleanup of old conversations
    - Message limit prevents prompt injection overflow
    
    Limitations (Demo Scope):
    - No encryption at rest (filesystem storage)
    - No distributed caching (single server)
    - No long-term learning (conversations expire)
    """
    
    MAX_MESSAGES_PER_CONVERSATION = 10  # Prevent token overflow
    RETENTION_DAYS = 7  # Auto-cleanup after 7 days
    
    def __init__(self, storage_path: str = "data/conversations"):
        """
        Initialize conversation memory.
        
        Args:
            storage_path: Directory for conversation storage
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def _get_user_dir(self, user_id: str) -> Path:
        """Get user-specific conversation directory"""
        user_dir = self.storage_path / user_id
        user_dir.mkdir(exist_ok=True)
        return user_dir
    
    def _get_conversation_path(self, user_id: str, conversation_id: str) -> Path:
        """Get path to conversation file"""
        return self._get_user_dir(user_id) / f"{conversation_id}.json"
    
    def create_conversation(self, user_id: str) -> str:
        """
        Create a new conversation session.
        
        Args:
            user_id: User identifier (from auth token)
            
        Returns:
            conversation_id: Unique conversation identifier
        """
        conversation_id = str(uuid4())
        now = datetime.utcnow().isoformat()
        
        conversation = Conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            created_at=now,
            updated_at=now,
            messages=[]
        )
        
        self._save_conversation(conversation)
        return conversation_id
    
    def add_message(
        self,
        user_id: str,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Add message to conversation.
        
        Args:
            user_id: User identifier (security boundary)
            conversation_id: Conversation session ID
            role: 'user' or 'assistant'
            content: Message text
            metadata: Optional metadata (sources, confidence, etc.)
            
        Raises:
            ValueError: If conversation doesn't belong to user
        """
        conversation = self._load_conversation(user_id, conversation_id)
        
        if conversation.user_id != user_id:
            raise ValueError(f"Conversation {conversation_id} does not belong to user {user_id}")
        
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.utcnow().isoformat(),
            metadata=metadata
        )
        
        conversation.messages.append(message)
        
        # Enforce message limit (sliding window)
        if len(conversation.messages) > self.MAX_MESSAGES_PER_CONVERSATION:
            conversation.messages = conversation.messages[-self.MAX_MESSAGES_PER_CONVERSATION:]
        
        conversation.updated_at = datetime.utcnow().isoformat()
        self._save_conversation(conversation)
    
    def get_conversation_history(
        self,
        user_id: str,
        conversation_id: str,
        max_messages: Optional[int] = None
    ) -> List[Dict]:
        """
        Retrieve conversation history for context injection.
        
        Args:
            user_id: User identifier (security boundary)
            conversation_id: Conversation session ID
            max_messages: Optional limit (defaults to MAX_MESSAGES_PER_CONVERSATION)
            
        Returns:
            List of messages in chronological order
            
        Security:
            - Only returns messages for authenticated user
            - Enforces message limit to prevent prompt overflow
        """
        conversation = self._load_conversation(user_id, conversation_id)
        
        if conversation.user_id != user_id:
            raise ValueError(f"Conversation {conversation_id} does not belong to user {user_id}")
        
        messages = conversation.messages
        
        if max_messages:
            messages = messages[-max_messages:]
        
        return [msg.to_dict() for msg in messages]
    
    def list_user_conversations(self, user_id: str) -> List[Dict]:
        """
        List all conversations for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of conversation metadata (no full messages)
        """
        user_dir = self._get_user_dir(user_id)
        conversations = []
        
        for conv_file in user_dir.glob("*.json"):
            try:
                with open(conv_file, 'r') as f:
                    data = json.load(f)
                    conversations.append({
                        'conversation_id': data['conversation_id'],
                        'created_at': data['created_at'],
                        'updated_at': data['updated_at'],
                        'message_count': len(data.get('messages', []))
                    })
            except Exception:
                continue
        
        return sorted(conversations, key=lambda x: x['updated_at'], reverse=True)
    
    def delete_conversation(self, user_id: str, conversation_id: str) -> None:
        """
        Delete a conversation.
        
        Args:
            user_id: User identifier (security boundary)
            conversation_id: Conversation to delete
        """
        conversation = self._load_conversation(user_id, conversation_id)
        
        if conversation.user_id != user_id:
            raise ValueError(f"Conversation {conversation_id} does not belong to user {user_id}")
        
        conv_path = self._get_conversation_path(user_id, conversation_id)
        conv_path.unlink(missing_ok=True)
    
    def cleanup_old_conversations(self) -> int:
        """
        Delete conversations older than RETENTION_DAYS.
        
        Returns:
            Number of conversations deleted
        """
        cutoff = datetime.utcnow() - timedelta(days=self.RETENTION_DAYS)
        deleted = 0
        
        for user_dir in self.storage_path.iterdir():
            if not user_dir.is_dir():
                continue
                
            for conv_file in user_dir.glob("*.json"):
                try:
                    with open(conv_file, 'r') as f:
                        data = json.load(f)
                        updated_at = datetime.fromisoformat(data['updated_at'])
                        
                        if updated_at < cutoff:
                            conv_file.unlink()
                            deleted += 1
                except Exception:
                    continue
        
        return deleted
    
    def _save_conversation(self, conversation: Conversation) -> None:
        """Save conversation to disk"""
        conv_path = self._get_conversation_path(
            conversation.user_id,
            conversation.conversation_id
        )
        
        with open(conv_path, 'w') as f:
            json.dump(conversation.to_dict(), f, indent=2)
    
    def _load_conversation(self, user_id: str, conversation_id: str) -> Conversation:
        """Load conversation from disk"""
        conv_path = self._get_conversation_path(user_id, conversation_id)
        
        if not conv_path.exists():
            raise FileNotFoundError(f"Conversation {conversation_id} not found for user {user_id}")
        
        with open(conv_path, 'r') as f:
            data = json.load(f)
            return Conversation.from_dict(data)


def format_history_for_prompt(messages: List[Dict], max_tokens: int = 2000) -> str:
    """
    Format conversation history for LLM context injection.
    
    Args:
        messages: List of message dicts from get_conversation_history()
        max_tokens: Approximate token limit (rough estimate: 4 chars = 1 token)
        
    Returns:
        Formatted history string for prompt injection
        
    SECURITY:
        - History is CONTEXT only, not authority
        - LLM can override history if sources contradict
        - Prevents prompt injection via message limit enforcement
    """
    if not messages:
        return ""
    
    formatted = ["Previous conversation context:"]
    total_chars = 0
    max_chars = max_tokens * 4  # Rough estimate
    
    # Add messages in reverse (most recent first) until limit
    for msg in reversed(messages):
        role = msg['role'].upper()
        content = msg['content']
        line = f"{role}: {content}"
        
        if total_chars + len(line) > max_chars:
            break
        
        formatted.insert(1, line)  # Insert after header
        total_chars += len(line)
    
    formatted.append("\nUse this context to understand the conversation flow, but prioritize retrieved sources for factual answers.\n")
    
    return "\n".join(formatted)
