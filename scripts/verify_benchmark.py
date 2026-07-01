"""
verify_benchmark.py
===================
Helps verify the benchmark's ground-truth answers against the actual corpus.

For each question it:
  1. checks that the gold document was legally in force on the query_date
  2. pulls the gold article's text from the database
  3. if the answer contains a specific figure, checks whether that figure
     actually appears in the source text (auto-verification)
  4. prints everything so you can confirm or correct each answer

Run with:
    cd ~/Desktop/vn-legal-rag
    source .venv/bin/activate
    export DATABASE_URL="postgresql://jacktrinh@localhost/vn_legal"
    python scripts/verify_benchmark.py
"""

import os
import json
from pathlib import Path

import psycopg2

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BENCH_FILE = PROJECT_ROOT / "data" / "benchmark" / "labor_law_benchmark.json"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jacktrinh@localhost/vn_legal")


def get_article_text(conn, document_id, article_label):
    """Return the concatenated chunk text for a given article of a document."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT content FROM document_chunks
            WHERE document_id = %s AND article_label = %s
            ORDER BY chunk_index;
            """,
            (document_id, article_label),
        )
        rows = cur.fetchall()
    return "\n".join(r[0] for r in rows)


def doc_valid_on(conn, document_id, query_date):
    """Check the gold doc was actually in force on the query date."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT effective_from, effective_to FROM legal_documents
            WHERE document_id = %s;
            """,
            (document_id,),
        )
        row = cur.fetchone()
    if not row:
        return None, "DOC NOT FOUND"
    ef, et = row
    qd = query_date
    ok = (str(ef) <= qd) and (et is None or str(et) >= qd)
    return ok, f"effective {ef} -> {et or 'still valid'}"


def main():
    with open(BENCH_FILE, encoding="utf-8") as f:
        bench = json.load(f)
    questions = bench["questions"]

    conn = psycopg2.connect(DATABASE_URL)
    print(f"Verifying {len(questions)} benchmark questions...\n")

    auto_ok = 0
    needs_review = 0
    temporal_problem = 0

    for q in questions:
        print("=" * 72)
        print(f"{q['id']} [{q['category']}/{q['topic']}]  date={q['query_date']}")
        print(f"  Q: {q['question']}")
        print(f"  Expected: {q['expected_answer']}")
        print(f"  Gold: {q['gold_document_id']} / {q['gold_article']}")

        # 1. temporal check: was the gold doc valid on that date?
        valid, info = doc_valid_on(conn, q["gold_document_id"], q["query_date"])
        if valid is None:
            print(f"  ⚠️  {info}")
            temporal_problem += 1
        elif not valid:
            print(f"  ⚠️  TEMPORAL MISMATCH: gold doc not in force on {q['query_date']} ({info})")
            temporal_problem += 1
        else:
            print(f"  ✓ temporal OK ({info})")

        # 2. pull gold article text
        text = get_article_text(conn, q["gold_document_id"], q["gold_article"])
        if not text:
            print(f"  ⚠️  Article '{q['gold_article']}' not found in chunks — CHECK gold_article")
            needs_review += 1
            print()
            continue

        # 3. figure auto-check
        fig = q.get("expected_figure", "").strip()
        if fig:
            if fig in text:
                print(f"  ✓ figure '{fig}' FOUND in source text → answer auto-verified")
                auto_ok += 1
            else:
                print(f"  ⚠️  figure '{fig}' NOT found in stored text "
                      f"(may be in a table not extracted) → REVIEW")
                needs_review += 1
        else:
            print(f"  ◷ descriptive answer → read source below and confirm manually")
            needs_review += 1

        # show a snippet of the source for manual confirmation
        snippet = text[:260].replace("\n", " ")
        print(f"  Source snippet: {snippet}...")
        print()

    conn.close()
    print("=" * 72)
    print(f"SUMMARY: {len(questions)} questions")
    print(f"  auto-verified (figure found): {auto_ok}")
    print(f"  needs manual review:          {needs_review}")
    print(f"  temporal problems:            {temporal_problem}")
    print("\nNext: read each 'REVIEW' item, confirm/correct the answer, "
          "then set \"verified\": true in the JSON.")


if __name__ == "__main__":
    main()
