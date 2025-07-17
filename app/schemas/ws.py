"""WebSocket message schemas."""

from enum import Enum
from typing import Optional, Any, Dict
from pydantic import BaseModel
from datetime import datetime


class MessageType(str, Enum):
    """WebSocket message types."""
    # Connection
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    
    # Subscription
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"
    
    # Communication
    PING = "ping"
    PONG = "pong"
    DIRECT = "direct"
    BROADCAST = "broadcast"


class ChannelType(str, Enum):
    """WebSocket channel types."""
    # Global channels
    SECURITY_ALERTS = "security.alerts"
    METRIC_UPDATES = "metrics.updates"
    SYSTEM_STATUS = "system.status"
    
    # Organization-specific (use with org ID)
    ORG_METRICS = "org.{}.metrics"
    ORG_ACTIVITY = "org.{}.activity"
    
    # Site-specific (use with site ID)
    SITE_STATUS = "site.{}.status"
    SITE_MODULES = "site.{}.modules"


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