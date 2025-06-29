"""Tests for enhanced sync endpoint with rate limiting and caching."""
import pytest
import asyncio
import json
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import get_redis, RATE_LIMIT_WINDOW, RATE_LIMIT_MAX_REQUESTS
from app.services.cache import ModuleCacheService


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    @pytest.mark.asyncio
    async def test_rate_limit_allows_requests_within_limit(
        self,
        client: AsyncClient,
        db: AsyncSession,
        auth_headers: dict,
        test_site: dict
    ):
        """Test that requests within rate limit are allowed."""
        # Create test payload
        payload = {
            "site": {
                "url": test_site["url"],
                "name": test_site["name"],
                "token": "test-token"
            },
            "drupal_info": {
                "core_version": "10.3.8",
                "php_version": "8.3.2",
                "ip_address": "192.168.1.100"
            },
            "modules": [
                {
                    "machine_name": f"test_module_{i}",
                    "display_name": f"Test Module {i}",
                    "module_type": "contrib",
                    "enabled": True,
                    "version": "1.0.0"
                }
                for i in range(10)
            ]
        }
        
        # Make requests up to the limit
        for i in range(RATE_LIMIT_MAX_REQUESTS):
            response = await client.post(
                f"/api/v1/sites/{test_site['id']}/modules",
                json=payload,
                headers=auth_headers
            )
            assert response.status_code == 200
            
            # Check rate limit headers
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers
            assert int(response.headers["X-RateLimit-Remaining"]) == RATE_LIMIT_MAX_REQUESTS - i - 1
    
    @pytest.mark.asyncio
    async def test_rate_limit_blocks_excessive_requests(
        self,
        client: AsyncClient,
        db: AsyncSession,
        auth_headers: dict,
        test_site: dict
    ):
        """Test that requests exceeding rate limit are blocked."""
        # Create test payload
        payload = {
            "site": {
                "url": test_site["url"],
                "name": test_site["name"],
                "token": "test-token"
            },
            "drupal_info": {
                "core_version": "10.3.8",
                "php_version": "8.3.2",
                "ip_address": "192.168.1.100"
            },
            "modules": [
                {
                    "machine_name": "test_module",
                    "display_name": "Test Module",
                    "module_type": "contrib",
                    "enabled": True,
                    "version": "1.0.0"
                }
            ]
        }
        
        # Clear any existing rate limit data
        redis_client = await get_redis()
        await redis_client.delete(f"rate_limit:site:{test_site['id']}:sync")
        
        # Make requests up to and beyond the limit
        for i in range(RATE_LIMIT_MAX_REQUESTS + 1):
            response = await client.post(
                f"/api/v1/sites/{test_site['id']}/modules",
                json=payload,
                headers=auth_headers
            )
            
            if i < RATE_LIMIT_MAX_REQUESTS:
                assert response.status_code == 200
            else:
                # Should be rate limited
                assert response.status_code == 429
                assert "Rate limit exceeded" in response.json()["detail"]
                assert "Retry-After" in response.headers


class TestCaching:
    """Test caching functionality."""
    
    @pytest.mark.asyncio
    async def test_module_cache_hit(
        self,
        db: AsyncSession,
        test_module: dict
    ):
        """Test that module cache returns cached data."""
        # First call should hit database
        with patch('app.crud.crud_module.get_module_by_machine_name') as mock_get:
            mock_get.return_value = test_module
            module1 = await ModuleCacheService.get_module_by_machine_name(
                db, test_module["machine_name"]
            )
            assert mock_get.called
        
        # Second call should hit cache
        with patch('app.crud.crud_module.get_module_by_machine_name') as mock_get:
            module2 = await ModuleCacheService.get_module_by_machine_name(
                db, test_module["machine_name"]
            )
            assert not mock_get.called
            assert module2.id == module1.id
    
    @pytest.mark.asyncio
    async def test_cache_invalidation(
        self,
        db: AsyncSession,
        test_module: dict
    ):
        """Test that cache invalidation works."""
        # Cache the module
        await ModuleCacheService.get_module_by_machine_name(
            db, test_module["machine_name"]
        )
        
        # Invalidate cache
        await ModuleCacheService.invalidate_module_cache(test_module["machine_name"])
        
        # Next call should hit database again
        with patch('app.crud.crud_module.get_module_by_machine_name') as mock_get:
            mock_get.return_value = test_module
            await ModuleCacheService.get_module_by_machine_name(
                db, test_module["machine_name"]
            )
            assert mock_get.called


class TestBackgroundProcessing:
    """Test background processing for large payloads."""
    
    @pytest.mark.asyncio
    async def test_large_payload_triggers_background_processing(
        self,
        client: AsyncClient,
        db: AsyncSession,
        auth_headers: dict,
        test_site: dict
    ):
        """Test that large payloads are processed in background."""
        # Create large payload (>500 modules)
        payload = {
            "site": {
                "url": test_site["url"],
                "name": test_site["name"],
                "token": "test-token"
            },
            "drupal_info": {
                "core_version": "10.3.8",
                "php_version": "8.3.2",
                "ip_address": "192.168.1.100"
            },
            "modules": [
                {
                    "machine_name": f"test_module_{i}",
                    "display_name": f"Test Module {i}",
                    "module_type": "contrib",
                    "enabled": True,
                    "version": "1.0.0"
                }
                for i in range(600)  # More than 500 modules
            ]
        }
        
        with patch('app.tasks.sync_tasks.sync_site_modules_task.delay') as mock_task:
            mock_task.return_value.id = "test-task-id"
            
            response = await client.post(
                f"/api/v1/sites/{test_site['id']}/modules",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "accepted"
            assert data["task_id"] == "test-task-id"
            assert "status_url" in data
            assert mock_task.called
    
    @pytest.mark.asyncio
    async def test_small_payload_processed_synchronously(
        self,
        client: AsyncClient,
        db: AsyncSession,
        auth_headers: dict,
        test_site: dict
    ):
        """Test that small payloads are processed synchronously."""
        # Create small payload (<500 modules)
        payload = {
            "site": {
                "url": test_site["url"],
                "name": test_site["name"],
                "token": "test-token"
            },
            "drupal_info": {
                "core_version": "10.3.8",
                "php_version": "8.3.2",
                "ip_address": "192.168.1.100"
            },
            "modules": [
                {
                    "machine_name": f"test_module_{i}",
                    "display_name": f"Test Module {i}",
                    "module_type": "contrib",
                    "enabled": True,
                    "version": "1.0.0"
                }
                for i in range(10)  # Only 10 modules
            ]
        }
        
        with patch('app.tasks.sync_tasks.sync_site_modules_task.delay') as mock_task:
            response = await client.post(
                f"/api/v1/sites/{test_site['id']}/modules",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "modules_processed" in data
            assert data["modules_processed"] == 10
            assert not mock_task.called  # Should not use background task


@pytest.fixture
async def test_module(db: AsyncSession):
    """Create a test module for caching tests."""
    from app.models import Module
    
    module = Module(
        id=1,
        machine_name="test_module",
        display_name="Test Module",
        module_type="contrib",
        description="Test module for caching",
        created_by=1,
        updated_by=1,
        is_active=True,
        is_deleted=False
    )
    return module


@pytest.fixture
async def test_site(db: AsyncSession):
    """Create a test site for rate limiting tests."""
    return {
        "id": 1,
        "url": "https://test-site.com",
        "name": "Test Site",
        "organization_id": 1
    }