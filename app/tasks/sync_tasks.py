"""Background tasks for module sync operations."""

import json
import time
from typing import Any, Dict, List

from celery import current_task
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app import crud, schemas
from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.redis import get_redis
from app.services.cache import ModuleCacheService

# Create async database engine for background tasks
engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@celery_app.task(bind=True, name="sync_site_modules_task")
def sync_site_modules_task(
    self, site_id: int, payload_json: str, user_id: int
) -> Dict[str, Any]:
    """
    Background task to sync site modules for large payloads.

    Args:
        site_id: Site ID
        payload_json: JSON serialized DrupalSiteSync payload
        user_id: User ID performing the sync

    Returns:
        Sync result dictionary
    """
    import asyncio

    # Run the async function in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(
            _async_sync_site_modules(self.request.id, site_id, payload_json, user_id)
        )
        return result
    finally:
        loop.close()


async def _async_sync_site_modules(
    task_id: str, site_id: int, payload_json: str, user_id: int
) -> Dict[str, Any]:
    """
    Async implementation of the sync task.
    """
    async with AsyncSessionLocal() as db:
        # Parse payload
        payload_data = json.loads(payload_json)
        modules = payload_data["modules"]
        drupal_info = payload_data["drupal_info"]
        site_info = payload_data["site"]

        # Initialize counters
        total_modules = len(modules)
        modules_processed = 0
        modules_created = 0
        modules_updated = 0
        modules_unchanged = 0
        errors = []

        # Update task progress
        current_task.update_state(
            state="PROGRESS",
            meta={
                "current": 0,
                "total": total_modules,
                "status": "Starting module sync...",
            },
        )

        # Process in batches for better performance
        batch_size = 100
        for i in range(0, total_modules, batch_size):
            batch = modules[i : i + batch_size]
            batch_errors = await _process_module_batch(
                db, site_id, batch, drupal_info, user_id
            )

            modules_processed += len(batch)
            modules_created += batch_errors.get("created", 0)
            modules_updated += batch_errors.get("updated", 0)
            modules_unchanged += batch_errors.get("unchanged", 0)
            errors.extend(batch_errors.get("errors", []))

            # Update progress
            current_task.update_state(
                state="PROGRESS",
                meta={
                    "current": modules_processed,
                    "total": total_modules,
                    "status": f"Processed {modules_processed}/{total_modules} modules",
                },
            )

        # Update site's last sync time
        site_update = schemas.SiteUpdate(name=site_info["name"])
        await crud.update_site(db, site_id, site_update, user_id)

        # Store result in Redis
        redis_client = await get_redis()
        result = {
            "site_id": site_id,
            "modules_processed": modules_processed,
            "modules_created": modules_created,
            "modules_updated": modules_updated,
            "modules_unchanged": modules_unchanged,
            "errors": errors,
            "message": f"Successfully synced {modules_processed} modules",
            "completed_at": int(time.time()),
        }

        # Store result with 24 hour TTL
        await redis_client.setex(f"task_result:{task_id}", 86400, json.dumps(result))

        return result


async def _process_module_batch(
    db: AsyncSession,
    site_id: int,
    modules: List[Dict[str, Any]],
    drupal_info: Dict[str, Any],
    user_id: int,
) -> Dict[str, Any]:
    """
    Process a batch of modules.
    """
    results = {"created": 0, "updated": 0, "unchanged": 0, "errors": []}

    # Get all machine names in the batch
    machine_names = [m["machine_name"] for m in modules]

    # Bulk fetch existing modules
    existing_modules = await ModuleCacheService.bulk_get_modules(db, machine_names)

    for module_info in modules:
        try:
            machine_name = module_info["machine_name"]

            # Check if module exists
            module = existing_modules.get(machine_name)
            if not module:
                # Create new module
                module_create = schemas.ModuleCreate(
                    machine_name=machine_name,
                    display_name=module_info["display_name"],
                    module_type=module_info["module_type"],
                    description=module_info.get("description"),
                )
                module = await crud.crud_module.create_module(
                    db, module_create, user_id
                )
                results["created"] += 1

                # Invalidate cache
                await ModuleCacheService.invalidate_module_cache(machine_name)

            # Check if version exists
            version = await ModuleCacheService.get_version_by_module_and_string(
                db, module.id, module_info["version"]
            )
            if not version:
                # Create new version
                version_create = schemas.ModuleVersionCreate(
                    module_id=module.id,
                    version_string=module_info["version"],
                    drupal_core_compatibility=[drupal_info["core_version"]],
                )
                version = await crud.crud_module_version.create_module_version(
                    db, version_create, user_id
                )

                # Invalidate cache
                await ModuleCacheService.invalidate_version_cache(
                    module.id, module_info["version"]
                )

            # Check if site-module association exists
            site_module = (
                await crud.crud_site_module.get_site_module_by_site_and_module(
                    db, site_id, module.id
                )
            )
            if site_module:
                # Update existing association
                if (
                    site_module.current_version_id != version.id
                    or site_module.enabled != module_info["enabled"]
                ):
                    update_data = schemas.SiteModuleUpdate(
                        current_version_id=version.id, enabled=module_info["enabled"]
                    )
                    await crud.crud_site_module.update_site_module(
                        db, site_id, module.id, update_data, user_id
                    )
                    results["updated"] += 1
                else:
                    results["unchanged"] += 1
            else:
                # Create new association
                site_module_create = schemas.SiteModuleCreate(
                    site_id=site_id,
                    module_id=module.id,
                    current_version_id=version.id,
                    enabled=module_info["enabled"],
                )
                await crud.crud_site_module.create_site_module(
                    db, site_module_create, user_id
                )
                results["created"] += 1

        except Exception as e:
            results["errors"].append(
                {"module": module_info["machine_name"], "error": str(e)}
            )

    return results


@celery_app.task(name="get_task_status")
def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get the status of a background task."""
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(_get_task_status_async(task_id))
        return result
    finally:
        loop.close()


async def _get_task_status_async(task_id: str) -> Dict[str, Any]:
    """Get task status from Redis."""
    redis_client = await get_redis()

    # Check if task result exists
    result_key = f"task_result:{task_id}"
    result_data = await redis_client.get(result_key)

    if result_data:
        return {"status": "completed", "result": json.loads(result_data)}

    # Check if task is still running
    task = celery_app.AsyncResult(task_id)
    if task.state == "PENDING":
        return {"status": "pending", "message": "Task is pending execution"}
    elif task.state == "PROGRESS":
        return {"status": "in_progress", "progress": task.info}
    elif task.state == "SUCCESS":
        return {"status": "completed", "result": task.result}
    elif task.state == "FAILURE":
        return {"status": "failed", "error": str(task.info)}
    else:
        return {"status": task.state.lower(), "info": task.info}
