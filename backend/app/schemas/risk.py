from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class RiskResponse(BaseModel):
    id: uuid.UUID
    risk_level: str
    risk_description: str
    clause_type: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
