"""
Simple Memory Implementation

In-memory conversation storage for the chatbot.
For production, replace with Redis or database.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class SimpleMemory:
    """
    Simple in-memory storage for conversation history.

    This is suitable for demos and development. For production:
    - Use Redis for short-term memory (conversation context)
    - Use PostgreSQL for long-term storage (analytics, history)
    - Implement TTL for automatic cleanup
    """

    def __init__(self, max_history: int = 20, ttl_minutes: int = 30):
        """
        Initialize memory.

        Args:
            max_history: Maximum messages to keep per conversation
            ttl_minutes: Time-to-live for conversations in minutes
        """
        self.storage: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.max_history = max_history
        self.ttl = timedelta(minutes=ttl_minutes)

    def add(
        self,
        user_id: str,
        agent_id: str,
        interaction: Dict[str, Any]
    ):
        """
        Add interaction to memory.

        Args:
            user_id: User identifier
            agent_id: Agent identifier
            interaction: Interaction data with 'user' and 'assistant' keys
        """
        key = self._make_key(user_id, agent_id)

        if key not in self.storage:
            self.storage[key] = {
                "messages": [],
                "metadata": {
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "message_count": 0
                }
            }

        # Add user message
        self.storage[key]["messages"].append({
            "role": "user",
            "content": interaction["user"],
            "timestamp": interaction.get("timestamp", datetime.utcnow().isoformat())
        })

        # Add assistant message
        self.storage[key]["messages"].append({
            "role": "assistant",
            "content": interaction["assistant"],
            "timestamp": interaction.get("timestamp", datetime.utcnow().isoformat())
        })

        # Update metadata
        self.storage[key]["metadata"]["updated_at"] = datetime.utcnow()
        self.storage[key]["metadata"]["message_count"] += 2

        # Trim history if needed
        if len(self.storage[key]["messages"]) > self.max_history:
            # Keep system message if exists, then trim oldest
            messages = self.storage[key]["messages"]
            system_msgs = [m for m in messages if m["role"] == "system"]
            other_msgs = [m for m in messages if m["role"] != "system"]

            # Keep only the most recent messages
            keep_count = self.max_history - len(system_msgs)
            self.storage[key]["messages"] = system_msgs + other_msgs[-keep_count:]

        # Cleanup old conversations
        self._cleanup_expired()

    def get(
        self,
        user_id: str,
        agent_id: str
    ) -> Dict[str, Any]:
        """
        Get conversation history.

        Args:
            user_id: User identifier
            agent_id: Agent identifier

        Returns:
            Conversation data with messages and metadata
        """
        key = self._make_key(user_id, agent_id)

        if key not in self.storage:
            return {"messages": [], "metadata": {}}

        # Check if expired
        metadata = self.storage[key]["metadata"]
        if self._is_expired(metadata["updated_at"]):
            self.clear(user_id, agent_id)
            return {"messages": [], "metadata": {}}

        return self.storage[key]

    def clear(self, user_id: str, agent_id: str):
        """
        Clear conversation history.

        Args:
            user_id: User identifier
            agent_id: Agent identifier
        """
        key = self._make_key(user_id, agent_id)
        if key in self.storage:
            del self.storage[key]

    def get_summary(self, user_id: str, agent_id: str) -> Dict[str, Any]:
        """
        Get conversation summary.

        Args:
            user_id: User identifier
            agent_id: Agent identifier

        Returns:
            Summary with message count, duration, etc.
        """
        data = self.get(user_id, agent_id)
        if not data["messages"]:
            return {"exists": False}

        metadata = data["metadata"]
        duration = (metadata["updated_at"] - metadata["created_at"]).total_seconds()

        return {
            "exists": True,
            "message_count": metadata["message_count"],
            "duration_seconds": duration,
            "created_at": metadata["created_at"].isoformat(),
            "updated_at": metadata["updated_at"].isoformat(),
            "active": not self._is_expired(metadata["updated_at"])
        }

    def _make_key(self, user_id: str, agent_id: str) -> str:
        """Create storage key."""
        return f"{user_id}:{agent_id}"

    def _is_expired(self, updated_at: datetime) -> bool:
        """Check if conversation is expired."""
        return datetime.utcnow() - updated_at > self.ttl

    def _cleanup_expired(self):
        """Remove expired conversations."""
        expired_keys = []

        for key, data in self.storage.items():
            if self._is_expired(data["metadata"]["updated_at"]):
                expired_keys.append(key)

        for key in expired_keys:
            del self.storage[key]

    def get_all_conversations(self) -> List[Dict[str, Any]]:
        """
        Get all active conversations.

        Returns:
            List of conversation summaries
        """
        conversations = []

        for key, data in self.storage.items():
            if not self._is_expired(data["metadata"]["updated_at"]):
                user_id, agent_id = key.split(":")
                conversations.append({
                    "user_id": user_id,
                    "agent_id": agent_id,
                    "message_count": data["metadata"]["message_count"],
                    "updated_at": data["metadata"]["updated_at"].isoformat()
                })

        return conversations

    def clear_all(self):
        """Clear all conversations."""
        self.storage.clear()
