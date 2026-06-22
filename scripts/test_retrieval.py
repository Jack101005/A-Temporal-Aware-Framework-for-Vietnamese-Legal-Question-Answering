"""
test_retrieval.py
=================
Demonstrates semantic + temporal retrieval working together.

Given a question and a query date, it:
  1. embeds the question with the same PhoBERT-based model
  2. finds the most semantically similar chunks via pgvector (cosine)
  3. BUT only among documents legally in force on the query date

This single query is the core of the thesis: meaning-based search that
respects time.

Run with:
    cd ~/Desktop/vn-legal-rag
    source .venv/bin/activate
    export DATABASE_URL="postgresql://jacktrinh@localhost/vn_legal"
    python scripts/test_retrieval.py
"""

import os
import psycopg2
from sentence_transformers import SentenceTransformer

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jacktrinh@localhost/vn_legal")
MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"


def search(conn, model, question, query_date, k=3):
    """Semantic search restricted to documents valid on query_date."""
    q_emb = model.encode([question], normalize_embeddings=True)[0]
    vec = "[" + ",".join(f"{x:.6f}" for x in q_emb) + "]"

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT c.document_id, c.article_label, c.content,
                   d.title, d.effective_from, d.effective_to,
                   c.embedding <=> %s::vector AS distance
            FROM document_chunks c
            JOIN legal_documents d ON c.document_id = d.document_id
            WHERE d.effective_from <= %s
              AND (d.effective_to >= %s OR d.effective_to IS NULL)
            ORDER BY distance
            LIMIT %s;
            """,
            (vec, query_date, query_date, k),
        )
        return cur.fetchall()


def main():
    conn = psycopg2.connect(DATABASE_URL)
    print("Connected. Loading model...\n")
    model = SentenceTransformer(MODEL_NAME)

    tests = [
        ("Mức lương tối thiểu vùng 1 là bao nhiêu?", "2026-06-22"),
        ("Mức lương tối thiểu vùng 1 là bao nhiêu?", "2023-03-01"),
        ("Khi nào người lao động được nghỉ hưu?", "2026-06-22"),
        ("Người nước ngoài làm việc tại Việt Nam cần giấy phép gì?", "2026-06-22"),
    ]

    for question, date in tests:
        print("=" * 70)
        print(f"Q: {question}")
        print(f"Ngày áp dụng: {date}")
        print("-" * 70)
        results = search(conn, model, question, date)
        for doc_id, label, content, title, ef, et, dist in results:
            sim = 1 - dist
            snippet = content[:90].replace("\n", " ")
            print(f"  [{sim:.3f}] {doc_id} / {label}")
            print(f"          {snippet}...")
        print()

    conn.close()


if __name__ == "__main__":
    main()
