"""Debug test to check environment variables"""
import os
import pytest
from app.core.config import settings


def test_debug_environment():
    """Print environment variables to debug the issue"""
    print("\n=== ENVIRONMENT DEBUG ===")
    print(f"TESTING env var: {os.getenv('TESTING')}")
    print(f"TESTING == 'True': {os.getenv('TESTING') == 'True'}")
    print(f"POSTGRES_USER env: {os.getenv('POSTGRES_USER')}")
    print(f"POSTGRES_PASSWORD env: {os.getenv('POSTGRES_PASSWORD')}")
    print(f"POSTGRES_DB env: {os.getenv('POSTGRES_DB')}")
    print(f"POSTGRES_HOST env: {os.getenv('POSTGRES_HOST')}")
    print(f"POSTGRES_SERVER env: {os.getenv('POSTGRES_SERVER')}")
    
    print("\n=== SETTINGS DEBUG ===")
    print(f"settings.POSTGRES_USER: {settings.POSTGRES_USER}")
    print(f"settings.POSTGRES_PASSWORD: {settings.POSTGRES_PASSWORD}")
    print(f"settings.POSTGRES_DB: {settings.POSTGRES_DB}")
    print(f"settings.POSTGRES_HOST: {settings.POSTGRES_HOST}")
    print(f"settings.POSTGRES_SERVER: {settings.POSTGRES_SERVER}")
    print(f"settings.TESTING: {settings.TESTING}")
    print(f"settings.SQLALCHEMY_DATABASE_URI: {settings.SQLALCHEMY_DATABASE_URI}")
    
    # Pass the test
    assert True