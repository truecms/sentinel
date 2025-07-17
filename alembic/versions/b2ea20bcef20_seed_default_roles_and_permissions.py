"""Seed default roles and permissions

Revision ID: b2ea20bcef20
Revises: 4cfcd47c975d
Create Date: 2025-07-17 11:11:08.952496

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b2ea20bcef20"
down_revision: Union[str, None] = "4cfcd47c975d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create metadata and table references
    metadata = sa.MetaData()

    roles_table = sa.Table(
        "roles",
        metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("is_system", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime),
    )

    permissions_table = sa.Table(
        "permissions",
        metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("resource", sa.String(50), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("description", sa.Text),
    )

    role_permissions_table = sa.Table(
        "role_permissions",
        metadata,
        sa.Column("role_id", sa.Integer, nullable=False),
        sa.Column("permission_id", sa.Integer, nullable=False),
        sa.Column("granted_by_id", sa.Integer),
        sa.Column("granted_at", sa.DateTime, server_default=sa.text("NOW()")),
    )

    # Define permissions
    permissions_data = [
        # Organization permissions
        ("organization:read", "organization", "read", "View organization details"),
        ("organization:write", "organization", "write", "Modify organization settings"),
        ("organization:delete", "organization", "delete", "Delete organization"),
        # Site permissions
        ("site:read", "site", "read", "View site information"),
        ("site:write", "site", "write", "Modify site settings"),
        ("site:delete", "site", "delete", "Delete site"),
        ("site:sync", "site", "sync", "Push module data to site"),
        # Module permissions
        ("module:read", "module", "read", "View module information"),
        ("module:write", "module", "write", "Update module data"),
        # User permissions
        ("user:read", "user", "read", "View user profiles"),
        ("user:write", "user", "write", "Modify user accounts"),
        ("user:delete", "user", "delete", "Delete users"),
        ("user:assign_roles", "user", "assign_roles", "Assign roles to users"),
        # Report permissions
        ("report:read", "report", "read", "View reports"),
        ("report:export", "report", "export", "Export report data"),
        # API Key permissions
        ("api_key:read", "api_key", "read", "View API keys"),
        ("api_key:write", "api_key", "write", "Create/modify API keys"),
        ("api_key:delete", "api_key", "delete", "Revoke API keys"),
        # Wildcard permissions
        ("*:*", "*", "*", "All permissions (superuser)"),
        ("organization:*", "organization", "*", "All organization permissions"),
        ("site:*", "site", "*", "All site permissions"),
        ("user:*", "user", "*", "All user permissions"),
        ("module:*", "module", "*", "All module permissions"),
        ("report:*", "report", "*", "All report permissions"),
        ("api_key:*", "api_key", "*", "All API key permissions"),
    ]

    # Define roles
    roles_data = [
        (
            "superadmin",
            "Super Administrator",
            "Full system access with all permissions",
            True,
        ),
        (
            "org_admin",
            "Organization Administrator",
            "Full access within organization scope",
            True,
        ),
        (
            "site_manager",
            "Site Manager",
            "Manage specific sites and their modules",
            True,
        ),
        ("viewer", "Viewer", "Read-only access to organization data", True),
    ]

    # Insert permissions
    conn = op.get_bind()

    for perm_name, resource, action, description in permissions_data:
        conn.execute(
            permissions_table.insert().values(
                name=perm_name,
                resource=resource,
                action=action,
                description=description,
            )
        )

    # Insert roles
    for role_name, display_name, description, is_system in roles_data:
        conn.execute(
            roles_table.insert().values(
                name=role_name,
                display_name=display_name,
                description=description,
                is_system=is_system,
            )
        )

    # Define role-permission mappings
    role_permissions_mapping = {
        "superadmin": ["*:*"],
        "org_admin": [
            "organization:read",
            "organization:write",
            "organization:delete",
            "site:*",
            "user:*",
            "module:*",
            "report:*",
            "api_key:*",
        ],
        "site_manager": [
            "site:read",
            "site:write",
            "site:sync",
            "module:read",
            "module:write",
            "report:read",
            "api_key:read",
        ],
        "viewer": ["organization:read", "site:read", "module:read", "report:read"],
    }

    # Get role and permission IDs
    roles_result = conn.execute(sa.select(roles_table.c.id, roles_table.c.name))
    role_ids = {row.name: row.id for row in roles_result}

    permissions_result = conn.execute(
        sa.select(permissions_table.c.id, permissions_table.c.name)
    )
    permission_ids = {row.name: row.id for row in permissions_result}

    # Insert role-permission mappings
    for role_name, permissions in role_permissions_mapping.items():
        role_id = role_ids.get(role_name)
        if role_id:
            for perm_name in permissions:
                perm_id = permission_ids.get(perm_name)
                if perm_id:
                    conn.execute(
                        role_permissions_table.insert().values(
                            role_id=role_id, permission_id=perm_id
                        )
                    )


def downgrade() -> None:
    # Remove role-permission mappings
    op.execute(
        "DELETE FROM role_permissions WHERE role_id IN (SELECT id FROM roles WHERE is_system = true)"
    )

    # Remove system roles
    op.execute("DELETE FROM roles WHERE is_system = true")

    # Remove all permissions
    op.execute("DELETE FROM permissions")
