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

    __tablename__ = "site_modules"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False, index=True)
    current_version_id = Column(
        Integer, ForeignKey("module_versions.id"), nullable=False
    )

    # Status fields
    enabled = Column(Boolean, default=True, nullable=False)
    update_available = Column(Boolean, default=False, nullable=False)
    security_update_available = Column(Boolean, default=False, nullable=False)
    latest_version_id = Column(Integer, ForeignKey("module_versions.id"), nullable=True)
    is_active = Column(Boolean(), default=True)
    is_deleted = Column(Boolean(), default=False)

    # Tracking fields
    first_seen = Column(DateTime, nullable=False, server_default=text("now()"))
    last_seen = Column(DateTime, nullable=False, server_default=text("now()"))
    last_updated = Column(DateTime, nullable=True)  # When version actually changed

    # Audit fields following existing pattern
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"))

    # Composite unique constraint and performance indexes
    __table_args__ = (
        UniqueConstraint("site_id", "module_id", name="uq_site_module"),
        Index(
            "idx_site_module_updates",
            "site_id",
            "update_available",
            "security_update_available",
        ),
    )

    # Relationships
    site = relationship("Site", back_populates="modules")
    module = relationship("Module", back_populates="site_modules")
    current_version = relationship(
        "ModuleVersion",
        foreign_keys=[current_version_id],
        back_populates="site_modules",
    )
    latest_version = relationship(
        "ModuleVersion",
        foreign_keys=[latest_version_id],
        back_populates="site_modules_latest",
    )
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
