from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class ModuleVersion(Base):
    """
    ModuleVersion model for tracking different versions of Drupal modules.

    Each module can have multiple versions, and each version can be installed
    on multiple sites. Tracks version-specific information like security updates
    and Drupal core compatibility.
    """

    __tablename__ = "module_versions"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False, index=True)
    version_string = Column(String(50), nullable=False)
    release_date = Column(DateTime, nullable=True)
    is_security_update = Column(Boolean, default=False, nullable=False)
    release_notes = Column(String, nullable=True)  # Text field in database
    drupal_core_compatibility = Column(String(100), nullable=True)
    is_active = Column(Boolean(), default=True)
    is_deleted = Column(Boolean(), default=False)

    # Audit fields following existing pattern
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"))

    # Composite unique constraint and performance indexes
    __table_args__ = (
        UniqueConstraint("module_id", "version_string", name="uq_module_version"),
        Index("idx_module_version_security", "module_id", "is_security_update"),
        Index("idx_module_version_date", "module_id", "release_date"),
    )

    # Relationships
    module = relationship("Module", back_populates="versions")
    site_modules = relationship(
        "SiteModule",
        back_populates="current_version",
        foreign_keys="SiteModule.current_version_id",
    )
    site_modules_latest = relationship(
        "SiteModule",
        back_populates="latest_version",
        foreign_keys="SiteModule.latest_version_id",
    )
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
