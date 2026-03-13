"""update users

Revision ID: c1f71aaa4d83
Revises: c049b14919c8
Create Date: 2026-03-12 12:54:35.443016

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1f71aaa4d83'
down_revision: Union[str, Sequence[str], None] = 'c049b14919c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('Nickname', sa.String(length=50), nullable=False, server_default='0'))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'Nickname')
    pass
