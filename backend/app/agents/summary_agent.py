from __future__ import annotations

import json
import logging
from typing import Any

import litellm

from app.config import get_settings
from app.workflows.state import ContractAnalysisState

logger = logging.getLogger(__name__)
settings = get_settings()

SUMMARY_SYSTEM_PROMPT = """You are a senior legal analyst.
Generate a structured contract summary. Return valid JSON only."""

SUMMARY_USER_PROMPT = """Generate a comprehensive summary of this contract.

Return ONLY valid JSON:
{{
  "summary": {{
    "executive_summary": "2-3 paragraph plain-English summary of the contract...",
    "key_terms": "Summary of key terms and definitions...",
    "important_obligations": [
      "Party A must deliver software within 30 days",
      "Party B must pay net-30 from invoice"
    ],
    "important_dates": [
      "Effective: January 1, 2025",
      "Expiration: December 31, 2026",
      "Renewal notice deadline: December 1, 2026"
    ]
  }}
}}

Contract text:
{document_text}"""


async def summary_node(state: ContractAnalysisState) -> dict[str, Any]:
    document_text = state.get("document_text", "")
    if not document_text:
        return {
            "summary": {},
            "agent_errors": state.get("agent_errors", []) + ["summary: empty document text"],
        }

    truncated = document_text[:12000]

    try:
        response = await litellm.acompletion(
            model=settings.litellm_model,
            api_key=settings.litellm_api_key,
            api_base=settings.litellm_base_url,
            messages=[
                {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": SUMMARY_USER_PROMPT.format(document_text=truncated),
                },
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)
        summary = data.get("summary", {})

        if not isinstance(summary, dict):
            summary = {}

        return {"summary": summary}

    except Exception as exc:
        logger.error("summary_node failed: %s", exc)
        return {
            "summary": {},
            "agent_errors": state.get("agent_errors", []) + [f"summary: {exc}"],
        }
