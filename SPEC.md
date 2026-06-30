# SPEC.md
# Contract Analysis Tool — Technical Specification

> This document is the authoritative technical reference for the implementation.
> All code, schema, and API design must conform to this specification.

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                            │
│         React + TypeScript + Tailwind CSS + Vite            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Upload Page  │  │ History Page │  │  Analysis Detail │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
└─────────┼─────────────────┼───────────────────┼────────────┘
          │   HTTP/SSE      │                   │
┌─────────▼─────────────────▼───────────────────▼────────────┐
│                          BACKEND                            │
│                    FastAPI (Python)                         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  Contracts  │  │   Analysis   │  │     Auth/Users    │  │
│  │   Router    │  │    Router    │  │      Router       │  │
│  └──────┬──────┘  └──────┬───────┘  └────────┬──────────┘  │
│         └────────────────┼───────────────────┘             │
│                    ┌─────▼──────┐                           │
│                    │  Services  │                           │
│                    └─────┬──────┘                           │
│         ┌────────────────┼───────────────────┐             │
│    ┌────▼────┐    ┌──────▼──────┐    ┌───────▼──────┐      │
│    │LangGraph│    │  RAG Layer  │    │  DB Layer    │      │
│    │Workflow │    │  (ChromaDB) │    │  (Supabase)  │      │
│    └────┬────┘    └─────────────┘    └──────────────┘      │
│    ┌────▼──────────────────────────────────────────────┐   │
│    │                  LiteLLM Gateway                  │   │
│    │           (OpenAI / model abstraction)            │   │
│    └───────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Project Structure

```
multi-agent-contract-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── contract.py
│   │   │   ├── analysis.py
│   │   │   ├── clause.py
│   │   │   └── risk.py
│   │   ├── schemas/
│   │   │   ├── contract.py
│   │   │   ├── analysis.py
│   │   │   ├── clause.py
│   │   │   └── risk.py
│   │   ├── routers/
│   │   │   ├── contracts.py
│   │   │   └── auth.py
│   │   ├── services/
│   │   │   ├── contract_service.py
│   │   │   ├── analysis_service.py
│   │   │   └── rag/
│   │   │       ├── contract_chunker.py
│   │   │       ├── contract_embeddings.py
│   │   │       └── contract_retriever.py
│   │   ├── agents/
│   │   │   ├── extraction_agent.py
│   │   │   ├── clause_agent.py
│   │   │   ├── risk_agent.py
│   │   │   ├── data_extraction_agent.py
│   │   │   ├── summary_agent.py
│   │   │   └── report_agent.py
│   │   ├── workflows/
│   │   │   └── contract_workflow.py
│   │   └── utils/
│   │       ├── file_parser.py
│   │       └── security.py
│   ├── tests/
│   │   ├── fixtures/
│   │   │   └── sample_nda.pdf
│   │   ├── test_agents.py
│   │   ├── test_routes.py
│   │   └── test_rag.py
│   ├── alembic/
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── UploadPage.tsx
│   │   │   ├── HistoryPage.tsx
│   │   │   └── AnalysisDetailPage.tsx
│   │   ├── components/
│   │   │   ├── ContractUpload/
│   │   │   ├── AnalysisReport/
│   │   │   ├── ClauseTable/
│   │   │   ├── RiskBadge/
│   │   │   ├── StreamingProgress/
│   │   │   └── ContractHistory/
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── types/
│   │   │   └── contract.ts
│   │   └── hooks/
│   │       └── useContractAnalysis.ts
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── tsconfig.json
├── docs/
│   ├── architecture.mmd
│   └── api.md
├── docker-compose.yml
└── README.md
```

---

## 3. Database Schema

### Table: `contracts`
```sql
CREATE TABLE contracts (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    file_name   VARCHAR(255) NOT NULL,
    file_size   INTEGER NOT NULL,
    file_type   VARCHAR(10) NOT NULL CHECK (file_type IN ('pdf', 'docx')),
    upload_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status      VARCHAR(20) NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    error_message TEXT
);
```

### Table: `contract_analysis`
```sql
CREATE TABLE contract_analysis (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id     UUID NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    summary         JSONB,
    contract_info   JSONB,
    risk_score      INTEGER CHECK (risk_score BETWEEN 0 AND 100),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (contract_id)
);
```

### Table: `contract_clauses`
```sql
CREATE TABLE contract_clauses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id     UUID NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    clause_type     VARCHAR(50) NOT NULL,
    clause_text     TEXT NOT NULL,
    page_number     INTEGER
);
```

