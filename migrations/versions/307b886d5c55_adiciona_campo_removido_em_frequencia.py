"""adiciona campo removido em frequencia

Revision ID: 307b886d5c55
Revises: 7178385c47ff
Create Date: 2026-06-02 16:46:28.347828

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '307b886d5c55'
down_revision = '7178385c47ff'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('frequencia', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'removido',
                sa.Boolean(),
                nullable=False,
                server_default=sa.false()
            )
        )


def downgrade():
    with op.batch_alter_table('frequencia', schema=None) as batch_op:
        batch_op.drop_column('removido')