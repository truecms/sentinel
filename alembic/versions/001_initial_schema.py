"""Initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-06-30 23:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create tables without circular foreign keys first
    
    # Organizations table
    op.create_table('organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'], unique=False)
    
    # Users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    
    # User organizations junction table
    op.create_table('user_organizations',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('user_id', 'organization_id')
    )
    
    # Modules table
    op.create_table('modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('machine_name', sa.String(length=255), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('drupal_org_link', sa.String(length=500), nullable=True),
        sa.Column('module_type', sa.String(length=50), nullable=False),
        sa.Column('is_covered', sa.Boolean(), nullable=True, default=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('machine_name')
    )
    op.create_index(op.f('ix_modules_id'), 'modules', ['id'], unique=False)
    op.create_index(op.f('ix_modules_machine_name'), 'modules', ['machine_name'], unique=True)
    
    # Sites table
    op.create_table('sites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('site_uuid', sa.String(length=36), nullable=True),
        sa.Column('api_token', sa.String(length=255), nullable=True),
        sa.Column('drupal_core_version', sa.String(length=50), nullable=True),
        sa.Column('php_version', sa.String(length=50), nullable=True),
        sa.Column('database_type', sa.String(length=50), nullable=True),
        sa.Column('database_version', sa.String(length=50), nullable=True),
        sa.Column('server_info', sa.JSON(), nullable=True),
        sa.Column('last_check', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url'),
        sa.UniqueConstraint('site_uuid')
    )
    op.create_index(op.f('ix_sites_id'), 'sites', ['id'], unique=False)
    op.create_index(op.f('ix_sites_name'), 'sites', ['name'], unique=False)
    
    # Module versions table
    op.create_table('module_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('version_string', sa.String(length=50), nullable=False),
        sa.Column('release_date', sa.DateTime(), nullable=True),
        sa.Column('is_security_update', sa.Boolean(), nullable=True, default=False),
        sa.Column('release_notes', sa.Text(), nullable=True),
        sa.Column('drupal_core_compatibility', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('module_id', 'version_string', name='uq_module_version')
    )
    op.create_index('idx_module_version_date', 'module_versions', ['module_id', 'release_date'], unique=False)
    op.create_index('idx_module_version_security', 'module_versions', ['module_id', 'is_security_update'], unique=False)
    op.create_index(op.f('ix_module_versions_id'), 'module_versions', ['id'], unique=False)
    op.create_index(op.f('ix_module_versions_module_id'), 'module_versions', ['module_id'], unique=False)
    
    # Site modules table
    op.create_table('site_modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('site_id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('current_version_id', sa.Integer(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('update_available', sa.Boolean(), nullable=False, default=False),
        sa.Column('security_update_available', sa.Boolean(), nullable=False, default=False),
        sa.Column('latest_version_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True, default=False),
        sa.Column('first_seen', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_seen', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('site_id', 'module_id', name='uq_site_module')
    )
    op.create_index('idx_site_module_updates', 'site_modules', ['site_id', 'update_available', 'security_update_available'], unique=False)
    op.create_index(op.f('ix_site_modules_id'), 'site_modules', ['id'], unique=False)
    op.create_index(op.f('ix_site_modules_module_id'), 'site_modules', ['module_id'], unique=False)
    op.create_index(op.f('ix_site_modules_site_id'), 'site_modules', ['site_id'], unique=False)
    
    # Now add all the foreign key constraints
    op.create_foreign_key(None, 'organizations', 'users', ['created_by'], ['id'])
    op.create_foreign_key(None, 'organizations', 'users', ['updated_by'], ['id'])
    
    op.create_foreign_key(None, 'users', 'organizations', ['organization_id'], ['id'])
    
    op.create_foreign_key(None, 'user_organizations', 'users', ['user_id'], ['id'])
    op.create_foreign_key(None, 'user_organizations', 'organizations', ['organization_id'], ['id'])
    
    op.create_foreign_key(None, 'modules', 'users', ['created_by'], ['id'])
    op.create_foreign_key(None, 'modules', 'users', ['updated_by'], ['id'])
    
    op.create_foreign_key(None, 'sites', 'organizations', ['organization_id'], ['id'])
    op.create_foreign_key(None, 'sites', 'users', ['created_by'], ['id'])
    op.create_foreign_key(None, 'sites', 'users', ['updated_by'], ['id'])
    
    op.create_foreign_key(None, 'module_versions', 'modules', ['module_id'], ['id'])
    op.create_foreign_key(None, 'module_versions', 'users', ['created_by'], ['id'])
    op.create_foreign_key(None, 'module_versions', 'users', ['updated_by'], ['id'])
    
    op.create_foreign_key(None, 'site_modules', 'sites', ['site_id'], ['id'])
    op.create_foreign_key(None, 'site_modules', 'modules', ['module_id'], ['id'])
    op.create_foreign_key(None, 'site_modules', 'module_versions', ['current_version_id'], ['id'])
    op.create_foreign_key(None, 'site_modules', 'module_versions', ['latest_version_id'], ['id'])
    op.create_foreign_key(None, 'site_modules', 'users', ['created_by'], ['id'])
    op.create_foreign_key(None, 'site_modules', 'users', ['updated_by'], ['id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('site_modules')
    op.drop_table('module_versions')
    op.drop_table('sites')
    op.drop_table('modules')
    op.drop_table('user_organizations')
    op.drop_table('users')
    op.drop_table('organizations')