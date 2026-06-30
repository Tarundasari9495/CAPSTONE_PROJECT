from __future__ import annotations

import uuid

from pydantic import BaseModel


class ClauseResponse(BaseModel):
    id: uuid.UUID
    clause_type: str
    clause_text: str
    page_number: int | None = None

    model_config = {"from_attributes": True}
