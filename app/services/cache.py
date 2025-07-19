"""Caching service for modules and versions."""

import json
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.core.redis import MODULE_CACHE_TTL, VERSION_CACHE_TTL, get_redis
from app.models import Module, ModuleVersion


class ModuleCacheService:
    """Service for caching module and version data."""

    @staticmethod
    async def get_module_by_machine_name(
        db: AsyncSession, machine_name: str
    ) -> Optional[Module]:
        """
        Get module by machine name with caching.

        Args:
            db: Database session
            machine_name: Module machine name

        Returns:
            Module object or None
        """
        redis_client = await get_redis()
        cache_key = f"module:machine_name:{machine_name}"

        # Try to get from cache
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            module_data = json.loads(cached_data)
            # Reconstruct Module object from cached data
            return Module(**module_data)

        # Get from database
        module = await crud.crud_module.get_module_by_machine_name(db, machine_name)

        if module:
            # Cache the result
            module_dict = {
                "id": module.id,
                "machine_name": module.machine_name,
                "display_name": module.display_name,
                "module_type": module.module_type,
                "description": module.description,
                "created_at": module.created_at.isoformat(),
                "updated_at": module.updated_at.isoformat(),
                "created_by": module.created_by,
                "updated_by": module.updated_by,
                "is_active": module.is_active,
                "is_deleted": module.is_deleted,
            }
            await redis_client.setex(
                cache_key, MODULE_CACHE_TTL, json.dumps(module_dict)
            )

        return module

    @staticmethod
    async def get_version_by_module_and_string(
        db: AsyncSession, module_id: int, version_string: str
    ) -> Optional[ModuleVersion]:
        """
        Get module version by module ID and version string with caching.

        Args:
            db: Database session
            module_id: Module ID
            version_string: Version string

        Returns:
            ModuleVersion object or None
        """
        redis_client = await get_redis()
        cache_key = f"version:module:{module_id}:version:{version_string}"

        # Try to get from cache
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            version_data = json.loads(cached_data)
            # Reconstruct ModuleVersion object from cached data
            return ModuleVersion(**version_data)

        # Get from database
        version = await crud.crud_module_version.get_version_by_module_and_string(
            db, module_id, version_string
        )

        if version:
            # Cache the result
            version_dict = {
                "id": version.id,
                "module_id": version.module_id,
                "version_string": version.version_string,
                "semantic_version": version.semantic_version,
                "release_date": (
                    version.release_date.isoformat() if version.release_date else None
                ),
                "is_security_update": version.is_security_update,
                "release_notes_link": version.release_notes_link,
                "drupal_core_compatibility": version.drupal_core_compatibility,
                "created_at": version.created_at.isoformat(),
                "updated_at": version.updated_at.isoformat(),
                "created_by": version.created_by,
                "updated_by": version.updated_by,
                "is_active": version.is_active,
                "is_deleted": version.is_deleted,
            }
            await redis_client.setex(
                cache_key, VERSION_CACHE_TTL, json.dumps(version_dict)
            )

        return version

    @staticmethod
    async def invalidate_module_cache(machine_name: str):
        """Invalidate module cache by machine name."""
        redis_client = await get_redis()
        cache_key = f"module:machine_name:{machine_name}"
        await redis_client.delete(cache_key)

    @staticmethod
    async def invalidate_version_cache(module_id: int, version_string: str):
        """Invalidate version cache."""
        redis_client = await get_redis()
        cache_key = f"version:module:{module_id}:version:{version_string}"
        await redis_client.delete(cache_key)

    @staticmethod
    async def bulk_get_modules(
        db: AsyncSession, machine_names: List[str]
    ) -> dict[str, Module]:
        """
        Bulk get modules by machine names with caching.

        Args:
            db: Database session
            machine_names: List of module machine names

        Returns:
            Dictionary mapping machine names to Module objects
        """
        redis_client = await get_redis()
        result = {}
        uncached_names = []

        # Try to get from cache
        for name in machine_names:
            cache_key = f"module:machine_name:{name}"
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                module_data = json.loads(cached_data)
                result[name] = Module(**module_data)
            else:
                uncached_names.append(name)

        # Get uncached modules from database
        if uncached_names:
            modules = await crud.crud_module.get_modules_by_machine_names(
                db, uncached_names
            )

            # Cache the results
            for module in modules:
                result[module.machine_name] = module

                module_dict = {
                    "id": module.id,
                    "machine_name": module.machine_name,
                    "display_name": module.display_name,
                    "module_type": module.module_type,
                    "description": module.description,
                    "created_at": module.created_at.isoformat(),
                    "updated_at": module.updated_at.isoformat(),
                    "created_by": module.created_by,
                    "updated_by": module.updated_by,
                    "is_active": module.is_active,
                    "is_deleted": module.is_deleted,
                }
                cache_key = f"module:machine_name:{module.machine_name}"
                await redis_client.setex(
                    cache_key, MODULE_CACHE_TTL, json.dumps(module_dict)
                )

        return result
