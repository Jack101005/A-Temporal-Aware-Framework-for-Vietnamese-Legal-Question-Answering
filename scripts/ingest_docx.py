"""
ingest_docx.py
==============
Reads the .docx files in data/raw/, combined with their metadata from
data/questions/labor_law_metadata.json, and inserts them into PostgreSQL.

Run with:
    cd ~/Desktop/vn-legal-rag
    source .venv/bin/activate
    export DATABASE_URL="postgresql://jacktrinh@localhost/vn_legal"
    python scripts/ingest_docx.py
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path

import psycopg2
from docx import Document

# Project root + paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
METADATA_FILE = PROJECT_ROOT / "data" / "questions" / "labor_law_metadata.json"

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jacktrinh@localhost/vn_legal")


def _parse_date(s):
    if not s:
        return None
    return datetime.strptime(s, "%Y-%m-%d").date()


def read_docx_text(filepath: Path) -> str:
    """Read all paragraphs from a .docx file, join into one text string."""
    doc = Document(str(filepath))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def main():
    # 1. load metadata
    with open(METADATA_FILE, encoding="utf-8") as f:
        metadata = json.load(f)
    print(f"Loaded metadata for {len(metadata)} documents.")

    # 2. connect to PostgreSQL
    conn = psycopg2.connect(DATABASE_URL)
    print("Connected to PostgreSQL.")

    # 3. for each docx file, read text + insert
    inserted = 0
    for doc_id, meta in metadata.items():
        filepath = RAW_DIR / f"{doc_id}.docx"
        if not filepath.exists():
            print(f"  ⚠️  File not found: {filepath} — skipping")
            continue

        print(f"  Reading {doc_id}.docx ...", end=" ", flush=True)
        content = read_docx_text(filepath)
        print(f"{len(content):,} characters")

        # structured_data holds extra info for the UI (just subject for now)
        structured_data = {"subject": meta.get("subject", "")}

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO legal_documents
                    (document_id, title, document_type, issuing_agency,
                     issue_date, effective_from, effective_to,
                     content, structured_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (document_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    document_type = EXCLUDED.document_type,
                    effective_from = EXCLUDED.effective_from,
                    effective_to = EXCLUDED.effective_to,
                    content = EXCLUDED.content,
                    structured_data = EXCLUDED.structured_data;
                """,
                (
                    doc_id, meta["title"], meta["document_type"],
                    meta["issuing_agency"],
                    _parse_date(meta["issue_date"]),
                    _parse_date(meta["effective_from"]),
                    _parse_date(meta["effective_to"]),
                    content,
                    json.dumps(structured_data),
                ),
            )
        inserted += 1

    conn.commit()
    print(f"\n✓ Inserted/updated {inserted} documents.")

    # 4. quick verification — show what's in the DB now
    print("\n--- Documents currently in database ---")
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT document_id, document_type, effective_from, effective_to,
                   LENGTH(content) as content_len
            FROM legal_documents
            ORDER BY effective_from;
            """
        )
        for row in cur.fetchall():
            doc_id, dtype, eff_from, eff_to, clen = row
            status = "valid" if eff_to is None else f"superseded {eff_to}"
            print(f"  {doc_id:15} | {dtype:10} | from {eff_from} | {status:25} | {clen:>7,} chars")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
