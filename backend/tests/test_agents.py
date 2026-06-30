from __future__ import annotations

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch

from app.workflows.state import ContractAnalysisState

# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────

SAMPLE_CONTRACT_TEXT = """
SOFTWARE LICENSE AGREEMENT

This Software License Agreement ("Agreement") is entered into as of January 1, 2025,
by and between Acme Corp ("Vendor") and BetaCo ("Client").

1. TERMINATION
Either party may terminate this Agreement with 30 days written notice.
Upon termination, all licenses granted herein shall immediately cease.

2. LIABILITY
In no event shall Vendor be liable for indirect, incidental, or consequential damages.
Total liability shall not exceed fees paid in the prior twelve (12) months.

3. CONFIDENTIALITY
Each party agrees to hold the other's Confidential Information in strict confidence.
This obligation survives termination for a period of five (5) years.

4. INDEMNIFICATION
Client shall indemnify, defend, and hold harmless Vendor from any third-party claims
arising from Client's use of the software.

5. PAYMENT TERMS
Client shall pay all invoices within thirty (30) days of the invoice date.

6. GOVERNING LAW
This Agreement shall be governed by the laws of the State of Delaware.

7. INTELLECTUAL PROPERTY
All intellectual property rights in the software shall remain with Vendor.

8. FORCE MAJEURE
Neither party shall be liable for delays caused by circumstances beyond their control.

Effective Date: January 1, 2025
Expiration Date: December 31, 2026
Contract Value: $250,000
"""


@pytest.fixture
def base_state() -> ContractAnalysisState:
    return ContractAnalysisState(
        contract_id="test-contract-id",
        file_bytes=b"",
        file_type="pdf",
        document_text=SAMPLE_CONTRACT_TEXT,
        page_count=5,
        document_metadata={"author": "Test Author", "title": "Test Contract"},
        clauses=[],
        risks=[],
        contract_information={},
        summary={},
        agent_errors=[],
    )


# ─────────────────────────────────────────────────────────────
# Extraction Agent Tests
# ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_extraction_agent_pdf_success():
    from app.agents.extraction_agent import extraction_node

    with patch("app.agents.extraction_agent.parse_pdf") as mock_parse:
        mock_parse.return_value = {
            "document_text": SAMPLE_CONTRACT_TEXT,
            "page_count": 5,
            "metadata": {"author": "Test"},
        }
        state = ContractAnalysisState(
            contract_id="test",
            file_bytes=b"%PDF-1.4 fake",
            file_type="pdf",
            agent_errors=[],
        )
        result = await extraction_node(state)

    assert result["document_text"] == SAMPLE_CONTRACT_TEXT
    assert result["page_count"] == 5
    assert "agent_errors" not in result or len(result.get("agent_errors", [])) == 0


@pytest.mark.asyncio
async def test_extraction_agent_corrupt_file():
    from app.agents.extraction_agent import extraction_node
    from app.utils.file_parser import ParseError

    with patch("app.agents.extraction_agent.parse_pdf", side_effect=ParseError("Corrupt PDF")):
        state = ContractAnalysisState(
            contract_id="test",
            file_bytes=b"not a pdf",
            file_type="pdf",
            agent_errors=[],
        )
        result = await extraction_node(state)

    assert result["document_text"] == ""
    assert len(result["agent_errors"]) > 0
    assert "extraction" in result["agent_errors"][0]


@pytest.mark.asyncio
async def test_extraction_agent_docx_success():
    from app.agents.extraction_agent import extraction_node

    with patch("app.agents.extraction_agent.parse_docx") as mock_parse:
        mock_parse.return_value = {
            "document_text": SAMPLE_CONTRACT_TEXT,
            "page_count": None,
            "metadata": {"author": "Test"},
        }
        state = ContractAnalysisState(
            contract_id="test",
            file_bytes=b"PK\x03\x04fake",
            file_type="docx",
            agent_errors=[],
        )
        result = await extraction_node(state)

    assert result["document_text"] == SAMPLE_CONTRACT_TEXT
    assert result["page_count"] == 0  # None converted to 0


