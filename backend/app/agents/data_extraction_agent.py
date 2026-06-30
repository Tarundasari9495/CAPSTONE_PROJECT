from __future__ import annotations

import json
import logging
from typing import Any

import litellm

from app.config import get_settings
from app.workflows.state import ContractAnalysisState

logger = logging.getLogger(__name__)
settings = get_settings()

DATA_EXTRACTION_SYSTEM_PROMPT = """You are a legal contract data extraction specialist.
Extract structured metadata from contract text. Return valid JSON only."""

DATA_EXTRACTION_USER_PROMPT = """Extract the following information from this contract:

- title: the contract's official title or name
- effective_date: when the contract takes effect (ISO date string or null)
- expiration_date: when the contract expires (ISO date string or null)
- parties: list of party objects with "name" and "role" fields
- contract_value: monetary value as string (e.g. "$250,000") or null if not stated
- renewal_terms: description of renewal conditions or null

Return ONLY valid JSON:
{{
  "contract_information": {{
    "title": "Software License Agreement",
    "effective_date": "2025-01-01",
    "expiration_date": "2026-12-31",
    "parties": [
      {{"name": "Acme Corp", "role": "Vendor"}},
      {{"name": "BetaCo", "role": "Client"}}
    ],
    "contract_value": "$250,000",
    "renewal_terms": "Auto-renews unless cancelled 30 days prior"
  }}
}}

Contract text:
{document_text}"""


async def data_extraction_node(state: ContractAnalysisState) -> dict[str, Any]:
    document_text = state.get("document_text", "")
    if not document_text:
        return {
            "contract_information": {},
            "agent_errors": state.get("agent_errors", []) + ["data_extraction: empty document text"],
        }

    truncated = document_text[:10000]

    try:
        response = await litellm.acompletion(
            model=settings.litellm_model,
            api_key=settings.litellm_api_key,
            api_base=settings.litellm_base_url,
            messages=[
                {"role": "system", "content": DATA_EXTRACTION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": DATA_EXTRACTION_USER_PROMPT.format(document_text=truncated),
                },
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)
        contract_info = data.get("contract_information", {})

        if not isinstance(contract_info, dict):
            contract_info = {}

        return {"contract_information": contract_info}

    except Exception as exc:
        logger.error("data_extraction_node failed: %s", exc)
        return {
            "contract_information": {},
            "agent_errors": state.get("agent_errors", []) + [f"data_extraction: {exc}"],
        }
