from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.models.base import Base

class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    url = Column(String, unique=True, nullable=False)
    site_uuid = Column(String(36), nullable=True)
    api_token = Column(String(255), nullable=True)
    drupal_core_version = Column(String(50), nullable=True)
    php_version = Column(String(50), nullable=True)
    database_type = Column(String(50), nullable=True)
    database_version = Column(String(50), nullable=True)
    server_info = Column(JSON, nullable=True)
    last_check = Column(DateTime, nullable=True)
    
    # Site overview tracking fields
    security_score = Column(Integer, nullable=True, default=0)
    total_modules_count = Column(Integer, nullable=True, default=0)
    security_updates_count = Column(Integer, nullable=True, default=0)
    non_security_updates_count = Column(Integer, nullable=True, default=0)
    last_data_push = Column(DateTime, nullable=True)
    last_drupal_org_check = Column(DateTime, nullable=True)
    
    is_active = Column(Boolean(), default=True)
    is_deleted = Column(Boolean(), default=False)
    
    # Ownership and timestamps
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    organization = relationship("Organization", back_populates="sites")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    modules = relationship("SiteModule", back_populates="site", cascade="all, delete-orphan")
