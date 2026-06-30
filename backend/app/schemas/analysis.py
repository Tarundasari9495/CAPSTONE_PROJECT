from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.clause import ClauseResponse
from app.schemas.risk import RiskResponse


class AnalysisReport(BaseModel):
    id: uuid.UUID
    contract_id: uuid.UUID
    summary: dict | None = None
    contract_info: dict | None = None
    risk_score: int | None = None
    clauses: list[ClauseResponse] = []
    risks: list[RiskResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}
