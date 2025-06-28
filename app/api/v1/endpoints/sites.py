from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.SiteResponse])
async def read_sites(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_db),
    current_user: schemas.UserResponse = Depends(deps.get_current_user)
):
    """Retrieve sites."""
    sites = await crud.get_sites(db, skip=skip, limit=limit)
    return sites

@router.post("/", response_model=schemas.SiteResponse)
async def create_site(
    *,
    db: AsyncSession = Depends(deps.get_db),
    site_in: schemas.SiteCreate,
    current_user: schemas.UserResponse = Depends(deps.get_current_user)
):
    """Create new site."""
    site = await crud.get_site_by_url(db, url=site_in.url)
    if site:
        raise HTTPException(
            status_code=400,
            detail="The site with this URL already exists."
        )
    site = await crud.create_site(
        db=db,
        site=site_in,
        created_by=current_user.id
    )
    return site

@router.get("/{site_id}", response_model=schemas.SiteResponse)
async def read_site(
    site_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: schemas.UserResponse = Depends(deps.get_current_user)
):
    """Get a specific site by id."""
    site = await crud.get_site(db, site_id=site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site

@router.put("/{site_id}", response_model=schemas.SiteResponse)
async def update_site(
    *,
    db: AsyncSession = Depends(deps.get_db),
    site_id: int,
    site_in: schemas.SiteUpdate,
    current_user: schemas.UserResponse = Depends(deps.get_current_user)
):
    """Update a site."""
    site = await crud.get_site(db, site_id=site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    site = await crud.update_site(
        db=db,
        site_id=site_id,
        site=site_in,
        updated_by=current_user.id
    )
    return site

@router.delete("/{site_id}", response_model=schemas.SiteResponse)
async def delete_site(
    *,
    db: AsyncSession = Depends(deps.get_db),
    site_id: int,
    current_user: schemas.UserResponse = Depends(deps.get_current_user)
):
    """Delete a site."""
    site = await crud.get_site(db, site_id=site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    site = await crud.delete_site(
        db=db,
        site_id=site_id,
        updated_by=current_user.id
    )
    return site
