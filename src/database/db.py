"""
db.py
=====
The only file that talks to PostgreSQL directly.

The rest of the code calls these methods instead of writing SQL.
The most important method is get_effective_documents(query_date) --
it returns ONLY the documents legally valid on that date. That single
query is what makes the temporal thesis work.
"""

from __future__ import annotations

import psycopg2
from psycopg2.extras import execute_values
from datetime import date

from configs.settings import DATABASE_URL
from src.database.models import LegalDocument


class LegalDB:
    """Thin repository over the PostgreSQL legal corpus."""

    def __init__(self, dsn: str = DATABASE_URL):
        self.dsn = dsn
        self.conn = None

    def connect(self):
        """Open a connection to PostgreSQL."""
        self.conn = psycopg2.connect(self.dsn)
        return self.conn

    def close(self):
        if self.conn:
            self.conn.close()

    def init_schema(self, schema_path: str = "src/database/schema.sql"):
        """Run schema.sql to create the tables (run once)."""
        with open(schema_path, "r", encoding="utf-8") as f:
            sql = f.read()
        with self.conn.cursor() as cur:
            cur.execute(sql)
        self.conn.commit()

    def insert_document(self, doc: LegalDocument):
        """Insert one legal document row."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO legal_documents
                    (document_id, title, document_type, issuing_agency,
                     issue_date, effective_from, effective_to, content, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (document_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    effective_from = EXCLUDED.effective_from,
                    effective_to = EXCLUDED.effective_to,
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding;
                """,
                (doc.document_id, doc.title, doc.document_type, doc.issuing_agency,
                 doc.issue_date, doc.effective_from, doc.effective_to,
                 doc.content, doc.embedding),
            )
        self.conn.commit()

    def get_effective_documents(self, query_date: date) -> list[LegalDocument]:
        """THE CORE TEMPORAL QUERY.
        Return only documents valid on query_date:
            effective_from <= query_date
            AND (effective_to >= query_date OR effective_to IS NULL)
        """
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT document_id, title, document_type, issuing_agency,
                       issue_date, effective_from, effective_to, content
                FROM legal_documents
                WHERE effective_from <= %s
                  AND (effective_to >= %s OR effective_to IS NULL);
                """,
                (query_date, query_date),
            )
            rows = cur.fetchall()
        return [
            LegalDocument(
                document_id=r[0], title=r[1], document_type=r[2],
                issuing_agency=r[3], issue_date=r[4],
                effective_from=r[5], effective_to=r[6], content=r[7],
            )
            for r in rows
        ]

    def vector_search(self, embedding: list[float], k: int = 10,
                      query_date: date | None = None) -> list[LegalDocument]:
        """Nearest-neighbour search via pgvector, optionally time-filtered.
        If query_date is given, only valid documents are searched -- this
        is dense retrieval + temporal filtering in ONE query."""
        where = ""
        params = [embedding]
        if query_date is not None:
            where = "WHERE effective_from <= %s AND (effective_to >= %s OR effective_to IS NULL)"
            params = [query_date, query_date, embedding]
        with self.conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT document_id, title, document_type, content
                FROM legal_documents
                {where}
                ORDER BY embedding <=> %s::vector
                LIMIT {k};
                """,
                params,
            )
            rows = cur.fetchall()
        return [
            LegalDocument(document_id=r[0], title=r[1],
                          document_type=r[2], content=r[3])
            for r in rows
        ]
