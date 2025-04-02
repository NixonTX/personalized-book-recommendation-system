"""add_test_table_only

Revision ID: 153ea1d81b86
Revises: ac067491d765
Create Date: 2025-04-02 13:48:19.641139

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '153ea1d81b86'
down_revision: Union[str, None] = 'ac067491d765'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.create_table(
        'test_table',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50)),
        schema='book_schema'
    )

def downgrade():
    op.drop_table('test_table', schema='book_schema')