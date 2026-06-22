"""
generate_embeddings.py
======================
Reads every document from the database, splits it into article-based chunks,
generates a PhoBERT-based embedding for each chunk, and stores the chunks
(with embeddings) in the document_chunks table.

Run with:
    cd ~/Desktop/vn-legal-rag
    source .venv/bin/activate
    export DATABASE_URL="postgresql://jacktrinh@localhost/vn_legal"
    python scripts/generate_embeddings.py
"""

import os
import sys
from pathlib import Path

import psycopg2
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from retrieval.chunker import chunk_document

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jacktrinh@localhost/vn_legal")
MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"
SCHEMA_FILE = PROJECT_ROOT / "src" / "database" / "schema_chunks.sql"


def main():
    conn = psycopg2.connect(DATABASE_URL)
    print("Connected to PostgreSQL.")

    # 1. make sure the chunks table exists
    with open(SCHEMA_FILE, encoding="utf-8") as f:
        with conn.cursor() as cur:
            cur.execute(f.read())
    conn.commit()
    print("Chunks table ready.")

    # 2. clear any old chunks (so re-runs are clean)
    with conn.cursor() as cur:
        cur.execute("DELETE FROM document_chunks;")
    conn.commit()
    print("Cleared old chunks.")

    # 3. load all documents
    with conn.cursor() as cur:
        cur.execute("SELECT document_id, content FROM legal_documents ORDER BY document_id;")
        docs = cur.fetchall()
    print(f"Loaded {len(docs)} documents.\n")

    # 4. load the embedding model (downloads once, then cached)
    print(f"Loading embedding model '{MODEL_NAME}' ...")
    model = SentenceTransformer(MODEL_NAME)
    print("Model loaded.\n")

    # 5. chunk + embed + insert
    total_chunks = 0
    for doc_id, content in docs:
        if not content or not content.strip():
            print(f"  {doc_id}: empty, skipped")
            continue

        chunks = chunk_document(content, doc_id)
        texts = [c["content"] for c in chunks]

        # encode all chunks of this document in one batch
        embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)

        with conn.cursor() as cur:
            for c, emb in zip(chunks, embeddings):
                vec = "[" + ",".join(f"{x:.6f}" for x in emb) + "]"
                cur.execute(
                    """
                    INSERT INTO document_chunks
                        (document_id, chunk_index, article_label, content, embedding)
                    VALUES (%s, %s, %s, %s, %s::vector);
                    """,
                    (c["document_id"], c["chunk_index"], c["article_label"],
                     c["content"], vec),
                )
        conn.commit()
        total_chunks += len(chunks)
        print(f"  {doc_id:15} -> {len(chunks):3} chunks embedded")

    print(f"\n✓ Done. {total_chunks} chunks stored across {len(docs)} documents.")

    # 6. quick verification
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM document_chunks;")
        n = cur.fetchone()[0]
    print(f"Total chunks in database: {n}")
    conn.close()


if __name__ == "__main__":
    main()
