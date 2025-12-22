"""Slack connector for loading message history."""
from typing import List, Optional
from datetime import datetime, timedelta
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

from ..core.config import settings


class SlackConnector:
    """Connect to Slack and load message history."""
    
    def __init__(self):
        """Initialize the Slack connector."""
        self.client = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
        )
        
        # Initialize connection if token is available
        if settings.slack_bot_token:
            self.client = WebClient(token=settings.slack_bot_token)
    
    def is_configured(self) -> bool:
        """Check if Slack is properly configured."""
        return self.client is not None
    
    def load_channel_history(
        self,
        channel_id: str,
        days: int = 30,
        limit: int = 1000
    ) -> List[Document]:
        """
        Load message history from a Slack channel.
        
        Args:
            channel_id: Slack channel ID
            days: Number of days of history to load
            limit: Maximum number of messages to load
            
        Returns:
            List of Document objects
        """
        if not self.is_configured():
            raise ValueError("Slack is not configured. Please set SLACK_BOT_TOKEN in .env file.")
        
        documents = []
        
        try:
            # Calculate timestamp for oldest message
            oldest = (datetime.now() - timedelta(days=days)).timestamp()
            
            # Get channel info
            channel_info = self.client.conversations_info(channel=channel_id)
            channel_name = channel_info['channel']['name']
            
            # Fetch messages
            result = self.client.conversations_history(
                channel=channel_id,
                oldest=str(oldest),
                limit=limit
            )
            
            messages = result['messages']
            
            # Group messages into conversations (threads)
            conversations = self._group_messages(messages)
            
            # Process each conversation
            for conv_id, conv_messages in conversations.items():
                doc = self._process_conversation(
                    conv_messages,
                    channel_id,
                    channel_name
                )
                if doc:
                    documents.extend(doc)
            
            return documents
            
        except SlackApiError as e:
            raise Exception(f"Error loading Slack channel {channel_id}: {str(e)}")
    
    def _group_messages(self, messages: List[dict]) -> dict:
        """
        Group messages into conversations/threads.
        
        Args:
            messages: List of Slack messages
            
        Returns:
            Dictionary mapping conversation ID to messages
        """
        conversations = {}
        
        for msg in messages:
            # Use thread_ts as conversation ID, or message ts if not in thread
            conv_id = msg.get('thread_ts', msg.get('ts'))
            
            if conv_id not in conversations:
                conversations[conv_id] = []
            
            conversations[conv_id].append(msg)
        
        return conversations
    
    def _process_conversation(
        self,
        messages: List[dict],
        channel_id: str,
        channel_name: str
    ) -> List[Document]:
        """
        Process a conversation into documents.
        
        Args:
            messages: List of messages in the conversation
            channel_id: Slack channel ID
            channel_name: Slack channel name
            
        Returns:
            List of Document objects
        """
        try:
            # Sort messages by timestamp
            messages = sorted(messages, key=lambda x: float(x.get('ts', 0)))
            
            # Combine messages into a single conversation text
            conversation_text = ""
            participants = set()
            
            for msg in messages:
                user = msg.get('user', 'Unknown')
                text = msg.get('text', '')
                timestamp = datetime.fromtimestamp(float(msg.get('ts', 0)))
                
                participants.add(user)
                conversation_text += f"[{timestamp.strftime('%Y-%m-%d %H:%M')}] {user}: {text}\n"
            
            if not conversation_text.strip():
                return []
            
            # Create metadata
            first_msg = messages[0]
            metadata = {
                "source": f"#{channel_name}",
                "source_type": "slack",
                "channel_id": channel_id,
                "channel_name": channel_name,
                "thread_ts": first_msg.get('thread_ts', first_msg.get('ts')),
                "participants": list(participants),
                "message_count": len(messages),
                "timestamp": datetime.fromtimestamp(float(first_msg.get('ts', 0))).isoformat()
            }
            
            # Create document
            doc = Document(
                page_content=conversation_text,
                metadata=metadata
            )
            
            # Split into chunks if needed
            split_documents = self.text_splitter.split_documents([doc])
            
            return split_documents
            
        except Exception as e:
            print(f"Warning: Failed to process conversation: {str(e)}")
            return []


slack_connector = SlackConnector()
