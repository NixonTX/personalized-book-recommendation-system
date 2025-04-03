"""create_reviews_table

Revision ID: 5644f75e467f
Revises: 374c72601bbf
Create Date: 2025-04-03 10:59:28.207173

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '5644f75e467f'
down_revision: Union[str, None] = '374c72601bbf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the review_status enum type first
    review_status = postgresql.ENUM(
        'pending', 'approved', 'rejected',
        name='review_status'
    )
    review_status.create(op.get_bind())

    # Create the reviews table
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('book_isbn', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_edited', sa.Boolean(), server_default=sa.text('false')),
        sa.Column('status', review_status, server_default='pending'),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['user_schema.users.id'],
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['book_isbn'],
            ['book_schema.books.isbn'],
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'book_isbn', name='unique_user_review'),
        schema='user_schema'
    )

    # Create index for better query performance
    op.create_index(
        'idx_reviews_book_isbn_status',
        'reviews',
        ['book_isbn', 'status'],
        schema='user_schema'
    )


def downgrade() -> None:
    # Drop the table first
    op.drop_table('reviews', schema='user_schema')
    
    # Drop the index
    op.drop_index('idx_reviews_book_isbn_status', schema='user_schema')
    
    # Drop the enum type
    review_status = postgresql.ENUM(
        'pending', 'approved', 'rejected',
        name='review_status'
    )
    review_status.drop(op.get_bind())