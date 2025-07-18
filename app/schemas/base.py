"""Base schemas for common API patterns."""

from fastapi import Query
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema."""

    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int


class PaginationParams(BaseModel):
    """Pagination parameters for API endpoints."""

    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=10, ge=1, le=100, description="Items per page")

    @property
    def skip(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get limit for database queries."""
        return self.page_size


def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
) -> PaginationParams:
    """Dependency for pagination parameters."""
    return PaginationParams(page=page, page_size=page_size)
