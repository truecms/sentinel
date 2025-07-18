from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class SiteModule(Base):
    """
    SiteModule model for tracking module installations on specific sites.

    Junction table that links sites to modules and tracks which version
    is currently installed, whether updates are available, and installation status.
    """

    _ = "site_modules"

    _ = Column(Integer, primary_key=True, index=True)
    _ = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)
    _ = Column(Integer, ForeignKey("modules.id"), nullable=False, index=True)
    current_version_id = Column(
        Integer, ForeignKey("module_versions.id"), nullable=False
    )

    # Status fields
    _ = Column(Boolean, default=True, nullable=False)
    _ = Column(Boolean, default=False, nullable=False)
    _ = Column(Boolean, default=False, nullable=False)
    latest_version_id = Column(Integer, ForeignKey("module_versions.id"), nullable=True)
    _ = Column(Boolean(), default=True)
    _ = Column(Boolean(), default=False)

    # Tracking fields
    _ = Column(DateTime, nullable=False, server_default=text("now()"))
    _ = Column(DateTime, nullable=False, server_default=text("now()"))
    _ = Column(DateTime, nullable=True)  # When version actually changed

    # Audit fields following existing pattern
    _ = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    _ = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"))

    # Composite unique constraint and performance indexes
    _ = (
        UniqueConstraint("site_id", "module_id", name="uq_site_module"),
        Index(
            "idx_site_module_updates",
            "site_id",
            "update_available",
            "security_update_available",
        ),
    )

    # Relationships
    _ = relationship("Site", back_populates="modules")
    _ = relationship("Module", back_populates="site_modules")
    _ = relationship(
        "ModuleVersion",
        foreign_keys=[current_version_id],
        back_populates="site_modules",
    )
    _ = relationship(
        "ModuleVersion",
        foreign_keys=[latest_version_id],
        _="site_modules_latest",
    )
    _ = relationship("User", foreign_keys=[created_by])
    _ = relationship("User", foreign_keys=[updated_by])
