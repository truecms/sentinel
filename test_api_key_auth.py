"""Test script to verify API key authentication is working."""

import asyncio
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user import User
from app.models.site import Site
from app.models.api_key import ApiKey
from app.models.organization import Organization


async def test_api_key_authentication():
    """Test that API key authentication works for site endpoints."""
    
    # Get database session
    async for db in get_db():
        try:
            # Create a test organization
            org = Organization(name="Test Organization")
            db.add(org)
            await db.commit()
            await db.refresh(org)
            
            # Create a test site
            site = Site(
                name="Test Site",
                url="https://test.example.com",
                organization_id=org.id,
                site_uuid="test-uuid-123",
                api_token="legacy-token-123"
            )
            db.add(site)
            await db.commit()
            await db.refresh(site)
            
            # Create an API key for the site
            api_key_obj, raw_key = ApiKey.create_for_site(site.id, "Test Site API Key")
            db.add(api_key_obj)
            await db.commit()
            
            print(f"✅ Created test site with ID: {site.id}")
            print(f"✅ Generated API key: {raw_key[:20]}...")
            print(f"✅ API key hash: {api_key_obj.key_hash[:20]}...")
            
            # Test API key authentication
            base_url = "http://localhost:8000"
            
            # Test 1: API key authentication
            print("\n🔍 Testing API key authentication...")
            
            test_data = {
                "site": {
                    "name": "Test Site",
                    "url": "https://test.example.com",
                    "site_uuid": "test-uuid-123",
                    "drupal_core_version": "10.0.0"
                },
                "modules": [
                    {
                        "name": "Test Module",
                        "machine_name": "test_module",
                        "project_name": "test_module",
                        "version": "1.0.0",
                        "status": "enabled"
                    }
                ]
            }
            
            # Test with API key
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{base_url}/api/v1/sites/{site.id}/modules",
                    json=test_data,
                    headers={"X-API-Key": raw_key}
                )
                
                if response.status_code == 200:
                    print("✅ API key authentication successful!")
                    print(f"   Response: {response.json()}")
                else:
                    print(f"❌ API key authentication failed: {response.status_code}")
                    print(f"   Response: {response.text}")
            
            # Test 2: Legacy site authentication (should still work)
            print("\n🔍 Testing legacy site authentication...")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{base_url}/api/v1/sites/{site.id}/modules",
                    json=test_data,
                    headers={
                        "X-Site-UUID": site.site_uuid,
                        "X-API-Token": site.api_token
                    }
                )
                
                if response.status_code == 200:
                    print("✅ Legacy site authentication successful!")
                    print(f"   Response: {response.json()}")
                else:
                    print(f"❌ Legacy site authentication failed: {response.status_code}")
                    print(f"   Response: {response.text}")
            
            # Test 3: Invalid API key
            print("\n🔍 Testing invalid API key...")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{base_url}/api/v1/sites/{site.id}/modules",
                    json=test_data,
                    headers={"X-API-Key": "invalid-key"}
                )
                
                if response.status_code == 401:
                    print("✅ Invalid API key correctly rejected!")
                else:
                    print(f"❌ Invalid API key not properly rejected: {response.status_code}")
                    print(f"   Response: {response.text}")
            
            # Test 4: Role management endpoints
            print("\n🔍 Testing role management endpoints...")
            
            async with httpx.AsyncClient() as client:
                # Test listing roles
                response = await client.get(
                    f"{base_url}/api/v1/rbac/roles",
                    headers={"X-API-Key": raw_key}
                )
                
                if response.status_code == 200:
                    roles = response.json()
                    print(f"✅ Successfully listed {len(roles)} roles")
                    for role in roles:
                        print(f"   - {role['name']}: {role['display_name']}")
                else:
                    print(f"❌ Failed to list roles: {response.status_code}")
                    print(f"   Response: {response.text}")
                
                # Test listing permissions
                response = await client.get(
                    f"{base_url}/api/v1/rbac/permissions",
                    headers={"X-API-Key": raw_key}
                )
                
                if response.status_code == 200:
                    permissions = response.json()
                    print(f"✅ Successfully listed {len(permissions)} permissions")
                    for perm in permissions[:5]:  # Show first 5
                        print(f"   - {perm['name']}: {perm['description']}")
                else:
                    print(f"❌ Failed to list permissions: {response.status_code}")
                    print(f"   Response: {response.text}")
            
            print("\n✅ All tests completed!")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Clean up test data
            try:
                # Delete test data
                await db.execute(f"DELETE FROM api_keys WHERE site_id = {site.id}")
                await db.execute(f"DELETE FROM sites WHERE id = {site.id}")
                await db.execute(f"DELETE FROM organizations WHERE id = {org.id}")
                await db.commit()
                print("🧹 Test data cleaned up")
            except:
                pass
            
            await db.close()
            break


if __name__ == "__main__":
    print("🚀 Starting API key authentication test...")
    asyncio.run(test_api_key_authentication())