"""move_version_table_to_public

Revision ID: 374c72601bbf
Revises: 5b086807bdb7
Create Date: 2025-04-02 15:38:21.510162

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '374c72601bbf'
down_revision: Union[str, None] = '5b086807bdb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
