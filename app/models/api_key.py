"""API Key model for authentication."""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ApiKey(Base):
    """API Key model for user and site authentication."""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(String(255), nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=True, index=True)
    name = Column(String(100), nullable=True)
    last_used = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="api_keys")
    site = relationship("Site", back_populates="api_keys")

    @classmethod
    def generate_key(cls, prefix: str = "sk_") -> str:
        """Generate a new API key."""
        # Generate 32 random bytes and encode as hex
        random_bytes = secrets.token_bytes(32)
        key_suffix = random_bytes.hex()
        return f"{prefix}{key_suffix}"

    @classmethod
    def hash_key(cls, key: str) -> str:
        """Hash an API key for secure storage."""
        return hashlib.sha256(key.encode()).hexdigest()

    def verify_key(self, key: str) -> bool:
        """Verify if the provided key matches this API key."""
        return self.key_hash == self.hash_key(key)

    def is_expired(self) -> bool:
        """Check if the API key has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if the API key is valid (active and not expired)."""
        return self.is_active and not self.is_expired()

    def update_last_used(self) -> None:
        """Update the last used timestamp."""
        self.last_used = datetime.utcnow()

    @classmethod
    def create_for_user(
        cls,
        user_id: int,
        name: Optional[str] = None,
        expires_in_days: Optional[int] = 365
    ) -> tuple["ApiKey", str]:
        """Create a new API key for a user."""
        raw_key = cls.generate_key("sk_user_")
        key_hash = cls.hash_key(raw_key)
        
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        api_key = cls(
            key_hash=key_hash,
            user_id=user_id,
            name=name,
            expires_at=expires_at
        )
        
        return api_key, raw_key

    @classmethod
    def create_for_site(
        cls,
        site_id: int,
        name: Optional[str] = None,
        expires_in_days: Optional[int] = None
    ) -> tuple["ApiKey", str]:
        """Create a new API key for a site."""
        raw_key = cls.generate_key("sk_site_")
        key_hash = cls.hash_key(raw_key)
        
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        api_key = cls(
            key_hash=key_hash,
            site_id=site_id,
            name=name,
            expires_at=expires_at
        )
        
        return api_key, raw_key

    def __repr__(self) -> str:
        """String representation of the API key."""
        return f"<ApiKey {self.id} for {'user' if self.user_id else 'site'}>"