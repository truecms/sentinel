from fastapi import FastAPI

from app.api.v1.api import api_router

app = FastAPI(
    title="Monitoring and Reporting Platform API",
    version="1.0.0",
    description="API for the Monitoring and Reporting Platform",
)
"""
FastAPI application for the Monitoring and Reporting Platform.
"""

app.include_router(api_router, prefix="/api/v1")
