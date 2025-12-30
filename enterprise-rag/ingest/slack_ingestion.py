"""
Slack data ingestion module.

Supports both Slack export files (JSON) and live Slack API integration.
Preserves conversation context, threads, and metadata.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from ..storage.raw_storage import RawDataStore
from ..storage.metadata import DocumentMetadata, IngestionRecord, SourceType
import uuid

logger = logging.getLogger(__name__)


class SlackIngestion:
    """
    Ingest Slack data from exports or API.
    
    Handles:
    - Slack export JSON files
    - Live Slack API (requires SLACK_BOT_TOKEN)
    - Thread context preservation
    - User resolution
    - Channel metadata
    """
    
    def __init__(self, storage: RawDataStore, slack_token: Optional[str] = None):
        """
        Initialize Slack ingestion.
        
        Args:
            storage: RawDataStore instance
            slack_token: Optional Slack bot token for API access
        """
        self.storage = storage
        self.client = WebClient(token=slack_token) if slack_token else None
        
        logger.info(f"SlackIngestion initialized (API: {self.client is not None})")
    
    def ingest_export(self, export_path: str) -> IngestionRecord:
        """
        Ingest data from a Slack export directory.
        
        Slack exports contain:
        - channels.json: Channel metadata
        - users.json: User metadata
        - {channel_name}/*.json: Daily message files
        
        Args:
            export_path: Path to unzipped Slack export directory
        
        Returns:
            IngestionRecord with ingestion metrics
        """
        export_dir = Path(export_path)
        ingestion_id = f"slack_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        record = IngestionRecord(
            source_type=SourceType.SLACK,
            ingestion_id=ingestion_id,
            started_at=datetime.now()
        )
        
        try:
            # Load metadata
            channels = self._load_channels(export_dir)
            users = self._load_users(export_dir)
            
            logger.info(f"Loaded {len(channels)} channels, {len(users)} users from export")
            
            # Create batch for this export
            batch_path = self.storage.create_ingestion_batch(
                source_type=SourceType.SLACK,
                batch_name="slack_export"
            )
            
            # Process each channel
            for channel in channels:
                channel_name = channel.get("name", "unknown")
                channel_id = channel.get("id", "unknown")
                
                try:
                    channel_docs = self._process_channel_export(
                        export_dir,
                        channel_name,
                        channel_id,
                        users,
                        batch_path
                    )
                    
                    record.documents_ingested += channel_docs
                    record.source_identifiers.append(channel_name)
                    
                except Exception as e:
                    logger.error(f"Failed to process channel {channel_name}: {e}")
                    record.documents_failed += 1
            
            record.status = "completed"
            record.completed_at = datetime.now()
            
        except Exception as e:
            record.status = "failed"
            record.error_message = str(e)
            record.completed_at = datetime.now()
            logger.error(f"Slack export ingestion failed: {e}")
        
        finally:
            self.storage.log_ingestion(record)
        
        return record
    
    def ingest_channel_api(
        self,
        channel_id: str,
        days_history: int = 30,
        limit: int = 1000
    ) -> IngestionRecord:
        """
        Ingest channel history via Slack API.
        
        Args:
            channel_id: Slack channel ID
            days_history: Number of days to retrieve
            limit: Maximum messages to retrieve
        
        Returns:
            IngestionRecord with ingestion metrics
        """
        if not self.client:
            raise ValueError("Slack API client not configured. Provide slack_token.")
        
        ingestion_id = f"slack_api_{channel_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        record = IngestionRecord(
            source_type=SourceType.SLACK,
            ingestion_id=ingestion_id,
            started_at=datetime.now(),
            source_identifiers=[channel_id]
        )
        
        try:
            # Get channel info
            channel_info = self.client.conversations_info(channel=channel_id)
            channel_name = channel_info["channel"]["name"]
            
            logger.info(f"Ingesting Slack channel: #{channel_name} ({channel_id})")
            
            # Create batch
            batch_path = self.storage.create_ingestion_batch(
                source_type=SourceType.SLACK,
                batch_name=channel_name
            )
            
            # Fetch messages
            oldest_ts = (datetime.now().timestamp() - (days_history * 86400))
            
            result = self.client.conversations_history(
                channel=channel_id,
                oldest=str(oldest_ts),
                limit=limit
            )
            
            messages = result["messages"]
            logger.info(f"Retrieved {len(messages)} messages from #{channel_name}")
            
            # Group into threads
            threads = self._group_messages_by_thread(messages)
            
            # Store each thread
            for thread_ts, thread_messages in threads.items():
                try:
                    self._store_thread(
                        thread_messages,
                        channel_id,
                        channel_name,
                        batch_path
                    )
                    record.documents_ingested += 1
                    
                except Exception as e:
                    logger.error(f"Failed to store thread {thread_ts}: {e}")
                    record.documents_failed += 1
            
            record.status = "completed"
            record.completed_at = datetime.now()
            
        except SlackApiError as e:
            record.status = "failed"
            record.error_message = f"Slack API error: {e.response['error']}"
            record.completed_at = datetime.now()
            logger.error(f"Slack API ingestion failed: {e}")
        
        except Exception as e:
            record.status = "failed"
            record.error_message = str(e)
            record.completed_at = datetime.now()
            logger.error(f"Slack ingestion failed: {e}")
        
        finally:
            self.storage.log_ingestion(record)
        
        return record
    
    def _load_channels(self, export_dir: Path) -> List[Dict]:
        """Load channels metadata from export."""
        channels_file = export_dir / "channels.json"
        if channels_file.exists():
            with open(channels_file, "r") as f:
                return json.load(f)
        return []
    
    def _load_users(self, export_dir: Path) -> Dict[str, Dict]:
        """Load users metadata from export."""
        users_file = export_dir / "users.json"
        if users_file.exists():
            with open(users_file, "r") as f:
                users_list = json.load(f)
                return {u["id"]: u for u in users_list}
        return {}
    
    def _process_channel_export(
        self,
        export_dir: Path,
        channel_name: str,
        channel_id: str,
        users: Dict[str, Dict],
        batch_path: str
    ) -> int:
        """Process all messages from a channel directory in export."""
        channel_dir = export_dir / channel_name
        
        if not channel_dir.exists():
            logger.warning(f"Channel directory not found: {channel_dir}")
            return 0
        
        # Collect all messages
        all_messages = []
        for message_file in sorted(channel_dir.glob("*.json")):
            with open(message_file, "r") as f:
                daily_messages = json.load(f)
                all_messages.extend(daily_messages)
        
        if not all_messages:
            logger.warning(f"No messages found in {channel_name}")
            return 0
        
        # Group by threads
        threads = self._group_messages_by_thread(all_messages)
        
        # Store each thread
        stored_count = 0
        for thread_ts, thread_messages in threads.items():
            try:
                self._store_thread(
                    thread_messages,
                    channel_id,
                    channel_name,
                    batch_path,
                    users
                )
                stored_count += 1
            except Exception as e:
                logger.error(f"Failed to store thread {thread_ts}: {e}")
        
        logger.info(f"Stored {stored_count} threads from #{channel_name}")
        return stored_count
    
    def _group_messages_by_thread(self, messages: List[Dict]) -> Dict[str, List[Dict]]:
        """Group messages into conversation threads."""
        threads = {}
        
        for msg in messages:
            # Use thread_ts if in thread, otherwise use message ts
            thread_ts = msg.get("thread_ts", msg.get("ts"))
            
            if thread_ts not in threads:
                threads[thread_ts] = []
            
            threads[thread_ts].append(msg)
        
        return threads
    
    def _store_thread(
        self,
        messages: List[Dict],
        channel_id: str,
        channel_name: str,
        batch_path: str,
        users: Optional[Dict[str, Dict]] = None
    ):
        """Store a conversation thread as raw data."""
        # Sort by timestamp
        messages = sorted(messages, key=lambda m: float(m.get("ts", 0)))
        
        if not messages:
            return
        
        first_msg = messages[0]
        thread_ts = first_msg.get("thread_ts", first_msg.get("ts"))
        
        # Build conversation text
        conversation = {
            "thread_ts": thread_ts,
            "channel_id": channel_id,
            "channel_name": channel_name,
            "message_count": len(messages),
            "participants": list(set(m.get("user", "unknown") for m in messages)),
            "messages": []
        }
        
        for msg in messages:
            user_id = msg.get("user", "unknown")
            user_name = user_id
            
            # Resolve user name if users dict available
            if users and user_id in users:
                user_name = users[user_id].get("name", user_id)
            
            timestamp = datetime.fromtimestamp(float(msg.get("ts", 0)))
            
            conversation["messages"].append({
                "user_id": user_id,
                "user_name": user_name,
                "text": msg.get("text", ""),
                "timestamp": timestamp.isoformat(),
                "ts": msg.get("ts")
            })
        
        # Create metadata
        metadata = DocumentMetadata(
            source_type=SourceType.SLACK,
            source_id=thread_ts,
            source_name=f"#{channel_name}",
            ingested_at=datetime.now(),
            source_timestamp=datetime.fromtimestamp(float(first_msg.get("ts", 0))),
            extra={
                "channel_id": channel_id,
                "channel_name": channel_name,
                "participants": conversation["participants"],
                "message_count": len(messages)
            }
        )
        
        # Store
        self.storage.store_raw_document(
            batch_path=batch_path,
            document_id=f"thread_{thread_ts}",
            content=conversation,
            metadata=metadata,
            file_extension="json"
        )
