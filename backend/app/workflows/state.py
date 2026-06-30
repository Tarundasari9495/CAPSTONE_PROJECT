from __future__ import annotations

from typing import Annotated, Any, Optional
from typing_extensions import TypedDict
import operator


def _merge_lists(a: list, b: list) -> list:
    """Merge lists from parallel branches."""
    return (a or []) + (b or [])


def _merge_dicts(a: dict, b: dict) -> dict:
    """Last-writer wins for dicts from parallel branches."""
    result = dict(a or {})
    result.update(b or {})
    return result


class ContractAnalysisState(TypedDict, total=False):
    # Input
    contract_id: str
    file_bytes: bytes
    file_type: str

    # Extraction output
    document_text: str
    page_count: int
    document_metadata: dict

    # Parallel agent outputs — use Annotated reducers for merge
    clauses: Annotated[list[dict], _merge_lists]
    risks: Annotated[list[dict], _merge_lists]
    contract_information: Annotated[dict, _merge_dicts]
    summary: Annotated[dict, _merge_dicts]
    risk_score: int

    # Final
    final_report: dict

    # Error collection — accumulate across all agents
    agent_errors: Annotated[list[str], operator.add]
