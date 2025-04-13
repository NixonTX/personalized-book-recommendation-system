"""add created_at and last_login to users

Revision ID: 89e347b142e7
Revises: 62d53bb5c1f4
Create Date: 2025-04-10 10:55:08.083224

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89e347b142e7'
down_revision: Union[str, None] = '62d53bb5c1f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.add_column(
        'users',
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        schema='user_schema'
    )
    op.add_column(
        'users',
        sa.Column('last_login', sa.DateTime(timezone=True)),
        schema='user_schema'
    )

def downgrade():
    op.drop_column('users', 'created_at', schema='user_schema')
    op.drop_column('users', 'last_login', schema='user_schema')