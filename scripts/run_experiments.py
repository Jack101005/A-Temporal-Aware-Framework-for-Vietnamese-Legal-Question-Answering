"""
run_experiments.py
==================
Core experiment: compares Standard RAG (semantic only) vs Temporal RAG
(semantic + temporal filter) on the labor-law benchmark.

For each question it retrieves top-k chunks under both configurations and scores:
  - temporal_accuracy : top-1 document == gold document in force on the query date
  - doc_in_topk       : gold document appears in top-k
  - citation_match    : top-1 document AND article match the gold
  - anachronism       : top-1 document was NOT in force on the query date
                        (retrieval-level hallucination; 0 by construction for Temporal)

Results are aggregated by category (temporal vs static) and saved to JSON.

Run with:
    cd ~/Desktop/vn-legal-rag
    source .venv/bin/activate
    export DATABASE_URL="postgresql://jacktrinh@localhost/vn_legal"
    python scripts/run_experiments.py
"""

import os
import json
from pathlib import Path

import psycopg2
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BENCH_FILE = PROJECT_ROOT / "data" / "benchmark" / "labor_law_benchmark.json"
OUT_FILE = PROJECT_ROOT / "data" / "benchmark" / "experiment_results.json"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jacktrinh@localhost/vn_legal")
MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"
TOP_K = 5


def retrieve(conn, vec, query_date, temporal):
    """Return list of (document_id, article_label, effective_from, effective_to)."""
    if temporal:
        sql = """
            SELECT c.document_id, c.article_label, d.effective_from, d.effective_to
            FROM document_chunks c JOIN legal_documents d ON c.document_id = d.document_id
            WHERE d.effective_from <= %s AND (d.effective_to >= %s OR d.effective_to IS NULL)
            ORDER BY c.embedding <=> %s::vector
            LIMIT %s;
        """
        params = (query_date, query_date, vec, TOP_K)
    else:
        sql = """
            SELECT c.document_id, c.article_label, d.effective_from, d.effective_to
            FROM document_chunks c JOIN legal_documents d ON c.document_id = d.document_id
            ORDER BY c.embedding <=> %s::vector
            LIMIT %s;
        """
        params = (vec, TOP_K)
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def valid_on(ef, et, date):
    return (str(ef) <= date) and (et is None or str(et) >= date)


def score(results, q):
    """Compute per-question metrics from retrieved results."""
    if not results:
        return dict(temporal_accuracy=0, doc_in_topk=0, citation_match=0, anachronism=0)
    top_doc, top_art, top_ef, top_et = results[0]
    docs = [r[0] for r in results]
    gold_doc, gold_art, date = q["gold_document_id"], q["gold_article"], q["query_date"]
    return dict(
        temporal_accuracy=int(top_doc == gold_doc),
        doc_in_topk=int(gold_doc in docs),
        citation_match=int(top_doc == gold_doc and top_art == gold_art),
        anachronism=int(not valid_on(top_ef, top_et, date)),
    )


def aggregate(rows, keys):
    n = len(rows)
    if n == 0:
        return {k: 0.0 for k in keys}
    return {k: round(100 * sum(r[k] for r in rows) / n, 1) for k in keys}


def main():
    with open(BENCH_FILE, encoding="utf-8") as f:
        questions = json.load(f)["questions"]

    conn = psycopg2.connect(DATABASE_URL)
    print("Connected. Loading model...\n")
    model = SentenceTransformer(MODEL_NAME)

    METRICS = ["temporal_accuracy", "doc_in_topk", "citation_match", "anachronism"]
    per_q = []

    for q in questions:
        emb = model.encode([q["question"]], normalize_embeddings=True)[0]
        vec = "[" + ",".join(f"{x:.6f}" for x in emb) + "]"
        std = score(retrieve(conn, vec, q["query_date"], temporal=False), q)
        tmp = score(retrieve(conn, vec, q["query_date"], temporal=True), q)
        per_q.append({"id": q["id"], "category": q["category"],
                      "standard": std, "temporal": tmp})
    conn.close()

    def report(subset, label):
        std_rows = [p["standard"] for p in per_q if subset(p)]
        tmp_rows = [p["temporal"] for p in per_q if subset(p)]
        n = len(std_rows)
        s = aggregate(std_rows, METRICS)
        t = aggregate(tmp_rows, METRICS)
        print("=" * 64)
        print(f"{label} (n={n})")
        print(f"  {'Metric':<28}{'Standard RAG':>14}{'Temporal RAG':>14}")
        print(f"  {'Temporal accuracy (top-1)':<28}{s['temporal_accuracy']:>13}%{t['temporal_accuracy']:>13}%")
        print(f"  {'Correct doc in top-5':<28}{s['doc_in_topk']:>13}%{t['doc_in_topk']:>13}%")
        print(f"  {'Citation match (doc+article)':<28}{s['citation_match']:>13}%{t['citation_match']:>13}%")
        print(f"  {'Anachronism rate (top-1)':<28}{s['anachronism']:>13}%{t['anachronism']:>13}%")
        print()
        return {"n": n, "standard": s, "temporal": t}

    print()
    results = {
        "temporal_questions": report(lambda p: p["category"] == "temporal", "TEMPORAL QUESTIONS"),
        "static_questions": report(lambda p: p["category"] == "static", "STATIC QUESTIONS"),
        "overall": report(lambda p: True, "OVERALL"),
        "per_question": per_q,
    }

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Saved detailed results to {OUT_FILE}")
    print("\nKey takeaway: on temporal questions, the anachronism rate should drop")
    print("to 0% with the temporal filter, while temporal accuracy rises.")


if __name__ == "__main__":
    main()
