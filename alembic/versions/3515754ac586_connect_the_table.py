"""connect the table 

Revision ID: 3515754ac586
Revises: dd8461859883
Create Date: 2025-10-19 20:28:28.577036

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3515754ac586'
down_revision: Union[str, Sequence[str], None] = 'dd8461859883'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add 'tea' column with a temporary default to avoid NOT NULL violation
    op.add_column(
        'income',
        sa.Column('tea', sa.String(), nullable=False, server_default='')
    )

    # Add 'water' column with a temporary default to avoid NOT NULL violation
    op.add_column(
        'income',
        sa.Column('water', sa.String(), nullable=False, server_default='')
    )

    # Remove the default after creation (optional, but keeps schema clean)
    op.alter_column('income', 'tea', server_default=None)
    op.alter_column('income', 'water', server_default=None)

    # Drop old column
    op.drop_column('income', 'extra')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('income', sa.Column('extra', sa.VARCHAR(), nullable=False))
    op.drop_column('income', 'water')
    op.drop_column('income', 'tea')
