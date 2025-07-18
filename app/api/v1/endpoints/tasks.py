"""Task status endpoints for background processing."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api import deps
from app.models.user import User
from app.tasks.sync_tasks import get_task_status

router = APIRouter()


@router.get("/{task_id}/status")
async def get_background_task_status(
    task_id: str, current_user: User = Depends(deps.get_current_user)
):
    """
    Get the status of a background task.

    Returns:
    - Task status (pending, in_progress, completed, failed)
    - Progress information for in-progress tasks
    - Result data for completed tasks
    - Error information for failed tasks
    """
    status_info = get_task_status.delay(task_id).get(timeout=5)

    if not status_info:
        raise HTTPException(_=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return status_info
