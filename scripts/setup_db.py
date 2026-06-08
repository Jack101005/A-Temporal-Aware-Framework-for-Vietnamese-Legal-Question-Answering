"""
setup_db.py
===========
One-time setup + sanity check. Run this AFTER installing PostgreSQL.

What it does (in order):
  1. connects to PostgreSQL
  2. creates the tables from schema.sql
  3. loads the 3 sample minimum-wage decrees
  4. runs the temporal query for several dates to prove it works

Run with:  python scripts/setup_db.py
"""

import sys, json
from datetime import date, datetime

sys.path.insert(0, ".")
from src.database.db import LegalDB
from src.database.models import LegalDocument


def _parse_date(s):
    return datetime.strptime(s, "%Y-%m-%d").date() if s else None


def main():
    db = LegalDB()
    db.connect()
    print("Connected to PostgreSQL.")

    db.init_schema()
    print("Schema created.")

    # Load sample documents
    with open("data/questions/sample_documents.json", encoding="utf-8") as f:
        raw = json.load(f)

    for r in raw:
        doc = LegalDocument(
            document_id=r["document_id"],
            title=r["title"],
            document_type=r["document_type"],
            issuing_agency=r["issuing_agency"],
            issue_date=_parse_date(r["issue_date"]),
            effective_from=_parse_date(r["effective_from"]),
            effective_to=_parse_date(r["effective_to"]),
            content=r["content"],
            embedding=None,   # embeddings added in a later step
        )
        db.insert_document(doc)
    print(f"Inserted {len(raw)} documents.")

    # Prove the temporal query works
    print("\n--- Which minimum-wage decree is valid on each date? ---")
    for qd in [date(2021, 5, 1), date(2023, 3, 1), date(2026, 6, 8)]:
        valid = db.get_effective_documents(qd)
        ids = [d.document_id for d in valid]
        print(f"{qd}: {ids}")

    db.close()
    print("\nDone. If each date returned exactly one decree, it works!")


if __name__ == "__main__":
    main()
