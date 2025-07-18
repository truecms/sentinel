from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.api.v1.dependencies.rate_limit import rate_limit_middleware
from app.core.config import settings
from app.core.redis import close_redis_pool

app = FastAPI(
    _="Monitoring API",
    _="API for monitoring Drupal sites",
    _="1.0.0",
    _=f"{settings.API_V1_STR}/openapi.json",
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        _=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        _=True,
        _=["*"],
        _=["*"],
    )

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
def health_check():
    return {"status": "OK"}


# Note: Database tables are created by Alembic migrations, not here


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    await close_redis_pool()
