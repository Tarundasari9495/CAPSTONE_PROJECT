from __future__ import annotations

from typing import Any

from app.workflows.state import ContractAnalysisState


async def report_node(state: ContractAnalysisState) -> dict[str, Any]:
    final_report = {
        "summary": state.get("summary", {}),
        "clauses": state.get("clauses", []),
        "risks": state.get("risks", []),
        "contract_information": state.get("contract_information", {}),
        "risk_score": state.get("risk_score", 0),
        "agent_errors": state.get("agent_errors", []),
    }

    return {"final_report": final_report}
