# Contract Analysis Tool

> **AI-Forge 2026 — Capstone Project 9**
> A production-grade AI-powered contract analysis system using a 6-agent LangGraph workflow.

---

## Overview

The Contract Analysis Tool is a standalone full-stack application that accepts PDF and DOCX contracts and performs automated:

- **Document extraction** — parse text and structure from contracts
- **Clause identification** — detect 10 critical clause types
- **Risk analysis** — classify risk per clause with an overall risk score
- **Metadata extraction** — extract parties, dates, contract value
- **Summarization** — generate executive summary and key terms
- **Comprehensive report generation** — unified structured analysis report

The system uses a parallel **LangGraph multi-agent workflow**, **ChromaDB RAG** for contract-aware retrieval, and streams real-time progress to a **React + TypeScript** frontend.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0 async |
| AI Orchestration | LangGraph, LangChain |
| LLM Gateway | LiteLLM → OpenAI (GPT-4o) |
| Embeddings | OpenAI text-embedding-3-large |
| Vector Store | ChromaDB |
| Database | PostgreSQL via Supabase |
| Frontend | React 18, TypeScript, Tailwind CSS, Vite |
| Auth | JWT (Supabase Auth compatible) |

---

## Project Structure

```
multi-agent-contract-analyzer/
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── agents/    # 6 LangGraph agents
│   │   ├── workflows/ # LangGraph contract workflow
│   │   ├── services/  # Business logic + RAG
│   │   ├── routers/   # API endpoints
│   │   ├── models/    # SQLAlchemy ORM models
│   │   └── schemas/   # Pydantic schemas
│   └── tests/
├── frontend/          # React + Vite application
│   └── src/
│       ├── pages/     # Upload, History, Analysis Detail
│       ├── components/
│       └── services/  # API layer
└── docs/              # Architecture diagrams
```

See [SPEC.md](SPEC.md) for the complete project structure.

---

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (for local PostgreSQL)
- OpenAI API key
- Supabase project (or local PostgreSQL)

---

## Local Setup

### 1. Clone and Configure

```bash
git clone <repo-url>
cd multi-agent-contract-analyzer
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your API keys and database URL
```

### 3. Database Setup

```bash
# Option A: Use Docker for local PostgreSQL
docker-compose up -d db

# Option B: Use Supabase cloud (configure DATABASE_URL in .env)

# Run migrations
alembic upgrade head
```

### 4. Start Backend

```bash
uvicorn app.main:app --reload --port 8000
```

API docs available at: `http://localhost:8000/docs`

### 5. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
copy .env.example .env.local
# Set VITE_API_BASE_URL=http://localhost:8000/api/v1

# Start dev server
npm run dev
```

Frontend available at: `http://localhost:5173`

---

## Environment Variables

See `backend/.env.example` for all required variables.

**Required:**

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
OPENAI_API_KEY=sk-...
LITELLM_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-large
JWT_SECRET_KEY=<random-256-bit-secret>
```

---

## API Endpoints

| Method | Route | Description |
|---|---|---|
| `POST` | `/api/v1/contracts/upload` | Upload a PDF or DOCX contract |
| `POST` | `/api/v1/contracts/analyze/{id}` | Start analysis (SSE stream) |
| `GET` | `/api/v1/contracts/{id}` | Get contract metadata |
| `GET` | `/api/v1/contracts/{id}/analysis` | Get full analysis report |
| `GET` | `/api/v1/contracts/history` | Get user's contract history |
| `DELETE` | `/api/v1/contracts/{id}` | Delete a contract |

All endpoints require JWT authentication. See [docs/api.md](docs/api.md) for full specification.

---

## Multi-Agent Workflow

```
Upload → Extract → ┌─ Clause Agent ────┐
                   ├─ Risk Agent ───────┤ → Report Agent → DB
                   ├─ Data Agent ───────┤
                   └─ Summary Agent ────┘
```

Six specialized agents run in a LangGraph workflow with parallel execution for maximum performance.

---

## Running Tests

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=html
```

---

## Documentation

| Document | Purpose |
|---|---|
| [REQUIREMENTS.md](REQUIREMENTS.md) | Approved functional requirements (frozen) |
| [SPEC.md](SPEC.md) | Technical specification |
| [PLAN.md](PLAN.md) | 2-week day-by-day implementation plan |
| [DEPENDENCIES.md](DEPENDENCIES.md) | All package dependencies with versions |
| [CHECKPOINTS.md](CHECKPOINTS.md) | Daily testable checkpoints |
| [DELIVERABLES.md](DELIVERABLES.md) | Final submission checklist |
| [MVP_PREVIEW.md](MVP_PREVIEW.md) | What the completed product looks like |
| [FUTURE_VISION.md](FUTURE_VISION.md) | Post-capstone roadmap |
| [PROMPT_SEQUENCES.md](PROMPT_SEQUENCES.md) | Copilot prompt sequences for implementation |
| [docs/architecture.mmd](docs/architecture.mmd) | Mermaid architecture diagram |

---

## Important: Is This a Standalone Application?

**Yes.** This is a standalone new application — not an extension of any existing chatbot or platform project. It shares the same technology stack as the AI-Forge platform but is independently architected, deployed, and evaluated.

---

## License

Capstone project — AI-Forge 2026. Not for production distribution.