# ─────────────────────────────────────────────────────────────
# Clause Agent Tests
# ─────────────────────────────────────────────────────────────

MOCK_CLAUSE_RESPONSE = {
    "clauses": [
        {"clause_type": "termination", "clause_text": "Either party may terminate...", "page_number": 1},
        {"clause_type": "liability", "clause_text": "Liability limited to...", "page_number": 2},
        {"clause_type": "confidentiality", "clause_text": "Hold in strict confidence...", "page_number": 3},
        {"clause_type": "indemnification", "clause_text": "Client shall indemnify...", "page_number": 4},
        {"clause_type": "payment_terms", "clause_text": "Net 30 from invoice...", "page_number": 4},
        {"clause_type": "governing_law", "clause_text": "Laws of Delaware...", "page_number": 5},
        {"clause_type": "intellectual_property", "clause_text": "IP remains with vendor...", "page_number": 5},
    ]
}


@pytest.mark.asyncio
async def test_clause_agent_success(base_state):
    from app.agents.clause_agent import clause_node

    mock_response = AsyncMock()
    mock_response.choices[0].message.content = __import__("json").dumps(MOCK_CLAUSE_RESPONSE)

    with patch("app.agents.clause_agent.litellm.acompletion", return_value=mock_response):
        result = await clause_node(base_state)

    assert len(result["clauses"]) == 7
    clause_types = {c["clause_type"] for c in result["clauses"]}
    assert "termination" in clause_types
    assert "liability" in clause_types


@pytest.mark.asyncio
async def test_clause_agent_llm_failure(base_state):
    from app.agents.clause_agent import clause_node

    with patch("app.agents.clause_agent.litellm.acompletion", side_effect=Exception("LLM error")):
        result = await clause_node(base_state)

    assert result["clauses"] == []
    assert len(result["agent_errors"]) > 0
    assert "clause" in result["agent_errors"][0]


@pytest.mark.asyncio
async def test_clause_agent_empty_document():
    from app.agents.clause_agent import clause_node

    state = ContractAnalysisState(
        contract_id="test",
        document_text="",
        agent_errors=[],
    )
    result = await clause_node(state)

    assert result["clauses"] == []
    assert len(result["agent_errors"]) > 0


# ─────────────────────────────────────────────────────────────
# Risk Agent Tests
# ─────────────────────────────────────────────────────────────

MOCK_RISK_RESPONSE = {
    "risks": [
        {"risk_level": "high", "risk_description": "Broad indemnification favors vendor.", "clause_type": "indemnification"},
        {"risk_level": "medium", "risk_description": "Auto-renewal trap.", "clause_type": "renewal"},
        {"risk_level": "low", "risk_description": "Standard liability cap.", "clause_type": "liability"},
    ],
    "overall_risk_score": 55,
}


@pytest.mark.asyncio
async def test_risk_agent_success(base_state):
    from app.agents.risk_agent import risk_node

    base_state["clauses"] = MOCK_CLAUSE_RESPONSE["clauses"]

    mock_response = AsyncMock()
    mock_response.choices[0].message.content = __import__("json").dumps(MOCK_RISK_RESPONSE)

    with patch("app.agents.risk_agent.litellm.acompletion", return_value=mock_response):
        result = await risk_node(base_state)

    assert len(result["risks"]) == 3
    assert result["risk_score"] == 55
    levels = {r["risk_level"] for r in result["risks"]}
    assert "high" in levels


@pytest.mark.asyncio
async def test_risk_agent_score_clamped(base_state):
    from app.agents.risk_agent import risk_node

    mock_data = {"risks": [], "overall_risk_score": 150}  # Over 100
    mock_response = AsyncMock()
    mock_response.choices[0].message.content = __import__("json").dumps(mock_data)

    with patch("app.agents.risk_agent.litellm.acompletion", return_value=mock_response):
        result = await risk_node(base_state)

    assert result["risk_score"] == 100


