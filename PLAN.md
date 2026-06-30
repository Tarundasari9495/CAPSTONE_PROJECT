# PLAN.md
# Contract Analysis Tool — 2-Week Implementation Plan

> All tasks align with approved REQUIREMENTS.md and SPEC.md.
> Scope is fixed. No feature additions during implementation.

---

## Sprint Overview

| Week | Focus | Goal |
|---|---|---|
| Week 1 | Foundation + Backend Core | Working API, database, LangGraph workflow, agents |
| Week 2 | RAG + Frontend + Integration + Polish | Full stack working, streaming, UI complete, tested |

---

## Week 1 — Backend & AI Core

### Day 1 — Project Bootstrap
**Goal:** Clean repo, working server, database connected.

- [ ] Initialize backend project: `pyproject.toml` / `requirements.txt`
- [ ] Initialize frontend project: Vite + React + TypeScript + Tailwind
- [ ] Set up `.env.example` and `.env` (local)
- [ ] Configure FastAPI app with CORS, lifespan events
- [ ] Set up SQLAlchemy async engine + Supabase connection
- [ ] Run Alembic initial migration — create all 4 tables
- [ ] Verify database connection with a health check endpoint `GET /health`
- [ ] Set up Docker Compose (PostgreSQL + ChromaDB local containers)
- [ ] Push initial project structure to repo

**Checkpoint:** `GET /health` returns 200, database tables exist.

---

### Day 2 — Authentication & File Upload
**Goal:** Authenticated users can upload contracts.

- [ ] Implement JWT authentication middleware
- [ ] Implement `get_current_user` dependency
- [ ] Implement `POST /api/v1/contracts/upload` endpoint
- [ ] Implement file type validation (magic bytes + extension)
- [ ] Implement file size validation (≤ 20 MB)
- [ ] Store contract record in `contracts` table with `status = 'pending'`
- [ ] Write unit tests for upload validation

**Checkpoint:** Authenticated POST to `/upload` stores a contract record. Invalid files are rejected with structured errors.

---

### Day 3 — Document Extraction Agent
**Goal:** Parse PDF and DOCX, extract text and metadata.

- [ ] Install and configure PyMuPDF (PDF parsing)
- [ ] Install and configure python-docx (DOCX parsing)
- [ ] Implement `file_parser.py` utility
- [ ] Implement `ExtractionAgent` in `agents/extraction_agent.py`
- [ ] Define `ContractAnalysisState` TypedDict
- [ ] Test extraction on sample NDA (PDF and DOCX)
- [ ] Handle corrupt file errors — return structured error state
- [ ] Write unit tests for extraction agent

**Checkpoint:** Extraction agent returns `document_text`, `page_count`, and `metadata` for both PDF and DOCX inputs.

---

### Day 4 — Clause Identification Agent + Risk Analysis Agent
**Goal:** LLM-powered clause detection and risk scoring.

- [ ] Configure LiteLLM with OpenAI backend
- [ ] Implement `ClauseAgent` — LLM prompt to identify all 10 clause types
- [ ] Implement clause output parser (validate JSON structure)
- [ ] Implement `RiskAgent` — LLM prompt to assess clause risk
- [ ] Implement risk score calculation (weighted average)
- [ ] Write unit tests for both agents with mock LLM responses

**Checkpoint:** Given extracted text, clause agent returns structured clauses. Risk agent returns risk levels and overall score.

---

### Day 5 — Data Extraction Agent + Summary Agent
**Goal:** Structured metadata extraction and executive summary generation.

- [ ] Implement `DataExtractionAgent` — extract title, dates, parties, value, renewal
- [ ] Implement `SummaryAgent` — generate executive summary, key terms, obligations, dates
- [ ] Write unit tests for both agents

**Checkpoint:** Both agents return valid, structured JSON output from contract text.

---

### Day 6 — Final Report Agent + LangGraph Workflow
**Goal:** Complete multi-agent pipeline wired with LangGraph.

- [ ] Implement `ReportAgent` — merge all agent outputs into final report
- [ ] Implement `contract_workflow.py` using LangGraph
- [ ] Wire parallel fan-out: clause, risk, data extraction, summary agents run in parallel after extraction
- [ ] Wire sequential fan-in: report agent waits for all parallel agents
- [ ] Wire DB persistence node after report assembly
- [ ] Test full workflow end-to-end with sample NDA
- [ ] Handle workflow state errors (individual agent failures do not crash the graph)

**Checkpoint:** Full LangGraph workflow executes end-to-end and persists final report to database.

---

### Day 7 — Analysis Endpoint + Streaming
**Goal:** API triggers workflow, streams progress to client.

- [ ] Implement `POST /api/v1/contracts/analyze/{contract_id}` as SSE endpoint
- [ ] Stream agent progress events as workflow nodes execute
- [ ] Implement `GET /api/v1/contracts/{contract_id}/analysis` to retrieve stored report
- [ ] Implement `GET /api/v1/contracts/{contract_id}` for contract metadata
- [ ] Implement `GET /api/v1/contracts/history` for user's contract list
- [ ] Implement `DELETE /api/v1/contracts/{contract_id}` with cascade
- [ ] Write integration tests for all routes

