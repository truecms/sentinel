from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Column, Integer, String, DateTime, text, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.user_organization import user_organization

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_at = Column(DateTime, nullable=False, server_default=text('now()'))
    last_login = Column(DateTime, nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    role = Column(String, nullable=True)

    # Relationships
    organization = relationship("Organization", foreign_keys=[organization_id], back_populates="users")
    organizations = relationship(
        "Organization", 
        secondary=user_organization,
        back_populates="users"
    )
    created_organizations = relationship(
        "Organization",
        back_populates="creator",
        foreign_keys="[Organization.created_by]"
    )
