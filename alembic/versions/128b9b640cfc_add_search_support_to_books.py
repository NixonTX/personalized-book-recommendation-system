"""add_search_support_to_books

Revision ID: 128b9b640cfc
Revises: 344869d49b8b
Create Date: 2025-04-05 09:23:54.008201

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TSVECTOR


# revision identifiers, used by Alembic.
revision: str = '128b9b640cfc'
down_revision: Union[str, None] = '344869d49b8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add new columns
    op.add_column('books', sa.Column('genre', sa.String(30)), schema='book_schema')
    op.add_column('books', sa.Column('page_count', sa.Integer), schema='book_schema')
    op.add_column('books', sa.Column('average_rating', sa.Float), schema='book_schema')

    # Create search optimization indexes
    op.create_index(op.f('ix_book_title'), 'books', ['title'], schema='book_schema')
    op.create_index(op.f('ix_book_author'), 'books', ['author'], schema='book_schema')

    # Add generated tsvector column for full-text search
    op.execute("""
        ALTER TABLE book_schema.books 
        ADD COLUMN search_vector tsvector
        GENERATED ALWAYS AS (
            setweight(to_tsvector('english', title), 'A') ||
            setweight(to_tsvector('english', author), 'B') ||
            setweight(to_tsvector('english', coalesce(genre, '')), 'C')
        ) STORED
    """)

    # Create GIN index on the search_vector
    op.create_index('ix_book_search_vector', 'books', ['search_vector'], postgresql_using='gin', schema='book_schema')


def downgrade():
    op.drop_index('ix_book_search_vector', table_name='books', schema='book_schema')
    op.execute("ALTER TABLE book_schema.books DROP COLUMN search_vector")
    op.drop_column('books', 'average_rating', schema='book_schema')
    op.drop_column('books', 'page_count', schema='book_schema')
    op.drop_column('books', 'genre', schema='book_schema')