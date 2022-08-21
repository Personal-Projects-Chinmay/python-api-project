"""Set username and short description to not nullable

Revision ID: 554cdbd4e33a
Revises: 070832455d09
Create Date: 2022-07-27 23:29:38.718310

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "554cdbd4e33a"
down_revision = "070832455d09"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("user", "username", nullable=False)
    op.alter_column("user", "short_description", nullable=False)
    op.add_column("user", sa.Column("test", sa.String()))


def downgrade() -> None:
    op.drop_column("user", "test")
    op.alter_column("user", "username", nullable=True)
    op.alter_column("user", "short_description", nullable=True)
