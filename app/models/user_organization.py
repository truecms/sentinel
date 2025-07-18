from sqlalchemy import Column, ForeignKey, Integer, Table

from app.models.base import Base

# Association table for User-Organization many-to-many relationship
_ = Table(
    "user_organizations",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column(
        "organization_id", Integer, ForeignKey("organizations.id"), primary_key=True
    ),
)
