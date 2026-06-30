"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-29

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "contracts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("file_type", sa.String(10), nullable=False),
        sa.Column("upload_date", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.CheckConstraint("file_type IN ('pdf', 'docx')", name="ck_contracts_file_type"),
        sa.CheckConstraint("status IN ('pending', 'processing', 'completed', 'failed')", name="ck_contracts_status"),
    )
    op.create_index("ix_contracts_user_id", "contracts", ["user_id"])

    op.create_table(
        "contract_analysis",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("summary", postgresql.JSONB(), nullable=True),
        sa.Column("contract_info", postgresql.JSONB(), nullable=True),
        sa.Column("risk_score", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("contract_id", name="uq_contract_analysis_contract_id"),
        sa.CheckConstraint("risk_score BETWEEN 0 AND 100", name="ck_analysis_risk_score"),
    )
    op.create_index("ix_contract_analysis_contract_id", "contract_analysis", ["contract_id"])

    op.create_table(
        "contract_clauses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("clause_type", sa.String(50), nullable=False),
        sa.Column("clause_text", sa.Text(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_contract_clauses_contract_id", "contract_clauses", ["contract_id"])

    op.create_table(
        "contract_risks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("risk_level", sa.String(10), nullable=False),
        sa.Column("risk_description", sa.Text(), nullable=False),
        sa.Column("clause_type", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
        sa.CheckConstraint("risk_level IN ('high', 'medium', 'low')", name="ck_risks_risk_level"),
    )
    op.create_index("ix_contract_risks_contract_id", "contract_risks", ["contract_id"])


def downgrade() -> None:
    op.drop_table("contract_risks")
    op.drop_table("contract_clauses")
    op.drop_table("contract_analysis")
    op.drop_table("contracts")
