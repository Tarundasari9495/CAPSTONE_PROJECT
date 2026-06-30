# REQUIREMENTS.md
# Contract Analysis Tool — Approved Requirements

> **STATUS: PENDING APPROVAL**
> Once approved, this document is FROZEN. No scope changes are permitted without a formal change request.

---

## 1. Project Overview

| Field | Value |
|---|---|
| Project Name | Contract Analysis Tool |
| Capstone Label | AI-Forge 2026 — Project 9 |
| Implementation Window | 2 Weeks |
| Application Type | Standalone New Application |
| Target User | Legal professionals, contract managers, business teams |

---

## 2. Functional Requirements

### FR-01 — Contract Upload
- The system SHALL accept PDF and DOCX file formats.
- The system SHALL validate file type before processing.
- The system SHALL validate file size (maximum 20 MB).
- The system SHALL store uploaded contracts in the database with a unique contract ID.
- The system SHALL associate uploaded contracts with the authenticated user.

### FR-02 — Document Extraction
- The system SHALL extract full text from uploaded PDF files.
- The system SHALL extract full text from uploaded DOCX files.
- The system SHALL preserve page structure during extraction.
- The system SHALL extract document-level metadata (page count, file size, author if available).
- The system SHALL handle encrypted or corrupt files gracefully with structured error responses.

### FR-03 — Clause Identification
- The system SHALL identify the following clause types:
  - Termination
  - Liability
  - Confidentiality
  - Indemnification
  - Payment Terms
  - Renewal
  - Governing Law
  - Intellectual Property
  - Non-Compete
  - Force Majeure
- The system SHALL return clause text alongside clause type.
- The system SHALL flag missing critical clauses.

### FR-04 — Risk Analysis
- The system SHALL analyze each identified clause for risk.
- The system SHALL classify risk as: High, Medium, or Low.
- The system SHALL identify missing clauses as a risk signal.
- The system SHALL detect unfavorable obligations, legal exposure, financial risks, and vendor/customer imbalance.
- The system SHALL compute an overall contract risk score (0–100).

### FR-05 — Contract Metadata Extraction
- The system SHALL extract:
  - Contract title
  - Effective date
  - Expiration date
  - Parties involved (names and roles)
  - Contract value (if present)
  - Renewal terms

### FR-06 — Contract Summarization
- The system SHALL generate:
  - Executive Summary
  - Key Terms Summary
  - Important Obligations
  - Important Dates

### FR-07 — Final Report Generation
- The system SHALL combine outputs from all agents into a single structured report.
- The report SHALL include: summary, clauses, risks, and contract information.
- The report SHALL be persisted in the database.

### FR-08 — RAG Support
- The system SHALL chunk contract text into semantically meaningful segments.
- The system SHALL generate embeddings for each chunk using OpenAI Embeddings Large.
- The system SHALL store embeddings in ChromaDB.
- The system SHALL support retrieval of relevant contract sections with citations.

### FR-09 — Analysis Streaming
- The system SHALL stream analysis progress updates to the frontend.
- Progress messages SHALL include agent-level status:
  - "Extracting document..."
  - "Identifying clauses..."
  - "Analyzing risks..."
  - "Generating summary..."
  - "Building report..."

### FR-10 — Contract History
- The system SHALL persist all analyzed contracts per user.
- The system SHALL provide a history view listing all user contracts with status and date.

### FR-11 — Contract Deletion
- The system SHALL allow authenticated users to delete their own contracts.
- Deletion SHALL cascade to all related analysis records.

### FR-12 — Authentication & Authorization
- The system SHALL enforce user authentication on all API endpoints.
- The system SHALL restrict contract access to the owning user only.

---

## 3. Non-Functional Requirements

### NFR-01 — Performance
- Contract analysis SHALL complete within 120 seconds for a standard 20-page contract.
- API endpoints SHALL respond within 2 seconds for non-analysis operations.

### NFR-02 — Security
- File uploads SHALL be validated for type (magic bytes + extension).
- File size SHALL be enforced server-side.
- All database queries SHALL use parameterized statements (no raw SQL).
- User-owned resource access SHALL be enforced at the service layer.

### NFR-03 — Reliability
- The system SHALL handle LLM failures with structured error responses (no unhandled exceptions).
- The system SHALL handle OCR/parsing failures per document with a per-file error state.

### NFR-04 — Maintainability
- Code SHALL follow PEP 8 (backend) and ESLint + Prettier (frontend).
- All agents SHALL be independently testable.
- Service layer SHALL be decoupled from the API layer.

### NFR-05 — Scalability (Capstone Scope Note)
- Architecture SHALL be designed to support horizontal scaling but single-instance deployment is acceptable for capstone.

---

## 4. Out of Scope (Capstone)

The following are explicitly out of scope for the 2-week implementation:

- OCR for scanned image-based PDFs
- Multi-language contract support
- Real-time collaboration / multi-user editing
- E-signature integration
- Export to Word or PDF report
- Email notifications
- Admin dashboard
- Role-based access control (RBAC) beyond basic auth
- Mobile application
- Automated clause negotiation suggestions

---

## 5. Success Criteria

| ID | Criterion | Measurable Target |
|---|---|---|
| SC-01 | Contract upload and storage | PDF and DOCX accepted, stored, status recorded |
| SC-02 | All 6 agents execute successfully | 100% of agent outputs returned without error |
| SC-03 | Clause identification coverage | Minimum 7 of 10 clause types detected in a standard NDA |
| SC-04 | Risk analysis output | Risk level assigned to every detected clause |
| SC-05 | Final report completeness | Report contains all 4 sections: summary, clauses, risks, metadata |
| SC-06 | Streaming works end-to-end | Frontend displays all 5 progress stages |
| SC-07 | History and retrieval | User can retrieve past analyses without re-running |
| SC-08 | Security enforcement | Non-owning user cannot access another user's contract via API |
| SC-09 | Error handling | Corrupt file returns structured error, not 500 |

---

## 6. Approval

| Reviewer | Status | Date |
|---|---|---|
| Project Owner | PENDING | — |

> **Once signed off, this document is FROZEN. Changes require a new version with changelog.**
