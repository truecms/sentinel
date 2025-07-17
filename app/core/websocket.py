"""WebSocket connection manager for real-time updates."""

import logging
from datetime import datetime
from typing import Any, Dict, Optional, Set

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and subscriptions."""

    def __init__(self):
        # Active connections by user_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Channel subscriptions by websocket
        self.user_subscriptions: Dict[WebSocket, Set[str]] = {}
        # Reverse mapping: channel -> websockets
        self.channel_subscribers: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """Accept and register a new WebSocket connection."""
        await websocket.accept()

        # Add to active connections
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

        # Initialize subscription tracking
        self.user_subscriptions[websocket] = set()

        logger.info(f"WebSocket connected for user {user_id}")

        # Send connection confirmation
        await websocket.send_json(
            {"type": "connected", "timestamp": datetime.utcnow().isoformat()}
        )

    async def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        """Remove a WebSocket connection and clean up subscriptions."""
        # Remove from active connections
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        # Clean up channel subscriptions
        if websocket in self.user_subscriptions:
            channels = self.user_subscriptions[websocket]
            for channel in channels:
                if channel in self.channel_subscribers:
                    self.channel_subscribers[channel].discard(websocket)
                    if not self.channel_subscribers[channel]:
                        del self.channel_subscribers[channel]
            del self.user_subscriptions[websocket]

        logger.info(f"WebSocket disconnected for user {user_id}")

    async def subscribe(self, websocket: WebSocket, channel: str) -> None:
        """Subscribe a WebSocket to a channel."""
        # Add to user subscriptions
        if websocket in self.user_subscriptions:
            self.user_subscriptions[websocket].add(channel)

        # Add to channel subscribers
        if channel not in self.channel_subscribers:
            self.channel_subscribers[channel] = set()
        self.channel_subscribers[channel].add(websocket)

        logger.debug(f"WebSocket subscribed to channel: {channel}")

        # Send subscription confirmation
        await websocket.send_json(
            {
                "type": "subscribed",
                "channel": channel,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    async def unsubscribe(self, websocket: WebSocket, channel: str) -> None:
        """Unsubscribe a WebSocket from a channel."""
        # Remove from user subscriptions
        if websocket in self.user_subscriptions:
            self.user_subscriptions[websocket].discard(channel)

        # Remove from channel subscribers
        if channel in self.channel_subscribers:
            self.channel_subscribers[channel].discard(websocket)
            if not self.channel_subscribers[channel]:
                del self.channel_subscribers[channel]

        logger.debug(f"WebSocket unsubscribed from channel: {channel}")

        # Send unsubscription confirmation
        await websocket.send_json(
            {
                "type": "unsubscribed",
                "channel": channel,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]) -> None:
        """Broadcast a message to all subscribers of a channel."""
        if channel not in self.channel_subscribers:
            return

        # Prepare message with channel info
        data = {
            "channel": channel,
            "data": message,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Send to all subscribers
        disconnected = []
        for websocket in self.channel_subscribers[channel]:
            try:
                await websocket.send_json(data)
            except Exception as e:
                logger.error(f"Error broadcasting to websocket: {e}")
                disconnected.append(websocket)

        # Clean up disconnected websockets
        for ws in disconnected:
            await self._cleanup_disconnected_websocket(ws)

    async def send_to_user(self, user_id: str, message: Dict[str, Any]) -> None:
        """Send a message to all connections of a specific user."""
        if user_id not in self.active_connections:
            return

        data = {
            "type": "direct",
            "data": message,
            "timestamp": datetime.utcnow().isoformat(),
        }

        disconnected = []
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_json(data)
            except Exception as e:
                logger.error(f"Error sending to user {user_id}: {e}")
                disconnected.append(websocket)

        # Clean up disconnected websockets
        for ws in disconnected:
            await self._cleanup_disconnected_websocket(ws)

    async def _cleanup_disconnected_websocket(self, websocket: WebSocket) -> None:
        """Clean up a disconnected WebSocket."""
        # Find user_id for this websocket
        user_id = None
        for uid, connections in self.active_connections.items():
            if websocket in connections:
                user_id = uid
                break

        if user_id:
            await self.disconnect(websocket, user_id)

    def get_connection_count(self) -> int:
        """Get total number of active connections."""
        return sum(len(connections) for connections in self.active_connections.values())

    def get_channel_subscriber_count(self, channel: str) -> int:
        """Get number of subscribers for a specific channel."""
        return len(self.channel_subscribers.get(channel, set()))


# Global connection manager instance
manager = ConnectionManager()
