"""create search_history table

Revision ID: 62d53bb5c1f4
Revises: a6864c9618e5
Create Date: 2025-04-09 15:20:06.980677

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '62d53bb5c1f4'
down_revision: Union[str, None] = 'a6864c9618e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'search_history',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.Column('query', sa.String(200), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        schema='user_schema'
    )
    op.create_index('ix_search_history_user_id', 'search_history', ['user_id'], schema='user_schema')
    op.create_index('ix_search_history_created_at', 'search_history', ['created_at'], schema='user_schema')

def downgrade():
    op.drop_table('search_history', schema='user_schema')