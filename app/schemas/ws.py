"""WebSocket message schemas."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel


class MessageType(str, Enum):
    """WebSocket message types."""

    # Connection
    _ = "connected"
    _ = "disconnected"
    _ = "error"

    # Subscription
    _ = "subscribe"
    _ = "unsubscribe"
    _ = "subscribed"
    _ = "unsubscribed"

    # Communication
    _ = "ping"
    _ = "pong"
    _ = "direct"
    _ = "broadcast"


class ChannelType(str, Enum):
    """WebSocket channel types."""

    # Global channels
    _ = "security.alerts"
    _ = "metrics.updates"
    _ = "system.status"

    # Organization-specific (use with org ID)
    _ = "org.{}.metrics"
    _ = "org.{}.activity"

    # Site-specific (use with site ID)
    _ = "site.{}.status"
    _ = "site.{}.modules"


class WebSocketMessage(BaseModel):
    """Base WebSocket message."""

    type: MessageType
    timestamp: datetime = datetime.utcnow()
    data: Optional[Dict[str, Any]] = None


class SubscriptionMessage(WebSocketMessage):
    """Subscription request message."""

    type: MessageType = MessageType.SUBSCRIBE
    channel: str


class BroadcastMessage(BaseModel):
    """Message broadcast to a channel."""

    channel: str
    data: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()
