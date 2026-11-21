"""enable vector extension

Revision ID: f25b99ccc7ae
Revises: 1fe37bc1e699
Create Date: 2026-11-07 13:45:27.867639

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'f25b99ccc7ae'
down_revision: Union[str, Sequence[str], None] = '1fe37bc1e699'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "CREATE EXTENSION IF NOT EXISTS vector"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        "DROP EXTENSION IF EXISTS vector"
    )