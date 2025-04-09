"""add filter indexes for search

Revision ID: a6864c9618e5
Revises: 6b04187412bc
Create Date: 2025-04-08 20:05:49.986391

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a6864c9618e5'
down_revision: Union[str, None] = '6b04187412bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_index('ix_book_genre', 'books', ['genre'], schema='book_schema')
    op.create_index('ix_book_rating', 'books', ['average_rating'], schema='book_schema')
    op.create_index('ix_book_page_count', 'books', ['page_count'], schema='book_schema')
    op.execute("""
        CREATE EXTENSION IF NOT EXISTS pg_trgm;
        CREATE INDEX ix_book_author_ft ON book_schema.books 
        USING gin (author gin_trgm_ops);
    """)

def downgrade():
    op.drop_index('ix_book_genre', table_name='books', schema='book_schema')
    op.drop_index('ix_book_rating', table_name='books', schema='book_schema')
    op.drop_index('ix_book_page_count', table_name='books', schema='book_schema')
    op.drop_index('ix_book_author_ft', table_name='books', schema='book_schema')