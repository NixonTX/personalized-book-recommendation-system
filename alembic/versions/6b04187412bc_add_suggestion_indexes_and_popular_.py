"""add suggestion indexes and popular_books view

Revision ID: 6b04187412bc
Revises: 128b9b640cfc
Create Date: 2025-04-08 16:46:03.424064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b04187412bc'
down_revision: Union[str, None] = '128b9b640cfc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        CREATE INDEX idx_book_title_prefix ON book_schema.books 
        (title text_pattern_ops);
    """)
    op.execute("""
        CREATE INDEX idx_book_author_prefix ON book_schema.books 
        (author text_pattern_ops);
    """)
    op.execute("""
        CREATE MATERIALIZED VIEW book_schema.popular_books AS
        SELECT b.isbn, b.title, b.author, 
               AVG(r.rating) as avg_rating,
               COUNT(r.id) as rating_count
        FROM book_schema.books b
        LEFT JOIN user_schema.ratings r ON b.isbn = r.book_isbn
        GROUP BY b.isbn
        ORDER BY rating_count DESC, avg_rating DESC
        LIMIT 100;
    """)
    op.execute("""
        CREATE UNIQUE INDEX idx_popular_books_isbn 
        ON book_schema.popular_books (isbn);
    """)

def downgrade():
    op.drop_index('idx_book_title_prefix', table_name='books', schema='book_schema')
    op.drop_index('idx_book_author_prefix', table_name='books', schema='book_schema')
    op.execute("DROP MATERIALIZED VIEW IF EXISTS book_schema.popular_books")