### Table: `contract_risks`
```sql
CREATE TABLE contract_risks (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id         UUID NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    risk_level          VARCHAR(10) NOT NULL CHECK (risk_level IN ('high', 'medium', 'low')),
    risk_description    TEXT NOT NULL,
    clause_type         VARCHAR(50),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 4. API Specification

### Base URL: `/api/v1`

#### POST `/contracts/upload`
- **Auth**: Required
- **Body**: `multipart/form-data` — field: `file`
- **Validates**: file type (PDF/DOCX), file size (≤ 20 MB)
- **Response 201**:
  ```json
  { "contract_id": "uuid", "file_name": "contract.pdf", "status": "pending" }
  ```
- **Response 422**: Invalid file type or size

#### POST `/contracts/analyze/{contract_id}`
- **Auth**: Required (must own contract)
- **Response 200**: SSE stream of analysis progress + final report
- **Stream events**:
  ```
  data: {"stage": "extracting", "message": "Extracting document text..."}
  data: {"stage": "clauses", "message": "Identifying clauses..."}
  data: {"stage": "risks", "message": "Analyzing risks..."}
  data: {"stage": "summary", "message": "Generating summary..."}
  data: {"stage": "report", "message": "Building final report..."}
  data: {"stage": "complete", "report": { ... }}
  ```

#### GET `/contracts/{contract_id}`
- **Auth**: Required (must own contract)
- **Response 200**: Contract metadata record

#### GET `/contracts/{contract_id}/analysis`
- **Auth**: Required (must own contract)
- **Response 200**: Full analysis report (summary, clauses, risks, contract_info)
- **Response 404**: Analysis not yet run

#### GET `/contracts/history`
- **Auth**: Required
- **Response 200**: Array of user's contracts with status and risk score

#### DELETE `/contracts/{contract_id}`
- **Auth**: Required (must own contract)
- **Response 204**: No content (cascade delete)

---

## 5. LangGraph Agent Specification

### State Schema
```python
class ContractAnalysisState(TypedDict):
    contract_id: str
    document_text: str
    page_count: int
    document_metadata: dict
    clauses: list[dict]
    risks: list[dict]
    contract_information: dict
    summary: dict
    final_report: dict
    error: Optional[str]
```

### Workflow Graph
```
document_extraction_node
        │
        ▼
   parallel_fan_out
   ┌────┬────┬─────┐
   ▼    ▼    ▼     ▼
clause risk  data  summary
agent  agent extr. agent
   └────┴────┴─────┘
        │
        ▼
  report_assembly_node
        │
        ▼
  db_persistence_node
```

### Agent Output Contracts

**Extraction Agent Output**
```json
{
  "document_text": "string",
  "page_count": 0,
  "metadata": { "author": "", "created_at": "" }
}
```

**Clause Agent Output**
```json
{
  "clauses": [
    { "clause_type": "termination", "clause_text": "...", "page_number": 3 }
  ]
}
```

**Risk Agent Output**
```json
{
  "risks": [
    {
      "risk_level": "high",
      "risk_description": "...",
      "clause_type": "indemnification"
    }
  ],
  "overall_risk_score": 67
}
```

**Data Extraction Agent Output**
```json
{
  "contract_information": {
    "title": "...",
    "effective_date": "...",
    "expiration_date": "...",
    "parties": [],
    "contract_value": null,
    "renewal_terms": "..."
  }
}
```

**Summary Agent Output**
```json
{
  "summary": {
    "executive_summary": "...",
    "key_terms": "...",
    "important_obligations": [],
    "important_dates": []
  }
}
```

**Final Report Agent Output**
```json
{
  "summary": {},
  "clauses": [],
  "risks": [],
  "contract_information": {}
}
```

---

## 6. RAG Specification

| Parameter | Value |
|---|---|
| Chunking strategy | Recursive character splitter |
| Chunk size | 1000 tokens |
| Chunk overlap | 200 tokens |
| Embedding model | `text-embedding-3-large` (OpenAI) |
| Vector store | ChromaDB (local persistent) |
| Collection name | `contract_{contract_id}` |
| Retrieval top-k | 5 |
| Metadata per chunk | `contract_id`, `page_number`, `chunk_index` |

---

## 7. Environment Variables

```env
# Backend
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
OPENAI_API_KEY=sk-...
LITELLM_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-large
CHROMA_PERSIST_DIR=./chroma_db
MAX_FILE_SIZE_MB=20
JWT_SECRET_KEY=<random-256-bit-key>
JWT_ALGORITHM=HS256
ALLOWED_ORIGINS=http://localhost:5173

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 8. Security Specification

| Concern | Implementation |
|---|---|
| File type validation | Magic byte check (python-magic) + extension whitelist |
| File size limit | Server-side check before processing begins |
| SQL injection | SQLAlchemy ORM only — no raw SQL |
| Auth on all routes | Depends on FastAPI `get_current_user` dependency |
| Resource ownership | Service layer checks `user_id == contract.user_id` |
| CORS | Restricted to `ALLOWED_ORIGINS` config |
| Secrets | All via environment variables — never hardcoded |

---

## 9. Error Handling Specification

| Scenario | HTTP Status | Error Code | Message |
|---|---|---|---|
| Invalid file type | 422 | `INVALID_FILE_TYPE` | "Only PDF and DOCX files are accepted." |
| File too large | 422 | `FILE_TOO_LARGE` | "File exceeds maximum size of 20 MB." |
| Corrupt PDF | 422 | `PARSE_ERROR` | "Document could not be parsed." |
| Empty document | 422 | `EMPTY_DOCUMENT` | "Document contains no extractable text." |
| LLM failure | 503 | `LLM_ERROR` | "AI analysis service temporarily unavailable." |
| Contract not found | 404 | `NOT_FOUND` | "Contract not found." |
| Unauthorized access | 403 | `FORBIDDEN` | "Access denied." |
| Analysis not run | 404 | `ANALYSIS_NOT_FOUND` | "Analysis has not been run for this contract." |
