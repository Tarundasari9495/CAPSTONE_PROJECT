# DEPENDENCIES.md
# Contract Analysis Tool — Dependencies

> This document defines all external dependencies, their purpose, version constraints, and install order.
> All versions should be pinned in `requirements.txt` and `package.json` before implementation begins.

---

## 1. Backend Dependencies (Python)

### Core Framework

| Package | Version | Purpose |
|---|---|---|
| `fastapi` | `^0.111.0` | Web framework and API routing |
| `uvicorn[standard]` | `^0.30.0` | ASGI server for FastAPI |
| `pydantic` | `^2.7.0` | Data validation and settings management |
| `pydantic-settings` | `^2.3.0` | Environment variable configuration |
| `python-multipart` | `^0.0.9` | Multipart form data (file uploads) |

### Database

| Package | Version | Purpose |
|---|---|---|
| `sqlalchemy` | `^2.0.0` | ORM, async database access |
| `asyncpg` | `^0.29.0` | Async PostgreSQL driver |
| `alembic` | `^1.13.0` | Database migrations |
| `supabase` | `^2.4.0` | Supabase Python client |

### AI / LLM Orchestration

| Package | Version | Purpose |
|---|---|---|
| `langchain` | `^0.2.0` | LLM chain utilities and prompt templates |
| `langchain-openai` | `^0.1.0` | OpenAI integration for LangChain |
| `langchain-community` | `^0.2.0` | Community integrations (ChromaDB loader) |
| `langgraph` | `^0.1.0` | Multi-agent graph orchestration |
| `litellm` | `^1.40.0` | Unified LLM gateway / model abstraction |
| `openai` | `^1.30.0` | OpenAI Python SDK (embeddings + completions) |

### Vector Store & RAG

| Package | Version | Purpose |
|---|---|---|
| `chromadb` | `^0.5.0` | Local vector store for contract embeddings |
| `langchain-chroma` | `^0.1.0` | LangChain ChromaDB integration |

### Document Parsing

| Package | Version | Purpose |
|---|---|---|
| `PyMuPDF` | `^1.24.0` | PDF text extraction and page structure |
| `python-docx` | `^1.1.0` | DOCX file parsing |
| `python-magic` | `^0.4.27` | Magic byte file type validation |

### Authentication & Security

| Package | Version | Purpose |
|---|---|---|
| `python-jose[cryptography]` | `^3.3.0` | JWT creation and validation |
| `passlib[bcrypt]` | `^1.7.4` | Password hashing (if local auth used) |
| `cryptography` | `^42.0.0` | Cryptographic primitives |

### Utilities

| Package | Version | Purpose |
|---|---|---|
| `httpx` | `^0.27.0` | Async HTTP client (used by Supabase SDK) |
| `python-dotenv` | `^1.0.0` | `.env` file loading |
| `aiofiles` | `^23.2.0` | Async file I/O |

### Testing

| Package | Version | Purpose |
|---|---|---|
| `pytest` | `^8.2.0` | Test runner |
| `pytest-asyncio` | `^0.23.0` | Async test support |
| `httpx` | `^0.27.0` | HTTPX test client for FastAPI |
| `pytest-cov` | `^5.0.0` | Code coverage reporting |

---

## 2. Frontend Dependencies (Node.js)

### Core Framework

| Package | Version | Purpose |
|---|---|---|
| `react` | `^18.3.0` | UI library |
| `react-dom` | `^18.3.0` | React DOM rendering |
| `typescript` | `^5.4.0` | TypeScript language |
| `vite` | `^5.3.0` | Build tool and dev server |
| `@vitejs/plugin-react` | `^4.3.0` | Vite React plugin |

### Styling

| Package | Version | Purpose |
|---|---|---|
| `tailwindcss` | `^3.4.0` | Utility-first CSS framework |
| `postcss` | `^8.4.0` | CSS processing (required by Tailwind) |
| `autoprefixer` | `^10.4.0` | CSS vendor prefixing |

### Routing & State

