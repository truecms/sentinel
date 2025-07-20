# Using Sample Data in CI/CD

This document explains how to use sample data in your CI/CD pipeline for more realistic integration testing.

## Overview

The test suite includes a `load_sample_data` fixture that can populate the test database with realistic sample data. This is particularly useful for:

- Integration tests that need realistic data
- CI/CD pipelines that test against production-like scenarios
- Testing dashboard and reporting features
- Validating security update detection

## Enabling Sample Data Loading

To enable sample data loading in your tests, set the environment variable:

```bash
export LOAD_SAMPLE_DATA=true
```

## CI/CD Configuration

### GitHub Actions Example

```yaml
- name: Run tests with sample data
  env:
    LOAD_SAMPLE_DATA: true
  run: |
    docker compose run test pytest tests/integration/test_sample_data_loading.py -v
```

### GitLab CI Example

```yaml
test-with-sample-data:
  stage: test
  variables:
    LOAD_SAMPLE_DATA: "true"
  script:
    - docker compose run test pytest tests/integration/test_sample_data_loading.py -v
```

## What Sample Data Includes

The sample data (`tests/fixtures/sample_data.sql`) includes:

1. **Modules**: 
   - Core modules (views, node, user, system)
   - Contrib modules (webform, pathauto, token, metatag)
   - Custom modules (custom_auth)

2. **Module Versions**:
   - Current versions
   - Available updates
   - Security updates

3. **Sites**:
   - Test Production Site (fully updated, security score: 92)
   - Test Staging Site (2 security updates needed, security score: 78)
   - Test Development Site (3 security updates needed, security score: 65)

4. **Site Modules**:
   - Module installations per site
   - Update availability flags
   - Security update indicators

## Writing Tests with Sample Data

### Basic Test Structure

```python
import os
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.skipif(
    os.getenv("LOAD_SAMPLE_DATA") != "true",
    reason="Sample data loading is not enabled"
)
class TestWithSampleData:
    @pytest.mark.asyncio
    async def test_with_sample_data(
        self, db_session: AsyncSession, load_sample_data, client, superuser_token_headers
    ):
        """Test with realistic sample data."""
        # Your test code here
```

### Example: Dashboard Overview Test

```python
@pytest.mark.asyncio
async def test_dashboard_overview_with_sample_data(
    self, db_session: AsyncSession, load_sample_data, client, superuser_token_headers
):
    """Test dashboard overview API with realistic sample data."""
    response = await client.get(
        "/api/v1/dashboard/overview",
        headers=superuser_token_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify metrics with actual sample data
    metrics = data["metrics"]
    assert metrics["total_sites"] >= 3  # We loaded 3 test sites
    
    # Verify vulnerability counts
    vulnerabilities = metrics["vulnerabilities"]
    assert vulnerabilities["critical"] >= 0
    assert vulnerabilities["high"] >= 0
```

### Example: Sites API Test

```python
@pytest.mark.asyncio
async def test_sample_sites_loaded(
    self, db_session: AsyncSession, load_sample_data
):
    """Test that sample sites are loaded correctly."""
    from sqlalchemy import select
    from app.models.site import Site
    
    result = await db_session.execute(
        select(Site).where(Site.organization_id == 1)
    )
    sites = result.scalars().all()
    
    assert len(sites) == 3
    
    # Verify site security scores
    for site in sites:
        if "Production" in site.name:
            assert site.security_score == 92
            assert site.security_updates_count == 0
        elif "Staging" in site.name:
            assert site.security_score == 78
            assert site.security_updates_count == 2
        elif "Development" in site.name:
            assert site.security_score == 65
            assert site.security_updates_count == 3
```

## Benefits

1. **Realistic Testing**: Tests run against data that mirrors production scenarios
2. **Consistent State**: Every CI/CD run starts with the same known data state
3. **Security Testing**: Pre-populated security issues for testing security features
4. **Performance Testing**: Enough data to test performance characteristics

## Maintenance

The sample data file is located at `tests/fixtures/sample_data.sql`. When updating:

1. Ensure backward compatibility
2. Document any new test scenarios added
3. Update this documentation if new data patterns are introduced
4. Test locally with `LOAD_SAMPLE_DATA=true` before committing