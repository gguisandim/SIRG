"""Cria tabela usuarios manualmente

Revision ID: cria_usuarios_manual
Revises: 307b886d5c55
"""

from alembic import op
import sqlalchemy as sa


revision = "cria_usuarios_manual"
down_revision = "307b886d5c55"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("perfil", sa.String(length=30), nullable=False, server_default="professor"),
        sa.Column("ativo", sa.Boolean(), nullable=True, server_default=sa.text("true")),
        sa.Column("membro_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["membro_id"], ["membro.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )


def downgrade():
    op.drop_table("usuarios")