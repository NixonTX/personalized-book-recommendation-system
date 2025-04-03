"""fix_version_tracking

Revision ID: 344869d49b8b
Revises: 5644f75e467f
Create Date: 2025-04-03 11:12:10.960272

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '344869d49b8b'
down_revision: Union[str, None] = '5644f75e467f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
