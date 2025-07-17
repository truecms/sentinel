"""Tests for update detector service."""

from unittest.mock import AsyncMock

import pytest

from app.services.update_detector import UpdateDetector, UpdateInfo


class TestUpdateDetector:
    """Test cases for UpdateDetector."""

    @pytest.fixture
    def detector(self):
        """Create an UpdateDetector instance."""
        return UpdateDetector()

    def test_update_info_initialization(self):
        """Test UpdateInfo class initialization."""
        # Test with defaults
        info = UpdateInfo("1.0.0")
        assert info.current_version == "1.0.0"
        assert info.latest_version is None
        assert info.latest_security_version is None
        assert info.update_available is False
        assert info.security_update_available is False
        assert info.version_lag == {}

        # Test with all parameters
        version_lag = {"major": 1, "minor": 2, "patch": 3}
        info = UpdateInfo(
            current_version="1.0.0",
            latest_version="2.2.3",
            latest_security_version="1.0.1-security1",
            update_available=True,
            security_update_available=True,
            version_lag=version_lag,
        )
        assert info.current_version == "1.0.0"
        assert info.latest_version == "2.2.3"
        assert info.latest_security_version == "1.0.1-security1"
        assert info.update_available is True
        assert info.security_update_available is True
        assert info.version_lag == version_lag

    def test_get_version_branch(self, detector):
        """Test getting version branch identifiers."""
        # Drupal contrib versions
        assert detector.get_version_branch("8.x-1.0") == "8.x-1.x"
        assert detector.get_version_branch("9.x-2.5") == "9.x-2.x"

        # Semantic versions
        assert detector.get_version_branch("1.0.0") == "1.x"
        assert detector.get_version_branch("2.5.3") == "2.x"

        # Dev versions
        assert detector.get_version_branch("8.x-1.x-dev") == "8.x-1.x"
        assert detector.get_version_branch("1.x-dev") == "1.x"

        # Invalid version
        assert detector.get_version_branch("invalid") is None

    @pytest.mark.asyncio
    async def test_check_module_updates_no_versions(self, detector):
        """Test check_module_updates when no versions exist."""
        # Mock database session that returns no versions
        mock_db = AsyncMock()
        mock_result = AsyncMock()
        mock_result.fetchall = AsyncMock(return_value=[])
        mock_db.execute = AsyncMock(return_value=mock_result)

        update_info = await detector.check_module_updates(mock_db, 1, "1.0.0")

        assert update_info.current_version == "1.0.0"
        assert update_info.latest_version is None
        assert update_info.security_update_available is False
        assert update_info.update_available is False

    @pytest.mark.asyncio
    async def test_check_module_updates_invalid_current_version(self, detector):
        """Test check_module_updates with invalid current version."""
        # Mock database session that returns versions
        mock_db = AsyncMock()
        mock_result = AsyncMock()
        mock_result.fetchall = AsyncMock(return_value=[("1.0.0",), ("1.1.0",)])
        mock_db.execute = AsyncMock(return_value=mock_result)

        update_info = await detector.check_module_updates(mock_db, 1, "invalid-version")

        assert update_info.current_version == "invalid-version"
        assert update_info.latest_version is None
        assert update_info.update_available is False

    @pytest.mark.asyncio
    async def test_batch_check_updates_empty(self, detector):
        """Test batch_check_updates with empty list."""
        mock_db = AsyncMock()

        results = await detector.batch_check_updates(mock_db, [])

        assert results == {}

    @pytest.mark.asyncio
    async def test_batch_check_updates_no_versions(self, detector):
        """Test batch_check_updates when no versions exist in database."""
        mock_db = AsyncMock()
        mock_result = AsyncMock()
        mock_result.__iter__ = lambda self: iter([])  # No versions found
        mock_db.execute.return_value = mock_result

        module_versions = [(1, "1.0.0"), (2, "2.0.0")]
        results = await detector.batch_check_updates(mock_db, module_versions)

        assert len(results) == 2
        assert 1 in results
        assert 2 in results
        assert results[1].current_version == "1.0.0"
        assert results[2].current_version == "2.0.0"
        assert not results[1].update_available
        assert not results[2].update_available
