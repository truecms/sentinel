"""Rename site_uuid to uuid in sites table

Revision ID: 35c98f38134e
Revises: b2ea20bcef20
Create Date: 2025-07-18 08:00:44.865762

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "35c98f38134e"
down_revision: Union[str, None] = "b2ea20bcef20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename site_uuid column to uuid
    op.alter_column("sites", "site_uuid", new_column_name="uuid")


def downgrade() -> None:
    # Rename uuid column back to site_uuid
    op.alter_column("sites", "uuid", new_column_name="site_uuid")