@pytest.mark.asyncio
async def test_risk_agent_llm_failure(base_state):
    from app.agents.risk_agent import risk_node

    with patch("app.agents.risk_agent.litellm.acompletion", side_effect=Exception("LLM error")):
        result = await risk_node(base_state)

    assert result["risks"] == []
    assert result["risk_score"] == 0
    assert len(result["agent_errors"]) > 0


# ─────────────────────────────────────────────────────────────
# Data Extraction Agent Tests
# ─────────────────────────────────────────────────────────────

MOCK_DATA_RESPONSE = {
    "contract_information": {
        "title": "Software License Agreement",
        "effective_date": "2025-01-01",
        "expiration_date": "2026-12-31",
        "parties": [{"name": "Acme Corp", "role": "Vendor"}, {"name": "BetaCo", "role": "Client"}],
        "contract_value": "$250,000",
        "renewal_terms": "Auto-renews unless cancelled",
    }
}


@pytest.mark.asyncio
async def test_data_extraction_agent_success(base_state):
    from app.agents.data_extraction_agent import data_extraction_node

    mock_response = AsyncMock()
    mock_response.choices[0].message.content = __import__("json").dumps(MOCK_DATA_RESPONSE)

    with patch("app.agents.data_extraction_agent.litellm.acompletion", return_value=mock_response):
        result = await data_extraction_node(base_state)

    info = result["contract_information"]
    assert info["title"] == "Software License Agreement"
    assert len(info["parties"]) == 2
    assert info["contract_value"] == "$250,000"


@pytest.mark.asyncio
async def test_data_extraction_agent_llm_failure(base_state):
    from app.agents.data_extraction_agent import data_extraction_node

    with patch("app.agents.data_extraction_agent.litellm.acompletion", side_effect=Exception("LLM error")):
        result = await data_extraction_node(base_state)

    assert result["contract_information"] == {}
    assert len(result["agent_errors"]) > 0


# ─────────────────────────────────────────────────────────────
# Summary Agent Tests
# ─────────────────────────────────────────────────────────────

MOCK_SUMMARY_RESPONSE = {
    "summary": {
        "executive_summary": "This is a software license agreement...",
        "key_terms": "License fee of $250,000 for 2-year term...",
        "important_obligations": ["Pay invoices within 30 days", "Maintain confidentiality"],
        "important_dates": ["Effective: Jan 1, 2025", "Expires: Dec 31, 2026"],
    }
}


@pytest.mark.asyncio
async def test_summary_agent_success(base_state):
    from app.agents.summary_agent import summary_node

    mock_response = AsyncMock()
    mock_response.choices[0].message.content = __import__("json").dumps(MOCK_SUMMARY_RESPONSE)

    with patch("app.agents.summary_agent.litellm.acompletion", return_value=mock_response):
        result = await summary_node(base_state)

    summary = result["summary"]
    assert "executive_summary" in summary
    assert len(summary["important_obligations"]) == 2


@pytest.mark.asyncio
async def test_summary_agent_llm_failure(base_state):
    from app.agents.summary_agent import summary_node

    with patch("app.agents.summary_agent.litellm.acompletion", side_effect=Exception("LLM error")):
        result = await summary_node(base_state)

    assert result["summary"] == {}
    assert len(result["agent_errors"]) > 0


# ─────────────────────────────────────────────────────────────
# Report Agent Tests
# ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_report_agent_assembles_correctly(base_state):
    from app.agents.report_agent import report_node

    base_state["clauses"] = MOCK_CLAUSE_RESPONSE["clauses"]
    base_state["risks"] = MOCK_RISK_RESPONSE["risks"]
    base_state["risk_score"] = 55
    base_state["contract_information"] = MOCK_DATA_RESPONSE["contract_information"]
    base_state["summary"] = MOCK_SUMMARY_RESPONSE["summary"]

    result = await report_node(base_state)

    report = result["final_report"]
    assert "summary" in report
    assert "clauses" in report
    assert "risks" in report
    assert "contract_information" in report
    assert report["risk_score"] == 55
