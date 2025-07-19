"""Tests for WebSocket schemas."""

import pytest
from datetime import datetime

from app.schemas.ws import ChannelType, MessageType, WebSocketMessage, SubscriptionMessage, BroadcastMessage


class TestWebSocketSchemas:
    """Test WebSocket message schemas."""

    def test_channel_types(self):
        """Test channel type enum values."""
        assert ChannelType.SECURITY_ALERTS == "security.alerts"
        assert ChannelType.METRICS_UPDATES == "metrics.updates"
        assert ChannelType.SYSTEM_STATUS == "system.status"
        # Template-based channels
        assert ChannelType.ORG_METRICS == "org.{}.metrics"
        assert ChannelType.ORG_ACTIVITY == "org.{}.activity"
        assert ChannelType.SITE_STATUS == "site.{}.status"
        assert ChannelType.SITE_MODULES == "site.{}.modules"

    def test_message_types(self):
        """Test message type enum values."""
        # Connection types
        assert MessageType.CONNECTED == "connected"
        assert MessageType.DISCONNECTED == "disconnected"
        assert MessageType.ERROR == "error"
        # Subscription types
        assert MessageType.SUBSCRIBE == "subscribe"
        assert MessageType.UNSUBSCRIBE == "unsubscribe"
        assert MessageType.SUBSCRIBED == "subscribed"
        assert MessageType.UNSUBSCRIBED == "unsubscribed"
        # Communication types
        assert MessageType.PING == "ping"
        assert MessageType.PONG == "pong"
        assert MessageType.DIRECT == "direct"
        assert MessageType.BROADCAST == "broadcast"

    def test_websocket_message_creation(self):
        """Test WebSocket message creation."""
        msg = WebSocketMessage(
            type=MessageType.PING,
            data={"test": "value"}
        )
        assert msg.type == MessageType.PING
        assert msg.data == {"test": "value"}
        assert isinstance(msg.timestamp, datetime)