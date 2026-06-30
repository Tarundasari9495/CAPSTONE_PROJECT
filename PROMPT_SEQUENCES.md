# PROMPT_SEQUENCES.md
# Contract Analysis Tool — Copilot Prompt Sequences

> This document provides the exact prompt sequences to use with GitHub Copilot (or any AI assistant)
> during implementation. Following these sequences ensures consistent, specification-aligned code generation.
>
> **Rule:** Always provide the relevant section of SPEC.md as context when prompting.

---

## How to Use This Document

1. When starting any implementation session, open this file.
2. Find the prompt sequence for the component you are building.
3. Use the prompt **exactly as written**, substituting `[CONTEXT]` placeholders with the referenced spec sections.
4. After generation, validate the output against the spec before accepting.

---

## Sequence 1 — Project Bootstrap

### Prompt 1.1 — Backend Project Structure
```
I am building a Contract Analysis Tool. Create the FastAPI project structure as defined in SPEC.md Section 2.

Requirements:
- Use FastAPI with async support
- Use SQLAlchemy 2.0 async
- Use Pydantic v2 for settings
- Use Alembic for migrations
- Configure CORS for ALLOWED_ORIGINS from .env
- Add a lifespan event handler for startup/shutdown
- Add GET /health endpoint

Do not generate any agent or analysis code yet. Only scaffold the base app.
```

### Prompt 1.2 — Database Models
```
Using the database schema in SPEC.md Section 3, generate SQLAlchemy 2.0 ORM models for:
- contracts
- contract_analysis
- contract_clauses
- contract_risks

Requirements:
- Use async-compatible declarative base
- Use UUID primary keys (server-generated)
- Use proper relationships with cascade delete
- Include all columns and constraints exactly as specified
```

### Prompt 1.3 — Alembic Migration
```
Generate an Alembic initial migration script that creates the following tables in order:
1. contracts
2. contract_analysis
3. contract_clauses
4. contract_risks

Use the exact SQL definitions from SPEC.md Section 3.
Include both upgrade() and downgrade() functions.
```

---

## Sequence 2 — Authentication

### Prompt 2.1 — JWT Auth Middleware
```
Implement JWT authentication for FastAPI using python-jose.

Requirements:
- Read JWT_SECRET_KEY and JWT_ALGORITHM from environment config
- Create a get_current_user dependency that:
  1. Reads the Authorization: Bearer <token> header
  2. Decodes and validates the JWT
  3. Returns the user_id from the token payload
  4. Raises HTTP 401 if token is missing or invalid
- Do not implement login/register — use Supabase for that
```

### Prompt 2.2 — Ownership Guard
```
Implement a reusable service function called verify_contract_ownership(contract_id, user_id, db) that:
- Queries the contracts table for the given contract_id
- Raises HTTP 404 if the contract does not exist
- Raises HTTP 403 if contract.user_id != user_id
- Returns the contract object if ownership is confirmed

Use SQLAlchemy 2.0 async session.
```

---

## Sequence 3 — File Upload

### Prompt 3.1 — Upload Endpoint
```
Implement POST /api/v1/contracts/upload in FastAPI.

Requirements from SPEC.md Section 4:
- Accept multipart/form-data with a 'file' field
- Validate file type using python-magic (magic bytes) — allow only PDF and DOCX
- Validate file size server-side — reject files over MAX_FILE_SIZE_MB
- Store contract record in the contracts table with status='pending'
- Associate the contract with the authenticated user (from get_current_user)
- Return: { contract_id, file_name, status } with HTTP 201
- Return structured errors as defined in SPEC.md Section 9
```

### Prompt 3.2 — File Validator Utility
```
Implement a file validation utility in app/utils/security.py:

validate_file(file: UploadFile) -> None:
- Check file extension against whitelist: ['.pdf', '.docx']
- Check magic bytes using python-magic to confirm actual file type
- Check file size against MAX_FILE_SIZE_MB config
- Raise HTTPException with appropriate error codes for each failure case
  (see SPEC.md Section 9 for error codes and messages)
```

---

## Sequence 4 — Document Parsing

### Prompt 4.1 — File Parser Utility
```
Implement app/utils/file_parser.py with two functions:

parse_pdf(file_bytes: bytes) -> dict:
- Use PyMuPDF (fitz) to extract text from all pages
- Preserve page boundaries in output
- Extract metadata: author, creation date if available
- Return: { document_text: str, page_count: int, metadata: dict }
- Raise a ParseError if the file is corrupt or unreadable

parse_docx(file_bytes: bytes) -> dict:
- Use python-docx to extract all paragraph text
- Return: { document_text: str, page_count: None, metadata: dict }
- Raise a ParseError if the file is corrupt or unreadable
```

