# CHECKPOINTS.md
# Contract Analysis Tool — Implementation Checkpoints

> Each checkpoint is a concrete, testable gate.
> Do not advance to the next day's work until the current checkpoint passes.
> Mark checkpoints with [x] as they are completed.

---

## Day 1 Checkpoint — Project Bootstrap

| # | Checkpoint | How to Verify | Status |
|---|---|---|---|
| 1.1 | Backend FastAPI server starts without errors | `uvicorn app.main:app --reload` shows "Application startup complete" | [ ] |
| 1.2 | `GET /health` returns HTTP 200 | `curl http://localhost:8000/health` | [ ] |
| 1.3 | Database connection established | Health check confirms DB connection; no SQLAlchemy errors in logs | [ ] |
| 1.4 | All 4 database tables created | `\dt` in psql shows contracts, contract_analysis, contract_clauses, contract_risks | [ ] |
| 1.5 | Frontend Vite dev server starts | `npm run dev` shows Vite server on port 5173 | [ ] |
| 1.6 | `.env.example` covers all required vars | All vars from SPEC.md Section 7 are present | [ ] |

---

## Day 2 Checkpoint — Authentication & Upload

| # | Checkpoint | How to Verify | Status |
|---|---|---|---|
| 2.1 | `POST /contracts/upload` with valid JWT and valid PDF returns 201 | Use Swagger UI / Postman | [ ] |
| 2.2 | Upload without JWT returns 401 | `curl` without Authorization header | [ ] |
| 2.3 | Upload with invalid file type (.txt) returns 422 with `INVALID_FILE_TYPE` | Unit test passes | [ ] |
| 2.4 | Upload with oversized file returns 422 with `FILE_TOO_LARGE` | Unit test passes | [ ] |
| 2.5 | Contract record inserted in DB with `status='pending'` | Database query confirms row exists | [ ] |

---

## Day 3 Checkpoint — Document Extraction Agent

| # | Checkpoint | How to Verify | Status |
|---|---|---|---|
| 3.1 | PDF extraction returns `document_text`, `page_count`, `metadata` | Unit test with sample_nda.pdf passes | [ ] |
| 3.2 | DOCX extraction returns `document_text` and `metadata` | Unit test with sample_nda.docx passes | [ ] |
| 3.3 | Corrupt PDF input → agent adds to `agent_errors`, returns safe state | Unit test with corrupt file passes | [ ] |
| 3.4 | Extracted text is non-empty for valid contracts | Manual inspection of output | [ ] |

---

## Day 4 Checkpoint — Clause & Risk Agents

| # | Checkpoint | How to Verify | Status |
|---|---|---|---|
| 4.1 | Clause agent returns list of clauses with `clause_type` and `clause_text` | Unit test (mock LLM) passes | [ ] |
| 4.2 | Clause agent detects at least 7 of 10 clause types in sample NDA | Integration test with real LLM | [ ] |
| 4.3 | Risk agent assigns a risk level (high/medium/low) to each clause | Unit test passes | [ ] |
| 4.4 | Risk agent returns `overall_risk_score` between 0 and 100 | Assertion in unit test | [ ] |
| 4.5 | LLM failure → agent adds error to `agent_errors`, returns safe default | Unit test with mocked exception | [ ] |

---

## Day 5 Checkpoint — Data Extraction & Summary Agents

| # | Checkpoint | How to Verify | Status |
|---|---|---|---|
| 5.1 | Data extraction agent returns all 6 metadata fields (nulls allowed) | Unit test passes | [ ] |
| 5.2 | Summary agent returns all 4 summary sections | Unit test passes | [ ] |
| 5.3 | Both agents handle LLM failures gracefully | Unit tests with mocked exceptions pass | [ ] |

---

## Day 6 Checkpoint — LangGraph Workflow

| # | Checkpoint | How to Verify | Status |
|---|---|---|---|
| 6.1 | LangGraph workflow compiles without errors | `python -c "from app.workflows.contract_workflow import contract_graph"` | [ ] |
| 6.2 | Full workflow executes end-to-end with sample NDA | Integration test: invoke graph with sample contract | [ ] |
| 6.3 | Parallel nodes (clause, risk, data, summary) execute concurrently | Verify via logs: all 4 start before any complete | [ ] |
| 6.4 | Final report contains all 4 sections | Assert on `final_report` keys in test | [ ] |
| 6.5 | Analysis record persisted to `contract_analysis` table | Database query after workflow confirms row | [ ] |
| 6.6 | Clauses persisted to `contract_clauses` table | Database query confirms rows | [ ] |
| 6.7 | Risks persisted to `contract_risks` table | Database query confirms rows | [ ] |

---

## Day 7 Checkpoint — Analysis API & All Routes

| # | Checkpoint | How to Verify | Status |
|---|---|---|---|
| 7.1 | `POST /contracts/analyze/{id}` triggers workflow and returns SSE stream | SSE client receives events | [ ] |
| 7.2 | All 5 progress stages are streamed | SSE event log shows all 5 stage messages | [ ] |
| 7.3 | `GET /contracts/{id}/analysis` returns full report after completion | API response contains summary, clauses, risks, contract_info | [ ] |
| 7.4 | `GET /contracts/history` returns user's contract list | API returns array with correct records | [ ] |
| 7.5 | `DELETE /contracts/{id}` removes record and cascades | DB confirms deletion of contract + all related rows | [ ] |
| 7.6 | Access to another user's contract returns 403 | Integration test with two user tokens confirms 403 | [ ] |

