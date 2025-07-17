"""Add site overview tracking fields

Revision ID: dc0a14d7a7da
Revises: 99d323ff6009
Create Date: 2025-07-17 12:57:33.839891

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dc0a14d7a7da"
down_revision: Union[str, None] = "99d323ff6009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new fields for site overview functionality
    op.add_column(
        "sites", sa.Column("security_score", sa.Integer(), nullable=True, default=0)
    )
    op.add_column(
        "sites",
        sa.Column("total_modules_count", sa.Integer(), nullable=True, default=0),
    )
    op.add_column(
        "sites",
        sa.Column("security_updates_count", sa.Integer(), nullable=True, default=0),
    )
    op.add_column(
        "sites",
        sa.Column("non_security_updates_count", sa.Integer(), nullable=True, default=0),
    )
    op.add_column("sites", sa.Column("last_data_push", sa.DateTime(), nullable=True))
    op.add_column(
        "sites", sa.Column("last_drupal_org_check", sa.DateTime(), nullable=True)
    )

    # Create indexes for performance
    op.create_index("ix_sites_security_score", "sites", ["security_score"])
    op.create_index("ix_sites_last_data_push", "sites", ["last_data_push"])
    op.create_index(
        "ix_sites_last_drupal_org_check", "sites", ["last_drupal_org_check"]
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_sites_last_drupal_org_check", "sites")
    op.drop_index("ix_sites_last_data_push", "sites")
    op.drop_index("ix_sites_security_score", "sites")

    # Drop columns
    op.drop_column("sites", "last_drupal_org_check")
    op.drop_column("sites", "last_data_push")
    op.drop_column("sites", "non_security_updates_count")
    op.drop_column("sites", "security_updates_count")
    op.drop_column("sites", "total_modules_count")
    op.drop_column("sites", "security_score")
