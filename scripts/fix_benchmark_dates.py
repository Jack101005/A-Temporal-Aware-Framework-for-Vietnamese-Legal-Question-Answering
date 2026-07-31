"""
fix_benchmark_dates.py
=======================
Patches query_date for auto-generated temporal questions so that the date
actually falls inside the gold document's own effective_from/effective_to
window. The bulk expansion script assigned a single fixed date to every
temporal-chain question regardless of which decree in the chain the
article came from, which produced a handful of self-contradictory items
(gold document already expired as of the assigned date). This script
fixes the date only, keeping the already-drafted question and answer text
so no LLM calls are needed again.

Run with:
    cd ~/Desktop/vn-legal-rag
    source .venv/bin/activate
    export DATABASE_URL="postgresql://jacktrinh@localhost/vn_legal"
    python scripts/fix_benchmark_dates.py
"""

import os
import json
from datetime import date, timedelta
from pathlib import Path

import psycopg2

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BENCH_FILE = PROJECT_ROOT / "data" / "benchmark" / "labor_law_benchmark.json"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jacktrinh@localhost/vn_legal")


def get_doc_dates(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT document_id, effective_from, effective_to FROM legal_documents;")
        return {row[0]: (row[1], row[2]) for row in cur.fetchall()}


def midpoint_date(eff_from, eff_to):
    """A date safely inside [eff_from, eff_to], or eff_from + 6 months if
    eff_to is null (document still in force)."""
    if eff_to is not None:
        span = (eff_to - eff_from).days
        return eff_from + timedelta(days=span // 2)
    return eff_from + timedelta(days=180)


def main():
    with open(BENCH_FILE, encoding="utf-8") as f:
        data = json.load(f)
    questions = data["questions"]

    conn = psycopg2.connect(DATABASE_URL)
    doc_dates = get_doc_dates(conn)
    conn.close()

    fixed = 0
    for q in questions:
        doc_id = q.get("gold_document_id")
        if doc_id not in doc_dates:
            continue
        eff_from, eff_to = doc_dates[doc_id]
        current_qdate = date.fromisoformat(q["query_date"])

        valid_now = (current_qdate >= eff_from) and (eff_to is None or current_qdate <= eff_to)
        if valid_now:
            continue   # already consistent, leave untouched (this preserves
                       # the original 20 hand-picked dates exactly as they were)

        new_date = midpoint_date(eff_from, eff_to)
        q["query_date"] = new_date.isoformat()
        q.setdefault("notes", "")
        q["notes"] = (q["notes"] + " | query_date corrected to fall inside "
                      "the gold document's actual effective window.").strip(" |")
        fixed += 1

    with open(BENCH_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Checked {len(questions)} questions.")
    print(f"Fixed {fixed} question(s) with an inconsistent query_date.")
    print(f"Saved back to {BENCH_FILE}")
    print("\nNext: re-run scripts/run_experiments.py to get corrected numbers.")


if __name__ == "__main__":
    main()
