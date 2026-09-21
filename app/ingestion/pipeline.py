import logging
import re
from pathlib import Path

from app.ingestion.loader import load_document, load_document_from_bytes
from app.ingestion.chunker import chunk_documents
from app.ingestion.embedder import Embedder
from app.graph.entity_resolver import EntityResolver
from app.graph.graph_writer import GraphWriter
from app.vector.pgvector_store import PgVectorStore
from app.llm.router import LLMRouter

logger = logging.getLogger(__name__)


def sanitize_document_id(filename: str) -> str:
    stem = Path(filename).stem
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", stem.lower())
    cleaned = cleaned.strip("_")
    return cleaned or "doc"


class DocumentIngestor:
    def __init__(self):
        self.embedder = Embedder()
        self.llm_router = LLMRouter()
        self.entity_resolver = EntityResolver(similarity_threshold=0.90)

    def ingest(
        self,
        filename: str,
        content_bytes: bytes | None = None,
        file_path: str | Path | None = None,
        document_id: str | None = None,
    ) -> dict:
        """
        Ingest a document into both the Knowledge Graph (Neo4j)
        and Vector Database (pgvector).
        """
        doc_id = document_id or sanitize_document_id(filename)

        # -------------------------------------------------------------
        # 1. Extract text from file bytes or path
        # -------------------------------------------------------------
        if content_bytes is not None:
            text = load_document_from_bytes(content_bytes, filename)
        elif file_path is not None:
            text = load_document(Path(file_path))
        else:
            raise ValueError("Either content_bytes or file_path must be provided.")

        cleaned_text = text.strip()
        if not cleaned_text:
            raise ValueError(f"No extractable text found in '{filename}'.")

        # -------------------------------------------------------------
        # 2. Chunk the document
        # -------------------------------------------------------------
        document_record = {
            "document_id": doc_id,
            "file_name": filename,
            "text": cleaned_text,
        }

        chunks = chunk_documents([document_record])
        if not chunks:
            raise RuntimeError(f"Could not generate chunks for '{filename}'.")

        # -------------------------------------------------------------
        # 3. Store into Vector Store (pgvector)
        # -------------------------------------------------------------
        vector_store = PgVectorStore()
        graph_writer = GraphWriter()

        unique_entities = set()
        total_relationships = 0

        try:
            vector_store.initialize()
            graph_writer.create_constraints()

            for chunk in chunks:
                chunk_text = chunk["text"]
                chunk_id = chunk["chunk_id"]

                # A. Generate vector embedding & store in pgvector
                try:
                    embedding = self.embedder.embed(chunk_text)
                    vector_store.upsert_chunk(
                        chunk_id=chunk_id,
                        document_id=doc_id,
                        content=chunk_text,
                        embedding=embedding,
                        section_path=chunk.get("section_path"),
                        document_date=chunk.get("document_date"),
                    )
                except Exception as e:
                    logger.error(f"Failed to store vector for chunk {chunk_id}: {e}")

                # B. Extract graph entities & relations via LLM
                try:
                    extraction, provider = self.llm_router.extract(chunk_text)
                    if extraction and extraction.entities:
                        mapping = self.entity_resolver.resolve_all(extraction.entities)
                        graph_writer.write_extraction(
                            extraction=extraction,
                            entity_mapping=mapping,
                            chunk_id=chunk_id,
                            document_id=doc_id,
                        )
                        unique_entities.update(mapping.values())
                        total_relationships += len(extraction.relationships)
                except Exception as e:
                    logger.warning(
                        f"Graph extraction skipped for chunk {chunk_id} due to LLM error: {e}"
                    )

        finally:
            vector_store.close()
            graph_writer.close()

        return {
            "status": "success",
            "document_id": doc_id,
            "file_name": filename,
            "char_count": len(cleaned_text),
            "chunk_count": len(chunks),
            "entity_count": len(unique_entities),
            "relationship_count": total_relationships,
            "sample_entities": sorted(list(unique_entities))[:15],
        }
