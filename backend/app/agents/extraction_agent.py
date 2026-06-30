from __future__ import annotations

from typing import Any

from app.utils.file_parser import ParseError, parse_docx, parse_pdf
from app.workflows.state import ContractAnalysisState


async def extraction_node(state: ContractAnalysisState) -> dict[str, Any]:
    file_bytes: bytes = state.get("file_bytes", b"")
    file_type: str = state.get("file_type", "pdf")

    try:
        if file_type == "pdf":
            result = parse_pdf(file_bytes)
        else:
            result = parse_docx(file_bytes)
    except ParseError as exc:
        return {
            "document_text": "",
            "page_count": 0,
            "document_metadata": {},
            "agent_errors": state.get("agent_errors", []) + [f"extraction: {exc}"],
        }

    return {
        "document_text": result["document_text"],
        "page_count": result["page_count"] or 0,
        "document_metadata": result["metadata"],
    }
