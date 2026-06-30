# DELIVERABLES.md
# Contract Analysis Tool — Deliverables

> This document defines every artifact that must be produced by the end of the 2-week sprint.
> Use this as the final checklist before project submission.

---

## Category 1: Backend Implementation

| # | Deliverable | Location | Status |
|---|---|---|---|
| B-01 | FastAPI application with all routes | `backend/app/` | [ ] |
| B-02 | JWT authentication middleware | `backend/app/routers/auth.py` | [ ] |
| B-03 | File upload endpoint with validation | `backend/app/routers/contracts.py` | [ ] |
| B-04 | Analysis trigger endpoint (SSE streaming) | `backend/app/routers/contracts.py` | [ ] |
| B-05 | Contract retrieval endpoint | `backend/app/routers/contracts.py` | [ ] |
| B-06 | Analysis report retrieval endpoint | `backend/app/routers/contracts.py` | [ ] |
| B-07 | Contract history endpoint | `backend/app/routers/contracts.py` | [ ] |
| B-08 | Contract delete endpoint | `backend/app/routers/contracts.py` | [ ] |
| B-09 | SQLAlchemy ORM models for all 4 tables | `backend/app/models/` | [ ] |
| B-10 | Pydantic schemas for request/response | `backend/app/schemas/` | [ ] |
| B-11 | Contract service layer | `backend/app/services/contract_service.py` | [ ] |
| B-12 | Analysis service layer | `backend/app/services/analysis_service.py` | [ ] |
| B-13 | Alembic migration (initial schema) | `backend/alembic/` | [ ] |
| B-14 | File parser utility (PDF + DOCX) | `backend/app/utils/file_parser.py` | [ ] |
| B-15 | File security validator (magic bytes) | `backend/app/utils/security.py` | [ ] |
| B-16 | Environment configuration module | `backend/app/config.py` | [ ] |

---

## Category 2: LangGraph Multi-Agent Workflow

| # | Deliverable | Location | Status |
|---|---|---|---|
| A-01 | Document Extraction Agent | `backend/app/agents/extraction_agent.py` | [ ] |
| A-02 | Clause Identification Agent | `backend/app/agents/clause_agent.py` | [ ] |
| A-03 | Risk Analysis Agent | `backend/app/agents/risk_agent.py` | [ ] |
| A-04 | Contract Data Extraction Agent | `backend/app/agents/data_extraction_agent.py` | [ ] |
| A-05 | Contract Summary Agent | `backend/app/agents/summary_agent.py` | [ ] |
| A-06 | Final Report Agent | `backend/app/agents/report_agent.py` | [ ] |
| A-07 | LangGraph workflow (parallel fan-out + fan-in) | `backend/app/workflows/contract_workflow.py` | [ ] |
| A-08 | ContractAnalysisState TypedDict | `backend/app/workflows/contract_workflow.py` | [ ] |

---

## Category 3: RAG Infrastructure

| # | Deliverable | Location | Status |
|---|---|---|---|
| R-01 | Contract chunker (recursive text splitter) | `backend/app/services/rag/contract_chunker.py` | [ ] |
| R-02 | Contract embeddings (OpenAI + ChromaDB store) | `backend/app/services/rag/contract_embeddings.py` | [ ] |
| R-03 | Contract retriever (ChromaDB query) | `backend/app/services/rag/contract_retriever.py` | [ ] |

---

## Category 4: Frontend Implementation

| # | Deliverable | Location | Status |
|---|---|---|---|
| F-01 | Contract Upload Page | `frontend/src/pages/UploadPage.tsx` | [ ] |
| F-02 | Drag-and-drop upload component | `frontend/src/components/ContractUpload/` | [ ] |
| F-03 | Analysis Detail Page | `frontend/src/pages/AnalysisDetailPage.tsx` | [ ] |
| F-04 | Contract Metadata section component | `frontend/src/components/AnalysisReport/` | [ ] |
| F-05 | Clause Table component | `frontend/src/components/ClauseTable/` | [ ] |
| F-06 | Risk Table + Risk Badge component | `frontend/src/components/RiskBadge/` | [ ] |
| F-07 | Streaming Progress component | `frontend/src/components/StreamingProgress/` | [ ] |
| F-08 | Contract History Page | `frontend/src/pages/HistoryPage.tsx` | [ ] |
| F-09 | Contract History list component | `frontend/src/components/ContractHistory/` | [ ] |
| F-10 | API service layer | `frontend/src/services/api.ts` | [ ] |
| F-11 | TypeScript types for all API contracts | `frontend/src/types/contract.ts` | [ ] |
| F-12 | React Router navigation with auth guard | `frontend/src/App.tsx` | [ ] |
| F-13 | useContractAnalysis custom hook | `frontend/src/hooks/useContractAnalysis.ts` | [ ] |

---

## Category 5: Database

| # | Deliverable | Verification | Status |
|---|---|---|---|
| D-01 | `contracts` table created with all columns | `\d contracts` in psql | [ ] |
| D-02 | `contract_analysis` table created | `\d contract_analysis` in psql | [ ] |
| D-03 | `contract_clauses` table created | `\d contract_clauses` in psql | [ ] |
| D-04 | `contract_risks` table created | `\d contract_risks` in psql | [ ] |
| D-05 | Cascade deletes working | Delete contract → all related rows removed | [ ] |

---

## Category 6: Testing

| # | Deliverable | Location | Status |
|---|---|---|---|
| T-01 | Agent unit tests (all 6 agents, mock LLM) | `backend/tests/test_agents.py` | [ ] |
| T-02 | API route integration tests | `backend/tests/test_routes.py` | [ ] |
| T-03 | RAG component tests | `backend/tests/test_rag.py` | [ ] |
| T-04 | Sample NDA fixture (PDF) | `backend/tests/fixtures/sample_nda.pdf` | [ ] |
| T-05 | Test coverage ≥ 60% | `pytest --cov` report | [ ] |

---

## Category 7: Documentation

| # | Deliverable | Location | Status |
|---|---|---|---|
| Doc-01 | README.md with full setup instructions | `README.md` | [ ] |
| Doc-02 | API documentation | `docs/api.md` | [ ] |
| Doc-03 | Architecture diagram (Mermaid) | `docs/architecture.mmd` | [ ] |
| Doc-04 | `.env.example` with all required variables | `backend/.env.example` | [ ] |
| Doc-05 | Swagger UI accessible at `/docs` | `http://localhost:8000/docs` | [ ] |

---

## Category 8: DevOps / Setup

| # | Deliverable | Location | Status |
|---|---|---|---|
| Ops-01 | `requirements.txt` with pinned versions | `backend/requirements.txt` | [ ] |
| Ops-02 | `package.json` with pinned versions | `frontend/package.json` | [ ] |
| Ops-03 | `docker-compose.yml` for local services | `docker-compose.yml` | [ ] |
| Ops-04 | Backend `Dockerfile` | `backend/Dockerfile` | [ ] |

---

## Final Submission Checklist

Before marking the project complete:

- [ ] All checkpoints in `CHECKPOINTS.md` Day 14 are green
- [ ] All deliverables above are marked complete
- [ ] Demo script from `MVP_PREVIEW.md` executes successfully end-to-end
- [ ] All 9 success criteria in `REQUIREMENTS.md` are met
- [ ] No hardcoded API keys or secrets in the codebase
- [ ] README.md allows a fresh developer to set up and run the project
