from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class ContractAnalysis(Base):
    __tablename__ = "contract_analysis"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    contract_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    summary: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    contract_info: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationship
    contract: Mapped["Contract"] = relationship(  # noqa: F821
        "Contract", back_populates="analysis"
    )

    __table_args__ = (
        UniqueConstraint("contract_id", name="uq_contract_analysis_contract_id"),
        CheckConstraint("risk_score BETWEEN 0 AND 100", name="ck_analysis_risk_score"),
    )
