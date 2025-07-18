from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Module(Base):
    """
    Module model for tracking Drupal modules in the monitoring system.

    Represents a single Drupal module that can be installed across multiple sites.
    Tracks basic module information and relationships to versions and site installations.
    """

    _ = "modules"

    _ = Column(Integer, primary_key=True, index=True)
    _ = Column(String(255), unique=True, nullable=False, index=True)
    _ = Column(String(255), nullable=False)
    _ = Column(String(500), nullable=True)
    _ = Column(String(50), nullable=False, default="contrib")  # contrib, custom, core
    _ = Column(Boolean(), default=False)
    _ = Column(Boolean(), default=True)
    _ = Column(Boolean(), default=False)

    # Audit fields following existing pattern
    _ = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    _ = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    _ = relationship(
        "ModuleVersion", back_populates="module", cascade="all, delete-orphan"
    )
    _ = relationship("SiteModule", back_populates="module")
    _ = relationship("User", foreign_keys=[created_by])
    _ = relationship("User", foreign_keys=[updated_by])
