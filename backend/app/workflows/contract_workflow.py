from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.agents.clause_agent import clause_node
from app.agents.data_extraction_agent import data_extraction_node
from app.agents.extraction_agent import extraction_node
from app.agents.report_agent import report_node
from app.agents.risk_agent import risk_node
from app.agents.summary_agent import summary_node
from app.workflows.state import ContractAnalysisState


def _should_continue(state: ContractAnalysisState) -> str:
    """Skip parallel agents if extraction failed (no document text)."""
    if not state.get("document_text"):
        return "report"
    return "parallel"


# ─────────────────────────────────────────────────────────────
# Build the graph
# ─────────────────────────────────────────────────────────────
builder = StateGraph(ContractAnalysisState)

# Nodes
builder.add_node("extraction", extraction_node)
builder.add_node("clause", clause_node)
builder.add_node("risk", risk_node)
builder.add_node("data_extraction", data_extraction_node)
builder.add_node("summary_gen", summary_node)
builder.add_node("report", report_node)

# Edges
builder.add_edge(START, "extraction")

# Conditional: if no document text after extraction, skip to report
builder.add_conditional_edges(
    "extraction",
    _should_continue,
    {
        "parallel": "clause",
        "report": "report",
    },
)
# Fan-out to parallel agents (clause already connected via conditional)
builder.add_edge("extraction", "risk")
builder.add_edge("extraction", "data_extraction")
builder.add_edge("extraction", "summary_gen")

# Fan-in: all parallel agents → report
builder.add_edge("clause", "report")
builder.add_edge("risk", "report")
builder.add_edge("data_extraction", "report")
builder.add_edge("summary_gen", "report")

builder.add_edge("report", END)

# Compile once at module level
contract_graph = builder.compile()
