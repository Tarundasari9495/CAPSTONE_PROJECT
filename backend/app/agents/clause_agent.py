from __future__ import annotations

import json
import logging
from typing import Any

import litellm

from app.config import get_settings
from app.workflows.state import ContractAnalysisState

logger = logging.getLogger(__name__)
settings = get_settings()

CLAUSE_TYPES = [
    "termination",
    "liability",
    "confidentiality",
    "indemnification",
    "payment_terms",
    "renewal",
    "governing_law",
    "intellectual_property",
    "non_compete",
    "force_majeure",
]

CLAUSE_SYSTEM_PROMPT = """You are a legal contract analysis expert.
Your task is to identify specific clause types in a contract document.
Return your response as valid JSON only — no explanation, no markdown code blocks."""

CLAUSE_USER_PROMPT = """Analyze the following contract text and identify all clauses.

For each clause type found, return:
- clause_type: one of {clause_types}
- clause_text: the exact or summarized text of the clause (max 500 chars)
- page_number: page number if determinable, otherwise null

If a clause type is not present, do NOT include it.

Return ONLY valid JSON in this exact format:
{{
  "clauses": [
    {{"clause_type": "termination", "clause_text": "...", "page_number": null}}
  ]
}}

Contract text:
{document_text}"""


async def clause_node(state: ContractAnalysisState) -> dict[str, Any]:
    document_text = state.get("document_text", "")
    if not document_text:
        return {
            "clauses": [],
            "agent_errors": state.get("agent_errors", []) + ["clause: empty document text"],
        }

    # Truncate to ~12000 chars to stay within context limits
    truncated = document_text[:12000]

    try:
        response = await litellm.acompletion(
            model=settings.litellm_model,
            api_key=settings.litellm_api_key,
            api_base=settings.litellm_base_url,
            messages=[
                {"role": "system", "content": CLAUSE_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": CLAUSE_USER_PROMPT.format(
                        clause_types=", ".join(CLAUSE_TYPES),
                        document_text=truncated,
                    ),
                },
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)
        clauses = data.get("clauses", [])

        # Validate structure
        validated: list[dict] = []
        for clause in clauses:
            if isinstance(clause, dict) and "clause_type" in clause and "clause_text" in clause:
                validated.append(
                    {
                        "clause_type": str(clause["clause_type"]).lower(),
                        "clause_text": str(clause["clause_text"])[:1000],
                        "page_number": clause.get("page_number"),
                    }
                )

        return {"clauses": validated}

    except Exception as exc:
        logger.error("clause_node failed: %s", exc)
        return {
            "clauses": [],
            "agent_errors": state.get("agent_errors", []) + [f"clause: {exc}"],
        }
