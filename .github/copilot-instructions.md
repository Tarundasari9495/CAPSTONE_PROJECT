---
applyTo: "d:/CAPSTONE/AI/Multi-Agent-Contract-Analyzer/**"
---

# GitHub Copilot Instructions
# Contract Analysis Tool — AI-Forge 2026 Capstone Project 9

## Project Identity

You are assisting with the **Contract Analysis Tool** — a standalone capstone project.
This is NOT an extension of any existing codebase. It is a new application.

---

## HARD RULES — Always Enforce

### 1. Scope Enforcement
- `REQUIREMENTS.md` is FROZEN after approval. Do NOT suggest or generate features outside it.
- If asked to implement something not in `REQUIREMENTS.md`, respond:
  > "This feature is not in the approved requirements. It can be added to FUTURE_VISION.md for post-capstone consideration."
- Explicitly out of scope (do not generate):
  - OCR for scanned PDFs
  - Multi-language support
  - Contract comparison
  - E-signature
  - Email notifications
  - PDF/Word export
  - Admin dashboard
  - RBAC
  - Mobile app

### 2. No Hardcoded Secrets
- NEVER hardcode API keys, database URLs, passwords, or JWT secrets.
- ALL configuration must come from environment variables via `app/config.py`.
- Check `.env.example` for the list of required variables.

### 3. Specification Alignment
- All generated code must conform to `SPEC.md`.
- Database schemas must match `SPEC.md Section 3` exactly.
- API responses must match `SPEC.md Section 4` exactly.
- Agent output structures must match `SPEC.md Section 5` exactly.

### 4. No Over-Engineering
- Do not add features "just in case."
- Do not add abstractions for one-time operations.
- Do not add extra error handling for impossible scenarios.
- Do not add comments, docstrings, or type annotations to code you didn't change.

---

## Architecture Rules

### Backend
- Use **FastAPI** with async/await throughout.
- Use **SQLAlchemy 2.0 async** — never synchronous SQLAlchemy.
- Use **Pydantic v2** for all schemas and settings.
- Use **Alembic** for all database migrations — never modify tables manually.
- All business logic lives in `services/` — not in routers.
- Routers only validate input and delegate to services.

### LangGraph
- Every agent is a standalone `async def node(state: ContractAnalysisState)` function.
- Agents must NOT share mutable state outside the `ContractAnalysisState`.
- Agent failures must NOT crash the graph — add to `agent_errors`, return safe default.
- The workflow graph is compiled once at module level as `contract_graph`.
- Parallel fan-out uses LangGraph's native parallel node execution.

### RAG
- ChromaDB collections are named `contract_{contract_id}`.
- Use `PersistentClient` — not legacy `Client`.
- Chunk size: 1000 tokens, overlap: 200 tokens (do not change without updating SPEC.md).

### Frontend
- All API calls go through `services/api.ts` — no inline `fetch()` or `axios` calls in components.
- SSE streaming is handled via the native `EventSource` API.
- All TypeScript types are defined in `types/contract.ts`.
- Use TanStack Query for all data fetching — no raw useEffect for API calls.

---

## Security Rules

- File uploads: ALWAYS validate with magic bytes (python-magic) AND extension whitelist.
- ALWAYS enforce ownership: check `contract.user_id == current_user.id` before returning data.
- NEVER return another user's contract data.
- CORS is restricted to `ALLOWED_ORIGINS` from config — no wildcard `*` in production.
- All database operations use SQLAlchemy ORM — no raw SQL strings.

---

## Error Handling Rules

- Use the error codes from `SPEC.md Section 9` exactly.
- Return `HTTPException` with the correct status code and `detail` as `{"error_code": "...", "message": "..."}`.
- LLM failures return HTTP 503 with `LLM_ERROR`.
- Parse failures return HTTP 422 with `PARSE_ERROR`.
- Ownership failures return HTTP 403 with `FORBIDDEN`.

---

## Testing Rules

- Every new agent must have a corresponding unit test in `tests/test_agents.py`.
- Every new API route must have a corresponding integration test in `tests/test_routes.py`.
- LLM calls in tests must be mocked — never make real API calls in tests.
- Use `pytest-asyncio` for all async tests.
- Target: minimum 60% test coverage.

---

## Code Style Rules

### Python
- Follow PEP 8.
- Use type hints on all function signatures.
- Use `async def` for all I/O-bound functions.
- Imports: stdlib → third-party → local, separated by blank lines.

### TypeScript / React
- Use functional components only (no class components).
- Use TypeScript interfaces, not `any`.
- Use named exports (not default exports) for components.
- Keep components under 150 lines — split if larger.

---

## Prompt Usage

When generating code, the developer will provide prompts from `PROMPT_SEQUENCES.md`.
Follow those prompts precisely. If the prompt conflicts with this file, this file takes precedence.

---

## Daily Development Workflow

1. Check today's task in `PLAN.md`.
2. Verify today's checkpoint criteria in `CHECKPOINTS.md`.
3. Use the relevant prompt from `PROMPT_SEQUENCES.md`.
4. Generate code.
5. Verify against `SPEC.md`.
6. Run tests.
7. Mark checkpoint complete.

---

## What Copilot Should NOT Do

- Do NOT suggest adding a new database table not in `SPEC.md Section 3`.
- Do NOT suggest a new API endpoint not in `SPEC.md Section 4`.
- Do NOT suggest a new agent not in `SPEC.md Section 5`.
- Do NOT suggest upgrading or downgrading package versions without checking `DEPENDENCIES.md`.
- Do NOT generate frontend pages not listed in `REQUIREMENTS.md Section FR-10 to FR-12` and `SPEC.md Section 2`.
- Do NOT generate Docker deployment, CI/CD pipelines, or infrastructure-as-code unless explicitly requested.
