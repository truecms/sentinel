from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.user_organization import user_organization


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean(), default=True)
    is_deleted = Column(Boolean(), default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    creator = relationship(
        "User", foreign_keys=[created_by], back_populates="created_organizations"
    )
    updater = relationship("User", foreign_keys=[updated_by])
    users = relationship(
        "User", secondary=user_organization, back_populates="organizations"
    )
    sites = relationship("Site", back_populates="organization")
