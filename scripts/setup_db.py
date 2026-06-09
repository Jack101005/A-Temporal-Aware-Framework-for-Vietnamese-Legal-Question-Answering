"""
setup_db.py
===========
One-time setup + sanity check. Run AFTER PostgreSQL is installed.

What it does:
  1. connects to PostgreSQL
  2. creates the tables from schema.sql
  3. loads the minimum-wage decrees (with structured_data for the UI)
  4. runs the temporal query for several dates to prove it works

Run with:  python scripts/setup_db.py
"""

import sys, json
from datetime import datetime

sys.path.insert(0, ".")
import psycopg2
from configs.settings import DATABASE_URL


def _parse_date(s):
    return datetime.strptime(s, "%Y-%m-%d").date() if s else None


def main():
    conn = psycopg2.connect(DATABASE_URL)
    print("Connected to PostgreSQL.")

    # create schema
    with open("src/database/schema.sql", encoding="utf-8") as f:
        with conn.cursor() as cur:
            cur.execute(f.read())
    conn.commit()
    print("Schema created.")

    # load wage documents (richer dataset with structured_data)
    with open("data/questions/wage_documents.json", encoding="utf-8") as f:
        docs = json.load(f)

    with conn.cursor() as cur:
        for d in docs:
            cur.execute(
                """
                INSERT INTO legal_documents
                    (document_id, title, document_type, issuing_agency,
                     issue_date, effective_from, effective_to, content, structured_data)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (document_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    effective_from = EXCLUDED.effective_from,
                    effective_to = EXCLUDED.effective_to,
                    content = EXCLUDED.content,
                    structured_data = EXCLUDED.structured_data;
                """,
                (d["document_id"], d["title"], d["document_type"], d["issuing_agency"],
                 _parse_date(d["issue_date"]), _parse_date(d["effective_from"]),
                 _parse_date(d["effective_to"]), d["content"],
                 json.dumps(d["structured_data"])),
            )
    conn.commit()
    print(f"Inserted {len(docs)} documents.")

    # prove the temporal query works
    print("\n--- Which minimum-wage decree is valid on each date? ---")
    for qd in ["2021-05-01", "2023-03-01", "2026-06-08"]:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT document_id FROM legal_documents
                WHERE document_type = 'Decree'
                  AND effective_from <= %s
                  AND (effective_to >= %s OR effective_to IS NULL);
                """,
                (qd, qd),
            )
            ids = [r[0] for r in cur.fetchall()]
        print(f"{qd}: {ids}")

    conn.close()
    print("\nDone. If each date returned exactly one decree, it works!")


if __name__ == "__main__":
    main()