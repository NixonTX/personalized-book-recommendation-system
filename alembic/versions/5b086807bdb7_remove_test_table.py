"""remove_test_table

Revision ID: 5b086807bdb7
Revises: 153ea1d81b86
Create Date: 2025-04-02 14:02:37.396778

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b086807bdb7'
down_revision: Union[str, None] = '153ea1d81b86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_table('test_table', schema='book_schema')

def downgrade():
    op.create_table(
        'test_table',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50)),
        schema='book_schema'
    )