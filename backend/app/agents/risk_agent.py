from __future__ import annotations

import json
import logging
from typing import Any

import litellm

from app.config import get_settings
from app.workflows.state import ContractAnalysisState

logger = logging.getLogger(__name__)
settings = get_settings()

RISK_SYSTEM_PROMPT = """You are a legal risk assessment expert.
Analyze contract clauses and identify risks. Return valid JSON only."""

RISK_USER_PROMPT = """Analyze the following contract clauses and identify risks.

For each risk:
- risk_level: "high", "medium", or "low"
- risk_description: clear explanation of the risk (max 300 chars)
- clause_type: the clause type this risk relates to (or null for missing clauses)

Also identify missing critical clauses from this list: {missing_clause_types}
Treat each missing critical clause as a "medium" risk.

Finally, compute overall_risk_score (0-100):
- High risks contribute 20 points each (max 60)
- Medium risks contribute 10 points each (max 30)
- Low risks contribute 2 points each (max 10)
- Cap at 100

Return ONLY valid JSON:
{{
  "risks": [
    {{"risk_level": "high", "risk_description": "...", "clause_type": "indemnification"}}
  ],
  "overall_risk_score": 67
}}

Identified clauses:
{clauses_text}"""


async def risk_node(state: ContractAnalysisState) -> dict[str, Any]:
    clauses = state.get("clauses", [])

    CRITICAL_CLAUSE_TYPES = {
        "termination", "liability", "confidentiality",
        "indemnification", "payment_terms", "governing_law",
    }
    found_types = {c["clause_type"] for c in clauses}
    missing = CRITICAL_CLAUSE_TYPES - found_types

    clauses_text = json.dumps(clauses, indent=2) if clauses else "No clauses identified."

    try:
        response = await litellm.acompletion(
            model=settings.litellm_model,
            api_key=settings.litellm_api_key,
            api_base=settings.litellm_base_url,
            messages=[
                {"role": "system", "content": RISK_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": RISK_USER_PROMPT.format(
                        missing_clause_types=", ".join(missing) if missing else "none",
                        clauses_text=clauses_text,
                    ),
                },
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)
        risks = data.get("risks", [])
        score = int(data.get("overall_risk_score", 0))
        score = max(0, min(100, score))

        validated: list[dict] = []
        for risk in risks:
            if isinstance(risk, dict) and "risk_level" in risk and "risk_description" in risk:
                level = str(risk["risk_level"]).lower()
                if level not in ("high", "medium", "low"):
                    level = "low"
                validated.append(
                    {
                        "risk_level": level,
                        "risk_description": str(risk["risk_description"])[:500],
                        "clause_type": risk.get("clause_type"),
                    }
                )

        return {"risks": validated, "risk_score": score}

    except Exception as exc:
        logger.error("risk_node failed: %s", exc)
        return {
            "risks": [],
            "risk_score": 0,
            "agent_errors": state.get("agent_errors", []) + [f"risk: {exc}"],
        }
