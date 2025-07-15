"""add_full_name_to_users

Revision ID: 99d323ff6009
Revises: 001_initial_schema
Create Date: 2025-07-15 11:36:11.999782

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99d323ff6009'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add full_name column to users table
    op.add_column('users', sa.Column('full_name', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove full_name column from users table
    op.drop_column('users', 'full_name')
