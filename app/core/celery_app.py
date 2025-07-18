"""Celery configuration and app initialization."""

import os

from celery import Celery

# Create Celery app
celery_app = Celery("monitoring_platform")

# Configure Celery
celery_app.conf.update(
    broker_url=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/0",
    result_backend=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/0",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes
    task_soft_time_limit=1500,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])