**Checkpoint:** All 6 API endpoints respond correctly. SSE stream delivers all 5 progress stages.

---

## Week 2 — RAG + Frontend + Integration

### Day 8 — RAG Infrastructure
**Goal:** Contract text chunked, embedded, and stored in ChromaDB.

- [ ] Implement `contract_chunker.py` — recursive text splitter
- [ ] Implement `contract_embeddings.py` — OpenAI embeddings integration
- [ ] Implement `contract_retriever.py` — ChromaDB query with top-k
- [ ] Integrate RAG into clause agent (retrieve relevant chunks before prompting)
- [ ] Integrate RAG into risk agent (retrieve clause context)
- [ ] Write unit tests for RAG components

**Checkpoint:** Contract text is chunked, embedded, and stored. Retriever returns top-5 relevant chunks with citations.

---

### Day 9 — Frontend Bootstrap + Upload Page
**Goal:** Frontend project running with upload UI.

- [ ] Verify Vite + React + TypeScript + Tailwind setup
- [ ] Configure API service layer (`services/api.ts`)
- [ ] Implement `ContractUpload` component with drag-and-drop
- [ ] Implement file type and size validation on the frontend
- [ ] Connect upload to `POST /upload` API
- [ ] Display upload success and trigger analysis start

**Checkpoint:** User can upload a PDF or DOCX from the UI and receive confirmation.

---

### Day 10 — Streaming Progress Component + Analysis Trigger
**Goal:** Frontend shows real-time analysis progress.

- [ ] Implement `StreamingProgress` component
- [ ] Connect to SSE stream from `POST /analyze/{id}`
- [ ] Display each stage with a spinner → checkmark transition
- [ ] Handle stream completion — navigate to analysis detail

**Checkpoint:** Streaming progress displays all 5 stages in real-time after upload.

---

### Day 11 — Analysis Detail Page
**Goal:** Full analysis report rendered in the UI.

- [ ] Implement `AnalysisDetailPage.tsx`
- [ ] Implement `ContractInfoSection` component (metadata table)
- [ ] Implement `ExecutiveSummarySection` component
- [ ] Implement `ClauseTable` component (clause type, status, excerpt)
- [ ] Implement `RiskTable` component with `RiskBadge` (color-coded High/Medium/Low)
- [ ] Display overall risk score prominently
- [ ] Connect to `GET /analysis` API

**Checkpoint:** Full analysis report renders correctly with real data from a sample NDA analysis.

---

### Day 12 — Contract History Page + Navigation
**Goal:** Users can browse all past analyses.

- [ ] Implement `HistoryPage.tsx`
- [ ] Display table: file name, date, status, risk score
- [ ] Link each row to `AnalysisDetailPage`
- [ ] Implement delete action from history row
- [ ] Implement route navigation (`react-router-dom`)
- [ ] Implement authentication guard (redirect to login if unauthenticated)

**Checkpoint:** History page loads user's contracts. Navigation between pages works.

---

### Day 13 — Error Handling + Security Hardening + Accessibility
**Goal:** Robust error states in UI and API; security verified.

- [ ] Implement error boundary in React
- [ ] Display structured error messages for upload failures
- [ ] Display error state on analysis detail if analysis failed
- [ ] Verify file upload security: magic bytes check in backend
- [ ] Verify ownership enforcement: integration test with two users
- [ ] Add loading skeletons for async data states
- [ ] Verify CORS config restricts to allowed origins

**Checkpoint:** All error states render correctly. Security tests pass.

---

### Day 14 — Testing, Docs, and Final Review
**Goal:** Project complete and demonstrable.

- [ ] Run full test suite — fix any failing tests
- [ ] Verify all 9 success criteria from `REQUIREMENTS.md`
- [ ] Complete API documentation in `docs/api.md`
- [ ] Update `README.md` with setup instructions
- [ ] Record demo or prepare demo script
- [ ] Final review against `DELIVERABLES.md` checklist
- [ ] Confirm all `CHECKPOINTS.md` items are green

**Checkpoint:** All deliverables complete. Demo script passes. All success criteria met.

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| LLM latency causes slow analysis | Medium | Medium | Parallel agent execution; streaming hides latency |
| LangGraph parallel state merging bugs | Medium | High | Unit test state schema; test with sample contracts Day 6 |
| ChromaDB persistence issues on restart | Low | Medium | Configure persistent directory; test on Day 8 |
| File parsing edge cases (malformed PDFs) | Medium | Low | Structured error handling; fixture-based tests |
| Scope creep | High | High | REQUIREMENTS.md frozen; enforced by copilot-instructions |
| LLM JSON output format inconsistency | High | Medium | Pydantic output parsers + retry logic in agents |

---

## Daily Stand-Up Template

```
Date: ___________

Yesterday:
- 

Today:
- 

Blockers:
- 
```
