"""
API endpoints for version checking and update detection.
"""

from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api import deps
from app.models.user import User
from app.services.update_detector import UpdateDetector, UpdateInfo
from app.services.version_comparator import VersionComparator
from app.schemas.module_version import VersionCheckRequest, VersionCheckResponse, UpdateCheckResponse


router = APIRouter()


@router.post("/check-updates", response_model=UpdateCheckResponse)
async def check_module_updates(
    *,
    db: AsyncSession = Depends(deps.get_db),
    request: VersionCheckRequest,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Check if updates are available for a specific module version.
    
    This endpoint:
    - Parses the provided version string
    - Checks for newer compatible versions
    - Identifies security updates
    - Returns update availability information
    """
    # Verify module exists
    module = await crud.crud_module.get_module_by_machine_name(db, request.machine_name)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module '{request.machine_name}' not found"
        )
    
    # Check for updates
    detector = UpdateDetector()
    update_info = await detector.check_module_updates(
        db, module.id, request.current_version
    )
    
    return UpdateCheckResponse(
        machine_name=request.machine_name,
        current_version=request.current_version,
        latest_version=update_info.latest_version,
        latest_security_version=update_info.latest_security_version,
        update_available=update_info.update_available,
        security_update_available=update_info.security_update_available,
        version_lag=update_info.version_lag
    )


@router.post("/batch-check-updates", response_model=List[UpdateCheckResponse])
async def batch_check_updates(
    *,
    db: AsyncSession = Depends(deps.get_db),
    requests: List[VersionCheckRequest],
    current_user: User = Depends(deps.get_current_user)
):
    """
    Check updates for multiple modules at once.
    
    Efficiently processes multiple module update checks in a single request.
    Useful for checking updates for an entire site's modules.
    
    Limit: 100 modules per request.
    """
    if len(requests) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 modules per batch request"
        )
    
    # Get all module names
    module_names = [req.machine_name for req in requests]
    
    # Fetch modules by machine names
    modules = await crud.crud_module.get_modules_by_machine_names(db, module_names)
    module_map = {m.machine_name: m for m in modules}
    
    # Build list of (module_id, version) tuples for modules that exist
    module_versions = []
    for req in requests:
        if req.machine_name in module_map:
            module_versions.append((module_map[req.machine_name].id, req.current_version))
    
    # Batch check updates
    detector = UpdateDetector()
    update_results = await detector.batch_check_updates(db, module_versions)
    
    # Build response
    responses = []
    for req in requests:
        if req.machine_name not in module_map:
            # Module not found
            responses.append(UpdateCheckResponse(
                machine_name=req.machine_name,
                current_version=req.current_version,
                latest_version=None,
                latest_security_version=None,
                update_available=False,
                security_update_available=False,
                version_lag={}
            ))
        else:
            module_id = module_map[req.machine_name].id
            if module_id in update_results:
                update_info = update_results[module_id]
                responses.append(UpdateCheckResponse(
                    machine_name=req.machine_name,
                    current_version=req.current_version,
                    latest_version=update_info.latest_version,
                    latest_security_version=update_info.latest_security_version,
                    update_available=update_info.update_available,
                    security_update_available=update_info.security_update_available,
                    version_lag=update_info.version_lag
                ))
            else:
                # No update info available
                responses.append(UpdateCheckResponse(
                    machine_name=req.machine_name,
                    current_version=req.current_version,
                    latest_version=None,
                    latest_security_version=None,
                    update_available=False,
                    security_update_available=False,
                    version_lag={}
                ))
    
    return responses


@router.post("/compare-versions", response_model=VersionCheckResponse)
async def compare_versions(
    *,
    version1: str,
    version2: str,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Compare two version strings.
    
    Returns:
    - comparison: -1 if version1 < version2, 0 if equal, 1 if version1 > version2
    - version1_parsed: Parsed components of version1
    - version2_parsed: Parsed components of version2
    """
    comparator = VersionComparator()
    
    try:
        comparison = comparator.compare(version1, version2)
        parsed1 = comparator.parser.parse(version1)
        parsed2 = comparator.parser.parse(version2)
        
        return VersionCheckResponse(
            comparison=comparison,
            version1=version1,
            version2=version2,
            version1_parsed={
                "drupal_core": parsed1.drupal_core,
                "major": parsed1.major,
                "minor": parsed1.minor,
                "patch": parsed1.patch,
                "release_type": parsed1.release_type.value,
                "release_number": parsed1.release_number,
                "semantic": parsed1.to_semantic()
            },
            version2_parsed={
                "drupal_core": parsed2.drupal_core,
                "major": parsed2.major,
                "minor": parsed2.minor,
                "patch": parsed2.patch,
                "release_type": parsed2.release_type.value,
                "release_number": parsed2.release_number,
                "semantic": parsed2.to_semantic()
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid version string: {str(e)}"
        )