| Package | Version | Purpose |
|---|---|---|
| `react-router-dom` | `^6.24.0` | Client-side routing |
| `@tanstack/react-query` | `^5.45.0` | Server state management and caching |

### HTTP & Streaming

| Package | Version | Purpose |
|---|---|---|
| `axios` | `^1.7.0` | HTTP client for API calls |

### UI Components & Utilities

| Package | Version | Purpose |
|---|---|---|
| `react-dropzone` | `^14.2.0` | Drag-and-drop file upload |
| `lucide-react` | `^0.400.0` | Icon library |
| `clsx` | `^2.1.0` | Conditional className utility |
| `tailwind-merge` | `^2.3.0` | Merge Tailwind classes without conflicts |

### Type Definitions

| Package | Version | Purpose |
|---|---|---|
| `@types/react` | `^18.3.0` | React TypeScript types |
| `@types/react-dom` | `^18.3.0` | React DOM types |
| `@types/node` | `^20.14.0` | Node.js types |

### Linting & Formatting

| Package | Version | Purpose |
|---|---|---|
| `eslint` | `^9.5.0` | JavaScript/TypeScript linting |
| `@typescript-eslint/eslint-plugin` | `^7.14.0` | TypeScript ESLint rules |
| `prettier` | `^3.3.0` | Code formatting |

---

## 3. Infrastructure Dependencies

| Tool | Version | Purpose |
|---|---|---|
| Python | `^3.11` | Backend runtime |
| Node.js | `^20.0` | Frontend runtime |
| PostgreSQL | `^15.0` | Relational database |
| ChromaDB | Embedded via `chromadb` package | Vector store |
| Docker | `^25.0` | Container runtime for local dev |
| Docker Compose | `^2.27.0` | Local service orchestration |

---

## 4. Dependency Graph

```
FastAPI Application
├── Pydantic v2           (validation)
├── SQLAlchemy            → asyncpg → PostgreSQL
├── Alembic               → SQLAlchemy (migrations)
├── Supabase SDK          → httpx → Supabase Cloud
├── FastAPI Auth          → python-jose (JWT)
│
├── LangGraph Workflow
│   ├── LangChain         → litellm → OpenAI API
│   ├── LangChain-OpenAI  → OpenAI SDK (embeddings)
│   ├── LangChain-Chroma  → ChromaDB (vectors)
│   └── Agents
│       ├── PyMuPDF       (PDF parsing)
│       └── python-docx   (DOCX parsing)
│
└── File Security
    └── python-magic      (file type validation)

React Frontend
├── Vite                  (build)
├── Tailwind CSS          (styling)
├── React Router          (routing)
├── TanStack Query        (server state)
├── Axios                 (HTTP)
└── React Dropzone        (file upload UX)
```

---

## 5. Installation Order

### Backend
```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install all backend dependencies
pip install -r requirements.txt

# 3. Verify LangGraph installed correctly
python -c "import langgraph; print(langgraph.__version__)"

# 4. Run database migrations
alembic upgrade head
```

### Frontend
```bash
# 1. Install Node dependencies
npm install

# 2. Verify TypeScript compilation
npx tsc --noEmit

# 3. Start dev server
npm run dev
```

### Local Services (Docker)
```bash
# Start PostgreSQL + ChromaDB (optional — can use Supabase cloud)
docker-compose up -d
```

---

## 6. Known Compatibility Notes

- **PyMuPDF** (`fitz`) requires `libmupdf` system libraries. On Docker, use `python:3.11-slim` and install via `apt-get install libmupdf-dev`.
- **python-magic** requires `libmagic1` on Linux/macOS. Windows users need `python-magic-bin` instead.
- **ChromaDB** v0.5+ changed its API; use `chromadb.PersistentClient` not the legacy `Client`.
- **LangGraph** `^0.1.0` has breaking changes from pre-release versions — pin to a specific minor.
- **Pydantic v2** is required; LangChain 0.2+ requires Pydantic v2 compatibility.
