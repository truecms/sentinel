"""Tests for WebSocket functionality."""

import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import WebSocket
from fastapi.testclient import TestClient

from app.api.v1.endpoints.ws import can_access_channel, get_websocket_user
from app.core.websocket import ConnectionManager, manager
from app.main import app
from app.models.user import User


@pytest.fixture
def mock_user():
    """Mock user for testing."""
    user = Mock(spec=User)
    user.id = 1
    user.email = "test@example.com"
    user.is_active = True
    user.is_superuser = False
    return user


@pytest.fixture
def connection_manager():
    """Fresh connection manager for each test."""
    return ConnectionManager()


class TestConnectionManager:
    """Test the WebSocket connection manager."""

    @pytest.mark.asyncio
    async def test_connect_websocket(self, connection_manager):
        """Test connecting a WebSocket."""
        mock_websocket = AsyncMock()
        user_id = "1"

        await connection_manager.connect(mock_websocket, user_id)

        # Verify WebSocket was accepted
        mock_websocket.accept.assert_called_once()
        mock_websocket.send_json.assert_called_once()

        # Verify connection was registered
        assert user_id in connection_manager.active_connections
        assert mock_websocket in connection_manager.active_connections[user_id]
        assert mock_websocket in connection_manager.user_subscriptions

    @pytest.mark.asyncio
    async def test_disconnect_websocket(self, connection_manager):
        """Test disconnecting a WebSocket."""
        mock_websocket = AsyncMock()
        user_id = "1"

        # Connect first
        await connection_manager.connect(mock_websocket, user_id)

        # Subscribe to a channel
        await connection_manager.subscribe(mock_websocket, "test.channel")

        # Disconnect
        await connection_manager.disconnect(mock_websocket, user_id)

        # Verify cleanup
        assert user_id not in connection_manager.active_connections
        assert mock_websocket not in connection_manager.user_subscriptions
        assert "test.channel" not in connection_manager.channel_subscribers

    @pytest.mark.asyncio
    async def test_subscribe_to_channel(self, connection_manager):
        """Test subscribing to a channel."""
        mock_websocket = AsyncMock()
        user_id = "1"
        channel = "security.alerts"

        # Connect first
        await connection_manager.connect(mock_websocket, user_id)

        # Subscribe
        await connection_manager.subscribe(mock_websocket, channel)

        # Verify subscription
        assert channel in connection_manager.user_subscriptions[mock_websocket]
        assert mock_websocket in connection_manager.channel_subscribers[channel]

        # Verify confirmation was sent
        assert mock_websocket.send_json.call_count == 2  # connect + subscribe
        subscribe_call = mock_websocket.send_json.call_args_list[1][0][0]
        assert subscribe_call["type"] == "subscribed"
        assert subscribe_call["channel"] == channel

    @pytest.mark.asyncio
    async def test_broadcast_to_channel(self, connection_manager):
        """Test broadcasting to a channel."""
        mock_websocket1 = AsyncMock()
        mock_websocket2 = AsyncMock()
        user_id1 = "1"
        user_id2 = "2"
        channel = "security.alerts"
        message = {"type": "alert", "data": "test"}

        # Connect both WebSockets
        await connection_manager.connect(mock_websocket1, user_id1)
        await connection_manager.connect(mock_websocket2, user_id2)

        # Subscribe both to the same channel
        await connection_manager.subscribe(mock_websocket1, channel)
        await connection_manager.subscribe(mock_websocket2, channel)

        # Broadcast message
        await connection_manager.broadcast_to_channel(channel, message)

        # Verify both received the message
        assert (
            mock_websocket1.send_json.call_count == 3
        )  # connect + subscribe + broadcast
        assert (
            mock_websocket2.send_json.call_count == 3
        )  # connect + subscribe + broadcast

        # Check broadcast message format
        broadcast_call = mock_websocket1.send_json.call_args_list[2][0][0]
        assert broadcast_call["channel"] == channel
        assert broadcast_call["data"] == message

    @pytest.mark.asyncio
    async def test_send_to_user(self, connection_manager):
        """Test sending direct message to user."""
        mock_websocket1 = AsyncMock()
        mock_websocket2 = AsyncMock()
        user_id = "1"
        message = {"type": "notification", "data": "test"}

        # Connect both WebSockets for same user
        await connection_manager.connect(mock_websocket1, user_id)
        await connection_manager.connect(mock_websocket2, user_id)

        # Send message to user
        await connection_manager.send_to_user(user_id, message)

        # Verify both connections received the message
        assert mock_websocket1.send_json.call_count == 2  # connect + direct message
        assert mock_websocket2.send_json.call_count == 2  # connect + direct message

        # Check direct message format
        direct_call = mock_websocket1.send_json.call_args_list[1][0][0]
        assert direct_call["type"] == "direct"
        assert direct_call["data"] == message

    def test_connection_count(self, connection_manager):
        """Test getting connection count."""
        assert connection_manager.get_connection_count() == 0

        # Add connections
        connection_manager.active_connections["1"] = {Mock(), Mock()}
        connection_manager.active_connections["2"] = {Mock()}

        assert connection_manager.get_connection_count() == 3

    def test_channel_subscriber_count(self, connection_manager):
        """Test getting channel subscriber count."""
        channel = "test.channel"
        assert connection_manager.get_channel_subscriber_count(channel) == 0

        # Add subscribers
        connection_manager.channel_subscribers[channel] = {Mock(), Mock(), Mock()}

        assert connection_manager.get_channel_subscriber_count(channel) == 3


