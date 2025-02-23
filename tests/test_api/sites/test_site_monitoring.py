"""
Tests for site monitoring operations.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.site import Site
from app.models.monitoring_data import MonitoringData
from datetime import datetime, timedelta

pytestmark = pytest.mark.asyncio

async def test_get_site_status(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_monitored_site: Site
):
    """Test getting site monitoring status."""
    response = await client.get(
        f"/api/v1/sites/{test_monitored_site.id}/status",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "last_check_time" in data
    assert "response_time" in data
    assert "ssl_expiry" in data

async def test_get_site_monitoring_history(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_monitored_site: Site,
    db_session: AsyncSession
):
    """Test getting site monitoring history."""
    # Add historical monitoring data
    now = datetime.utcnow()
    for i in range(5):
        check_time = now - timedelta(hours=i)
        monitoring_data = MonitoringData(
            site_id=test_monitored_site.id,
            status="up" if i % 2 == 0 else "down",
            response_time=100 + i * 10,
            check_time=check_time.isoformat() + "Z"
        )
        db_session.add(monitoring_data)
    await db_session.commit()

    response = await client.get(
        f"/api/v1/sites/{test_monitored_site.id}/history",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5
    assert all("status" in entry for entry in data)
    assert all("response_time" in entry for entry in data)
    assert all("check_time" in entry for entry in data)

async def test_get_site_uptime(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_monitored_site: Site,
    db_session: AsyncSession
):
    """Test getting site uptime statistics."""
    # Add monitoring data with mixed status
    now = datetime.utcnow()
    for i in range(10):
        check_time = now - timedelta(hours=i)
        monitoring_data = MonitoringData(
            site_id=test_monitored_site.id,
            status="up" if i < 8 else "down",  # 80% uptime
            response_time=100,
            check_time=check_time.isoformat() + "Z"
        )
        db_session.add(monitoring_data)
    await db_session.commit()

    response = await client.get(
        f"/api/v1/sites/{test_monitored_site.id}/uptime",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "uptime_percentage" in data
    assert data["uptime_percentage"] == 80.0

async def test_get_site_ssl_info(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_monitored_site: Site
):
    """Test getting site SSL certificate information."""
    response = await client.get(
        f"/api/v1/sites/{test_monitored_site.id}/ssl",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "ssl_expiry" in data
    assert "days_until_expiry" in data
    assert "issuer" in data
    assert "subject" in data

async def test_trigger_site_check(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_monitored_site: Site
):
    """Test triggering an immediate site check."""
    response = await client.post(
        f"/api/v1/sites/{test_monitored_site.id}/check",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "response_time" in data
    assert "check_time" in data

async def test_get_site_response_times(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_monitored_site: Site,
    db_session: AsyncSession
):
    """Test getting site response time statistics."""
    # Add monitoring data with various response times
    now = datetime.utcnow()
    response_times = [100, 150, 200, 120, 180]
    for i, rt in enumerate(response_times):
        check_time = now - timedelta(hours=i)
        monitoring_data = MonitoringData(
            site_id=test_monitored_site.id,
            status="up",
            response_time=rt,
            check_time=check_time.isoformat() + "Z"
        )
        db_session.add(monitoring_data)
    await db_session.commit()

    response = await client.get(
        f"/api/v1/sites/{test_monitored_site.id}/response-times",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "average_response_time" in data
    assert "min_response_time" in data
    assert "max_response_time" in data
    assert data["min_response_time"] == 100
    assert data["max_response_time"] == 200

async def test_get_site_alerts(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_monitored_site: Site,
    db_session: AsyncSession
):
    """Test getting site monitoring alerts."""
    # Add some alerts
    now = datetime.utcnow()
    alerts = [
        {"type": "down", "message": "Site is down", "time": now - timedelta(hours=2)},
        {"type": "ssl", "message": "SSL certificate expiring", "time": now - timedelta(hours=1)},
        {"type": "response_time", "message": "High response time", "time": now}
    ]
    
    for alert in alerts:
        monitoring_alert = MonitoringAlert(
            site_id=test_monitored_site.id,
            alert_type=alert["type"],
            message=alert["message"],
            created_at=alert["time"].isoformat() + "Z"
        )
        db_session.add(monitoring_alert)
    await db_session.commit()

    response = await client.get(
        f"/api/v1/sites/{test_monitored_site.id}/alerts",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert all("type" in alert for alert in data)
    assert all("message" in alert for alert in data)
    assert all("created_at" in alert for alert in data) 