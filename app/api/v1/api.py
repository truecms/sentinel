from fastapi import APIRouter

from app.api.v1.endpoints import (auth, dashboard, module_sites,
                                  module_versions, module_versions_global,
                                  module_versions_standalone, modules,
                                  organizations, roles, sites, tasks, users,
                                  version_check, ws)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    organizations.router, prefix="/organizations", tags=["organizations"]
)
api_router.include_router(sites.router, prefix="/sites", tags=["sites"])
api_router.include_router(modules.router, prefix="/modules", tags=["modules"])
api_router.include_router(
    module_versions.router, prefix="/modules", tags=["module-versions"]
)
api_router.include_router(
    module_versions_standalone.router,
    prefix="/module-versions",
    tags=["module-versions"],
)
api_router.include_router(
    module_versions_global.router, prefix="", tags=["module-versions"]
)
api_router.include_router(module_sites.router, prefix="/modules", tags=["module-sites"])
api_router.include_router(
    version_check.router, prefix="/version-check", tags=["version-check"]
)
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(dashboard.router, prefix="", tags=["dashboard"])
api_router.include_router(ws.router, prefix="/ws", tags=["websocket"])
api_router.include_router(roles.router, prefix="/rbac", tags=["rbac", "roles"])