---

## Day 8 Checkpoint — RAG Infrastructure

| # | Checkpoint | How to Verify | Status |
|---|---|---|---|
| 8.1 | Contract text is split into chunks | `len(chunk_contract(text, id)) > 0` | [ ] |
| 8.2 | Chunks are embedded and stored in ChromaDB | ChromaDB collection `contract_{id}` exists with correct count | [ ] |
| 8.3 | Retriever returns top-5 chunks for a query | `retrieve_relevant_chunks("termination clause", id)` returns 5 results | [ ] |
| 8.4 | RAG integrated into clause agent | Clause agent prompt uses retrieved chunks | [ ] |
| 8.5 | ChromaDB persists across server restart | Stop/start server; collection still queryable | [ ] |

---

## Day 9 Checkpoint — Frontend Upload Page

| # | Checkpoint | How to Verify | Status |
|---|---|---|---|
| 9.1 | Frontend builds without TypeScript errors | `npx tsc --noEmit` exits 0 | [ ] |
| 9.2 | Drag-and-drop accepts PDF and DOCX, rejects other types | Manual UI test | [ ] |
| 9.3 | File size limit enforced in UI (>20 MB rejected with message) | Manual UI test | [ ] |
| 9.4 | Upload button calls API and shows loading state | Observe network tab and UI | [ ] |
| 9.5 | Successful upload transitions to analysis view | UI navigation occurs after upload | [ ] |

---

## Day 10 Checkpoint — Streaming Progress UI

| # | Checkpoint | How to Verify | Status |
|---|---|---|---|
| 10.1 | StreamingProgress component renders 5 stages | Visual inspection | [ ] |
| 10.2 | Stages update in real-time as SSE events arrive | Watch UI during analysis | [ ] |
| 10.3 | Completed stages show checkmark icon | Visual inspection | [ ] |
| 10.4 | On stream complete: navigates to analysis detail | Manual test with real contract upload | [ ] |
| 10.5 | On stream error: displays error message | Trigger error in backend, observe UI | [ ] |

---

## Day 11 Checkpoint — Analysis Detail Page

| # | Checkpoint | How to Verify | Status |
|---|---|---|---|
| 11.1 | Contract metadata section renders all 6 fields | Visual inspection with real data | [ ] |
| 11.2 | Executive summary section renders | Visual inspection | [ ] |
| 11.3 | Clauses table renders with detected/missing status | Visual inspection | [ ] |
| 11.4 | Risks table renders with color-coded badges | Red=High, Yellow=Medium, Green=Low | [ ] |
| 11.5 | Overall risk score is prominently displayed | Visual inspection | [ ] |
| 11.6 | Page loads data from `GET /analysis` API | Network tab shows API call | [ ] |

---

## Day 12 Checkpoint — History Page & Navigation

| # | Checkpoint | How to Verify | Status |
|---|---|---|---|
| 12.1 | History page lists all user contracts | Manual test after uploading 3 contracts | [ ] |
| 12.2 | Each row shows: file name, date, status, risk score | Visual inspection | [ ] |
| 12.3 | Clicking a row navigates to analysis detail | Manual navigation test | [ ] |
| 12.4 | Delete action removes contract from list | Manual test; row disappears | [ ] |
| 12.5 | Unauthenticated access redirects to login | Clear JWT, navigate to /history | [ ] |

---

## Day 13 Checkpoint — Error Handling & Security

| # | Checkpoint | How to Verify | Status |
|---|---|---|---|
| 13.1 | Corrupt PDF upload shows structured error in UI | Upload a corrupt file; error message appears | [ ] |
| 13.2 | Backend returns 422 with correct error code for corrupt files | API test confirms error code `PARSE_ERROR` | [ ] |
| 13.3 | Ownership enforcement: user B cannot access user A's contract | Integration test confirms 403 | [ ] |
| 13.4 | CORS rejects requests from unauthorized origins | Browser test or curl with bad Origin header | [ ] |
| 13.5 | Loading skeletons display during data fetch | Simulate slow network in browser DevTools | [ ] |

---

## Day 14 Checkpoint — Final Acceptance (All Success Criteria)

| # | Success Criterion | Status |
|---|---|---|
| SC-01 | PDF and DOCX accepted, stored, status recorded | [ ] |
| SC-02 | All 6 agents execute without error on sample NDA | [ ] |
| SC-03 | Minimum 7 of 10 clause types detected in sample NDA | [ ] |
| SC-04 | Risk level assigned to every detected clause | [ ] |
| SC-05 | Final report contains all 4 sections | [ ] |
| SC-06 | Frontend shows all 5 streaming progress stages | [ ] |
| SC-07 | User can retrieve past analyses without re-running | [ ] |
| SC-08 | Non-owning user receives 403 on API access | [ ] |
| SC-09 | Corrupt file returns structured error, not 500 | [ ] |
| SC-10 | All unit and integration tests pass | [ ] |
| SC-11 | README.md setup instructions work end-to-end | [ ] |
| SC-12 | Swagger UI documents all API endpoints | [ ] |

---

> **Project is complete when all Day 14 checkpoints are marked [x].**
