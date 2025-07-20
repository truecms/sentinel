"""add_is_default_to_user_organizations

Revision ID: 439a847c88cc
Revises: f6a561b0cc0e
Create Date: 2025-07-20 02:21:20.542406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '439a847c88cc'
down_revision: Union[str, None] = 'f6a561b0cc0e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_default column to user_organizations table
    op.add_column('user_organizations', sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'))
    
    # Create a partial unique index to ensure only one default organization per user
    op.create_index(
        'uq_user_default_org',
        'user_organizations',
        ['user_id'],
        unique=True,
        postgresql_where=sa.text('is_default = true')
    )
    
    # Set the first organization for each user as default
    op.execute("""
        UPDATE user_organizations
        SET is_default = true
        WHERE (user_id, organization_id) IN (
            SELECT user_id, MIN(organization_id) as organization_id
            FROM user_organizations
            GROUP BY user_id
        )
    """)


def downgrade() -> None:
    # Drop the unique index
    op.drop_index('uq_user_default_org', table_name='user_organizations')
    
    # Remove the is_default column
    op.drop_column('user_organizations', 'is_default')
