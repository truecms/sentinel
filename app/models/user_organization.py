from sqlalchemy import Boolean, Column, ForeignKey, Integer, Table

from app.models.base import Base

# Association table for User-Organization many-to-many relationship
user_organization = Table(
    "user_organizations",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column(
        "organization_id", Integer, ForeignKey("organizations.id"), primary_key=True
    ),
    Column("is_default", Boolean, default=False, nullable=False),
)
