# MVP_PREVIEW.md
# Contract Analysis Tool — MVP Preview

> This document defines exactly what the working product will look like at the end of the 2-week capstone sprint.
> This is NOT a vision document. It describes the concrete, demonstrable, fully working product.

---

## MVP Definition

The Minimum Viable Product is a **fully functional, end-to-end contract analysis application** with a working UI, working backend, and working AI pipeline. It is not a prototype or a demo with mocked data.

---

## What the User Can Do in the MVP

### 1. Upload a Contract
- Navigate to the Contract Upload page.
- Drag-and-drop or browse to select a PDF or DOCX file (max 20 MB).
- Click "Analyze Contract."
- Receive immediate feedback: upload confirmation and analysis started.

### 2. Watch Real-Time Analysis Progress
- A progress panel shows live streaming updates:
  ```
  ✅ Document uploaded
  ⏳ Extracting document text...
  ⏳ Identifying clauses...
  ⏳ Analyzing risks...
  ⏳ Generating summary...
  ⏳ Building final report...
  ✅ Analysis complete
  ```

### 3. View the Full Analysis Report
After analysis completes, the user sees a structured report page containing:

#### Section A: Contract Information
| Field | Example Value |
|---|---|
| Contract Title | Software License Agreement |
| Parties | Acme Corp (Vendor), BetaCo (Client) |
| Effective Date | January 1, 2025 |
| Expiration Date | December 31, 2026 |
| Contract Value | $250,000 |
| Renewal Terms | Auto-renews 30 days prior notice |

#### Section B: Executive Summary
> "This is a 2-year software license agreement between Acme Corp and BetaCo valued at $250,000. The agreement includes standard IP protections but contains an unusually broad indemnification clause favoring the vendor..."

#### Section C: Identified Clauses
| Clause Type | Detected | Excerpt |
|---|---|---|
| Termination | ✅ | "Either party may terminate with 30-day written notice..." |
| Liability | ✅ | "Liability limited to fees paid in prior 12 months..." |
| Confidentiality | ✅ | "Recipient agrees to hold in confidence..." |
| Indemnification | ✅ | "Client shall indemnify vendor from any third-party claims..." |
| Payment Terms | ✅ | "Net 30 from invoice date..." |
| Non-Compete | ❌ | Not found |
| Force Majeure | ✅ | "Neither party shall be liable for delays caused by..." |

#### Section D: Risk Analysis
| Risk | Level | Description |
|---|---|---|
| Broad indemnification | 🔴 High | Client bears full third-party liability with no cap |
| Missing Non-Compete | 🟡 Medium | No non-compete clause; vendor may serve direct competitors |
| Auto-renewal trap | 🟡 Medium | Short notice window for cancellation (30 days) |
| Liability cap favorable | 🟢 Low | Liability capped at contract value — standard |

**Overall Risk Score: 67 / 100**

### 4. View Contract History
- A history page lists all previously analyzed contracts.
- Each row shows: file name, upload date, status, risk score.
- Clicking a row navigates to the full analysis report.

### 5. Delete a Contract
- From history or the detail view, user can delete a contract.
- Deletion removes all analysis data.

---

## What Is NOT in the MVP

| Capability | Status |
|---|---|
| OCR for scanned PDFs | Out of scope |
| Contract comparison | Out of scope |
| Multi-language support | Out of scope |
| Clause negotiation suggestions | Out of scope |
| Email notifications | Out of scope |
| PDF/Word export of report | Out of scope |
| Admin dashboard | Out of scope |
| Multi-user organizations | Out of scope |

---

## Technical MVP State

| Layer | MVP State |
|---|---|
| Backend | FastAPI server running with all 6 API routes functional |
| LangGraph | 6-agent workflow executing in parallel where applicable |
| RAG | Contract chunks embedded in ChromaDB |
| Database | All 4 tables created and populated via Supabase/PostgreSQL |
| Streaming | SSE stream delivering agent progress to frontend |
| Frontend | 3 pages: Upload, History, Analysis Detail |
| Auth | JWT-based authentication on all routes |
| Error Handling | Structured errors for corrupt files, LLM failures, empty docs |

---

## Demo Script (End-of-Capstone Presentation)

1. Open the application in a browser.
2. Log in with a test user account.
3. Upload a sample NDA (provided in `/tests/fixtures/sample_nda.pdf`).
4. Show the real-time streaming progress bar.
5. Navigate to the completed analysis report.
6. Highlight: identified clauses, risk levels, executive summary, metadata.
7. Navigate to contract history — show the analyzed contract in the list.
8. Show the API documentation (Swagger UI at `/docs`).
9. Demonstrate authentication enforcement: attempt to access another user's contract — receive 403.

---

## Acceptance Gate

The MVP is accepted when all items in `CHECKPOINTS.md` — Day 14 checkpoint — are marked complete.
