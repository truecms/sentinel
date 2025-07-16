"""WebSocket endpoints for real-time dashboard updates."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from jose import jwt
import json
import logging

from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.websocket import manager
from app.models.user import User
from app.schemas.ws import WebSocketMessage, ChannelType

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_websocket_user(
    token: str = Query(...),
    db: AsyncSession = Depends(deps.get_db)
) -> Optional[User]:
    """Validate WebSocket connection token and return user."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # Get user by ID from database
        query = select(User).where(User.id == int(user_id))
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            return None
        
        return user
    except (jwt.JWTError, ValueError):
        return None


def can_access_channel(user: User, channel: str) -> bool:
    """Check if user has permission to access a channel."""
    # Parse channel type and ID
    parts = channel.split(".")
    if len(parts) < 2:
        return False
    
    channel_type = parts[0]
    
    # Global channels - all authenticated users can access
    if channel_type in ["security", "metrics", "system"]:
        return True
    
    # Organization-specific channels
    if channel_type == "org" and len(parts) >= 3:
        org_id = parts[1]
        # Check if user belongs to this organization
        # For now, we'll allow access if user is authenticated
        # TODO: Implement proper organization membership check
        return True
    
    # Site-specific channels
    if channel_type == "site" and len(parts) >= 3:
        site_id = parts[1]
        # Check if user has access to this site
        # For now, we'll allow access if user is authenticated
        # TODO: Implement proper site access check
        return True
    
    return False


@router.websocket("/dashboard")
async def websocket_dashboard_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(deps.get_db)
):
    """WebSocket endpoint for real-time dashboard updates."""
    # Validate token and get user
    user = await get_websocket_user(token, db)
    if not user:
        await websocket.close(code=4001, reason="Unauthorized")
        return
    
    # Connect the WebSocket
    await manager.connect(websocket, str(user.id))
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                msg_type = message.get("type")
                
                if msg_type == "subscribe":
                    channel = message.get("channel")
                    if channel and can_access_channel(user, channel):
                        await manager.subscribe(websocket, channel)
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Unauthorized channel access"
                        })
                
                elif msg_type == "unsubscribe":
                    channel = message.get("channel")
                    if channel:
                        await manager.unsubscribe(websocket, channel)
                
                elif msg_type == "ping":
                    await websocket.send_json({"type": "pong"})
                
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {msg_type}"
                    })
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Internal server error"
                })
                
    except WebSocketDisconnect:
        await manager.disconnect(websocket, str(user.id))
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket, str(user.id))


@router.get("/ws/status")
async def get_websocket_status(
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """Get WebSocket connection status (admin only)."""
    return {
        "total_connections": manager.get_connection_count(),
        "channels": {
            channel: manager.get_channel_subscriber_count(channel)
            for channel in ["security.alerts", "metrics.updates", "system.status"]
        }
    }