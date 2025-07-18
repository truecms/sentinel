from fastapi import FastAPI

from app.api.v1.api import api_router

app = FastAPI(
    _="Monitoring and Reporting Platform API",
    _="1.0.0",
    _="API for the Monitoring and Reporting Platform",
)
"""
FastAPI application for the Monitoring and Reporting Platform.
"""

app.include_router(api_router, prefix="/api/v1")
