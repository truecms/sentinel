#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append('/app')

from httpx import AsyncClient, ASGITransport

async def debug_sync():
    from app.main import app as main_app
    
    async with AsyncClient(
        transport=ASGITransport(app=main_app),
        base_url="http://test",
        follow_redirects=True,
    ) as client:
        # Test the sync endpoint without auth to see the error
        response = await client.post('/api/v1/sites/1/modules/sync', json={
            'site': {
                'url': 'https://modules.example.com',
                'name': 'Module Test Site',
                'token': 'site-auth-token-123',
            },
            'drupal_info': {
                'core_version': '10.3.8',
                'php_version': '8.3.2',
                'ip_address': '192.168.1.100',
            },
            'modules': [
                {
                    'machine_name': 'node',
                    'display_name': 'Node',
                    'module_type': 'core',
                    'enabled': True,
                    'version': '10.3.8',
                }
            ],
        })
        print(f'Status: {response.status_code}')
        print(f'Response: {response.text}')

if __name__ == "__main__":
    asyncio.run(debug_sync())