"""Add new_column to projects

Revision ID: 2d9c8049d34d
Revises: 4cc224f727c8
Create Date: 2025-08-02 22:36:23.167094

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d9c8049d34d'
down_revision: Union[str, Sequence[str], None] = '4cc224f727c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""

    # Convert "Cavity" to INTEGER
    op.execute('ALTER TABLE "Die" ALTER COLUMN "Cavity" TYPE INTEGER USING "Cavity"::integer')

    # Convert "Weight" to FLOAT
    op.execute('ALTER TABLE "Die" ALTER COLUMN "Weight" TYPE DOUBLE PRECISION USING "Weight"::double precision')

    # Convert "Pro_hr_count" to FLOAT
    op.execute('ALTER TABLE "Die" ALTER COLUMN "Pro_hr_count" TYPE DOUBLE PRECISION USING "Pro_hr_count"::double precision')

    # Convert "Price" to INTEGER
    op.execute('ALTER TABLE "Die" ALTER COLUMN "Price" TYPE INTEGER USING "Price"::integer')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column('Die', 'Price',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(),
               existing_nullable=False)
    op.alter_column('Die', 'Pro_hr_count',
               existing_type=sa.Float(),
               type_=sa.VARCHAR(),
               existing_nullable=False)
    op.alter_column('Die', 'Weight',
               existing_type=sa.Float(),
               type_=sa.VARCHAR(),
               existing_nullable=False)
    op.alter_column('Die', 'Cavity',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(),
               existing_nullable=False)
    # ### end Alembic commands ###