---

## Sequence 5 — LangGraph Agents

### Prompt 5.1 — State Schema
```
Define the LangGraph state schema for the contract analysis workflow.

Use TypedDict as defined in SPEC.md Section 5:
- ContractAnalysisState with all fields
- All fields should be Optional where appropriate (parallel agents populate them)
- Add a field: agent_errors: list[str] to collect per-agent failures without crashing the graph
```

### Prompt 5.2 — Extraction Agent
```
Implement the Document Extraction Agent in agents/extraction_agent.py.

This is a LangGraph node function: async def extraction_node(state: ContractAnalysisState) -> ContractAnalysisState

Requirements:
- Call the file_parser utility based on file_type in state
- Populate: document_text, page_count, document_metadata
- On parse failure: add error to agent_errors, set document_text to empty string
- Do NOT call any LLM in this agent
```

### Prompt 5.3 — Clause Identification Agent
```
Implement the Clause Identification Agent in agents/clause_agent.py.

This is a LangGraph node function: async def clause_node(state: ContractAnalysisState) -> ContractAnalysisState

Requirements:
- Use LiteLLM to call the configured LLM model
- Build a prompt that instructs the LLM to identify these clause types:
  Termination, Liability, Confidentiality, Indemnification, Payment Terms,
  Renewal, Governing Law, Intellectual Property, Non-Compete, Force Majeure
- Use the document_text from state (or RAG-retrieved chunks if available)
- Parse LLM JSON response using Pydantic
- Output conforms to SPEC.md Section 5 Clause Agent Output
- On LLM failure: add error to agent_errors, set clauses to []
```

### Prompt 5.4 — Risk Analysis Agent
```
Implement the Risk Analysis Agent in agents/risk_agent.py.

This is a LangGraph node function: async def risk_node(state: ContractAnalysisState) -> ContractAnalysisState

Requirements:
- Takes clauses from state as input context
- Build a prompt that assesses each clause for: High/Medium/Low risk
- Identify missing critical clauses (from the 10-clause list) as Medium risk signals
- Calculate an overall_risk_score (0-100) based on risk distribution
- Output conforms to SPEC.md Section 5 Risk Agent Output
- On LLM failure: add error to agent_errors, set risks to []
```

### Prompt 5.5 — Data Extraction Agent
```
Implement the Contract Data Extraction Agent in agents/data_extraction_agent.py.

This is a LangGraph node function: async def data_extraction_node(state: ContractAnalysisState) -> ContractAnalysisState

Requirements:
- Extract structured contract metadata from document_text
- Fields: title, effective_date, expiration_date, parties, contract_value, renewal_terms
- Use LiteLLM with a structured extraction prompt
- Output conforms to SPEC.md Section 5 Data Extraction Agent Output
- On LLM failure: add error to agent_errors, set contract_information to {}
```

### Prompt 5.6 — Summary Agent
```
Implement the Contract Summary Agent in agents/summary_agent.py.

This is a LangGraph node function: async def summary_node(state: ContractAnalysisState) -> ContractAnalysisState

Requirements:
- Generate a human-readable contract summary
- Sections: executive_summary, key_terms, important_obligations, important_dates
- Use LiteLLM
- Output conforms to SPEC.md Section 5 Summary Agent Output
- On LLM failure: add error to agent_errors, set summary to {}
```

### Prompt 5.7 — Final Report Agent
```
Implement the Final Report Agent in agents/report_agent.py.

This is a LangGraph node function: async def report_node(state: ContractAnalysisState) -> ContractAnalysisState

Requirements:
- Merge outputs from clause_node, risk_node, data_extraction_node, summary_node
- Assemble the final_report field: { summary, clauses, risks, contract_information }
- Output conforms to SPEC.md Section 5 Final Report Agent Output
- This agent does NOT call an LLM — it only assembles and validates the output
```

### Prompt 5.8 — LangGraph Workflow
```
Implement the complete LangGraph workflow in workflows/contract_workflow.py.

Requirements from SPEC.md Section 5 Workflow Graph:
- Start node: extraction_node
- After extraction: fan out in parallel to: clause_node, risk_node, data_extraction_node, summary_node
- After all parallel nodes complete: fan in to report_node
- After report_node: db_persistence_node (persists final report to PostgreSQL)
- Use StateGraph with ContractAnalysisState
- Add conditional edge: if document_text is empty after extraction, skip to error node
- Return the compiled graph as a module-level 'contract_graph' object
```

---

## Sequence 6 — RAG

