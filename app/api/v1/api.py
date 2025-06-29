from fastapi import APIRouter

from app.api.v1.endpoints import users, auth, organizations, sites, modules, module_versions, module_versions_standalone, module_versions_global, module_sites, tasks, version_check

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(sites.router, prefix="/sites", tags=["sites"])
api_router.include_router(modules.router, prefix="/modules", tags=["modules"])
api_router.include_router(module_versions.router, prefix="/modules", tags=["module-versions"])
api_router.include_router(module_versions_standalone.router, prefix="/module-versions", tags=["module-versions"])
api_router.include_router(module_versions_global.router, prefix="", tags=["module-versions"])
api_router.include_router(module_sites.router, prefix="/modules", tags=["module-sites"])
api_router.include_router(version_check.router, prefix="/version-check", tags=["version-check"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