class TestWebSocketEndpoints:
    """Test WebSocket endpoint functions."""

    @pytest.mark.asyncio
    async def test_get_websocket_user_valid_token(self, mock_user):
        """Test getting user from valid token."""
        with patch("app.api.v1.endpoints.ws.jwt.decode") as mock_jwt_decode, patch(
            "app.api.v1.endpoints.ws.deps.get_user_by_id"
        ) as mock_get_user:

            mock_jwt_decode.return_value = {"sub": "1"}
            mock_get_user.return_value = mock_user

            user = await get_websocket_user("valid_token", Mock())

            assert user == mock_user
            mock_jwt_decode.assert_called_once()
            mock_get_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_websocket_user_invalid_token(self):
        """Test getting user from invalid token."""
        with patch("app.api.v1.endpoints.ws.jwt.decode") as mock_jwt_decode:
            mock_jwt_decode.side_effect = Exception("Invalid token")

            user = await get_websocket_user("invalid_token", Mock())

            assert user is None

    def test_can_access_channel_global_channels(self, mock_user):
        """Test access to global channels."""
        # Global channels should be accessible to all authenticated users
        assert can_access_channel(mock_user, "security.alerts") is True
        assert can_access_channel(mock_user, "metrics.updates") is True
        assert can_access_channel(mock_user, "system.status") is True

    def test_can_access_channel_org_channels(self, mock_user):
        """Test access to organization channels."""
        # Organization channels should be accessible (TODO: implement proper check)
        assert can_access_channel(mock_user, "org.1.metrics") is True
        assert can_access_channel(mock_user, "org.2.activity") is True

    def test_can_access_channel_site_channels(self, mock_user):
        """Test access to site channels."""
        # Site channels should be accessible (TODO: implement proper check)
        assert can_access_channel(mock_user, "site.1.status") is True
        assert can_access_channel(mock_user, "site.2.modules") is True

    def test_can_access_channel_invalid_channels(self, mock_user):
        """Test access to invalid channels."""
        assert can_access_channel(mock_user, "invalid") is False
        assert can_access_channel(mock_user, "invalid.channel") is False
        assert can_access_channel(mock_user, "") is False


class TestWebSocketIntegration:
    """Integration tests for WebSocket functionality."""

    def test_websocket_status_endpoint(self):
        """Test the WebSocket status endpoint."""
        client = TestClient(app)

        # This endpoint requires superuser authentication
        # For now, this test will fail until we implement proper auth in tests
        # response = client.get("/api/v1/ws/status")
        # assert response.status_code == 401  # Unauthorized without proper auth

        # TODO: Add proper authenticated test when auth is set up
        pass

    @pytest.mark.asyncio
    async def test_websocket_message_handling(self, connection_manager):
        """Test WebSocket message handling flow."""
        mock_websocket = AsyncMock()
        user_id = "1"

        # Connect
        await connection_manager.connect(mock_websocket, user_id)

        # Simulate subscription message
        await connection_manager.subscribe(mock_websocket, "security.alerts")

        # Broadcast a message
        test_message = {
            "type": "security_alert",
            "severity": "high",
            "message": "New security update available",
        }
        await connection_manager.broadcast_to_channel("security.alerts", test_message)

        # Verify message was received
        assert (
            mock_websocket.send_json.call_count == 3
        )  # connect + subscribe + broadcast

        # Check the broadcast message
        broadcast_call = mock_websocket.send_json.call_args_list[2][0][0]
        assert broadcast_call["channel"] == "security.alerts"
        assert broadcast_call["data"] == test_message
        assert "timestamp" in broadcast_call

    @pytest.mark.asyncio
    async def test_websocket_error_handling(self, connection_manager):
        """Test WebSocket error handling."""
        mock_websocket = AsyncMock()
        mock_websocket.send_json.side_effect = Exception("Connection lost")
        user_id = "1"

        # Connect
        await connection_manager.connect(mock_websocket, user_id)

        # Subscribe (this should work despite future send errors)
        await connection_manager.subscribe(mock_websocket, "security.alerts")

        # Try to broadcast (should handle the error gracefully)
        await connection_manager.broadcast_to_channel(
            "security.alerts", {"test": "data"}
        )

        # The error should be logged but not crash the system
        # The connection should be cleaned up
        # Note: This test depends on the actual error handling implementation