### Prompt 6.1 — Contract Chunker
```
Implement app/services/rag/contract_chunker.py.

Function: chunk_contract(document_text: str, contract_id: str) -> list[dict]

Requirements from SPEC.md Section 6:
- Use LangChain RecursiveCharacterTextSplitter
- Chunk size: 1000 tokens, overlap: 200 tokens
- Each chunk dict: { text: str, contract_id: str, chunk_index: int }
- Return list of chunk dicts
```

### Prompt 6.2 — Contract Embeddings
```
Implement app/services/rag/contract_embeddings.py.

Function: embed_and_store(chunks: list[dict], contract_id: str) -> None

Requirements from SPEC.md Section 6:
- Use OpenAI text-embedding-3-large via LangChain-OpenAI
- Store embeddings in ChromaDB using PersistentClient
- Collection name: f"contract_{contract_id}"
- Store metadata per chunk: contract_id, chunk_index
- Use CHROMA_PERSIST_DIR from config
```

### Prompt 6.3 — Contract Retriever
```
Implement app/services/rag/contract_retriever.py.

Function: retrieve_relevant_chunks(query: str, contract_id: str, top_k: int = 5) -> list[dict]

Requirements from SPEC.md Section 6:
- Query ChromaDB collection f"contract_{contract_id}"
- Return top_k most similar chunks
- Each result: { text: str, chunk_index: int, score: float }
```

---

## Sequence 7 — Frontend

### Prompt 7.1 — API Service Layer
```
Implement frontend/src/services/api.ts.

Requirements:
- Use axios with a configured base URL from VITE_API_BASE_URL
- Add a request interceptor that attaches the JWT from localStorage as Authorization: Bearer
- Export typed functions for each API endpoint from SPEC.md Section 4:
  uploadContract(file: File): Promise<ContractUploadResponse>
  analyzeContract(contractId: string): EventSource  (returns SSE stream)
  getContractAnalysis(contractId: string): Promise<AnalysisReport>
  getContractHistory(): Promise<Contract[]>
  deleteContract(contractId: string): Promise<void>
- Use TypeScript types from types/contract.ts
```

### Prompt 7.2 — TypeScript Types
```
Implement frontend/src/types/contract.ts.

Define TypeScript interfaces that match SPEC.md Section 5 agent output contracts:
- Contract
- ContractUploadResponse
- AnalysisReport
- Clause
- Risk
- ContractInformation
- Summary
- ProgressEvent (for SSE streaming)
```

### Prompt 7.3 — Upload Page
```
Implement frontend/src/pages/UploadPage.tsx.

Requirements:
- Use react-dropzone for drag-and-drop
- Accept only .pdf and .docx files
- Enforce 20 MB client-side size limit
- Show file name and size after selection
- "Analyze Contract" button calls uploadContract() then analyzeContract()
- On success: navigate to analysis detail page
- On error: display structured error message from API
- Style with Tailwind CSS
```

### Prompt 7.4 — Streaming Progress Component
```
Implement frontend/src/components/StreamingProgress/StreamingProgress.tsx.

Requirements:
- Accept an EventSource as a prop
- Render a list of 5 stages: extracting, clauses, risks, summary, report
- Each stage shows: spinner (in-progress), checkmark (complete), waiting (not started)
- Update in real-time as SSE events arrive
- On stream complete: call onComplete(report) callback prop
- On stream error: call onError(message) callback prop
```

---

## Sequence 8 — Testing

### Prompt 8.1 — Agent Unit Tests
```
Write pytest unit tests for all 6 agents in tests/test_agents.py.

Requirements:
- Mock the LLM calls using unittest.mock
- Test each agent with a sample NDA text (use the fixture text provided below)
- Test happy path: agent returns correct output structure
- Test failure path: LLM throws exception → agent adds to agent_errors, returns safe default
- Use pytest-asyncio for async tests
```

### Prompt 8.2 — API Integration Tests
```
Write pytest integration tests for all API routes in tests/test_routes.py.

Requirements:
- Use httpx.AsyncClient with FastAPI test app
- Test: upload → valid file returns 201
- Test: upload → invalid file type returns 422 with error code INVALID_FILE_TYPE
- Test: upload → file too large returns 422 with error code FILE_TOO_LARGE
- Test: get analysis → other user's contract returns 403
- Test: delete → removes contract and cascades
- Mock database and auth dependencies for isolation
```

---

## Validation Checklist (Post-Prompt)

After generating any component, verify:

- [ ] Output structure matches SPEC.md (types, field names, nullability)
- [ ] No hardcoded values (model names, API keys, URLs)
- [ ] Error handling follows SPEC.md Section 9 (status codes and error codes)
- [ ] No features outside the approved REQUIREMENTS.md scope
- [ ] Async/await used correctly throughout
