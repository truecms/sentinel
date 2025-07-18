"""add_version_updated_at_to_site_modules

Revision ID: f6a561b0cc0e
Revises: 35c98f38134e
Create Date: 2025-07-18 08:20:52.840996

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f6a561b0cc0e"
down_revision: Union[str, None] = "35c98f38134e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add version_updated_at column to site_modules table
    op.add_column(
        "site_modules", sa.Column("version_updated_at", sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    # Remove version_updated_at column from site_modules table
    op.drop_column("site_modules", "version_updated_at")
