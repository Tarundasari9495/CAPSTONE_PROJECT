# API Documentation
# Contract Analysis Tool — REST API Reference

**Base URL:** `http://localhost:8000/api/v1`
**Auth:** All contract endpoints require `Authorization: Bearer <jwt_token>`

---

## Authentication

### POST `/auth/token`
Issue a development test token.

**Request:**
```json
{ "user_id": "00000000-0000-0000-0000-000000000001" }
```
**Response 200:**
```json
{ "access_token": "eyJ...", "token_type": "bearer" }
```

---

## Contracts

### POST `/contracts/upload`
Upload a PDF or DOCX contract.

**Headers:** `Authorization: Bearer <token>`
**Body:** `multipart/form-data` — field `file`
**Constraints:** PDF or DOCX only, max 20 MB

**Response 201:**
```json
{
  "contract_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "file_name": "nda.pdf",
  "status": "pending"
}
```

**Error Responses:**
| Status | Error Code | Condition |
|---|---|---|
| 401 | `UNAUTHORIZED` | Missing or invalid JWT |
| 422 | `INVALID_FILE_TYPE` | File is not PDF or DOCX |
| 422 | `FILE_TOO_LARGE` | File exceeds 20 MB |
| 422 | `PARSE_ERROR` | File is corrupt/unreadable |

---

### POST `/contracts/analyze/{contract_id}`
Start contract analysis and stream progress via SSE.

**Headers:** `Authorization: Bearer <token>`
**Body:** `multipart/form-data` — field `file` (same file to parse)

**Response 200 — SSE Stream:**
```
data: {"stage": "extracting", "message": "Extracting document text..."}
data: {"stage": "clauses", "message": "Identifying clauses..."}
data: {"stage": "risks", "message": "Analyzing risks..."}
data: {"stage": "summary", "message": "Generating summary..."}
data: {"stage": "report", "message": "Building final report..."}
data: {"stage": "complete", "message": "Analysis complete.", "report": { ... }}
```

**Error Event:**
```
data: {"stage": "error", "message": "Analysis failed.", "error_code": "LLM_ERROR"}
```

---

### GET `/contracts/history`
Get all contracts belonging to the authenticated user.

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
[
  {
    "id": "uuid",
    "file_name": "nda.pdf",
    "upload_date": "2025-01-01T00:00:00Z",
    "status": "completed",
    "risk_score": 55
  }
]
```

---

### GET `/contracts/{contract_id}`
Get contract metadata.

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "id": "uuid",
  "file_name": "nda.pdf",
  "file_size": 204800,
  "file_type": "pdf",
  "upload_date": "2025-01-01T00:00:00Z",
  "status": "completed",
  "error_message": null
}
```

**Error Responses:**
| Status | Error Code | Condition |
|---|---|---|
| 403 | `FORBIDDEN` | Contract belongs to another user |
| 404 | `NOT_FOUND` | Contract does not exist |

---

### GET `/contracts/{contract_id}/analysis`
Get the full analysis report for a contract.

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "id": "uuid",
  "contract_id": "uuid",
  "summary": {
    "executive_summary": "...",
    "key_terms": "...",
    "important_obligations": ["..."],
    "important_dates": ["..."]
  },
  "contract_info": {
    "title": "Software License Agreement",
    "effective_date": "2025-01-01",
    "expiration_date": "2026-12-31",
    "parties": [
      {"name": "Acme Corp", "role": "Vendor"},
      {"name": "BetaCo", "role": "Client"}
    ],
    "contract_value": "$250,000",
    "renewal_terms": "Auto-renews unless cancelled"
  },
  "risk_score": 55,
  "clauses": [
    {
      "id": "uuid",
      "clause_type": "termination",
      "clause_text": "Either party may terminate...",
      "page_number": 2
    }
  ],
  "risks": [
    {
      "id": "uuid",
      "risk_level": "high",
      "risk_description": "Broad indemnification...",
      "clause_type": "indemnification",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "created_at": "2025-01-01T00:00:00Z"
}
```

**Error Responses:**
| Status | Error Code | Condition |
|---|---|---|
| 403 | `FORBIDDEN` | Contract belongs to another user |
| 404 | `NOT_FOUND` | Contract does not exist |
| 404 | `ANALYSIS_NOT_FOUND` | Analysis has not been run |

---

### DELETE `/contracts/{contract_id}`
Delete a contract and all associated analysis data.

**Headers:** `Authorization: Bearer <token>`

**Response 204:** No content

**Error Responses:**
| Status | Error Code | Condition |
|---|---|---|
| 403 | `FORBIDDEN` | Contract belongs to another user |
| 404 | `NOT_FOUND` | Contract does not exist |

---

## Error Response Format

All errors return:
```json
{
  "detail": {
    "error_code": "INVALID_FILE_TYPE",
    "message": "Only PDF and DOCX files are accepted."
  }
}
```

## Interactive Docs

Swagger UI: `http://localhost:8000/docs`
ReDoc: `http://localhost:8000/redoc`
OpenAPI JSON: `http://localhost:8000/openapi.json`
