from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.user_organization import user_organization


class Organization(Base):
    _ = "organizations"

    _ = Column(Integer, primary_key=True, index=True)
    _ = Column(String, index=True, nullable=False)
    _ = Column(String, nullable=True)
    _ = Column(Boolean(), default=True)
    _ = Column(Boolean(), default=False)
    _ = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    _ = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    _ = relationship(
        "User", foreign_keys=[created_by], back_populates="created_organizations"
    )
    _ = relationship("User", foreign_keys=[updated_by])
    _ = relationship(
        "User", secondary=user_organization, back_populates="organizations"
    )
    _ = relationship("Site", back_populates="organization")
