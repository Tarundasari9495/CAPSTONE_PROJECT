from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        info={"check": "file_type IN ('pdf', 'docx')"},
    )
    upload_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        info={"check": "status IN ('pending', 'processing', 'completed', 'failed')"},
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    analysis: Mapped["ContractAnalysis | None"] = relationship(  # noqa: F821
        "ContractAnalysis", back_populates="contract", cascade="all, delete-orphan", uselist=False
    )
    clauses: Mapped[list["ContractClause"]] = relationship(  # noqa: F821
        "ContractClause", back_populates="contract", cascade="all, delete-orphan"
    )
    risks: Mapped[list["ContractRisk"]] = relationship(  # noqa: F821
        "ContractRisk", back_populates="contract", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("file_type IN ('pdf', 'docx')", name="ck_contracts_file_type"),
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed')",
            name="ck_contracts_status",
        ),
    )
