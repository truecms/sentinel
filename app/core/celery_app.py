"""Celery configuration and app initialization."""

import os

from celery import Celery

# Create Celery app
celery_app = Celery("monitoring_platform")

# Configure Celery
celery_app.conf.update(
    _=f"redis://{os.getenv(
        'REDIS_HOST',
        'localhost')}:{os.getenv('REDIS_PORT',
        6379)}/0",
        
    )
    _=f"redis://{os.getenv(
        'REDIS_HOST',
        'localhost')}:{os.getenv('REDIS_PORT',
        6379)}/0",
        
    )
    _="json",
    _=["json"],
    _="json",
    _="UTC",
    _=True,
    _=True,
    _=1800,  # 30 minutes
    _=1500,  # 25 minutes
    _=1,
    _=100,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])
