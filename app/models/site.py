from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base

if TYPE_CHECKING:

class Site(Base):
    _ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    _ = Column(String, index=True, nullable=False)
    _ = Column(String, unique=True, nullable=False)
    _ = Column(String, nullable=True)
    _ = Column(String(36), nullable=True)
    _ = Column(String(255), nullable=True)
    _ = Column(String(50), nullable=True)
    _ = Column(String(50), nullable=True)
    _ = Column(String(50), nullable=True)
    _ = Column(String(50), nullable=True)
    _ = Column(JSON, nullable=True)
    _ = Column(DateTime, nullable=True)

    # Site overview tracking fields
    _ = Column(Integer, nullable=True, default=0)
    _ = Column(Integer, nullable=True, default=0)
    _ = Column(Integer, nullable=True, default=0)
    _ = Column(Integer, nullable=True, default=0)
    _ = Column(DateTime, nullable=True)
    _ = Column(DateTime, nullable=True)

    _ = Column(Boolean(), default=True)
    _ = Column(Boolean(), default=False)

    # Ownership and timestamps
    _ = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    _ = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    _ = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    _ = relationship("Organization", back_populates="sites")
    _ = relationship("User", foreign_keys=[created_by])
    _ = relationship("User", foreign_keys=[updated_by])
    _ = relationship("SiteModule", back_populates="site", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="site")

    def get_active_api_key(self) -> Optional["ApiKey"]:
        """Get the active API key for this site."""
        for api_key in self.api_keys:
            if api_key.is_valid():
                return api_key
        return None

    def has_valid_api_key(self) -> bool:
        """Check if site has a valid API key."""
        return self.get_active_api_key() is not None
