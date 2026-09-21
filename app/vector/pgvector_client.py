from sqlalchemy import create_engine, text

from app.config import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)


class PostgresClient:
    def __init__(self):
        database_url = (
            f"postgresql+psycopg2://"
            f"{POSTGRES_USER}:{POSTGRES_PASSWORD}"
            f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        )

        self.engine = create_engine(database_url)

    def verify_connection(self):
        with self.engine.connect() as connection:
            result = connection.execute(
                text("SELECT 'PostgreSQL connection successful' AS message")
            )
            return result.scalar()

    def enable_pgvector(self):
        with self.engine.begin() as connection:
            connection.execute(
                text("CREATE EXTENSION IF NOT EXISTS vector")
            )

    def close(self):
        self.engine.dispose()
