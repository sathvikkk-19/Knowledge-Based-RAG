# Knowledge-Based RAG (Hybrid Graph & Vector Retrieval-Augmented Generation)

An enterprise-grade **Hybrid Knowledge Graph & Vector RAG** system that combines **Neo4j**, **PostgreSQL (pgvector)**, and **Google Gemini** to deliver accurate, context-rich, and verifiable answers across multi-format documents.

---

## 🌟 Key Features

- **Multi-Format Document Ingestion:**
  - Upload and parse **PDF** (`.pdf`), **Word** (`.docx`, `.doc`), **CSV** (`.csv`), **Excel** (`.xlsx`, `.xls`), **PowerPoint** (`.pptx`, `.ppt`), and **Plain Text / Markdown** (`.txt`, `.md`).
- **Knowledge Graph Construction (Neo4j):**
  - Extracts entities and relationships via LLM query routing.
  - Resolves duplicate and aliased entities canonically using sequence-matching heuristics.
  - Builds directed relational paths with confidence scoring.
- **Fast & Secure Vector Embeddings (pgvector + fastembed):**
  - Uses `fastembed` (Microsoft ONNX Runtime) with `sentence-transformers/all-MiniLM-L6-v2` generating 384-dimensional embeddings.
  - Native Windows 11 Smart App Control compatibility without PyTorch DLL blocks.
  - Stores chunk embeddings with HNSW cosine indexing in PostgreSQL `pgvector`.
- **Intelligent Hybrid Query Routing:**
  - Dynamically classifies user questions (`vector`, `graph`, or `both`) to combine structured graph traversal with semantic similarity.
- **Modern Interactive UI (React + Vite):**
  - Drag-and-drop document upload with 3-stage live ingestion tracker.
  - Document-scoped querying or global knowledge search.
  - Visual display of knowledge graph evidence paths and source text chunks.

---

## 🏗️ Architecture

```
User Question / Document Upload
              │
              ▼
       FastAPI Backend
       ├── Document Ingestor
       │   ├── Multi-format Loader (PDF, DOCX, CSV, XLSX, PPTX, TXT)
       │   ├── Recursive Character Chunker
       │   ├── Entity & Relation Extractor (LLM Router)
       │   ├── Canonical Entity Resolver
       │   ├── Neo4j Graph Writer
       │   └── FastEmbed Vector Generator (384-dim)
       │
       └── Hybrid Retriever & Generator
           ├── Router (Classifies query type: Graph vs Vector vs Both)
           ├── Neo4j Graph Traversal (multi-hop relation paths)
           ├── pgvector Similarity Search (HNSW cosine similarity)
           └── Gemini Answer Synthesis (with citations & graph evidence)
              │
              ▼
   React + Vite Modern Frontend
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Desktop (for Neo4j and PostgreSQL)

---

### 2. Start Databases

Start Neo4j and PostgreSQL with `pgvector`:

```bash
docker compose up -d
```

- **Neo4j Browser:** [http://localhost:7474](http://localhost:7474) (Auth: `neo4j` / `password123`)
- **PostgreSQL:** `localhost:5432` (`kgrag` / `password123`)

---

### 3. Setup Environment Variables

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password123

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=kgrag
POSTGRES_USER=kgrag
POSTGRES_PASSWORD=password123

GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

---

### 4. Run Backend Server

In your first terminal:

```powershell
# Activate virtual environment (if using PowerShell)
.\venv\Scripts\Activate.ps1

# Run FastAPI backend
.\venv\Scripts\python -m uvicorn app.api:app --reload --host 127.0.0.1 --port 8000
```

- **API Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### 5. Run Frontend UI

In your second terminal:

```powershell
cd frontend
npm.cmd run dev
```

- **Frontend App:** [http://localhost:5173](http://localhost:5173)

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload` | Multipart upload for `.pdf`, `.docx`, `.csv`, `.xlsx`, `.pptx`, `.txt` |
| `GET` | `/documents` | Lists all ingested documents and chunk counts |
| `POST` | `/query` | Hybrid query with optional `document_id` scope filter |
| `GET` | `/health` | Health check |

---

## 🧪 Testing

Run the automated test suite:

```bash
.\venv\Scripts\python tests/test_multi_format_upload.py
```

---

## 📄 License

MIT License.
