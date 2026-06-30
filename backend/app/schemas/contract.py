from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ContractUploadResponse(BaseModel):
    contract_id: uuid.UUID
    file_name: str
    status: str


class ContractRecord(BaseModel):
    id: uuid.UUID
    file_name: str
    file_size: int
    file_type: str
    upload_date: datetime
    status: str
    error_message: str | None = None

    model_config = {"from_attributes": True}


class ContractHistoryItem(BaseModel):
    id: uuid.UUID
    file_name: str
    upload_date: datetime
    status: str
    risk_score: int | None = None

    model_config = {"from_attributes": True}
