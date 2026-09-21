import psycopg
from pgvector.psycopg import register_vector
from pgvector import Vector

from app.config import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)


class PgVectorStore:
    DIMENSIONS = 384

    def __init__(self):
        self.connection = psycopg.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        )

        self.connection.autocommit = True

        register_vector(
            self.connection
        )

    def initialize(self):

        self.connection.execute(
            """
            CREATE EXTENSION IF NOT EXISTS vector;
            """
        )

        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS document_chunks (
                chunk_id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                content TEXT NOT NULL,
                section_path TEXT,
                document_date TEXT,
                embedding VECTOR(384) NOT NULL
            );
            """
        )

        self.connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            document_chunks_embedding_hnsw
            ON document_chunks
            USING hnsw (
                embedding vector_cosine_ops
            )
            WITH (
                m = 16,
                ef_construction = 64
            );
            """
        )

        self.connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            document_chunks_document_id_idx
            ON document_chunks(document_id);
            """
        )

    def upsert_chunk(
        self,
        chunk_id: str,
        document_id: str,
        content: str,
        embedding: list[float],
        section_path: str | None = None,
        document_date: str | None = None,
    ):

        self.connection.execute(
            """
            INSERT INTO document_chunks (
                chunk_id,
                document_id,
                content,
                section_path,
                document_date,
                embedding
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            ON CONFLICT (chunk_id)
            DO UPDATE SET
                document_id = EXCLUDED.document_id,
                content = EXCLUDED.content,
                section_path = EXCLUDED.section_path,
                document_date = EXCLUDED.document_date,
                embedding = EXCLUDED.embedding;
            """,
            (
                chunk_id,
                document_id,
                content,
                section_path,
                document_date,
                Vector(embedding),
            ),
        )

    def search(
        self,
        query_embedding: list[float],
        limit: int = 5,
        document_id: str | None = None,
    ):
        if document_id:
            rows = self.connection.execute(
                """
                SELECT
                    chunk_id,
                    document_id,
                    content,
                    section_path,
                    document_date,
                    1 - (
                        embedding <=> %s
                    ) AS similarity
                FROM document_chunks
                WHERE document_id = %s
                ORDER BY embedding <=> %s
                LIMIT %s;
                """,
                (
                    Vector(query_embedding),
                    document_id,
                    Vector(query_embedding),
                    limit,
                ),
            ).fetchall()
        else:
            rows = self.connection.execute(
                """
                SELECT
                    chunk_id,
                    document_id,
                    content,
                    section_path,
                    document_date,
                    1 - (
                        embedding <=> %s
                    ) AS similarity
                FROM document_chunks
                ORDER BY embedding <=> %s
                LIMIT %s;
                """,
                (
                    Vector(query_embedding),
                    Vector(query_embedding),
                    limit,
                ),
            ).fetchall()

        return rows

    def list_documents(self) -> list[dict]:
        rows = self.connection.execute(
            """
            SELECT
                document_id,
                COUNT(*) as chunk_count
            FROM document_chunks
            GROUP BY document_id
            ORDER BY document_id;
            """
        ).fetchall()

        return [
            {"document_id": r[0], "chunk_count": r[1]}
            for r in rows
        ]

    def count_chunks(self) -> int:

        row = self.connection.execute(
            """
            SELECT COUNT(*)
            FROM document_chunks;
            """
        ).fetchone()

        return row[0]

    def close(self):

        self.connection.close()
