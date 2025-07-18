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

    _ = "module_versions"

    _ = Column(Integer, primary_key=True, index=True)
    _ = Column(Integer, ForeignKey("modules.id"), nullable=False, index=True)
    _ = Column(String(50), nullable=False)
    _ = Column(DateTime, nullable=True)
    _ = Column(Boolean, default=False, nullable=False)
    _ = Column(String, nullable=True)  # Text field in database
    _ = Column(String(100), nullable=True)
    _ = Column(Boolean(), default=True)
    _ = Column(Boolean(), default=False)

    # Audit fields following existing pattern
    _ = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    _ = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"))

    # Composite unique constraint and performance indexes
    _ = (
        UniqueConstraint("module_id", "version_string", name="uq_module_version"),
        Index("idx_module_version_security", "module_id", "is_security_update"),
        Index("idx_module_version_date", "module_id", "release_date"),
    )

    # Relationships
    _ = relationship("Module", back_populates="versions")
    _ = relationship(
        "SiteModule",
        back_populates="current_version",
        foreign_keys="SiteModule.current_version_id",
    )
    _ = relationship(
        "SiteModule",
        _="latest_version",
        foreign_keys="SiteModule.latest_version_id",
    )
    _ = relationship("User", foreign_keys=[created_by])
    _ = relationship("User", foreign_keys=[updated_by])
