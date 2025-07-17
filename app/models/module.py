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

    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    machine_name = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    drupal_org_link = Column(String(500), nullable=True)
    module_type = Column(
        String(50), nullable=False, default="contrib"
    )  # contrib, custom, core
    is_covered = Column(Boolean(), default=False)
    is_active = Column(Boolean(), default=True)
    is_deleted = Column(Boolean(), default=False)

    # Audit fields following existing pattern
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    versions = relationship(
        "ModuleVersion", back_populates="module", cascade="all, delete-orphan"
    )
    site_modules = relationship("SiteModule", back_populates="module")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
