import os
import shutil
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.ingestion.loader import SUPPORTED_EXTENSIONS
from app.ingestion.pipeline import DocumentIngestor
from app.llm.answer_generator import AnswerGenerator
from app.retrieval.hybrid_retriever import HybridRetriever
from app.vector.pgvector_store import PgVectorStore


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Hybrid Graph RAG API",
    description="Multi-format Document Ingestion and Hybrid RAG using Neo4j, pgvector and Gemini",
    version="2.0.0",
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST / RESPONSE MODELS
# ============================================================

class QueryRequest(BaseModel):
    question: str
    document_id: str | None = None


class QueryResponse(BaseModel):
    question: str
    answer: str
    route: str
    query_type: str
    confidence: float
    entities: list[str]
    sources: list[str]
    graph_evidence: list[dict]
    document_id: str | None = None


class UploadResponse(BaseModel):
    status: str
    document_id: str
    file_name: str
    char_count: int
    chunk_count: int
    entity_count: int
    relationship_count: int
    sample_entities: list[str]
    message: str


class DocumentItem(BaseModel):
    document_id: str
    chunk_count: int


# Directory for uploaded files
UPLOADS_DIR = Path("data/uploads")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# ROOT & HEALTH ENDPOINTS
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Hybrid Graph RAG API is running",
        "supported_formats": sorted(list(SUPPORTED_EXTENSIONS)),
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Hybrid Graph RAG API",
        "version": "2.0.0",
    }


# ============================================================
# DOCUMENT MANAGEMENT ENDPOINTS
# ============================================================

@app.get("/documents")
def get_documents():
    """List all ingested documents available in the knowledge base."""
    store = None
    try:
        store = PgVectorStore()
        docs = store.list_documents()
        return {
            "status": "success",
            "count": len(docs),
            "documents": docs,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Could not list documents: {e}",
            "documents": [],
        }
    finally:
        if store:
            store.close()


@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and dynamically ingest a document into both
    the Knowledge Graph (Neo4j) and Vector Database (pgvector).
    Supported formats: .pdf, .docx, .doc, .csv, .xlsx, .xls, .pptx, .ppt, .txt, .md
    """
    filename = file.filename or "uploaded_file"
    suffix = Path(filename).suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file format '{suffix}'. "
                f"Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            ),
        )

    try:
        content_bytes = await file.read()
        if not content_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        # Save copy locally
        saved_file_path = UPLOADS_DIR / filename
        with open(saved_file_path, "wb") as f:
            f.write(content_bytes)

        # Ingest into Vector DB and Knowledge Graph
        ingestor = DocumentIngestor()
        result = ingestor.ingest(
            filename=filename,
            content_bytes=content_bytes,
        )

        return UploadResponse(
            status="success",
            document_id=result["document_id"],
            file_name=result["file_name"],
            char_count=result["char_count"],
            chunk_count=result["chunk_count"],
            entity_count=result["entity_count"],
            relationship_count=result["relationship_count"],
            sample_entities=result["sample_entities"],
            message=(
                f"Successfully ingested '{filename}'! "
                f"Created {result['chunk_count']} vector chunks and extracted "
                f"{result['entity_count']} entities with {result['relationship_count']} relationships."
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process and ingest '{filename}': {str(e)}",
        )


# ============================================================
# QUERY ENDPOINT
# ============================================================

@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    """
    Query the knowledge base using hybrid retrieval (Graph + Vector).
    Optionally scopes to a specific document_id.
    """
    retriever = HybridRetriever()
    generator = AnswerGenerator()

    try:
        # ----------------------------------------------------
        # RETRIEVAL
        # ----------------------------------------------------
        retrieval = retriever.retrieve(
            question=request.question,
            document_id=request.document_id,
        )

        route = retrieval["route"]

        # ----------------------------------------------------
        # ANSWER GENERATION
        # ----------------------------------------------------
        generated = generator.generate(
            question=request.question,
            vector_results=retrieval["vector_results"],
            graph_results=retrieval["graph_results"],
        )

        return QueryResponse(
            question=request.question,
            answer=generated["answer"],
            route=route.route.value,
            query_type=route.query_type.value,
            confidence=route.confidence,
            entities=route.entities,
            sources=generated["sources"],
            graph_evidence=generated["graph_evidence"],
            document_id=request.document_id,
        )

    finally:
        retriever.close()